#!/usr/bin/env python3

# -*- coding: utf-8 -*- 

''' MIT License
Copyright © 2024 Serpenseth

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

""" NOTICE:
    While reading the contents of this file, you will notice
    some inconsistencies in how I've approached some things.
    Some things will be more 'advanced' than others, for example,
    or some implementation will be the 'naive' way of doing things.
    This is because I've built this program as I was learning Python.
    I'm still learning, of course, but the progress is noticable.
    The inconsistencies show you the order that I worked on things.

    I'm going to polish up the code as time goes on. Sorry for the mess!
"""

from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QGraphicsBlurEffect,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QRadioButton,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QFileDialog,
    QAbstractItemView,
    QTextEdit,
    QFrame
)

from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize, QThread, QTimer, Qt, pyqtSignal

# os stuff
import os

import sys

# time.sleep
import time

# os.path.exists()
import os.path

# Python threading and related
from threading import Thread
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# url stuff
import requests
from requests.adapters import HTTPAdapter

# JSON and ORJSON
import json
import orjson

# QR code generator
import segno

# Web3 related
from web3 import Web3
from eth_account import Account
from eth_account.hdaccount import Mnemonic

## Required for `Web3.contract` functions
from hexbytes import HexBytes

## ENS
from ens import ENS

## Uniswap
from uniswap_universal_router_decoder import (
    FunctionRecipient,
    RouterCodec
)

# Avoid having to save QR codes on device - save in memory instead
from io import BytesIO

# Update-related
import subprocess

# Move function
import shutil

import platform

def main():
    TigerWalletVersion = "3.1"

    s = requests.Session()
    s.mount(
        "https://",
        HTTPAdapter(
            max_retries=1,
            pool_connections=64,
            pool_maxsize=108
        ),
    )

    # BEGIN functions
    def self_destruct() -> None:
        import psutil

        for proc in psutil.process_iter():
            # check whether the process pid matches
            if proc.pid == os.getpid():
                proc.kill()
    
    # New in v3.1
    def _platform() -> str:
        if platform.system() == 'Windows':
            return 'nt'
        elif platform.system() == 'Linux':
            return 'linux'
        else:
            return 'mac'

    # Error box
    def errbox(msg) -> None:
        QMessageBox.critical(None, "TigerWallet", msg)

    # Question box
    def questionbox(question) -> bool:
        ret = QMessageBox.question(
            None,
            "TigerWallet",
            question
        )

        if ret == ret.Yes:
            return True

        return False

    # Information box
    def msgbox(msg) -> None:
        QMessageBox.information(None, "TigerWallet", msg)

    def rm_e_notation(number: str) -> str:
        """
            Removes scientific notations, resulting in an actual decimal
            example: 1e-10 becomes 0.0000000001
        """
        import numpy
        return numpy.format_float_positional((float(number)), trim="-")

    def percent(percent, number) -> float:
        if number == 0 or percent == 0:
            return 0

        return (percent * number) / 100.0
    
    # Mnemonic phrase
    def generate_mnemonic_phrase() -> str:
        mnemonic = Mnemonic()
        
        return mnemonic.generate()
        

    # Rounded corners
    def add_round_corners(window, radius=16) -> None:
        """
        Creates curved edges, adding flavor,
        and removes the window's top bar.

        Source:
            https://stackoverflow.com/questions/63804512/pyqt5-mainwindow-hide-windows-border

        Adapted to Pyqt6
        
        On MacOS, it leaves black corners where the edges are rounded,
        so this function serves no purpose on that platform.
        """
        
        # Do nothing if the platform is MacOS
        if _platform() == 'mac':
            return
        
        from PyQt6.QtCore import QRect
        from PyQt6.QtGui import QRegion

        radius = radius

        window.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        base = window.rect()
        ellipse = QRect(0, 0, 2 * radius, 2 * radius)

        base_region = QRegion(base.adjusted(radius, 0, -radius, 0))
        base_region |= QRegion(base.adjusted(0, radius, 0, -radius))
        base_region |= QRegion(ellipse, QRegion.RegionType.Ellipse)

        ellipse.moveTopRight(base.topRight())

        base_region |= QRegion(ellipse, QRegion.RegionType.Ellipse)
        ellipse.moveBottomRight(base.bottomRight())

        base_region |= QRegion(ellipse, QRegion.RegionType.Ellipse)

        ellipse.moveBottomLeft(base.bottomLeft())

        base_region |= QRegion(ellipse, QRegion.RegionType.Ellipse)

        window.setMask(base_region)

    # Center window
    def align_to_center(window):
        """
        Windows seems to be the only one that automatically
        aligns every Qt window to the center of the screen.

        This function is for Linux/Mac.
        """

        windowframegeo = window.frameGeometry()
        centerpos = window.screen().availableGeometry().center()

        windowframegeo.moveCenter(centerpos)
        window.move(windowframegeo.topLeft())

    def fix_white_borders(comboboxes: list, theme='dark') -> None:
        if theme == 'dark':
            for item in comboboxes:
                item.view().parentWidget().setStyleSheet(
                    'background-color: #0a0f18;'
                )

        elif theme == 'light':
            for item in comboboxes:
                item.view().parentWidget().setStyleSheet(
                    'background-color: #eff1f3;'
                )
    
    def set_widget_font_size(widget, size) -> None:
        font = widget.font()
        font.setPointSize(size)
        widget.setFont(font)
    # END functions
    
    # Variables
    class GlobalVariable:
        def __init__(self):
            self.dest_path = ""
            self.account = type(Account)

            import getpass
            
            self.current_usr = getpass.getuser()

            if _platform() == "nt":
                self.dest_path = "C:/ProgramData/TigerWallet/"

            elif _platform() == 'linux':
                self.dest_path = (
                    "/home/"
                    + self.current_usr
                    + "/.TigerWallet/"
                )
                
            elif _platform() == 'mac':
                self.dest_path = (
                    "/Users/"
                    + self.current_usr
                    + "/.TigerWallet/"
                )

            if not os.path.exists(self.dest_path):
                try:
                    os.mkdir(self.dest_path)

                except Exception as e:
                    print(e)
                    """
                    An instance of QApplication must be
                    active for messagebox to appear
                    """
                    app = QApplication([])

                    errbox(
                        "Fatal error: Could not create TigerWallet folder.\n"
                        + "Make sure that you have write permissions"
                    )

                    quit()

            self.local_path = os.path.dirname(__file__) + "/"
            self.imgfolder = self.dest_path + "images/"
            self.tokenimgfolder = self.dest_path + "images/token_images/"
            

            # Added in v2.1
            '''
            Move the imgfolder from local path to app data folder.

            The previous versions had the folder stored in
            the same directory as the TigerWallet script.
            This was fine, until I realized that when you run
            tigerwallet that was installed via pip install git+,
            the images folder was stored in the python3 folder, which is the
            /home/$USER/.local/lib/python3.version/site-packages directory,
            where $USER is the current user, and version is the python version

            This is not the right way to do things.
            '''
            if not os.path.exists(self.imgfolder):
                try:
                    shutil.move(
                        self.local_path + 'images/',
                        self.imgfolder,
                        copy_function=shutil.copytree
                    )

                except Exception as e:
                    print(e)
                    """
                    An instance of QApplication must be
                    active for messagebox to appear
                    """
                    app = QApplication([])

                    errbox(
                        'Fatal error: Could not move '
                        + 'TigerWallet image folder.\n'
                        + "Make sure that you have write permissions"
                    )

                    quit()

            # ABI
            self.abi = orjson.loads(
                """[{"inputs": [{"internalType":"uint256","name":"_totalSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_address","type":"address"},{"internalType":"bool","name":"_isBlacklisting","type":"bool"}],"name":"blacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"blacklists","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"limited","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxHoldingAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minHoldingAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_limited","type":"bool"},{"internalType":"address","name":"_uniswapV2Pair","type":"address"},{"internalType":"uint256","name":"_maxHoldingAmount","type":"uint256"},{"internalType":"uint256","name":"_minHoldingAmount","type":"uint256"}],"name":"setRule","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]
                    """
            )

            self.conf_file = self.dest_path + "conf.json"
            self.configs = {
                "version": TigerWalletVersion,
                "wallets": [],
                "rpc": {
                    'eth': "https://ethereum-rpc.publicnode.com",
                    'base': 'https://base-pokt.nodies.app'
                },
                "currency": "USD",
                "theme": "default_dark",
                "play_loading_gif": True
            }

            if (
                not os.path.exists(self.conf_file)
                or os.stat(self.conf_file).st_size == 0
                or not 'play_loading_gif' in json.load(
                    open(self.conf_file, mode='r')
                )
            ):
                # Create conf.json file if it doesn't exist
                with open(self.conf_file, "w") as f:
                    json.dump(
                        obj=self.configs,
                        indent=4,
                        fp=f
                    )

            else:
                # Load conf.json file
                with open(self.conf_file, "r") as f:
                    self.configs = json.load(f)

                    # If version is out of date, we close the file and update it
                    if self.configs['version'] != TigerWalletVersion:
                        f.close()

                with open(self.conf_file, "w") as f:
                    self.configs['version'] = TigerWalletVersion

                    json.dump(
                        obj=self.configs,
                        indent=4,
                        fp=f
                    )

            # New in v.2.0
            self.chain = 'eth'

            # Default addresses
            self.addresses = {
                'eth': [
                    # DAI
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                    # USDT
                    "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    # USDC
                    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    # BNB
                    "0xB8c77482e45F1F44dE1745F52C74426C631bDD52",
                    # POL (formerly MATIC)
                    "0x455e53CBB86018Ac2B8092FdCd39d8444aFFC3F6",
                    # PEPE
                    "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                    # SHIB
                    "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
                ],
                'base': [
                    # DAI
                    '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
                    # USDC
                    '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
                    # BRETT
                    '0x532f27101965dd16442E59d40670FaF5eBB142E4',
                    # TOSHI
                    '0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4'
                ]
            }

            # New in v2.0
            self.default_symbols = {
                'eth': {
                    'symbol': [
                        'dai',
                        'usdt',
                        'usdc',
                        'bnb',
                        'pol',
                        'pepe',
                        'shib'
                    ]
                },
                'base': {
                    'symbol': [
                        'dai',
                        'usdc',
                        'brett',
                        'toshi'
                    ]
                }
            }

            # New in v2.0
            self.token_names = {
                'eth': {
                    'name': [
                        'dai stablecoin',
                        'tether usd',
                        'usd coin',
                        'bnb',
                        'polygon ecosystem token',
                        'pepe',
                        'shiba inu'
                    ]
                },
                'base': {
                    'name': [
                        'dai stablecoin',
                        'usd coin',
                        'brett',
                        'toshi'
                    ]
                }
            }

            # New in v2.0
            self.eth_token_images = [
                (
                    self.tokenimgfolder
                    + symbol
                    + '.png'
                )
                for symbol in self.default_symbols['eth']['symbol']
            ]

            self.base_token_images = [
                (
                    self.tokenimgfolder
                    + symbol
                    + '.png'
                )
                for symbol in self.default_symbols['base']['symbol']
            ]

            self.asset_default = {
                'eth': {
                    "address": self.addresses['eth'],
                    "name": self.token_names['eth']['name'],
                    "symbol": self.default_symbols['eth']['symbol'],
                    "image": self.eth_token_images
                },
                'base': {
                    "address": self.addresses['base'],
                    "name": self.token_names['base']['name'],
                    "symbol": self.default_symbols['base']['symbol'],
                    "image": self.base_token_images
                }
            }

            self.asset = self.asset_default
            self.assets_json =  self.dest_path + "assets.json"

            if (
                not os.path.exists(self.assets_json)
                or os.stat(self.assets_json).st_size == 0
                # Older asset file
                or not isinstance(
                    json.load(
                        open(self.assets_json, mode='r')
                    ),
                    dict,
                )
            ):
                with open(self.assets_json, mode='w') as f:
                    json.dump(
                        obj=self.asset,
                        fp=f,
                        indent=4
                    )

            else:
                with open(self.assets_json, mode='rb') as f:
                    self.asset = orjson.loads(f.read())

            # New in v2.0
            list_of_tokens_raw = {
                'eth': [
                    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
                    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "0x514910771AF9Ca656af840dff83E8264EcF986CA",
                    "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
                    "0x2AF5D2aD76741191D15Dfe7bF6aC92d4Bd912Ca3",
                    "0xdC035D45d973E3EC169d2276DDab16f1e407384F",
                    "0x4c9EDD5852cd905f086C759E8383e09bff1E68B3",
                    "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
                    "0x3593D125a4f7849a1B059E64F4517A86Dd60c95d",
                    "0xCd5fE23C85820F7B72D0926FC9b05b43E359b7ee",
                    "0xfAbA6f8e4a5E8Ab82F62fe7C39859FA577269BE3",
                    "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                    "0x152649eA73beAb28c5b49B26eb48f7EAD6d4c898",
                    "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
                    "0x57e114B691Db790C35207b2e685D4A43181e6061",
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                    "0x44ff8620b8cA30902395A7bD3F2407e1A091BF73",
                    "0x163f8C2467924be0ae7B5347228CABF260318753",
                    "0xA2cd3D43c775978A96BdBf12d733D5A1ED94fb18",
                    "0xcf0C122c6b73ff809C693DB761e7BaeBe62b6a2E",
                    "0x6E2a43be0B1d33b726f0CA3b8de60b3482b8b050",
                    "0x3845badAde8e6dFF049820680d1F14bD3903a5d0",
                    "0x3c3a81e81dc49A522A592e7622A7E711c06bf354",
                    "0xec53bF9167f50cDEB3Ae105f56099aaaB9061F83",
                    "0x808507121B80c02388fAd14726482e061B8da827",
                    "0x6e1A19F235bE7ED8E3369eF73b196C07257494DE",
                    "0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1",
                    "0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85",
                    "0xD533a949740bb3306d119CC777fa900bA034cd52",
                    "0xc5f0f7b66764F6ec8C8Dff7BA683102295E16409",
                    "0x8D983cb9388EaC77af0474fA441C4815500Cb7BB",
                    "0xe28b3B32B6c345A34Ff64674606124Dd5Aceca30",
                    "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
                    "0x3073f7aAA4DB83f95e9FFf17424F71D4751a3073",
                    "0x1151CB3d861920e07a38e03eEAd12C32178567F6",
                    "0xE0f63A424a4439cBE457D80E4f4b51aD25b2c56C",
                    "0xaaeE1A9723aaDB7afA2810263653A34bA2C21C7a",
                    "0xac57de9c1a09fec648e93eb98875b212db0d460b",
                    "0xa35923162c49cf95e6bf26623385eb431ad920d3",
                    "0xb131f4a55907b10d1f0a50d8ab8fa09ec342cd74",
                    "0x812ba41e071c7b7fa4ebcfb62df5f45f6fa853ee",
                    "0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3",
                    "0x8ed97a637a790be1feff5e888d43629dc05408f6",
                    "0x594DaaD7D77592a2b97b725A7AD59D7E188b5bFa",
                    "0x68bbed6a47194eff1cf514b50ea91895597fc91e",
                    "0x9813037ee2218799597d83D4a5B6F3b6778218d9",
                    "0x12970e6868f88f6557b76120662c1b3e50a646bf",
                    "0x5026F006B85729a8b14553FAE6af249aD16c9aaB",
                    "0xb90b2a35c65dbc466b04240097ca756ad2005295",
                    "0xb9f599ce614Feb2e1BBe58F180F370D05b39344E"
                ],
                'base': [
                    # WETH
                    '0x4200000000000000000000000000000000000006',
                    # WBTC
                    '0x0555E30da8f98308EdB960aa94C0Db47230d2B9c',
                    # wstETH
                    '0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452',
                    # USDS
                    '0x820C137fa70C8691f0e44Dc420a5e53c168921Dc',
                    # OM
                    '0x3992B27dA26848C2b19CeA6Fd25ad5568B68AB98',
                    # USDe
                    '0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34',
                    # DAI
                    '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
                    # weETH.base
                    '0x04C0599Ae5A44757c0af6F9eC3b93da8976c150A',
                    # AAVE
                    '0x63706e401c06ac8513145b7687A14804d17f814b',
                    # ENA
                    '0x58538e6A46E07434d7E7375Bc268D3cb839C0133',
                    # rETH
                    '0xB6fe221Fe9EeF5aBa221c348bA20A1Bf5e73624c',
                    # TEL
                    '0x09bE1692ca16e06f536F0038fF11D1dA8524aDB1',
                    # PYTH
                    '0x4c5d8A75F3762c1561D96f177694f67378705E98',
                    # VIRTUAL
                    '0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b',
                    # ezETH
                    '0x2416092f143378750bb29b79eD961ab195CcEea5',
                    # CRV
                    '0x8Ee73c484A26e0A5df2Ee2a4960B789967dd0415',
                    # AERO
                    '0x940181a94A35A4569E4529A3CDfB74e38FD98631',
                    # PENDLE
                    '0xA99F6e6785Da0F5d6fB42495Fe424BCE029Eeb3E',
                    # MORPHO
                    '0xBAa5CC21fd487B8Fcc2F632f3F4E8D37262a0842',
                    # 1INCH
                    '0xc5fecC3a29Fb57B5024eEc8a2239d4621e111CBE',
                    # cbETH
                    '0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22',
                    # SNX
                    '0x22e6966B799c4D5B13BE962E1D117b56327FDa66',
                    # ZRO
                    '0x6985884C4392D348587B19cb9eAAf157F13271cd',
                    # PRIME
                    '0xfA980cEd6895AC314E7dE34Ef1bFAE90a5AdD21b',
                    # SUPER
                    '0x391359ab0CCef572DcaC78F74E47D7C06Db0b982',
                    # YFI
                    '0x9EaF8C1E34F05a589EDa6BAfdF391Cf6Ad3CB239',
                    # FAI
                    '0xb33Ff54b9F7242EF1593d2C9Bcd8f9df46c77935',
                    # WMTX
                    '0x3e31966d4f81C72D2a55310A6365A56A4393E98D',
                    # COW
                    '0xc694a91e6b071bF030A18BD3053A7fE09B6DaE69',
                    # B3
                    '0xB3B32F9f8827D4634fE7d973Fa1034Ec9fdDB3B3',
                    # PHA
                    '0x336C9297AFB7798c292E9f80d8e566b947f291f0',
                    # VVV
                    '0xacfE6019Ed1A7Dc6f7B508C02d1b04ec88cC21bf',
                    # USDz
                    '0x04D5ddf5f3a8939889F11E97f8c4BB48317F1938',
                    # CFG
                    '0x2b51E2Ec9551F9B87B321f63b805871f1c81ba97',
                    # BTRST
                    '0xA7d68d155d17cB30e311367c2Ef1E82aB6022b67',
                    # OLAS
                    '0x54330d28ca3357F294334BDC454a032e7f353416',
                    # DEGEN
                    '0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed',
                    # BRETT
                    '0x532f27101965dd16442E59d40670FaF5eBB142E4',
                    # TOSHI
                    '0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4',
                    # SPX6900
                    '0x50dA645f148798F68EF2d7dB7C1CB22A6819bb2C',
                    # Mog
                    '0x2Da56AcB9Ea78330f947bD57C54119Debda7AF71',
                    # AIXBT
                    '0x4F9Fd6Be4a90f2620860d680c0d4d5Fb53d1A825',
                    # KAITO
                    '0x98d0baa52b2D063E780DE12F615f963Fe8537553'
                ]
            }

            list_of_token_names = {
                'eth': [
                    "Wrapped Ether",
                    "Liquid staked Ether 2.0",
                    "Wrapped BTC",
                    "ChainLink Token",
                    "Wrapped liquid staked Ether 2.0",
                    "Bitfinex LEO Token",
                    "USDS Stablecoin",
                    "USDe",
                    "Uniswap",
                    "MANTRA DAO",
                    "Wrapped eETH",
                    "Ondo",
                    "Pepe",
                    "PancakeSwap Token",
                    "Aave Token",
                    "ENA",
                    "Dai Stablecoin",
                    "Virtual Protocol",
                    "Worldcoin",
                    "Chain",
                    "FLOKI",
                    "Arkham",
                    "SAND",
                    "Mantle",
                    "Eigen",
                    "Pendle",
                    "Wrapped Filecoin",
                    "Arbitrum",
                    "Fetch",
                    "Curve DAO Token",
                    "First Digital USD",
                    "Cosmos",
                    "Injective Token",
                    "Lido DAO Token",
                    "Movement",
                    "Bonk",
                    "SPX6900",
                    "Mog Coin",
                    "Baby Doge Coin",
                    "Turbo",
                    "Memecoin",
                    "Neiro",
                    "Dogelon",
                    "Non-Playable Coin",
                    "Apu Apustaja",
                    "Andy",
                    "BONE SHIBASWAP",
                    "Milady",
                    "Wojak Coin",
                    "BOBO",
                    "PepeFork"
                ],
                'base': [
                    "Wrapped Ether",
                    "Wrapped BTC",
                    "Wrapped liquid staked Ether 2.0",
                    "USDS Stablecoin",
                    "MANTRA",
                    "USDe",
                    "Dai Stablecoin",
                    "Wrapped eETH",
                    "Aave Token",
                    "ENA",
                    "Rocket Pool ETH",
                    "Telcoin",
                    "Pyth Network",
                    "Virtual Protocol",
                    "Renzo Restaked ETH",
                    "Curve DAO Token",
                    "Aerodrome",
                    "Pendle",
                    "Morpho Token",
                    "1INCH Token",
                    "Coinbase Wrapped Staked ETH",
                    "Synthetix Network Token",
                    "LayerZero",
                    "Prime",
                    "SuperVerse",
                    "yearn.finance",
                    "FAI",
                    "WorldMobileToken",
                    "CoW Protocol Token",
                    "B3",
                    "Phala",
                    "Venice Token",
                    "USDz",
                    "Centrifuge",
                    "BTRST",
                    "Autonolas",
                    "Degen",
                    "Brett",
                    "Toshi",
                    "SPX6900",
                    "Mog Coin",
                    "aixbt by Virtuals",
                    "KAITO"
                ]
            }

            list_of_token_symbols = {
                'eth': [
                    "WETH",
                    "stETH",
                    "WBTC",
                    "LINK",
                    "wstETH",
                    "LEO",
                    "USDS",
                    "USDe",
                    "UNI",
                    "OM",
                    "weETH",
                    "ONDO",
                    "PEPE",
                    "Cake",
                    "AAVE",
                    "ENA",
                    "DAI",
                    "VIRTUAL",
                    "WLD",
                    "XCN",
                    "FLOKI",
                    "ARKM",
                    "SAND",
                    "MNT",
                    "EIGEN",
                    "PENDLE",
                    "WFIL",
                    "ARB",
                    "FET",
                    "CRV",
                    "FDUSD",
                    "ATOM",
                    "INJ",
                    "LDO",
                    "MOVE",
                    "Bonk",
                    "SPX",
                    "Mog",
                    "BabyDoge",
                    "TURBO",
                    "MEME",
                    "Neiro",
                    "ELON",
                    "NPC",
                    "APU",
                    "ANDY",
                    "BONE",
                    "LADYS",
                    "WOJAK",
                    "BOBO",
                    "PORK"
                ],
                'base': [
                    'WETH',
                    "WBTC",
                    "wstETH",
                    "USDS",
                    "OM",
                    "USDe",
                    "DAI",
                    "weETH",
                    "AAVE",
                    "ENA",
                    "rETH",
                    "TEL",
                    "PYTH",
                    "VIRTUAL",
                    "ezETH",
                    "CRV",
                    "AERO",
                    "PENDLE",
                    "MORPHO",
                    "1INCH",
                    "cbETH",
                    "SNX",
                    "ZRO",
                    "PRIME",
                    "SUPER",
                    "YFI",
                    "FAI",
                    "WMTX",
                    "COW",
                    "B3",
                    "PHA",
                    "VVV",
                    "USDz",
                    "CFG",
                    "BTRST",
                    "OLAS",
                    "DEGEN",
                    "BRETT",
                    "TOSHI",
                    "SPX",
                    "Mog",
                    "AIXBT",
                    "KAITO"
                ]
            }

            self.lotr = list_of_tokens_raw

            eth_list_of_token_images = [
                self.tokenimgfolder
                + symbol.lower()
                + '.png'
                for symbol in list_of_token_symbols['eth']
            ]

            base_list_of_token_images = [
                self.tokenimgfolder
                + symbol.lower()
                + '.png'
                for symbol in list_of_token_symbols['base']
            ]

            swap_token_details = {
                'address': {
                    'eth': list_of_tokens_raw['eth'],
                    'base': list_of_tokens_raw['base'],
                },
                'name': {
                    'eth': list_of_token_names['eth'],
                    'base': list_of_token_names['base'],
                },
                'symbol':{
                    'eth': list_of_token_symbols['eth'],
                    'base': list_of_token_symbols['base'],
                },
                'image': {
                    'eth': eth_list_of_token_images,
                    'base': base_list_of_token_images
                },
            }

            if not os.path.exists(
                self.dest_path
                + 'swap_token_details.json',
            ):
                with open(
                    self.dest_path
                    + 'swap_token_details.json',
                    mode='w'
                ) as f:
                    json.dump(
                        obj=swap_token_details,
                        fp=f,
                        indent=4
                    )

            # Free up memory
            #del list_of_tokens_raw
            del list_of_token_names
            del list_of_token_symbols
            del eth_list_of_token_images
            del base_list_of_token_images
            del swap_token_details

            # Assets details
            self.asset_details = {
                'eth': {
                    "value": [],
                    "price": [],
                },
                'base': {
                    "value": [],
                    "price": [],
                }
            }

            self.contactbook = {
                "name": [],
                "address": []
            }

            self.contactsjson = self.dest_path + "contacts.json"

            if (
                not os.path.exists(self.contactsjson)
                or os.stat(self.contactsjson).st_size == 0
            ):
                with open(self.contactsjson, "w") as f:
                    json.dump(
                        obj=self.contactbook,
                        fp=f,
                        indent=4
                    )

            else:
                with open(self.contactsjson, "r") as f:
                    self.contactbook = json.load(f)

            self.rpc_list = {
                'eth': [
                    "https://ethereum-rpc.publicnode.com",
                    "https://rpc.mevblocker.io",
                    "https://rpc.mevblocker.io/fast",
                    "https://rpc.ankr.com/eth",
                    "https://rpc.flashbots.net",
                    "https://1rpc.io/eth",
                ],
                'base': 'https://base-pokt.nodies.app'
            }

            self.rpc_list_file = self.dest_path + "rpc_list.json"

            if (
                not os.path.exists(self.rpc_list_file)
                or os.stat(self.rpc_list_file).st_size == 0
                # Older rpc file
                or not isinstance(
                    json.load(
                        open(self.rpc_list_file, mode='r')
                    ),
                    dict,
                )
            ):
                with open(self.rpc_list_file, "w") as f:
                    json.dump(
                        obj=self.rpc_list,
                        fp=f,
                        indent=4
                    )

            # Mnemonic phrase
            Account.enable_unaudited_hdwallet_features()
            self.mnemonic_phrase = generate_mnemonic_phrase()

            self.is_new = True
            self.nameofwallet = ""
            self.from_experienced = False
            self.opened_from_wallet = False
            self.from_mnemonic = False
            self.from_private_key = False
            self.new_wallet = False
            self.switched_wallets = False
            self.used_import_wallet_from_userwallet = False
            self.invoked_from_settings = False

            '''
            Used when switching wallets
            so that the user can go back
            to the wallet that they were on
            '''
            self.reserved_nameofwallet = ''

             # New in v2.0
            self.eth_price = '0.0'

            # New in v2.0
            self.eth_amount = '0.0'
            self.base_eth_amount = '0.0'

            # New in v3.1
            self.eth_gas = '0.0'
            self.base_gas = '0.0'

            # New in v3.1
            self.total_balance = 0.0
            self.total_base_balance = 0.0

    prog = GlobalVariable()

    # BEGIN Web3-related stuff
    web3_provider = Web3.HTTPProvider(
        #endpoint_uri='https://eth-mainnet.g.alchemy.com/v2/AQCB0XL4kYRidnAaVmqs_uOxAY8MOmyB',
        endpoint_uri=prog.configs["rpc"]['eth'],
        exception_retry_configuration=None,
        request_kwargs={
            "timeout": (35, 10),
            "allow_redirects": False
        },
        session=s,
    )

    base_web3_provider = Web3.HTTPProvider(
        endpoint_uri='https://base-rpc.publicnode.com',
        exception_retry_configuration=None,
        request_kwargs={
            "timeout": (25, 10),
            "allow_redirects": False
        },
        session=s,
    )

    # https://web3py.readthedocs.io/en/v7.9.0/troubleshooting.html#how-can-i-optimize-ethereum-json-rpc-api-access
    # except I am using orjson, instead of ujson
    def _fast_decode_rpc_response(raw_response: bytes):
        from web3.providers import JSONBaseProvider
        from web3.types import RPCResponse
        from typing import cast

        decoded = orjson.loads(raw_response)
        return cast(RPCResponse, decoded)

    def patch_provider(provider) -> None:
        provider.decode_rpc_response = _fast_decode_rpc_response

    patch_provider(web3_provider)
    #patch_provider(base_web3_provider)

    w3 = Web3(web3_provider)
    base_w3 = Web3(base_web3_provider)

    w3.strict_bytes_type_checking = False
    base_w3.enable_strict_bytes_checking = False

    def create_contract(
        address: str,
        abi=prog.abi,
        chain='eth'
    ) -> w3.eth.contract:
        # Return contract based off of chain
        if chain == 'base':
            return base_w3.eth.contract(
                address=w3.to_checksum_address(address),
                abi=abi
            )

        return w3.eth.contract(
            address=w3.to_checksum_address(address),
            abi=abi
        )

    def token_balance(
        address,
        contract=None
    ) -> float:
        return contract.functions.balanceOf(address).call()

    def token_image(
        address,
        chain='eth'
    ) -> None:
        if chain == 'eth':
            try:
                contract = create_contract(
                    address,
                    chain='eth'
                )

            except ValueError:
                return

            try:
                sym = contract.functions.symbol().call()

                if os.path.exists(
                    prog.tokenimgfolder
                    + f"{sym.lower()}.png"
                ):
                    return

            except Exception:
                return

        elif chain == 'base':
            try:
                contract = create_contract(
                    address,
                    chain='base'
                )

            except Exception:
                return

            try:
                sym = contract.functions.symbol().call()

                if os.path.exists(
                    prog.tokenimgfolder
                    + f"{sym.lower()}.png"
                ):
                    return

            except Exception:
                return

        # The proper name for the chain
        if chain == 'eth':
            chain = 'ethereum'

        agent = (
            'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) ' 
            'Gecko/20100101 Firefox/136.0'
        )

        headers = {
            "User-Agent": agent,
            'Content-Type': 'application/json'
        }

        url = (
            'https://raw.githubusercontent.com/trustwallet/assets/'
            f"refs/heads/master/blockchains/{chain}/assets/"
        )
        
        addr = w3.to_checksum_address(address)

        resp = s.get(f"{url}{addr}/logo.png", headers=headers)

        if (
            resp.status_code == 404 
            or resp.status_code == 400
        ):
            url = f"https://{chain}.blockscout.com/api/v2/tokens/{addr}"

            try:
                resp = s.get(url)
                resp = orjson.loads(resp_raw.text)
                img_url = orjson.loads(resp_raw.text)['icon_url']

                resp = s.get(img_url)
            except requests.exceptions.MissingSchema:
                return


        path = prog.tokenimgfolder + f"{sym.lower()}.png"

        with open(path, "wb") as out_file:
            out_file.write(resp.content)

    # Polished and shortened in v3.1
    def get_price(From) -> str:
        """
        Fetches asset price in USDT.

        Currently, this function only converts to USDT.

        This function will undergo changes in the
        future (i.e converting to yen, franc, other crypto, etc)

        If the default url is rate-limiting the user, it switches
        to the back-up url. This should suffice, for now.
        """

        if From.lower() == 'ccbtc':
            From = 'btc'

        default_url = (
            'https://min-api.cryptocompare.com/data/price?fsym='
            f"{From}&tsyms=USDT"
        )

        backup_url = (
            f"https://api.coinbase.com/v2/exchange-rates?currency={From}"
        )

        try:
            # Fetch price from default url
            page_data = s.get(default_url)

            resp = orjson.loads(page_data.text)
            resp = rm_e_notation(resp["USDT"])

            return resp

        # If there was an error, fetch price from back up url
        except Exception:
            try:
                page_data = s.get(backup_url)

                resp = orjson.loads(page_data.text)
                resp = rm_e_notation(resp["data"]["rates"]["USDT"])

                return resp

            # If there was an error, return '0.0'
            except Exception:
                return '0.0'

    def get_eth_price() -> str:
        return get_price("ETH")

    def get_price_from_list(symbols: list) -> list:
        result_list = [
            get_price(item)
            for item in symbols
        ]
        
        return result_list

    # BEGIN kkk
    def __load_base_assets_price() -> None:
        price_list = get_price_from_list(
            prog.asset['eth']['symbol']
        )

        prog.asset_details['base']['price'] = [
            str(price)[:18]
            for price in price_list
        ]

    _base_assets_price = Thread(
        target=__load_base_assets_price
    )
    _base_assets_price.start()

    def __load_eth_asset_prices() -> None:
        price_list = get_price_from_list(
            prog.asset['eth']['symbol']
        )

        prog.asset_details['eth']['price'] = [
            str(price[:18])
            for price in price_list
        ]

    _load_eth_asset_prices = Thread(
        target=__load_eth_asset_prices,
        daemon=True
    )
    # END kkk

    _load_eth_asset_prices.start()
    # END Web3-related stuff

    # Images
    class TigerWalletImage:
        def __init__(self):
            app = QApplication([])
            self.setup_images()

        def setup_images(self):
            # TigerWallet logo
            self.tigerwallet_logo = QIcon(
                prog.imgfolder
                + "tigerwallet_logo.png"
            )

            # Ethereum logo
            self.eth_img = QIcon(
                prog.imgfolder
                + "eth.png"
            )

            # Base logo
            self.base_img = QIcon(
                prog.imgfolder
                + "base.png"
            )

            # Home
            self.home_blue = QIcon(
                prog.imgfolder + "icons8-home_blue.png"
            )

            # Loading background
            self.loading_bg = prog.imgfolder + "loading-bg.png"
            self.feelsbad = QIcon(prog.imgfolder + "feelsbadman.png")

            """===== https://emojipedia.org/ ===="""
            # Open mouth emoji
            self.shocked_img = QIcon(
                prog.imgfolder + "face-with-open-mouth_1f62e.png"
            )

            """==Icons-8 ===="""
            # Glasses emoji
            self.cool_blue = QIcon(
                prog.imgfolder + "icons8-cool-blue.png"
            )

            # Next arrow
            self.continue_ = QIcon(
                prog.imgfolder + "icons8-next-32.png"
            )

            # Back arrow
            self.back = QIcon(
                prog.imgfolder + "icons8-go-back-48.png"
            )

            # Close regular
            self.close = QIcon(
                prog.imgfolder + "icons8-close-32.png"
            )

            # Close blue
            self.close_blue = QIcon(
                prog.imgfolder + "icons8-close-blue.png"
            )

            # Close blue2
            self.close_blue2 = QIcon(
                prog.imgfolder + "icons8-close-blue2.png"
            )

            # Hide pass image
            self.closed_eye_blue = QIcon(
                prog.imgfolder + "icons8-eyes-closed-blue.png"
            )

            # Show pass image
            self.opened_eye = QIcon(
                prog.imgfolder + "icons8-eyes.png"
            )

            self.opened_eye_blue = QIcon(
                prog.imgfolder + "icons8-eyes-blue.png"
            )

            # Clipboard image blue
            self.copy_blue = QIcon(
                prog.imgfolder + "icons8-copy-blue.png"
            )

            # History blue
            self.history_blue = QIcon(
                prog.imgfolder + "icons8-history-blue.png"
            )

            self.refresh_blue = QIcon(
                prog.imgfolder + "icons8-refresh-blue.png"
            )

            # Swap image blue
            self.swap_blue = QIcon(
                prog.imgfolder + "icons8-swap-blue.png"
            )

            # Blue Wallet icon
            self.wallet_blue = QIcon(
                prog.imgfolder + "icons8-wallet-blue.png"
            )

            # Address book 1 blue
            self.address_book_blue = QIcon(
                prog.imgfolder + "icons8-open-book-blue.png"
            )

            # Send crypto icon
            self.send_blue = QIcon(
                prog.imgfolder + "icons8-right-arrow-blue.png"
            )

            # Receive crypto icon
            self.receive_blue = QIcon(
                prog.imgfolder + "icons8-left-arrow-blue.png"
            )

            # Delete contact icon
            self.delete_blue = QIcon(
                prog.imgfolder + "icons8-minus-blue.png"
            )

            # Add contact icon
            self.plus_blue = QIcon(
                prog.imgfolder + "icons8-plus-blue.png"
            )

            # Settings
            self.settings_blue = QIcon(
                prog.imgfolder + "icons8-settings-blue.png"
            )

            # RPC
            self.rpc_blue = QIcon(
                prog.imgfolder + "icons8-server-blue.png"
            )

            self.rpc = QIcon(
                prog.imgfolder + "icons8-server.png"
            )

            # Pass
            self.pass_blue = QIcon(
                prog.imgfolder + "icons8-password-pass-blue.png"
            )

            # Sun (light mode)
            self.sun_blue = QIcon(
                prog.imgfolder + "icons8-sun-blue.png"
            )

            # Moon (dark mode)
            self.moon_blue = QIcon(
                prog.imgfolder + "icons8-half-moon-blue.png"
            )

            # Private key
            self.key_blue = QIcon(
                prog.imgfolder + "icons8-key-blue.png"
            )

            # Donation icon
            self.donate_blue = QIcon(
                prog.imgfolder + "icons8-donate-blue.png"
            )

            self.about_blue = QIcon(
                prog.imgfolder + "icons8-question-blue.png"
            )

            # Lock
            self.lock_blue = QIcon(
                prog.imgfolder + "icons8-lock-blue.png"
            )

            self.checkmark = QIcon(
                prog.imgfolder + 'icons8-checkmark-blue.png'
            )

            self.gif_blue = QIcon(
                prog.imgfolder + 'icons8-gif-blue.png'
            )

            self.arrow_down_blue = QIcon(
                prog.imgfolder + 'icons8-arrow-down-blue.png'
            )
            
            self.restore_blue = QIcon(
                prog.imgfolder + 'icons8-restore-blue.png'
            )

            self.blue_robot = QIcon(
                prog.imgfolder + 'icons8-robot-blue.png'
            )

    TigerWalletImage = TigerWalletImage()

    # First screen
    class FirstWindow(QWidget):
        def __init__(self):
            super().__init__()

            # Main
            self.setup_main()
            # Label that is at the top of the screen
            self.init_label()
            # Text in the middle
            self.init_label2()
            # New to crypto button
            self.init_btn1()
            # User has previous experience button
            self.init_btn2()

            self.btn1.clicked.connect(self.launchwalletname)
            self.btn2.clicked.connect(self.launchuserwithexperience)

            if "default" in prog.configs["theme"]:
                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + 'background: transparent;'
                )

            # Default theme
            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")

                self.label2.setStyleSheet(
                    "font-size: 16px;"
                    "color: #c5d4e7;"
                    "border: 1px solid #1e2b45;;"
                    "border-radius: 8px;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )


            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label2.setStyleSheet(
                    "font-size: 17px;"
                    "color: #3c598e;"
                    "border: 1px solid #1e2b45;;"
                    "border-radius: 8px;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

        # Window UI
        def setup_main(self):
            self.setFixedWidth(580)
            self.setFixedHeight(320)
            self.setWindowTitle("TigerWallet  -  Welcome")
            align_to_center(self)

        # Topmost label
        def init_label(self):
            self.label = QLabel("Welcome! ", self)
            self.label.resize(580, 80)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label in the middle
        def init_label2(self):
            text = (
                "TigerWallet is a non-custodial wallet on the"
                "Ethereum chain. \n You own your crypto assets!"
                "Your private key never leaves this device. \n"
                "Your private key is encrypted."
            )

            self.label2 = QLabel(
                text=text,
                parent=self
            )
            self.label2.resize(540, 120)
            self.label2.setWordWrap(True)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label2.move(20, 80)

        # New to crypto button
        def init_btn1(self):
            self.btn1 = QPushButton(
                text=" I'm new to crypto!",
                parent=self,
                icon=TigerWalletImage.shocked_img,
            )

            self.btn1.setFixedSize(240, 56)
            self.btn1.setIconSize(QSize(28, 28))
            self.btn1.move(32, 226)

        # Experienced user button
        def init_btn2(self):
            self.btn2 = QPushButton(
                text="Import",
                parent=self,
                icon=TigerWalletImage.cool_blue
            )

            self.btn2.setFixedSize(266, 56)
            self.btn2.setIconSize(QSize(28, 28))
            self.btn2.move(281, 226)

        def launchwalletname(self):
            prog.is_new = True

            self.wnap = WalletNameAndPassword()
            self.wnap.show()
            self.close()
            self.deleteLater()

        def launchuserwithexperience(self):
            self.uwe = UserWithExperience()
            self.uwe.show()
            self.close()
            self.deleteLater()

    class UserWithExperience(QWidget):
        def __init__(self, master=None):
            super().__init__()
            self.master = master

            self.init_window()
            self.init_recovery_options()
            self.init_return()
            self.init_continue()

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.ret.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.continue_.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.msg.setStyleSheet(
                    "font-size: 26px;"
                    + "color: #9fb1ca;"
                    + "background: transparent;"
                )

                self.import_via_pkey.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

                self.import_via_phrase.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

                self.import_tigw.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.ret.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.continue_.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.msg.setStyleSheet(
                    "font-size: 26px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.import_via_pkey.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

                self.import_via_phrase.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

                self.import_tigw.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

        def init_window(self):
            self.setFixedWidth(500)
            self.setFixedHeight(480)
            self.setWindowTitle("TigerWallet  -  Experienced user")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(481, 450)
            self.border.move(9, 18)

            if not prog.used_import_wallet_from_userwallet:
                text = (
                    "Oh, so you have experience, huh?\n"
                    + "Ok, so what would you like to do?"
                )

                self.msg = QLabel(
                    text=text,
                    parent=self
                )
                self.msg.resize(440, 120)
                self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msg.move(26, 30)

            else:
                text = 'Select how you want to import a wallet'

                self.msg = QLabel(
                    text=text,
                    parent=self
                )
                self.msg.resize(340, 120)
                self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msg.move(76, 30)
                self.msg.setWordWrap(True)

        def init_recovery_options(self):
            self.opt = 0

            secret_phrase_text = \
                "Import from secret phrase (12 words only)"

            # Recovery phrase
            self.import_via_phrase = QRadioButton(
                text=secret_phrase_text,
                parent=self
            )

            self.import_via_phrase.setGeometry(48, 157, 400, 70)
            self.import_via_phrase.toggled.connect(
                lambda: self._setchoice(1)
            )

            # Recovery key
            self.import_via_pkey = QRadioButton(
                text="Import from private key",
                parent=self
            )

            self.import_via_pkey.setGeometry(48, 226, 400, 70)
            self.import_via_pkey.toggled.connect(
                lambda: self._setchoice(2)
            )

            # tigw file
            self.import_tigw = QRadioButton(
                text="Import .tigw file",
                parent=self
            )

            self.import_tigw.setGeometry(48, 295, 400, 70)
            self.import_tigw.toggled.connect(
                lambda: self._setchoice(3)
            )

        def _setchoice(self, choice):
            self.opt = choice

        def init_return(self):
            self.ret = QPushButton(
                text=" Return    ",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.ret.setFixedSize(170, 44)
            self.ret.setIconSize(QSize(28, 28))
            self.ret.move(54, 396)
            self.ret.clicked.connect(self.return_to_first_window)

        def init_continue(self):
            self.continue_ = QPushButton(
                text="Continue ",
                parent=self,
                icon=TigerWalletImage.send_blue
            )

            self.continue_.setFixedSize(170, 44)
            self.continue_.setIconSize(QSize(28, 28))
            self.continue_.move(274, 396)
            self.continue_.clicked.connect(self.continue_import)
            self.continue_.setLayoutDirection(
                QtCore.Qt.LayoutDirection.RightToLeft
            )

        def continue_import(self):
            if self.opt == 0:
                errbox("No option was selected")
                return

            elif self.opt == 1:
                prog.from_experienced = True
                self.rwfp = RecoverWalletFromPhrase()
                self.rwfp.show()
                self.close()
                self.deleteLater()

            elif self.opt == 2:
                prog.from_experienced = True
                self.rwfpk = RecoverWalletFromPrivateKey()
                self.rwfpk.show()
                self.close()
                self.deleteLater()

            elif self.opt == 3:
                prog.from_experienced = True

                file_chooser = QFileDialog.getOpenFileName(
                    self,
                    "Open a TigerWallet file",
                    prog.dest_path,
                    "tigerwallet file (*.tigw)",
                )

                if len(file_chooser[0]) == 0:
                    return

                # File path doesn't contain \ on Windows (thankfully)
                prog.nameofwallet = file_chooser[0]

                self.vp = ValidatePassword()
                self.vp.show()
                self.close()
                self.deleteLater()

        def return_to_first_window(self):
            if prog.used_import_wallet_from_userwallet:
                prog.used_import_wallet_from_userwallet = False
                self.master.stacked_layout.setCurrentIndex(0)
                return

            self.fw = FirstWindow()
            self.fw.show()
            self.close()
            self.deleteLater()

    ##@=== New in v2.0 ===@##
    # Fixed a BUG where wallet was not saving properly in v3.1
    # Fixed a BUG where program crashed when pressing continue in v3.1
    # Wallet name and password
    class WalletNameAndPassword(QWidget):
        def __init__(self, master=None):
            super().__init__()
            self.master = master

            self.init_self()
            self.init_buttons()
            self.init_showhidepass_buttons()
            self.init_fields()

            if 'default' in prog.configs['theme']:
                self.btn_showhide1.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn_showhide2.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.label2.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #c5d4e7;"
                    + "background: transparent;"
                )

                for i in range(3):
                    self.entry_field_label[i].setStyleSheet(
                        "font-size: 16px;"
                        + "color: #9fb1ca;"
                    )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            elif  prog.configs["theme"] == "default_light":
                self.setStyleSheet("background: #eff1f3")
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #eff1f3;"
                )

                self.label2.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                for i in range(3):
                    self.entry_field_label[i].setStyleSheet(
                        "font-size: 16px;"
                        + "color: #0a0f18;"
                    )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

        def init_self(self):
            self.setFixedWidth(650)
            self.setFixedHeight(400)
            self.setWindowTitle("TigerWallet  -  Welcome")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(630, 346)
            self.border.move(10, 44)

            self.label = QLabel("Create new wallet", self)
            self.label.resize(350, 50)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(148, 18)

            self.label2 = QLabel(
                text="Please enter a name and a password for your wallet",
                parent=self
            )
            self.label2.resize(440, 48)
            self.label2.move(102, 70)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_fields(self):
            self.opt1 = 1
            self.opt2 = 1

            self.entry_field = [QLineEdit(self) for i in range(3)]
            self.entry_field_label = [QLabel(self) for i in range(3)]

            for i in range(3):
                self.entry_field[i].resize(380, 36)
                self.entry_field_label[i].resize(140, 20)

            # Name
            self.entry_field_label[0].setText('Wallet Name:')
            self.entry_field_label[0].move(34, 136)
            self.entry_field[0].move(180, 130)

            # Password
            self.entry_field_label[1].setText('Password:')
            self.entry_field_label[1].move(34, 190)
            self.entry_field[1].move(180, 185)
            self.entry_field[1].setEchoMode(
                QLineEdit.EchoMode.Password
            )

            # Repeat password
            self.entry_field_label[2].setText('Repeat password:')
            self.entry_field_label[2].move(34, 244)
            self.entry_field[2].move(180, 240)
            self.entry_field[2].setEchoMode(
                QLineEdit.EchoMode.Password
            )

        def init_showhidepass_buttons(self):
            self.btn_showhide1 = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_showhide1.setIconSize(QSize(28, 28))
            self.btn_showhide1.move(580, 190)
            self.btn_showhide1.clicked.connect(self.unhide1)

            self.btn_showhide2 = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_showhide2.setIconSize(QSize(28, 28))
            self.btn_showhide2.move(580, 244)
            self.btn_showhide2.clicked.connect(self.unhide2)

        def init_buttons(self):
            self.btn1 = QPushButton(
                text=" Return   ",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.btn1.setFixedSize(240, 56)
            self.btn1.setIconSize(QSize(48, 48))
            self.btn1.move(80, 302)
            self.btn1.clicked.connect(self.ret)

            self.btn2 = QPushButton(
                text="Continue ",
                parent=self,
                icon=TigerWalletImage.send_blue
            )

            self.btn2.setFixedSize(240, 56)
            self.btn2.setIconSize(QSize(48, 48))
            self.btn2.move(330, 302)
            self.btn2.setLayoutDirection(
                QtCore.Qt.LayoutDirection.RightToLeft
            )
            self.btn2.clicked.connect(
                lambda: self.continue_(
                    self.entry_field[0].text(), # Wallet name
                    self.entry_field[1].text(), # Password
                    self.entry_field[2].text(), # Repeat password
                )
            )


        def continue_(
            self,
            wallet_name,
            password,
            repeat_password
        ):
            if len(wallet_name) == 0:
                errbox('Wallet must have a name')
                return

            elif len(wallet_name) > 254:
                errbox(
                    "Wallet name cannot be longer than 255 characters"
                )

            elif "\n" in wallet_name:
                errbox("Character \\n is not allowed")

            if len(password) == 0:
                errbox('Please enter a password for your wallet')
                return

            if password != repeat_password:
                errbox('Passwords did not match')
                return

            wallet_name = prog.dest_path + wallet_name
            
            if wallet_name in prog.configs["wallets"]:
                errbox(f"{wallet_name} already exists")
                return


            if _platform() == 'nt':
                wallet_name = wallet_name.replace('\\', '/')

            if wallet_name.find(".tigw") == -1:
                wallet_name += ".tigw"

            prog.nameofwallet = wallet_name
            
            if (
                not prog.from_mnemonic
                and not prog.from_private_key
            ):                
                prog.account = Account.from_mnemonic(
                    prog.mnemonic_phrase
                )

                encrypted = Account.encrypt(
                    prog.account.key,
                    password=password
                )

                prog.configs["wallets"].append(
                        prog.nameofwallet
                    )

                with open(prog.nameofwallet, "w") as f:
                    json.dump(encrypted, f)
                    
                self.close()
                self.mnemonic = None

                if self.master is  None:
                    self.deleteLater()
                    self.mnemonic = MnemonicPhraseWindow()

                else:
                    self.hide()
                    self.mnemonic = MnemonicPhraseWindow(self)

                self.mnemonic.show()

            elif prog.from_mnemonic:
                self.encrypted = Account.encrypt(
                    prog.account.key,
                    password=password
                )

                with open(prog.conf_file, "w") as ff:
                    prog.configs["wallets"].append(prog.nameofwallet)
                    json.dump(
                        obj=prog.configs,
                        fp=ff,
                        indent=4
                    )

                    with open(prog.nameofwallet, "w") as f:
                        json.dump(self.encrypted, f)

                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()

            elif prog.from_private_key:
                self.encrypted = Account.encrypt(
                    prog.account.key, 
                    password=password
                )

                with open(prog.conf_file, "w") as ff:
                    prog.configs["wallets"].append(prog.nameofwallet)
                    json.dump(
                        obj=prog.configs,
                        fp=ff,
                        indent=4
                    )

                    with open(prog.nameofwallet, "w") as f:
                        json.dump(self.encrypted, f)

                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()

        def unhide1(self):
            if self.opt1 == 1:
                self.btn_showhide1.setIcon(TigerWalletImage.opened_eye_blue)
                self.entry_field[1].setEchoMode(
                    QLineEdit.EchoMode.Normal
                )

                self.opt1 = 0

            elif self.opt1 == 0:
                self.btn_showhide1.setIcon(TigerWalletImage.closed_eye_blue)
                self.entry_field[1].setEchoMode(
                    QLineEdit.EchoMode.Password
                )

                self.opt1 = 1

        def unhide2(self):
            if self.opt2 == 1:
                self.btn_showhide2.setIcon(TigerWalletImage.opened_eye_blue)
                self.entry_field[2].setEchoMode(
                    QLineEdit.EchoMode.Normal
                )

                self.opt2 = 0

            elif self.opt2 == 0:
                self.btn_showhide2.setIcon(TigerWalletImage.closed_eye_blue)
                self.entry_field[2].setEchoMode(
                    QLineEdit.EchoMode.Password
                )

                self.opt2 = 1

        def ret(self):
            if prog.from_mnemonic:
                prog.from_mnemonic = False

                self.rwfp = RecoverWalletFromPhrase()
                self.rwfp.show()
                self.close()
                self.deleteLater()
                return

            elif prog.from_private_key:
                prog.from_private_key = False

                self.rwfpk = RecoverWalletFromPrivateKey()
                self.rwfpk.show()
                self.close()
                self.deleteLater()
                return

            elif prog.new_wallet:
                self.master.stacked_layout.setCurrentIndex(0)
                prog.new_wallet = False

                [self.entry_field[i].clear() for i in range(3)]
                return

            elif not prog.opened_from_wallet:
                prog.opened_from_wallet = False

                self.fw = FirstWindow()
                self.fw.show()
                self.close()
                self.deleteLater()
                return

    # Login window
    class Login(QWidget):
        def __init__(self):
            super().__init__()

            self.init_window()
            self.init_label()
            self.init_wallet_selection()
            self.init_passfield()
            self.init_eye_btn()
            self.init_login_btn()
            self.init_forgot_pass()

            self.login.clicked.connect(self.login_to_wallet)
            self.entry.returnPressed.connect(self.login_to_wallet)

            if "default" in prog.configs["theme"]:
                self.btn_showhide.setStyleSheet(
                    "QPushButton{background-color: none;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #1e1e1e;}"
                )
                
                self.login.setStyleSheet(
                    "QPushButton{background-color: #627eea;"
                    + "border-radius: 24px;"
                    + "font-size: 23px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #627eea;}"
                )

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18;")
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.forgotpass.setStyleSheet(
                    "QPushButton{background-color:  #0a0f18;"
                    + "font-size: 20px;"
                    + "border-radius: 0px;"
                    + "color: #778ba5}"
                    + "QPushButton::hover{background-color: #1e1e1e;"
                    + "color: #627eea;"
                    + 'border-radius: 8px;}'

                )

                fix_white_borders([self.selection])

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #eff1f3;"
                )

                self.forgotpass.setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "font-size: 20px;"
                    + "border-radius: 0px;"
                    + "color: #778ba5}"
                    + "QPushButton::hover{background-color: #eff1f3;"
                    + "color: #627eea;}"
                )

        def init_window(self):
            self.setFixedWidth(500)
            self.setFixedHeight(410)
            
            self.border = QLabel(self)
            self.border.resize(481, 352)
            self.border.move(9, 50)
            
            self.setWindowTitle("Login")
            align_to_center(self)
            self.opt = 1

            self.fp = ForgotPassword()

        # Topmost label
        def init_label(self):
            self.label = QLabel("Welcome back!!", self)
            self.label.resize(316, 50)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(91, 26)

        def init_wallet_selection(self):
            # TODO: Make last item appear first on the list
            self.selection = QComboBox(self)
            self.selection.resize(448, 50)
            self.selection.move(26, 110)
            self.selection.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.selection.setAttribute(
                Qt.WidgetAttribute.WA_MacShowFocusRect,
                False
            )

            self.qlist = QtWidgets.QListView(self.selection)

            self.shortname = ""

            for i in range(len(prog.configs["wallets"])):
                self.shortname = prog.configs["wallets"][i]

                if "\\" in self.shortname:
                    self.shortname = self.shortname[
                        self.shortname.rfind("\\") + 1 : len(self.shortname)
                    ]

                else:
                    self.shortname = self.shortname[
                        self.shortname.rfind("/") + 1 : len(self.shortname)
                    ]

                self.selection.insertItem(i, self.shortname)


            del self.shortname
            self.selection.setView(self.qlist)

        def init_passfield(self):
            self.entry = QLineEdit(self)
            self.entry.setPlaceholderText("Enter your password")
            self.entry.move(32, 190)
            self.entry.resize(391, 38)
            self.entry.setEchoMode(QLineEdit.EchoMode.Password)

        def init_eye_btn(self):
            self.btn_showhide = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_showhide.setIconSize(QSize(24, 24))
            self.btn_showhide.move(438, 197)
            self.btn_showhide.clicked.connect(self.unhide)

        def init_login_btn(self):
            self.login = QPushButton("Login", self)
            self.login.setFixedSize(436, 48)
            self.login.move(32, 260)

        def init_forgot_pass(self):
            self.forgotpass = QPushButton(
                text=" Forgot password",
                parent=self,
                icon=TigerWalletImage.feelsbad,
            )

            self.forgotpass.setFixedSize(200, 46)
            self.forgotpass.setIconSize(QSize(28, 28))
            self.forgotpass.move(152, 328)
            self.forgotpass.clicked.connect(
                lambda: [
                    self.fp.show(),
                    self.close(),
                    self.deleteLater()
                ]
            )

        def unhide(self):
            if self.opt == 1:
                self.btn_showhide.setIcon(TigerWalletImage.opened_eye_blue)
                self.entry.setEchoMode(QLineEdit.EchoMode.Normal)
                self.opt = 0

            elif self.opt == 0:
                self.btn_showhide.setIcon(TigerWalletImage.closed_eye_blue)
                self.entry.setEchoMode(QLineEdit.EchoMode.Password)
                self.opt = 1

        def login_to_wallet(self):
            index = self.selection.currentIndex()
            self.choice = prog.configs["wallets"][index]

            prog.nameofwallet = self.choice

            if len(self.entry.text()) == 0:
                errbox("Password field is empty")
                return

            try:
                with open(self.choice, "r") as f:
                    prog.account = Account.from_key(
                        Account.decrypt(
                            json.load(f),
                            password=self.entry.text()
                        )
                    )

                    with open(prog.conf_file, "w") as ff:
                        if not self.choice in prog.configs["wallets"]:
                            prog.configs["wallets"].append(self.choice)

                        json.dump(
                            obj=prog.configs,
                            fp=ff,
                            indent=4
                        )

            except ValueError:
                errbox("Incorrect password. Try again")
                return

            if len(prog.asset['eth']['address']) != 0:
                self.alb = AssetLoadingBar()
                self.alb.show()
                self.close()
                self.deleteLater()
            else:
                """
                If user decided to remove all
                assets, only load Ether data.

                This does not require loading
                the AssetLoadingBar class.
                """
                self.uw = UserWallet()
                self.uw.show()
                self.close()
                self.deleteLater()

    # Forgot password
    class ForgotPassword(QWidget):
        def __init__(self):
            super().__init__()

            self.init_window()
            self.init_top_label()
            self.init_recover_msg()
            self.init_recovery_options()
            self.init_return()
            self.init_continue()

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.ret.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.continue_.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.msg.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #9fb1ca;"
                    + "background: transparent;"
                )

                self.phrase_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #9fb1ca;"
                    + "border-radius: 16px;"
                )

                self.pkey_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #9fb1ca;"
                    + "border-radius: 16px;"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #eff1f3;"
                )

                self.ret.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.continue_.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.msg.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.phrase_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #b0c4de;"
                    + "border-radius: 16px;"
                )

                self.pkey_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #b0c4de;"
                    + "border-radius: 16px;"
                )

        def init_window(self):
            self.setFixedWidth(500)
            self.setFixedHeight(476)
            self.setWindowTitle("TigerWallet  -  Recover account")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(481, 408)
            self.border.move(9, 58)

        def init_top_label(self):
            self.label = QLabel("Account Recovery", self)
            self.label.resize(348, 61)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(78, 26)

        def init_recover_msg(self):
            text = (
                "It's ok, it happens!\n\n"
                + "Because of the non-custodial nature of this wallet,\n"
                + "TigerWallet cannot recover your password.\n"
                + "You only have the following two options:"
            )

            self.msg = QLabel(
                text=text,
                parent=self,
            )

            self.msg.resize(440, 140)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(26, 80)

        def init_recovery_options(self):
            self.opt = 0

            # Recovery phrase
            self.phrase_recovery = QRadioButton(
                text="Recover account with your recovery phrase",
                parent=self
            )

            self.phrase_recovery.setGeometry(48, 237, 400, 70)
            self.phrase_recovery.toggled.connect(lambda: self._setchoice(1))

            # Recovery key
            self.pkey_recovery = QRadioButton(
                text="Recover account with your private key",
                parent=self
            )

            self.pkey_recovery.setGeometry(48, 306, 400, 70)
            self.pkey_recovery.toggled.connect(lambda: self._setchoice(2))

        def init_return(self):
            self.ret = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.ret.setFixedSize(170, 44)
            self.ret.setIconSize(QSize(28, 28))
            self.ret.move(60, 396)
            self.ret.clicked.connect(self.return_to_login)

        def init_continue(self):
            self.continue_ = QPushButton(
                text="Continue ",
                parent=self,
                icon=TigerWalletImage.send_blue
            )

            self.continue_.setFixedSize(170, 44)
            self.continue_.setIconSize(QSize(28, 28))
            self.continue_.move(258, 396)
            self.continue_.clicked.connect(self.continue_recovery)
            self.continue_.setLayoutDirection(
                QtCore.Qt.LayoutDirection.RightToLeft
            )

        # Get radiobutton choice
        def _setchoice(self, choice):
            self.opt = choice

        def continue_recovery(self):
            if self.opt == 0:
                errbox("No option was selected")
                return

            elif self.opt == 1:
                self.rwfp = RecoverWalletFromPhrase()
                self.rwfp.show()
                self.close()
                self.deleteLater()

            elif self.opt == 2:
                self.rwfpk = RecoverWalletFromPrivateKey()
                self.rwfpk.show()
                self.close()
                self.deleteLater()

        # Return to login window
        def return_to_login(self):
            self.login = Login()
            self.login.show()
            self.close()
            self.deleteLater()

    # Recovery from mnemonic phrase (12 Englsh words)
    class RecoverWalletFromPhrase(QWidget):
        def __init__(self):
            super().__init__()

            self.init_window()
            self.init_label()
            self.init_middle_msg()
            self.init_fields()
            self.init_buttons()

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.paste_btn.setStyleSheet(
                     'QPushButton{'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #627eea;}"
                    + "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.msg.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #b0c4de;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.paste_btn.setStyleSheet(
                    'QPushButton {background-color: transparent;'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #3c598e;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #eff1f3;"
                )

                self.msg.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

        def init_window(self):
            self.setFixedWidth(640)
            self.setFixedHeight(614)
            self.setWindowTitle("TigerWallet  -  Recover account")
            align_to_center(self)

        def init_label(self):
            self.border = QLabel(self)
            self.border.resize(621, 546)
            self.border.move(9, 58)

            self.label = QLabel("Account Recovery", self)
            self.label.resize(356, 61)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(148, 28)

        def init_middle_msg(self):
            self.msg = QLabel(
                text=(
                    'Please enter your 12 secret'
                    ' recovery words (<b>order matters</b>)'
                ),
                parent=self,
            )

            self.msg.resize(552, 70)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(43, 102)

        def init_fields(self):
            self.field = [QLineEdit(self) for i in range(12)]
            self.field_number = [
                QLabel(
                    text=str(i+1) + ')',
                    parent=self
                )
                for i in range(12)
            ]

            for i in range(12):
                self.field[i].resize(140, 40)
                self.field[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.field_number[i].setStyleSheet(
                    'font: 16px;',
                )

            # Row 1
            self.field[0].move(60, 200)
            self.field_number[0].move(24, 208)

            self.field[1].move(250, 200)
            self.field_number[1].move(216, 208)

            self.field[2].move(448, 200)
            self.field_number[2].move(414, 208)

            # Row 2
            self.field[3].move(60, 262)
            self.field_number[3].move(24, 270)

            self.field[4].move(250, 262)
            self.field_number[4].move(216, 270)

            self.field[5].move(448, 262)
            self.field_number[5].move(414, 270)

            # Row 3
            self.field[6].move(60, 324)
            self.field_number[6].move(24, 332)

            self.field[7].move(250, 324)
            self.field_number[7].move(216, 332)

            self.field[8].move(448, 324)
            self.field_number[8].move(414, 332)

            # Row 4
            self.field[9].move(60, 386)
            self.field_number[9].move(22, 394)

            self.field[10].move(250, 386)
            self.field_number[10].move(212, 394)

            self.field[11].move(448, 386)
            self.field_number[11].move(410, 394)

        def init_buttons(self):
            # Back
            self.btn1 = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.btn1.setFixedSize(180, 52)
            self.btn1.setIconSize(QSize(32, 32))
            self.btn1.move(116, 516)
            self.btn1.clicked.connect(self.return_)

            self.btn2 = QPushButton(
                text=" Continue",
                parent=self,
                icon=TigerWalletImage.checkmark
            )

            # Continue
            self.btn2.setFixedSize(180, 52)
            self.btn2.setIconSize(QSize(28, 28))
            self.btn2.move(330, 516)
            self.btn2.clicked.connect(self.continue_)

            # Paste
            self.paste_btn = QPushButton(
                text=" Paste recovery phrase",
                parent=self,
                icon=TigerWalletImage.copy_blue,
            )

            self.paste_btn.setIconSize(QSize(16, 16))
            self.paste_btn.resize(238, 36)
            self.paste_btn.move(198, 462)
            self.paste_btn.clicked.connect(self.paste_phrase)

        def paste_phrase(self):
            self.copy_blue_contents = QApplication.clipboard().text()
            self.p = self.copy_blue_contents.split()
            self.p = list(self.p)

            if len(self.p) < 12:
                errbox("Invalid recovery phrase")
                return

            elif len(self.p) > 12:
                errbox(
                    "Currently, TigerWallet only supports 12-words recovery"
                )
                return

            [self.field[i].setText(self.p[i]) for i in range(12)]

        def return_(self):
            if not prog.from_experienced:
                self.fp = ForgotPassword()
                self.fp.show()
                self.close()
                self.deleteLater()
                return

            prog.from_experienced = False
            self.uwe = UserWithExperience()
            self.uwe.show()
            self.close()
            self.deleteLater()

        def continue_(self):
            self.words = " ".join(
                [
                    self.field[i].text() for i in range(12)
                ]
            )

            # 11 "  ", meaning no fields were filled
            if len(self.words) == 11:
                errbox(
                    'Please enter your mnemonic '
                    + 'phrase to recover your wallet'
                )
                return

            prog.mnemonic_phrase = self.words
            prog.from_mnemonic = True

            try:
                prog.account = Account.from_mnemonic(self.words)

            except Exception:
                errbox("Invalid mnemonic phrase")
                return

            self.walletname = WalletName()
            self.walletname.show()
            self.close()
            self.deleteLater()

    # Recovery from private key
    # Fixed a BUG in v3.1 where recovering from private key crashes program
    class RecoverWalletFromPrivateKey(QWidget):
        def __init__(self):
            super().__init__()

            self.init_window()
            self.init_labels()
            self.init_key_entry_field()
            self.init_eye_btn()
            self.init_return_btn()
            self.init_continue_btn()

            self.entry.returnPressed.connect(self.continue_)

            if "default" in prog.configs["theme"]:
                self.btn_showhide.setStyleSheet(
                    "QPushButton{background-color: none;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #1e1e1e;}"
                )

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #b0c4de;"
                    + "background: transparent;"
                    + "padding: 4px;"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #eff1f3;"
                )

                self.msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #3c598e;"
                    + "background: #eff1f3;"
                )

        def init_window(self):
            self.setFixedWidth(580)
            self.setFixedHeight(376)
            self.setWindowTitle("TigerWallet  -  Recover account")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(562, 314)
            self.border.move(9, 52)

            self.opt = 1

        def init_labels(self):
            self.label = QLabel("Account Recovery", self)
            self.label.resize(356, 44)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(110, 30)

            self.msg = QLabel(
                text="Enter your private key to recover your wallet:\n"
                "(With or without the 0x prefix)",
                parent=self,
            )

            self.msg.resize(420, 58)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(76, 100)

        def init_key_entry_field(self):
            self.entry = QLineEdit(self)
            self.entry.setPlaceholderText("Enter your private key")
            self.entry.move(31, 194)
            self.entry.resize(472, 44)
            self.entry.setEchoMode(QLineEdit.EchoMode.Password)

        def init_eye_btn(self):
            self.btn_showhide = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_showhide.setIconSize(QSize(24, 24))
            self.btn_showhide.move(518, 202)
            self.btn_showhide.clicked.connect(self.unhide)

        def init_return_btn(self):
            self.btn1 = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.btn1.setFixedSize(180, 52)
            self.btn1.setIconSize(QSize(32, 32))
            self.btn1.move(86, 276)
            self.btn1.clicked.connect(self.return_)

        def init_continue_btn(self):
            self.btn2 = QPushButton(
                text=" Continue",
                parent=self,
                icon=TigerWalletImage.checkmark
            )

            self.btn2.setFixedSize(180, 52)
            self.btn2.setIconSize(QSize(28, 28))
            self.btn2.move(310, 276)
            self.btn2.clicked.connect(self.continue_)

        # Hide/show password
        def unhide(self):
            if self.opt == 1:
                self.btn_showhide.setIcon(TigerWalletImage.opened_eye)
                self.entry.setEchoMode(QLineEdit.EchoMode.Normal)
                self.opt = 0

            elif self.opt == 0:
                self.btn_showhide.setIcon(TigerWalletImage.closed_eye)
                self.entry.setEchoMode(QLineEdit.EchoMode.Password)
                self.opt = 1

        def continue_(self):
            if len(self.entry.text()) == 0:
                errbox("No private key was provided")
                return

            try:
                prog.account = Account.from_key(self.entry.text())

            except ValueError:
                errbox("Invalid private key")
                return

            prog.from_private_key = True

            self.wn = WalletNameAndPassword()
            self.wn.show()
            self.close()
            self.deleteLater()

        def return_(self):
            if not prog.from_experienced:
                self.fp = ForgotPassword()
                self.fp.show()
                self.close()
                self.deleteLater()

            else:
                self.uwe = UserWithExperience()
                self.uwe.show()
                self.close()
                self.deleteLater()

    # Mnemonic phrase
    class MnemonicPhraseWindow(QWidget):
        """
        Displays the 12 recovery words that
        are needed to restore a user's wallet
        """

        def __init__(self, master=None):
            super().__init__()

            self.master = master

            self.init_window()
            self.init_table()
            self.init_labels()
            self.init_show_recovery_btn()
            self.init_copy_btn()
            self.init_check_box()
            self.init_continue_btn()
            self.init_return_btn()

            if "default" in prog.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")

                self.label.setStyleSheet(
                    'font-size: 40px;'
                    + 'color: #627eea;'
                    + 'background: #0a0f18;'
                )

                self.label2.setStyleSheet(
                    'font-size: 23px;'
                    + 'color: #c5d4e7;'
                    + 'background: #0a0f18;'
                )

                self.btnshow.setStyleSheet(
                    'QPushButton{'
                    + "border-radius: 8;"
                    + "font-size: 16px;"
                    + "color: #627eea;}"
                    + "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btncopy.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.retbtn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btncont.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.chbox.setStyleSheet("color: #c5d4e7;")

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label.setStyleSheet(
                    'font-size: 40px;'
                    + 'color: #627eea;'
                    + 'background: #eff1f3;'
                )

                self.label2.setStyleSheet(
                    'font-size: 23px;'
                    + 'color: #3c598e;'
                    + 'background: #eff1f3;'
                )

                self.btnshow.setStyleSheet(
                    'QPushButton {background-color: transparent;'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #3c598e;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.btncopy.setStyleSheet(
                    'QPushButton {background-color: transparent;'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #3c598e;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.retbtn.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.btncont.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.chbox.setStyleSheet("color: #c5d4e7;")

        def init_window(self):
            self.setFixedWidth(650)
            self.setFixedHeight(530)
            self.setWindowTitle("TigerWallet  -  Mnemonic Phrase")
            align_to_center(self)

            self.mphrase = prog.mnemonic_phrase
            self.wnap = WalletNameAndPassword()

            self.border = QLabel(self)
            self.border.resize(630, 470)
            self.border.move(10, 44)

        def init_table(self):
            self.table = QTableWidget(self)
            self.table.setRowCount(4)
            self.table.setColumnCount(3)
            self.table.setColumnWidth(0, 150)
            self.table.setColumnWidth(1, 150)
            self.table.setColumnWidth(2, 150)
            self.table.move(100, 164)
            self.table.setEnabled(False)
            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setVisible(False)
            self.table.setFixedWidth(452)
            self.table.setFixedHeight(122)
            self.table.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )

            self.blur = QGraphicsBlurEffect(self.table)
            self.blur.setEnabled(True)
            self.blur.setBlurRadius(30)
            self.table.setGraphicsEffect(self.blur)

            self.words = self.mphrase.split()
            self.words_with_index = self.mphrase.split()

            for i, word in enumerate(self.words_with_index):
                self.table.setItem(
                    0, i, QTableWidgetItem(f"{i + 1}) {word}")
                )

                if i == 3:
                    self.table.setItem(
                        1, i, QTableWidgetItem(f"{i + 1}) {word}")
                    )

                if i == 6:
                    self.table.setItem(
                        2, i, QTableWidgetItem(f"{i + 1}) {word}")
                    )

        def init_labels(self):
            self.label = QLabel("Recovery Phrase", self)
            self.label.resize(322, 54)
            self.label.move(170, 18)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.label2 = QLabel(
                text="Keep this recovery phrase somewhere safe!",
                parent=self
            )
            self.label2.resize(440, 30)
            self.label2.move(104, 90)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_show_recovery_btn(self):
            self.opt = 1

            self.btnshow = QPushButton(
                text=" Show recovery phrase",
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )
            self.btnshow.setFixedSize(260, 40)
            self.btnshow.setIconSize(QSize(28, 28))
            self.btnshow.move(60, 322)
            self.btnshow.clicked.connect(self.show_recovery_words)

        def init_copy_btn(self):
            self.btncopy = QPushButton(
                text=" Copy mnemonic phrase",
                parent=self,
                icon=TigerWalletImage.copy_blue,
            )

            self.btncopy.setFixedSize(260, 40)
            self.btncopy.setIconSize(QSize(28, 28))
            self.btncopy.move(328, 322)
            self.btncopy.clicked.connect(
                lambda: [
                    QApplication.clipboard().setText(self.mphrase),
                    msgbox("Recover phrase has been copied!"),
                ]
            )

        def init_check_box(self):
            self.chbox = QCheckBox(
                text="I have saved my recovery phrase",
                parent=self
            )

            self.chbox.move(232, 388)
            self.chbox.setEnabled(True)
            self.chbox.clicked.connect(self._enablecont)

        def init_return_btn(self):
            self.retbtn = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.retbtn.setFixedSize(240, 58)
            self.retbtn.move(70, 420)
            self.retbtn.setIconSize(QSize(48, 48))

            if self.master is not None:
                self.retbtn.clicked.connect(
                    lambda: [
                        os.remove(prog.nameofwallet),
                        self.master.show(),
                        self.wnap.deleteLater(),
                        self.close(),
                        self.deleteLater()
                    ]
                )

            else:
                self.retbtn.clicked.connect(
                    lambda: [
                        os.remove(prog.nameofwallet),
                        self.wnap.show(),
                        self.close(),
                        self.deleteLater()
                    ]
                )

        def init_continue_btn(self):
            self.btncont = QPushButton(
                text=" Continue",
                parent=self,
                icon=TigerWalletImage.checkmark
            )

            self.btncont.setFixedSize(240, 58)
            self.btncont.move(332, 420)
            self.btncont.setIconSize(QSize(32, 32))
            self.btncont.setEnabled(False)
            self.btncont.clicked.connect(
                self._startloadingbarclass
            )


        def show_recovery_words(self):
            if self.opt == 1:
                self.btnshow.setText('Hide recovery phrase')
                self.btnshow.setIcon(TigerWalletImage.opened_eye_blue)

                self.blur.setEnabled(False)
                self.opt = 0

            elif self.opt == 0:
                self.btnshow.setText('Show recovery phrase')
                self.btnshow.setIcon(TigerWalletImage.closed_eye_blue)

                self.blur.setEnabled(True)
                self.opt = 1

        def _enablecont(self):
            self.btncont.setEnabled(True)
            self.chbox.setEnabled(False)

        # Continue to user wallet (wallet creation complete)
        def _startloadingbarclass(self):
            with open(prog.conf_file, "w") as ff:
                json.dump(
                    obj=prog.configs,
                    fp=ff,
                    indent=4
                )

            self.close()
            self.deleteLater()
            self.alb = AssetLoadingBar()
            self.alb.show()

    # QR code
    class QrCodeWindow(QWidget):
        def __init__(self, private_key):
            super().__init__()
            self.pkey = private_key

            self.init_main()
            self.init_qr_code()
            self.init_buttons()

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18")

                self.close_self.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.show_qr.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.copy_pkey.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.uppertxt.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.lbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #627eea;"
                    + "background-color: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.close_self.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.show_qr.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.copy_pkey.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.uppertxt.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #3c598e;"
                    + "background-color: #eff1f3;"
                )

                self.lbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #3c598e;"
                    + "background-color: transparent;"
                )

        def init_main(self):
            self.setFixedWidth(530)
            self.setFixedHeight(580)
            self.setWindowTitle("TigerWallet  -  QR Code")
            align_to_center(self)

            self.uppertxt = QLabel(self)
            self.uppertxt.resize(530, 70)
            self.uppertxt.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.lbl = QLabel(self)
            self.lbl.resize(530, 250)
            self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl.move(0, 100)

            self.haveread = False
            self.qropt = 1
            self.passopt = 1

        def init_qr_code(self):
            buf = BytesIO()

            self.qrcode = segno.make(self.pkey)
            self.qrcode.save(
                buf,
                scale=9,
                border=1,
                kind="png"
            )

            self.pix = QPixmap()
            self.pix.loadFromData(buf.getvalue())
            self.lbl.setPixmap(self.pix)

            self.uppertxt.setText("Private key")
            self.blur = QGraphicsBlurEffect(self.lbl)
            self.lbl.setGraphicsEffect(self.blur)
            self.blur.setEnabled(True)
            self.blur.setBlurRadius(50)

        def init_buttons(self):
            self.show_qr = QPushButton(
                text="Show QR code",
                parent=self,
                icon=TigerWalletImage.closed_eye_blue,
            )
            self.show_qr.resize(176, 40)
            self.show_qr.setIconSize(QSize(32, 32))
            self.show_qr.move(70, 412)
            self.show_qr.clicked.connect(self.show_hide_qr)

            self.copy_pkey = QPushButton(
                text="Copy private key",
                parent=self,
                icon=TigerWalletImage.copy_blue,
            )
            self.copy_pkey.resize(176, 40)
            self.copy_pkey.setIconSize(QSize(32, 32))
            self.copy_pkey.move(290, 412)
            self.copy_pkey.clicked.connect(
                lambda: [
                    QApplication.clipboard().setText(str(self.pkey.hex())),
                    msgbox("Private key has been copied!"),
                ]
            )

            self.close_self = QPushButton(
                text="Close",
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.close_self.resize(160, 50)
            self.close_self.setIconSize(QSize(32, 32))
            self.close_self.move(184, 480)
            self.close_self.clicked.connect(
                lambda: [
                    (
                        self.blur.setEnabled(True)
                        if self.blur.isEnabled()
                        else None
                    ),
                    self.close(),
                    self.deleteLater(),
                ]
            )

        def show_hide_qr(self):
            if self.qropt == 1:
                self.blur.setEnabled(False)
                self.show_qr.setIcon(TigerWalletImage.opened_eye_blue)
                self.qropt = 0
                self.show_qr.setText("Hide QR code")

            elif self.qropt == 0:
                self.blur.setEnabled(True)
                self.show_qr.setIcon(TigerWalletImage.closed_eye_blue)
                self.qropt = 1
                self.show_qr.setText("Show QR code")

    # A worker for AssetLoadingBar class
    # Speed uplift in v2.0
    # Slight visual changes in v3.0
    # Slight uplift in speed in v3.1
    class AssetLoadingBarWorker(QThread):
        prog = pyqtSignal(str)
        cont = pyqtSignal(int)

        def __init__(self):
            super(QThread, self).__init__()

            self.address = prog.account.address
            self.asset = prog.asset['eth']
            self.basset = prog.asset['base']
            self.assetamount = len(self.asset['name'])
            self.no_internet = False

            eth_history_thread = Thread(target=self._fetch_history_eth)
            eth_history_thread.start()

            base_history_thread = Thread(target=self._fetch_history_base)
            base_history_thread.start()

        def _fetch_eth_price_and_amount(self) -> None:
            prog.eth_price = get_eth_price()

            prog.eth_amount = float(w3.eth.get_balance(self.address))
            prog.eth_amount = round(prog.eth_amount, 14)
            prog.eth_amount /= 10**18 if not 0 else 0
            prog.eth_amount = rm_e_notation(prog.eth_amount)

            prog.base_eth_amount = base_w3.eth.get_balance(self.address)

            if not isinstance(prog.base_eth_amount, tuple):
                prog.base_eth_amount = float(prog.base_eth_amount)
                prog.base_eth_amount = round(prog.base_eth_amount, 14)
                prog.base_eth_amount /= 10**18 if not 0 else 0
                prog.base_eth_amount = rm_e_notation(prog.base_eth_amount)

            else:
                prog.base_eth_amount = 0.0


        def _fetch_history_eth(self) -> None:
            url = f"https://api.ethplorer.io/getAddressHistory/{self.address}"
            key = "?apiKey=freekey&limit=100&showZeroValues=false"

            data = s.get(url + key, stream=True)
            data = orjson.loads(data.text)

            with open(
                prog.dest_path
                + "history_eth.json", "w"
            ) as f:
                json.dump(
                    obj=data,
                    fp=f,
                    indent=4
                )

        def _fetch_history_base(self) -> None:
            url = (
                f"https://base.blockscout.com/api/v2/addresses/{self.address}/token-transfers?"
                'type=ERC-20%2CERC-721%2CERC-1155&filter=to%20%7C%20from'
            )

            data = s.get(url, stream=True)
            data = orjson.loads(data.text)
            data_sz = len(data['items'])

            # Attempt to filter out spam/scam tokens
            if data_sz != 0:
                filtered_list = [
                    data['items'][i]
                    for i in range(data_sz)
                    if (
                        data['items'][i]['token']['decimals'] != "0"
                        and data['items'][i]['token']['circulating_market_cap'] != None
                        and data['items'][i]['token']['exchange_rate'] != None
                        and not '#' in data['items'][i]['token']['name']
                        and not '.' in data['items'][i]['token']['name']
                        and not 'claim' in data['items'][i]['token']['name']
                        and not '.' in data['items'][i]['token']['symbol']
                        and not 'claim' in data['items'][i]['token']['symbol']
                    )
                ]

                data['items'] = filtered_list

            with open(
                prog.dest_path
                + "history_base.json", "w"
            ) as f:
                json.dump(
                    obj=data,
                    fp=f,
                    indent=4
                )

        def build_contract_list(self, chain):
            if chain == 'eth':
                contract_list = [
                    create_contract(address, chain=chain)
                    for address in self.asset['address']
                ]

                return contract_list

            contract_list = [
                create_contract(address, chain=chain)
                for address in self.basset['address']
            ]

            return contract_list

        def base_token_balance(self):
            contract_list = self.build_contract_list(chain='base')

            with base_w3.batch_requests() as batch_token_balance:
                for contract in contract_list:
                    batch_token_balance.add(
                        token_balance(
                            self.address,
                            contract=contract
                        )
                    )

                token_balance_list = batch_token_balance.execute()

                for token_bal in token_balance_list:
                    prog.asset_details['base']["value"].append(
                        str(base_w3.from_wei(token_bal, 'ether'))
                    )

        def work(self) -> None:
            if not w3.is_connected():
                self.no_internet = True
                self.cont.emit(len(self.asset['name']))

            btb = Thread(
                target=self.base_token_balance
            )

            btb.start()

            with ThreadPoolExecutor() as pool:
                self._fetch_eth_price_and_amount()

                contract_list = pool.submit(
                    self.build_contract_list, 'eth'
                )

                with w3.batch_requests() as batch_token_balance:
                    contract_list = contract_list.result()

                    for contract in contract_list:
                        batch_token_balance.add(
                            token_balance(
                                self.address,
                                contract=contract
                            )
                        )

                    token_balance_list = batch_token_balance.execute()

                    for token_bal in token_balance_list:
                        prog.asset_details['eth']["value"].append(
                            str(
                                w3.from_wei(token_bal, 'ether')
                            )
                        )

                for i in range(1, self.assetamount):
                    time.sleep(0.01)

                    self.prog.emit(
                        str(int((i / self.assetamount) * 100)) + '%'
                    )

                    if i == self.assetamount-1:
                        self.prog.emit("99%")

                    self.cont.emit(i)

            # Ensures the threads are finished before proceeding
            while (
                _load_eth_asset_prices.is_alive()
                or _base_assets_price.is_alive()
            ):
                pass
            else:
                self.prog.emit("100%")
                self.cont.emit(len(self.asset['name']))

    # visual changes in v1.2
    # more visual changes in v2.0 (and v3.0)
    # Bar has a different blue in v3.1
    class AssetLoadingBar(QWidget):
        """
        Loads assets, so that user doesn't
        need to wait for the data to get fetched
        """
        def __init__(self):
            super().__init__()

            self.setup_main()
            self.init_loading_label()
            self.init_progressbar()
            self.init_asset_label()
            self.init_thread()

            if "default" in prog.configs["theme"]:
                if prog.configs['play_loading_gif']:
                    self.label.setStyleSheet(
                        "font-size: 40px;"
                        + "color: #0a0f18;"
                        + "background: transparent;"
                    )

                    self.label2.setStyleSheet(
                        "font-size: 25px;"
                        + "color: #0a0f18;"
                        + "background: transparent;"
                    )

                else:
                    self.label.setStyleSheet(
                        "font-size: 40px;"
                        + "color: #eff1f3;"
                        + "background: transparent;"
                    )

                    self.label2.setStyleSheet(
                        "font-size: 25px;"
                        + "color: #eff1f3;"
                        + "background: transparent;"
                    )

                self.barstyle = """
                        QProgressBar{
                            color: black;
                            border-radius: 0px;
                            background: #2E425D;
                            border-radius:3px;
                        }

                        QProgressBar::chunk{
                            background-color: #c1ccf7;
                            border-radius: 3px;
                        }
                    """

                self.bar.setStyleSheet(self.barstyle)

        # Window ui
        def setup_main(self):
            self.setFixedWidth(680)
            self.setFixedHeight(310)
            self.setWindowTitle("TigerWallet  -  Loading assets")
            self.thread = QThread()

            align_to_center(self)
            add_round_corners(self, 32)

            self.list_ = {}

        # Loading label
        def init_loading_label(self):
            self.img_holder = QLabel(self)
            self.img_holder.resize(680, 350)

            if prog.configs['play_loading_gif']:
                self.gif = prog.imgfolder + 'cat.gif'
                self.movie = QtGui.QMovie(self.gif)
                self.img_holder.setMovie(self.movie)

            else:
                self.tiger_pic = QPixmap(TigerWalletImage.loading_bg)
                self.tiger_pic = self.tiger_pic.scaled(QSize(680, 350))
                self.img_holder.setPixmap(self.tiger_pic)


            self.label = QLabel("Loading assets...", self)
            self.label.resize(680, 240)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # Progress bar
        def init_progressbar(self):
            self.bar = QProgressBar(self)
            self.bar.resize(420, 7)

            self.bar.setRange(0, len(prog.asset['eth']['name']))
            self.bar.setValue(0)
            self.bar.move(Qt.AlignmentFlag.AlignCenter, 180)
            self.bar.setTextVisible(False)

        def init_asset_label(self):
            self.label2 = QLabel(self)
            self.label2.resize(680, 30)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label2.move(0, 206)

        # Thread creation
        def init_thread(self):
            self.worker = AssetLoadingBarWorker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.work)
            self.worker.prog.connect(self.print_names)
            self.worker.cont.connect(self.endworker)
            self.thread.start()

            if prog.configs['play_loading_gif']:
                self.movie.start()

        def print_names(self, names):
            self.label2.setText(names)

        def endworker(self, n):
            self.bar.setValue(n)

            if prog.chain == 'eth':
                self.list_ = prog.asset['eth']['name']

            elif prog.chain == 'base':
                self.list_ = prog.asset['base']['name']

            if n == len(self.list_):
                if self.worker.no_internet:
                    self.thread.quit()
                    self.worker.quit()
                    self.worker.deleteLater()
                    self.thread.deleteLater()

                    errbox(
                        'Could not connect. '
                        + 'Do you have an internet connection right now?'
                        + '\nTigerWallet requires an internet connection.'
                        + ' Shutting down'
                    )

                    self.close()
                    self.deleteLater()
                    return

                self.thread.quit()
                self.worker.quit()
                self.worker.deleteLater()
                self.thread.deleteLater()
                self.launch_wallet()

        def launch_wallet(self):
            self.uw = UserWallet()
            self.uw.show()
            self.close()
            self.deleteLater()

    from web3 import AsyncWeb3, WebSocketProvider
    from eth_abi.abi import decode
    import asyncio

    from web3.utils.subscriptions import (
        NewHeadsSubscription,
        NewHeadsSubscriptionContext,
        LogsSubscription,
        LogsSubscriptionContext
    )

    class SubToEthChain(QThread):
        """
        A timed worker that checks for
        new tokens in the user's wallet
        """
        received_new_tokens = pyqtSignal(bool)

        def __init__(self):
            super().__init__()
            self.address = prog.account.address
            self.token = {
                'address': '',
                'symbol': '',
                'name': ''
            }

            self.wss_provider = 'wss://mainnet.gateway.tenderly.co'
            self.token_addr = ''
            self.src = ''
            self.dst = ''

        async def check_for_new_tokens(
            self,
            handler_context: LogsSubscriptionContext
        ) -> None:
            self.received_new_tokens.emit(False)

            async_w3 = handler_context.async_w3
            log = handler_context.result

            self.src = decode(["address"], log["topics"][1])[0]
            self.src = async_w3.to_checksum_address(self.src)

            self.dst = decode(["address"], log["topics"][2])[0]
            self.dst = async_w3.to_checksum_address(self.dst)

            self.token_addr = async_w3.to_checksum_address(log['address'])

            if self.src == self.address or self.dst == self.address:
                self.contract = create_contract(log['address'])

                symbol = self.contract.functions.symbol().call()
                name = self.contract.functions.name().call()

                self.token = {
                    'address': self.token_addr,
                    'symbol': symbol,
                    'name': name
                }

                self.decimals = (
                    self.contract.functions.decimals()
                    .call()
                )

                self.balance = float(
                    self.contract.functions.balanceOf(self.address)
                    .call()
                )

                self.balance /= 10**self.decimals

                if (
                    not self.token_addr in prog.asset['eth']['address']
                    and not log['address'] in prog.asset['eth']['address']
                ):
                    prog.asset['eth']['address'].append(
                        self.token['address']
                    )

                    prog.asset_details['eth']['value'].append(
                        str(self.balance)[:18]
                    )

                    prog.asset['eth']['symbol'].append(symbol.lower())
                    prog.asset['eth']['name'].append(name)

                    token_image(self.token_addr, chain='eth')

                    img = (
                        prog.tokenimgfolder
                        + symbol.lower()
                        + ".png"
                    )

                    prog.asset['eth']['image'].append(img)

                    self.received_new_tokens.emit(True)
                    return

                else:
                    index = prog.asset['eth']['symbol'].index(symbol.lower())
                    prog.asset_details['eth']['value'][index] = (
                        str(self.balance)[:18]
                    )

        async def fetch_gas(
            self,
            handler_context: LogsSubscriptionContext
        ) -> None:
            async_w3 = handler_context.async_w3
            log = handler_context.result

            gas = 0.0

            try:
                gas = int(log['baseFeePerGas'], 16) # Convert from hex to decimal

            except TypeError:
                gas = log['baseFeePerGas']

            gas /= 10**18
            gas += (gas * 0.25)
            #gas *= float(get_eth_price())
            gas *= 24000
            gas = round(gas, 14)

            prog.eth_gas = rm_e_notation(gas)

        async def async_events(self):
            # The actual subscriptions and management of subs
            async with AsyncWeb3(
                WebSocketProvider(
                    endpoint_uri=self.wss_provider,
                    websocket_kwargs= {
                        'open_timeout': None,
                        'close_timeout': None,
                    },
                )
            ) as wss_w3:
                # Signature of the Transfer event
                event_signature = w3.keccak(
                    text="Transfer(address,address,uint256)"
                )

                await wss_w3.subscription_manager.subscribe(
                    [
                        # Transfer sub
                        LogsSubscription(
                            topics=[event_signature],
                            handler=self.check_for_new_tokens,
                        ),
                        # Gas sub
                        NewHeadsSubscription(handler=self.fetch_gas),
                    ]
                )

                await wss_w3.subscription_manager.handle_subscriptions()

        def work(self):
            asyncio.run(self.async_events())

    class SubToBaseChain(QThread):
        """
        A timed worker that checks for
        new tokens in the user's wallet
        """
        received_new_tokens = pyqtSignal(bool)

        def __init__(self):
            super().__init__()
            self.address = prog.account.address
            self.token = {
                'address': '',
                'symbol': '',
                'name': ''
            }

            self.wss_provider = 'wss://base-rpc.publicnode.com'
            self.token_addr = ''
            self.src = ''
            self.dst = ''

        async def check_for_new_tokens(
            self,
            handler_context: LogsSubscriptionContext
        ) -> None:
            self.received_new_tokens.emit(False)

            async_w3 = handler_context.async_w3
            log = handler_context.result

            self.src = decode(["address"], log["topics"][1])[0]
            self.src = async_w3.to_checksum_address(self.src)

            self.dst = decode(["address"], log["topics"][2])[0]
            self.dst = async_w3.to_checksum_address(self.dst)

            self.token_addr = async_w3.to_checksum_address(log['address'])

            if self.src == self.address or self.dst == self.address:
                self.contract = create_contract(
                    log['address'],
                    chain='base'
                )

                symbol = self.contract.functions.symbol().call()
                name = self.contract.functions.name().call()

                self.token = {
                    'address': self.token_addr,
                    'symbol': symbol,
                    'name': name,
                }

                self.decimals = (
                    self.contract.functions.decimals()
                    .call()
                )

                self.balance = float(
                    self.contract.functions.balanceOf(self.address)
                    .call()
                )
                self.balance /= 10**self.decimals

                if (
                    not self.token_addr in prog.asset['base']['address']
                    and not log['address'] in prog.asset['base']['address']
                ):
                    prog.asset['base']['address'].append(
                        self.token['address']
                    )

                    prog.asset_details['base']['value'].append(
                        str(self.balance)[:18]
                    )

                    prog.asset['base']['symbol'].append(symbol.lower())
                    prog.asset['base']['name'].append(name)

                    token_image(self.token_addr, chain='base')

                    img = (
                        prog.tokenimgfolder
                        + symbol.lower()
                        + ".png"
                    )

                    prog.asset['base']['image'].append(img)

                    self.received_new_tokens.emit(True)
                    return

                else:
                    value = prog.asset_details['base']['value']
                    index = prog.asset['base']['symbol'].index(symbol.lower())

                    prog.asset_details['base']['value'][index] = (
                        str(self.balance)[:18]
                    )

        async def fetch_gas(
            self,
            handler_context: LogsSubscriptionContext
        ) -> None:
            async_w3 = handler_context.async_w3
            log = handler_context.result

            gas = log['baseFeePerGas'] # Output is already a number
            gas /= 10**18
            gas += (gas * 0.25)
            #gas *= float(get_eth_price())
            gas *= 24000
            gas = round(gas, 22)

            prog.base_gas = rm_e_notation(gas)

        async def async_events(self):
            # The actual subscriptions and management of subs
            async with AsyncWeb3(
                WebSocketProvider(
                    endpoint_uri=self.wss_provider,
                    websocket_kwargs= {
                        'open_timeout': None,
                        'close_timeout': None,
                        'ping_timeout': None,
                        'max_size': None
                    },
                )
            ) as wss_w3:
                # Signature of the Transfer event
                event_signature = w3.keccak(
                    text="Transfer(address,address,uint256)"
                )

                await wss_w3.subscription_manager.subscribe(
                    [
                        # Transfer sub
                        LogsSubscription(
                            topics=[event_signature],
                            handler=self.check_for_new_tokens,
                        ),
                        # Gas sub
                        NewHeadsSubscription(handler=self.fetch_gas),
                    ]
                )

                await wss_w3.subscription_manager.handle_subscriptions()

        def work(self):
            asyncio.run(self.async_events())

    class TimedUpdateTotalBalance(QThread):
        balance = pyqtSignal(float)

        def __init__(self):
            super().__init__()
            self.bal = 0.0
            self.address = prog.account.address

        def work(self):
            for val, price in zip(
                prog.asset_details[prog.chain]['value'],
                prog.asset_details[prog.chain]['price']
            ):
                self.bal += (float(val) * float(price))

            if prog.chain == 'eth':
                prog.eth_amount = w3.eth.get_balance(self.address)
                prog.eth_amount /= 10**18 # convert to ether

                prog.total_balance = self.bal + prog.eth_amount

            elif prog.chain == 'base':
                prog.base_eth_amount = base_w3.eth.get_balance(self.address)
                prog.eth_amount /= 10**18 # convert to ether

                prog.total_balance = self.bal + prog.base_eth_amount


            self.balance.emit(prog.total_balance)
            time.sleep(10000)

    # Updates the price of assets
    class TimedUpdatePriceOfAssetsWorker(QThread):
        eth_price = pyqtSignal(str)
        timer = QTimer()

        def __init__(self):
            super(QThread, self).__init__()
            self.address = prog.account.address

        def work(self):
            price = [
                get_price(symbol)
                for symbol in prog.asset[prog.chain]['symbol']
            ]

            #for i in range(len(prog.asset[self.chain['name'])):
            prog.asset_details[prog.chain]['price'] = price

            self.eth_price.emit(get_eth_price())

    class ValidatePassword(QWidget):
        def __init__(self):
            super().__init__()
            self.opt = 1

            self.init_window()
            self.init_buttons()

            if "default" in prog.configs["theme"]:
                self.btn_showhide.setStyleSheet(
                    'QPushButton {background-color: #7e91ac;'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #8ba1bf;}"
                )

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18;")

                self.verify.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.cancel.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.label.setStyleSheet(
                    "font-size: 25px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3;")

                self.verify.setStyleSheet(
                    "QPushButton{background-color:  transparent;"
                    + "font-size: 15px;"
                    + "color: #3c598e;"
                    + "border-radius: 8px;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.cancel.setStyleSheet(
                    "QPushButton{background-color:  transparent;"
                    + "font-size: 15px;"
                    + "color: #3c598e;"
                    + "border-radius: 8px;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.password.setStyleSheet(
                    "color: #3c598e; "
                    + "font: 16px;"
                    + "border: 1px solid #1e2b45;;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.label.setStyleSheet(
                    "font-size: 27px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

        def init_window(self):
            self.setFixedWidth(570)
            self.setFixedHeight(300)
            self.setWindowTitle("TigerWallet  -  Password verification")
            align_to_center(self)

            self.label = QLabel("Please enter your password to continue", self)
            self.label.resize(500, 90)
            self.label.move(30, 38)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setWordWrap(True)
            self.label.show()

            self.password = QLineEdit(self)
            self.password.setEchoMode(QLineEdit.EchoMode.Password)
            self.password.resize(430, 34)
            self.password.move(46, 144)
            self.password.returnPressed.connect(
                lambda: self.validate_pass(self.password.text())
            )

        def init_buttons(self):
            self.cancel = QPushButton(
                text=" Return   ",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.cancel.setFixedSize(180, 50)
            self.cancel.move(50, 210)
            self.cancel.setIconSize(QSize(32, 32))
            self.cancel.clicked.connect(self.return_)

            self.verify = QPushButton(self)

            if prog.switched_wallets:
                self.label.setText(
                    "Enter your wallet's password:"
                )
                self.verify.setText(" Login")
                self.verify.setIcon(TigerWalletImage.wallet_blue)

            elif prog.used_import_wallet_from_userwallet:
                self.label.setText(
                    "Enter your wallet's password:"
                )
                self.verify.setText(" Import wallet")
                self.verify.setIcon(TigerWalletImage.checkmark)

            elif prog.invoked_from_settings:
                self.verify.setText(" Verify password")
                self.verify.setIcon(TigerWalletImage.key_blue)

                self.cancel.setIcon(TigerWalletImage.close_blue)

            elif not prog.from_experienced:
                self.verify.setText(" Verify password")
                self.verify.setIcon(TigerWalletImage.key_blue)

            self.verify.setFixedSize(200, 50)
            self.verify.move(300, 210)
            self.verify.setIconSize(QSize(32, 32))
            self.verify.clicked.connect(
                lambda: self.validate_pass(self.password.text())
            )

            self.btn_showhide = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye
            )

            self.btn_showhide.setIconSize(QSize(32, 32))
            self.btn_showhide.move(500, 145)
            self.btn_showhide.clicked.connect(self.unhide)

        def return_(self):
            if prog.switched_wallets:
                prog.switched_wallets = False

                self.uw = UserWallet()
                self.uw.show()
                self.close()
                return

            elif prog.from_experienced:
                prog.from_experienced = False

                self.uwe = UserWithExperience()
                self.uwe.show()
                self.close()
                self.deleteLater()
                return

            elif prog.invoked_from_settings:
                prog.invoked_from_settings = False

                self.close
                self.deleteLater()


        def unhide(self):
            if self.opt == 1:
                self.btn_showhide.setIcon(TigerWalletImage.opened_eye)
                self.password.setEchoMode(QLineEdit.EchoMode.Normal)
                self.opt = 0

            elif self.opt == 0:
                self.btn_showhide.setIcon(TigerWalletImage.closed_eye)
                self.password.setEchoMode(QLineEdit.EchoMode.Password)
                self.opt = 1

        def validate_pass(self, passwd):
            if prog.switched_wallets:
                try:
                    with open(prog.reserved_nameofwallet, "r") as f:
                        prog.account = Account.from_key(
                            Account.decrypt(
                                json.load(f),
                                password=passwd
                            )
                        )
                        prog.nameofwallet = prog.reserved_nameofwallet

                except ValueError:
                    errbox("Invalid password")
                    return

                if (
                    len(prog.asset['eth']['address']) != 0
                    or len(prog.asset['base']['address']) != 0
                ):
                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()
                else:
                    """
                    If user decided to remove all
                    assets, only load Ether data.

                    This does not require loading
                    the AssetLoadingBar class.
                    """
                    self.uw = UserWallet()
                    self.uw.show()
                    self.close()
                    self.deleteLater()

            elif prog.from_experienced:
                if len(passwd) == 0:
                    errbox("Password field is empty")
                    return

                try:
                    with open(prog.nameofwallet, "r") as f:
                        prog.account = Account.from_key(
                            Account.decrypt(
                                json.load(f),
                                password=passwd
                            )
                        )

                        with open(prog.conf_file, "w") as ff:
                            if (
                                not prog.nameofwallet
                                in prog.configs["wallets"]
                            ):
                                prog.configs["wallets"].append(
                                    prog.nameofwallet
                                )

                            json.dump(
                                obj=prog.configs,
                                fp=ff,
                                indent=4
                            )

                except ValueError:
                    errbox("Incorrect password. Try again")
                    return

                if (
                    len(prog.asset['eth']['address']) != 0
                    or len(prog.asset['base']['address']) != 0
                ):
                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()
                else:
                    """
                    If user decided to remove all
                    assets, only load Ether data.

                    This does not require loading
                    the AssetLoadingBar class.
                    """
                    self.uw = UserWallet()
                    self.uw.show()
                    self.close()
                    self.deleteLater()

            elif prog.used_import_wallet_from_userwallet:
                try:
                    with open(prog.nameofwallet, "r") as f:
                        prog.account = Account.from_key(
                            Account.decrypt(
                                json.load(f),
                                password=passwd
                            )
                        )

                except ValueError:
                    errbox("Invalid password")
                    return

                if (
                    len(prog.asset['eth']['address']) != 0
                    or len(prog.asset['base']['address']) != 0
                ):
                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()
                else:
                    """
                    If user decided to remove all
                    assets, only load Ether data.

                    This does not require loading
                    the AssetLoadingBar class.
                    """
                    self.uw = UserWallet()
                    self.uw.show()
                    self.close()
                    self.deleteLater()

            elif not prog.from_experienced:
                with open(prog.nameofwallet, "rb") as f:
                    try:
                        Account.decrypt(
                            orjson.loads(f.read()),
                            password=passwd
                        )

                        self.qrcode = QrCodeWindow(
                            prog.account.key
                        )
                        self.qrcode.show()
                        self.close()
                        self.deleteLater()

                    except ValueError:
                        errbox("Invalid password")
                        return

    class DownloadUpdateWorker(QThread):
        from zipfile import ZipFile

        dl_prog = pyqtSignal(int)
        total_size = pyqtSignal(str)
        is_finished = pyqtSignal(bool)

        def __init__(
            self,
            parent=None,
            method_of_execution=None,
            version=0
        ):
            super(QThread, self).__init__()
            self.method_of_execution = method_of_execution
            self.version = version
            self.parent = parent

            if _platform() == 'nt':
                self.extract_path = f"C:\\Users\\{prog.current_usr}\\"

            else:
                self.extract_path = f"/home/{prog.current_usr}/"

        def work(self):
            self.dl_prog.emit(0)
            self.is_finished.emit(False)
            dl = 0

            # Ran via pyinstaller's executable
            if self.method_of_execution == 'pyinstaller-executable':
                ver = self.version
                tigerwallet_executable_file = \
                    f"{ver}/tigerwallet-{ver[1:len(ver)]}-x86-64"

                if _platform() == 'nt':
                    dl_executable_link = (
                        'https://github.com/Serpenseth/'
                        + 'TigerWallet/releases/download/'
                        + tigerwallet_executable_file
                        + '.exe'
                    )

                    with open(
                        self.extract_path
                        + f"tigerwallet-{ver[1:len(ver)]}-x86-64.exe",
                        mode='wb'
                    ) as exe_file:
                        # Download the file as a stream
                        downloaded_executable = s.get(
                            url=dl_executable_link,
                            stream=True
                        )

                        self.size = int(
                            downloaded_executable.headers.get(
                                'content-length'
                            )
                        )

                        self.parent.total_file_size = self.size
                        self.parent.bar.setRange(
                            0,
                            self.size
                        )

                        for data in downloaded_executable.iter_content(
                            chunk_size=4096
                        ):
                            dl += len(data)
                            exe_file.write(data)
                            self.dl_prog.emit(dl)

                        self.is_finished.emit(True)

                else:
                    dl_executable_link = (
                        'https://github.com/Serpenseth/'
                        + 'TigerWallet/releases/download/'
                        + tigerwallet_executable_file
                    )

                    with open(
                        self.extract_path
                        + f"tigerwallet-{ver[1:len(ver)]}-x86-64",
                        mode='wb'
                    ) as file_:
                        # Download the file as a stream
                        downloaded_executable = s.get(
                            url=dl_executable_link,
                            stream=True
                        )

                        self.size = int(
                            downloaded_executable.headers.get(
                                'content-length'
                            )
                        )

                        self.parent.total_file_size = self.size
                        self.parent.bar.setRange(
                            0,
                            self.size
                        )

                        for data in downloaded_executable.iter_content(
                            chunk_size=4096
                        ):
                            dl += len(data)
                            file_.write(data)
                            self.dl_prog.emit(dl)

                        self.is_finished.emit(True)

            # Ran via appimage
            elif self.method_of_execution == 'appimage-executable':
                ver = self.version
                tigerwallet_executable_file = \
                    f"{ver}/tigerwallet-{ver[1:len(ver)]}-x86-64"

                dl_executable_link = (
                    'https://github.com/Serpenseth/'
                    + 'TigerWallet/releases/download/'
                    + tigerwallet_executable_file
                    + '.AppImage'
                )

                with open(
                    self.extract_path
                    + f"tigerwallet-{self.version}-x86-64.AppImage",
                    mode='wb'
                ) as exe_file:
                    # Download the file as a stream
                    downloaded_executable = s.get(
                        url=dl_executable_link,
                        stream=True
                    )

                    self.size = int(
                        downloaded_executable.headers.get(
                            'content-length'
                        )
                    )

                    self.parent.total_file_size = self.size
                    self.parent.bar.setRange(
                        0,
                        self.size
                    )

                    for data in downloaded_executable.iter_content(
                        chunk_size=4096
                    ):
                        dl += len(data)
                        exe_file.write(data)
                        self.dl_prog.emit(dl)

                    self.is_finished.emit(True)

            elif self.method_of_execution == 'exe-installer':
                ver = self.version
                tigerwallet_executable_file = \
                    f"{ver}/tigerwallet-{ver[1:len(ver)]}-installer"

                dl_executable_link = (
                    'https://github.com/Serpenseth/'
                    + 'TigerWallet/releases/download/'
                    + tigerwallet_executable_file
                    + '.exe '
                )

                with open(
                    self.extract_path
                    + f"tigerwallet-{self.version}-installer.exe",
                    mode='wb'
                ) as exe_file:
                    # Download the file as a stream
                    downloaded_executable = s.get(
                        url=dl_executable_link,
                        stream=True
                    )

                    self.size = int(
                        downloaded_executable.headers.get(
                            'content-length'
                        )
                    )

                    self.parent.total_file_size = self.size
                    self.parent.bar.setRange(
                        0,
                        self.size
                    )

                    for data in downloaded_executable.iter_content(
                        chunk_size=4096
                    ):
                        dl += len(data)
                        exe_file.write(data)
                        self.dl_prog.emit(dl)

                    self.is_finished.emit(True)

            # Ran via py/python
            elif self.method_of_execution == 'python-command':
                dl_link = 'https://github.com/Serpenseth/TigerWallet'
                dl_link += '/archive/refs/heads/main.zip'

                with BytesIO() as zip_:
                    zipped_dl = s.get(
                        url=dl_link,
                        stream=True
                    )

                    # Loop progress bar until finished
                    self.parent.bar.setRange(0, 0)

                    for data in zipped_dl.iter_content(
                        chunk_size=4096
                    ):
                        dl += len(data)
                        zip_.write(data)
                        self.dl_prog.emit(dl)

                    with self.ZipFile(zip_, mode='r') as zip_ref:
                        zip_ref.extractall(self.extract_path)

                    self.is_finished.emit(True)

            # Ran via tigerwallet (pip install  with git)
            elif self.method_of_execution == 'pip-install-executable':
                dl_link = 'https://github.com/Serpenseth/TigerWallet'
                install_cmd = 'install git+'

                self.parent.bar.setRange(0, 0)

                result = subprocess.run(
                    [
                        sys.executable,
                        '-m',
                        'pip',
                        'install',
                        f"git+{dl_link}"
                    ],
                    stdout=subprocess.PIPE,
                )

                # Do nothing while pip hasn't completed
                while (
                    not 'Successfully'
                    in result.stdout.decode('utf-8')
                ):
                    self.is_finished.emit(False)

                self.is_finished.emit(True)

    # New in v1.5
    # Added .exe installer in v2.1
    class CheckForUpdates(QWidget):
        def __init__(
            self,
            url: str
        ):
            super().__init__()
            self.current_version = TigerWalletVersion
            self.url = url
            self.local_path = prog.local_path
            self.execution_method = self.__how_is_tigerwallet_running()
            self.total_file_size = 0
            self.init_self()

            self.init_loading_label()
            self.init_thread()

            self.init_progressbar()
            self.init_asset_label()
            self.check_if_update_is_available()

            if "default" in prog.configs["theme"]:
                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.label2.setStyleSheet(
                    "font-size: 25px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.barstyle = """
                    QProgressBar{
                        color: black;
                        border-radius: 0px;
                        background: transparent;
                    }

                    QProgressBar::chunk{
                        background-color: #87cefa;
                        border-radius: 5px;
                    }
                """

            self.bar.setStyleSheet(self.barstyle + "color: black;")

        def __how_is_tigerwallet_running(self):
            # Pyinstaller
            if '_MEI' in self.local_path:
                return 'pyinstaller-executable'

            # Appimage
            elif '/tmp/.mount' in self.local_path:
                return 'appimage-executable'

            # Pip install
            elif (
                'AppData\\Local' in self.local_path
                or 'site-packages' in self.local_path
            ):
                return 'pip-install-executable'

            # Pynsist (.exe installer)
            elif(
                'Program Files' in self.local_path
                or 'Local\\Programs\\TigerWallet' in self.local_path
            ):
                return 'exe-installer'

            # Python3/py tigerwallet
            return 'python-command'

        def check_if_update_is_available(self):
            if float(self.current_version) < self.github_version:
                resp = questionbox(
                    'A new update is available. '
                    + 'Install now?'
                )

                self.show()

                if resp:
                    if len(prog.configs['wallets']) != 0:
                        login.close()
                        login.deleteLater()

                    else:
                        first.close()
                        first.deleteLater()

                    self.download_update()

                else:
                    self.close()
                    self.deleteLater()

            else:
                self.close()
                self.deleteLater()

        def init_thread(self):
            self.thread = QThread()

        def init_self(self):
            self.setFixedWidth(680)
            self.setFixedHeight(310)
            self.setWindowTitle("TigerWallet  -  Loading assets")

            align_to_center(self)
            add_round_corners(self, 32)

            self.data = s.get(url=self.url)
            self.data = self.data.text.split()
            self.github_version = ' '.join(self.data[11 : 14])

            # No idea why it sometimes gives a completely incorrect value
            if 'html' in self.github_version:
                self.close()
                self.deleteLater()
                return

            self.github_version = float(self.github_version[11 : 14])

        def init_progressbar(self):
            self.bar = QProgressBar(self)
            self.bar.resize(420, 12)
            self.bar.setValue(0)
            self.bar.move(Qt.AlignmentFlag.AlignCenter, 180)
            self.bar.setTextVisible(False)

        def init_loading_label(self):
            self.img_holder = QLabel(self)
            self.img_holder.resize(680, 350)
            self.tiger_pic = QPixmap(TigerWalletImage.loading_bg)
            self.tiger_pic = self.tiger_pic.scaled(QSize(680, 350))
            self.img_holder.setPixmap(self.tiger_pic)

            self.label = QLabel("Downloading update...", self)
            self.label.resize(740, 216)
            self.label.move(140, 20)

        def init_asset_label(self):
            self.label2 = QLabel(self)
            self.label2.resize(680, 30)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label2.move(0, 220)

        def emit_progress(self, n):
            num = 0

            if (
                self.execution_method != 'pip-install-executable'
                and self.execution_method != 'python-command'
            ):
                if n <= 0:
                    num = 0

                else:
                    num = (
                        (
                            float(n)
                            / float(self.total_file_size)
                        )
                        * 100.0
                    )

            self.label2.setText(
                f"{str(int(num))} %"
            )

            self.bar.setValue(n)

        def download_update(self):
            ver = 'v' + str(self.github_version)

            # Using pyinstaller
            if self.execution_method == 'pyinstaller-executable':
                self.duw = DownloadUpdateWorker(
                    parent=self,
                    method_of_execution='pyinstaller-executable',
                    version=ver
                )

                def is_done(res):
                    if res:
                        if _platform() == 'nt':
                            msgbox(
                                'New version downloaded to path: '
                                + f"C:\\Users\\{prog.current_usr}\\"
                                + f"tigerwallet-{ver[1 : len(ver)]}-x86-64.exe",
                            )

                            subprocess.run(
                                [
                                    f"/home/{prog.current_usr}/"
                                    f"tigerwallet-{ver[1 : len(ver)]}-x86-64.exe"
                                ]
                            )

                        else:
                            msgbox(
                                'New version downloaded to path: '
                                + f"/home/{prog.current_usr}/"
                                + f"tigerwallet-{ver[1 : len(ver)]}-x86-64",
                            )

                            # Make it executable
                            subprocess.run(
                                [
                                    'chmod',
                                    '+x',
                                    f"tigerwallet-{ver[1 : len(ver)]}-x86-64"
                                ]
                            )

                            # Launch the updated version
                            subprocess.run(
                                [
                                    f"/home/{prog.current_usr}/"
                                    f"tigerwallet-{ver[1 : len(ver)]}-x86-64"
                                ]
                            )

                        self.thread.quit()
                        self.duw.quit()
                        self.thread.deleteLater()
                        self.duw.deleteLater()

                        self.close()
                        self.deleteLater()

                self.duw.moveToThread(self.thread)
                self.duw.dl_prog.connect(self.emit_progress)
                self.duw.is_finished.connect(is_done)
                self.thread.started.connect(self.duw.work)
                self.thread.start()

            # Using AppImage
            elif self.execution_method == 'appimage-executable':
                self.duw = DownloadUpdateWorker(
                    parent=self,
                    method_of_execution='appimage-executable',
                    version=ver
                )

                def is_done(res):
                    if res:
                        msgbox(
                            'New version downloaded to path: '
                            + f"/home/{prog.current_usr}/"
                            + f"tigerwallet-{ver[1 : len(ver)]}-x86-64.AppImage",
                        )

                        self.thread.quit()
                        self.duw.quit()
                        self.thread.deleteLater()
                        self.duw.deleteLater()

                        self.close()
                        self.deleteLater()

                        subprocess.run(
                            [
                                f"/home/{prog.current_usr}/"
                                f"tigerwallet-{ver[1 : len(ver)]}-x86-64.AppImage"
                            ]
                        )

                self.duw.moveToThread(self.thread)
                self.duw.dl_prog.connect(self.emit_progress)
                self.duw.is_finished.connect(is_done)
                self.thread.started.connect(self.duw.work)
                self.thread.start()

            # Using tigerwallet installed via git+pip
            elif self.execution_method == 'pip-install-executable':
                self.duw = DownloadUpdateWorker(
                    parent=self,
                    method_of_execution='pip-install-executable'
                )

                self.label.setText('Running pip install...')
                self.label.resize(740, 216)
                self.label.move(154, 20)
                self.label2.hide()

                def pip_install_finished(completed):
                    if completed:
                        msgbox('Update complete')

                        self.thread.quit()
                        self.duw.quit()
                        self.thread.deleteLater()
                        self.duw.deleteLater()

                        self.close()
                        self.deleteLater()

                        subprocess.run(['tigerwallet'])

                self.duw.moveToThread(self.thread)
                #self.duw.dl_prog.connect(self.emit_progress)
                self.duw.is_finished.connect(pip_install_finished)
                self.thread.started.connect(self.duw.work)
                self.thread.start()

            # Using source code directly
            elif self.execution_method == 'python-command':
                self.duw = DownloadUpdateWorker(
                    parent=self,
                    method_of_execution='python-command',
                    version=ver
                )

                self.label2.hide()

                def is_done(res):
                    if res:
                        if _platform() == 'nt':
                            msgbox(
                                'New version downloaded to path: '
                                + f"C:\\Users\\{prog.current_usr}\\"
                                + 'Desktop\\'
                                + 'TigerWallet-main'
                            )

                        else:
                            msgbox(
                                'New version downloaded to path: '
                                + f"/home/{prog.current_usr}"
                                + 'TigerWallet-main'
                            )

                        self.thread.quit()
                        self.duw.quit()
                        self.thread.deleteLater()
                        self.duw.deleteLater()

                        self.close()
                        self.deleteLater()

                        if _platform() == 'nt':
                            subprocess.run(
                                [
                                    sys.executable,
                                    f"C:\\Users\\{prog.current_usr}\\"
                                    + 'Desktop\\TigerWallet-main\\'
                                    + 'src\\TigerWallet\\tigerwallet.py'
                                ]
                            )

                        else:
                            subprocess.run(
                                [
                                    sys.executable,
                                    f"/home/{prog.current_usr}/"
                                    + 'TigerWallet-main/src/'
                                    + 'TigerWallet/tigerwallet.py'
                                ]
                            )

                self.duw.moveToThread(self.thread)
                self.duw.dl_prog.connect(self.emit_progress)
                self.duw.is_finished.connect(is_done)
                self.thread.started.connect(self.duw.work)
                self.thread.start()

            # Using .exe installer
            elif self.execution_method == 'exe-installer':
                self.duw = DownloadUpdateWorker(
                    parent=self,
                    method_of_execution='exe-installer',
                    version=ver
                )

                def is_done(res):
                    if res:
                        msgbox(
                            'New version downloaded to path: '
                            + self.local_path
                            + f"/tigerwallet-{ver[1:len(ver)]}-installer.exe"
                        )

                        self.thread.quit()
                        self.duw.quit()
                        self.thread.deleteLater()
                        self.duw.deleteLater()

                        self.close()
                        self.deleteLater()

                        subprocess.run(
                            [
                                self.local_path
                               +  f"tigerwallet-{ver[1 : len(ver)]}-x86-64.AppImage"
                            ]
                        )

                self.duw.moveToThread(self.thread)
                self.duw.dl_prog.connect(self.emit_progress)
                self.duw.is_finished.connect(is_done)
                self.thread.started.connect(self.duw.work)
                self.thread.start()

    # Fixed program crash in v1.5
    # when adding an invalid RPC
    # Visual improvement to scrollbar
    # Changed visuals in v3.1
    class Settings(QWidget):
        """
        Settings window - used by UserWallet
        """
        def __init__(self, master):
            super().__init__()
            self.master = master
            self.init_window()
            self.init_options()
            self.init_about()

            
            if prog.configs["theme"] == "default_dark":
                self.apply_dark_mode()
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.apply_light_mode()
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

        def init_window(self):
            self.setWindowTitle("TigerWallet  -  Settings")
            self.setFixedWidth(600)
            self.setFixedHeight(500)

            align_to_center(self)
            add_round_corners(self)

            self.border = QLabel(self)
            self.border.resize(578, 430)
            self.border.move(10, 60)

            self.list_ = QListWidget(self)
            self.list_.setMinimumSize(480, 384)
            self.list_.move(40, 90)
            self.list_.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.list_.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )
            self.list_.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.list_.setIconSize(QSize(32, 32))

            self.settingslbl = QLabel("Settings", self)
            self.settingslbl.resize(148, 40)
            self.settingslbl.move(220, 40)
            self.settingslbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.close_settings_window = QPushButton(
                text=" Return to wallet",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )
            self.close_settings_window.resize(178, 34)
            self.close_settings_window.setIconSize(QSize(24, 24))
            self.close_settings_window.move(30, 15)
            self.close_settings_window.clicked.connect(
                self.master.clear_tab8
            )

            self.close_prog = QPushButton(
                text=" Quit",
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.close_prog.resize(80, 34)
            self.close_prog.setIconSize(QSize(24, 24))
            self.close_prog.move(490, 15)
            self.close_prog.clicked.connect(app.closeAllWindows)

        #
        def init_options(self):
            self.list_.clearSelection()
            
            self.options = {
                "rpc": QListWidgetItem(" RPC settings"),
                "pass": QListWidgetItem(" Change password"),
                "show_pkey": QListWidgetItem(" Show private key"),
                "gif_on_off": QListWidgetItem(" Play loading screen gif"),
                "lock_wallet": QListWidgetItem(" Configure lock settings"),
                "theme_switch": QListWidgetItem(" Switch to light mode"),
                "about": QListWidgetItem(" About TigerWallet"),
            }

            for option in self.options:
                self.options[option].setSizeHint(QSize(0, 50))
                self.list_.addItem(self.options[option])

            if prog.configs['play_loading_gif']:
                self.options['gif_on_off'].setText(
                    self.options['gif_on_off'].text() + ': ON'
                )

            elif not prog.configs['play_loading_gif']:
                self.options['gif_on_off'].setText(
                    self.options['gif_on_off'].text() + ': OFF'
                )

            if prog.configs['theme'] == 'default_dark':
                self.options['theme_switch'].setText(
                    f"{self.options['theme_switch'].text()} light mode"
                )

                self.options['theme_switch'].setIcon(
                    TigerWalletImage.sun_blue
                )

            elif prog.configs['theme'] == 'default_light':
                self.options['theme_switch'].setText(
                    f"{self.options['theme_switch'].text()} dark mode"
                )

                self.options['theme_switch'].setIcon(
                    TigerWalletImage.moon_blue
                )


            self.options["rpc"].setIcon(TigerWalletImage.rpc_blue)
            self.options["pass"].setIcon(TigerWalletImage.lock_blue)
            self.options["show_pkey"].setIcon(TigerWalletImage.key_blue)
            self.options["gif_on_off"].setIcon(TigerWalletImage.gif_blue)
            self.options["lock_wallet"].setIcon(TigerWalletImage.pass_blue)
            self.options["about"].setIcon(TigerWalletImage.about_blue)

            def user_choice(item):
                if item.text() == self.options["rpc"].text():
                    self.list_.clearSelection()
                    self.change_rpc()

                elif item.text() == self.options["pass"].text():
                    self.list_.clearSelection()
                    self.change_password_window()

                elif item.text() == self.options["gif_on_off"].text():
                    self.list_.clearSelection()
                    text = self.options['gif_on_off'].text()

                    if prog.configs['play_loading_gif']:
                        text = text.replace('ON', 'OFF')
                        self.options['gif_on_off'].setText(text)

                        prog.configs['play_loading_gif'] = False

                    elif not prog.configs['play_loading_gif']:
                        text = text.replace('OFF', 'ON')
                        self.options['gif_on_off'].setText(text)

                        prog.configs['play_loading_gif'] = True

                    with open(prog.conf_file, mode='w') as f:
                        json.dump(
                            obj=prog.configs,
                            fp=f,
                            indent=4
                        )

                elif item.text() == self.options["show_pkey"].text():
                    prog.invoked_from_settings = True
                    self.list_.clearSelection()

                    self.vp = ValidatePassword()
                    self.vp.show()

                elif item.text() == self.options["lock_wallet"].text():
                    self.list_.clearSelection()
                    self.change_lock_timer()

                elif item.text() == self.options["about"].text():
                    self.list_.clearSelection()
                    self.launch_about_window()

                elif item.text() == self.options['theme_switch'].text():
                    self.list_.clearSelection()

                    if prog.configs['theme'] == 'default_dark':
                        self.options['theme_switch'].setIcon(
                            TigerWalletImage.sun_blue
                        )

                        prog.configs["theme"] = "default_light"

                        with open(
                            prog.local_path + 'light.css',
                            mode='r',
                            encoding="utf-8"
                        ) as f:
                            app.setStyleSheet(f.read())

                        self.apply_light_mode()
                        self.master.apply_default_light_theme()

                    elif prog.configs["theme"] == "default_light":
                        self.options['theme_switch'].setIcon(
                            TigerWalletImage.moon_blue
                        )

                        prog.configs["theme"] = "default_dark"

                        with open(
                            prog.local_path + 'dark.css',
                            mode='r',
                            encoding="utf-8"
                        ) as f:
                            app.setStyleSheet(f.read())

                        self.apply_dark_mode()
                        self.master.apply_default_dark_theme()

                    with open(prog.conf_file, "w") as f:
                        json.dump(prog.configs, f, indent=4)

            self.list_.itemClicked.connect(user_choice)
            self.list_.setIconSize(QSize(40, 40))
            self.list_.setStyleSheet(
                'margin-left: 8px;' 
                + 'background: transparent'
            )

        def init_about(self):
            from PyQt6.QtWidgets import QTabWidget
            from PyQt6.QtCore import QT_VERSION_STR

            self.about_parent = QWidget(self)
            self.about_parent.resize(570, 430)
            self.about_parent.move(10, 50)

            self.tabs = QTabWidget(parent=self.about_parent)
            self.tabs.resize(500, 300)
            self.tabs.move(22, 56)

            self.about = QWidget()
            self.author = QWidget()
            self.thanks = QWidget()

            self.tabs.addTab(self.about, "About")
            self.tabs.addTab(self.author, "Author")
            self.tabs.addTab(self.thanks, "Thank you to")

            y_coords = [70, 110, 150]

            # About tab
            self.about_item = [QLabel(self.tabs) for i in range(3)]
            self.about_item[0].setText(f"Version: {TigerWalletVersion}")
            self.about_item[1].setText(
                f"Python version: {sys.version_info[0]}"
            )
            self.about_item[2].setText(f"Qt version: {QT_VERSION_STR}")

            for i in range(3):
                self.about_item[i].resize(430, 30)
                self.about_item[i].move(13, y_coords[i])

            # Author tab
            self.author_item = [QLabel(self.tabs) for i in range(3)]
            self.author_item[0].setText("Author: Serpenseth")
            self.author_item[1].setText("Email: serpenseth@tuta.io")
            self.author_item[2].setText(
                "GitHub: https://github.com/Serpenseth"
            )

            self.author_item[1].setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.author_item[2].setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )

            for i in range(3):
                self.author_item[i].resize(400, 30)
                self.author_item[i].move(13, y_coords[i])
                self.author_item[i].hide()

            # Thanks to tab
            self.thanks_list = QListWidget(self.tabs)
            self.thanks_list.resize(380, 280)
            self.thanks_list.move(-5, 50)
            self.thanks_list.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )
            self.thanks_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.thanks_list.hide()

            self.thanks_item = [QListWidgetItem() for i in range(4)]

            self.shoutout_list = [
                'Lillie G (X: @lkg_cla)',
                'Mikko Ohtamaa (answering questions)',
                'DefiDeBlitzen (answering questions)',
                'Maka (answering questions)',
                'felipe (answering questions)'
            ]

            for index in range(4):
                self.thanks_item[index].setText(
                    self.shoutout_list[index]
                )

                self.thanks_list.insertItem(
                    index,
                    self.thanks_item[index]
                )

                self.thanks_list.item(index).setSizeHint(QSize(280, 40))

            def tab_switcher(index):
                if index == 0:
                    [self.about_item[i].show() for i in range(3)]
                    [self.author_item[i].hide() for i in range(3)]

                    self.thanks_list.hide()

                elif index == 1:
                    [self.about_item[i].hide() for i in range(3)]
                    [self.author_item[i].show() for i in range(3)]

                    self.thanks_list.hide()

                elif index == 2:
                    [self.about_item[i].hide() for i in range(3)]
                    [self.author_item[i].hide() for i in range(3)]

                    self.thanks_list.show()

            self.tabs.tabBarClicked.connect(tab_switcher)

            self.close_about = QPushButton(
                text=" Return",
                parent=self.about_parent,
                icon=TigerWalletImage.receive_blue,
            )

            self.close_about.resize(200, 50)
            self.close_about.setIconSize(QSize(32, 32))
            self.close_about.move(180, 366)
            self.close_about.clicked.connect(
                lambda: [
                    self.about_parent.hide(),
                    self.list_.show()
                ]
            )
            self.about_parent.hide()

        def launch_about_window(self):
            self.list_.hide()
            self.about_parent.show()

        def apply_dark_mode(self):
            self.setStyleSheet("background-color: #0a0f18;")
            self.about_parent.setStyleSheet("background-color: transparent;")
            
            self.close_settings_window.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )
            
            self.close_prog.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.settingslbl.setStyleSheet(
                "font-size: 30px;"
                "color: #627eea;"
                "background: #0a0f18;"
                'border-radius: 6px;'
            )

            for i in range(3):
                self.about_item[i].setStyleSheet(
                    "background: #0a0f18;"
                    "color: #b0c4de;"
                    "font: 18px;"
                )

                self.author_item[i].setStyleSheet(
                    "background: #0a0f18;"
                    "color: #b0c4de;"
                    "font: 18px;"
                )

            self.thanks_list.setStyleSheet(
                "QListView {font-size: 18px;"
                + "color: #b0c4de;"
                + "border-radius: 16px;"
                + "background: transparent;}"
                
                + 'QListView::item:hover {background: transparent;'
                + 'padding-left: 0px;'
                + 'color: #b0c4de;}'
            )


            self.tabs.setStyleSheet(
                "QTabWidget {background: #0a0f18;"
                "border-radius: 6px;}"
                "QTabWidget::pane {border: 1px solid lightgray;"
                "border-radius: 6px;}"
                "QTabBar::tab {background: #0a0f18;"
                "color: #b0c4de;"
                "border-radius: 6px;"
                "border-top-left-radius: 4px;"
                "border-top-right-radius: 4px;"
                "border-bottom-left-radius: 0px;"
                "border-bottom-right-radius: 0px;"
                "font: 16px;"
                "padding: 9px;}"
                "QTabBar::tab:selected {border-top: 4px solid #627eea;"
                "border-bottom:  3px solid #1e1e1e;"
                "font: 20px;}"
                "QTabBar::tab:hover {border-top: 3px solid gray;"
                "border-bottom:  3px solid #1e1e1e;}"
            )

            self.close_about.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

        def apply_light_mode(self):
            self.setStyleSheet("background-color: #eff1f3;")
            self.about_parent.setStyleSheet("background-color: transparent;")

            self.close_settings_window.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )
            
            self.close_prog.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.settingslbl.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: #eff1f3;"
            )

            for i in range(3):
                self.about_item[i].setStyleSheet(
                    "background: #eff1f3;"
                    + "color: #3c598e;"
                    + "font: 18px;"
                )

                self.author_item[i].setStyleSheet(
                    "background: #eff1f3;"
                    + "color: #3c598e;"
                    + "font: 18px;"
                )
            
            self.thanks_list.setStyleSheet(
                "QListView {font-size: 18px;"
                + "color: #3c598e;"
                + "border-radius: 16px;"
                + "background: transparent;}"
                
                + 'QListView::item:hover {background: transparent;'
                + 'padding-left: 0px;'
                + 'color: #3c598e;}'
            )

            self.tabs.setStyleSheet(
                "QTabWidget {background: #eff1f3;"
                "border-radius: 4px;}"
                "QTabWidget::pane {border: 1px solid lightgray;"
                "border-radius: 4px;}"
                "QTabBar::tab {background: #eff1f3;"
                "color: #3c598e;"
                "border-radius: 4px;"
                "border-top-left-radius: 4px;"
                "border-top-right-radius: 4px;"
                "border-bottom-left-radius: 0px;"
                "border-bottom-right-radius: 0px;"
                "font: 16px;"
                "padding: 9px;}"
                "QTabBar::tab:selected {border-top: 4px solid #3c598e;"
                "border-bottom:  3px solid #eaeaeb;"
                "font: 20px;}"
                "QTabBar::tab:hover {border-top: 3px solid gray;"
                "border-bottom:  3px solid #eaeaeb;}"
            )

            self.close_about.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

        def change_rpc(self):
            self.list_.hide()

            self.rpc_list_options = QListWidget(self)
            self.rpc_list_options.resize(550, 196)
            self.rpc_list_options.move(30, 80)
            self.rpc_list_options.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.rpc_list = []

            with open(prog.rpc_list_file, "r") as f:
                self.rpc_list = json.load(f)

            self.rpc_list = self.rpc_list['eth']
            self.prev = 0

            for item in enumerate(self.rpc_list):
                self.rpc_list_options.insertItem(*item)

            for i in range(len(self.rpc_list)):
                self.rpc_list_options.item(i).setSizeHint(QSize(480, 50))

                if (
                    self.rpc_list[i]
                    == prog.configs["rpc"]['eth']
                ):
                    self.rpc_list_options.item(i).setText(
                        self.rpc_list_options.item(i).text()
                        + " (current)"
                    )

                    self.prev = i

            self.rpc_list_options.show()
            self.rpc_list_options.itemClicked.connect(self._rpc_choice)

            self.delete_rpc_btn = QPushButton(
                text=" Delete RPC",
                parent=self,
                icon=TigerWalletImage.close_blue
            )

            self.delete_rpc_btn.setFixedSize(220, 50)
            self.delete_rpc_btn.setIconSize(QSize(32, 32))
            self.delete_rpc_btn.move(334, 328)
            self.delete_rpc_btn.show()
            self.delete_rpc_btn.clicked.connect(self.rm_rpc_window)

            #
            self.add_rpc_btn = QPushButton(
                text=" Add RPC",
                parent=self,
                icon=TigerWalletImage.plus_blue
            )

            self.add_rpc_btn.setFixedSize(220, 50)
            self.add_rpc_btn.setIconSize(QSize(32, 32))
            self.add_rpc_btn.move(46, 328)
            self.add_rpc_btn.show()
            self.add_rpc_btn.clicked.connect(self.add_rpc_window)

            self.cancel_rpc_btn = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.cancel_rpc_btn.setFixedSize(220, 50)
            self.cancel_rpc_btn.setIconSize(QSize(32, 32))
            self.cancel_rpc_btn.move(186, 398)
            self.cancel_rpc_btn.show()
            self.cancel_rpc_btn.clicked.connect(self._close_rpc_window)

            if prog.configs["theme"] == "default_dark":
                self.delete_rpc_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.add_rpc_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.cancel_rpc_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.delete_rpc_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.add_rpc_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.cancel_rpc_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

        def add_rpc_window(self):
            self.rpc_list_options.hide()
            self.cancel_rpc_btn.hide()
            self.add_rpc_btn.hide()

            self.enter_rpc_msg = QLabel(
                text="Enter the HTTPS or HTTP of the RPC you wish to add:",
                parent=self,
            )
            self.enter_rpc_msg.resize(500, 50)
            self.enter_rpc_msg.move(50, 100)
            self.enter_rpc_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.enter_rpc_msg.show()

            self.add_rpc_https = QLineEdit(self)
            self.add_rpc_https.resize(420, 40)
            self.add_rpc_https.setPlaceholderText(
                "example: https://ethereum-rpc.publicnode.com"
            )
            self.add_rpc_https.move(88, 180)
            self.add_rpc_https.show()

            self.rpclbl = QLabel("RPC:", self)
            self.rpclbl.resize(50, 40)
            self.rpclbl.move(40, 180)
            self.rpclbl.show()

            self.add_rpc_port = QLineEdit(self)
            self.add_rpc_port.resize(420, 40)
            self.add_rpc_port.setPlaceholderText(
                "This field is optional, unless your RPC requires it"
            )
            self.add_rpc_port.move(88, 240)
            self.add_rpc_port.show()

            self.portlbl = QLabel("Port:", self)
            self.portlbl.resize(50, 40)
            self.portlbl.move(40, 240)
            self.portlbl.show()

            def _close_add_rpc_window():
                self.rpc_list_options.show()
                self.cancel_rpc_btn.show()
                self.add_rpc_btn.show()

                self.add_user_rpc.close()
                self.enter_rpc_msg.close()
                self.add_rpc_https.close()
                self.cancel_add_rpc.close()
                self.rpclbl.close()
                self.portlbl.close()
                self.add_rpc_port.close()

            self.cancel_add_rpc = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )
            self.cancel_add_rpc.setFixedSize(220, 50)
            self.cancel_add_rpc.setIconSize(QSize(32, 32))
            self.cancel_add_rpc.move(46, 328)
            self.cancel_add_rpc.show()
            self.cancel_add_rpc.clicked.connect(_close_add_rpc_window)

            def _test_rpc(rpc):
                if len(rpc) == 0:
                    errbox("RPC field is empty")
                    return

                elif  "ws" in rpc or "wss" in rpc:
                    errbox("ws or wss is currently not supported")
                    return

                elif (
                    rpc.find("https") != 0
                    or rpc.find("http") != 0
                ):
                    errbox("Invalid RPC")
                    return

                list_of_bad_eth_RPCs = [
                    "https://ethereum.blockpi.network/v1/rpc/public",
                    "https://eth.llamarpc.com/",
                ]

                if rpc in list_of_bad_eth_RPCs:
                    errbox(
                        rpc
                        + "is known to cause issues with TigerWallet.\n"
                        + "Please use another RPC"
                    )
                    return

                with open(prog.rpc_list_file, "r") as f:
                    tmp_list = json.load(f)

                    if rpc in tmp_list['eth']:
                        errbox("RPC is already on your list")
                        return

                port = self.add_rpc_port.text()

                for i in range(len(port)):
                    if (
                        ord(port[i]) < 48
                        or ord(port[i]) > 57
                    ):
                        errbox("Ports only consist of numbers")
                        return

                class _TestingRPCMsgBox(QWidget):
                    def __init__(self, master):
                        super().__init__()

                        self.init_window()

                        if prog.configs["theme"] == "default_dark":
                            self.setStyleSheet("background: #0a0f18")
                            
                            self.border.setStyleSheet(
                                "border: 1px solid #1e2b45;"
                                + "border-radius: 16px;"
                                + "background: transparent;"
                            )

                            self.lbl.setStyleSheet(
                                "font-size: 17px;"
                                + "color: #b0c4de;"
                                + "background: transparent;"
                            )

                        elif prog.configs["theme"] == "default_light":
                            self.setStyleSheet("background: #eff1f3")
                            
                            self.border.setStyleSheet(
                                "border: 1px solid #bbc8e2;"
                                + "border-radius: 16px;"
                                + "background: transparent;"
                            )

                            self.lbl.setStyleSheet(
                                "font-size: 17px;"
                                + "color: #3c598e;"
                                + "background: transparent;"
                            )

                    def init_window(self):
                        self.setWindowTitle("TigerWallet")
                        self.setFixedWidth(400)
                        self.setFixedHeight(160)

                        self.lbl = QLabel(
                            text="Trying to connect to the provided RPC...\n"
                            + "Please wait a few seconds...",
                            parent=self,
                        )
                        self.lbl.resize(380, 130)
                        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.lbl.move(10, 14)
                        self.lbl.setWordWrap(True)

                        add_round_corners(self)

                        self.border = QLabel(self)
                        self.border.resize(401, 160)

                class _TestRPCWorker(QThread):
                    done = pyqtSignal(bool)
                    has_error = pyqtSignal(bool)

                    def __init__(self, master):
                        super().__init__()
                        self.master = master
                        self.rpc = self.master.add_rpc_https.text()
                        self.port = self.master.add_rpc_port.text()
                        self.err = 0

                    def work(self):
                        self.done.emit(False)
                        self.has_error.emit(False)

                        provider = Web3.HTTPProvider(
                            self.rpc + self.port,
                            exception_retry_configuration=None,
                            request_kwargs={"timeout": (5, 1)},
                        )

                        patch_provider(provider)

                        _w3 = Web3(provider)

                        try:
                            good = _w3.is_connected()

                            if not good:
                                self.err = 1
                                self.done.emit(True)

                            else:
                                self.done.emit(True)

                        except orjson.JSONDecodeError:
                            self.err = 2
                            self.done.emit(True)


                self.trpcmb = _TestingRPCMsgBox(self)
                self.test_rpc_worker = _TestRPCWorker(self)
                self.test_rpc_thread = QThread()

                def _kill_thread_if_done(is_done):
                    if is_done:
                        self.test_rpc_worker.quit()
                        self.test_rpc_thread.quit()
                        self.test_rpc_thread.wait()

                        if self.test_rpc_worker.err == 1:
                            self.trpcmb.close()
                            errbox(
                                'Failed to connect to '
                                + self.add_rpc_https.text()
                                + f" {self.add_rpc_port.text()}"
                            )
                            return

                        elif self.test_rpc_worker.err == 2:
                            self.trpcmb.close()
                            errbox('Input provided is not a web3 RPC')
                            return

                        r = (
                            self.add_rpc_https.text()
                            + self.add_rpc_port.text()
                        )

                        if not r in self.rpc_list:
                            self.rpc_list.append(
                                self.add_rpc_https.text()
                                + self.add_rpc_port.text()
                            )

                        else:
                            self.trpcmb.close()
                            errbox("RPC is already on your list")
                            return

                        with open(prog.rpc_list_file, "w") as f:
                            json.dump(
                                obj=self.rpc_list,
                                fp=f,
                                indent=4
                            )

                        self.rpc_list_options.addItem(
                            self.add_rpc_https.text()
                            + self.add_rpc_port.text()
                        )

                        self.rpc_list_options.item(
                            len(self.rpc_list) - 1
                        ).setSizeHint(QSize(0, 54))

                        self.trpcmb.close()
                        msgbox("RPC added successfully")

                self.test_rpc_worker.moveToThread(self.test_rpc_thread)
                self.test_rpc_worker.done.connect(_kill_thread_if_done)
                self.test_rpc_thread.started.connect(
                    self.test_rpc_worker.work
                )
                self.test_rpc_thread.start()
                self.trpcmb.show()

            self.add_rpc_https.returnPressed.connect(
                lambda: _test_rpc(
                    self.add_rpc_https.text()
                )
            )

            self.add_user_rpc = QPushButton(
                text=" Add RPC",
                parent=self,
                icon=TigerWalletImage.rpc_blue
            )
            self.add_user_rpc.setFixedSize(220, 50)
            self.add_user_rpc.setIconSize(QSize(32, 32))
            self.add_user_rpc.move(334, 328)
            self.add_user_rpc.show()
            self.add_user_rpc.clicked.connect(
                lambda: _test_rpc(
                    self.add_rpc_https.text()
                    )
            )

            if prog.configs["theme"] == "default_dark":
                self.cancel_add_rpc.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.add_user_rpc.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.enter_rpc_msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #b0c4de;"
                    + "background: transparent;"
                )

                self.rpclbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #9fb1ca;"
                    + "background: transparent;"
                )

                self.portlbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #9fb1ca;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.cancel_add_rpc.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.add_user_rpc.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.enter_rpc_msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.rpclbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.portlbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

        def rm_rpc_window(self):
            self.settingslbl.hide()
            self.delete_rpc_btn.hide()
            self.add_rpc_btn.hide()
            self.cancel_rpc_btn.move(186, 348)

            self.selectlbl = QLabel(
                text="Click on the RPC that you want to remove",
                parent=self
            )
            self.selectlbl.resize(388, 28)
            self.selectlbl.move(96, 36)
            self.selectlbl.show()
            self.selectlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            def _rm_choice(item):
                res = questionbox(
                    f"You are about to delete {item.text()}. Continue?"
                )

                if res:
                    _row = self.rpc_list_options.indexFromItem(item).row()
                    self.rpc_list_options.takeItem(_row)
                    del self.rpc_list[_row]

                    prog.rpc_list['eth'] = self.rpc_list

                    with open(prog.rpc_list_file, "w") as f:
                        json.dump(
                            obj=prog.rpc_list,
                            fp=f,
                            indent=4
                        )

                    if "(current)" in item.text():
                        _tmp = self.rpc_list[_row - 1]
                        _tmp[: _tmp.find("(")]

                        self.rpc_list_options.item(_row - 1).setText(
                            self.rpc_list_options.item(_row - 1).text()
                            + " (current)"
                        )

                        with open(prog.conf_file, "w") as ff:
                            prog.configs["rpc"]['eth'] = _tmp

                            json.dump(
                                obj=prog.configs,
                                fp=ff,
                                indent=4
                            )

                    self.rpc_list_options.clearSelection()
                    msgbox(f"{item.text()} deleted")
                    return

                elif not res:
                    self.rpc_list_options.clearSelection()
                    return

            self.rpc_list_options.itemClicked.disconnect()
            self.rpc_list_options.itemClicked.connect(_rm_choice)

            def _close_delrpc_window():
                self.settingslbl.show()
                self.delete_rpc_btn.show()
                self.add_rpc_btn.show()
                self.selectlbl.close()

                self.cancel_rpc_btn.move(186, 398)
                self.cancel_rpc_btn.clicked.connect(self._close_rpc_window)
                self.rpc_list_options.itemClicked.disconnect()
                self.rpc_list_options.itemClicked.connect(self._rpc_choice)
                return

            self.cancel_rpc_btn.clicked.disconnect()
            self.cancel_rpc_btn.clicked.connect(_close_delrpc_window)

            if prog.configs["theme"] == "default_dark":
                self.selectlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #627eea;"
                    + "background: #1e1e1e;"
                )

            elif prog.configs["theme"] == "default_light":
                self.selectlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #627eea;"
                    + "background: #eaeaeb;"
                )

        def change_password_window(self):
            self.list_.hide()
            self.opt1 = 1
            self.opt2 = 1
            self.opt3 = 1

            self.current_password = QLineEdit(self)
            self.current_password.resize(332, 40)
            self.current_password.move(170, 130)
            self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.current_password.show()

            self.current_password_lbl = QLabel("Current password:", self)
            self.current_password_lbl.resize(120, 40)
            self.current_password_lbl.move(40, 130)
            self.current_password_lbl.show()

            self.new_password1 = QLineEdit(self)
            self.new_password1.resize(332, 40)
            self.new_password1.move(170, 190)
            self.new_password1.setEchoMode(QLineEdit.EchoMode.Password)
            self.new_password1.show()

            self.new_password1_lbl = QLabel("New password:", self)
            self.new_password1_lbl.resize(120, 40)
            self.new_password1_lbl.move(40, 190)
            self.new_password1_lbl.show()

            self.new_password2 = QLineEdit(self)
            self.new_password2.resize(332, 40)
            self.new_password2.move(170, 250)
            self.new_password2.setEchoMode(QLineEdit.EchoMode.Password)
            self.new_password2.show()

            self.new_password2_lbl = QLabel("Repeat password:", self)
            self.new_password2_lbl.resize(130, 40)
            self.new_password2_lbl.move(40, 250)
            self.new_password2_lbl.show()

            def _unhide1():
                if self.opt1 == 1:
                    self.btn_eye1.setIcon(TigerWalletImage.opened_eye_blue)
                    self.current_password.setEchoMode(
                        QLineEdit.EchoMode.Normal
                    )
                    self.opt1 = 0

                elif self.opt1 == 0:
                    self.btn_eye1.setIcon(TigerWalletImage.closed_eye_blue)
                    self.current_password.setEchoMode(
                        QLineEdit.EchoMode.Password
                    )
                    self.opt1 = 1

            def _unhide2():
                if self.opt2 == 1:
                    self.btn_eye2.setIcon(TigerWalletImage.opened_eye_blue)
                    self.new_password1.setEchoMode(QLineEdit.EchoMode.Normal)
                    self.opt2 = 0

                elif self.opt2 == 0:
                    self.btn_eye2.setIcon(TigerWalletImage.closed_eye_blue)
                    self.new_password1.setEchoMode(QLineEdit.EchoMode.Password)
                    self.opt2 = 1

            def _unhide3():
                if self.opt3 == 1:
                    self.btn_eye3.setIcon(TigerWalletImage.opened_eye_blue)
                    self.new_password2.setEchoMode(QLineEdit.EchoMode.Normal)
                    self.opt3 = 0

                elif self.opt3 == 0:
                    self.btn_eye3.setIcon(TigerWalletImage.closed_eye_blue)
                    self.new_password2.setEchoMode(QLineEdit.EchoMode.Password)
                    self.opt3 = 1

            def _is_current_pass_valid():
                passwd = self.current_password.text()

                if len(passwd) == 0:
                    errbox("Enter your current password in order to change it")
                    return False

                try:
                    with open(prog.nameofwallet, "r") as f:
                        Account.decrypt(json.load(f), password=passwd)
                except ValueError:
                    errbox("Wrong current password")
                    return False
                return True

            def _are_same_passwords():
                if len(self.new_password1.text()) == 0:
                    errbox("Empty passwords are a no no")
                    return False

                if self.new_password1.text() != self.new_password2.text():
                    errbox("Passwords did not match")
                    return False

                return True

            def _validate_passwords():
                if _is_current_pass_valid():
                    if _are_same_passwords():
                        self._change_password(self.new_password1.text())
                    else:
                        return
                else:
                    return

            self.btn_eye1 = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_eye1.setIconSize(QSize(24, 24))
            self.btn_eye1.move(521, 138)
            self.btn_eye1.show()
            self.btn_eye1.clicked.connect(_unhide1)

            self.btn_eye2 = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_eye2.setIconSize(QSize(24, 24))
            self.btn_eye2.move(521, 198)
            self.btn_eye2.show()
            self.btn_eye2.clicked.connect(_unhide2)

            self.btn_eye3 = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_eye3.setIconSize(QSize(24, 24))
            self.btn_eye3.move(521, 258)
            self.btn_eye3.show()
            self.btn_eye3.clicked.connect(_unhide3)

            self.checkbox = QCheckBox(self)
            self.checkbox.setText(
                "I have written down my new password"
            )
            self.checkbox.resize(320, 40)
            self.checkbox.move(150, 315)
            self.checkbox.show()

            self.cancel_change_passwd = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )
            self.cancel_change_passwd.setFixedSize(220, 50)
            self.cancel_change_passwd.setIconSize(QSize(24, 24))
            self.cancel_change_passwd.move(46, 378)
            self.cancel_change_passwd.show()

            self.continue_change_passwd = QPushButton(
                text=" Complete",
                parent=self,
                icon=TigerWalletImage.checkmark
            )
            self.continue_change_passwd.setFixedSize(220, 50)
            self.continue_change_passwd.setIconSize(QSize(28, 28))
            self.continue_change_passwd.move(328, 378)
            self.continue_change_passwd.setEnabled(False)
            self.continue_change_passwd.show()

            def _enable_continue_if_checked(is_checked):
                if is_checked == Qt.CheckState.Checked:
                    self.current_password.returnPressed.connect(
                        _validate_passwords
                    )
                    self.checkbox.setEnabled(False)
                    self.continue_change_passwd.setEnabled(True)

            self.checkbox.checkStateChanged.connect(
                _enable_continue_if_checked
            )
            self.continue_change_passwd.clicked.connect(
                _validate_passwords
            )
            self.cancel_change_passwd.clicked.connect(
                self._close_change_passwd_window
            )

            if "default" in prog.configs["theme"]:
                self.btn_eye1.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn_eye2.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.btn_eye3.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            if prog.configs["theme"] == "default_dark":
                self.cancel_change_passwd.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.current_password_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #c5d4e7;"
                    + "background: transparent;"
                )

                self.new_password1_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #c5d4e7;"
                    + "background: transparent;"
                )

                self.new_password2_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #c5d4e7;"
                    + "background: transparent;"
                )

                self.checkbox.setStyleSheet(
                    "color: #eff1f3;"
                    + "font-size: 16px;"
                )

                self.continue_change_passwd.setStyleSheet(
                    ':enabled {'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #627eea;}"
                    + ':disabled {'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + 'background: transparent;'
                    + "color: gray;}"
                    + 'QPushButton::hover{background-color: #1e1e1e;}'
                )

            elif prog.configs["theme"] == "default_light":
                self.cancel_change_passwd.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.current_password_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.new_password1_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.new_password2_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

                self.checkbox.setStyleSheet(
                    "color: #3c598e;"
                    + "font-size: 16px;"
                )

                self.continue_change_passwd.setStyleSheet(
                    ":enabled {"
                    + "background-color: transparent;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: #3c598e;"
                    + "padding: 7px;}"
                    + ":disabled {background-color: #adb4bf;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: #3c598e;"
                    + "padding: 7px;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

        def change_lock_timer(self):
            self.list_.hide()

            self.timer_list_options = QListWidget(self)
            self.timer_list_options.resize(530, 286)
            self.timer_list_options.move(40, 80)
            self.timer_list_options.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.timer_list_options.setFocusPolicy(
                Qt.FocusPolicy.NoFocus
            )
            self.timer_list_options.show()

            self.timer_options = [
                "Lock in 1 minute",
                "Lock in 5 minutes",
                "Lock in 15 minutes",
                "Lock in 30 minutes",
                "Lock in 1 hour",
                "Lock in 4 hours",
                "Never lock",
            ]

            for item in enumerate(self.timer_options):
                self.timer_list_options.insertItem(*item)

            for i in range(7):
                self.timer_list_options.item(i).setSizeHint(QSize(520, 54))

            self.prev = 0

            # 1 minute
            if self.master.afk_time == 100000:
                self.timer_list_options.item(0).setText(
                    self.timer_options[0] + "      (current)"
                )

            # 5 minutes
            elif self.master.afk_time == 300000:
                self.timer_list_options.item(1).setText(
                    self.timer_options[1] + "      (current)"
                )
                self.prev = 1

            # 15 minutes
            elif self.master.afk_time == 900000:
                self.timer_list_options.item(2).setText(
                    self.timer_options[2] + "      (current)"
                )
                self.prev = 2

            # 30 minutes
            elif self.master.afk_time == 1800000:
                self.timer_list_options.item(3).setText(
                    self.timer_options[3] + "      (current)"
                )
                self.prev = 3

            # 1 hour
            elif self.master.afk_time == 3600000:
                self.timer_list_options.item(4).setText(
                    self.timer_options[4] + "      (current)"
                )
                self.prev = 4

            # 4 hours
            elif self.master.afk_time == 14400000:
                self.timer_list_options.item(5).setText(
                    self.timer_options[5] + "      (current)"
                )
                self.prev = 5

            # Never lock
            elif self.master.afk_time == None:
                self.timer_list_options.item(6).setText(
                    self.timer_options[6] + "      (current)"
                )
                self.prev = 6

            self.timer_list_options.currentRowChanged.connect(
                self._change_afk_time
            )

            self.close_change_timer = QPushButton(
                text=" Return",
                parent=self,
                icon=TigerWalletImage.receive_blue
            )

            self.close_change_timer.resize(200, 50)
            self.close_change_timer.setIconSize(QSize(32, 32))
            self.close_change_timer.move(190, 386)
            self.close_change_timer.clicked.connect(
                lambda: [
                    self.timer_list_options.hide(),
                    self.list_.show(),
                    self.close_change_timer.close(),
                ]
            )

            if prog.configs["theme"] == "default_dark":
                self.close_change_timer.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.close_change_timer.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

            self.close_change_timer.show()

        def _change_afk_time(self, choice):
            if "current" in self.timer_list_options.item(choice).text():
                errbox("This is the current option")
                return

            opt = self.timer_options[choice]

            if choice == 0:
                self.master.afk_time = 100000
                self.timer_list_options.item(0).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 0

            elif choice == 1:
                self.master.afk_time = 300000
                self.timer_list_options.item(1).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 1

            elif choice == 2:
                self.master.afk_time = 900000
                self.timer_list_options.item(2).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 2

            elif choice == 3:
                self.master.afk_time = 1800000
                self.timer_list_options.item(3).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 3

            elif choice == 4:
                self.master.afk_time = 3600000
                self.timer_list_options.item(4).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 4

            elif choice == 5:
                self.master.afk_time = 14400000
                self.timer_list_options.item(5).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 5

            elif choice == 6:
                self.master.afk_time = None
                self.timer_list_options.item(6).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 6

        def _close_rpc_window(self):
            self.rpc_list_options.close()
            self.cancel_rpc_btn.close()
            self.add_rpc_btn.close()
            self.delete_rpc_btn.close()

            self.list_.clearSelection()
            self.list_.show()

        def _rpc_choice(self, item):
            self.rpc_list_options.clearSelection()

            choice = item.text()
            current_rpc = prog.configs["rpc"]['eth']

            if (
                choice[:choice.find(' ')]
                == current_rpc
            ):
                errbox("This is the current RPC")
                return

            else:
                item.setText(choice + " (current)")

                prog.configs["rpc"]['eth'] = choice

                previous_item = self.rpc_list_options.item(self.prev)
                previous_item = previous_item.text()

                self.rpc_list_options.item(self.prev).setText(
                    previous_item.replace(" (current)", "")
                )
                self.prev = \
                    self.rpc_list_options.indexFromItem(item).row()

                with open(prog.conf_file, "w") as f:
                    json.dump(
                        obj=prog.configs,
                        fp=f,
                        indent=4
                    )

                msgbox(
                    'RPC successfully changed to: '
                    + choice
                )

        def _close_change_passwd_window(self):
            self.current_password.setText(None)
            self.current_password.close()
            self.current_password_lbl.close()
            self.new_password1.setText(None)
            self.new_password1.close()
            self.new_password1_lbl.close()
            self.new_password2.setText(None)
            self.new_password2.close()
            self.new_password2_lbl.close()
            self.btn_eye1.close()
            self.btn_eye2.close()
            self.btn_eye3.close()
            self.cancel_change_passwd.close()
            self.continue_change_passwd.close()
            self.checkbox.close()

            self.list_.show()

        def _change_password(self, new_password):
            self._new_encrypted_file = Account.encrypt(
                prog.account.key,
                password=new_password
            )

            with open(prog.nameofwallet, "w") as f:
                json.dump(self._new_encrypted_file, f)

            msgbox("Your password has been changed sucessfully")
            self._close_change_passwd_window()

    class UpdateHistoryWorker(QThread):
        is_done = pyqtSignal(bool)

        def __init__(self, master):
            super().__init__()

            self.has_changes = False
            self.had_error = False
            self.master = master
            self.address = prog.account.address

        def work(self):
            self.is_done.emit(False)
            self.had_error = False

            dest_path = prog.dest_path

            if prog.chain == 'eth':
                url = f"https://api.ethplorer.io/getAddressHistory/{self.address}"
                key = "?apiKey=freekey&limit=100&showZeroValues=false"

                data = s.get(url + key)
                data = orjson.loads(data.text)

                if data["operations"] != self.master.data:
                    self.has_changes = True

            elif prog.chain == 'base':
                url = (
                    f"https://base.blockscout.com/api/v2/addresses/{self.address}/token-transfers?"
                    'type=ERC-20%2CERC-721%2CERC-1155&filter=to%20%7C%20from'
                )

                data = s.get(url, stream=True)
                data = orjson.loads(data.text)

                if data != self.master.data:
                    self.has_changes = True

            self.is_done.emit(True)

    # Added history for Base in v3.0
    # Fixed a bug where load table was not set correctly
    class WalletHistory(QWidget):
        def __init__(
            self, 
            master,
            chain='eth', 
        ):
            super().__init__()
            
            self.master = master
            self.chain = chain
            self.max_ = 25
            self.transfers = 0
            self.address = prog.account.address
            self.total_tx = 0
            self.data = {}

            self.load_file()

            self.init_window()
            self.init_table()
            self.init_tip()
            self.init_refresh_button()
            self.init_no_tx_msg()

            self.unload_history_data()
            self.init_limit_selector()

            if "default" in prog.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet("background: #0a0f18;")

                self.refresh.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.history_title.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #627eea;"
                    + "background: #0a0f18;"
                )

                self.tip_label.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #c5d4e7;"
                    + "background: transparent;"
                )

                fix_white_borders([self.selector])
                
                self.ret_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )
                
                self.quit_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3;")

                self.refresh.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.history_title.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #3c598e;"
                    + "background: #eff1f3;"
                )

                self.tip_label.setStyleSheet(
                    "font-size: 18px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                fix_white_borders([self.selector], theme='light')
                
                self.ret_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )
                
                self.quit_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )
        
        def init_window(self) -> None:
            self.setFixedWidth(1300)
            self.setFixedHeight(720)
            self.setWindowTitle("TigerWallet  -  Transaction history")
            
            add_round_corners(self, 8)
            align_to_center(self)
            
            self.border = QLabel(self)
            self.border.resize(1280, 644)
            self.border.move(10, 66)

            self.history_title = QLabel("Transaction history", self)
            self.history_title.resize(320, 39)
            self.history_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_title.move(474, 44)
            
            self.ret_btn = QPushButton(
                text=' Return to wallet',
                parent=self,
                icon=TigerWalletImage.receive_blue
            )
            self.ret_btn.setIconSize(QSize(24, 24))
            
            self.ret_btn.resize(176, 40)
            self.ret_btn.move(30, 14)
            self.ret_btn.clicked.connect(self.master.clear_tab7)
            
            self.quit_btn = QPushButton(
                text=' Quit',
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.quit_btn.setIconSize(QSize(24, 24))
            
            self.quit_btn.resize(140, 40)
            self.quit_btn.move(1130, 14)
            self.quit_btn.clicked.connect(app.closeAllWindows)

        def init_table(self) -> None:
            self.history_table = QTableWidget(self)
            self.history_table.show()
            self.history_table.setColumnCount(6)
            self.history_table.setRowCount(self.max_)
            self.history_table.resize(1238, 520)
            self.history_table.move(30, 156)

            self.header_items = [
                QTableWidgetItem("Time (Y/M/D)"),
                QTableWidgetItem("Symbol"),
                QTableWidgetItem("From"),
                QTableWidgetItem("To"),
                QTableWidgetItem("Hash"),
                QTableWidgetItem("Amount"),
            ]

            self.header_sizes = [150, 125, 240, 250, 260, 190]

            for item in enumerate(self.header_items):
                self.history_table.setHorizontalHeaderItem(*item)

            for item in enumerate(self.header_sizes):
                self.history_table.setColumnWidth(*item)

            self.history_table.verticalHeader().setVisible(False)
            self.history_table.horizontalHeader().setVisible(True)
            self.history_table.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )

            self.history_table.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )

            self.history_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.history_table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            self.history_table.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.Fixed
            )

            self.history_table.cellPressed.connect(self.copy_clicked_item)

        def init_limit_selector(self) -> None:
            self.selector = QComboBox(self)
            self.selector.resize(80, 44)
            self.selector.move(80, 98)
            self.options = ["10", "25", "50", "75", "100"]

            for item in enumerate(self.options):
                self.selector.insertItem(*item)

            self.selector.setCurrentIndex(1)
            self.selector.activated.connect(self.adjust_table)

        def init_no_tx_msg(self) -> None:
            self.notx = QLabel(self)

            if self.total_tx == -1:
                self.notx.setText(
                    "Failed to fetch wallet history. Try again later"
                )
                return
            else:
                self.notx.setText("No transactions found")

            self.notx.resize(1310, 220)
            self.notx.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notx.move(0, 200)
            self.notx.hide()

            self.pix_holder = QLabel(self)
            self.pix_holder.resize(64, 64)
            self.pix_holder.move(340, 280)
            self.pix_holder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pix = QPixmap()
            self.pix.load(
                prog.imgfolder
                + 'feelsbadman.png'
            )

            self.pix = self.pix.scaled(
                QSize(64, 64),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            self.pix_holder.setPixmap(self.pix)
            self.pix_holder.hide()

            if prog.configs["theme"] == "default_dark":
                self.notx.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #627eea;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.notx.setStyleSheet(
                    "font-size: 40px;"
                    + "color: black;"
                    + "background: transparent;"
                )

            self.pix_holder.setStyleSheet("background: transparent;")

        def init_tip(self) -> None:
            text = (
                'Tip: you can click on any row in column 3'
                + ' 4, and 5 to copy the value'
            )

            self.tip_label = QLabel(
                text=text,
                parent=self,
            )

            self.tip_label.resize(700, 66)
            self.tip_label.move(300, 84)
            self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_refresh_button(self) -> None:
            self.refresh = QPushButton(
                text=" Refresh",
                parent=self,
                icon=TigerWalletImage.refresh_blue
            )

            self.refresh.setIconSize(QSize(32, 32))
            self.refresh.resize(140, 40)
            self.refresh.move(1000, 92)

            def kill_thread(is_done):
                if is_done:
                    self.uhw.quit()
                    self.ubt.quit()

                    if self.uhw.has_changes and not self.notx.isHidden():
                        self.notx.close()
                        self.pix_holder.close()

                        # Clear table contents
                        [
                            self.history_table.takeItem(i, ii)
                            for i in range(self.total_tx)
                            for ii in range(6)
                        ]

                        self.history_table.setRowCount(self.max_)
                        self.load_file()
                        self.unload_history_data()

                    if self.uhw.had_error:
                        pass
                    else:
                        msgbox("No new transactions were found")

                    self.refresh.setEnabled(True)
                    self.refresh.setText(" Refresh")
                    self.refresh.resize(140, 40)
                    self.refresh.move(1000, 92)


            self.uhw = UpdateHistoryWorker(self)
            self.ubt = QThread()

            self.uhw.moveToThread(self.ubt)
            self.ubt.started.connect(self.uhw.work)
            self.uhw.is_done.connect(kill_thread)

            self.refresh.clicked.connect(
                lambda: [
                    self.refresh.setText("Looking for transactions..."),
                    self.refresh.resize(270, 40),
                    self.refresh.move(950, 92),
                    self.refresh.setEnabled(False),
                    self.ubt.start(),
                ]
            )

        def load_file(self) -> None:
            if self.chain == 'eth':
                with open(
                    prog.dest_path
                    + "history_eth.json", "rb"
                ) as f:
                    self.data = orjson.loads(f.read())

                    if "error" in self.data:
                        self.data = {"operations": []}

                        self.total_tx = -1
                        return

                    self.data = self.data["operations"]
                    self.total_tx = len(self.data)

            elif self.chain == 'base':
                with open(
                    prog.dest_path
                    + "history_base.json", "rb"
                ) as f:
                    self.data = orjson.loads(f.read())

                    if "error" in self.data:
                        self.data = {}

                        self.total_tx = -1
                        return

                    self.total_tx = len(self.data['items'])

        # Timestamps
        def load_block_timestamps(self) -> list:
            times = []

            if self.chain == 'eth':
                from datetime import datetime

                times_ = [
                    self.data[n]["timestamp"]
                    for n in range(self.total_tx)
                ]

                times = [
                    datetime.fromtimestamp(times[n])
                    for n in range(self.total_tx)
                ]

            elif self.chain == 'base':
                if self.total_tx != 0:
                    times = [
                        self.data['items'][n]['timestamp'][:10]
                        for n in range(self.total_tx)
                    ]

            return times

        # Symbols
        def load_symbols(self) -> list:
            if self.chain == 'eth':
                return [
                    self.data[n]["tokenInfo"]["symbol"]
                    for n in range(self.total_tx)
                ]

            elif self.chain == 'base':
                return [
                    self.data['items'][i]['token']['symbol']
                    for i in range(self.total_tx)
                ]

        # From addresses
        def load_from_addresses(self) -> list:
            if self.chain == 'eth':
                return [
                    self.data[n]["from"]
                    for n in range(self.total_tx)
                ]


            elif self.chain == 'base':
                return [
                    self.data['items'][n]["from"]['hash']
                    for n in range(self.total_tx)
                ]

        # To addresses
        def load_to_addresses(self) -> list:
            if self.chain == 'eth':
                return [
                    self.data[n]["to"]
                    for n in range(self.total_tx)
                ]


            elif self.chain == 'base':
                return [
                    self.data['items'][n]["to"]['hash']
                    for n in range(self.total_tx)
                ]

        # Hashes
        def load_hashes(self) -> list:
            if self.chain == 'eth':
                return [
                    self.data[n]["transactionHash"]
                    for n in range(self.total_tx)
                ]


            elif self.chain == 'base':
                return [
                    self.data['items'][n]["transaction_hash"]
                    for n in range(self.total_tx)
                ]

        # Amount
        def load_amount(self) -> list:
            if self.chain == 'eth':
                return [
                    self.data[n]["value"]
                    for n in range(self.total_tx)
                ]

            elif self.chain == 'base':
                amount_in_wei = [
                    self.data['items'][n]["total"]['value']
                    for n in range(self.total_tx)
                ]

                decimals = [
                    self.data['items'][n]["total"]['decimals']
                    for n in range(self.total_tx)
                ]

                amount = [
                    int(item) / (10**int(dec))
                    for item, dec in zip(amount_in_wei, decimals)
                ]

                return amount

        def unload_history_data(self) -> None:
            """
            Summon a pool of minions that willl
            perform list comprehension.

            The table gets filled up pretty much instantly.
            """
            if self.total_tx == 0:
                self.history_table.setRowCount(0)
                self.notx.show()
                self.pix_holder.show()
                return

            elif self.total_tx < self.max_:
                self.history_table.setRowCount(self.total_tx)

            with ThreadPoolExecutor(max_workers=15) as pool:
                self.times = pool.submit(self.load_block_timestamps).result()
                self.symbols = pool.submit(self.load_symbols).result()
                self.faddr = pool.submit(self.load_from_addresses).result()
                self.taddr = pool.submit(self.load_to_addresses).result()
                self.hashes = pool.submit(self.load_hashes).result()
                self.amount = pool.submit(self.load_amount).result()

                # Timestamps
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 0, QTableWidgetItem(str(self.times[item]))
                        )
                        for item in range(self.total_tx)
                    ]
                )

                # Symbols
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 1, QTableWidgetItem(self.symbols[item])
                        )
                        for item in range(self.total_tx)
                    ]
                )

                # From addresses
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 2, QTableWidgetItem(self.faddr[item])
                        )
                        for item in range(self.total_tx)
                    ]
                )

                # To addresses
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 3, QTableWidgetItem(self.taddr[item])
                        )
                        for item in range(self.total_tx)
                    ]
                )

                # Hashes
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 4, QTableWidgetItem(self.hashes[item])
                        )
                        for item in range(self.total_tx)
                    ]
                )

                # Amount
                pool.submit(
                    [
                        self.history_table.setItem(
                            item,
                            5,
                            QTableWidgetItem(
                                rm_e_notation(
                                    float(self.amount[item])
                                )[:14]
                            ),
                        )
                        for item in range(self.total_tx)
                    ]
                )

        def copy_clicked_item(self):
            if self.total_tx == 0:
                return

            self.model = self.history_table.model()

            self.column = self.history_table.currentColumn()
            self.row = self.history_table.currentRow()

            if self.column not in range(2, 5):
                pass

            else:
                self.item = self.history_table.itemFromIndex(
                    self.model.index(self.row, self.column)
                )

                self.clicked_item = self.item.text()

                QApplication.clipboard().setText(self.clicked_item)
                msgbox(f"{self.clicked_item} copied to clipboard")

        def adjust_table(self, i) -> None:
            self.selection = int(self.options[i])

            if self.selection > self.total_tx:
                return

            # Clear table contents
            [
                self.history_table.takeItem(i, ii)
                for i in range(self.total_tx)
                for ii in range(6)
            ]

            self.max_ = self.selection
            self.history_table.setRowCount(self.max_)

            # Fill table contents
            self.unload_history_data()

    class UniSwap:
        uniswap_abi = orjson.loads(
            """[{"inputs":[{"components":[{"internalType":"address","name":"permit2","type":"address"},{"internalType":"address","name":"weth9","type":"address"},{"internalType":"address","name":"seaport","type":"address"},{"internalType":"address","name":"nftxZap","type":"address"},{"internalType":"address","name":"x2y2","type":"address"},{"internalType":"address","name":"foundation","type":"address"},{"internalType":"address","name":"sudoswap","type":"address"},{"internalType":"address","name":"nft20Zap","type":"address"},{"internalType":"address","name":"cryptopunks","type":"address"},{"internalType":"address","name":"looksRare","type":"address"},{"internalType":"address","name":"routerRewardsDistributor","type":"address"},{"internalType":"address","name":"looksRareRewardsDistributor","type":"address"},{"internalType":"address","name":"looksRareToken","type":"address"},{"internalType":"address","name":"v2Factory","type":"address"},{"internalType":"address","name":"v3Factory","type":"address"},{"internalType":"bytes32","name":"pairInitCodeHash","type":"bytes32"},{"internalType":"bytes32","name":"poolInitCodeHash","type":"bytes32"}],"internalType":"struct RouterParameters","name":"params","type":"tuple"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"ContractLocked","type":"error"},{"inputs":[],"name":"ETHNotAccepted","type":"error"},{"inputs":[{"internalType":"uint256","name":"commandIndex","type":"uint256"},{"internalType":"bytes","name":"message","type":"bytes"}],"name":"ExecutionFailed","type":"error"},{"inputs":[],"name":"FromAddressIsNotOwner","type":"error"},{"inputs":[],"name":"InsufficientETH","type":"error"},{"inputs":[],"name":"InsufficientToken","type":"error"},{"inputs":[],"name":"InvalidBips","type":"error"},{"inputs":[{"internalType":"uint256","name":"commandType","type":"uint256"}],"name":"InvalidCommandType","type":"error"},{"inputs":[],"name":"InvalidOwnerERC1155","type":"error"},{"inputs":[],"name":"InvalidOwnerERC721","type":"error"},{"inputs":[],"name":"InvalidPath","type":"error"},{"inputs":[],"name":"InvalidReserves","type":"error"},{"inputs":[],"name":"LengthMismatch","type":"error"},{"inputs":[],"name":"NoSlice","type":"error"},{"inputs":[],"name":"SliceOutOfBounds","type":"error"},{"inputs":[],"name":"SliceOverflow","type":"error"},{"inputs":[],"name":"ToAddressOutOfBounds","type":"error"},{"inputs":[],"name":"ToAddressOverflow","type":"error"},{"inputs":[],"name":"ToUint24OutOfBounds","type":"error"},{"inputs":[],"name":"ToUint24Overflow","type":"error"},{"inputs":[],"name":"TransactionDeadlinePassed","type":"error"},{"inputs":[],"name":"UnableToClaim","type":"error"},{"inputs":[],"name":"UnsafeCast","type":"error"},{"inputs":[],"name":"V2InvalidPath","type":"error"},{"inputs":[],"name":"V2TooLittleReceived","type":"error"},{"inputs":[],"name":"V2TooMuchRequested","type":"error"},{"inputs":[],"name":"V3InvalidAmountOut","type":"error"},{"inputs":[],"name":"V3InvalidCaller","type":"error"},{"inputs":[],"name":"V3InvalidSwap","type":"error"},{"inputs":[],"name":"V3TooLittleReceived","type":"error"},{"inputs":[],"name":"V3TooMuchRequested","type":"error"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"RewardsSent","type":"event"},{"inputs":[{"internalType":"bytes","name":"looksRareClaim","type":"bytes"}],"name":"collectRewards","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"commands","type":"bytes"},{"internalType":"bytes[]","name":"inputs","type":"bytes[]"}],"name":"execute","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes","name":"commands","type":"bytes"},{"internalType":"bytes[]","name":"inputs","type":"bytes[]"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"execute","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"onERC1155BatchReceived","outputs":[{"internalType":"bytes4","name":"","type":"bytes4"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"onERC1155Received","outputs":[{"internalType":"bytes4","name":"","type":"bytes4"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"onERC721Received","outputs":[{"internalType":"bytes4","name":"","type":"bytes4"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"int256","name":"amount0Delta","type":"int256"},{"internalType":"int256","name":"amount1Delta","type":"int256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"uniswapV3SwapCallback","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]
            """
        )

        permit2_abi = orjson.loads(
            '''[{"inputs":[{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"AllowanceExpired","type":"error"},{"inputs":[],"name":"ExcessiveInvalidation","type":"error"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"InsufficientAllowance","type":"error"},{"inputs":[{"internalType":"uint256","name":"maxAmount","type":"uint256"}],"name":"InvalidAmount","type":"error"},{"inputs":[],"name":"InvalidContractSignature","type":"error"},{"inputs":[],"name":"InvalidNonce","type":"error"},{"inputs":[],"name":"InvalidSignature","type":"error"},{"inputs":[],"name":"InvalidSignatureLength","type":"error"},{"inputs":[],"name":"InvalidSigner","type":"error"},{"inputs":[],"name":"LengthMismatch","type":"error"},{"inputs":[{"internalType":"uint256","name":"signatureDeadline","type":"uint256"}],"name":"SignatureExpired","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint160","name":"amount","type":"uint160"},{"indexed":false,"internalType":"uint48","name":"expiration","type":"uint48"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"address","name":"spender","type":"address"}],"name":"Lockdown","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint48","name":"newNonce","type":"uint48"},{"indexed":false,"internalType":"uint48","name":"oldNonce","type":"uint48"}],"name":"NonceInvalidation","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint160","name":"amount","type":"uint160"},{"indexed":false,"internalType":"uint48","name":"expiration","type":"uint48"},{"indexed":false,"internalType":"uint48","name":"nonce","type":"uint48"}],"name":"Permit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"word","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"mask","type":"uint256"}],"name":"UnorderedNonceInvalidation","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint160","name":"amount","type":"uint160"},{"internalType":"uint48","name":"expiration","type":"uint48"},{"internalType":"uint48","name":"nonce","type":"uint48"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint160","name":"amount","type":"uint160"},{"internalType":"uint48","name":"expiration","type":"uint48"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint48","name":"newNonce","type":"uint48"}],"name":"invalidateNonces","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"wordPos","type":"uint256"},{"internalType":"uint256","name":"mask","type":"uint256"}],"name":"invalidateUnorderedNonces","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"internalType":"struct IAllowanceTransfer.TokenSpenderPair[]","name":"approvals","type":"tuple[]"}],"name":"lockdown","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"nonceBitmap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"components":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint160","name":"amount","type":"uint160"},{"internalType":"uint48","name":"expiration","type":"uint48"},{"internalType":"uint48","name":"nonce","type":"uint48"}],"internalType":"struct IAllowanceTransfer.PermitDetails[]","name":"details","type":"tuple[]"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"sigDeadline","type":"uint256"}],"internalType":"struct IAllowanceTransfer.PermitBatch","name":"permitBatch","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"components":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint160","name":"amount","type":"uint160"},{"internalType":"uint48","name":"expiration","type":"uint48"},{"internalType":"uint48","name":"nonce","type":"uint48"}],"internalType":"struct IAllowanceTransfer.PermitDetails","name":"details","type":"tuple"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"sigDeadline","type":"uint256"}],"internalType":"struct IAllowanceTransfer.PermitSingle","name":"permitSingle","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct ISignatureTransfer.TokenPermissions","name":"permitted","type":"tuple"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct ISignatureTransfer.PermitTransferFrom","name":"permit","type":"tuple"},{"components":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"requestedAmount","type":"uint256"}],"internalType":"struct ISignatureTransfer.SignatureTransferDetails","name":"transferDetails","type":"tuple"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"permitTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct ISignatureTransfer.TokenPermissions[]","name":"permitted","type":"tuple[]"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct ISignatureTransfer.PermitBatchTransferFrom","name":"permit","type":"tuple"},{"components":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"requestedAmount","type":"uint256"}],"internalType":"struct ISignatureTransfer.SignatureTransferDetails[]","name":"transferDetails","type":"tuple[]"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"permitTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct ISignatureTransfer.TokenPermissions","name":"permitted","type":"tuple"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct ISignatureTransfer.PermitTransferFrom","name":"permit","type":"tuple"},{"components":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"requestedAmount","type":"uint256"}],"internalType":"struct ISignatureTransfer.SignatureTransferDetails","name":"transferDetails","type":"tuple"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bytes32","name":"witness","type":"bytes32"},{"internalType":"string","name":"witnessTypeString","type":"string"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"permitWitnessTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct ISignatureTransfer.TokenPermissions[]","name":"permitted","type":"tuple[]"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct ISignatureTransfer.PermitBatchTransferFrom","name":"permit","type":"tuple"},{"components":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"requestedAmount","type":"uint256"}],"internalType":"struct ISignatureTransfer.SignatureTransferDetails[]","name":"transferDetails","type":"tuple[]"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bytes32","name":"witness","type":"bytes32"},{"internalType":"string","name":"witnessTypeString","type":"string"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"permitWitnessTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint160","name":"amount","type":"uint160"},{"internalType":"address","name":"token","type":"address"}],"internalType":"struct IAllowanceTransfer.AllowanceTransferDetails[]","name":"transferDetails","type":"tuple[]"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint160","name":"amount","type":"uint160"},{"internalType":"address","name":"token","type":"address"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"}]
            '''
        )

        router_addresses = {
            "ethereum": "0x66a9893cc07d91d95644aedd05d03f95e1dba8af",
            "base": "0x6ff5693b99212da76ad316178a184ab56d299b43",
        }

        def __init__(
            self,
        ):
            self.chain_id = 1 if prog.chain == 'eth' else 8453
            self.chain = 'ethereum' if self.chain_id == 1 else 'base'
            self.w3 =  Web3(
                    Web3.HTTPProvider(
                        prog.configs["rpc"]['eth']
                    )
                )

            self.router_address = self.w3.to_checksum_address(
               '0x66a9893cc07d91d95644aedd05d03f95e1dba8af'
            )

            self.router = self.w3.eth.contract(
                address=self.router_address,
                abi=self.uniswap_abi,
            )

            self.zero_in_hex = '0x0000000000000000000000000000000000000000'

            self.permit2 = self.w3.eth.contract(
                address=w3.to_checksum_address(
                    "0x000000000022D473030F116dDEE9F6B43aC78BA3"
                ),
                abi=self.permit2_abi,
            )

        def approve_permit2(self, token_address, amount) -> int:
            token_contract = self.w3.eth.contract(
                token_address,
                abi=prog.abi
            )

            approve_contract =  token_contract.functions.approve(
                self.permit2.address,
                2**256 - 1
            )

            # Does not cost anything, but whines if gas is omitted
            tx = approve_contract.build_transaction({
                "from": prog.account.address,
                "gas": 500_000,
                "maxFeePerGas": self.w3.eth.gas_price,
                "type": 2,
                "nonce": self.w3.eth.get_transaction_count(
                    prog.account.address
                ),
                'chainId': self.chain_id
            })

            signed_tx = self.w3.eth.account.sign_transaction(
                tx,
                prog.account.key
            )

            try:
                tx_hash = self.w3.eth.send_raw_transaction(
                    signed_tx.raw_transaction
                )
            except Exception:
                errbox('Not enough ETH to pay for permit2 allowance')
                return 0

            return 1

        def create_permit_signature(self, token_address)-> tuple:
            token_address = self.w3.to_checksum_address(token_address)

            permit2_contract = self.w3.eth.contract(
                address=self.permit2.address,
                abi=self.permit2_abi
            )

            p2_amount, p2_expiration, p2_nonce = (
                permit2_contract.functions.allowance(
                    prog.account.address,
                    token_address,
                    self.router_address
                )
                .call()
            )

            codec = RouterCodec()
            allowance_amount = 2**160 - 1

            permit_data, signable_message = (
                codec.create_permit2_signable_message(
                    token_address,
                    allowance_amount,
                    codec.get_default_expiration(),
                    p2_nonce,
                    self.router_address,
                    codec.get_default_deadline(),
                    self.chain_id
                )
            )

            signed = prog.account.sign_message(signable_message)

            return permit_data, signed

        def has_permit2_allowance(self, token_address) -> bool:
            """
            Check if token has already been approved for Permit2
            True if sufficient allowance exists, False otherwise
            """

            in_address_is_eth = token_address == self.zero_in_hex

            if in_address_is_eth:
                return True

            token_contract = self.w3.eth.contract(
                address=w3.to_checksum_address(token_address),
                abi=prog.abi
            )

            # Check allowance for Permit2 contract
            permit2_allowance = (
                token_contract.functions.allowance(
                    prog.account.address,
                    self.permit2.address
                )
                .call()
            )

            if (
                isinstance(permit2_allowance, tuple)
                and prog.chain == 'base'
            ):
                bwp = Web3.HTTPProvider(
                    endpoint_uri='https://base.drpc.org',
                    exception_retry_configuration=None,
                    request_kwargs={
                        "timeout": (5, 10),
                        "allow_redirects": False
                    },
                    session=s,
                )

                bw3 = Web3(bwp)

                token_contract = bw3.eth.contract(
                    address=w3.to_checksum_address(token_address),
                    abi=prog.abi
                )

                permit2_allowance = (
                    token_contract.functions.allowance(
                        prog.account.address,
                        self.permit2.address
                    )
                    .call()
                )

            approval_threshold = 2**200

            return permit2_allowance > approval_threshold

        def swap(
            self,
            from_token,
            to_token,
            amount,
            min_amount_out, # amount - slippage (5%)
            fee=3000, # 0.3% fee
        ) -> hex:
            # Determine if input is native token (ETH/MATIC)
            in_address_is_eth = from_token == self.zero_in_hex

            if not in_address_is_eth:
                approved = self.approve_permit2(from_token, amount)

                if not approved:
                    return

            permit_data, signed_message = \
                self.create_permit_signature(from_token)

            amount_in_wei = amount
            codec = RouterCodec()

            tick_spacing = 60

            pool_key = codec.encode.v4_pool_key(
                from_token,
                to_token,
                fee,
                tick_spacing,
            )

            self.nonce = self.w3.eth.get_transaction_count(
                prog.account.address
            )

            encoded_data = (
                codec
                .encode
                .chain()
                .v4_swap()
                .swap_exact_in_single(
                    pool_key=pool_key,
                    zero_for_one=True,
                    amount_in=amount_in_wei,
                    amount_out_min=min_amount_out,
                )
                .take_all(to_token, 0)
                .settle_all(from_token, amount_in_wei)
                .build_v4_swap()
                .build(deadline=codec.get_default_deadline())
            )

            tx_params = {
                "from": prog.account.address,
                "value": amount_in_wei,
                "to": self.router_address,
                "chainId": self.chain_id,
                "nonce": self.nonce,
                "type": 2,
                "gas": 500_000,
                "maxFeePerGas": self.w3.eth.gas_price,
                "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
                "data": encoded_data,
            }

            signed_tx = \
                self.w3.eth.account.sign_transaction(
                    tx_params,
                    prog.account.key
                )

            tx_hash = 0x0

            try:
                tx_hash = self.w3.eth.send_raw_transaction(
                    signed_tx.raw_transaction
                )
            except Exception:
                errbox('Not enough ETH to pay for swap gas fees')
                return

            return tx_hash.hex()

    # Actual user wallet
    # Added ENS support in v2.0
    # Base support in v3.0
    # Fixed BUG where total balance wasn't updating when switching networks in v3.1
    # Fixed BUG where itoken mages didn't get deleted in v3.1
    # Visual update in v3.1
    class UserWallet(QWidget):
        def __init__(self):
            super().__init__()
            
            self.init_threads()
            self.setMouseTracking(True)
            self.setup_main()
            
            self.init_afk_timer()
            self.init_table()

            # New in v3.1. Hides main window to display widgets
            self.stacked_layout = QStackedLayout()
            self.stacked_layout.addWidget(self)
            
            self.init_coin_row()
            self.init_side_bar()
            self.init_wallet_btn_options()
            self.init_sidebar_style()
            self.init_unlock_wallet()

            self.init_change_wallet_window()
            self.init_send_window()
            self.init_receive_window()
            self.init_swap_window()
            self.init_robot_window()
            self.init_addressbook_window()
            self.init_history_window()
            self.init_settings_window()

            self.stacked_layout.addWidget(self.wh)
            self.stacked_layout.addWidget(self.s)
            self.stacked_layout.addWidget(self.launch_new_wallet_window)
            self.stacked_layout.addWidget(self.exp_user)

            if prog.configs['currency'] == 'USD':
                self.init_total_balance(0)
            else:
                self.init_total_balance(1)

            self.start_afk_timer()
            self.fill_up_table()

            if "default" in prog.configs["theme"]:
                self.box1.setStyleSheet("background: transparent;")
                self.box2.setStyleSheet("background: transparent;")
                self.box3.setStyleSheet("background: transparent;")
                self.box4.setStyleSheet("background: transparent;")
                self.box5.setStyleSheet("background: transparent;")
                self.box6.setStyleSheet("background: transparent;")

                self.unlock_wallet_box.setStyleSheet(
                    "background: #0a0f18;"
                    "border: 1px solid #1e2b45;;"
                    "border-radius: 16px;"
                )

                self.unlock_wallet_lbl.setStyleSheet(
                    "border: 0px solid #1e1e1e;"
                    "font: 19px;"
                    "color: #eff1f3;"
                )

                self.showhidepass.setStyleSheet(
                    'QPushButton {border: none;}'
                    "QPushButton::hover {background-color: #1e1e1e;}"
                )

                self.arrow_img.setStyleSheet(
                    'background: transparent;'
                    'border-radius: 0px;'
                )

            if prog.configs["theme"] == "default_dark":
                self.apply_default_dark_theme()
                self.setStyleSheet('background: #0a0f18;')
                
                self.border.setStyleSheet(
                    "border: 1px solid #1e2b45;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.apply_default_light_theme()
                self.setStyleSheet('background: #eff1f3;')
                
                self.border.setStyleSheet(
                    "border: 1px solid #bbc8e2;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

        def _update_currency_setting(self):
            self.update_balance_thread.quit()
            self.update_balance_thread.wait()

            with open(prog.conf_file, 'w') as f:
                json.dump(
                    obj=prog.configs,
                    fp=f,
                    indent=4
                )

            self.update_balance_thread.start()
            self.update_balance_worker.start()

        # new in v3.0
        def _close_tab(self, tab):
            ''' pythonic way to close tabs '''
            tabs = {
                1: self.clear_tab1,
                2: self.clear_tab2,
                3: self.clear_tab3,
                4: self.clear_tab4,
                5: self.clear_tab5,
                6: self.clear_tab6
            }

            if tab != 0:
                return tabs[tab]()

            else:
                if self.donation_window_active:
                    self.clear_donation_tab()

                elif self.rm_wallet_tab:
                    self.clear_rm_wallet_tab()

                elif self.rmcointab:
                    self.clear_rm_coin_tab()

                elif self.add_contact_section2:
                    self.clear_add_contact_details()

        def _kill_threads(self):
            # End threads
            self.thread.quit()
            self.thread2.quit()

            self.update_balance_thread.quit()
            self.update_balance_thread.wait()

            self.update_eth_gas.stop()
            self.update_base_gas.stop()

            self.update_price_thread.quit()
            self.update_price_thread.wait()

            # End workers
            self.worker.quit()
            self.worker2.quit()

            self.update_balance_worker.quit()
            self.update_balance_worker.wait()

            self.update_price_worker.quit()
            self.update_price_worker.wait()

            #  Stop timer
            self.tm.stop()

        def _start_threads(self):
            self.thread.start()
            self.worker.start()

            self.update_balance_thread.start()
            self.update_balance_worker.start()

            self.update_price_thread.start()
            self.update_price_worker.start()

            self.tm.start(15000)
            

        def closeEvent(self, event):
            '''
            if (
                not prog.switched_wallets
                and not prog.new_wallet
                and not prog.used_import_wallet_from_userwallet
                and not self.called_restore_default_coins
            ):
                self._kill_threads()
                return
            '''

            #app.closeAllWindows()

            with open(prog.contactsjson, "w") as f:
                json.dump(
                    obj=prog.contactbook,
                    fp=f,
                    indent=4
                )

            self_destruct()
            event.accept()

        def mouseMoveEvent(self, event):
            def verify_if_afk():
                if event.type() != Qt.MouseButton.NoButton:
                    self.black_out_window()
                    self.unlock_wallet_box.show()
                    self.setEnabled(False)

            self.afk_timer.timeout.connect(verify_if_afk)

        def setup_main(self):
            self.setFixedSize(1100, 740)
            self.setWindowTitle(f"TigerWallet  -  {prog.nameofwallet}")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(0, 0)
            self.border.resize(1080, 616)
            self.border.move(10, 116)

            self.val = QLineEdit(self)
            self.val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.val.setEchoMode(QLineEdit.EchoMode.Normal)
            self.val.setReadOnly(True)
            self.val.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.val.resize(1120, 40)
            self.val.move(0, 132)
            self.preserved_val = ''

            self.address = prog.account.address
            self.eth_price = prog.eth_price
            self.eth_amount = prog.eth_amount

            # New in v3.0
            self.currency_box = QComboBox(self)
            self.clist = QtWidgets.QListView(self.currency_box)
            self.clist.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.currency_box.insertItem(0, 'USD')
            self.currency_box.insertItem(1, 'ETH')
            self.currency_box.setView(self.clist)
            self.currency_box.setAttribute(
                Qt.WidgetAttribute.WA_MacShowFocusRect,
                False
            )
            self.currency_box.resize(140, 34)
            self.currency_box.move(890, 136)
            self.currency_box.currentIndexChanged.connect(
                self.init_total_balance
            )

            if prog.configs['currency'] == 'USD':
                self.currency_box.setCurrentIndex(0)

            else:
                self.currency_box.setCurrentIndex(1)

            self.tab = 0
            self.rm_wallet_tab = False
            self.browser_active = False
            self.tab2_hidden = False
            self.settings_tab_active = False
            self.add_contact_section2 = False
            self.add_contact_section3 = False
            self.addcointab = False
            self.rmcointab = False
            self.donation_window_active = False
            self.called_restore_default_coins = False
            self.afk_time = 900000
            self.opt = 1

            self.btn_showhide = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye_blue
            )

            self.btn_showhide.setIconSize(QSize(24, 24))
            self.btn_showhide.move(760, 142)
            self.btn_showhide.clicked.connect(self.unhide)

            self.exp_user = UserWithExperience(self)
            self.launch_new_wallet_window = WalletNameAndPassword(self)


        def init_total_balance(self, index):
            total = 0.0

            if index == 0:
                total_list = [
                    float(val)
                    * float(price) if price != 'N/A' else 0.0
                    for val, price in zip(
                        prog.asset_details[prog.chain]['value'],
                        prog.asset_details[prog.chain]['price']
                    )
                ]

                for item in total_list:
                    total += item

                if prog.chain == 'eth':
                    total += (
                        float(prog.eth_amount)
                        * float(self.eth_price)
                    )
                else:
                    total += (
                        float(prog.base_eth_amount)
                        * float(self.eth_price)
                    )
                total = round(total, 14)
                total = rm_e_notation(total)

                self.val.setText(f"Balance: ${total}")
                self.preserved_val = self.val.text()

                prog.total_balance = total

            else:
                total_list = [
                    float(val)
                    / float(self.eth_price)
                    if float(val) > 0  else 0
                    for val in prog.asset_details[prog.chain]['value']
                ]

                for item in total_list:
                    # convert to a positive decimal/integer
                    if item < 0:
                        item -= (item * 2)

                    total += item

                total += float(prog.eth_amount)
                total = round(total, 14)
                total = rm_e_notation(total)

                self.val.setText(f"Balance: {total} ETH")
                self.preserved_val = self.val.text()

                prog.total_balance = total

        def init_afk_timer(self):
            self.afk_timer = QTimer()

        def _update_asset_balances(self):
            for index in range(len(prog.asset[prog.chain]['name'])):
                val = prog.asset_details[prog.chain]['value'][index]
                val = rm_e_notation(val)

                if self.opt == 1:
                    self.table.setItem(index+1, 1, QTableWidgetItem(val[:18]))

                else:
                    self.table.setItem(index+1, 1, QTableWidgetItem('*' * 26))

        # Removed gas threads in v3.1
        def init_threads(self):
            # Monitor for incoming Base tokens
            self.thread = QThread()
            self.worker = SubToEthChain()
            self.worker.moveToThread(self.thread)

            def add_eth_coin_if_new_one_arrived(cond):
                if cond:
                    self.add_coin(
                        'eth',
                        self.worker.token['name'],
                        self.worker.token['address'],
                        self.worker.token['symbol'],
                        invoked_from_worker=True
                    )

            self.worker.received_new_tokens.connect(
                add_eth_coin_if_new_one_arrived
            )
            self.thread.started.connect(self.worker.work)

            # Monitor for incoming Base tokens
            def add_base_coin_if_new_one_arrived(cond):
                if cond:
                    self.add_coin(
                        'base',
                        self.worker.token['name'],
                        self.worker.token['address'],
                        self.worker.token['symbol'],
                        invoked_from_worker=True
                    )

            self.thread2 = QThread()
            self.worker2 = SubToBaseChain()
            self.worker2.moveToThread(self.thread2)
            self.worker2.received_new_tokens.connect(
                add_base_coin_if_new_one_arrived
            )
            self.thread2.started.connect(self.worker2.work)

            self.asset_timer = QTimer()
            self.asset_timer.timeout.connect(self._update_asset_balances)
            self.asset_timer.start(1000)

            self.update_balance_thread = QThread()
            self.update_balance_worker = TimedUpdateTotalBalance()

            self.update_balance_worker.moveToThread(
                self.update_balance_thread
            )
            self.update_balance_worker.balance.connect(
                self.update_balance
            )
            self.update_balance_thread.started.connect(
                self.update_balance_worker.work
            )

            self.update_eth_gas = QTimer()
            self.update_base_gas = QTimer()

            # Price update Thread/Worker
            self.update_price_worker = TimedUpdatePriceOfAssetsWorker()
            self.update_price_thread = QThread()

            self.update_price_worker.moveToThread(self.update_price_thread)
            self.update_price_worker.timer.timeout.connect(
                self.update_price_worker.work
            )
            self.update_price_worker.eth_price.connect(self.update_eth_price)
            self.update_price_thread.started.connect(
                lambda: self.update_price_worker.timer.start(15000)
            )

            self.tm = QTimer()
            self.tm.timeout.connect(self.update_price)

            self.thread.start()
            self.thread2.start()
            self.update_balance_thread.start()
            self.tm.start(15000)
            self.update_price_thread.start()

        # Switched to QTableWidgetItem instead of QlineEdit in v3.1
        def init_table(self):
            self.table = QTableWidget(self)
            self.table.setRowCount(
                len(prog.asset['eth']['name']) + 1
            )
            self.table.setColumnCount(3)
            self.table.setColumnWidth(0, 380)
            self.table.setColumnWidth(1, 294)
            self.table.setColumnWidth(2, 300)
            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setVisible(True)
            self.table.resize(1040, 450)
            self.table.move(32, 186)
            self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.table.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.table.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )
            self.table.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.Fixed
            )
            
            header_items = [
                QTableWidgetItem("Asset"),
                QTableWidgetItem("Amount"),
                QTableWidgetItem("Market Price")
            ]
            
            for item in enumerate(header_items):
                self.table.setHorizontalHeaderItem(*item)
            
            self.table.setIconSize(QSize(32, 32))
            
        def init_coin_row(self):
            self.coin_settings_box = QWidget(self)
            self.coin_settings_box.setFixedSize(200, 70)
            self.coin_settings_box.show()
            self.coin_settings_layout = QHBoxLayout()
            
            self.coin_settings_box.setLayout(self.coin_settings_layout)
            self.coin_settings_box.setStyleSheet('background: transparent;')
            self.coin_settings_box.move(30, 118)
            
            self.add_coin_btn = QPushButton(
                parent=self.coin_settings_box,
                icon=TigerWalletImage.plus_blue
            )

            self.add_coin_btn.setToolTip('Add a cryptocurrency')
            self.add_coin_btn.setFixedSize(50, 40)
            self.add_coin_btn.setIconSize(QSize(32, 32))
            self.add_coin_btn.show()
            self.add_coin_btn.clicked.connect(
                lambda: self.init_add_coin_window(prog.chain)
            )

            
            self.default_coin_btn = QPushButton(
                parent=self.coin_settings_box,
                icon=TigerWalletImage.restore_blue
            )
            self.default_coin_btn.setToolTip('Restore default token list')
            self.default_coin_btn.setFixedSize(50, 40)
            self.default_coin_btn.setIconSize(QSize(32, 32))
            self.default_coin_btn.show()
            self.default_coin_btn.clicked.connect(self.restore_default_coins)

            self.del_coin_btn = QPushButton(
                parent=self.coin_settings_box,
                icon=TigerWalletImage.delete_blue
            )
            self.del_coin_btn.setToolTip('Remove a cryptocurrency')
            self.del_coin_btn.setFixedSize(50, 40)
            self.del_coin_btn.setIconSize(QSize(32, 32))
            self.del_coin_btn.show()
            self.del_coin_btn.clicked.connect(self.init_rm_coin_window)
            
            self.coin_settings_layout.addWidget(self.add_coin_btn)
            self.coin_settings_layout.addWidget(self.default_coin_btn)
            self.coin_settings_layout.addWidget(self.del_coin_btn)

        def init_add_coin_window(self, chain=prog.chain):
            self.addcointab = True
            self.add_coin_btn.hide()
            self.del_coin_btn.hide()
            self.default_coin_btn.hide()
            self.table.hide()
            self.val.hide()
            self.btn_showhide.hide()
            
            self.coin_add_box = QWidget(self)
            self.coin_add_box.setStyleSheet('background: transparent;')
            self.coin_add_box.setMinimumSize(470, 358)
            self.coin_add_box.move(359, 180)
            self.coin_add_box.show()
            
            self.coin_add_layout = QVBoxLayout()
            self.coin_add_box.setLayout(self.coin_add_layout)
            
            # Coin address
            self.coinaddr = QLineEdit(self.coin_add_box)
            self.coinaddr.setPlaceholderText("Contract address")
            self.coinaddr.setMinimumSize(460, 36)
            self.coinaddr.setMaxLength(42)

            self.errlbl = QLabel("Invalid contract address", self)
            self.errlbl.resize(1100, 64)
            self.errlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.errlbl.move(0, 248)

            self.contractlbl = QLabel("Contract:", self)
            self.contractlbl.resize(90, 30)
            self.contractlbl.move(264, 230)
            self.contractlbl.show()

            # Coin name
            self.coinname = QLineEdit(self.coin_add_box)
            self.coinname.setMinimumSize(460, 36)
            self.coinname.setEnabled(False)

            self.coinnamelbl = QLabel("Name:", self)
            self.coinnamelbl.resize(90, 30)
            self.coinnamelbl.move(264, 296)
            self.coinnamelbl.show()

            # Coin symbol
            self.coinsym = QLineEdit(self.coin_add_box)
            self.coinsym.setMinimumSize(460, 36)
            self.coinsym.setEnabled(False)

            self.coinsymlbl = QLabel("Symbol:", self)
            self.coinsymlbl.resize(90, 30)
            self.coinsymlbl.move(264, 382)
            self.coinsymlbl.show()

            # Decimals
            self.coindec = QLineEdit(self.coin_add_box)
            self.coindec.setMinimumSize(460, 36)
            self.coindec.setEnabled(False)

            self.coindeclbl = QLabel("Decimal:", self)
            self.coindeclbl.resize(90, 30)
            self.coindeclbl.move(264, 458)
            self.coindeclbl.show()
            
            self.coin_add_layout.addWidget(self.coinaddr)
            self.coin_add_layout.addWidget(self.coinname)
            self.coin_add_layout.addWidget(self.coinsym)
            self.coin_add_layout.addWidget(self.coindec)
            

            def _fetch_token_info():
                try:
                    self.c = create_contract(
                        self.coinaddr.text(),
                        chain=chain
                    )

                    self.coinname.setText(
                        self.c.functions.name().call()
                    )

                    self.coinsym.setText(
                        self.c.functions.symbol().call()
                    )
                    
                    dec = self.c.functions.decimals().call()

                    self.coindec.setText(str(dec))

                    self.continue_add_coin_btn.setEnabled(True)
                except Exception:
                    self.errlbl.show()
                    return

            def _validate_address(addr):
                if self.errlbl.text() == "Asset is already in your asset list":
                    self.errlbl.setText(
                        "Invalid Ethereum contract address"
                    )

                if len(addr) == 42:
                    if not w3.is_address(addr):
                        self.errlbl.show()
                        return

                    else:
                        self.errlbl.hide()

                    if addr in prog.asset[chain]['address']:
                        self.errlbl.setText(
                            "Asset is already in your asset list"
                        )
                        self.errlbl.show()
                        return

                    _fetch_token_info()

                else:
                    self.errlbl.hide()
                    self.continue_add_coin_btn.setEnabled(False)

            # Add entered coin button
            self.continue_add_coin_btn = QPushButton(
                text=" Add coin",
                parent=self,
                icon=TigerWalletImage.plus_blue
            )

            def launch_add_coin():
                self.add_coin(
                    self.coinname.text(),
                    self.coinaddr.text(),
                    self.coinsym.text()
                )

            self.continue_add_coin_btn.setFixedSize(240, 62)
            self.continue_add_coin_btn.setIconSize(QSize(32, 32))
            self.continue_add_coin_btn.move(550, 540)
            self.continue_add_coin_btn.show()
            self.continue_add_coin_btn.setEnabled(False)
            self.continue_add_coin_btn.clicked.connect(launch_add_coin)

            self.close_add_coin_btn = QPushButton(
                text=" Close",
                parent=self,
                icon=TigerWalletImage.close_blue
            )

            self.close_add_coin_btn.setFixedSize(240, 62)
            self.close_add_coin_btn.setIconSize(QSize(32, 32))
            self.close_add_coin_btn.move(290, 540)
            self.close_add_coin_btn.show()
            self.close_add_coin_btn.clicked.connect(
                self.close_add_coin_window
            )

            self.coinaddr.textChanged.connect(_validate_address)

            if prog.configs["theme"] == "default_dark":
                self.continue_add_coin_btn.setStyleSheet(
                    ':enabled {'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #627eea;}"
                    + ':disabled {'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + 'background: transparent;'
                    + "color: gray;}"
                    + 'QPushButton::hover{background-color: #1e1e1e;}'
                )

                self.close_add_coin_btn.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.contractlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6ca0dc;"
                    + "background: #0a0f18;"
                )

                # Text that gets displayed when address is invalid
                self.errlbl.setStyleSheet(
                    "font-size: 17px;"
                    + "color: red;"
                    + "background: transparent;"
                )

                self.coinnamelbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6ca0dc;"
                    + "background: #0a0f18;"
                )

                self.coinsymlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6ca0dc;"
                    + "background: #0a0f18;"
                )

                self.coindeclbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6ca0dc;"
                    + "background: #0a0f18;"
                )

            elif prog.configs["theme"] == "default_light":
                self.continue_add_coin_btn.setStyleSheet(
                    ':enabled {'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #627eea;}"
                    + ':disabled {'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + 'background: transparent;'
                    + "color: gray;}"
                    + 'QPushButton::hover{background-color: #ced7e9;}'
                )

                self.close_add_coin_btn.setStyleSheet(
                    'QPushButton {background-color: transparent;'
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: #3c598e;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                # Address
                self.coinaddr.setStyleSheet(
                    "color: #3c598e;"
                    + "border: 1px solid #1e2b45;;"
                    + "font-size: 18px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.contractlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #0a0f18;"
                    + "background: transparent;"
                )

                # Text that gets displayed when address is invalid
                self.errlbl.setStyleSheet(
                    "font-size: 17px;"
                    + "color: red;"
                    + "background: transparent;"
                )

                # Name
                self.coinname.setStyleSheet(
                    ":disabled {color: #3c598e;"
                    + "border: 1px solid #1e2b45;;"
                    + "font-size: 18px;"
                    + "border-radius: 16px;"
                    + 'background: transparent;'
                    + "padding: 4px;}"
                )

                self.coinnamelbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #0a0f18;"
                    + "background: transparent;"
                )

                # Symbol
                self.coinsym.setStyleSheet(
                    ":disabled {color: #3c598e;"
                    + "border: 1px solid #1e2b45;;"
                    + "font-size: 18px;"
                    + "border-radius: 16px;"
                    + 'background: transparent;'
                    + "padding: 4px;}"
                )

                self.coinsymlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #0a0f18;"
                    + "background: transparent;"
                )

                # Decimal
                self.coindec.setStyleSheet(
                    ":disabled {color: #3c598e;"
                    + "border: 1px solid #1e2b45;;"
                    + "font-size: 18px;"
                    + "border-radius: 16px;"
                    + 'background: transparent;'
                    + "padding: 4px;}"
                )

                self.coindeclbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #0a0f18;"
                    + "background: transparent;"
                )

        def init_rm_coin_window(self):
            self.rmcointab = True

            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.val.hide()
            self.btn_showhide.hide()

            self.uppermsg = QLabel(
                text="Select which tokens you want to remove",
                parent=self
            )
            self.uppermsg.resize(len(self.uppermsg.text()) + 540, 36)
            self.uppermsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.uppermsg.move(260, 136)
            self.uppermsg.show()

            # Cancel Button
            self.rm_coin_cancel = QPushButton(
                text=" Cancel",
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.rm_coin_cancel.setFixedSize(200, 46)
            self.rm_coin_cancel.setIconSize(QSize(32, 32))
            self.rm_coin_cancel.move(300, 652)
            self.rm_coin_cancel.show()
            self.rm_coin_cancel.clicked.connect(
                lambda: [
                    self.table.clearSelection(),
                    self.table.setSelectionMode(
                        QAbstractItemView.SelectionMode.NoSelection
                    ),
                    self.clear_rm_coin_tab()
                ]
            )

            self.rm_coin_continue = QPushButton(
                text=" Continue",
                parent=self,
                icon=TigerWalletImage.checkmark
            )
            self.rm_coin_continue.setFixedSize(200, 46)
            self.rm_coin_continue.setIconSize(QSize(32, 32))
            self.rm_coin_continue.move(580, 652)
            self.rm_coin_continue.show()
            self.rm_coin_continue.clicked.connect(self.rm_coin)

            self.table.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection
            )

            self.table.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )

            if prog.configs["theme"] == "default_dark":
                self.rm_coin_continue.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.rm_coin_cancel.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.uppermsg.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #eff1f3;"
                    + "background: #0a0f18;"
                )

            elif prog.configs["theme"] == "default_light":
                self.rm_coin_continue.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.rm_coin_cancel.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.uppermsg.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

        def init_side_bar(self):
            self.button_box = QWidget(self)
            self.button_box.hide()
            self.button_box.resize(1100, 126)
            self.button_box.setStyleSheet("background: transparent;")
            
            self.btn_box_layout = QHBoxLayout()
            self.button_box.setLayout(self.btn_box_layout)

            icon_size = QSize(32, 32)

            # Switch networks
            self.switch_network_button = QPushButton(self)
            self.switch_network_button.setFixedSize(72, 72)
            #self.switch_network_button.move(20, 28)
            self.switch_network_button.setIconSize(icon_size)
            self.switch_network_button.clicked.connect(self.switch_networks)
            self.switch_network_button.setIcon(
                TigerWalletImage.eth_img
            )

            # Load up sidebar buttons
            self.sidebar_button = [
                QPushButton(self)
                for i in range(8)
            ]

            for i in range(8):
                self.sidebar_button[i].setFixedSize(72, 72)
                self.sidebar_button[i].setIconSize(icon_size)

            self.home_button = QPushButton(self)
            self.home_button.setIcon(TigerWalletImage.home_blue)
            self.home_button.setFixedSize(72, 72)
            self.home_button.setIconSize(icon_size)
            self.home_button.clicked.connect(
                lambda: self._close_tab(self.tab)
            )
            self.home_button.setToolTip('Return to main screen')
            self.home_button.setEnabled(False)
            
            # Change wallet
            self.sidebar_button[0].setIcon(TigerWalletImage.wallet_blue)
            self.sidebar_button[0].clicked.connect(self.show_tab1)
            self.sidebar_button[0].setToolTip('Pop out wallet menu')

            # Send
            self.sidebar_button[1].setIcon(TigerWalletImage.send_blue)
            self.sidebar_button[1].clicked.connect(self.show_tab2)
            self.sidebar_button[1].setToolTip('Send crypto to another wallet')

            # Receieve
            self.sidebar_button[2].setIcon(TigerWalletImage.receive_blue)
            self.sidebar_button[2].clicked.connect(self.show_tab3)
            self.sidebar_button[2].setToolTip("Display your wallet's address")

            # Swap
            self.sidebar_button[3].setIcon(TigerWalletImage.swap_blue)
            self.sidebar_button[3].clicked.connect(self.show_tab4)
            self.sidebar_button[3].setToolTip('Swap tokens')

            # Robot
            self.sidebar_button[4].setIcon(TigerWalletImage.blue_robot)
            self.sidebar_button[4].clicked.connect(self.show_tab5)
            self.sidebar_button[4].setToolTip(
                'Use an assistant to perform various tasks'
            )

            # Address book
            self.sidebar_button[5].setIcon(TigerWalletImage.address_book_blue)
            self.sidebar_button[5].clicked.connect(self.show_tab6)
            self.sidebar_button[5].setToolTip('Show your contacts')

            # History
            self.sidebar_button[6].setIcon(TigerWalletImage.history_blue)
            self.sidebar_button[6].clicked.connect(self.show_tab7)
            self.sidebar_button[6].setToolTip('Display your past transactions')

            # Settings
            self.sidebar_button[7].setIcon(TigerWalletImage.settings_blue)
            self.sidebar_button[7].clicked.connect(self.show_tab8)
            self.sidebar_button[7].setToolTip('Change TigerWallet settings')

            # Donation button
            self.donation_button = QPushButton(self)
            self.donation_button.setFixedSize(72, 72)
            self.donation_button.setIcon(TigerWalletImage.donate_blue)
            self.donation_button.setIconSize(icon_size)
            self.donation_button.clicked.connect(self.init_donate_window)
            self.donation_button.setToolTip('Buy me a coffee')
            
            self.lock_wallet_button = QPushButton(
                parent=self,
                icon=TigerWalletImage.pass_blue,
            )
            self.lock_wallet_button.setFixedSize(72, 72)
            self.lock_wallet_button.setIconSize(icon_size)
            self.lock_wallet_button.setToolTip(
                'Lock your wallet'
            )
            self.lock_wallet_button.clicked.connect(
                lambda: [
                    self.unlock_wallet_box.show(),
                    self.setStyleSheet("background: transparent;"),
                    self.black_out_window(),
                ]
            )
            
            ''' 
            Button order
            
            The first button is switch network.
            Then we have action buttons (the for loop + donation + lock)
            The last button is settings button
            '''
            self.btn_box_layout.addWidget(self.switch_network_button)
            self.btn_box_layout.addWidget(self.home_button)
            
            for i in range(7):
                self.btn_box_layout.addWidget(self.sidebar_button[i])
            
            self.btn_box_layout.addWidget(self.donation_button)
            self.btn_box_layout.addWidget(self.lock_wallet_button)
            self.btn_box_layout.addWidget(self.sidebar_button[7])
            

            self.button_box.show()

        def init_sidebar_style(self):
            if prog.configs["theme"] == "default_dark":
                for i in range(7):
                    self.sidebar_button[i].setStyleSheet(
                         "QPushButton {background-color: transparent;"
                        + "border-radius: 36px;}"
                        + "QPushButton::hover{background: #1e1e1e;}"
                        + 'QPushButton::menu-indicator{image: none;}'
                    )

                self.donation_button.setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

                self.switch_network_button.setStyleSheet(
                    "QPushButton {background: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

                self.home_button.setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                for i in range(7):
                    self.sidebar_button[i].setStyleSheet(
                         "QPushButton {background-color: transparent;"
                        + "border-radius: 36px;}"
                        + "QPushButton::hover{background: #ced7e9;}"
                        + 'QPushButton::menu-indicator{image: none;}'
                    )

                self.donation_button.setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

                self.switch_network_button.setStyleSheet(
                    "QPushButton {background: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

                self.home_button.setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        def init_wallet_btn_options(self):
            self.wallet_menu = QtWidgets.QMenu()

            _w_options = [
                'Switch wallets',
                'Create new wallet',
                'Import wallet',
                'Delete wallet'
            ]

            self.wallet_menu.addAction(
                _w_options[0],
                self.show_tab1
            )

            def launch_create_wallet():
                prog.new_wallet = True
                self.stacked_layout.setCurrentIndex(3)
                
            self.wallet_menu.addAction(
                _w_options[1],
                launch_create_wallet
            )

            def launch_import_wallet():
                prog.used_import_wallet_from_userwallet = True
                self.stacked_layout.setCurrentIndex(4)
                

            self.wallet_menu.addAction(
                _w_options[2],
                launch_import_wallet
            )

            self.wallet_menu.addAction(
                _w_options[3],
                self.del_wallet_window
            )

            self.sidebar_button[0].setMenu(self.wallet_menu)

        # FIRST button
        def init_change_wallet_window(self):
            self.box1 = QWidget(self)
            self.box1.resize(790, 620)
            self.box1.move(166, 140)
            self.box1.hide()

            self.change_wallet_title = QLabel(
                text="Select your wallet",
                parent=self.box1
            )

            self.change_wallet_title.setFixedSize(390, 50)
            self.change_wallet_title.move(180, 40)
            self.change_wallet_title.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            # Wallet selection
            self.wallet_list = QListWidget(self.box1)
            self.wallet_list.resize(730, 412)
            self.wallet_list.move(30, 110)
            self.wallet_list.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.wallet_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.wallets = prog.configs["wallets"]

            for wallets in enumerate(self.wallets):
                self.wallet_list.insertItem(*wallets)

            for i in range(len(self.wallets)):
                self.wallet_list.item(i).setSizeHint(QSize(730, 50))

                if self.wallet_list.item(i).text() == prog.nameofwallet:
                    self.wallet_list.item(i).setText(
                        self.wallet_list.item(i).text()
                        + " (current)"
                    )

            self.item = None

            # Click event
            def _clicked(item):
                if "(current)" in item.text():
                    errbox("This is the current wallet")
                    self.wallet_list.clearSelection()
                    return

                self.item = item.text()

            self.wallet_list.itemClicked.connect(_clicked)

            # Cancel button to return to the grid view
            self.cancel = QPushButton(
                text=" Cancel",
                parent=self.box1,
                icon=TigerWalletImage.close_blue
            )
            self.cancel.setFixedSize(240, 62)
            self.cancel.setIconSize(QSize(32, 32))
            self.cancel.move(120, 500)

            self.continue_btn = QPushButton(
                text=" Use selected wallet",
                parent=self.box1,
                icon=TigerWalletImage.checkmark,
            )
            self.continue_btn.setFixedSize(240, 62)
            self.continue_btn.setIconSize(QSize(32, 32))
            self.continue_btn.move(390, 500)
            self.continue_btn.clicked.connect(
                lambda: self.launch_chosen_wallet(self.item)
            )

            self.cancel.clicked.connect(self.clear_tab1)

        # SECOND button
        # Added ENS support in v2.0
        # Added paste button in v3.1
        def init_send_window(self):
            """ Send crypto window """
            self.box2 = QWidget(self)
            self.box2.resize(790, 620)
            self.box2.move(166, 126)
            self.box2.hide()

            self.eth_ns = ENS(web3_provider)

            self.asset_list_ = prog.asset[prog.chain]
            self.assetsval = prog.asset_details[prog.chain]['value']

            self.assets_addr = self.asset_list_['address']
            self.names = self.asset_list_["name"]
            self.symbols = self.asset_list_["symbol"]

            self.index = 0

            self.ethamount = (
                f"~{str(prog.eth_amount)[:18]} ETH"
                if prog.chain == 'eth'
                else f"~{str(prog.base_eth_amount)[:18]} ETH"
            )

            self.lblsize = [78, 30]

            self.sendlabel = QLabel("Send crypto", self.box2)
            self.sendlabel.setFixedSize(210, 48)
            self.sendlabel.move(274, 37)
            self.sendlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.topmsglabel = QLabel(
                text="Select the crypto that you want to send",
                parent=self.box2
            )
            self.topmsglabel.setFixedSize(780, 110)
            self.topmsglabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.topmsglabel.move(0, 58)

            """
                Asset list from which user selects
                the asset that they want to send
            """
            self.asset_list = QComboBox(self.box2)
            self.asset_list.resize(400, 52)
            self.asset_list.move(132, 176)
            self.asset_list.show()
            self.asset_list.insertItem(0, "ETHER (ETH)")
            self.asset_list.setItemIcon(0, TigerWalletImage.eth_img)

            self.qlist = QtWidgets.QListView(self.asset_list)
            self.qlist.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.asset_list.setView(self.qlist)

            for i in range(0, len(self.names)):
                self.asset_list.insertItem(
                    i + 1,
                    f"{self.names[i].upper()} ({self.symbols[i].upper()})"
                )

                self.asset_list.setItemIcon(
                    i + 1,
                    QIcon(self.asset_list_["image"][i])
                )

            self.asset_list.setIconSize(QSize(24, 24))

            # Dotted line fix for mac
            self.asset_list.setAttribute(
                Qt.WidgetAttribute.WA_MacShowFocusRect,
                False
            )

            """ Display the word 'Asset' before entry field """
            self.assetlbl = QLabel("Asset:", self.box2)
            self.assetlbl.resize(*self.lblsize)
            self.assetlbl.move(48, 182)

            """ Display user balance of chosen asset """
            self.estimate_amount = QLabel(self.box2)
            self.estimate_amount.resize(240, 40)
            self.estimate_amount.move(560, 176)

            if self.ethamount != 0:
                if prog.chain == 'eth':
                    self.estimate_amount.setText(
                        f"~{prog.eth_amount} ETH"
                    )

                elif prog.chain == 'base':
                    self.estimate_amount.setText(
                        f"~{prog.base_eth_amount} ETH"
                    )

            else:
                self.estimate_amount.setText("0 (ETH)")

            """Update balance text based on asset selection"""
            def _update_avail(num):
                self.index = num - 1

                if num == 0:
                    self.estimate_amount.setText(self.ethamount)

                else:
                    self.c = float(self.assetsval[num - 1])

                    if self.c == 0.0:
                        self.estimate_amount.setText(
                            f"0.0 {self.symbols[num - 1].upper()}"
                        )

                    else:
                        amount = self.assetsval[:18]
                        self.estimate_amount.setText(
                            f"~{amount} {self.symbols[num - 1].upper()}"
                        )

            self.estimate_amount.show()
            self.asset_list.currentIndexChanged.connect(_update_avail)

            # Send to
            def _validate_address(inp):
                if inp in prog.contactbook['address']:
                    return

                if inp.endswith('.eth'):
                    if inp == '.eth':
                        self.errlabel.setText(
                            "Invalid ENS name"
                        )
                        self.errlabel.show()
                        return

                    try:
                        ens_address = self.eth_ns.address(inp)

                        if ens_address is None:
                            self.errlabel.setText(
                                "This ENS is not registered to any address"
                            )
                            self.errlabel.show()
                            return

                    except Exception:
                        self.errlabel.setText(
                            "Invalid ENS name. Did you type it correctly?"
                        )
                        self.errlabel.show()
                        return

                if len(inp) == 42:
                    if not w3.is_address(inp):
                        self.errlabel.setText(
                            "This is not a valid ERC-20 address"
                        )
                        self.errlabel.show()
                        return

                    try:
                        w3.eth.to_checksum_address(inp)
                    except Exception:
                        self.errlabel.setText(
                            "This is not a valid ERC-20 address"
                        )
                        self.errlabel.show()
                        return

                    try:
                        _contract = create_contract(inp)
                        _tmp = _contract.functions.symbol().call()

                        self.errlabel.setText(
                            "You're trying to send to a contract address"
                        )
                        self.errlabel.show()
                        return

                    except Exception:
                        pass

                self.errlabel.hide()

            self.typeaddr = QLineEdit(self.box2)
            self.typeaddr.setPlaceholderText(" Address to send to")
            self.typeaddr.resize(400, 32)
            self.typeaddr.move(134, 260)
            self.typeaddr.setMaxLength(42)
            self.typeaddr.textChanged.connect(_validate_address)

            self.paste_addr = QPushButton(
                text=' Paste address',
                parent=self.box2,
                icon=TigerWalletImage.copy_blue
            )
            self.paste_addr.setIconSize(QSize(32, 32))
            self.paste_addr.resize(180, 40)
            self.paste_addr.move(558, 258)

            self.paste_menu = QtWidgets.QMenu()
            self.paste_menu.addAction(
                'Paste from clipboard',
                lambda: self.typeaddr.setText(
                    QApplication.clipboard().text()
                )
            )

            self.paste_contact_info_menu = QtWidgets.QMenu(
                'Paste from contact book     ', # Space between text and arrow
                self.paste_addr
            )

            for index in range(len(prog.contactbook['name'])):
                self.paste_contact_info_menu.addAction(
                    prog.contactbook['name'][index]
                    + f" ({prog.contactbook['address'][index]})",
                    lambda: [
                        self.typeaddr.setText(
                            prog.contactbook['address'][index]
                        ),
                    ]
                )

            self.paste_addr.setMenu(self.paste_menu)
            self.paste_menu.addMenu(self.paste_contact_info_menu)

            self.sendtolbl = QLabel("Send to:", self.box2)
            self.sendtolbl.resize(*self.lblsize)
            self.sendtolbl.move(48, 258)

            self.errlabel = QLabel(self.box2)
            self.errlabel.resize(400, 40)
            self.errlabel.move(190, 286)

            # Amount
            self.amount = QLineEdit(self.box2)
            self.amount.setPlaceholderText(" Amount to send")
            self.amount.resize(400, 30)
            self.amount.move(134, 330)

            validator = QtGui.QDoubleValidator()
            validator.setBottom(0.00000000000000000000000000000001)
            validator.setDecimals(30)
            validator.setTop(1000000000000000000000000000000)
            validator.setNotation(validator.Notation.StandardNotation)

            self.amount.setValidator(validator)

            self.amountlbl = QLabel("Amount:", self.box2)
            self.amountlbl.resize(*self.lblsize)
            self.amountlbl.move(48, 327)

            self.slider = QSlider(Qt.Orientation.Horizontal, self.box2)
            self.slider.setRange(0, 100)
            self.slider.setTickInterval(25)
            self.slider.setPageStep(25)
            self.slider.setTickPosition(self.slider.TickPosition.TicksAbove)
            self.slider.move(562, 332)
            self.slider.resize(180, 26)

            def _update(num):
                if self.asset_list.currentIndex() == 0:
                    bal = (
                        prog.eth_amount if prog.chain == 'eth'
                        else prog.base_eth_amount
                    )

                    if self.slider.value() == 0:
                        self.amount.setText("")

                    elif self.slider.value() == 100:
                        self.amount.setText(str(bal)[:18])

                    else:
                        self.amount.setText(
                            rm_e_notation(
                                float(bal)
                                / float(100 / num)
                            )
                            [:18]
                        )

                else:
                    if self.assetsval == "0.0":
                        return

                    self.amount.setText(
                        rm_e_notation(
                            str(
                                float(self.assetsval)
                                / float(100 / num)
                            )
                            [:18]
                        )
                    )

            self.slider.valueChanged.connect(_update)

            # Gas
            self.gasfeelbl = QLabel("Gas:", self.box2)
            self.gasfeelbl.resize(*self.lblsize)
            self.gasfeelbl.move(48, 396)

            self.gasfee = QLineEdit(self.box2)
            self.gasfee.resize(400, 32)
            self.gasfee.move(134, 398)
            self.gasfee.setEnabled(False)

            self.update_eth_gas.timeout.connect(
                lambda:
                    self.gasfee.setText(
                        f"{prog.eth_gas} ETH"
                    )
            )
            self.update_eth_gas.start(500)

            self.update_base_gas.timeout.connect(
                lambda:
                    self.gasfee.setText(
                        f"{prog.base_gas} ETH"
                    )
            )

            # Close/Send buttons
            self.close_send_btn = QPushButton(
                text=" Close",
                parent=self.box2,
                icon=TigerWalletImage.close_blue
            )
            self.close_send_btn.setFixedSize(240, 62)
            self.close_send_btn.setIconSize(QSize(32, 32))
            self.close_send_btn.move(120, 490)

            self.send_btn = QPushButton(
                text=" Continue",
                parent=self.box2,
                icon=TigerWalletImage.checkmark,
            )
            self.send_btn.setFixedSize(240, 62)
            self.send_btn.setIconSize(QSize(32, 32))
            self.send_btn.move(390, 490)

            # Complete transaction
            class ConfirmAndSend(QWidget):
                def __init__(self, master):
                    super().__init__()
                    self.opt = 1
                    self.master = master
                    self._gas = 0.0
                    self._priority = 0.0
                    self._amount = 0.0

                    self.tx_hash = ''

                    self.init_confirmation()
                    self.init_buttons()

                    if "default" in prog.configs["theme"]:
                        self.frm.setStyleSheet(
                            "border: 1px solid #1e2b45;;"
                            + "border-radius: 16px;"
                            + "background: transparent;"
                        )

                        self.send.setStyleSheet(
                            "QPushButton{background-color:  #4f86f7;"
                            + "border-radius: 24px;"
                            + "font-size: 23px;"
                            + "color: black}"
                            + "QPushButton::hover{background-color: #627eea;}"
                        )

                        self.cancel.setStyleSheet(
                            "QPushButton::hover{background-color: #1e1e1e;}"
                        )

                    if prog.configs["theme"] == "default_dark":
                        self.setStyleSheet("background: #0a0f18")

                        self.topmsg.setStyleSheet(
                            "font-size: 30px;"
                            + "color: #627eea;"
                            + "background: #0a0f18;"
                        )

                        self.notice_msg.setStyleSheet(
                            "font-size: 20px;"
                            + "color: #c5d4e7;"
                            + "background: transparent;"
                        )

                        self.assetlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.sendtolbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.send_to_address.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.user_asset.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.am.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.amlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.gaslbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.gas_amount.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.prioritylbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.priority.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.total.setStyleSheet(
                            "font-size: 28px;"
                            + "color: #627eea;"
                            + "background: transparent;"
                            + "border: 1px solid #1e2b45;;"
                            + "border-radius: 16px;"
                        )

                        self.pass_label.setStyleSheet(
                            "font-size: 22px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.btn_showhide.setStyleSheet(
                            "QPushButton{background-color:  #778ba5;"
                            + "border-radius: 8px;}"
                            + "QPushButton::hover{background-color: #ced7e9;}"
                        )

                    elif prog.configs["theme"] == "default_light":
                        self.setStyleSheet("background-color: #eff1f3")

                        self.topmsg.setStyleSheet(
                            "font-size: 30px;"
                            + "color: #627eea;"
                            + "background: #eff1f3;"
                        )

                        self.notice_msg.setStyleSheet(
                            "font-size: 20px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.assetlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.sendtolbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.send_to_address.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.user_asset.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.am.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.amlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.gaslbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.gas_amount.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.prioritylbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #339AF0;"
                            + "background: transparent;"
                        )

                        self.priority.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.total.setStyleSheet(
                            "font-size: 28px;"
                            + "color: #627eea;"
                            + "background: transparent;"
                            + "border: 1px solid #1e2b45;;"
                            + "border-radius: 16px;"
                        )

                        self.pass_label.setStyleSheet(
                            "font-size: 22px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.btn_showhide.setStyleSheet(
                            "QPushButton{background-color: #778ba5;"
                            + "border-radius: 8px;}"
                            + "QPushButton::hover{background-color: #ced7e9;}"
                        )

                        self.send.setStyleSheet(
                            "QPushButton::hover{background-color: #ced7e9;}"
                        )

                        self.cancel.setStyleSheet(
                            "QPushButton::hover{background-color: #ced7e9;}"
                        )

                def init_confirmation(self):
                    if (
                        self.master.index == -1
                        or self.master.index == 0
                    ):
                        self.sym = "ETH"

                    else:
                        self.sym = \
                            self.master.symbols[self.master.index].upper()

                    if (
                        self.master.index == -1
                        or self.master.index == 0
                    ):
                        self.asset = 'Ether'

                    else:
                        self.asset = self.master.names[self.master.index]

                    self.setFixedWidth(650)
                    self.setFixedHeight(670)
                    self.setWindowTitle("TigerWallet  -  Send confirmation")

                    align_to_center(self)

                    self.frm = QLabel(self)
                    self.frm.resize(626, 600)
                    self.frm.move(12, 54)

                    self.topmsg = QLabel("Send crypto asset", self)
                    self.topmsg.resize(294, 42)
                    self.topmsg.move(174, 32)
                    self.topmsg.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    self.notice_msg = QLabel(
                        text="Below is a summary of your transaction:",
                        parent=self
                    )
                    self.notice_msg.resize(346, 46)
                    self.notice_msg.move(150, 82)
                    self.notice_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    self.assetlbl = QLabel("Asset:", self)
                    self.assetlbl.resize(50, 40)
                    self.assetlbl.move(70, 139)

                    self.user_asset = QLabel(self)
                    self.user_asset.resize(360, 40)
                    self.user_asset.move(158, 140)
                    self.user_asset.setText(f"{self.asset}")

                    self.sendtolbl = QLabel("Send to:", self)
                    self.sendtolbl.resize(100, 40)
                    self.sendtolbl.move(70, 179)

                    self.send_to_address = QLabel(self)
                    self.send_to_address.resize(460, 40)
                    self.send_to_address.move(158, 180)

                    self.send_to_address.setText(
                        f"{self.master.typeaddr.text()}"
                    )

                    self.amlbl = QLabel("Amount:", self)
                    self.amlbl.resize(100, 40)
                    self.amlbl.move(70, 219)

                    self.am = QLabel(self)
                    self.am.resize(400, 40)
                    self.am.move(158, 220)

                    def _quick_price_check():
                        self.p = float(get_price(self.sym))
                        amount = float(self.master.amount.text())
                        amount_total = self.p*amount
                        amount_as_str = rm_e_notation(amount_total)

                        self.am.setText(
                            f"${amount_as_str[:13]}"
                            f" ({self.master.amount.text()} {self.sym})"
                        )

                        self._amount = amount_as_str[:13]

                    _tmp = Thread(target=_quick_price_check)
                    _tmp.run()

                    self.gas_amount = QLabel(self)

                    def display_gas():
                        while True:
                            if prog.chain == 'eth':
                                self.gas_amount.setText(
                                    f"{prog.eth_gas} ETH"
                                )
                                self._gas = prog.eth_gas

                            elif prog.chain == 'base':
                                self.gas_amount.setText(
                                    f"{prog.base_gas} ETH"
                                )
                                self._gas = prog.base_gas

                    gas_th = Thread(target=display_gas)
                    gas_th.start()

                    self.gas_amount.resize(400, 40)
                    self.gas_amount.move(158, 260)

                    self.gaslbl = QLabel("Gas:", self)
                    self.gaslbl.resize(100, 40)
                    self.gaslbl.move(70, 259)

                    self.priority = QLabel(self)

                    def _quick_priority_check():
                        priority_value = w3.eth.max_priority_fee
                        priority_value = float(priority_value)
                        priority_value *=2
                        priority_value /= 10**18
                        priority_value *= 23000
                        priority_value = round(priority_value, 8)

                        self._priority = priority_value

                        self.priority.setText(
                            f"{rm_e_notation(priority_value)} ETH"
                        )

                    _quick_priority_check()

                    self.prioritylbl = QLabel("Priority:", self)
                    self.prioritylbl.resize(100, 40)
                    self.prioritylbl.move(70, 299)

                    self.priority.resize(400, 40)
                    self.priority.move(158, 300)

                    self.total = QLabel(self)
                    self.total.resize(400, 46)
                    self.total.move(120, 364)
                    self.total.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    def calculate_total_value():
                        priority = self._priority

                        _total = (
                            float(self._amount)
                            + float(self._gas)
                            + float(priority)
                        )

                        _total = round(_total, 2)

                        self.total.setText(f"TOTAL: ~${str(_total)}")

                    calculate_total_value()

                    self.pass_label = QLabel(
                        text=(
                            'Your password is required '
                            + 'to complete this transaction'
                        ),
                        parent=self
                    )

                    self.pass_label.resize(650, 38)
                    self.pass_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.pass_label.move(0, 428)


                    self.send_field = QLineEdit(self)
                    self.send_field.setEchoMode(QLineEdit.EchoMode.Password)
                    self.send_field.setPlaceholderText(
                        'Enter your password'
                    )
                    self.send_field.resize(430, 38)
                    self.send_field.move(84, 500)
                    self.send_field.returnPressed.connect(self.validate_pass)

                def init_buttons(self):
                    self.cancel = QPushButton(
                        parent=self,
                        icon=TigerWalletImage.close_blue
                    )

                    self.cancel.setFixedSize(40, 36)
                    self.cancel.setIconSize(QSize(24, 24))
                    self.cancel.move(40, 10)
                    self.cancel.clicked.connect(self.close)

                    total_am = self.am.text()

                    self.send = QPushButton(
                        text=(
                            'Send '
                            + total_am[
                                    total_am.find('(')+1
                                    : len(total_am)-1
                                ]
                                .upper()
                        ),
                        parent=self
                    )

                    self.send.setFixedSize(540, 48)
                    self.send.setIconSize(QSize(32, 32))
                    self.send.move(54, 580)
                    self.send.clicked.connect(
                        self.validate_pass
                    )

                    self.btn_showhide = QPushButton(
                        text=None,
                        parent=self,
                        icon=TigerWalletImage.closed_eye,
                    )

                    self.btn_showhide.setIconSize(QSize(28, 28))
                    self.btn_showhide.move(540, 506)
                    self.btn_showhide.clicked.connect(self.unhide)

                def send_tx(self):
                    send_address = self.send_to_address.text()

                    if send_address.endswith('.eth'):
                        self.eth_ns =  ENS(
                            web3_provider
                        )

                        send_address = self.eth_ns.address(send_address)

                    if prog.chain == 'eth':
                        chainId = 1

                    elif prog.chain == 'base':
                        chainId = 8453

                    # Convert to WEI
                    amount_ = float(self._amount) * 10**18

                    __gas = (
                        prog.eth_gas if prog.chain == 'eth'
                        else prog.base_gas
                    )

                    if __gas == '0.0':
                        __gas = w3.eth.gas_price

                    gas_ = float(__gas) * 10**18
                    priority_ = int(self._priority) * 10**18

                    from_ = prog.account.address
                    to = send_address

                    transaction = ''

                    if self.asset != "Ether":
                        cc = create_contract(
                            (
                                prog.asset[prog.chain]
                                ['address']
                                [self.master.index]
                            ),
                            chain=prog.chain
                        )

                        transaction = (
                            cc.functions.transfer(to, int(amount_))
                            .build_transaction({
                                "from": from_,
                                "nonce": w3.eth.get_transaction_count(
                                    prog.account.address
                                ),
                                "gas": 23000,
                                "maxFeePerGas": int(gas_),
                                "maxPriorityFeePerGas": priority_,
                                'chainId': chainId
                            })
                        )

                    else:
                        transaction = {
                            "from": from_,
                            "to": to,
                            "value": int(amount_) ,
                            "nonce": w3.eth.get_transaction_count(
                                prog.account.address
                            ),
                            "gas": 23000,
                            "maxFeePerGas": int(gas_),
                            "maxPriorityFeePerGas": priority_,
                            'chainId': chainId
                        }

                    signed = w3.eth.account.sign_transaction(
                        transaction_dict=transaction,
                        private_key=prog.account.key
                    )

                    try:
                        self.tx_hash = w3.eth.send_raw_transaction(
                            signed.raw_transaction
                        )

                    except Exception:
                        errbox('Not enough funds to complete this transaction')
                        return

                    #th = Thread(target=self.wait_for_tx_to_finalize)
                    #th.start()
                    self.wait_for_tx_to_finalize()


                def wait_for_tx_to_finalize(self):
                    # Close window elements
                    def _close_elements():
                        self.notice_msg.close()
                        self.assetlbl.close()
                        self.user_asset.close()
                        self.sendtolbl.close()
                        self.send_to_address.close()
                        self.amlbl.close()
                        self.am.close()
                        self.gas_amount.close()
                        self.gaslbl.close()
                        self.priority.close()
                        self.prioritylbl.close()
                        self.total.close()
                        self.send_field.close()
                        self.pass_label.close()

                        self.btn_showhide.close()
                        self.cancel.close()
                        #self.send.close()

                    _close_elements()

                    self.pass_label2 = QLabel(self)
                    self.pass_label2.resize(650, 70)
                    self.pass_label2.setAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )
                    self.pass_label2.setText('Transaction comple\n')
                    self.pass_label2.move(0, 209)
                    self.pass_label2.show()

                    self.tx_label = QLabel(self)
                    self.tx_label.hide()
                    self.tx_label.resize(650, 70)
                    self.tx_label.move(20, 340)

                    self.tx_label.setTextInteractionFlags(
                        Qt.TextInteractionFlag.TextSelectableByMouse
                    )
                    self.tx_label.setAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                    self.tx_label.setText(
                        'Transaction hash:\n'
                        + self.tx_hash
                    )

                    # Reusing the send button to close the window
                    self.send.setText('Close window')
                    self.send.setFixedSize(240, 48)
                    self.send.setIconSize(QSize(32, 32))
                    self.send.move(208, 490)
                    self.send.clicked.connect(
                        lambda: [
                            self.close(),
                            self.deleteLater()
                        ]
                    )
                    self.send.hide()

                    if prog.configs['theme'] == 'default_dark':
                        self.pass_label2.setStyleSheet(
                            "font-size: 22px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                        self.tx_label.setStyleSheet(
                            "font-size: 16px;"
                            + "color: #9fb1ca;"
                            + "background: transparent;"
                        )

                    elif prog.configs['theme'] == 'default_light':
                        self.pass_label2.setStyleSheet(
                            "font-size: 22px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                        self.tx_label.setStyleSheet(
                            "font-size: 16px;"
                            + "color: #3c598e;"
                            + "background: transparent;"
                        )

                #
                def unhide(self):
                    if self.opt == 1:
                        self.btn_showhide.setIcon(TigerWalletImage.opened_eye)
                        self.send_field.setEchoMode(QLineEdit.EchoMode.Normal)
                        self.opt = 0

                    elif self.opt == 0:
                        self.btn_showhide.setIcon(TigerWalletImage.closed_eye)
                        self.send_field.setEchoMode(
                            QLineEdit.EchoMode.Password
                        )
                        self.opt = 1

                # Validate pass
                def validate_pass(self):
                    passwd = self.send_field.text()

                    if len(passwd) == 0:
                        errbox("Please enter a password")
                        return

                    with open(prog.nameofwallet, "rb") as f:
                        try:
                            Account.decrypt(
                                orjson.loads(f.read()),
                                password=passwd
                            )

                        except ValueError:
                            errbox("Invalid password")
                            return

                    self.send_tx()

            def _continue_send():
                if (
                    len(self.typeaddr.text()) == 0
                    or len(self.amount.text()) == 0
                ):
                    errbox("One or more of the entry fields are empty")
                    return

                if not self.errlabel.isHidden():
                    return

                self.cas = ConfirmAndSend(self)
                self.cas.show()

            self.send_btn.clicked.connect(_continue_send)
            self.close_send_btn.clicked.connect(self.clear_tab2)

        # THIRD button
        def init_receive_window(self):
            """ Receive crypto window  """
            self.box3 = QWidget(self)
            self.box3.resize(770, 620)
            self.box3.move(162, 80)
            self.box3.hide()

            self.receive = QLabel("Receive", self.box3)
            self.receive.setFixedSize(178, 56)
            self.receive.move(300, 62)
            self.receive.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.label = QLabel(
                text="Only send ERC-20 assets to this address!",
                parent=self.box3,
            )

            self.label.resize(384, 61)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(198, 106)

            self.qrlabel = QLabel(self.box3)
            self.qrlabel.resize(340, 310)
            self.qrlabel.move(224, 174)

            buf = BytesIO()

            self.qrcode = segno.make(self.address)
            self.qrcode.save(
                buf,
                scale=10,
                border=2,
                light=(
                    None
                    if prog.configs["theme"] == "default_light"
                    else "white"
                ),
                kind="png",
            )

            self.qrimg = QPixmap()
            self.qrimg.loadFromData(buf.getvalue())
            self.qrlabel.setPixmap(self.qrimg)

            self.addr = QLineEdit(self.box3)
            self.addr.resize(408, 30)
            self.addr.move(172, 514)
            self.addr.setText(self.address)
            self.addr.setReadOnly(True)
            #self.addr.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.closebtn = QPushButton(
                text=" Close",
                parent=self.box3,
                icon=TigerWalletImage.close_blue
            )

            self.closebtn.setFixedSize(200, 54)
            self.closebtn.setIconSize(QSize(32, 32))
            self.closebtn.move(288, 568)
            self.closebtn.clicked.connect(self.clear_tab3)

            self.copy_address = QPushButton(
                text=None,
                parent=self.box3,
                icon=TigerWalletImage.copy_blue
            )

            self.copy_address.setIconSize(QSize(16, 16))
            self.copy_address.move(542, 521)
            self.copy_address.clicked.connect(
                lambda: [
                    QApplication.clipboard().setText(self.address),
                    msgbox("Address has been copied!"),
                ]
            )

        # Massive improvements in v3.0
        # Supports base in v3.0
        # FOURTH button
        def init_swap_window(self):
            self.box4 = QWidget(self)
            self.box4.resize(1050, 680)
            self.box4.move(32, 80)
            self.box4.hide()

            self.uniswap = UniSwap()

            self.swap_title = QLabel(
                text=(
                    'Warning! Swapping is still in beta!\n'
                    'Do not use large funds when performing a swap!'
                ),
                parent=self.box4
            )

            self.swap_title.resize(1026, 80)
            self.swap_title.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.swap_title.move(0, 80)

            self.from_droplist = QComboBox(self.box4)
            self.from_droplist.resize(480, 52)
            self.from_droplist.move(280, 190)
            self.from_droplist.insertItem(
                0,
                'Ether'
                + ' (ETH)'
            )
            self.from_droplist.setItemIcon(0, TigerWalletImage.eth_img)
            self.from_droplist.setAttribute(
                Qt.WidgetAttribute.WA_MacShowFocusRect,
                False
            )

            self.qlist2 = QtWidgets.QListView(self.from_droplist)
            self.qlist2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.from_droplist.setView(self.qlist2)
            self.from_droplist.setIconSize(QSize(32, 32))

            for i in range(len(prog.asset[prog.chain]['name'])):
                self.from_droplist.insertItem(
                    i+1,
                    prog.asset[prog.chain]['name'][i].upper()
                    + f" ({prog.asset[prog.chain]['symbol'][i].upper()})"
                )
                self.from_droplist.setItemIcon(
                    i+1,
                    QIcon(prog.asset[prog.chain]['image'][i])
                )
                
            self.to_droplist = QComboBox(self.box4)
            self.to_droplist.resize(480, 52)
            self.to_droplist.move(280, 290)
            self.to_droplist.setAttribute(
                Qt.WidgetAttribute.WA_MacShowFocusRect,
                False
            )

            self.qlist3 = QtWidgets.QListView(self.to_droplist)
            self.qlist3.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.to_droplist.setView(self.qlist3)
            self.to_droplist.setIconSize(QSize(32, 32))

            self.swap_token_detail = {}

            with open(
                prog.dest_path
                + 'swap_token_details.json',
                mode='rb'
            ) as f:
                file_contents = orjson.loads(f.read())
                self.swap_token_detail = file_contents

                for i in range(len(file_contents['name']['eth'])):
                    self.to_droplist.insertItem(
                        i,
                        file_contents['name']['eth'][i].upper()
                        + f" ({file_contents['symbol']['eth'][i].upper()})"
                    )

                    self.to_droplist.setItemIcon(
                        i,
                        QIcon(file_contents['image']['eth'][i])
                    )

            # Image in-between the two checkboxes
            self.arrow_img = QPushButton(
                icon=TigerWalletImage.arrow_down_blue,
                parent=self.box4
            )
            self.arrow_img.setIconSize(QSize(32, 32))
            self.arrow_img.move(490, 252)

            self.network = prog.chain
            self.zero_in_hex = '0x0000000000000000000000000000000000000000'
            self.chosen_address_from_list = self.zero_in_hex # ETH

            # Also first choice on the list
            self.chosen_address_to_list = (
                self.swap_token_detail['address'][self.network][0]
            )

            self.index1 = 0
            self.index2 = 0
            self.to_token_decimals = 0
            self.eth_price_ = get_eth_price()
            self.__gas = 0.0
            self.in_price = self.eth_price_
            self.out_price = self.eth_price_
            self.out_symbol = 'WETH'

            self.min_amount_out = 0.0

            if float(self.in_price) > 0.0:
                self.min_amount_out = (
                    float(self.in_price)
                    / float(self.out_price)
                )

            self.swap_amount = QLineEdit(self.box4)
            self.swap_amount.resize(480, 44)
            self.swap_amount.move(280, 376)
            self.swap_amount.setPlaceholderText(
                'Amount to swap (minimum value of $9)'
            )

            validator = QtGui.QDoubleValidator()
            validator.setBottom(0.0000000000001)
            validator.setDecimals(40)
            validator.setTop(1000000000000)
            validator.setNotation(validator.Notation.StandardNotation)

            self.swap_amount.setValidator(validator)

            self.min_out_lbl = QLabel(
                text=(
                    '<u>Rate:</u> 1 ETH = '
                    + f"~{str(self.min_amount_out)[:14]} WETH"
                ),
                parent=self.box4
            )
            self.min_out_lbl.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.min_out_lbl.resize(500, 44)
            self.min_out_lbl.move(320, 430)

            self.total_fee_lbl = QLabel(self.box4)
            self.total_fee_lbl.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.total_fee_lbl.resize(500, 44)
            self.total_fee_lbl.move(320, 476)

            self.min_received = QLabel(self.box4)
            self.min_received.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.min_received.resize(500, 44)
            self.min_received.move(320, 522)
            self.min_received.hide()

            def get_exchange_rate():
                item = self.index1

                if item != 0:
                    from_token_contract = create_contract(
                        self.chosen_address_from_list,
                        chain=self.network
                    )

                    from_token_decimals = (
                        from_token_contract
                        .functions
                        .decimals()
                        .call()
                    )

                    from_token_symbol = \
                        prog.asset[self.network]['symbol'][self.index1-1]

                    if self.index2 == 0:
                        self.chosen_address_to_list = \
                            self.swap_token_detail['address'][self.network][0]

                    to_token_contract = create_contract(
                        self.chosen_address_to_list,
                        chain=self.network
                    )

                    to_token_symbol = (
                        to_token_contract
                        .functions
                        .symbol()
                        .call()
                    )

                    self.in_price = get_price(
                        from_token_symbol
                    )

                    self.out_price = get_price(
                        to_token_symbol
                    )

                    self.min_amount_out = (
                        (
                            float(self.in_price)
                            / float(self.out_price)
                        )
                    )

                    mao = rm_e_notation(self.min_amount_out)

                    self.min_out_lbl.setText(
                        f"<u>Rate:</u> 1 {from_token_symbol.upper()} = "
                        + f"~{mao[:14]} "
                        + to_token_symbol.upper()
                    )

                    self.out_symbol = to_token_symbol

                    amount_received()

                else:
                    to_token_contract = create_contract(
                        self.chosen_address_to_list,
                        chain=self.network
                    )

                    to_token_symbol = (
                        to_token_contract
                        .functions
                        .symbol()
                        .call()
                    )

                    price_of_in_token = get_eth_price()

                    price_of_out_token = get_price(
                        to_token_symbol
                    )

                    self.min_amount_out = (
                        (
                            float(price_of_in_token)
                            / float(price_of_out_token)
                        )
                    )

                    mao = rm_e_notation(self.min_amount_out)

                    self.min_out_lbl.setText(
                        '<u>Rate:</u> 1 ETH = '
                        + f"~{mao[:14]} "
                        + to_token_symbol.upper()
                    )

                    self.out_symbol = to_token_symbol.upper()

                    amount_received()

            def amount_received():
                amount_to_send = self.swap_amount.text()

                if (
                    len(amount_to_send) == 0
                    and len(self.min_received.text()) != 0
                ):
                    self.min_out_lbl.hide()
                    self.min_received.hide()
                    self.total_fee_lbl.hide()

                if (
                    not amount_to_send.startswith('.')
                    and len(amount_to_send) != 0
                ):
                    self.min_out_lbl.show()
                    self.min_received.show()
                    self.total_fee_lbl.show()

                    amount_to_send = float(amount_to_send)

                    fee = amount_to_send * 0.003
                    fee = rm_e_notation(fee)

                    __gas = 0.0

                    if prog.chain == 'eth':
                        __gas = float(w3.eth.gas_price)

                    elif prog.chain == 'base':
                        __gas = float(base_w3.eth.gas_price)

                    __gas *= 500_000
                    __gas /= 10**18
                    __gas = round(__gas, 11)

                    if not self.uniswap.has_permit2_allowance(
                        self.chosen_address_from_list
                    ):
                        __gas *= 2

                    __gas = rm_e_notation(__gas)
                    print(__gas)

                    if self.index1 != 0:
                        symbol = (
                            prog.asset[self.network]
                            ['symbol']
                            [self.index1-1]
                            .upper()
                        )

                        self.total_fee_lbl.setText(
                            '<u>Fee</u>: '
                            + fee[:10]
                            + f" {symbol}"
                            + f" + {__gas} ETH (gas)"
                        )

                    else:
                        self.total_fee_lbl.setText(
                            '<u>Fee</u>: '
                            + f"{fee[:10]} ETH "
                            + f"{__gas} ETH (gas)"
                        )

                    amount_to_send = float(amount_to_send)
                    amount_to_send *= self.min_amount_out

                    if amount_to_send < 0:
                        amount_to_send =- amount_to_send*2

                    amount_to_send = rm_e_notation(
                        amount_to_send
                    )

                    if self.index2 != 0:
                        self.min_received.setText(
                            '<u>You will receive</u>: ~'
                            + amount_to_send[:14]
                            + f" {self.out_symbol.upper()}"
                        )

                    else:
                        amount_to_send = float(amount_to_send)
                        amount_to_send -= float(fee) - float(__gas)

                        if amount_to_send < 0:
                            amount_to_send =- amount_to_send*2

                        amount_to_send = rm_e_notation(amount_to_send)

                        self.min_received.setText(
                            '<u>You will receive</u>: ~'
                            + amount_to_send[:14]
                            + ' WETH'
                        )

            def get_item_from_list_one(item):
                self.index1 = item

                if item == 0:
                    self.chosen_address_from_list = self.zero_in_hex

                self.chosen_address_from_list = (
                    prog.asset[self.network]
                    ['address']
                    [self.index1-1]
                )

                get_exchange_rate()

                #ger = Thread(target=get_exchange_rate, daemon=True)
                #ger.start()

            def get_item_from_list_two(item):
                self.index2 = item

                self.chosen_address_to_list = (
                    self.swap_token_detail
                    ['address']
                    [self.network]
                    [item]
                )

                get_exchange_rate()

                #ger = Thread(target=get_exchange_rate, daemon=True)
                #ger.start()

                #get_exchange_rate()

            self.execute_swap = QPushButton(
                text=' Swap tokens ',
                parent=self.box4,
                icon=TigerWalletImage.checkmark
            )
            self.execute_swap.resize(200, 44)
            self.execute_swap.setIconSize(QSize(32, 32))
            self.execute_swap.move(524, 576)
            self.execute_swap.setLayoutDirection(
                QtCore.Qt.LayoutDirection.RightToLeft
            )

            def validate_input():
                swap_amount = self.swap_amount.text()

                if len(swap_amount) == 0:
                    errbox('Please enter how many tokens you wish to swap')
                    return

                if not swap_amount.startswith('.'):
                    self.chosen_address_from_list = \
                        w3.to_checksum_address(
                            self.chosen_address_from_list
                        )

                    self.chosen_address_to_list = \
                        w3.to_checksum_address(
                            self.chosen_address_to_list
                        )

                    swap_amount = w3.to_wei(swap_amount, 'wei')

                    min_out = float(self.min_amount_out)
                    min_out -= (min_out * 0.05)
                    min_out = w3.to_wei(min_out, 'wei')

                    swap_tx = self.uniswap.swap(
                        self.chosen_address_from_list,
                        self.chosen_address_to_list,
                        swap_amount,
                        min_out
                    )

                    if swap_tx != 0x0 and swap_tx is not None:
                        self.l = QLabel(
                            text=(
                                'Swap confirmed!\n\n Transaction hash:\n'
                                + f"{swap_tx}\n",
                            ),
                            parent=self,
                        )
                        self.l.resize(520, 240)

                        self.l.setTextInteractionFlags(
                            Qt.TextInteractionFlag.TextSelectableByMouse
                        )
                        self.l.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.l.setStyleSheet(
                            'background: #1e1e1e;'
                            'color: #b0c4de;'
                            'border: 3px solid gray;'
                            'border-radius: 16px;'
                            'font: 21px;'
                        )
                        self.l.show()
                        add_round_corners(self.l)

                        self.l.move(280, 260)

                        self.b = QPushButton(
                            text='Close',
                            parent=self,
                            icon=TigerWalletImage.close_blue
                        )
                        self.b.setStyleSheet(
                            "QPushButton::hover{background-color: #1e1e1e;}"
                        )
                        self.b.resize(180, 44)
                        self.b.setIconSize(QSize(32, 32))
                        self.b.move(448, 444)
                        self.b.clicked.connect(
                            lambda: [
                                self.l.close(),
                                self.b.close(),
                                self.l.deleteLater(),
                                self.b.deleteLater(),
                            ]
                        )
                        self.b.show()
                        return

                else:
                    errbox('Invalid amount')
                    return

            self.execute_swap.clicked.connect(validate_input)
            self.swap_amount.returnPressed.connect(validate_input)
            self.swap_amount.textEdited.connect(amount_received)

            self.close_swap = QPushButton(
                text=' Close',
                parent=self.box4,
                icon=TigerWalletImage.close_blue
            )
            self.close_swap.resize(200, 44)
            self.close_swap.setIconSize(QSize(32, 32))
            self.close_swap.move(310, 576)
            self.close_swap.clicked.connect(
                self.clear_tab4
            )

            self.from_droplist.activated.connect(
                get_item_from_list_one
            )

            self.to_droplist.activated.connect(
                get_item_from_list_two
            )

        # FIFTH button
        # New in v3.1
        def init_robot_window(self):
            self.box5 = QWidget(self)
            self.box5.resize(1050, 700)
            self.box5.move(32, 80)
            self.box5.hide()

            inner_border = QLabel(self.box5)
            inner_border.resize(960, 520)
            inner_border.move(40, 88)
            inner_border.setStyleSheet(
                'background: transparent;'
                'border-radius: 6px;'
                'border: 1px solid #44505f;'
            )

            self.text_area = QTextEdit(self.box5)
            self.text_area.resize(950, 418)
            self.text_area.move(40, 108)
            self.text_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.text_area.setStyleSheet(
                'border-bottom: none;'
                'border-radius: 4px;'
                'color: yellow;'
                'padding-top: 8px;'
                'padding-left: 18px;'
                'font: 16px;'
            )

            prompt_msg_box = QLineEdit(self.box5)
            prompt_msg_box.resize(960, 54)
            prompt_msg_box.move(40, 552)
            prompt_msg_box.setMaxLength(120)
            prompt_msg_box.setStyleSheet(
                'border: 1px solid #44505f;'
                'border-bottom: none;'
                'border-radius: 4px;'
            )

            def bot_reg_txt_color(text):
                    return f"<span style=color:#b0c4de>{text}</span>"

            def bot_good_txt_color(text):
                    return f"<span style=color:#1aff1a>{text}</span>"

            def bot_err_txt_color(text):
                return f"<span style=color:red>{text}</span>"

            def _send(
                asset='',
                to='',
                amount=0,
                chain='eth'
            ) -> str:
                chainId = 1 if prog.chain == 'eth' else 8453
                gas = prog.eth_gas if chain == 'eth' else prog.base_eth_gas
                priority = 0

                if float(gas) == 0.0:
                    if prog.chain == 'eth':
                        gas = w3.eth.gas_price
                        priority = w3.eth.max_priority_fee
                    else:
                        gas = base_w3.eth.gas_price
                        priority = base_w3.eth.max_priority_fee
                else:
                    gas = float(gas) * 10**18

                if prog.chain == 'eth':
                    _eth = float(prog.eth_amount) * 10**18

                    if _eth < gas:
                        self.text_area.append(
                            bot_err_txt_color(
                                'Failed to complete transaction: '
                                'Not enough eth to pay for gas! :('
                            )
                        )
                        return

                elif prog.chain == 'base':
                    _eth = float(prog.base_eth_amount) * 10**18

                    if _eth < gas:
                        self.text_area.append(
                            bot_err_txt_color(
                                'Failed to complete transaction: '
                                'Not enough eth to pay for gas! :('
                            )
                        )
                        return


                if asset != self.zero_in_hex:
                    contract = create_contract(asset, chain=chain)

                    amount *= 10**18

                    transaction = (
                        contract.functions.transfer(to, amount)
                        .build_transaction({
                            "from": prog.account.address,
                            "nonce": w3.eth.get_transaction_count(
                                prog.account.address
                            ),
                            "gas": 23000,
                            "maxFeePerGas": int(gas),
                            "maxPriorityFeePerGas": priority,
                            'chainId': chainId
                        })
                    )

                else:
                    transaction = {
                        "from": prog.account.address,
                        "to": to,
                        "value": int(amount) ,
                        "nonce": w3.eth.get_transaction_count(
                            prog.account.address
                        ),
                        "gas": 23000,
                        "maxFeePerGas": gas,
                        "maxPriorityFeePerGas": priority,
                        'chainId': chainId
                    }

                signed = w3.eth.account.sign_transaction(
                    transaction_dict=transaction,
                    private_key=prog.account.key
                )

                sent_tx = ''

                try:
                    sent_tx = w3.eth.send_raw_transaction(
                        signed.raw_transaction
                    )
                except Exception:
                    self.text_area.append(
                        bot_err_txt_color(
                            'Failed to complete transaction: '
                            'Not enough funds! :('
                        )
                    )
                    return

                tx_hash = w3.eth.wait_for_transaction_receipt(sent_tx)

                if tx_hash['from'] == prog.account.address:
                    self.text_area.append(
                        bot_good_txt_color(
                            'Done!!'
                            'Transaction hash has been copied to your clipboard'
                        )
                    )
                    QApplication.clipboard().setText(sent_tx)


            def __gen_response(txt):
                self.text_area.setEnabled(False)

                import re

                words = re.findall(r'\w+', txt)
                words = [item.lower() for item in words]

                ##==- Check for send command -==##
                if 'send' in words:
                    am_arg_index = words.index('send')
                    am_arg = words[am_arg_index+1]

                    #=- Get amount -=#
                    if am_arg.endswith('k'):
                        am_arg = am_arg[0 : len(am_arg)-1]

                    amount = 0.0

                    try:
                       amount =  float(am_arg)

                       if amount == 0.0:
                            self.text_area.append(
                                bot_err_txt_color(
                                    'Failed to complete transaction : '
                                    'The amount that was specified was 0'
                                )
                            )
                            self.text_area.append('\n')
                            return

                    except Exception:
                        self.text_area.append(
                            bot_err_txt_color(
                                'Failed to complete transaction : '
                                'Amount specified was not a number'
                            )
                        )
                        self.text_area.append('\n')
                        return

                    #=- Get asset -=#
                    asset_arg = words[am_arg_index+2]

                    if asset_arg == 'to':
                        self.text_area.append(
                            bot_err_txt_color(
                                'Failed to complete transaction: '
                                'You forgot to tell me what asset I should send!'
                            )
                        )
                        self.text_area.append('\n')
                        return

                    __symbol = prog.asset[prog.chain]['symbol']
                    __name = prog.asset[prog.chain]['name']

                    if (
                        not asset_arg in __symbol
                        or not asset_arg in __name
                    ):
                        self.text_area.append(
                            bot_err_txt_color(
                                'Failed to complete transaction: '
                                f"'{asset_arg}' was not found in your wallet"
                            )
                        )
                        self.text_area.append('\n')
                        return

                    #=- Get address -=#
                    addr_index = words.index('to')
                    addr = ''

                    if words[addr_index+1] == 'address':
                        addr = words[addr_index+2]
                    else:
                        addr = words[addr_index+1]

                    ens_name = ''

                    if '.eth' in txt:
                        addr += '.eth'

                        try:
                            _ENS =  ENS(web3_provider)
                            addr = _ENS.address(addr)

                        except Exception:
                            self.text_area.append(
                                bot_err_txt_color(
                                    'Robot: Failed to complete transaction: '
                                    "Invalid ENS name"
                                )
                            )
                            self.text_area.append('\n')
                            return

                        if addr == None:
                            self.text_area.append(
                                bot_err_txt_color(
                                    'Robot: Failed to complete transaction: '
                                    'ENS name has expired. '
                                    'Could not find its address'
                                )
                            )
                            self.text_area.append('\n')
                            return

                    #=- Putting it all together -=#
                    if asset_arg != 'eth':
                        __i = ''

                        try:
                            __i = \
                                prog.asset[prog.chain]['symbol'].index(asset_arg)
                        except Exception:
                            __i = \
                                prog.asset[prog.chain]['name'].index(asset_arg)

                        asset = prog.asset[prog.chain]['address'][__i]

                        robot_th = Thread()
                        robot_th.target = _send(
                            asset=asset,
                            to=addr,
                            amount=int(amount),
                            chain=prog.chain
                        )

                        robot_th.start()

                else:
                    self.text_area.append(
                        bot_err_txt_color(
                            'I did not understand your command :('
                        )
                    )
                    return

                self.text_area.setEnabled(True)

            def __set_txt():
                txt = prompt_msg_box.text()

                if len(txt) != 0:
                    self.text_area.append(f"You: {txt} \n")
                    self.text_area.append(
                        bot_reg_txt_color(
                            'Robot: Attempting to complete your transaction... '
                            'Please hold...'
                        )
                    )

                    __gen_response(txt)
                    prompt_msg_box.clear()

            prompt_msg_box.returnPressed.connect(__set_txt)

        # SIXTH button
        def init_addressbook_window(self):
            self.contacts = prog.contactbook

            self.box6 = QWidget(self)
            self.box6.resize(1050, 680)
            self.box6.move(32, 80)
            self.box6.hide()

            self.contactlbl = QLabel("Contact book", self.box6)
            self.contactlbl.resize(1050, 30)
            self.contactlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.contactlbl.move(0, 62)

            self.tip = QLabel(
                text="Double click on a row to copy the contact's address",
                parent=self.box6,
            )
            self.tip.resize(1050, 40)
            self.tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tip.move(0, 98)

            # Table
            # BEGIN
            self.contactbook_sz = len(prog.contactbook["name"])

            self.contact_table = QTableWidget(self.box6)
            self.contact_table.setRowCount(self.contactbook_sz)
            self.contact_table.setColumnCount(2)
            self.contact_table.setColumnWidth(0, 305)
            self.contact_table.setColumnWidth(1, 505)
            self.contact_table.verticalHeader().setVisible(False)
            self.contact_table.horizontalHeader().setVisible(True)
            self.contact_table.resize(1040, 346)
            self.contact_table.move(156, 162)
            self.contact_table.setHorizontalHeaderItem(
                0, QTableWidgetItem("Contact Name")
            )
            self.contact_table.setHorizontalHeaderItem(
                1, QTableWidgetItem("Contact Address")
            )
            self.contact_table.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.contact_table.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )
            self.contact_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.contact_table.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )
            self.contact_table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.contact_table.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.Fixed
            )

            self.contact_table.show()
            self.contact_table.itemDoubleClicked.connect(
                lambda: [
                    QApplication.clipboard().setText(
                        self.contacts["address"][
                            self.contact_table.currentRow()
                        ]
                    ),
                    msgbox("Contact address has been copied!"),
                ]
            )
            # END
            # Table

            self.add_contact = QPushButton(
                text=" Add contact",
                parent=self.box6,
                icon=TigerWalletImage.plus_blue,
            )
            self.add_contact.setFixedSize(240, 40)
            self.add_contact.setIconSize(QSize(32, 32))
            self.add_contact.move(276, 524)
            self.add_contact.show()
            self.add_contact.clicked.connect(self.init_add_contact_window)

            # Remove contact
            self.del_contact = QPushButton(
                text=" Delete contact",
                parent=self.box6,
                icon=TigerWalletImage.delete_blue,
            )
            self.del_contact.setFixedSize(240, 40)
            self.del_contact.setIconSize(QSize(32, 32))
            self.del_contact.move(546, 524)
            self.del_contact.show()
            self.del_contact.clicked.connect(self.init_rm_contact_window)

            self.close_book = QPushButton(
                text=" Close",
                parent=self.box6,
                icon=TigerWalletImage.close_blue
            )
            self.close_book.setFixedSize(200, 52)
            self.close_book.setIconSize(QSize(32, 32))
            self.close_book.move(426, 568)
            self.close_book.clicked.connect(self.clear_tab6)

        # SIXTH button
        def init_history_window(self):
            self.wh = WalletHistory(self)

        # SEVENTH button
        def init_settings_window(self):
            """ Settings window """
            self.s = Settings(self)
        
        # Donation
        def init_donate_window(self):
            self.selected_donobtn_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            self.donation_window_active = True

            self.val.hide()
            self.table.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.dono_msg = QLabel(
                text="If you like my work, buy me a coffee!",
                parent=self
            )

            self.dono_msg.resize(1100, 34)
            self.dono_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dono_msg.move(0, 148)
            self.dono_msg.show()

            self.dono_addrs = [
                # BTC
                "bc1q0twjllj6wae3uxawe6h4yunzww7evp9r5l9hpy",
                # ETH
                "0x508547c4Bac880C1f4A2336E39C55AB520d43F59",
                # SOL
                "8TrSGinmesMxQQCJL4eMKP6AfYcbtpiXktpiRtjaG4eQ",
                # LTC
                "ltc1qnn23rwkvw6kv3ryvaeut0k56pk34jktuuyvmlu",
                # TRC-20
                "TJyonFv58FKedY7tryztppuGLKhpZRUHH9",
                # ETC
                "0x7a37a759bec9eD277c113F44Be86DbbFb3707eCe",
                # BCH
                "qqh85dkmpwkfm2lr4yrntjlhwngumnn8ps5x7u0rda",
            ]

            buf_list = [BytesIO() for i in range(7)]

            self.qrs = [
                segno.make(self.dono_addrs[i])
                for i in range(7)
            ]

            [
                self.qrs[i].save(
                    buf_list[i],
                    kind="png",
                    scale=4,
                    border=1
                )
                for i in range(7)
            ]

            self.qr_holders = [QLabel(self) for i in range(7)]
            self.pix = [QPixmap() for i in range(7)]

            [
                self.pix[i].loadFromData(buf_list[i].getvalue())
                for i in range(7)
            ]

            self.qr_holders = [QLabel(self) for i in range(7)]
            [self.qr_holders[i].setPixmap(self.pix[i]) for i in range(7)]

            # QR codes
            self.widg1 = QWidget(self)
            self.widg1.resize(540, 140)
            self.widg1.move(308, 266)
            self.widg1.show()

            self.layout1 = QHBoxLayout()
            self.widg1.setLayout(self.layout1)

            for index in range(0, 3):
                self.layout1.addWidget(self.qr_holders[index])

            self.widg2 = QWidget(self)
            self.widg2.resize(540, 140)
            self.widg2.move(308, 502)
            self.widg2.show()

            self.layout2 = QHBoxLayout()
            self.widg2.setLayout(self.layout2)

            for index in range(3, 6):
                self.layout2.addWidget(self.qr_holders[index])

            # Name of chain row 1
            self.assets_labels = [
                "BTC (SegWit Bench32)",
                "ETH/ARB",
                "SOL",
                "LTC (Not MW)",
                "TRC-20",
                "ETC",
                "BCH (P2PKH)",
            ]

            self.widg3 = QWidget(self)
            self.widg3.resize(540, 52)
            self.widg3.move(286, 190)
            self.widg3.show()
            self.widg3.setStyleSheet("background: transparent;")

            self.layout3 = QHBoxLayout()
            self.widg3.setLayout(self.layout3)

            self.assets_row1 = [
                QLabel(self)
                for label in self.assets_labels
            ]

            for index in range(0, 3):
                self.assets_row1[index].setText(self.assets_labels[index])
                self.assets_row1[index].setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.layout3.addWidget(self.assets_row1[index])
                self.assets_row1[index].setWordWrap(True)
                self.assets_row1[index].resize(50, 74)

                if prog.configs["theme"] == "default_dark":
                    self.assets_row1[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: #627eea;"
                        + "background: transparent;"
                    )

                elif prog.configs["theme"] == "default_light":
                    self.assets_row1[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: black;"
                        + "background: transparent;"
                    )

            self.copyrow1 = [
                QPushButton(
                    parent=self,
                    text=" Copy Address",
                    icon=TigerWalletImage.copy_blue,
                )
                for item in self.assets_labels
            ]

            self.btnwidget1 = QWidget(self)
            self.btnwidget1.resize(540, 36)
            self.btnwidget1.move(286, 226)
            self.btnwidget1.show()

            self.btnlayout1 = QHBoxLayout(self.btnwidget1)

            def connect_copy_to_buttons():
                self.copyrow1[0].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[0]),
                        msgbox("BTC address copied to the copy_blue"),
                    ]
                )

                self.copyrow1[1].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[1]),
                        msgbox("ETH address copied to the copy_blue"),
                    ]
                )

                self.copyrow1[2].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[2]),
                        msgbox("SOL address copied to the copy_blue"),
                    ]
                )

            connect_copy_to_buttons()

            for index in range(0, 3):
                self.btnlayout1.addWidget(self.copyrow1[index])
                self.copyrow1[index].show()

                if prog.configs["theme"] == "default_dark":
                    self.copyrow1[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 4px;"
                        + "font-size: 17px;"
                        + "color: #b0c4de}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

                elif prog.configs["theme"] == "default_light":
                    self.copyrow1[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 4px;"
                        + "font-size: 17px;"
                        + "color: #79829A}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

            self.widg4 = QWidget(self)
            self.widg4.resize(540, 52)
            self.widg4.move(286, 430)
            self.widg4.show()
            self.widg4.setStyleSheet("background: transparent;")

            self.layout4 = QHBoxLayout()
            self.widg4.setLayout(self.layout4)

            self.assets_row2 = [
                QLabel(self)
                for label in self.assets_labels
            ]

            for index in range(3, 6):
                self.assets_row2[index].setText(self.assets_labels[index])
                self.assets_row2[index].setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.layout4.addWidget(self.assets_row2[index])
                self.assets_row2[index].setWordWrap(True)
                self.assets_row2[index].resize(50, 74)

                if prog.configs["theme"] == "default_dark":
                    self.assets_row2[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: #627eea;"
                        + "background: transparent;"
                    )

                elif prog.configs["theme"] == "default_light":
                    self.assets_row2[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: #3c598e;"
                        + "background: transparent;"
                    )

            self.copyrow2 = [
                QPushButton(
                    parent=self,
                    text=" Copy Address",
                    icon=TigerWalletImage.copy_blue,
                )
                for item in self.assets_labels
            ]

            self.btnwidget2 = QWidget(self)
            self.btnwidget2.resize(540, 36)
            self.btnwidget2.move(286, 466)
            self.btnwidget2.show()

            self.btnlayout2 = QHBoxLayout(self.btnwidget2)

            for index in range(3, 6):
                self.btnlayout2.addWidget(self.copyrow2[index])
                self.copyrow2[index].show()

                if prog.configs["theme"] == "default_dark":
                    self.copyrow2[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 4px;"
                        + "font-size: 17px;"
                        + "color: #b0c4de}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

                elif prog.configs["theme"] == "default_light":
                    self.copyrow2[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 4px;"
                        + "font-size: 17px;"
                        + "color: #79829A}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

            # Didn't work when it was looped, so doing it the naive way
            def connect_copy_to_buttons2():
                self.copyrow2[0].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[3]),
                        msgbox("LTC address copied to the copy_blue"),
                    ]
                )

                self.copyrow2[1].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[4]),
                        msgbox("TRC-20 address copied to the copy_blue"),
                    ]
                )

                self.copyrow2[2].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[5]),
                        msgbox("ETC address copied to the copy_blue"),
                    ]
                )

            connect_copy_to_buttons2()

            self.close_dono = QPushButton(
                text=" Close",
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.close_dono.setFixedSize(200, 48)
            self.close_dono.setIconSize(QSize(32, 32))
            self.close_dono.move(448, 656)
            self.close_dono.show()
            self.close_dono.clicked.connect(self.clear_donation_tab)

            if prog.configs["theme"] == "default_dark":
                self.close_dono.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.dono_msg.setStyleSheet(
                    "font-size: 22px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.close_dono.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.dono_msg.setStyleSheet(
                    "font-size: 22px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

        # Add a contact
        # added ENS support in v2.0
        # Displays errors when entering an invalid address in v3.1
        def init_add_contact_window(self):
            self.contactlbl.hide()
            self.add_contact_section2 = True

            self.contact_table.hide()
            self.add_contact.hide()
            self.del_contact.hide()
            self.close_book.hide()
            self.val.hide()
            self.tip.hide()

            txt = (
                "Enter the desired name for your contact.\n"
                "Only enter an ERC-20 address!"
            )

            self.enter_details = QLabel(
                text = txt,
                parent=self,
            )
            self.enter_details.resize(800, 90)
            self.enter_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.enter_details.move(160, 136)
            self.enter_details.show()

            self.cname = QLabel("Name:", self)
            self.cname.resize(200, 39)
            self.cname.move(292, 254)
            self.cname.show()

            # Name
            self.form1 = QLineEdit(self)
            self.form1.resize(430, 38)
            self.form1.move(380, 260)
            self.form1.show()

            self.caddr = QLabel("Address: ", self)
            self.caddr.resize(90, 39)
            self.caddr.move(292, 319)
            self.caddr.show()

            # Address
            self.form2 = QLineEdit(self)
            self.form2.resize(430, 38)
            self.form2.move(380, 320)
            self.form2.setMaxLength(42)
            self.form2.show()

            self.close_add = QPushButton(
                text=" Cancel",
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.close_add.setFixedSize(240, 62)
            self.close_add.setIconSize(QSize(32, 32))
            self.close_add.move(310, 410)
            self.close_add.show()

            def validate_address():
                name = self.form1.text()
                addr = self.form2.text()

                if len(name) == 0:
                    errbox("Empty name")
                    return

                elif len(addr) == 0:
                    errbox("No address was provided")
                    return

                if addr.endswith('.eth'):
                    if addr == '.eth':
                        errbox("Invalid ENS name")
                        return

                    try:
                        ens_address = self.eth_ns.address(a)

                        if ens_address is None:
                            errbox(
                                "This ENS is not registered to any address"
                            )
                            return

                    except Exception:
                        errbox(
                            "Invalid ENS name. Did you type it correctly?"
                        )
                        return

                if not addr.endswith('.eth') and len(addr) < 42:
                    errbox('Invalid address')
                    return

                if len(addr) == 42:
                    if not w3.is_address(addr):
                        errbox('Invalid address')
                        return

                    if prog.chain == 'eth':
                        try:
                            contract = create_contract(addr)
                            contract.functions.symbol.call()

                            errbox(
                                'You are trying to add a '
                                '<u>contract address</u>'
                            )
                            return

                        except Exception:
                            pass

                    elif prog.chain == 'base':
                        try:
                            contract = create_contract(addr, chain='base')
                            contract.functions.symbol.call()

                            errbox(
                                'You are trying to add a '
                                '<u>contract address</u>'
                            )
                            return

                        except Exception:
                            pass

                if (
                    name in self.contacts["name"]
                    or addr in self.contacts["address"]
                ):
                    errbox("A contact with this name already exists")
                    return

                self.add_contact_details(
                    self.form1.text(),
                    self.form2.text()
                )

            self.continue_add = QPushButton(
                text=" Continue",
                parent=self,
                icon=TigerWalletImage.checkmark
            )
            self.continue_add.setFixedSize(240, 62)
            self.continue_add.setIconSize(QSize(32, 32))
            self.continue_add.move(560, 410)
            self.continue_add.show()
            self.continue_add.clicked.connect(validate_address)

            self.close_add.clicked.connect(
                lambda: [
                    self.enter_details.close(),
                    self.cname.close(),
                    self.form1.close(),
                    self.form2.close(),
                    self.caddr.close(),
                    self.close_add.close(),
                    self.continue_add.close(),

                    self.contact_table.show(),
                    self.add_contact.show(),
                    self.del_contact.show(),
                    self.close_book.show(),
                    self.tip.show(),
                    self.contactlbl.hide()
                ]
            )

            if prog.configs["theme"] == "default_dark":
                self.close_add.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.continue_add.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.cname.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #9fb1ca;"
                )

                self.caddr.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #9fb1ca;"
                )

                self.enter_details.setStyleSheet(
                    "font-size: 23px;"
                    + "color: #c5d4e7;"
                    + "background: transparent;"
                )

            elif prog.configs["theme"] == "default_light":
                self.close_add.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.continue_add.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.cname.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #3c598e;"
                )

                self.caddr.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #3c598e;"
                )

                self.enter_details.setStyleSheet(
                    "font-size: 23px;"
                    + "color: #3c598e;"
                    + "background: transparent;"
                )

        #
        def init_rm_contact_window(self):
            """ Remove contact window """
            self.add_contact.hide()
            self.del_contact.hide()
            self.close_book.hide()

            self.add_contact_section3 = True
            self.tip.setText("Select the contact(s) that you want to remove")

            self.contact_table.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection
            )

            self.contact_table.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )

            self.contact_table.itemDoubleClicked.disconnect()

            self.close_rm = QPushButton(
                text=" Cancel",
                parent=self,
                icon=TigerWalletImage.close_blue
            )
            self.close_rm.setFixedSize(240, 62)
            self.close_rm.setIconSize(QSize(32, 32))
            self.close_rm.move(296, 600)
            self.close_rm.show()

            self.continue_rm = QPushButton(
                text=" Continue",
                parent=self,
                icon=TigerWalletImage.checkmark
            )
            self.continue_rm.setFixedSize(240, 62)
            self.continue_rm.setIconSize(QSize(32, 32))
            self.continue_rm.move(566, 600)
            self.continue_rm.show()
            self.continue_rm.clicked.connect(self.rm_contact_details)

            self.close_rm.clicked.connect(
                lambda: [
                    self.continue_rm.close(),
                    self.close_rm.close(),
                    self.contact_table.setSelectionBehavior(
                        QAbstractItemView.SelectionBehavior.SelectItems
                    ),
                    self.contact_table.setSelectionMode(
                        QAbstractItemView.SelectionMode.NoSelection
                    ),
                    self.contact_table.clearSelection(),
                    self.add_contact.show(),
                    self.del_contact.show(),
                    self.close_book.show(),
                    self.contact_table.itemDoubleClicked.connect(
                        lambda: [
                            QApplication.clipboard().setText(
                                self.contacts["address"][
                                    self.contact_table.currentRow()
                                ]
                            ),
                            msgbox("Contact address has been copied!"),
                        ]
                    ),
                    self.tip.setText(
                        "Double click on a row to copy the contact's address"
                    ),
                ]
            )

            if prog.configs["theme"] == 'default_dark':
                self.close_rm.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.continue_rm.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

            elif prog.configs["theme"] == 'default_light':
                self.close_rm.setStyleSheet(
                    "QPushButton{background-color:  transparent;"
                    + "font-size: 20px;"
                    + "color: #3c598e;"
                    + "border-radius: 8px;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.continue_rm.setStyleSheet(
                    "QPushButton{background-color:  transparent;"
                    + "font-size: 20px;"
                    + "color: #3c598e;"
                    + "border-radius: 8px;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                )

        # new in v1.3
        def init_unlock_wallet(self):
            self.opt = 1

            self.unlock_wallet_box = QWidget(self)
            self.unlock_wallet_box.resize(510, 260)
            self.unlock_wallet_box.move(
                294,
                Qt.AlignmentFlag.AlignCenter + 48
            )

            self.unlock_wallet_lbl = QLabel(
                text="Enter your password to unlock your wallet",
                parent=self.unlock_wallet_box,
            )

            self.unlock_wallet_lbl.resize(390, 40)
            self.unlock_wallet_lbl.move(72, 40)

            def unhide():
                if self.opt == 1:
                    self.showhidepass.setIcon(
                        TigerWalletImage.opened_eye_blue
                    )
                    self.unlock_wallet_pbox.setEchoMode(
                        QLineEdit.EchoMode.Normal
                    )
                    self.opt = 0

                elif self.opt == 0:
                    self.showhidepass.setIcon(
                        TigerWalletImage.closed_eye_blue
                    )
                    self.unlock_wallet_pbox.setEchoMode(
                        QLineEdit.EchoMode.Password
                    )
                    self.opt = 1

            self.unlock_wallet_pbox = QLineEdit(self.unlock_wallet_box)
            self.unlock_wallet_pbox.setEchoMode(
                QLineEdit.EchoMode.Password
            )
            self.unlock_wallet_pbox.setPlaceholderText(
                'Enter your password'
            )
            self.unlock_wallet_pbox.resize(386, 36)
            self.unlock_wallet_pbox.move(40, 110)

            self.unlock_wallet_pbox.returnPressed.connect(
                lambda: self.unlock_wallet(
                    self.unlock_wallet_pbox.text()
                )
            )

            self.showhidepass = QPushButton(self.unlock_wallet_box)
            self.showhidepass.setIcon(TigerWalletImage.closed_eye_blue)
            self.showhidepass.setIconSize(QSize(32, 32))
            self.showhidepass.move(444, 111)
            self.showhidepass.clicked.connect(unhide)

            self.unlock_wallet_button = QPushButton(
                text=" Unlock wallet",
                parent=self.unlock_wallet_box,
                icon=TigerWalletImage.pass_blue,
            )

            self.unlock_wallet_button.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.unlock_wallet_button.setFixedSize(220, 46)
            self.unlock_wallet_button.setIconSize(QSize(32, 32))
            self.unlock_wallet_button.move(140, 180)
            self.unlock_wallet_button.clicked.connect(
                lambda: self.unlock_wallet(
                    self.unlock_wallet_pbox.text()
                )
            )

            self.unlock_wallet_box.hide()



        # New in v3.0
        def switch_networks(self):
            #self._kill_threads()

            if prog.chain == 'eth':
                prog.chain = 'base'
                
                #self._start_threads()
                self.switch_network_button.setIcon(
                    TigerWalletImage.base_img
                )

                self.fill_up_table(chain='base')

                #self.fill_up_table(chain='base')

                self.asset_list.clear()
                self.asset_list.insertItem(0, "ETHER (ETH)")
                self.asset_list.setItemIcon(0, TigerWalletImage.eth_img)

                for index in range(len(prog.asset['base']['name'])):
                    self.asset_list.insertItem(
                        index + 1,
                        f"{prog.asset['base']['name'][index].upper()}"
                        f" ({prog.asset['base']['symbol'][index].upper()})"
                    )

                    self.asset_list.setItemIcon(
                        index + 1,
                        QIcon(prog.asset['base']['image'][index])
                    )

                self.update_eth_gas.stop()
                self.update_base_gas.start(500)

                #base_eth_amount = w3.from_wei(
                    #base_w3.eth.get_balance(self.address),
                    #"ether"
                #)

                self.estimate_amount.setText(
                    #f"~{rm_e_notation(base_eth_amount)[:18]} ETH"
                    f"~{rm_e_notation(prog.base_eth_amount)[:18]} ETH"
                )

                self.from_droplist.clear()
                self.to_droplist.clear()

                self.from_droplist.insertItem(
                    0,
                    'Ether'
                    + ' (ETH)'
                )
                self.from_droplist.setItemIcon(
                    0,
                    TigerWalletImage.eth_img
                )

                for i in range(len(prog.asset[prog.chain]['name'])):
                    self.from_droplist.insertItem(
                        i+1,
                        prog.asset[prog.chain]['name'][i].upper()
                        + f" ({prog.asset[prog.chain]['symbol'][i].upper()})"
                    )
                    self.from_droplist.setItemIcon(
                        i+1,
                        QIcon(prog.asset[prog.chain]['image'][i])
                    )

                with open(
                    prog.dest_path
                    + 'swap_token_details.json',
                    mode='rb'
                ) as f:
                    file_contents = orjson.loads(f.read())
                    self.swap_token_detail = file_contents

                    for i in range(len(file_contents['name']['base'])):
                        self.to_droplist.insertItem(
                            i,
                            file_contents['name']['base'][i].upper()
                            + f" ({file_contents['symbol']['base'][i].upper()})"
                        )

                        self.to_droplist.setItemIcon(
                            i,
                            QIcon(file_contents['image']['base'][i])
                        )

                #gas = float(base_w3.eth.gas_price)

                #gas *= 500_000
                #gas /= 10**18
                #gas = float(w3.from_wei(gas, 'ether'))

                #self.__gas = gas

                self.swap_amount.clear()
                self.total_fee_lbl.clear()
                self.min_received.clear()

                self.chosen_address_from_list = self.zero_in_hex

                # Also first choice on the list
                self.chosen_address_to_list = (
                    self.swap_token_detail['address']['base'][0]
                )

                self.uniswap = UniSwap()
                self.uniswap.w3 = Web3(
                    Web3.HTTPProvider(
                        prog.configs["rpc"]['base']
                    )
                )

                self.wh = WalletHistory(chain='base', master=self)
                self.eth_ns = ENS(base_web3_provider)
                self.network = 'base'

            elif prog.chain == 'base':
                prog.chain = 'eth'

                self.switch_network_button.setIcon(
                    TigerWalletImage.eth_img
                )

                self.fill_up_table(chain='eth')

                self.asset_list.clear()
                self.asset_list.insertItem(0, "ETHER (ETH)")
                self.asset_list.setItemIcon(0, TigerWalletImage.eth_img)

                for index in range(len(prog.asset['eth']['name'])):
                    self.asset_list.insertItem(
                        index + 1,
                        f"{prog.asset['eth']['name'][index].upper()}"
                        f" ({prog.asset['eth']['symbol'][index].upper()})"
                    )

                    self.asset_list.setItemIcon(
                        index + 1,
                        QIcon(prog.asset['eth']["image"][index])
                    )

                self.update_base_gas.stop()
                self.update_eth_gas.start(500)

                #eth_amount = w3.from_wei(
                    #w3.eth.get_balance(self.address),
                    #"ether"
                #)

                self.estimate_amount.setText(
                    f"~{rm_e_notation(prog.eth_amount)[:18]} ETH"
                )

                self.from_droplist.clear()
                self.to_droplist.clear()

                self.from_droplist.insertItem(
                    0,
                    'Ether'
                    + ' (ETH)'
                )
                self.from_droplist.setItemIcon(
                    0,
                    TigerWalletImage.eth_img
                )

                for i in range(len(prog.asset[prog.chain]['name'])):
                    self.from_droplist.insertItem(
                        i+1,
                        prog.asset[prog.chain]['name'][i].upper()
                        + f" ({prog.asset[prog.chain]['symbol'][i].upper()})"
                    )
                    self.from_droplist.setItemIcon(
                        i+1,
                        QIcon(prog.asset[prog.chain]['image'][i])
                    )

                with open(
                    prog.dest_path
                    + 'swap_token_details.json',
                    mode='rb'
                ) as f:
                    file_contents = orjson.loads(f.read())
                    self.swap_token_detail = file_contents

                    for i in range(len(file_contents['name']['eth'])):
                        self.to_droplist.insertItem(
                            i,
                            file_contents['name']['eth'][i].upper()
                            + f" ({file_contents['symbol']['eth'][i].upper()})"
                        )

                        self.to_droplist.setItemIcon(
                            i,
                            QIcon(file_contents['image']['eth'][i])
                        )

                #gas = float(w3.eth.gas_price)

                #gas *= 500_000
                #gas /= 10**18
                #gas = float(w3.from_wei(gas, 'ether'))

                #self.__gas = gas

                self.swap_amount.clear()
                self.total_fee_lbl.clear()
                self.min_received.clear()

                self.chosen_address_from_list = self.zero_in_hex

                # Also first choice on the list
                self.chosen_address_to_list = (
                    self.swap_token_detail['address']['eth'][0]
                )

                self.uniswap = UniSwap()
                self.uniswap.w3 = Web3(
                    Web3.HTTPProvider(
                        prog.configs["rpc"]['eth']
                    )
                )

                self.wh = WalletHistory(self)
                self.eth_ns = ENS(web3_provider)
                self.network = 'eth'
            
            if prog.configs['currency'] == 'USD':
                self.init_total_balance(0)
            else:
                self.init_total_balance(1)

        def close_add_coin_window(self):
            self.coinaddr.close()
            self.errlbl.close()
            self.contractlbl.close()
            self.coinname.close()
            self.coinnamelbl.close()
            self.coinsym.close()
            self.coinsymlbl.close()
            self.coindec.close()
            self.coindeclbl.close()
            self.continue_add_coin_btn.close()
            self.close_add_coin_btn.close()

            self.add_coin_btn.show()
            self.del_coin_btn.show()
            self.default_coin_btn.show()
            self.table.show()
            self.val.show()
            self.btn_showhide.show()

        # Switched to QTableWidgetItem instead of QlineEdit in v3.1
        def unhide(self):
            items_len = len(prog.asset[prog.chain]['name'])
            
            if self.opt == 1:
                self.btn_showhide.setIcon(
                    TigerWalletImage.opened_eye_blue
                )

                self.opt = 0
                #self.btn_showhide.move(780, 142)
                
                self.val.setText('*' * 26)
                
                text = ''
                
                if prog.chain == 'eth':
                    text = self.eth_amount  
                else:
                    text = prog.base_eth_amount
                    
                self.table.item(0, 1).setText('*' * 26)
                
                for i in range(items_len):
                    self.table.item(i+1, 1).setText('*' * 26)
                        
            elif self.opt == 0:
                self.btn_showhide.setIcon(TigerWalletImage.closed_eye_blue)
                self.opt = 1
                #self.btn_showhide.move(760, 142)
                
                self.table.item(0,1).setText(
                    prog.eth_amount if prog.chain == 'eth'
                    else prog.base_eth_amount
                )
                self.val.setText(self.preserved_val)

                for i in range(items_len):
                    self.table.item(i+1, 1).setText(
                        prog.asset_details['eth']['value'][i][:22]
                    )

        def del_wallet_window(self):
            self.selected_btn1_style()
            self._close_tab(self.tab)

            if self.donation_window_active:
                self.clear_donation_tab()

            self.rm_wallet_tab = True
            self.sidebar_button[0].setEnabled(False)
            self.home_button.setEnabled(True)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.wallet_box = QWidget(self)
            self.wallet_box.resize(990, 570)
            self.wallet_box.move(166, 90)
            self.wallet_box.setStyleSheet(
                'background: transparent;'
            )

            self.rm_wallet_title = QLabel(
                text="Select the wallet that you want to delete",
                parent=self.wallet_box
            )

            self.rm_wallet_title.setMinimumSize(590, 50)
            self.rm_wallet_title.move(80, 62)
            self.rm_wallet_title.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            # Wallet selection
            self.rm_wallet_list = QListWidget(self.wallet_box)
            self.rm_wallet_list.resize(730, 370)
            self.rm_wallet_list.move(20, 110)
            self.rm_wallet_list.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.rm_wallet_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.wallets = []
            
            with open(prog.conf_file, 'r') as f:
                self.wallets = json.load(f)["wallets"]

            for self.wallets in enumerate(self.wallets):
                self.rm_wallet_list.insertItem(*self.wallets)

            for i in range(len(self.wallets)):
                if self.rm_wallet_list.item(i).text() == prog.nameofwallet:
                    self.rm_wallet_list.item(i).setText(
                        self.rm_wallet_list.item(i).text()
                        + " (current)"
                    )

            self.wallet_to_rm = None
            self.rm_wallet_row = 0
            
            if len(self.wallets) == 1:
                errbox(
                    'You only have 1 wallet - nothing to remove, silly'
                )
                return

            # Click event
            def _clicked(item):
                if 'current' in item.text():
                    self.rm_wallet_list.clearSelection()

                    errbox(
                        'Please switch wallets first'
                        ', then delete current wallet'
                    )
                    return

                self.rm_wallet_row = self.rm_wallet_list.row(item)
                self.wallet_to_rm = item.text()

            self.rm_wallet_list.itemClicked.connect(_clicked)

            # Cancel button to return to the grid view
            self.cancel_rm_wallet = QPushButton(
                text=" Cancel",
                parent=self.wallet_box,
                icon=TigerWalletImage.close_blue
            )
            self.cancel_rm_wallet.setFixedSize(244, 62)
            self.cancel_rm_wallet.setIconSize(QSize(32, 32))
            self.cancel_rm_wallet.move(120, 492)

            self.continue_rm_wallet = QPushButton(
                text=" Delete selected wallet",
                parent=self.wallet_box,
                icon=TigerWalletImage.checkmark,
            )
            self.continue_rm_wallet.setFixedSize(244, 62)
            self.continue_rm_wallet.setIconSize(QSize(32, 32))
            self.continue_rm_wallet.move(390, 492)
            self.continue_rm_wallet.clicked.connect(
                lambda: self.rm_wallet(self.wallet_to_rm)
            )

            self.cancel_rm_wallet.clicked.connect(
                self.clear_rm_wallet_tab
            )

            if prog.configs['theme'] == 'default_dark':
                self.cancel_rm_wallet.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.continue_rm_wallet.setStyleSheet(
                    "QPushButton::hover{background-color: #1e1e1e;}"
                )

                self.rm_wallet_title.setStyleSheet(
                    "font-size: 25px;"
                    + "color: #627eea;"
                    + 'border: 0px;'
                    + "background: transparent;"
                )

            elif prog.configs['theme'] == 'default_light':
                self.cancel_rm_wallet.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.continue_rm_wallet.setStyleSheet(
                    "QPushButton::hover{background-color: #ced7e9;}"
                )

                self.rm_wallet_title.setStyleSheet(
                    "font-size: 25px;"
                    + "color: #627eea;"
                    + 'border: 0px;'
                    + "background: transparent;"
                )

            self.wallet_box.show()

        def rm_wallet(self, wallet):
            resp = questionbox(
                'Are you sure that you want delete this wallet?'
                + ' <u>THIS ACTION CANNOT BE UNDONE</u>! '
                + "Please make sure that you have this wallet's private key"
                + ' and mnemonic phrase'
            )

            if resp:
                __row = self.rm_wallet_row

                with open(prog.conf_file, mode='w') as f:
                    del prog.configs['wallets'][__row]

                    json.dump(
                        obj=prog.configs,
                        fp=f,
                        indent=4
                    )
                
                self.rm_wallet_list.takeItem(__row)

                msgbox(
                    f"Wallet {prog.nameofwallet} deleted successfully"
                )

                self.wallet_box.close()
                self.wallet_box.deleteLater()
                self.rm_wallet_title.close()

                self.sidebar_button[0].setEnabled(True)
                self.default_btn1_style()

                self.table.show()
                self.val.show()
                self.add_coin_btn.show()
                self.default_coin_btn.show()
                self.del_coin_btn.show()

            elif not resp:
                return

        def clear_main_table(self, chain=prog.chain):
            sz = len(prog.asset[chain]["name"])

        # new in v1.3
        def black_out_window(self):
            self.button_box.hide()
            self.border.hide()
            self.lock_wallet_button.hide()
            self.donation_button.hide()
            self.switch_network_button.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            if self.tab == 0:
                if self.donation_window_active:
                    self.default_donobtn_style()
                    self.donation_button.setEnabled(True)
                    self.close_dono.close()
                    self.dono_msg.close()

                    self.widg1.close()
                    self.widg2.close()
                    self.widg3.close()
                    self.widg4.close()
                    self.btnwidget1.close()
                    self.btnwidget2.close()
                    self.layout1.deleteLater()
                    self.layout2.deleteLater()
                    self.layout3.deleteLater()
                    self.layout4.deleteLater()

                elif self.rm_wallet_tab:
                    self.clear_rm_wallet_tab()

                elif self.rmcointab:
                    self.clear_rm_coin_tab()

                self.table.hide()
                self.val.hide()
                self.add_coin_btn.hide()
                self.default_coin_btn.hide()
                self.del_coin_btn.hide()
                self.button_box.hide()

            def _hide_box(box):
                tabs = {
                    1: self.box1.hide,
                    2: self.box2.hide,
                    3: self.box3.hide,
                    4: self.box4.hide,
                    5: self.box5.hide,
                    6: self.box6.hide
                }

                if box != 0:
                    return tabs[box]()

            _hide_box(self.tab)

        # new in v1.3
        def unlock_wallet(self, password):
            if len(password) == 0:
                errbox('Please enter your password to unlock your wallet')
                return

            with open(prog.nameofwallet, "rb") as f:
                try:
                    Account.decrypt(
                        orjson.loads(f.read()),
                        password
                    )
                except ValueError:
                    errbox("Invalid password")
                    return

            self.unlock_wallet_box.hide()
            self.unlock_wallet_pbox.clear()

            if prog.configs["theme"] == "default_dark":
                self.setStyleSheet('background: #0a0f18;')

            elif prog.configs["theme"] == "default_light":
                self.setStyleSheet('background: #eff1f3;')

            self.button_box.show()
            self.border.show()
            self.lock_wallet_button.show()
            self.donation_button.show()
            self.switch_network_button.show()
            self.currency_box.show()
            self.btn_showhide.show()

            if self.tab == 0:
                if self.donation_window_active:
                    self.init_donate_window()

                self.table.show()
                self.val.show()
                self.border.show()
                self.add_coin_btn.show()
                self.default_coin_btn.show()
                self.del_coin_btn.show()
                self.button_box.show()
                self.lock_wallet_button.show()

            elif self.tab == 1:
                self.box1.show()

            elif self.tab == 2:
                self.box2.show()

            elif self.tab == 3:
                self.box3.show()

            elif self.tab == 4:
                self.box4.show()

        def start_afk_timer(self, afk_time=900000):
            self.afk_time = afk_time

            if afk_time == None:
                return

            self.afk_timer.start(afk_time)

        # Wallet menu
        def show_tab1(self):
            self.selected_btn1_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.donation_window_active:
                self.clear_donation_tab()

            elif self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            elif self.add_contact_section2:
                self.clear_add_contact_details()

            self.tab = 1
            self.sidebar_button[0].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.box1.show()

        # Send
        def show_tab2(self):
            self.selected_btn2_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.donation_window_active:
                self.clear_donation_tab()

            elif self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            elif self.add_contact_section2:
                self.clear_add_contact_details()

            self.tab = 2
            self.sidebar_button[1].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.box2.show()

        # Receive
        def show_tab3(self):
            self.selected_btn3_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.donation_window_active:
                self.clear_donation_tab()

            elif self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            elif self.add_contact_section2:
                self.clear_add_contact_details()

            self.tab = 3
            self.sidebar_button[2].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.box3.show()

        # Swap
        def show_tab4(self):
            self.selected_btn4_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.donation_window_active:
                self.clear_donation_tab()

            elif self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            elif self.add_contact_section2:
                self.clear_add_contact_details()

            self.tab = 4
            self.sidebar_button[3].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.box4.show()

        # Robot
        def show_tab5(self):
            self.selected_btn5_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.donation_window_active:
                self.clear_donation_tab()

            elif self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            elif self.add_contact_section2:
                self.clear_add_contact_details()

            self.tab = 5
            self.sidebar_button[4].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.box5.show()

        # Address book
        def show_tab6(self):
            self.selected_btn6_style()
            self._close_tab(self.tab)
            self.home_button.setEnabled(True)

            if self.donation_window_active:
                self.clear_donation_tab()

            elif self.rm_wallet_tab:
                self.clear_rm_wallet_tab()

            elif self.rmcointab:
                self.clear_rm_coin_tab()

            elif self.add_contact_section2:
                self.clear_add_contact_details()

            self.tab = 6
            self.sidebar_button[5].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.btn_showhide.hide()
            self.currency_box.hide()

            self.box6.show()

        # History
        def show_tab7(self):
            self.default_btn7_style()
            self.stacked_layout.setCurrentIndex(1)
            self.sidebar_button[6].setEnabled(False)
         
        # Settings
        def show_tab8(self):
            self.default_btn8_style()
            self.stacked_layout.setCurrentIndex(2)
            self.sidebar_button[7].setEnabled(False)

        ## Applies default_dark theme
        def apply_default_dark_theme(self):
            self.setStyleSheet(
                ":enabled {background-color: #0a0f18;}"
                ":disabled {background: black;}"
            )

            self.init_sidebar_style()

            self.btn_showhide.setStyleSheet(
                "QPushButton{background-color:  transparent;"
                + "border-radius: 8;}"
                + "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.add_coin_btn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.default_coin_btn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.del_coin_btn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.cancel.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.continue_btn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.closebtn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.add_contact.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.del_contact.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.close_book.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.execute_swap.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.close_swap.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.paste_addr.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
                + 'QPushButton::menu-indicator{image: none;}'
            )

            self.errlabel.setStyleSheet(
                "font-size: 17px;"
                + "color: red;"
                + "background: transparent;"
            )

            self.close_send_btn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.send_btn.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.val.setStyleSheet(
                "font-size: 25px;"
                + "color: #627eea;"
                + 'border: 0px;'
                + "background: transparent;"
            )
            
            self.change_wallet_title.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: #0a0f18;"
            )

            self.addr.setStyleSheet("font-size: 15px;")

            self.receive.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: #0a0f18;"
            )

            self.label.setStyleSheet(
                "font-size: 18px;"
                + "color: #c5d4e7;"
                + "background: #0a0f18;"
            )

            self.copy_address.setStyleSheet(
                "QPushButton::hover{background-color: #1e1e1e;}"
            )

            self.contactlbl.setStyleSheet(
                "font-size: 25px;"
                + "color: #627eea;"
                + "background: #0a0f18;"
            )

            self.tip.setStyleSheet(
                "font-size: 20px;"
                + "color: #c5d4e7;"
                + "background: transparent;"
            )

            self.topmsglabel.setStyleSheet(
                "font-size: 22px;"
                + "color: #b0c4de;"
                + "background: transparent;"
            )

            self.sendlabel.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: #0a0f18;"
            )

            self.assetlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

            self.estimate_amount.setStyleSheet(
                "font-size: 17px;"
                + "color: #c5d4e7;"
                + "background: transparent;"
            )

            self.swap_title.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: transparent;"
            )

            fix_white_borders([
                self.asset_list,
                self.from_droplist,
                self.to_droplist,
                self.currency_box
            ])

            self.typeaddr.setStyleSheet(
                "color: #c5d4e7;"
                + "border: 1px solid #1e2b45;;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.sendtolbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

            self.amount.setStyleSheet(
                "color: #c5d4e7;"
                + "border: 1px solid #1e2b45;;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.amountlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

            self.slider.setStyleSheet(
                "color: transparent;"
                + "background: transparent;"
            )

            self.gasfeelbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

            self.gasfee.setStyleSheet(
                "color: #c5d4e7;"
                + "border: 1px solid #1e2b45;;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.lock_wallet_button.setStyleSheet(
               "QPushButton {background-color: transparent;"
                + "border-radius: 36px;}"
                + "QPushButton::hover{background: #1e1e1e;}"
                + 'QPushButton::menu-indicator{image: none;}'
            )

            self.total_fee_lbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

            self.min_out_lbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

            self.min_received.setStyleSheet(
                "font-size: 20px;"
                + "color: #9fb1ca;"
                + "background: transparent;"
            )

        ## Applies default_light theme
        def apply_default_light_theme(self):
            self.setStyleSheet(
                ":enabled {background-color: #eff1f3;}"
                ":disabled {background: black;}"
            )

            self.init_sidebar_style()

            fix_white_borders(
                [
                    self.asset_list,
                    self.from_droplist,
                    self.to_droplist,
                    self.currency_box
                ],
                theme='light'
            )

            self.btn_showhide.setStyleSheet(
                "QPushButton{background-color:  transparent;"
                + "border-radius: 8;}"
                + "QPushButton::hover{background-color: #ced7e9;}"
            )
            
            self.add_coin_btn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.default_coin_btn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.del_coin_btn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.cancel.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.continue_btn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.closebtn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.add_contact.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.del_contact.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.close_book.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.paste_addr.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
                + 'QPushButton::menu-indicator{image: none;}'
            )

            self.errlabel.setStyleSheet(
                "font-size: 17px;"
                + "color: red;"
                + "background: transparent;"
            )

            self.close_send_btn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.send_btn.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.execute_swap.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.close_swap.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.val.setStyleSheet(
                "font-size: 25px;"
                + "color: #627eea;"
                + 'border: 0px;'
                + "background: transparent;"
            )

            self.change_wallet_title.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: #eff1f3;"
            )

            self.addr.setStyleSheet("font-size: 15px;")

            self.receive.setStyleSheet(
                "font-size: 30px;"
                + "color: #627eea;"
                + "background: #eff1f3;"
            )

            self.label.setStyleSheet(
                "font-size: 18px;"
                + "color: #3c598e;"
                + "background: #eff1f3;"
            )

            self.copy_address.setStyleSheet(
                "QPushButton::hover{background-color: #ced7e9;}"
            )

            self.contactlbl.setStyleSheet(
                "font-size: 25px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.tip.setStyleSheet(
                "font-size: 20px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.topmsglabel.setStyleSheet(
                "font-size: 22px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.sendlabel.setStyleSheet(
                "font-size: 30px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.assetlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.estimate_amount.setStyleSheet(
                "font-size: 17px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.swap_title.setStyleSheet(
                "font-size: 30px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )


            self.typeaddr.setStyleSheet(
                "color: #3c598e;"
                + "border: 1px solid #1e2b45;;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.sendtolbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.amount.setStyleSheet(
                "color: #3c598e;"
                + "border: 1px solid #1e2b45;;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.amountlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.slider.setStyleSheet(
                "color: transparent;"
                + "background: transparent;"
            )

            self.gasfeelbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #3c598e;"
                + "background: transparent;"
            )

            self.gasfee.setStyleSheet(
                "color: #3c598e;"
                + "border: 1px solid #1e2b45;;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.lock_wallet_button.setStyleSheet(
               "QPushButton {background-color: transparent;"
                + "border-radius: 36px;}"
                + "QPushButton::hover{background: #ced7e9;}"
            )

        # BEGIN button styles

        ##==Default Styles==##

        # Change wallet
        def default_btn1_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                    + 'QPushButton::menu-indicator{image: none;}'
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[0].setStyleSheet(
                    'QPushButton {background-color: transparent;'
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background-color: #ced7e9;}"
                    + 'QPushButton::menu-indicator{image: none;}'
                )

        # Send
        def default_btn2_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Receive
        def default_btn3_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Swap
        def default_btn4_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Robot
        def default_btn5_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Address book
        def default_btn6_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # History
        def default_btn7_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[6].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[6].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Settings
        def default_btn8_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Donate
        def default_donobtn_style(self):
            if prog.configs["theme"] == "default_dark":
                self.donation_button.setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.donation_button.setStyleSheet(
                    "QPushButton {background-color: transparent;"
                    + "border-radius: 36px;}"
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        ##==Selected Styles==##

        # Wallet settings
        def selected_btn1_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                    + 'QPushButton::menu-indicator{image: none;}'
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                    + 'QPushButton::menu-indicator{image: none;}'
                )

        # Send
        def selected_btn2_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Receive
        def selected_btn3_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Swap
        def selected_btn4_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Robot
        def selected_btn5_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Address book
        def selected_btn6_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # History
        def selected_btn7_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[6].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[6].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Settings
        def selected_btn8_style(self):
            if prog.configs["theme"] == "default_dark":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )

        # Donate
        def selected_donobtn_style(self):
            if prog.configs["theme"] == "default_dark":
                self.donation_button.setStyleSheet(
                    "QPushButton {background-color: #1e1e1e;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #1e1e1e;}"
                )

            elif prog.configs["theme"] == "default_light":
                self.donation_button.setStyleSheet(
                    "QPushButton {background-color: #ced7e9;"
                    + "border-radius: 36px;"
                    + 'border: 1px solid #242A32;}'
                    + "QPushButton::hover{background: #ced7e9;}"
                )
        # END side button styles

        # Fixed BUG in v3.1 where program crashed when changing wallets
        def launch_chosen_wallet(self, wallet):
            if wallet is None:
                errbox("You haven't selected a wallet!")
                return
            
            prog.reserved_nameofwallet = wallet
            prog.switched_wallets = True

            self.close()
            self.vp = ValidatePassword()
            self.vp.show()
            
            return

        # Load up the list
        def fill_up_table(self, chain='eth'):
            #self.table.setCellWidget(0, 1, self.first_amount_cell)
            self.table.setItem(0, 0, QTableWidgetItem(" ETHER (ETH)"))
            
            if chain != 'eth':
                self.table.setItem(
                    0, 1, QTableWidgetItem(self.eth_amount)
                )
            else:
               self.table.setItem(
                   0, 1, QTableWidgetItem(
                       rm_e_notation(prog.base_eth_amount)[:18]
                    )
                )
                               
            self.table.setItem(0, 2, QTableWidgetItem(self.eth_price))
            self.table.item(0, 0).setIcon(TigerWalletImage.eth_img)
            self.table.setRowCount(
                len(prog.asset[chain]['name']) + 1
            )
            self.table.item(0, 0).setSizeHint(QSize(360, 50))
            self.table.item(0, 1).setSizeHint(QSize(294, 50))
            self.table.item(0, 2).setSizeHint(QSize(300, 50))

            self.asset = prog.asset[chain]
            self.value = prog.asset_details[chain]["value"]
            self._tp = prog.asset_details[chain]["price"]

            for pos in range(len(prog.asset[chain]['name'])):
                pos += 1

                asset_name = self.asset['name'][pos-1]
                asset_symbol = self.asset['symbol'][pos-1]

                # Asset name and symbol
                self.table.setItem(
                    pos,
                    0,
                    QTableWidgetItem(
                        f" {asset_name.upper()} ({asset_symbol.upper()})"

                    )
                )

                self.table.item(pos, 0).setIcon(
                    QIcon(self.asset["image"][pos - 1])
                )

                # Amount of asset user holds
                if self.value[pos - 1] != "0.0":
                    self.table.setItem(
                        pos,
                        1,
                        QTableWidgetItem(self.value[pos - 1][:18])
                    )

                else:
                    #self.entry_table_cells[pos-1].setText('0')
                    self.table.setItem(pos, 0,QTableWidgetItem('0'))

                    # Current valuation of asset
                self.table.setItem(
                    pos,
                    2,
                    QTableWidgetItem(self._tp[pos - 1][:18])
                )

                self.table.item(pos, 0).setSizeHint(QSize(360, 50))
                self.table.item(pos, 1).setSizeHint(QSize(294, 50))
                self.table.item(pos, 2).setSizeHint(QSize(300, 50))

            self.table.resizeRowsToContents()

        # Update balance
        def update_balance(self, number):
            num = rm_e_notation(round(number, 14))

            if prog.configs['currency'] == 'USD':
                self.val.setText(f"Balance: ${num}")

            else:
                self.val.setText(f"Balance: {num} ETH")

            if num == '0':
                self.val.setText("Balance: $0.0")

            prog.total_balance = num

        def update_price(self):
            list_size = len(prog.asset[prog.chain]['address'])

            for pos in range(list_size):
                item = QTableWidgetItem(
                    prog.asset_details[prog.chain]["price"][pos]
                )

                self.table.setItem(pos + 1, 2, item)

        def update_eth_price(self, new_price):
            self.table.setItem(
                0,
                2,
                QTableWidgetItem(str(new_price))
            )

        # Add coin function
        def add_coin(
            self,
            chain: str,
            coin_name=None,
            coin_address=None,
            coin_symbol=None,
            invoked_from_worker=False,
        ):
            def get_bal():
                if not invoked_from_worker:
                    contract = create_contract(
                        coin_address,
                        chain=chain
                    )

                    bal = contract.functions.balanceOf(
                        self.address
                    ).call()

                    bal /= 10**18
                    #w3.from_wei(float(bal), 'ether')

                    prog.asset[chain]['address'].append(coin_address)

                    prog.asset_details[chain]["value"].append(
                        rm_e_notation(bal)[:18]
                    )

                    token_image(coin_address, chain=chain)

                    img = (
                        prog.tokenimgfolder
                        + coin_symbol.lower()
                        + ".png"
                    )

                    prog.asset[chain]['image'].append(img)

            price = get_price(coin_symbol)

            if price == "N/A" or price == 0.0:
                price = 'N/A'

            prog.asset_details[chain]['price'].append(price)

            self.table.setRowCount(self.table.rowCount() + 1)


            # Clear table
            self.clear_main_table(chain)

            self.table.setItem(0, 0, QTableWidgetItem(" ETHER (ETH)"))
            self.table.setItem(
                0,
                1,
                QTableWidgetItem(
                    str(
                        prog.eth_amount if chain == 'eth'
                        else prog.base_eth_amount
                    )
                )
            )
            self.table.setItem(0, 2, QTableWidgetItem(self.eth_price))
            self.table.item(0, 0).setIcon(TigerWalletImage.eth_img)

            sz = len(prog.asset[chain]['name'])

            asset_label = [
                f" {prog.asset[chain]['name'][i].upper()}"
                + f" ({prog.asset[chain]['symbol'][i].upper()})"
                for i in range(sz)
            ]

            for i in range(sz):
                self.table.setItem(
                    i + 1,
                    0,
                    QTableWidgetItem(asset_label[i])
                )

                #if not isinstance(self.table.item(i + 1, 0), type(None)):
                try:
                    self.table.item(i + 1, 0).setIcon(
                        QIcon(prog.asset[chain]["image"][i])
                    )
                except Exception:
                    pass

                self.table.setItem(
                    i + 1,
                    1,
                    QTableWidgetItem(
                        prog.asset_details[chain]["value"][i]
                    )
                )

                self.table.setItem(
                    i + 1,
                    2,
                    QTableWidgetItem(
                        f"{prog.asset_details[chain]['price'][i]}"
                    ),
                )

            for pos in range(sz):
                self.table.item(pos, 0).setSizeHint(
                    QSize(360, 50)
                )

                self.table.item(pos, 2).setSizeHint(
                    QSize(340, 50)
                )

            with open(prog.assets_json, "w") as f:
                json.dump(
                    obj=prog.asset,
                    fp=f,
                    indent=4
                )

            self.table.resizeRowsToContents()

            if not invoked_from_worker:
                self.coinaddr.close()
                self.errlbl.close()
                self.contractlbl.close()
                self.coinname.close()
                self.coinnamelbl.close()
                self.coinsym.close()
                self.coinsymlbl.close()
                self.coindec.close()
                self.coindeclbl.close()
                self.continue_add_coin_btn.close()
                self.close_add_coin_btn.close()

                self.add_coin_btn.show()
                self.del_coin_btn.show()
                self.default_coin_btn.show()
                self.table.show()

        # Remove coin function
        # Found a BUG here (from before v3.1) that caused crashes
        def rm_coin(self):
            chain = 'eth' if prog.chain == 'eth' else 'base'

            ind = self.table.selectionModel().selectedRows()
            amount_rows_selected = len(ind)

            model = self.table.model()

            if amount_rows_selected == 0:
                errbox("No coin was selected")
                return

            if 0 in ind:
                errbox("Ether cannot be removed")
                self.table.clearSelection()
                return

            # Get tokens' value(s)
            removed_items_value = (
                [
                    self.table.itemFromIndex(
                        model.index(ind[i].row(), 1)
                    )
                    for i in range(amount_rows_selected)
                ]
            )

            # Get tokens' price(s)
            removed_items_price = (
                [
                    self.table.itemFromIndex(
                        model.index(ind[i].row(), 2)
                    )
                    for i in range(amount_rows_selected)
                ]
            )

            amount_to_deduct = [
                float(amount.text())
                * float(price.text()) if not ' N/A' else 0.0
                for amount in removed_items_value
                for price in removed_items_price
            ]

            current_balance = float(
                self.val.text()[10:len(self.val.text())]
            )

            for item in amount_to_deduct:
                current_balance -= item

            current_balance = rm_e_notation(
                round(current_balance, 14)
            )

            self.val.setText(
                f"Balance: ${current_balance}"
            )

            # https://stackoverflow.com/questions/37786299how-to-delete-row-rows-from-a-qtableview-in-pyqt/
            for row in reversed(sorted(ind)):
                self.table.removeRow(row.row())

                del prog.asset[chain]['address'][row.row() - 1]
                del prog.asset[chain]['name'][row.row() - 1]
                del prog.asset[chain]['symbol'][row.row() - 1]
                del prog.asset[chain]['image'][row.row() - 1]

                del prog.asset_details[chain]['value'][row.row() - 1]
                del prog.asset_details[chain]['price'][row.row() - 1]

            with open(prog.assets_json, "w") as f:
                json.dump(
                    obj=prog.asset,
                    fp=f,
                    indent=4
                )

            msgbox("Deletion complete")

            self.rm_coin_continue.close()
            self.rm_coin_cancel.close()
            self.uppermsg.close()
            self.table.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )

            self.thread.start()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.val.show()

        def restore_default_coins(self):
            if prog.chain == 'eth':
                if prog.asset['eth']['address'] == prog.addresses:
                    errbox("List is the same as the default list")
                    return

            elif prog.chain == 'base':
                if prog.asset['base']['address'] == prog.addresses:
                    errbox("List is the same as the default list")
                    return

            text = (
                "This will restore the asset list to"
                + 'the default state. Continue?'
            )


            self.res = questionbox(text)

            if not self.res:
                return

            self.called_restore_default_coins = True

            """
                This is the cheap way of doing this,
                but it works fine, so I'll keep it this way, for now
            """
            prog.asset = prog.asset_default

            self.alb = AssetLoadingBar()
            self.alb.show()
            self.deleteLater()
            self.close()

            with open(prog.assets_json, mode='w') as f:
                json.dump(
                    obj=prog.asset_default,
                    fp=f,
                    indent=4
                )

        # Add contact details
        def add_contact_details(
            self,
            name: str,
            addr: str
        ):
            self.contacts["name"].append(name)
            self.contacts["address"].append(addr)
            self.size = len(self.contacts["name"]) - 1

            self.contact_table.insertRow(self.size)
            self.contact_table.setItem(self.size, 0, QTableWidgetItem(name))
            self.contact_table.setItem(self.size, 1, QTableWidgetItem(addr))


            msgbox("Contact added successfully!")

            self.cname.close(),
            self.caddr.close(),
            self.form1.close(),
            self.form2.close(),
            self.close_add.close(),
            self.continue_add.close(),
            self.enter_details.close(),
            self.contact_table.show(),
            self.add_contact.show(),
            self.del_contact.show()
            self.close_book.show()
            self.tip.show()

        def rm_contact_details(self):
            self.ind2 = self.contact_table.selectionModel().selectedRows()

            if len(self.ind2) == 0:
                errbox("No contact was selected")
                return

            for row in reversed(sorted(self.ind2)):
                self.contact_table.removeRow(row.row())
                del self.contacts["name"][row.row()]
                del self.contacts["address"][row.row()]

            msgbox("Contacts have been removed successfully")
            self.continue_rm.close()
            self.close_rm.close()
            self.contact_table.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectItems
            )
            self.contact_table.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )
            self.contact_table.clearSelection()
            self.add_contact.show()
            self.del_contact.show()
            self.close_book.show()

            with open(prog.contactsjson, "w") as f:
                json.dump(self.contacts, f, indent=4)

            self.contact_table.itemDoubleClicked.connect(
                lambda: [
                    QApplication.clipboard().setText(
                        self.contacts["address"][
                            self.contact_table.currentRow()
                        ]
                    ),
                    msgbox("Contact address has been copied!"),
                ]
            )

        # wallet
        def clear_tab1(self):
            self.default_btn1_style()
            self.sidebar_button[0].setEnabled(True)
            self.home_button.setEnabled(False)

            self.box1.hide()
            #self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0
            return

        # Send
        def clear_tab2(self):
            self.default_btn2_style()
            self.sidebar_button[1].setEnabled(True)
            self.home_button.setEnabled(False)

            self.box2.hide()
            #self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0
            return

        # Receive
        def clear_tab3(self):
            self.default_btn3_style()
            self.sidebar_button[2].setEnabled(True)
            self.home_button.setEnabled(False)

            self.box3.hide()
            #self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0
            return

        # Swap
        def clear_tab4(self):
            self.default_btn4_style()
            self.sidebar_button[3].setEnabled(True)
            self.home_button.setEnabled(False)
            self.box4.hide()

            #self._start_threads()
            self.table.show()
            self.val.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0

        # Robot
        def clear_tab5(self):
            self.default_btn5_style()
            self.sidebar_button[4].setEnabled(True)
            self.home_button.setEnabled(False)

            self.box5.hide()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0

        # Address book
        def clear_tab6(self):
            self.default_btn6_style()
            self.sidebar_button[5].setEnabled(True)
            self.home_button.setEnabled(False)

            self.box6.hide()
            #self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0

        # History
        def clear_tab7(self):
            self.default_btn7_style()
            self.sidebar_button[6].setEnabled(True)
            
            self.stacked_layout.setCurrentIndex(0)

        # Settings
        def clear_tab8(self):
            self.default_btn8_style()
            self.sidebar_button[7].setEnabled(True)
            
            self.stacked_layout.setCurrentIndex(0)

        def clear_donation_tab(self):
            self.default_donobtn_style()
            self.donation_button.setEnabled(True)
            self.home_button.setEnabled(False)
            self.close_dono.close()
            self.dono_msg.close()

            self.widg1.close()
            self.widg2.close()
            self.widg3.close()
            self.widg4.close()
            self.btnwidget1.close()
            self.btnwidget2.close()
            self.layout1.deleteLater()
            self.layout2.deleteLater()
            self.layout3.deleteLater()
            self.layout4.deleteLater()

            self.thread.start()
            self.table.show()
            self.val.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.donation_window_active = False
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0

            return

        def clear_rm_wallet_tab(self):
            self.wallet_box.close()
            self.rm_wallet_title.close()
            self.default_btn1_style()
            self.sidebar_button[0].setEnabled(True)
            self.home_button.setEnabled(False)

            self.thread.start()
            self.table.show()
            self.val.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.donation_window_active = False
            self.btn_showhide.show()
            self.currency_box.show()
            self.tab = 0
            return

        def clear_rm_coin_tab(self):
            self.rmcointab = False

            self.uppermsg.hide()
            self.rm_coin_cancel.hide()
            self.rm_coin_continue.hide()
            self.table.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )
            self.home_button.setEnabled(False)

            #self.thread.start()
            self.table.show()
            self.val.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.btn_showhide.show()
            self.currency_box.show()
            self.btn_showhide.show()
            self.tab = 0

        def clear_add_contact_details(self):
            self.enter_details.close(),
            self.cname.close(),
            self.form1.close(),
            self.form2.close(),
            self.caddr.close(),
            self.close_add.close(),
            self.continue_add.close(),

            self.contact_table.show(),
            self.add_contact.show(),
            self.del_contact.show(),
            self.close_book.show(),
            self.tip.show(),
            self.contactlbl.hide()

    # Underlying root
    app = QApplication([])
    app.setWindowIcon(TigerWalletImage.tigerwallet_logo)
    
    # This try/except block is new in v3.1
    if prog.configs['theme'] == 'default_dark':
        try:  
            with open(
                prog.local_path + 'dark.css',
                mode='r',
                encoding="utf-8"
            ) as f:
                app.setStyleSheet(f.read())
        except FileNotFoundError:
            errbox(
                "File 'dark.css' was not found. "
                'Is it in the same directory as tigerwallet?'
            )

    else:
        try:
            with open(
                prog.local_path + 'light.css',
                mode='r',
                encoding="utf-8"
            ) as f:
                app.setStyleSheet(f.read())
        except FileNotFoundError:
            errbox(
                "File 'light.css' was not found. "
                'Is it in the same directory as tigerwallet?'
            )

    json_contents = {}

    with open(prog.conf_file, "r") as f:
        json_contents = json.load(f)

    number_of_wallets = len(json_contents["wallets"])

    if number_of_wallets != 0:
        login = Login()
        login.show()
    else:
        first = FirstWindow()
        first.show()

    updates = CheckForUpdates(
        'https://raw.githubusercontent.com/Serpenseth/'
        + 'TigerWallet/refs/heads/main/pyproject.toml'
    )

    app.exec()

if __name__ == "__main__":
    main()
