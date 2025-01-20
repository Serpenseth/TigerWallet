#!/usr/bin/env python3

""" MIT License
Copyright © 2024 Serpenseth

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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
    QFileDialog,
)

from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize, QThread, QTimer, Qt, pyqtSignal

# os stuff
import os

# time.sleep
import time

# os.path.exists()
import os.path

# Python threading and related
from threading import Thread
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# url stuff
import requests
from requests.adapters import HTTPAdapter

# JSON and ORSON
import json
import orjson

# QR code generator
import segno

# Web3 related
from web3 import Web3
from eth_account import Account

# Required for `Web3.contract` functions
from hexbytes import HexBytes

# Avoid having to save QR codes on device - save in memory instead
from io import BytesIO

import subprocess

# ===Version1.5=== #
def main():
    TigerWalletVersion = "1.5"

    s = requests.Session()
    s.mount(
        "https://",
        HTTPAdapter(
            max_retries=1,
            pool_connections=16,
            pool_maxsize=100
        ),
    )

    # BEGIN functions
    def self_destruct():
        import psutil

        for proc in psutil.process_iter():
            # check whether the process pid matchges
            if proc.pid == os.getpid():
                proc.kill()

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

    def rm_scientific_notation(number: str) -> str:
        """Removes scientific notations, resulting in an actual decimal
        example: 1e-10 becomes 0.0000000001"""
        import numpy

        return numpy.format_float_positional((float(number)), trim="-")

    def percent(percent, number) -> float:
        if number == 0 or percent == 0:
            return 0

        return (percent * number) / 100.0

    # Mnemonic phrase
    def generate_mnemonic_phrase() -> str:
        from mnemonic import Mnemonic

        return Mnemonic("english").generate(strength=128)

    # Rounded corners
    def add_round_corners(window, radius=16):
        """
        Creates curved edges, adding flavor,
        and removes the window's top bar.

        Source:
            https://stackoverflow.com/questions/63804512/pyqt5-mainwindow-hide-windows-border

        Adapted to Pyqt6
        """
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

    # END    functions

    # Variables
    class GlobalVariable:
        def __init__(self):
            self.dest_path = ""

            self.account = type(Account)

            import getpass

            self.current_usr = getpass.getuser()

            if os.name == "nt":
                self.dest_path = "C:/ProgramData/TigerWallet/"

            else:
                self.dest_path = (
                    "/home/"
                    + self.current_usr
                    + "/.TigerWallet/"
                )

            if not os.path.exists(self.dest_path):
                try:
                    os.mkdir(self.dest_path)

                except Exception:
                    """An instance of QApplication must be active for messagebox to appear"""
                    app = QApplication([])

                    errbox(
                        "Fatal error: Could not create TigerWallet folder.\n"
                        + "Make sure that you have write permissions"
                    )

                    quit()

            self.local_path = os.path.dirname(__file__) + "/"
            self.imgfolder = self.local_path + "images/"
            self.tokenimgfolder = self.dest_path + "token_images/"

            if not os.path.exists(self.tokenimgfolder):
                try:
                    os.mkdir(self.tokenimgfolder)

                except Exception:
                    """An instance of QApplication must be active for messagebox to appear"""
                    app = QApplication([])

                    errbox(
                        "Fatal error: Could not create TigerWallet folder.\n"
                        + "Make sure that you have write permissions"
                    )

                    quit()

            # ABI
            self.abi_json_file = self.dest_path + "abi_data.json"
            self.abi = (
                """[{"inputs": [{"internalType":"uint256","name":"_totalSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_address","type":"address"},{"internalType":"bool","name":"_isBlacklisting","type":"bool"}],"name":"blacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"blacklists","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"limited","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxHoldingAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minHoldingAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_limited","type":"bool"},{"internalType":"address","name":"_uniswapV2Pair","type":"address"},{"internalType":"uint256","name":"_maxHoldingAmount","type":"uint256"},{"internalType":"uint256","name":"_minHoldingAmount","type":"uint256"}],"name":"setRule","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]
                    """
            )

            if (
                not os.path.exists(self.abi_json_file)
                or os.stat(self.abi_json_file).st_size == 0
            ):
                # JSON abi file, used for token contracts
                with open(self.abi_json_file, "w") as jsonfile:
                    json.dump(
                        obj=self.abi,
                        indent=4,
                        fp=jsonfile
                    )

            self.conf_file = self.dest_path + "conf.json"
            self.configs = {
                "version": TigerWalletVersion,
                "wallets": [],
                "rpc": "https://ethereum-rpc.publicnode.com",
                "currency": "USD",
                "theme": "default_dark",
            }

            if (
                not os.path.exists(self.conf_file)
                or os.stat(self.conf_file).st_size == 0
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

                    # If version is out of date, update it
                    if self.configs['version'] != TigerWalletVersion:
                        f.close()

                with open(self.conf_file, "w") as f:
                    self.configs['version'] = TigerWalletVersion

                    json.dump(
                        obj=self.configs,
                        indent=4,
                        fp=f
                    )

            self.assets_json = ""
            self.position = 0
            self.is_new = True
            self.nameofwallet = ""
            self.account_addr = ""
            self.filechosen = 0
            self.recovered = 0

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
                    json.dump(self.contactbook, f, indent=4)

            else:
                with open(self.contactsjson, "r") as f:
                    self.contactbook = json.load(f)

            # Contract-related
            self.abi = orjson.loads(
                open(
                    self.abi_json_file,
                    "rb"
                ).read()
            )
            # Asset-related
            self.assets_json = self.dest_path + "assets.json"
            # List of crypto to display #
            self.assets_addr = []
            # Default addresses
            self.addresses = [
                "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "0xB8c77482e45F1F44dE1745F52C74426C631bDD52",
                "0x455e53CBB86018Ac2B8092FdCd39d8444aFFC3F6",
                "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
            ]

            if (
                not os.path.exists(self.assets_json)
                or os.stat(self.assets_json).st_size == 0
            ):
                # If first run or assets_json got messed with
                with open(self.assets_json, "w") as f:
                    json.dump(
                        obj=self.addresses,
                        fp=f,
                        indent=4
                    )

            self.assets_addr = []

            with open(self.assets_json, "r") as f:
                self.assets_addr = json.load(f)

            # Assets details
            self.assets_details = {
                "name": [],
                "symbol": [],
                "image": [],
                "value": [],
                "price": [],
            }

            self.from_experienced = False
            self.opened_from_wallet = False
            self.from_mnemonic = False
            self.from_private_key = False
            self.settings_new_wallet = False

            self.rpc_list = []
            self.rpc_list_file = self.dest_path + "rpc_list.json"

            if (
                not os.path.exists(self.rpc_list_file)
                or os.stat(self.rpc_list_file).st_size == 0
            ):
                # Create RPC list
                with open(self.rpc_list_file, "w") as f:
                    self.rpc_list = [
                        "https://ethereum-rpc.publicnode.com",
                        "https://rpc.mevblocker.io",
                        "https://rpc.mevblocker.io/fast",
                        "https://rpc.ankr.com/eth",
                        "https://rpc.flashbots.net",
                        "https://1rpc.io/eth",
                    ]

                    json.dump(self.rpc_list, f, indent=4)

            else:
                with open(self.rpc_list_file, "r") as f:
                    self.rpc_list = json.load(f)

            # Mnemonic phrase
            Account.enable_unaudited_hdwallet_features()
            self.mnemonic_phrase = generate_mnemonic_phrase()

    globalvar = GlobalVariable()

    # BEGIN Web3-related stuff
    web3_provider = Web3.HTTPProvider(
        endpoint_uri=globalvar.configs["rpc"],
        exception_retry_configuration=None,
        request_kwargs={"timeout": 20, "allow_redirects": False},
        session=s,
    )

    # https://web3py.readthedocs.io/en/v7.6.0/troubleshooting.html#how-can-i-optimize-ethereum-json-rpc-api-access
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
    w3 = Web3(web3_provider)

    def create_contract(address: str) -> w3.eth.contract:
        return w3.eth.contract(
            address=HexBytes(address),
            abi=globalvar.abi
        )

    def token_name(contract: w3.eth.contract) -> str:
        return contract.functions.name.call()

    def token_symbol(contract: w3.eth.contract) -> str:
        return contract.functions.symbol.call()

    def token_balance(contract: w3.eth.contract,
                                    address: str) -> float:
        return contract.functions.balanceOf(address).call()

    def token_image(address) -> None:
        agent = (
            'Mozilla/5.0 (X11; Linux x86_64; rv:131.0)'
            'Gecko/20220911 Firefox/131.0'
        )

        headers = {"User-Agent": agent}
        url = (
            'https://raw.githubusercontent.com/trustwallet/assets/'
            'refs/heads/master/blockchains/ethereum/assets/'
        )

        resp = s.get(
            f"{url}{w3.to_checksum_address(address)}/logo.png",
            headers=headers,
            stream=True,
        )

        if resp.status_code == 404:
            return

        contract = create_contract(address)
        sym = contract.functions.symbol().call()
        sym = sym.lower()

        if os.path.exists(
            globalvar.tokenimgfolder
            + f"{sym}.png"
        ):
            pass

        else:
            with open(
                globalvar.tokenimgfolder
                + f"{sym}.png", "wb"
            ) as out_file:
                out_file.write(resp.content)

    #
    def token_image_from_list(address_list: list) -> None:
        agent = (
            'Mozilla/5.0 (X11; Linux x86_64; rv:131.0)'
            'Gecko/20220911 Firefox/131.0'
        )

        headers = {"User-Agent": agent}
        url = (
            'https://raw.githubusercontent.com/trustwallet/assets/'
            'refs/heads/master/blockchains/ethereum/assets/'
        )

        resp_list = [
            s.get(
                f"{url}{w3.to_checksum_address(address)}/logo.png",
                headers=headers,
                stream=True,
            )
            for address in address_list
        ]

        with w3.batch_requests() as batched:
            for i in range(len(address_list)):
                batched.add(
                    token_symbol(
                        create_contract(address_list[i])
                    )
                )

            batched_symbols = batched.execute()

            for symbol in batched_symbols:
                if os.path.exists(
                    globalvar.tokenimgfolder
                    + f"{symbol}.png"
                ):
                    return

                with open(
                    globalvar.tokenimgfolder + f"{symbol}.png", "wb"
                ) as out_file:
                    for response in resp_list:
                        out_file.write(response.content)


    def get_price(From) -> str:
        """
        Fetches asset price in USDT.

        Currently, this function only converts to USDT.

        This function will undergo changes in the
        future (i.e converting to yen, franc, other crypto, etc)

        if the default url is rate-limiting the user, switch
        to the back-up url. This should suffice, for now.
        """
        backup_url = (
            'https://min-api.cryptocompare.com/data/price?fsym='
            f"{From}&tsyms=USDT"
        )

        default_url = (
            f"https://api.coinbase.com/v2/exchange-rates?currency={From}"
        )

        try:
            page_data = s.get(
                (
                    default_url
                    if not "rate limit" in s.get(default_url).text
                    else backup_url
                ),
                stream=True,
            )
        except ConnectionError:
            return "N/A"

        if "coinbase" in page_data.url:
            if not "USDT" in page_data.json()["data"]["rates"]:
                page_data = s.get(
                    backup_url,
                    stream=True,
                )

                if 'Response' in page_data.json():
                    return 'N/A'

                return rm_scientific_notation(page_data.json()["USDT"])

            return rm_scientific_notation(
                page_data.json()["data"]["rates"]["USDT"]
            )
        else:
            return rm_scientific_notation(page_data.json()["USDT"])

    def get_eth_price() -> str:
        return get_price("ETH")

    def get_price_from_list(symbols: list) -> list:
        url_list = [
            f"https://api.coinbase.com/v2/exchange-rates?currency={symbol}"
            for symbol in symbols
        ]

        page_data_list = [
            s.get(
                url,
                stream=True,
            )
            for url in url_list
        ]

        result_list = []

        for item in page_data_list:
            if not "USDT" in item.json()["data"]["rates"]:
                result_list.append("N/A")
            else:
                result_list.append(item.json()["data"]["rates"]["USDT"])

        '''
        result_list = [
            page_data.json()["data"]["rates"]["USDT"]
            for page_data in page_data_list
        ]
        '''

        return result_list

        '''
        url = "https://min-api.cryptocompare.com/data/price?fsym="
        url += f"USDT&tsyms={','.join(symbols)}"

        try:
            page_data = s.get(
                url,
                stream=True,
            )
        except ConnectionError:
            pass

        result = page_data.json()

        return_result = [item for item in result.values()]

        return return_result
        '''

    # END Web3-related stuff

    # Images
    class TigerWalletImage:
        def __init__(self):
            app = QApplication([])
            self.setup_images()

        def setup_images(self):
            # Eth
            self.eth_img = QIcon(globalvar.imgfolder + "eth.png")

            # Loading background
            self.loading_bg = globalvar.imgfolder + "loading-bg.png"

            self.feelsbad = QIcon(globalvar.imgfolder + "feelsbadman.png")

            """===== https://emojipedia.org/ ===="""

            # Open mouth emoji
            self.shocked_img = QIcon(
                globalvar.imgfolder + "face-with-open-mouth_1f62e.png"
            )

            """===== Icons-8 ===="""
            # Glasses emoji
            self.cool_blue = QIcon(
                globalvar.imgfolder + "icons8-cool-blue.png"
            )

            # Next arrow
            self.continue_ = QIcon(globalvar.imgfolder + "icons8-next-32.png")

            # Back arrow
            self.back = QIcon(globalvar.imgfolder + "icons8-go-back-48.png")

            # Close regular
            self.close = QIcon(globalvar.imgfolder + "icons8-close-32.png")

            # Close blue
            self.close_blue = QIcon(
                globalvar.imgfolder + "icons8-close-blue.png"
            )

            # Close blue2
            self.close_blue2 = QIcon(
                globalvar.imgfolder + "icons8-close-blue2.png"
            )

            # Hide pass image
            self.closed_eye = QIcon(
                globalvar.imgfolder + "icons8-eyes-24-closed.png"
            )

            # Show pass image
            self.opened_eye = QIcon(globalvar.imgfolder + "icons8-eyes-24.png")

            # Clipboard image
            self.clipboard = QIcon(globalvar.imgfolder + "icons8-copy-24.png")

            # Clipboard image blue
            self.copy_blue = QIcon(
                globalvar.imgfolder + "icons8-copy-blue.png"
            )

            # History blue
            self.history_blue = QIcon(
                globalvar.imgfolder + "icons8-history-blue.png"
            )

            self.refresh = QIcon(
                globalvar.imgfolder + "icons8-refresh.png"
            )

            # Swap image blue
            self.swap_blue = QIcon(
                globalvar.imgfolder + "icons8-swap-blue.png"
            )

            # Blue Wallet icon
            self.wallet_blue = QIcon(
                globalvar.imgfolder + "icons8-wallet-blue.png"
            )

            # Address book 1 blue
            self.address_book_blue = QIcon(
                globalvar.imgfolder + "icons8-open-book-blue.png"
            )

            # Send crypto icon
            self.send_blue = QIcon(
                globalvar.imgfolder + "icons8-right-arrow-blue.png"
            )

            # Receive crypto icon
            self.receive_blue = QIcon(
                globalvar.imgfolder + "icons8-left-arrow-blue.png"
            )

            # Delete contact icon
            self.delete = QIcon(
                globalvar.imgfolder + "icons8-cross-50.png"
            )

            # Add contact icon
            self.plus = QIcon(
                globalvar.imgfolder + "icons8-plus-48.png"
            )

            # Settings
            self.settings_blue = QIcon(
                globalvar.imgfolder + "icons8-settings-blue.png"
            )

            # RPC
            self.rpc_blue = QIcon(
                globalvar.imgfolder + "icons8-server-blue.png"
            )

            # Pass
            self.pass_blue = QIcon(
                globalvar.imgfolder + "icons8-password-pass-blue.png"
            )

            # Sun (light mode)
            self.sun_blue = QIcon(
                globalvar.imgfolder + "icons8-sun-blue.png"
            )

            # Moon (dark mode)
            self.moon_blue = QIcon(
                globalvar.imgfolder + "icons8-half-moon-blue.png"
            )

            # Private key
            self.pkey_blue = QIcon(
                globalvar.imgfolder + "icons8-password-key-blue.png"
            )

            # Donation icon
            self.donate_blue = QIcon(
                globalvar.imgfolder + "icons8-donate-blue.png"
            )

            self.about_blue = QIcon(
                globalvar.imgfolder + "icons8-question-mark-bluee.png"
            )

            # Lock
            self.lock_blue = QIcon(
                globalvar.imgfolder + "icons8-lock-blue.png"
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

            if "default" in globalvar.configs["theme"]:
                self.btn1.setStyleSheet(
                    "QPushButton{background-color:  #6495ed;"
                    "border-radius: 8;"
                    "font-size: 20px;"
                    "color: black}"
                    "QPushButton::hover{background-color: #6ca0dc;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton{background-color:  #6495ed;"
                    "border-radius: 8;"
                    "font-size: 20px;"
                    "color: black}"
                    "QPushButton::hover{background-color: #6ca0dc;}"
                )

            # Default theme
            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.label.setStyleSheet("font-size: 40px;" "color: #6495ed;")

                self.label2.setStyleSheet(
                    "font-size: 16px;"
                    "color: #eff1f3;"
                    "border: 2px solid #b0c4de;"
                    "border-radius: 8;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                self.label.setStyleSheet("font-size: 40px; color: #6495ed;")

                self.label2.setStyleSheet(
                    "font-size: 16px;"
                    "color: black;"
                    "border: 2px solid #b0c4de;"
                    "border-radius: 8;"
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
                "Ethereum blockchain. \n You own your crypto assets!"
                "Your private key never leaves this device. \n"
                "Your private key is encrypted."
            )

            self.label2 = QLabel(text=text, parent=self)
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

            self.btn1.setFixedSize(240, 62)
            self.btn1.setIconSize(QSize(28, 28))
            self.btn1.move(38, 216)

        # Experienced user button
        def init_btn2(self):
            self.btn2 = QPushButton(
                text="Import", parent=self, icon=TigerWalletImage.cool_blue
            )

            self.btn2.setFixedSize(266, 62)
            self.btn2.setIconSize(QSize(28, 28))
            self.btn2.move(281, 216)

        def launchwalletname(self):
            globalvar.is_new = True
            self.wn = WalletName()
            self.wn.show()
            self.close()
            self.deleteLater()

        def launchuserwithexperience(self):
            self.uwe = UserWithExperience()
            self.uwe.show()
            self.close()
            self.deleteLater()

    class UserWithExperience(QWidget):
        def __init__(self):
            super().__init__()

            self.init_window()
            self.init_recovery_options()
            self.init_return()
            self.init_continue()

            if "default" in globalvar.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 1px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.ret.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.continue_.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.msg.setStyleSheet(
                    "font-size: 26px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.import_via_pkey.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #eff1f3;"
                    + "border-radius: 16px;"
                )

                self.import_via_phrase.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #eff1f3;"
                    + "border-radius: 16px;"
                )
                self.import_tigw.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #eff1f3;"
                    + "border-radius: 16px;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.msg.setStyleSheet(
                    "font-size: 26px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.import_via_pkey.setStyleSheet(
                    "font-size: 17px;"
                    + "color: black;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 16px;"
                )

                self.import_via_phrase.setStyleSheet(
                    "font-size: 17px;"
                    + "color: black;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 16px;"
                )

                self.import_tigw.setStyleSheet(
                    "font-size: 17px;"
                    + "color: black;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #778ba5;"
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

            text = (
                "Oh, so you have experience, huh?\n"
                "Ok, so what would you like to do?"
            )

            self.msg = QLabel(text=text, parent=self)

            self.msg.resize(440, 140)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(26, 30)

        def init_recovery_options(self):
            self.opt = 0

            secret_phrase_text = "Import from secret phrase (12 words only)"

            # Recovery phrase
            self.import_via_phrase = QRadioButton(
                text=secret_phrase_text,
                parent=self
            )

            self.import_via_phrase.setGeometry(48, 157, 400, 70)
            self.import_via_phrase.toggled.connect(lambda: self._setchoice(1))

            # Recovery key
            self.import_via_pkey = QRadioButton(
                text="Import from private key",
                parent=self
            )

            self.import_via_pkey.setGeometry(48, 226, 400, 70)
            self.import_via_pkey.toggled.connect(lambda: self._setchoice(2))

            # tigw file
            self.import_tigw = QRadioButton(
                text="Import .tigw file",
                parent=self
            )

            self.import_tigw.setGeometry(48, 295, 400, 70)
            self.import_tigw.toggled.connect(lambda: self._setchoice(3))

        def _setchoice(self, choice):
            self.opt = choice

        def init_return(self):
            self.ret = QPushButton(
                text="Return",
                parent=self,
                icon=TigerWalletImage.back
            )

            self.ret.setFixedSize(170, 44)
            self.ret.setIconSize(QSize(28, 28))
            self.ret.move(62, 396)
            self.ret.clicked.connect(self.return_to_first_window)

        def init_continue(self):
            self.continue_ = QPushButton(
                text="Continue",
                parent=self,
                icon=TigerWalletImage.continue_
            )

            self.continue_.setFixedSize(170, 44)
            self.continue_.setIconSize(QSize(28, 28))
            self.continue_.move(262, 396)
            self.continue_.clicked.connect(self.continue_import)

        def continue_import(self):
            if self.opt == 0:
                errbox("No option was selected")
                return

            elif self.opt == 1:
                globalvar.from_experienced = True
                self.rwfp = RecoverWalletFromPhrase()
                self.rwfp.show()
                self.close()
                self.deleteLater()

            elif self.opt == 2:
                globalvar.from_experienced = True
                self.rwfpk = RecoverWalletFromPrivateKey()
                self.rwfpk.show()
                self.close()
                self.deleteLater()

            elif self.opt == 3:
                globalvar.from_experienced = True

                file_chooser = QFileDialog.getOpenFileName(
                    self,
                    "Open a TigerWallet file",
                    globalvar.dest_path,
                    "tigerwallet file (*.tigw)",
                )

                if len(file_chooser[0]) == 0:
                    return

                globalvar.nameofwallet = file_chooser[0]

                self.vp = ValidatePassword()
                self.vp.show()
                self.close()
                self.deleteLater()

        def return_to_first_window(self):
            self.fw = FirstWindow()
            self.fw.show()
            self.close()
            self.deleteLater()

    # Give wallet a name
    class WalletName(QWidget):
        def __init__(self):
            super().__init__()

            self.setup_main()
            self.init_label()
            self.init_name_label()
            self.init_entry()
            self.init_btn1()
            self.init_btn2()

            if "default" in globalvar.configs["theme"]:
                self.btn1.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            # Style
            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")
                self.label.setStyleSheet("font-size: 25px; color: #6495ed;")
                self.n.setStyleSheet("font-size: 17px; color: #eff1f3;")

                self.entry.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")
                self.label.setStyleSheet("font-size: 25px; color: #6495ed;")
                self.n.setStyleSheet("font-size: 17px; color: black;")

                self.entry.setStyleSheet(
                    "color: black;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

        def setup_main(self):
            self.setFixedWidth(580)
            self.setFixedHeight(320)
            self.setWindowTitle("TigerWallet  -  Welcome")
            align_to_center(self)

        # First text in widget
        def init_label(self):
            self.label = QLabel(
                text="Enter a name for your wallet.\nThis name is stored locally!",
                parent=self,
            )

            self.label.resize(580, 62)
            self.label.move(0, 40)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text before entry field
        def init_name_label(self):
            self.n = QLabel("Name:", self)

            self.n.resize(50, 20)
            self.n.move(40, 140)

        # Entry field
        def init_entry(self):
            self.entry = QLineEdit(self)
            self.entry.resize(420, 30)
            self.entry.move(96, 138)
            self.entry.returnPressed.connect(self.continue_)

        # Return button
        def init_btn1(self):
            self.btn1 = QPushButton(
                text=" Return", parent=self, icon=TigerWalletImage.back
            )

            self.btn1.setFixedSize(240, 62)
            self.btn1.setIconSize(QSize(32, 32))
            self.btn1.move(40, 210)
            self.btn1.clicked.connect(self.ret)

        # Continue button

        def init_btn2(self):
            self.btn2 = QPushButton(
                text=" Continue", parent=self, icon=TigerWalletImage.eth_img
            )

            self.btn2.setFixedSize(260, 62)
            self.btn2.setIconSize(QSize(28, 28))
            self.btn2.move(281, 210)
            self.btn2.clicked.connect(self.continue_)

        def continue_(self):
            self.fname = self.entry.text()

            # empty entry field
            if len(self.fname) == 0:
                errbox("Name cannot be empty")
                return

            # name too long
            elif len(self.fname) > 254:
                errbox("Wallet name cannot be longer than 255 characters")
                self.entry.clear()
                return

            elif "\n" in self.fname:
                errbox("character \\n is not allowed")
                self.entry.clear()
                return

            # if directory
            if os.path.isdir(self.fname):
                errbox("'" + self.fname + "' is a directory")
                self.entry.clear()
                return

            if self.fname[0:3] != "C:\\":
                self.tmp = globalvar.dest_path + self.fname
                self.fname = self.tmp

            if self.fname.find(".tigw") != -1:
                globalvar.nameofwallet = self.fname

            else:
                globalvar.nameofwallet = self.fname + ".tigw"

            globalvar.nameofwallet = globalvar.nameofwallet.replace("\\", "/")

            if globalvar.nameofwallet in globalvar.configs["wallets"]:
                errbox("A wallet with that name already exists")
                return

            self.pbox = PassBox()
            self.pbox.show()
            self.close()
            self.deleteLater()

        def ret(self):
            if globalvar.from_mnemonic:
                self.rwfp = RecoverWalletFromPhrase()
                self.rwfp.show()
                self.close()
                self.deleteLater()

            elif globalvar.settings_new_wallet:
                self.uw = UserWallet()
                self.uw.show()
                self.uw.show_tab6_contents()
                self.close()
                self.deleteLater()

            elif globalvar.from_private_key:
                self.rwfpk = RecoverWalletFromPrivateKey()
                self.rwfpk.show()
                self.close()
                self.deleteLater()

            elif not globalvar.opened_from_wallet:
                self.fw = FirstWindow()
                self.fw.show()
                self.close()
                self.deleteLater()

            else:
                self.uw = UserWallet()
                self.uw.show()
                self.close()
                self.deleteLater()

    # Passbox
    class PassBox(QWidget):
        def __init__(self):
            super().__init__()

            self.setup_main()
            self.init_label()
            self.init_password_label()
            self.init_entry()
            self.init_btn()
            self.init_show_pass()
            self.init_entry2()
            self.init_btn2()
            self.init_show_pass2()

            if "default" in globalvar.configs["theme"]:
                self.btn_showhide.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn2_hideshow.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn1.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton{background-color:  #6495ed;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #6ca0dc;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.label2.setStyleSheet(
                    "font-size: 17px;"
                    + "color: #eff1f3;"
                    + "border: 1px solid gray;"
                    + "border-radius: 8;"
                )

                self.n1.setStyleSheet("font-size: 15px; color: #eff1f3;")
                self.n2.setStyleSheet("font-size: 15px; color: #eff1f3;")

                self.entry1.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

                self.entry2.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label2.setStyleSheet(
                    "font-size: 17px;"
                    + "color: black;"
                    + "border: 1px solid gray;"
                    + "border-radius: 8px;"
                )

                self.n1.setStyleSheet("font-size: 15px; color: black;")
                self.n2.setStyleSheet("font-size: 15px; color: black;")

                self.entry1.setStyleSheet(
                    "color: black;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

                self.entry2.setStyleSheet(
                    "color: black;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

        def setup_main(self):
            self.setFixedWidth(650)
            self.setFixedHeight(430)
            self.setWindowTitle("TigerWallet  -  Welcome")
            align_to_center(self)

        def init_label(self):
            self.label = QLabel("Create a password ", self)
            self.label.resize(650, 100)
            self.label.setStyleSheet("font-size: 40px; color: #6495ed;")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_password_label(self):
            # Message box
            self.label2 = QLabel(
                "Enter a password. This password will be used to decrypt your wallet.\n"
                "Your password does NOT leave this device! It is stored locally.\n\n"
                "Because of this, if you forget your password, \nyou'll have to use your recovery key or phrase.",
                parent=self,
            )

            self.label2.resize(580, 130)
            self.label2.move(38, 86)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_entry(self):
            self.opt1 = 1
            self.opt2 = 1

            # Entry field
            self.entry1 = QLineEdit(self)
            self.entry1.resize(390, 30)
            self.entry1.move(170, 230)
            self.entry1.setEchoMode(QLineEdit.EchoMode.Password)

            self.n1 = QLabel("Password:", self)

            self.n1.resize(90, 20)
            self.n1.move(40, 232)

        def init_show_pass(self):
            self.btn_showhide = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye
            )

            self.btn_showhide.setIconSize(QSize(28, 28))
            self.btn_showhide.move(580, 230)
            self.btn_showhide.clicked.connect(self.unhide1)

        def init_entry2(self):
            # Entry2 field
            self.entry2 = QLineEdit(self)
            self.entry2.resize(390, 30)
            self.entry2.move(170, 280)
            self.entry2.setEchoMode(QLineEdit.EchoMode.Password)

            self.n2 = QLabel("Repeat password:", self)

            self.n2.resize(130, 20)
            self.n2.move(40, 282)

            self.btn2_hideshow = QPushButton(
                parent=self,
                icon=TigerWalletImage.closed_eye
            )

        def init_btn(self):
            self.btn1 = QPushButton(
                text="Return",
                parent=self,
                icon=TigerWalletImage.back
            )

            self.btn1.setFixedSize(240, 62)
            self.btn1.setIconSize(QSize(28, 28))
            self.btn1.move(70, 330)
            self.btn1.clicked.connect(self.ret)

        def init_btn2(self):
            self.btn2 = QPushButton(
                text="Continue",
                parent=self,
                icon=TigerWalletImage.continue_
            )

            self.btn2.setFixedSize(240, 62)
            self.btn2.setIconSize(QSize(48, 48))
            self.btn2.move(330, 330)
            self.btn2.clicked.connect(self.check_pass)

        def init_show_pass2(self):
            self.btn2_hideshow.setIconSize(QSize(28, 28))
            self.btn2_hideshow.move(580, 280)
            self.btn2_hideshow.clicked.connect(self.unhide2)

        def ret(self):
            self.wn = WalletName()
            self.wn.show()
            self.close()
            self.deleteLater()

        # BEGIN def unhide1() and unhide2() function
        def unhide1(self):
            if self.opt1 == 1:
                self.btn_showhide.setIcon(TigerWalletImage.opened_eye)
                self.entry1.setEchoMode(QLineEdit.EchoMode.Normal)
                self.opt1 = 0

            elif self.opt1 == 0:
                self.btn_showhide.setIcon(TigerWalletImage.closed_eye)
                self.entry1.setEchoMode(QLineEdit.EchoMode.Password)
                self.opt1 = 1

        def unhide2(self):
            if self.opt2 == 1:
                self.btn2_hideshow.setIcon(TigerWalletImage.opened_eye)
                self.entry2.setEchoMode(QLineEdit.EchoMode.Normal)
                self.opt2 = 0

            elif self.opt2 == 0:
                self.btn2_hideshow.setIcon(TigerWalletImage.closed_eye)
                self.entry2.setEchoMode(QLineEdit.EchoMode.Password)
                self.opt2 = 1

        # END def unhide1() and unhide2() function

        def check_pass(self):
            if self.entry1.text() != self.entry2.text():
                errbox("Passwords did not match")
                return

            elif len(self.entry1.text()) == 0 and len(self.entry1.text()) == 0:
                errbox("Empty passwords are a no no")
                return

            if (
                not globalvar.from_mnemonic
                and not globalvar.from_private_key
            ):
                globalvar.account = Account.from_mnemonic(
                    globalvar.mnemonic_phrase
                )

                self.encrypted = Account.encrypt(
                    globalvar.account.key,
                    password=self.entry1.text()
                )

                with open(globalvar.nameofwallet, "w") as f:
                    f.write(json.dumps(self.encrypted))

                self.mnemonic = MnemonicPhraseWindow()
                self.mnemonic.show()
                self.close()
                self.deleteLater()

            elif globalvar.from_mnemonic:
                self.encrypted = Account.encrypt(
                    globalvar.account.key,
                    password=self.entry1.text()
                )

                with open(globalvar.conf_file, "w") as ff:
                    globalvar.configs["wallets"].append(globalvar.nameofwallet)

                    json.dump(globalvar.configs, ff, indent=4)

                    with open(globalvar.nameofwallet, "w") as f:
                        json.dump(self.encrypted, f)

                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()

            elif globalvar.from_private_key:
                self.encrypted = Account.encrypt(
                    globalvar.account.key, password=self.entry1.text()
                )

                with open(globalvar.conf_file, "w") as ff:
                    globalvar.configs["wallets"].append(globalvar.nameofwallet)
                    json.dump(globalvar.configs, ff, indent=4)

                    with open(globalvar.nameofwallet, "w") as f:
                        json.dump(self.encrypted, f)

                    self.alb = AssetLoadingBar()
                    self.alb.show()
                    self.close()
                    self.deleteLater()

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

            if "default" in globalvar.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn_showhide.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.login.setStyleSheet(
                    "QPushButton{background-color:  #4f86f7;"
                    + "border-radius: 24px;"
                    + "font-size: 23px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #6495ed;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e;")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #1e1e1e;"
                )

                if os.name == "nt":
                    self.selection.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        + "padding: 8px;"
                        + "font: 18px;"
                        + "border-radius: 4px;"
                        + "background: #1e1e1e;"
                        + "color: #b0c4de;}"
                        + "QAbstractItemView {selection-background-color: transparent;"
                        + "color: #b0c4de;"
                        + "border: 2px solid #778ba5;"
                        + "border-radius: 4px;"
                        + "padding: 8px;}"
                    )

                else:
                    self.selection.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        "border-radius: 4px;"
                        "color: #b0c4de;"
                        "font: 18px;}"
                    )

                self.entry.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 16px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.forgotpass.setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "font-size: 20px;"
                    + "border-radius: 0px;"
                    + "color: #778ba5}"
                    + "QPushButton::hover{background-color: #1e1e1e;"
                    + "color: #6495ed;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #eff1f3;"
                )

                if os.name == "nt":
                    self.selection.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        + "padding: 8px;"
                        + "font: 18px;"
                        + "border-radius: 4px;"
                        + "background: #eff1f3;"
                        + "color: black;}"
                        + "QAbstractItemView {selection-background-color: transparent;"
                        + "color: black;"
                        + "border: 2px solid #778ba5;"
                        + "border-radius: 4px;"
                        + "padding: 8px;}"
                    )

                else:
                    self.selection.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        "border-radius: 4px;"
                        "color: black;"
                        "font: 18px;}"
                    )

                self.entry.setStyleSheet(
                    "color: black; "
                    + "font: 16px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.forgotpass.setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "font-size: 20px;"
                    + "border-radius: 0px;"
                    + "color: #778ba5}"
                    + "QPushButton::hover{background-color: #eff1f3;"
                    + "color: #6495ed;}"
                )

        def init_window(self):
            self.setFixedWidth(500)
            self.setFixedHeight(410)
            self.setWindowTitle("TigerWallet  -  Login")
            align_to_center(self)
            self.opt = 1

            self.fp = ForgotPassword()

        # Topmost label
        def init_label(self):
            self.border = QLabel(self)
            self.border.resize(481, 348)
            self.border.move(9, 50)

            self.label = QLabel("Welcome back!!", self)
            self.label.resize(310, 50)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(91, 26)

        def init_wallet_selection(self):
            # TODO: Make last item appear first on the list
            self.selection = QComboBox(self)
            self.selection.resize(448, 50)
            self.selection.move(26, 110)
            self.selection.setAutoFillBackground(True)
            self.shortname = ""

            for i in range(len(globalvar.configs["wallets"])):
                self.shortname = globalvar.configs["wallets"][i]

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

            if os.name != "nt":
                pal = self.selection.palette()

                if globalvar.configs["theme"] == "default_dark":
                    pal.setColor(
                        QtGui.QPalette.ColorRole.ButtonText,
                        QtGui.QColor("#b0c4de"),
                    )

                elif globalvar.configs["theme"] == "default_light":
                    pal.setColor(
                        QtGui.QPalette.ColorRole.ButtonText,
                        QtGui.QColor("black"),
                    )

                self.selection.setPalette(pal)

        def init_passfield(self):
            self.entry = QLineEdit(self)
            self.entry.setPlaceholderText("Enter your password")
            self.entry.move(32, 190)
            self.entry.resize(390, 38)
            self.entry.setEchoMode(QLineEdit.EchoMode.Password)

        def init_eye_btn(self):
            self.btn_showhide = QPushButton(
                text=None, parent=self, icon=TigerWalletImage.closed_eye
            )

            self.btn_showhide.setIconSize(QSize(32, 32))
            self.btn_showhide.move(436, 194)
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
                lambda: [self.fp.show(), self.close(), self.deleteLater()]
            )

        def unhide(self):
            if self.opt == 1:
                self.btn_showhide.setIcon(TigerWalletImage.opened_eye)
                self.entry.setEchoMode(QLineEdit.EchoMode.Normal)
                self.opt = 0

            elif self.opt == 0:
                self.btn_showhide.setIcon(TigerWalletImage.closed_eye)
                self.entry.setEchoMode(QLineEdit.EchoMode.Password)
                self.opt = 1

        def login_to_wallet(self):
            self.choice = globalvar.configs["wallets"][
                self.selection.currentIndex()
            ]

            globalvar.nameofwallet = self.choice

            if len(self.entry.text()) == 0:
                errbox("Password field is empty")
                return

            try:
                with open(self.choice, "r") as f:
                    globalvar.account = Account.from_key(
                        Account.decrypt(
                            json.load(f), password=self.entry.text()
                        )
                    )

                    with open(globalvar.conf_file, "w") as ff:
                        if not self.choice in globalvar.configs["wallets"]:
                            globalvar.configs["wallets"].append(self.choice)

                        json.dump(globalvar.configs, ff, indent=4)

            except ValueError:
                errbox("Incorrect password. Try again")
                return

            if len(globalvar.assets_addr) != 0:
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

            if "default" in globalvar.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 1px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.ret.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.continue_.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #1e1e1e;"
                )

                self.msg.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.phrase_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #eff1f3;"
                    + "border-radius: 16px;"
                )

                self.pkey_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 1px solid #eff1f3;"
                    + "border-radius: 16px;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #eff1f3;"
                )

                self.msg.setStyleSheet(
                    "font-size: 18px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.phrase_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: black;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 16px;"
                )

                self.pkey_recovery.setStyleSheet(
                    "font-size: 18px;"
                    + "color: black;"
                    + "background: transparent;"
                    + "padding: 12px;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 16px;"
                )

        def init_window(self):
            self.setFixedWidth(500)
            self.setFixedHeight(480)
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
            self.msg = QLabel(
                text="It's ok, it happens!\n\n"
                + "Because of the non-custodial nature of this wallet,\n"
                + "TigerWallet cannot recover your password.\n"
                + "You only have the following two options:",
                parent=self,
            )

            self.msg.resize(440, 140)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(26, 88)

        def init_recovery_options(self):
            self.opt = 0

            # Recovery phrase
            self.phrase_recovery = QRadioButton(
                text="Recover account with your recovery phrase", parent=self
            )

            self.phrase_recovery.setGeometry(48, 237, 400, 70)
            self.phrase_recovery.toggled.connect(lambda: self._setchoice(1))

            # Recovery key
            self.pkey_recovery = QRadioButton(
                text="Recover account with your private key", parent=self
            )

            self.pkey_recovery.setGeometry(48, 306, 400, 70)
            self.pkey_recovery.toggled.connect(lambda: self._setchoice(2))

        def init_return(self):
            self.ret = QPushButton(
                text="Return", parent=self, icon=TigerWalletImage.back
            )

            self.ret.setFixedSize(170, 44)
            self.ret.setIconSize(QSize(28, 28))
            self.ret.move(62, 396)
            self.ret.clicked.connect(self.return_to_login)

        def init_continue(self):
            self.continue_ = QPushButton(
                text="Continue", parent=self, icon=TigerWalletImage.continue_
            )

            self.continue_.setFixedSize(170, 44)
            self.continue_.setIconSize(QSize(28, 28))
            self.continue_.move(262, 396)
            self.continue_.clicked.connect(self.continue_recovery)

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
            self.init_table()
            self.init_back()
            self.init_continue()
            self.init_paste_button()

            if "default" in globalvar.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn1.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.paste_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 16px;"
                    + "font-size: 18px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #1e1e1e;"
                )

                self.msg.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                    + "border: 1px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

                self.table.setStyleSheet(
                    "QTableView::item {border-top: 1px solid #eff1f3;"
                    "border-left: 1px solid #eff1f3;"
                    "border-bottom: 1px solid #eff1f3;"
                    "border-right: 1px solid #eff1f3;}"
                    "QTableView {font-size: 15px;"
                    + "background: transparent;"
                    + "color: white;"
                    + "selection-background-color: #363636;"
                    + "selection-color: white};"
                    + "QHeaderView {background: transparent;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #eff1f3;"
                )

                self.msg.setStyleSheet(
                    "font-size: 14px;"
                    + "color: black;"
                    + "background: transparent;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                )

                self.table.setStyleSheet(
                    "QTableView::item {border-top: 1px solid black;"
                    "border-left: 1px solid black;"
                    "border-bottom: 1px solid black;"
                    "border-right: 1px solid black;}"
                    "QTableView {font-size: 15px;"
                    + "background: transparent;"
                    + "color: black;"
                    + "selection-background-color: #363636;"
                    + "selection-color: white};"
                    + "QHeaderView {background: transparent;}"
                )

        def init_window(self):
            self.setFixedWidth(540)
            self.setFixedHeight(500)
            self.setWindowTitle("TigerWallet  -  Recover account")
            align_to_center(self)

        def init_label(self):
            self.border = QLabel(self)
            self.border.resize(521, 426)
            self.border.move(9, 58)

            self.label = QLabel("Account Recovery", self)
            self.label.resize(348, 61)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(98, 26)

        def init_middle_msg(self):
            self.msg = QLabel(
                text="Please enter your 12 secret recovery words (<b>order matters</b>)",
                parent=self,
            )

            self.msg.resize(412, 80)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(63, 110)

        def init_table(self):
            self.table = QTableWidget(self)
            self.table.setRowCount(4)
            self.table.setColumnCount(3)
            self.table.setColumnWidth(0, 140)
            self.table.setColumnWidth(1, 140)
            self.table.setColumnWidth(2, 140)
            self.table.move(58, 220)
            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setVisible(False)
            self.table.setFixedWidth(421)
            self.table.setFixedHeight(122)

            self.table.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.table.setEditTriggers(
                QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers
            )
            self.table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )
            self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.model = self.table.model()

        def init_back(self):
            self.btn1 = QPushButton(
                text=" Return", parent=self, icon=TigerWalletImage.back
            )

            self.btn1.setFixedSize(180, 52)
            self.btn1.setIconSize(QSize(32, 32))
            self.btn1.move(68, 410)
            self.btn1.clicked.connect(self.return_)

        def init_continue(self):
            self.btn2 = QPushButton(
                text=" Continue", parent=self, icon=TigerWalletImage.eth_img
            )

            self.btn2.setFixedSize(180, 52)
            self.btn2.setIconSize(QSize(28, 28))
            self.btn2.move(290, 410)
            self.btn2.clicked.connect(self.continue_)

        def init_paste_button(self):
            self.paste_btn = QPushButton(
                text="Paste recovery phrase",
                parent=self,
                icon=TigerWalletImage.clipboard,
            )

            self.paste_btn.setIconSize(QSize(24, 24))
            self.paste_btn.resize(220, 36)
            self.paste_btn.move(150, 355)
            self.paste_btn.clicked.connect(self.paste_phrase)

        def paste_phrase(self):
            self.clipboard_contents = QApplication.clipboard().text()
            self.p = []
            self.p = self.clipboard_contents.split()

            if len(self.p) < 12:
                errbox("Invalid recovery phrase")
                return

            elif len(self.p) > 12:
                errbox(
                    "Currently, TigerWallet only supports 12-words recovery"
                )
                return

            for i in range(len(self.p)):
                self.table.setItem(0, i, QTableWidgetItem(self.p[i]))

                if i == 3:
                    self.table.setItem(1, i, QTableWidgetItem(self.p[i]))

                elif i == 6:
                    self.table.setItem(2, i, QTableWidgetItem(self.p[i]))

                if i == 9:
                    self.table.setItem(3, i, QTableWidgetItem(self.p[i]))

        def return_(self):
            if not globalvar.from_experienced:
                self.fp = ForgotPassword()
                self.fp.show()
                self.close()
                self.deleteLater()
                return

            globalvar.from_experienced = False
            self.uwe = UserWithExperience()
            self.uwe.show()
            self.close()
            self.deleteLater()

        def continue_(self):
            self.words = []
            self._missing_words = False

            def _is_empty(inp):
                if inp is None:
                    errbox(
                        "Your recovery phrase consists of 12 words; missing words"
                    )
                    self._missing_words = True
                    return True

                elif len(inp) == 0:
                    errbox(
                        "Your recovery phrase consists of 12 words; missing words"
                    )
                    self._missing_words = True
                    return True

                return False

            # https://stackoverflow.com/questions/21280061/get-data-from-every-cell-from-a-qtableview
            for i in range(4):
                for ii in range(self.model.columnCount()):
                    self.index = self.model.index(i, ii)
                    self.word = self.model.data(self.index)

                    if _is_empty(self.word):
                        return

                    self.words.append(self.word)

            if self._missing_words:
                return

            self.w = " ".join(self.words)
            globalvar.mnemonic_phrase = self.w
            globalvar.from_mnemonic = True

            try:
                globalvar.account = Account.from_mnemonic(self.w)

            except Exception:
                errbox("Invalid mnemonic phrase")
                return

            self.walletname = WalletName()
            self.walletname.show()
            self.close()
            self.deleteLater()

    # Recovery from private key
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

            if "default" in globalvar.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 1px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.btn_showhide.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn1.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn2.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #1e1e1e;"
                )

                self.border.setStyleSheet(
                    "border: 1px solid #778ba5;" + "border-radius: 16px;"
                )

                self.msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: white;"
                    + "background: #1e1e1e;"
                )

                self.entry.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 13px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: #eff1f3;"
                )

                self.msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

                self.entry.setStyleSheet(
                    "color: black; "
                    + "font: 13px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

        def init_window(self):
            self.setFixedWidth(580)
            self.setFixedHeight(380)
            self.setWindowTitle("TigerWallet  -  Recover account")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(562, 308)
            self.border.move(9, 58)

            self.opt = 1

        def init_labels(self):
            self.label = QLabel("Account Recovery", self)
            self.label.resize(348, 44)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(120, 36)

            self.msg = QLabel(
                text="Enter your private key to recover your wallet:\n"
                "(With or without the 0x prefix)",
                parent=self,
            )

            self.msg.resize(410, 58)
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.move(86, 100)

        def init_key_entry_field(self):
            self.entry = QLineEdit(self)
            self.entry.setPlaceholderText("Enter your private key")
            self.entry.move(31, 190)
            self.entry.resize(472, 38)
            self.entry.setEchoMode(QLineEdit.EchoMode.Password)

        def init_eye_btn(self):
            self.btn_showhide = QPushButton(
                text=None, parent=self, icon=TigerWalletImage.closed_eye
            )

            self.btn_showhide.setIconSize(QSize(28, 28))
            self.btn_showhide.move(520, 194)
            self.btn_showhide.clicked.connect(self.unhide)

        def init_return_btn(self):
            self.btn1 = QPushButton(
                text=" Return", parent=self, icon=TigerWalletImage.back
            )

            self.btn1.setFixedSize(180, 52)
            self.btn1.setIconSize(QSize(32, 32))
            self.btn1.move(86, 276)
            self.btn1.clicked.connect(self.return_)

        def init_continue_btn(self):
            self.btn2 = QPushButton(
                text=" Continue", parent=self, icon=TigerWalletImage.eth_img
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
                globalvar.account = Account.from_key(self.entry.text())

            except ValueError:
                errbox("Invalid private key")
                return

            globalvar.from_private_key = True

            self.wn = WalletName()
            self.wn.show()
            self.close()
            self.deleteLater()

        def return_(self):
            if not globalvar.from_experienced:
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
        The 12 recovery words that are
        needed to restore the wallet
        """

        def __init__(self):
            super().__init__()

            self.init_window()
            self.init_table()
            self.init_labels()
            self.init_show_recovery_btn()
            self.init_copy_btn()
            self.init_check_box()
            self.init_continue_btn()
            self.init_return_btn()
            # self.init_warning_window()

            self.btnshow.clicked.connect(self.init_warning)
            self.chbox.clicked.connect(self._enablecont)
            self.btncont.clicked.connect(self._startloadingbarclass)
            self.retbtn.clicked.connect(
                lambda: [self.pbox.show(), self.close(), self.deleteLater()]
            )

            if "default" in globalvar.configs["theme"]:
                self.label.setStyleSheet("font-size: 30px; color: #6495ed;")

                self.btnshow.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 16px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btncopy.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 16px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.retbtn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btncont.setStyleSheet(
                    "QPushButton{background-color:  #6495ed;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.label2.setStyleSheet("font-size: 17px; color: #eff1f3;")

                self.table.setStyleSheet(
                    "font-size: 14px;"
                    + "gridline-color: #eff1f3;"
                    + "color: #b0c4de;"
                    + "border: 1px solid #b0c4de;"
                )

                self.chbox.setStyleSheet("color: #eff1f3;")

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.label2.setStyleSheet("font-size: 17px; color: black;")

                self.table.setStyleSheet(
                    "font-size: 14px;"
                    + "gridline-color: black;"
                    + "color: black;"
                    + "border: 1px solid #b0c4de;"
                )

                self.chbox.setStyleSheet("color: black;")

        def init_window(self):
            self.setFixedWidth(650)
            self.setFixedHeight(530)
            self.setWindowTitle("TigerWallet  -  Mnemonic Phrase")
            align_to_center(self)

            self.mphrase = globalvar.mnemonic_phrase
            self.pbox = PassBox()

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
                QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )

            self.blur = QGraphicsBlurEffect(self.table)
            self.blur.setEnabled(True)
            self.blur.setBlurRadius(30)
            self.table.setGraphicsEffect(self.blur)

            self.words = self.mphrase.split()
            self.words_with_index = self.mphrase.split()

            for i, word in enumerate(self.words_with_index):
                self.table.setItem(0, i, QTableWidgetItem(f"{i + 1}) {word}"))

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
            self.label.resize(650, 40)
            self.label.move(0, 40)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.label2 = QLabel("Keep this safe!", self)
            self.label2.resize(650, 20)
            self.label2.move(0, 100)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_show_recovery_btn(self):
            self.btnshow = QPushButton("Show recovery phrase", self)
            self.btnshow.setFixedSize(256, 30)
            self.btnshow.move(200, 320)

        def init_copy_btn(self):
            self.btncopy = QPushButton(
                text="Copy mnemonic phrase",
                parent=self,
                icon=TigerWalletImage.clipboard,
            )

            self.btncopy.setFixedSize(266, 43)
            self.btncopy.setIconSize(QSize(28, 28))
            self.btncopy.move(190, 310)
            self.btncopy.hide()
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

            self.chbox.move(232, 380)
            self.chbox.setEnabled(False)

        def init_return_btn(self):
            self.retbtn = QPushButton(
                text="Return",
                parent=self,
                icon=TigerWalletImage.back
            )

            self.retbtn.setFixedSize(240, 62)
            self.retbtn.move(70, 420)
            self.retbtn.setIconSize(QSize(32, 32))

        def init_continue_btn(self):
            self.btncont = QPushButton(
                text="Continue", parent=self, icon=TigerWalletImage.continue_
            )

            self.btncont.setFixedSize(240, 62)
            self.btncont.move(340, 420)
            self.btncont.setIconSize(QSize(32, 32))
            self.btncont.setEnabled(False)

        def init_warning(self):
            self.label.hide()
            self.label2.hide()
            self.btnshow.hide()
            self.table.hide()
            self.chbox.hide()

            self.top = QLabel("Notice", self)
            self.top.resize(650, 40)
            self.top.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top.move(0, 40)
            self.top.show()

            self.lbl = QLabel(self)
            self.lbl.resize(470, 140)
            self.lbl.setText(
                "Your recover phrase grants access\n"
                "to your wallet, bypassing your password!\n\n"
                "Please keep this phrase safe!"
            )

            self.lbl.move(90, 100)
            self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl.show()

            def _p():
                self.btnshow.close()
                self.btncopy.show()
                self.blur.setEnabled(False)
                self.chbox.setEnabled(True)
                self.top.close()
                self.lbl.close()
                self.btnex.close()

                self.label.show()
                self.label2.show()
                self.btnshow.show()
                self.table.show()
                self.chbox.show()

            self.btnex = QPushButton("I understand", self)
            self.btnex.setFixedSize(240, 62)
            self.btnex.move(200, 300)
            self.btnex.clicked.connect(_p)
            self.btnex.show()

            if "default" in globalvar.configs["theme"]:
                self.top.setStyleSheet("font-size: 40px; color: #6495ed;")

                self.btnex.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.lbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6495ed;"
                    + "border: 2px solid #b0c4de;"
                    + "border-radius: 8px;"
                    + "padding: 16px;"
                )

        def _enablecont(self):
            self.btncont.setEnabled(True)
            self.chbox.setEnabled(False)

        # Continue to user wallet (wallet creation complete)
        def _startloadingbarclass(self):
            with open(globalvar.conf_file, "w") as ff:
                globalvar.configs["wallets"].append(globalvar.nameofwallet)

                json.dump(globalvar.configs, ff, indent=4)

            self.hide()
            self.alb = AssetLoadingBar()
            self.alb.show()
            self.close()
            self.deleteLater()

    # QR code
    class QrCodeWindow(QWidget):
        def __init__(self, private_key):
            super().__init__()
            self.pkey = private_key

            self.init_main()
            self.init_qr_code()
            self.init_buttons()

            if "default" in globalvar.configs["theme"]:
                self.close_self.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    "border-radius: 8px;"
                    "font-size: 18px;"
                    "color: black;"
                    "padding : 7px;}"
                    "QPushButton::hover{background-color: #99badd;}"
                )

                self.show_qr.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 17px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.copy_pkey.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 17px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e")

                self.uppertxt.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background-color: #1e1e1e;"
                )

                self.lbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6495ed;"
                    + "background-color: transparent;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3")

                self.uppertxt.setStyleSheet(
                    "font-size: 40px;"
                    + "color: black;"
                    + "background-color: #eff1f3;"
                )

                self.lbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
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
            self.qrcode.save(buf, scale=9, border=1, kind="png")

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
                icon=TigerWalletImage.closed_eye,
            )
            self.show_qr.resize(166, 40)
            self.show_qr.setIconSize(QSize(32, 32))
            self.show_qr.move(90, 412)
            self.show_qr.clicked.connect(self.show_hide_qr)

            self.copy_pkey = QPushButton(
                text="Copy private key",
                parent=self,
                icon=TigerWalletImage.copy_blue,
            )
            self.copy_pkey.resize(166, 40)
            self.copy_pkey.setIconSize(QSize(32, 32))
            self.copy_pkey.move(270, 412)
            self.copy_pkey.clicked.connect(
                lambda: [
                    QApplication.clipboard().setText(str(self.pkey.hex())),
                    msgbox("Private key has been copied!"),
                ]
            )

            self.close_self = QPushButton(
                text="Close", parent=self, icon=TigerWalletImage.close
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
                self.show_qr.setIcon(TigerWalletImage.opened_eye)
                self.qropt = 0
                self.show_qr.setText("Hide QR code")

            elif self.qropt == 0:
                self.blur.setEnabled(True)
                self.show_qr.setIcon(TigerWalletImage.closed_eye)
                self.qropt = 1
                self.show_qr.setText("Show QR code")

    # A worker for AssetLoadingBar class
    class AssetLoadingBarWorker(QThread):
        prog = pyqtSignal(str)
        cont = pyqtSignal(int)

        def __init__(self):
            super(QThread, self).__init__()
            self.address = globalvar.account.address
            self.assetamount = len(globalvar.assets_addr)

        def _fetch_history(self):
            url = f"https://api.ethplorer.io/getAddressHistory/{self.address}"
            key = "?apiKey=freekey&limit=100&showZeroValues=false"

            self.data = s.get(url + key, stream=True)
            self.data = self.data.json()

            with open(
                globalvar.dest_path
                + "history.json", "w"
            ) as f:
                json.dump(
                    obj=self.data,
                    fp=f,
                    indent=4
                )

        def fetch_images(self):
            token_image_from_list(globalvar.assets_addr)

        def work(self):
            with ThreadPoolExecutor() as pool:
                pool.submit(self._fetch_history)

                pool.submit(
                    lambda: [
                        token_image(
                            globalvar.assets_addr[i]
                        )
                        for i in range(self.assetamount)
                    ]
                )

                self.contract = pool.submit(
                    lambda: [
                        create_contract(globalvar.assets_addr[i])
                        for i in range(self.assetamount)
                    ]
                ).result()

                with w3.batch_requests() as batch_symbol:
                    for i in range(self.assetamount):
                        batch_symbol.add(
                            self.contract[i].functions.symbol()
                        )

                    batched_requests = pool.submit(batch_symbol.execute).result()
                    price = get_price_from_list(batched_requests)

                    for i in range(self.assetamount):
                        globalvar.assets_details["price"].append(
                            str(price[i])[:17]
                        )

                        globalvar.assets_details["symbol"].append(
                            batched_requests[i].upper()
                        )

                with w3.batch_requests() as batch_token_balance:
                    for i in range(self.assetamount):
                        batch_token_balance.add(
                            token_balance(
                                self.contract[i],
                                self.address
                            )
                        )

                    res = pool.submit(batch_token_balance.execute).result()

                    pool.submit(
                        lambda: [
                            globalvar.assets_details["value"].append(
                                str(
                                    w3.from_wei(res[i], 'ether')
                                )
                            )
                            for i in range(self.assetamount)
                        ]
                    )

                with w3.batch_requests() as batch_token_name:
                    for i in range(self.assetamount):
                        batch_token_name.add(
                            token_name(self.contract[i])
                        )

                    res = pool.submit(batch_token_name.execute).result()

                    for ii in range(self.assetamount):
                        self.cont.emit(ii)
                        time.sleep(0.05)

                        globalvar.assets_details["name"].append(res[ii].upper())

                        globalvar.assets_details["image"].append(
                            globalvar.tokenimgfolder
                            + globalvar.assets_details["symbol"][ii].lower()
                            + ".png"
                        )

                        self.prog.emit(res[ii].upper() + f" ({i+1}/{self.assetamount})")


            self.cont.emit(len(globalvar.assets_addr))

    # visual changes in 1.2
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

            if "default" in globalvar.configs["theme"]:
                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: white;"
                    + "background: transparent;"
                )

                self.label2.setStyleSheet(
                    "font-size: 25px;"
                    + "color: white;"
                    + "background: transparent;"
                )

                self.barstyle = """
                        QProgressBar{
                            color: black;
                            border-radius: 0px;
                            background: transparent;
                        }

                        QProgressBar::chunk{
                            background-color: #6495ed;
                            border-radius: 3px;
                        }
                    """

                self.bar.setStyleSheet(self.barstyle + "color: black;")


        # Window ui
        def setup_main(self):
            self.setFixedWidth(680)
            self.setFixedHeight(310)
            self.setWindowTitle("TigerWallet  -  Loading assets")
            self.thread = QThread()

            align_to_center(self)
            add_round_corners(self, 32)

        # Loading label
        def init_loading_label(self):
            self.img_holder = QLabel(self)
            self.img_holder.resize(680, 350)
            self.tiger_pic = QPixmap(TigerWalletImage.loading_bg)
            self.tiger_pic = self.tiger_pic.scaled(QSize(680, 350))
            self.img_holder.setPixmap(self.tiger_pic)

            self.label = QLabel("Loading assets...", self)
            self.label.resize(680, 216)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        def init_progressbar(self):
            self.bar = QProgressBar(self)
            self.bar.resize(420, 11)
            self.bar.setRange(0, len(globalvar.assets_addr))
            self.bar.setValue(0)
            self.bar.move(Qt.AlignmentFlag.AlignCenter, 180)
            self.bar.setTextVisible(False)

        def init_asset_label(self):
            self.label2 = QLabel(self)
            self.label2.resize(680, 30)
            self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label2.move(0, 220)

        # Thread creation
        def init_thread(self):
            self.worker = AssetLoadingBarWorker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.work)
            self.worker.prog.connect(self.print_names)
            self.worker.cont.connect(self.endworker)
            self.thread.start()

        def print_names(self, names):
            self.label2.setText(names)

        def endworker(self, n):
            self.bar.setValue(n)

            if n == len(globalvar.assets_addr):
                with open(
                    globalvar.assets_json, "w"
                ) as f:
                    json.dump(
                        obj=globalvar.assets_addr,
                        fp=f,
                        indent=4
                    )

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

    # New in v1.5
    class TimedMonitorForNewTransfers(QThread):
        """
        A timed worker that checks for
        new tokens in the user's wallet
        """

        received_new_tokens = pyqtSignal(bool)
        timer = QTimer()

        def __init__(self):
            super().__init__()
            self.address = globalvar.account.address
            self.new_tokens = {
                'address': '',
                'symbol': '',
                'name': ''
            }

        def work(self):
            current_block = w3.eth.get_block('latest', True)
            self.received_new_tokens.emit(False)

            for tx in current_block.transactions:
                if (
                    tx['from'] == self.address
                    or tx['to'] == self.address
                ):
                    hash_ = '0x' + tx['hash'].hex()

                    url = (
                        f"https://eth.blockscout.com/api/v2/transactions/{hash_}"
                        + '/token-transfers?type=ERC-20'
                    )

                    self.data = s.get(url, stream=True)

                    if (
                        'items' in self.data.json().keys()
                        and len(self.data.json()['items']) != 0
                    ):
                        data = self.data.json()['items'][0]

                        if (
                            not data['token']['address']
                            in globalvar.assets_addr
                        ):
                            self.token = {
                                'address': data['token']['address'],
                                'symbol': data['token']['symbol'],
                                'name': data['token']['name']
                            }

                            globalvar.assets_addr.append(
                                self.token['address']
                            )

                            self.balance = create_contract(
                                self.token['address']
                            )
                            self.balance = self.balance.functions.balanceOf(
                                self.address
                            )
                            self.balance = w3.from_wei(
                                float(self.balance.call()),
                                'ether'
                            )

                            globalvar.assets_details['value'].append(
                                str(self.balance)[:17]
                            )

                            self.new_tokens = self.token
                            self.received_new_tokens.emit(True)

    class TimedUpdateTotalBalance(QThread):
        balance = pyqtSignal(float)
        timer = QTimer()

        def __init__(self):
            super().__init__()
            self.address = globalvar.account.address

        def work(self):
            eth_balance = float(
                w3.from_wei(
                    w3.eth.get_balance(self.address),
                    'ether'
                )
            )

            eth_price = float(get_eth_price())
            eth_balance *= eth_price

            amount_of_assets = len(globalvar.assets_details['symbol'])

            assets_price = globalvar.assets_details['price']
            assets_amount = globalvar.assets_details['value']

            total_list = [
                float(assets_price[i]) if not 'N/A' else 0.0
                * float(assets_amount[i])
                for i in range(amount_of_assets)
                if float(assets_amount[i]) != 0.0
            ]

            total = 0.0

            for item in total_list:
                total += item

            total += float(eth_balance)

            self.balance.emit(total)

    # Gets gas continuously
    class TimedUpdateGasFeeWorker(QThread):
        """
        A timed worker that updates gas price
        """

        gas = pyqtSignal(str)
        timer = QTimer()

        def __init__(self):
            super().__init__()
            self.g = 0.0
            self.gwei = 0.0

        def work(self):
            try:
                self.g = float(w3.eth.gas_price) + 200000
                self.gwei = w3.from_wei(self.g, "ether") * 1000000000
                self.p = float(w3.from_wei(self.g, "ether"))
                self.p *= float(get_eth_price())
                self.p *= 200000

                self.p = rm_scientific_notation(round(self.p, 2))
                self.gwei = rm_scientific_notation(self.gwei)

                self.gas.emit(
                    f" {self.gwei} GWEI  ~${self.p} (updates every 10 secs)"
                )
            except Exception:
                self.gas.emit(
                    "Failed to fetch gas price. Trying again in 3 seconds..."
                )

            if not w3.is_connected():
                self.gas.emit(" N/A (No internet connection)")

    # Updates the price of assets
    class TimedUpdatePriceOfAssetsWorker(QThread):
        eth_price = pyqtSignal(str)
        timer = QTimer()

        # globalvar.assets_details['symbol'])).result()
        def __init__(self):
            super(QThread, self).__init__()
            self.address = globalvar.account.address
            self.pool = ThreadPoolExecutor()

        def work(self):
            self.assetamount = len(globalvar.assets_addr)

            self.eth_price.emit(self.pool.submit(get_eth_price).result())

            self.contract_list = [
                create_contract(globalvar.assets_addr[i])
                for i in range(self.assetamount)
            ]

            pricep = [
                get_price(self.contract_list[i].functions.symbol().call())
                for i in range(self.assetamount)
            ]

            for i in range(self.assetamount):
                globalvar.assets_details["price"][i] = pricep[i]

    # Gets gas once
    class FetchGasWorker(QThread):
        """
        Fetches gas price once
        """

        gas = pyqtSignal(str)

        def __init__(self):
            super().__init__()

        def work(self):
            self.g = float(w3.eth.gas_price) + 23000
            self.gwei = w3.from_wei(self.g, "ether") * 1000000000
            self.p = float(w3.from_wei(self.g, "ether"))
            self.p *= float(get_eth_price())
            self.p *= 23000

            self.gwei = rm_scientific_notation(self.gwei)
            self.p = round(round(self.p, 2))
            self.p = rm_scientific_notation(self.p)

            self.gas.emit(
                f" {self.gwei} GWEI  ~${self.p} (updates every 10 secs)"
            )
            self.quit()

    class ValidatePassword(QWidget):
        def __init__(self):
            super().__init__()
            self.opt = 1

            self.init_window()
            self.init_buttons()

            if "default" in globalvar.configs["theme"]:
                self.verify.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.cancel.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn_showhide.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    "border-radius: 8px;}"
                    "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e;")

                self.password.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 16px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.label.setStyleSheet(
                    "font-size: 27px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3;")

                self.password.setStyleSheet(
                    "color: black; "
                    + "font: 16px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "background: transparent;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.label.setStyleSheet(
                    "font-size: 27px;"
                    + "color: black;"
                    + "background: transparent;"
                )

        def init_window(self):
            self.setFixedWidth(570)
            self.setFixedHeight(300)
            self.setWindowTitle("TigerWallet  -  Password verification")
            align_to_center(self)

            self.label = QLabel("Please enter your password to continue", self)
            self.label.resize(500, 100)
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
                text="Cancel", parent=self, icon=TigerWalletImage.back
            )

            self.cancel.setFixedSize(200, 50)
            self.cancel.move(70, 210)
            self.cancel.setIconSize(QSize(32, 32))
            self.cancel.clicked.connect(self.return_)

            self.verify = QPushButton(self)

            if not globalvar.from_experienced:
                self.verify.setText(" Verify password")
                self.verify.setIcon(TigerWalletImage.pkey_blue)
            else:
                self.verify.setText("Login")
                self.verify.setIcon(TigerWalletImage.wallet_blue)

            self.verify.setFixedSize(200, 50)
            self.verify.move(300, 210)
            self.verify.setIconSize(QSize(32, 32))
            self.verify.clicked.connect(
                lambda: self.validate_pass(self.password.text())
            )

            self.btn_showhide = QPushButton(
                text=None, parent=self, icon=TigerWalletImage.closed_eye
            )

            self.btn_showhide.setIconSize(QSize(32, 32))
            self.btn_showhide.move(500, 145)
            self.btn_showhide.clicked.connect(self.unhide)

        def return_(self):
            if globalvar.from_experienced:
                globalvar.from_experienced = False
                self.close()
                self.uwe = UserWithExperience()
                self.uwe.show()
                self.deleteLater()
            else:
                self.close()
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
            if globalvar.from_experienced:
                if len(passwd) == 0:
                    errbox("Password field is empty")
                    return

                try:
                    with open(globalvar.nameofwallet, "r") as f:
                        globalvar.account = Account.from_key(
                            Account.decrypt(json.load(f), password=passwd)
                        )

                        with open(globalvar.conf_file, "w") as ff:
                            if (
                                not globalvar.nameofwallet
                                in globalvar.configs["wallets"]
                            ):
                                globalvar.configs["wallets"].append(
                                    globalvar.nameofwallet
                                )

                            json.dump(globalvar.configs, ff, indent=4)

                except ValueError:
                    errbox("Incorrect password. Try again")
                    return

                if len(globalvar.assets_addr) != 0:
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

            if not globalvar.from_experienced:
                with open(globalvar.nameofwallet, "rb") as f:
                    try:
                        Account.decrypt(
                            orjson.loads(f.read()), password=passwd
                        )

                        self.qrcode = QrCodeWindow(globalvar.account.key)
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

            if os.name == 'nt':
                self.extract_path = (
                    f"C:\\Users\\{globalvar.current_usr}\\"
                    + 'Desktop\\'
                )

            else:
                self.extract_path = (
                    f"/home/{globalvar.current_usr}/"
                )

        def work(self):
            self.dl_prog.emit(0)
            self.is_finished.emit(False)
            dl = 0

            # Ran via pyinstaller's exe
            if self.method_of_execution == 'pyinstaller-executable':
                ver = self.version
                tigerwallet_executable_file = \
                    f"{ver}/tigerwallet-{ver[1:len(ver)]}-x86-64"

                dl_executable_link = (
                    'https://github.com/Serpenseth/'
                    + 'TigerWallet/releases/download/'
                    + tigerwallet_executable_file
                    + '.exe'
                )

                with open(
                    self.extract_path
                    + f"tigerwallet-{self.version}-x86-64.exe",
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

                   #self.parent.total_file_size = self.size
                    self.parent.bar.setRange(0, 0)

                    for data in zipped_dl.iter_content(
                        chunk_size=1024
                    ):
                        dl += len(data)
                        zip_.write(data)
                        self.dl_prog.emit(dl)

                    with self.ZipFile(zip_, 'r') as zip_ref:
                        zip_ref.extractall(self.extract_path)

                    self.is_finished.emit(True)

            # Ran as an appimage
            elif self.method_of_execution == 'appimage-executable':
                ver = self.version
                tigerwallet_executable_file = \
                    f"{ver}/tigerwallet-{ver[1:len(ver)]}-x86-64"

                dl_executable_link = (
                    'https://github.com/Serpenseth/'
                    + 'TigerWallet/releases/download/'
                    + tigerwallet_executable_file
                    + '.Appimage'
                )

                with open(
                    self.extract_path
                    + f"tigerwallet-{self.version}-x86-64.Appimage",
                    mode='wb'
                ) as appimage_file:
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
                    self.parent.bar.setRange(0, self.size)

                    for data in downloaded_executable.iter_content(
                        chunk_size=4096
                    ):
                        dl += len(data)
                        appimage_file.write(data)
                        self.dl_prog.emit(dl)

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
    class CheckForUpdates(QWidget):
        def __init__(
            self,
            url: str
        ):
            super().__init__()
            self.current_version = TigerWalletVersion
            self.url = url
            self.local_path = globalvar.local_path
            self.execution_method = self.__how_is_tigerwallet_running()
            self.total_file_size = 0

            self.init_self()

            self.init_loading_label()
            self.init_thread()

            self.init_progressbar()
            self.init_asset_label()
            self.check_if_update_is_available()

            if "default" in globalvar.configs["theme"]:
                self.label.setStyleSheet(
                    "font-size: 40px;"
                    + "color: white;"
                    + "background: transparent;"
                )

                self.label2.setStyleSheet(
                    "font-size: 25px;"
                    + "color: white;"
                    + "background: transparent;"
                )

                self.barstyle = (
                    """
                        QProgressBar{
                            color: black;
                            border-radius: 0px;
                            background: transparent;
                        }

                        QProgressBar::chunk{
                            background-color: #6495ed;
                            border-radius: 3px;
                        }
                    """
                )

                self.bar.setStyleSheet(
                    self.barstyle
                    + "color: black;"
                )

        def __how_is_tigerwallet_running(self):
            if os.name == "nt":
                if '_MEI' in self.local_path:
                    return 'pyinstaller-executable'

                elif 'AppData\\Local' in self.local_path:
                    return 'pip-install-executable'

            if '/tmp/.mount' in self.local_path:
                return 'appimage-executable'

            return 'python-command'

        def check_if_update_is_available(self):
            data = s.get(url=self.url)
            data = data.text.split()

            github_version = ' '.join(data[11:14])

            github_version = float(github_version[11:14])
            self.current_version = float(self.current_version)

            if self.current_version < github_version:
                resp = questionbox(
                    'A new update is available. '
                    + 'Install now?'
                )

                if resp:
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

        def init_progressbar(self):
            self.bar = QProgressBar(self)
            self.bar.resize(420, 12)
            #self.bar.setRange(0, self.total_file_size)
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
            self.label2.setText(
                f"{str(n)}/{self.total_file_size} KB"
            )

            self.bar.setValue(n)

        def download_update(self):
            ver = 'v' + self.current_version

            # Using pyinstaller
            if self.execution_method == 'pyinstaller-executable':
                self.duw = DownloadUpdateWorker(
                    parent=self,
                    method_of_execution='pyinstaller-executable',
                    version=ver
                )

                def is_done(res):
                    if res:
                        msgbox(
                            'New version downloaded to path: '
                            + f"C:\\Users\\{globalvar.current_usr}\\"
                            + 'Desktop\\'
                            + f"tigerwallet-{ver}-x86-64.exe",
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

            # Using appimage
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
                            f"/home/{globalvar.current_usr}/"
                            + f"tigerrwallet-{ver}-x86-64.Appimage",
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
                        if os.name == 'nt':
                            msgbox(
                                'New version downloaded to path: '
                                + f"C:\\Users\\{globalvar.current_usr}\\"
                                + 'Desktop\\'
                                + 'TigerWallet-main'
                            )

                        else:
                            msgbox(
                                'New version downloaded to path: '
                                + f"/home/{globalvar.current_usr}"
                                + 'TigerWallet-main'
                            )

                        self.thread.quit()
                        self.duw.quit()
                        self.thread.deleteLater()
                        self.duw.deleteLater()

                        self.close()
                        self.deleteLater()

                        if os.name == 'nt':
                            subprocess.run(
                                [
                                    sys.executable,
                                    f"C:\\Users\\{globalvar.current_usr}\\"
                                    + 'Desktop\\TigerWallet-main\\'
                                    + 'src\\TigerWallet\\tigerwallet.py'
                                ]
                            )

                        else:
                            subprocess.run(
                                [
                                    sys.executable,
                                    f"/home/{globalvar.current_usr}/"
                                    + 'TigerWallet-main/src/'
                                    + 'TigerWallet/tigerwallet.py'
                                ]
                            )

                self.duw.moveToThread(self.thread)
                self.duw.dl_prog.connect(self.emit_progress)
                self.duw.is_finished.connect(is_done)
                self.thread.started.connect(self.duw.work)
                self.thread.start()

            if number_of_wallets != 0:
                login.close()
                login.deleteLater()
                return

            first.close()
            first.deleteLater()


    # Fixed program crash in v1.5
    # when adding an invalid RPC
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

            if "default" in globalvar.configs["theme"]:
                # The border that fills up space
                self.border.setStyleSheet(
                    "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.close_about.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.apply_dark_mode()

            elif globalvar.configs["theme"] == "default_light":
                self.apply_light_mode()

        def init_window(self):
            self.setWindowTitle("TigerWallet  -  Settings")
            self.setFixedWidth(600)
            self.setFixedHeight(500)

            align_to_center(self)
            add_round_corners(self)

            self.border = QLabel(self)
            self.border.resize(578, 438)
            self.border.move(10, 50)

            self.list_ = QListWidget(self)
            self.list_.resize(510, 340)
            self.list_.move(40, 90)
            self.list_.setIconSize(QSize(32, 32))
            self.list_.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.list_.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.settingslbl = QLabel("Settings", self)
            self.settingslbl.resize(148, 40)
            self.settingslbl.move(220, 30)
            self.settingslbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.close_settings_window = QPushButton(
                text="Close", parent=self, icon=TigerWalletImage.close_blue
            )
            self.close_settings_window.resize(80, 40)
            self.close_settings_window.setIconSize(QSize(24, 24))
            self.close_settings_window.move(16, 5)
            self.close_settings_window.clicked.connect(self.close_self)

        #
        def init_options(self):
            self.list_.clearSelection()

            self.options = {
                "rpc": QListWidgetItem("      RPC settings"),
                "pass": QListWidgetItem("      Change password"),
                "show_pkey": QListWidgetItem("      Show private key"),
                "create_wallet": QListWidgetItem("      Create new wallet"),
                "lock_wallet": QListWidgetItem(
                    "      Configure lock settings"
                ),
                "about": QListWidgetItem("      About TigerWallet"),
            }

            for option in self.options:
                self.options[option].setSizeHint(QSize(0, 50))
                self.list_.addItem(self.options[option])

            self.options["rpc"].setIcon(TigerWalletImage.rpc_blue)
            self.options["pass"].setIcon(TigerWalletImage.pass_blue)
            self.options["show_pkey"].setIcon(TigerWalletImage.pkey_blue)
            self.options["create_wallet"].setIcon(TigerWalletImage.wallet_blue)
            self.options["lock_wallet"].setIcon(TigerWalletImage.lock_blue)
            self.options["about"].setIcon(TigerWalletImage.about_blue)

            def user_choice(item):
                if item.text() == self.options["rpc"].text():
                    self.list_.clearSelection()
                    self.change_rpc()

                elif item.text() == self.options["pass"].text():
                    self.list_.clearSelection()
                    self.change_password_window()

                elif item.text() == self.options["create_wallet"].text():
                    self.list_.clearSelection()
                    globalvar.settings_new_wallet = True

                    self.master.thread.quit()
                    self.master.worker.quit()
                    self.master._gasupdate.quit()
                    self.master.update_price_worker.quit()
                    self.master.update_price_thread.quit()
                    self.master.tm.stop()
                    self.master.close()

                    self.wn = WalletName()
                    self.wn.show()
                    self.close()
                    self.deleteLater()

                elif item.text() == self.options["show_pkey"].text():
                    self.list_.clearSelection()

                    self.vp = ValidatePassword()
                    self.vp.show()

                elif item.text() == self.options["lock_wallet"].text():
                    self.list_.clearSelection()
                    self.change_lock_timer()

                elif item.text() == self.options["about"].text():
                    self.list_.clearSelection()
                    self.launch_about_window()

            self.list_.itemClicked.connect(user_choice)

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
            self.thanks_item = [QLabel(self.tabs) for i in range(4)]
            self.thanks_item[0].setText(
                f"Shoutout: Mikko Ohtamaa, DefiDeBlitzen, Maka, felipe"
            )

            for i in range(1):
                self.thanks_item[i].resize(400, 30)
                self.thanks_item[i].move(13, y_coords[i])
                self.thanks_item[i].hide()

            def tab_switcher(index):
                if index == 0:
                    [self.about_item[i].show() for i in range(3)]
                    [self.author_item[i].hide() for i in range(3)]
                    [self.thanks_item[i].hide() for i in range(1)]

                elif index == 1:
                    [self.about_item[i].hide() for i in range(3)]
                    [self.author_item[i].show() for i in range(3)]
                    [self.thanks_item[i].hide() for i in range(1)]

                elif index == 2:
                    [self.about_item[i].hide() for i in range(3)]
                    [self.author_item[i].hide() for i in range(3)]
                    [self.thanks_item[i].show() for i in range(1)]

            self.tabs.tabBarClicked.connect(tab_switcher)

            self.close_about = QPushButton(
                text="Return",
                parent=self.about_parent,
                icon=TigerWalletImage.back,
            )

            self.close_about.resize(200, 50)
            self.close_about.setIconSize(QSize(32, 32))
            self.close_about.move(180, 366)
            self.close_about.clicked.connect(
                lambda: [self.about_parent.hide(), self.list_.show()]
            )
            self.about_parent.hide()

        def close_self(self):
            self.master.button_box.show()
            self.master.border.show()
            self.master.lock_wallet_button.show()
            self.master.setEnabled(True)
            self.hide()

            if self.master.tab == 0:
                if self.master.donation_window_active:
                    self.master.init_donate_window()
                    return

                self.master.table.show()
                self.master.val.show()
                self.master.add_coin_btn.show()
                self.master.default_coin_btn.show()
                self.master.del_coin_btn.show()

            elif self.master.tab == 1:
                self.master.show_tab1_contents()

            elif self.master.tab == 2:
                self.master.show_tab2_contents()

            elif self.master.tab == 3:
                self.master.show_tab3_contents()

            elif self.master.tab == 4:
                self.master.show_tab4_contents()

        def launch_about_window(self):
            self.list_.hide()
            self.about_parent.show()

        def apply_dark_mode(self):
            self.setStyleSheet("background-color: #111212;")
            self.about_parent.setStyleSheet("background-color: transparent;")

            self.close_settings_window.setStyleSheet(
                "QPushButton{background-color:  transparent;"
                + "font-size: 15px;"
                + "color: #eff1f3;"
                + "border-radius: 8px;}"
                + "QPushButton::hover{background-color: #363636;}"
            )

            self.list_.setStyleSheet(
                "QListWidget {font-size: 20px;"
                + "color: #eff1f3;"
                + "padding: 7px;"
                + "border: transparent;"
                + "background: transparent;}"
                "QListView::item:hover{color: #b0c4de;"
                "background: #363636;"
                "border-radius: 8px;}"
            )

            self.settingslbl.setStyleSheet(
                "font-size: 30px;"
                "color: #6495ed;"
                "background: #111212;"
            )

            for i in range(3):
                self.about_item[i].setStyleSheet(
                    "background: transparent;"
                    "color: #b0c4de;"
                    "font: 18px;"
                )

                self.author_item[i].setStyleSheet(
                    "background: transparent;"
                    "color: #b0c4de;"
                    "font: 18px;"
                )

            self.thanks_item[0].setStyleSheet(
                "background: transparent;"
                "color: #b0c4de;"
                "font: 18px;"
            )

            self.tabs.setStyleSheet(
                "QTabWidget {background: transparent;"
                "border-radius: 4px;}"
                "QTabWidget::pane {border: 1px solid lightgray;"
                "border-radius: 4px;}"
                "QTabBar::tab {background: #1e1e1e;"
                "color: #b0c4de;"
                "border-radius: 4px;"
                "border-top-left-radius: 4px;"
                "border-top-right-radius: 4px;"
                "border-bottom-left-radius: 0px;"
                "border-bottom-right-radius: 0px;"
                "font: 16px;"
                "padding: 9px;}"
                "QTabBar::tab:selected {border-top: 4px solid #6495ed;"
                "border-bottom:  3px solid #111212;"
                "border-right: 1px solid lightgray;"
                "border-left: 1px solid lightgray;"
                "font: 20px;}"
                "QTabBar::tab:hover {border-top: 3px solid gray;"
                "border-bottom:  3px solid #111212;}"
            )

        def apply_light_mode(self):
            self.setStyleSheet("background-color: #eaeaeb;")
            self.about_parent.setStyleSheet("background-color: transparent;")

            self.close_settings_window.setStyleSheet(
                "QPushButton{background-color:  transparent;"
                + "font-size: 15px;"
                + "color: black;"
                + "border-radius: 8px;}"
                + "QPushButton::hover{background-color: #adb4bf;}"
            )

            self.list_.setStyleSheet(
                "QListWidget {font-size: 20px;"
                + "color: black;"
                + "padding: 7px;"
                + "border: transparent;"
                + "background: transparent;}"
                + "QListView::item:hover{color: black;"
                "background: #adb4bf;"
                "border-radius: 8px;}"
            )

            self.settingslbl.setStyleSheet(
                "font-size: 30px;" + "color: #6495ed;" + "background: #eaeaeb;"
            )

            for i in range(3):
                self.about_item[i].setStyleSheet(
                    "background: transparent;"
                    + "color: black;"
                    + "font: 18px;"
                )

                self.author_item[i].setStyleSheet(
                    "background: transparent;"
                    + "color: black;"
                    + "font: 18px;"
                )

            self.thanks_item[0].setStyleSheet(
                "background: transparent;"
                + "color: black;"
                + "font: 18px;"
            )

            self.tabs.setStyleSheet(
                "QTabWidget {background: transparent;"
                "border-radius: 4px;}"
                "QTabWidget::pane {border: 2px solid lightgray;"
                "border-radius: 4px;}"
                "QTabBar::tab {background: #c3c5c8;"
                "color: black;"
                "border-radius: 4px;"
                "border-top-left-radius: 4px;"
                "border-top-right-radius: 4px;"
                "border-bottom-left-radius: 0px;"
                "border-bottom-right-radius: 0px;"
                "font: 16px;"
                "padding: 9px;}"
                "QTabBar::tab:selected {border-top: 4px solid #6495ed;"
                "border-bottom:  3px solid #c3c5c8;"
                "border-right: 1px solid lightgray;"
                "border-left: 1px solid lightgray;"
                "font: 20px;}"
                "QTabBar::tab:hover {border-top: 3px solid gray;"
                "border-bottom:  3px solid #c3c5c8;}"
            )

        def change_rpc(self):
            self.list_.hide()

            self.rpc_list_options = QListWidget(self)
            self.rpc_list_options.resize(520, 196)
            self.rpc_list_options.move(40, 80)
            self.rpc_list_options.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.rpc_list_options.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.rpc_list = []

            with open(globalvar.rpc_list_file, "r") as f:
                self.rpc_list = json.load(f)

            self.prev = 0

            for item in enumerate(self.rpc_list):
                self.rpc_list_options.insertItem(*item)

            for i in range(len(self.rpc_list)):
                self.rpc_list_options.item(i).setSizeHint(QSize(0, 54))

                if self.rpc_list[i] == globalvar.configs["rpc"]:
                    self.rpc_list_options.item(i).setText(
                        self.rpc_list_options.item(i).text()
                        + "     (current)"
                    )

                    self.prev = i

            self.rpc_list_options.show()
            self.rpc_list_options.itemClicked.connect(self._rpc_choice)

            self.delete_rpc_btn = QPushButton(
                text="Delete RPC",
                parent=self,
                icon=TigerWalletImage.close
            )

            self.delete_rpc_btn.setFixedSize(220, 50)
            self.delete_rpc_btn.setIconSize(QSize(32, 32))
            self.delete_rpc_btn.move(334, 328)
            self.delete_rpc_btn.show()
            self.delete_rpc_btn.clicked.connect(self.rm_rpc_window)

            #
            self.add_rpc_btn = QPushButton(
                text="Add RPC",
                parent=self,
                icon=TigerWalletImage.plus
            )

            self.add_rpc_btn.setFixedSize(220, 50)
            self.add_rpc_btn.setIconSize(QSize(32, 32))
            self.add_rpc_btn.move(46, 328)
            self.add_rpc_btn.show()
            self.add_rpc_btn.clicked.connect(self.add_rpc_window)

            self.cancel_rpc_btn = QPushButton(
                text="Return",
                parent=self,
                icon=TigerWalletImage.back
            )

            self.cancel_rpc_btn.setFixedSize(220, 50)
            self.cancel_rpc_btn.setIconSize(QSize(32, 32))
            self.cancel_rpc_btn.move(186, 398)
            self.cancel_rpc_btn.show()
            self.cancel_rpc_btn.clicked.connect(self._close_rpc_window)

            if "default" in globalvar.configs["theme"]:
                self.delete_rpc_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.add_rpc_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.cancel_rpc_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.rpc_list_options.setStyleSheet(
                    "QListWidget {font-size: 20px;"
                    + "color: #eff1f3;"
                    + "padding: 7px;"
                    + "border: transparent;"
                    + "background: transparent;}"
                    + "QListView::item:hover{color: #b0c4de;"
                    "background: #363636;"
                    "border-radius: 8px;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.rpc_list_options.setStyleSheet(
                    "QListWidget {font-size: 20px;"
                    + "color: black;"
                    + "padding: 7px;"
                    + "border: transparent;"
                    + "background: transparent;}"
                    + "QListView::item:hover{color: black;"
                    "background: #adb4bf;"
                    "border-radius: 8px;}"
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
                text="Return", parent=self, icon=TigerWalletImage.back
            )
            self.cancel_add_rpc.setFixedSize(220, 50)
            self.cancel_add_rpc.setIconSize(QSize(32, 32))
            self.cancel_add_rpc.move(46, 328)
            self.cancel_add_rpc.show()
            self.cancel_add_rpc.clicked.connect(_close_add_rpc_window)

            def _test_rpc():
                if len(self.add_rpc_https.text()) == 0:
                    errbox("RPC field is empty")
                    return

                elif (
                    "ws" in self.add_rpc_https.text()
                    or "wss" in self.add_rpc_https.text()
                ):
                    errbox("ws or wss is currently not supported")
                    return

                elif (
                    self.add_rpc_https.text().find("https") != 0
                    or self.add_rpc_https.text().find("http") != 0
                ):
                    errbox("Invalid RPC")
                    return

                list_of_bad_RPCs = [
                    "https://ethereum.blockpi.network/v1/rpc/public",
                    "https://eth.llamarpc.com/",
                ]

                if self.add_rpc_https.text() in list_of_bad_RPCs:
                    errbox(
                        self.add_rpc_https.text()
                        + "is known to cause issues with TigerWallet.\n"
                        + "Please use another RPC"
                    )
                    return

                with open(globalvar.rpc_list_file, "r") as f:
                    tmp_list = json.load(f)

                    if self.add_rpc_https.text() in tmp_list:
                        errbox("RPC is already on your list")
                        return

                for i in range(len(self.add_rpc_port.text())):
                    if (
                        ord(self.add_rpc_port.text()[i]) < 48
                        or ord(self.add_rpc_port.text()[i]) > 57
                    ):
                        errbox("Ports only consist of numbers")
                        return

                class _TestingRPCMsgBox(QWidget):
                    def __init__(self, master):
                        super().__init__()

                        self.init_window()

                        if "default" in globalvar.configs["theme"]:
                            self.border.setStyleSheet(
                                "border: 2px solid #778ba5;"
                                + "border-radius: 16px;"
                                + "background: transparent;"
                            )

                        if globalvar.configs["theme"] == "default_dark":
                            self.setStyleSheet("background: #1e1e1e")

                            self.lbl.setStyleSheet(
                                "font-size: 17px;"
                                + "color: #b0c4de;"
                                + "background: transparent;"
                            )

                        elif globalvar.configs["theme"] == "default_light":
                            self.setStyleSheet("background: #eff1f3")

                            self.lbl.setStyleSheet(
                                "font-size: 17px;"
                                + "color: black;"
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
                            request_kwargs={"timeout": 15},
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

                        with open(globalvar.rpc_list_file, "w") as f:
                            json.dump(self.rpc_list, f, indent=4)

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
                self.test_rpc_thread.started.connect(self.test_rpc_worker.work)
                self.test_rpc_thread.start()
                self.trpcmb.show()

            self.add_rpc_https.returnPressed.connect(_test_rpc)

            self.add_user_rpc = QPushButton(
                text="Add RPC", parent=self, icon=TigerWalletImage.rpc_blue
            )
            self.add_user_rpc.setFixedSize(220, 50)
            self.add_user_rpc.setIconSize(QSize(32, 32))
            self.add_user_rpc.move(334, 328)
            self.add_user_rpc.show()
            self.add_user_rpc.clicked.connect(_test_rpc)

            if "default" in globalvar.configs["theme"]:
                self.cancel_add_rpc.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.add_user_rpc.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.enter_rpc_msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #b0c4de;"
                    + "background: transparent;"
                )

                self.add_rpc_https.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.rpclbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.add_rpc_port.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.portlbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.enter_rpc_msg.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.add_rpc_https.setStyleSheet(
                    "color: black; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.rpclbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.add_rpc_port.setStyleSheet(
                    "color: black; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.portlbl.setStyleSheet(
                    "font-size: 16px;"
                    + "color: black;"
                    + "background: transparent;"
                )

        def rm_rpc_window(self):
            self.settingslbl.hide()
            self.delete_rpc_btn.hide()
            self.add_rpc_btn.hide()
            self.cancel_rpc_btn.move(186, 348)

            self.selectlbl = QLabel(
                "Click on the RPC that you want to remove", self
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

                    with open(globalvar.rpc_list_file, "w") as f:
                        json.dump(self.rpc_list, f, indent=4)

                    if "(current)" in item.text():
                        _tmp = self.rpc_list[_row - 1]
                        _tmp[: _tmp.find("(")]

                        self.rpc_list_options.item(_row - 1).setText(
                            self.rpc_list_options.item(_row - 1).text()
                            + "     (current)"
                        )

                        with open(globalvar.conf_file, "w") as ff:
                            globalvar.configs["rpc"] = _tmp
                            json.dump(globalvar.configs, ff)

                    self.rpc_list_options.clearSelection()
                    msgbox("RPC deleted!")
                    return

                elif not res:
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

            if globalvar.configs["theme"] == "default_dark":
                self.selectlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6495ed;"
                    + "background: #111212;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.selectlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #6495ed;"
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
                    self.btn_eye1.setIcon(TigerWalletImage.opened_eye)
                    self.current_password.setEchoMode(
                        QLineEdit.EchoMode.Normal
                    )
                    self.opt1 = 0

                elif self.opt1 == 0:
                    self.btn_eye1.setIcon(TigerWalletImage.closed_eye)
                    self.current_password.setEchoMode(
                        QLineEdit.EchoMode.Password
                    )
                    self.opt1 = 1

            def _unhide2():
                if self.opt2 == 1:
                    self.btn_eye2.setIcon(TigerWalletImage.opened_eye)
                    self.new_password1.setEchoMode(QLineEdit.EchoMode.Normal)
                    self.opt2 = 0

                elif self.opt2 == 0:
                    self.btn_eye2.setIcon(TigerWalletImage.closed_eye)
                    self.new_password1.setEchoMode(QLineEdit.EchoMode.Password)
                    self.opt2 = 1

            def _unhide3():
                if self.opt3 == 1:
                    self.btn_eye3.setIcon(TigerWalletImage.opened_eye)
                    self.new_password2.setEchoMode(QLineEdit.EchoMode.Normal)
                    self.opt3 = 0

                elif self.opt3 == 0:
                    self.btn_eye3.setIcon(TigerWalletImage.closed_eye)
                    self.new_password2.setEchoMode(QLineEdit.EchoMode.Password)
                    self.opt3 = 1

            def _is_current_pass_valid():
                passwd = self.current_password.text()

                if len(passwd) == 0:
                    errbox("Enter your current password in order to change it")
                    return False

                try:
                    with open(globalvar.nameofwallet, "r") as f:
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
                text=None, parent=self, icon=TigerWalletImage.closed_eye
            )

            self.btn_eye1.setIconSize(QSize(28, 28))
            self.btn_eye1.move(521, 132)
            self.btn_eye1.show()
            self.btn_eye1.clicked.connect(_unhide1)

            self.btn_eye2 = QPushButton(
                text=None, parent=self, icon=TigerWalletImage.closed_eye
            )

            self.btn_eye2.setIconSize(QSize(28, 28))
            self.btn_eye2.move(521, 192)
            self.btn_eye2.show()
            self.btn_eye2.clicked.connect(_unhide2)

            self.btn_eye3 = QPushButton(
                text=None, parent=self, icon=TigerWalletImage.closed_eye
            )

            self.btn_eye3.setIconSize(QSize(28, 28))
            self.btn_eye3.move(521, 252)
            self.btn_eye3.show()
            self.btn_eye3.clicked.connect(_unhide3)

            self.checkbox = QCheckBox(self)
            self.checkbox.setText("I have written down my new password")
            self.checkbox.resize(320, 40)
            self.checkbox.move(150, 315)
            self.checkbox.show()

            self.cancel_change_passwd = QPushButton(
                text="Return", parent=self, icon=TigerWalletImage.back
            )
            self.cancel_change_passwd.setFixedSize(220, 50)
            self.cancel_change_passwd.setIconSize(QSize(32, 32))
            self.cancel_change_passwd.move(46, 378)
            self.cancel_change_passwd.show()

            self.continue_change_passwd = QPushButton(
                text="Continue", parent=self, icon=TigerWalletImage.continue_
            )
            self.continue_change_passwd.setFixedSize(220, 50)
            self.continue_change_passwd.setIconSize(QSize(28, 28))
            self.continue_change_passwd.move(334, 378)
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
            self.continue_change_passwd.clicked.connect(_validate_passwords)
            self.cancel_change_passwd.clicked.connect(
                self._close_change_passwd_window
            )

            if "default" in globalvar.configs["theme"]:
                self.btn_eye1.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn_eye2.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.btn_eye3.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.cancel_change_passwd.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.current_password.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.current_password_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.new_password1.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.new_password1_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.new_password2.setStyleSheet(
                    "color: #eff1f3; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.new_password2_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.checkbox.setStyleSheet(
                    "color: #eff1f3;" + "font-size: 16px;"
                )

                self.continue_change_passwd.setStyleSheet(
                    +"background-color: #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "background-color: #222222;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.current_password.setStyleSheet(
                    "color: black; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.current_password_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.new_password1.setStyleSheet(
                    "color: black; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.new_password1_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.new_password2.setStyleSheet(
                    "color: black; "
                    + "font: 14px;"
                    + "border: 1px solid #778ba5;"
                    + "border-radius: 8px;"
                    + "padding: 7px;"
                    + "QLineEdit::placeholder{ color: #767e89; }"
                )

                self.new_password2_lbl.setStyleSheet(
                    "font-size: 14px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.checkbox.setStyleSheet(
                    "color: black;" + "font-size: 16px;"
                )

                self.continue_change_passwd.setStyleSheet(
                    ":enabled {"
                    + "background-color: #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + ":disabled {background-color: #adb4bf;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

        def change_lock_timer(self):
            self.list_.hide()

            self.timer_list_options = QListWidget(self)
            self.timer_list_options.resize(520, 286)
            self.timer_list_options.move(40, 80)
            self.timer_list_options.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.timer_list_options.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
                self.timer_list_options.item(i).setSizeHint(QSize(0, 54))

            self.prev = 0

            if self.master.afk_time == 100000:
                self.timer_list_options.item(0).setText(
                    self.timer_options[0] + "      (current)"
                )

            elif self.master.afk_time == 500000:
                self.timer_list_options.item(1).setText(
                    self.timer_options[1] + "      (current)"
                )
                self.prev = 1

            elif self.master.afk_time == 1500000:
                self.timer_list_options.item(2).setText(
                    self.timer_options[2] + "      (current)"
                )
                self.prev = 2

            elif self.master.afk_time == 3000000:
                self.timer_list_options.item(3).setText(
                    self.timer_options[3] + "      (current)"
                )
                self.prev = 3

            elif self.master.afk_time == 10000000:
                self.timer_list_options.item(4).setText(
                    self.timer_options[4] + "      (current)"
                )
                self.prev = 4

            elif self.master.afk_time == 40000000:
                self.timer_list_options.item(5).setText(
                    self.timer_options[5] + "      (current)"
                )
                self.prev = 5

            elif self.master.afk_time == None:
                self.timer_list_options.item(6).setText(
                    self.timer_options[6] + "      (current)"
                )
                self.prev = 6

            self.timer_list_options.currentRowChanged.connect(
                self._change_afk_time
            )

            self.close_change_timer = QPushButton(
                text="Return", parent=self, icon=TigerWalletImage.back
            )

            self.close_change_timer.resize(200, 50)
            self.close_change_timer.setIconSize(QSize(32, 32))
            self.close_change_timer.move(200, 386)
            self.close_change_timer.clicked.connect(
                lambda: [
                    self.timer_list_options.hide(),
                    self.list_.show(),
                    self.close_change_timer.close(),
                ]
            )

            if globalvar.configs["theme"] == "default_dark":
                self.timer_list_options.setStyleSheet(
                    "QListWidget {font-size: 20px;"
                    + "color: #eff1f3;"
                    + "padding: 7px;"
                    + "border: transparent;"
                    + "background: transparent;}"
                    + "QListView::item:hover{color: #b0c4de;"
                    "background: #363636;"
                    "border-radius: 8px;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.timer_list_options.setStyleSheet(
                    "QListWidget {font-size: 20px;"
                    + "color: black;"
                    + "padding: 7px;"
                    + "border: transparent;"
                    + "background: transparent;}"
                    + "QListView::item:hover{color: black;"
                    "background: #adb4bf;"
                    "border-radius: 8px;}"
                )

            self.close_change_timer.setStyleSheet(
                "QPushButton{background-color:  #b0c4de;"
                + "border-radius: 8px;"
                + "font-size: 18px;"
                + "color: black;"
                + "padding : 7px;}"
                + "QPushButton::hover{background-color: #99badd;}"
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
                self.master.afk_time = 500000
                self.timer_list_options.item(1).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 1

            elif choice == 2:
                self.master.afk_time = 1500000
                self.timer_list_options.item(2).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 2

            elif choice == 3:
                self.master.afk_time = 3000000
                self.timer_list_options.item(3).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 3

            elif choice == 4:
                self.master.afk_time = 10000000
                self.timer_list_options.item(4).setText(
                    opt + "      (current)"
                )
                self.timer_list_options.item(self.prev).setText(
                    self.timer_options[self.prev]
                )
                self.prev = 4

            elif choice == 5:
                self.master.afk_time = 40000000
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
            if (
                item.text()[: item.text().find(" ")]
                == globalvar.configs["rpc"]
            ):
                errbox("This is the current RPC")
                return

            else:
                item.setText(item.text() + "     (current)")
                globalvar.configs["rpc"] = item.text()[: item.text().find(" ")]
                self.rpc_list_options.item(self.prev).setText(
                    self.rpc_list_options.item(self.prev)
                    .text()
                    .replace("     (current)", "")
                )
                self.prev = self.rpc_list_options.indexFromItem(item).row()

                with open(globalvar.conf_file, "w") as f:
                    json.dump(globalvar.configs, f, indent=4)

                msgbox(
                    f"RPC successfully changed to {globalvar.configs['rpc']}"
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
                globalvar.account.key, password=new_password
            )

            with open(globalvar.nameofwallet, "w") as f:
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
            self.data = {}
            self.address = globalvar.account.address

        def work(self):
            self.is_done.emit(False)
            self.had_error = False

            dest_path = globalvar.dest_path

            url = f"https://api.ethplorer.io/getAddressHistory/{self.address}"
            key = "?apiKey=freekey&limit=100&showZeroValues=false"

            self.data = s.get(url + key, stream=True)
            self.data = self.data.json()

            if self.data["operations"] != self.master.data:
                self.has_changes = True
                self.is_done.emit(True)

    class WalletHistory(QWidget):
        def __init__(self):
            super().__init__()
            self.max_ = 25
            self.transfers = 0
            self.address = globalvar.account.address

            self.load_file()

            self.init_window()
            self.init_table()
            self.init_tip()
            self.init_refresh_button()

            self.unload_history_data()
            self.init_limit_selector()

            if "default" in globalvar.configs["theme"]:
                self.border.setStyleSheet(
                    "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.refresh.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    + "border-radius: 8px;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet("background-color: #1e1e1e;")

                self.history_title.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #6495ed;"
                    + "background: #1e1e1e;"
                )

                self.tip_label.setStyleSheet(
                    "font-size: 18px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

                self.history_table.setStyleSheet(
                    "QTableView{font-size: 16px;"
                    + "gridline-color: #363636;"
                    + "border-radius: 16px;"
                    + "color: #eff1f3;}"
                    # Upper part of the table
                    + "QHeaderView::section{background-color: #1e1e1e;"
                    + "border-radius: 8px;"
                    + "color: #b0c4de;"
                    + "margin: 5px;"
                    + "border: 1px solid gray;"
                    + "font-size: 16px;}"
                )

                if os.name == "nt":
                    self.selector.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        + "padding: 8px;"
                        + "font: 18px;"
                        + "border-radius: 4px;"
                        + "background: #1e1e1e;"
                        + "color: #b0c4de;}"
                        + "QAbstractItemView {selection-background-color: transparent;"
                        + "color: #b0c4de;"
                        + "border: 2px solid #778ba5;"
                        + "border-radius: 4px;"
                        + "padding: 8px;}"
                    )

                else:
                    self.selector.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        "border-radius: 4px;"
                        "color: #b0c4de;"
                        "font: 18px;}"
                    )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet("background-color: #eff1f3;")

                self.history_title.setStyleSheet(
                    "font-size: 30px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

                self.tip_label.setStyleSheet(
                    "font-size: 18px;"
                    + "color: black;"
                    + "background: transparent;"
                )

                self.history_table.setStyleSheet(
                    "QTableView{font-size: 16px;"
                    + "gridline-color: #c9cdcd;"
                    + "border-radius: 16px;"
                    + "color: black;}"
                    # Upper part of the table
                    + "QHeaderView::section{background-color: #eff1f3;"
                    + "border-radius: 8px;"
                    + "color: black;"
                    + "margin: 5px;"
                    + "border: 2px solid gray;"
                    + "font-size: 16px;}"
                )

                if os.name == "nt":
                    self.selector.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        + "padding: 8px;"
                        + "font: 18px;"
                        + "border-radius: 4px;"
                        + "background: #eff1f3;"
                        + "color: black;}"
                        + "QAbstractItemView {selection-background-color: transparent;"
                        + "color: black;"
                        + "border: 2px solid #778ba5;"
                        + "border-radius: 4px;"
                        + "padding: 8px;}"
                    )

                else:
                    self.selector.setStyleSheet(
                        "QComboBox {border: 2px solid #778ba5;"
                        "border-radius: 4px;"
                        "color: black;"
                        "font: 18px;}"
                    )

        def init_window(self) -> None:
            self.setFixedWidth(1300)
            self.setFixedHeight(720)
            self.setWindowTitle("TigerWallet  -  Transaction history")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(1280, 644)
            self.border.move(10, 60)

            self.history_title = QLabel("Transaction history", self)
            self.history_title.resize(320, 39)
            self.history_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_title.move(474, 40)

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
                QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            )

            self.history_table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.NoSelection
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

            if os.name != "nt":
                pal = self.selector.palette()

                if globalvar.configs["theme"] == "default_dark":
                    pal.setColor(
                        QtGui.QPalette.ColorRole.ButtonText,
                        QtGui.QColor("#b0c4de"),
                    )

                elif globalvar.configs["theme"] == "default_light":
                    pal.setColor(
                        QtGui.QPalette.ColorRole.ButtonText,
                        QtGui.QColor("black"),
                    )

                self.selector.setPalette(pal)

        def init_no_tx_msg(self) -> None:
            self.notx = QLabel(self)

            if self.total_tx == -1:
                self.notx.setText(
                    "Failed to fetch wallet history. Try again later"
                )
                return
            else:
                self.notx.setText("No transactions found")

            self.notx.resize(1300, 220)
            self.notx.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notx.move(0, 200)

            self.pix_holder = QLabel(self)
            self.pix_holder.resize(64, 64)
            self.pix_holder.move(364, 280)
            self.pix_holder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pix = QPixmap()
            self.pix.load(globalvar.imgfolder + "feelsbadman.png")

            self.pix = self.pix.scaled(
                QSize(64, 64),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            self.pix_holder.setPixmap(self.pix)

            if globalvar.configs["theme"] == "default_dark":
                self.notx.setStyleSheet(
                    "font-size: 40px;"
                    + "color: #6495ed;"
                    + "background: transparent;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.notx.setStyleSheet(
                    "font-size: 40px;"
                    + "color: black;"
                    + "background: transparent;"
                )

            self.pix_holder.setStyleSheet("background: transparent;")

        def init_tip(self) -> None:
            self.tip_label = QLabel(
                text="Tip: you can click on any row in column 3, 4, and 5 to copy the value",
                parent=self,
            )

            self.tip_label.resize(700, 66)
            self.tip_label.move(300, 84)
            self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def init_refresh_button(self) -> None:
            self.refresh = QPushButton(
                text="Refresh", parent=self, icon=TigerWalletImage.refresh
            )

            self.refresh.setIconSize(QSize(32, 32))
            self.refresh.resize(210, 40)
            self.refresh.move(1030, 98)

            def kill_thread(is_done):
                if is_done:
                    self.uhw.quit()
                    self.ubt.quit()

                    if self.uhw.has_changes:
                        if not self.notx.isHidden():
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
                        msgbox("No transactions found")

                    self.refresh.setEnabled(True)
                    self.refresh.setText("Refresh")

            self.uhw = UpdateHistoryWorker(self)
            self.ubt = QThread()

            self.uhw.moveToThread(self.ubt)
            self.ubt.started.connect(self.uhw.work)
            self.uhw.is_done.connect(kill_thread)

            self.refresh.clicked.connect(
                lambda: [
                    self.refresh.setText("Looking for transactions..."),
                    self.refresh.setEnabled(False),
                    self.ubt.start(),
                ]
            )

        def load_file(self) -> None:
            with open(
                globalvar.dest_path
                + "history.json", "rb"
            ) as f:
                self.data = orjson.loads(f.read())

                if "error" in self.data:
                    self.data = {"operations": []}

                    self.total_tx = -1
                    return

                self.data = self.data["operations"]
                sz = len(self.data)
                self.total_tx = sz

        # Timestamps
        def load_block_timestamps(self) -> list:
            from datetime import datetime

            times = [self.data[n]["timestamp"] for n in range(self.total_tx)]

            timess = [
                datetime.fromtimestamp(times[i]) for i in range(self.total_tx)
            ]

            return timess

        # Symbols
        def load_symbols(self) -> list:
            return [
                self.data[n]["tokenInfo"]["symbol"]
                for n in range(self.total_tx)
            ]

        # From addresses
        def load_from_addresses(self) -> list:
            return [self.data[n]["from"] for n in range(self.total_tx)]

        # To addresses
        def load_to_addresses(self) -> list:
            return [self.data[n]["to"] for n in range(self.total_tx)]

        # Hashes
        def load_hashes(self) -> list:
            return [
                self.data[n]["transactionHash"] for n in range(self.total_tx)
            ]

        # Amount
        def load_amount(self) -> list:
            return [self.data[n]["value"] for n in range(self.total_tx)]

        def unload_history_data(self) -> None:
            """
            Summon a pool of minions that willl
            perform list comprehension.

            The table gets filled up pretty much instantly.
            """
            with ThreadPoolExecutor(max_workers=15) as pool:
                self.times = pool.submit(self.load_block_timestamps).result()
                self.symbols = pool.submit(self.load_symbols).result()
                self.faddr = pool.submit(self.load_from_addresses).result()
                self.taddr = pool.submit(self.load_to_addresses).result()
                self.hashes = pool.submit(self.load_hashes).result()
                self.amount = pool.submit(self.load_amount).result()

                if self.total_tx == 0:
                    self.history_table.setRowCount(0)
                    self.init_no_tx_msg()
                    return

                # Timestamps
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 0, QTableWidgetItem(str(self.times[item]))
                        )
                        for item in range(self.max_)
                    ]
                )

                # Symbols
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 1, QTableWidgetItem(self.symbols[item])
                        )
                        for item in range(self.max_)
                    ]
                )

                # From addresses
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 2, QTableWidgetItem(self.faddr[item])
                        )
                        for item in range(self.max_)
                    ]
                )

                # To addresses
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 3, QTableWidgetItem(self.taddr[item])
                        )
                        for item in range(self.max_)
                    ]
                )

                # Hashes
                pool.submit(
                    [
                        self.history_table.setItem(
                            item, 4, QTableWidgetItem(self.hashes[item])
                        )
                        for item in range(self.max_)
                    ]
                )

                # Amount
                pool.submit(
                    [
                        self.history_table.setItem(
                            item,
                            5,
                            QTableWidgetItem(
                                rm_scientific_notation(
                                    float(self.amount[item])
                                )[:15]
                            ),
                        )
                        for item in range(self.max_)
                    ]
                )

            # Align labels to the center
            [
                self.history_table.item(i, ii).setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                for i in range(self.max_)
                for ii in range(6)
            ]

            # Make the labels less crammed
            [
                self.history_table.item(i, ii).setSizeHint(
                    QSize(self.header_sizes[ii], 52)
                )
                for i in range(self.max_)
                for ii in range(6)
            ]

            # Apply the setSizeHint settings
            self.history_table.resizeColumnsToContents()
            self.history_table.resizeRowsToContents()

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
                self.addr = None

                if self.column == 2:
                    self.addr = self.data[self.row]["from"]
                    self.clicked_item = (
                        f"{self.clicked_item} (Address: {self.addr})"
                    )

                elif self.column == 3:
                    self.addr = self.data[self.row]["to"]
                    self.clicked_item = (
                        f"{self.clicked_item} (Address: {self.addr})"
                    )

                QApplication.clipboard().setText(self.addr)
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

    # Actual user wallet
    class UserWallet(QWidget):
        def __init__(self):
            super().__init__()
            self.setMouseTracking(True)
            self.setup_main()

            self.init_afk_timer()
            self.init_threads()
            self.init_table()
            self.init_coin_row()
            self.init_side_bar()
            self.init_sidebar_style()
            self.init_unlock_wallet()
            self.init_lock_wallet_button()
            self.init_change_wallet_window()
            self.init_send_window()
            self.init_receive_window()
            self.init_addressbook_window()
            self.init_settings_window()
            self.init_history_window()
            self.start_afk_timer()

            with ThreadPoolExecutor() as pool:
                pool.submit(self.fill_up_table)

            if "default" in globalvar.configs["theme"]:
                # The border that fills up space
                self.border.setStyleSheet(
                    "border: 1px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "background: transparent;"
                )

                self.add_coin_btn.setStyleSheet(
                    "QPushButton {background-color: #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.cancel.setStyleSheet(
                    "QPushButton {background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.continue_btn.setStyleSheet(
                    "QPushButton {background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.default_coin_btn.setStyleSheet(
                    "QPushButton {background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.del_coin_btn.setStyleSheet(
                    "QPushButton {background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.closebtn.setStyleSheet(
                    "QPushButton {background-color:  #6495ed;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #6ca0dc;}"
                )

                self.add_contact.setStyleSheet(
                    "QPushButton {background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.del_contact.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.close_book.setStyleSheet(
                    "QPushButton{background-color:  #6495ed;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #6ca0dc;}"
                )

                self.errlabel.setStyleSheet(
                    "font-size: 17px;"
                    + "color: red;"
                    + "background: transparent;"
                )

                self.close_send_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black;}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.send_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.box1.setStyleSheet("background: transparent;")
                self.box2.setStyleSheet("background: transparent;")
                self.box3.setStyleSheet("background: transparent;")
                self.box4.setStyleSheet("background: transparent;")

                self.unlock_wallet_box.setStyleSheet(
                    "background: #1e1e1e;"
                    "border: 1px solid #778ba5;"
                    "border-radius: 16px;"
                )

                self.unlock_wallet_lbl.setStyleSheet(
                    "border: 0px solid #1e1e1e;"
                    "font: 21px;"
                    "color: #eff1f3;"
                )

                self.showhidepass.setStyleSheet(
                    "QPushButton{background-color:  #778ba5;"
                    "border-radius: 8px;}"
                    "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.apply_default_dark_theme()

            elif globalvar.configs["theme"] == "default_light":
                self.apply_default_light_theme()

        def closeEvent(self, event):
            app.closeAllWindows()
            event.accept()

        def mouseMoveEvent(self, event):
            def verify_if_afk():
                if event.type() != Qt.MouseButton.NoButton:
                    self.black_out_window()
                    self.unlock_wallet_box.show()
                    self.setStyleSheet("background: black;")

            self.afk_timer.timeout.connect(verify_if_afk)

        def setup_main(self):
            self.setFixedWidth(1100)
            self.setFixedHeight(700)
            self.setWindowTitle(f"TigerWallet  -  {globalvar.nameofwallet}")
            align_to_center(self)

            self.border = QLabel(self)
            self.border.resize(790, 620)
            self.border.move(166, 60)

            self.val = QLabel(self)
            self.val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.address = globalvar.account.address
            self.assets = globalvar.assets_details

            pool = ThreadPoolExecutor()
            self.eth_price = pool.submit(get_eth_price).result()

            self._m = pool.submit(
                lambda: w3.eth.get_balance(self.address)
            ).result()

            self._m = pool.submit(
                lambda: w3.from_wei(self._m if not None else 0, "ether")
            ).result()

            self.money = float(self._m) * float(self.eth_price)

            self.val.setText(f"Balance: ${str(self.money)}")

            if len(self.val.text() + str(self.money)) == 16:
                self.val.resize(214 + len(str(self.money)), 40)
                self.val.move(438, 38)
            else:
                self.val.resize(454 + len(str(self.money)), 40)
                self.val.move(310, 38)

            self.tab = 0
            self.browser_active = False
            self.tab2_hidden = False
            self.settings_tab_active = False
            self.add_contact_section2 = False
            self.add_contact_section3 = False
            self.addcointab = False
            self.rmcointab = False
            self.donation_window_active = False
            self.afk_time = 1500000

        def init_afk_timer(self):
            self.afk_timer = QTimer()

        def init_threads(self):
            # Main Thread/worker
            self.thread = QThread()
            self.worker = TimedMonitorForNewTransfers()

            self.worker.moveToThread(self.thread)

            def add_coin_if_new_one_arrived(cond):
                if cond:
                    self.add_coin(
                        self.worker.new_tokens['name'],
                        self.worker.new_tokens['address'],
                        self.worker.new_tokens['symbol'],
                        invoked_from_worker=True
                    )

            self.worker.received_new_tokens.connect(
                add_coin_if_new_one_arrived
            )
            self.worker.timer.timeout.connect(self.worker.work)
            self.thread.started.connect(
                lambda: self.worker.timer.start(15000)
            )
            self.thread.start()

            self.update_balance_thread = QThread()
            self.update_balance_worker = TimedUpdateTotalBalance()

            self.update_balance_worker.moveToThread(
                self.update_balance_thread
            )
            self.update_balance_worker.balance.connect(
                self.update_balance
            )
            self.update_balance_worker.timer.timeout.connect(
                self.update_balance_worker.work
            )
            self.update_balance_thread.started.connect(
                lambda: self.update_balance_worker.timer.start(10000)
            )
            self.update_balance_thread.start()

            # Gas update Thread/Worker
            self._gas_th = QThread()
            self._gasupdate = TimedUpdateGasFeeWorker()

            self._gasupdate.moveToThread(self._gas_th)
            self._gasupdate.timer.timeout.connect(self._gasupdate.work)
            self._gas_th.started.connect(
                lambda: self._gasupdate.timer.start(5000)
            )
            self._gas_th.start()

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
            self.tm.start(15000)
            self.update_price_thread.start()

        def init_table(self):
            b = ThreadPoolExecutor().submit(
                lambda: w3.from_wei(
                    w3.eth.get_balance(self.address), "ether"
                )
            ).result()

            self.ethbal = QTableWidgetItem(f" {str(b)[:15]}")

            self.table = QTableWidget(self)
            self.table.setRowCount(len(globalvar.assets_addr) + 1)
            self.table.setColumnCount(3)
            self.table.setColumnWidth(0, 278)
            self.table.setColumnWidth(1, 230)
            self.table.setColumnWidth(2, 228)
            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setVisible(True)
            self.table.resize(748, 490)
            self.table.move(188, 108)
            self.table.setItem(0, 0, QTableWidgetItem(" ETHER (ETH)"))
            self.table.setItem(0, 1, self.ethbal)
            self.table.setItem(0, 2, QTableWidgetItem(" " + self.eth_price))
            self.table.item(0, 0).setIcon(TigerWalletImage.eth_img)

            self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            self.table.setEditTriggers(
                QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.NoSelection
            )

            self.table.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.Fixed
            )

            self.table.setHorizontalHeaderItem(0, QTableWidgetItem("Asset"))
            self.table.setHorizontalHeaderItem(1, QTableWidgetItem("Amount"))
            self.table.setHorizontalHeaderItem(
                2, QTableWidgetItem("Market Price")
            )
            self.table.setIconSize(QSize(32, 32))

        def init_coin_row(self):
            self.add_coin_btn = QPushButton(
                text="Add a coin",
                parent=self,
                icon=TigerWalletImage.plus
            )

            self.add_coin_btn.setFixedSize(190, 46)
            self.add_coin_btn.setIconSize(QSize(32, 32))
            self.add_coin_btn.move(226, 608)
            self.add_coin_btn.show()
            self.add_coin_btn.clicked.connect(self.init_add_coin_window)

            self.default_coin_btn = QPushButton(
                "Restore default coin list", self
            )
            self.default_coin_btn.setFixedSize(260, 46)
            self.default_coin_btn.setIconSize(QSize(32, 32))
            self.default_coin_btn.move(431, 608)
            self.default_coin_btn.show()
            self.default_coin_btn.clicked.connect(self.restore_default_coins)

            self.del_coin_btn = QPushButton(
                text="Remove a coin",
                parent=self,
                icon=TigerWalletImage.delete
            )
            self.del_coin_btn.setFixedSize(190, 46)
            self.del_coin_btn.setIconSize(QSize(32, 32))
            self.del_coin_btn.move(706, 608)
            self.del_coin_btn.show()
            self.del_coin_btn.clicked.connect(self.init_rm_coin_window)

        def init_add_coin_window(self):
            self.addcointab = True
            self.add_coin_btn.hide()
            self.del_coin_btn.hide()
            self.default_coin_btn.hide()
            self.table.hide()

            # Coin address
            self.coinaddr = QLineEdit(self)
            self.coinaddr.setPlaceholderText("ERC-20 token contract address")
            self.coinaddr.resize(460, 36)
            self.coinaddr.move(368, 180)
            self.coinaddr.setMaxLength(42)
            self.coinaddr.show()
            self.errlbl = QLabel("Invalid ERC-20 contract address", self)
            self.errlbl.resize(1100, 50)
            self.errlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.errlbl.move(0, 208)

            self.contractlbl = QLabel("Contract:", self)
            self.contractlbl.resize(90, 30)
            self.contractlbl.move(274, 182)
            self.contractlbl.show()

            # Coin name
            self.coinname = QLineEdit(self)
            self.coinname.resize(460, 36)
            self.coinname.move(368, 256)
            self.coinname.setEnabled(False)
            self.coinname.show()

            self.coinnamelbl = QLabel("Name:", self)
            self.coinnamelbl.resize(90, 30)
            self.coinnamelbl.move(274, 258)
            self.coinnamelbl.show()

            # Coin symbol
            self.coinsym = QLineEdit(self)
            self.coinsym.resize(460, 36)
            self.coinsym.move(368, 332)
            self.coinsym.setEnabled(False)
            self.coinsym.show()

            self.coinsymlbl = QLabel("Symbol:", self)
            self.coinsymlbl.resize(90, 30)
            self.coinsymlbl.move(274, 334)
            self.coinsymlbl.show()

            # Decimals
            self.coindec = QLineEdit(self)
            self.coindec.resize(460, 36)
            self.coindec.move(368, 408)
            self.coindec.setEnabled(False)
            self.coindec.show()

            self.coindeclbl = QLabel("Decimal:", self)
            self.coindeclbl.resize(90, 30)
            self.coindeclbl.move(274, 410)
            self.coindeclbl.show()

            def _validate_address(addr):
                if self.errlbl.text() == "Asset is already in your asset list":
                    self.errlbl.setText("Invalid ERC-20 contract address")

                if len(addr) == 42:
                    if not w3.is_address(addr):
                        self.errlbl.show()
                        return

                    else:
                        self.errlbl.hide()

                    if addr in globalvar.assets_addr:
                        self.errlbl.setText(
                            "Asset is already in your asset list"
                        )
                        self.errlbl.show()
                        return

                    try:
                        self.c = create_contract(addr)

                        with ThreadPoolExecutor() as pool:
                            pool.submit(
                                lambda: self.coinname.setText(
                                    self.c.functions.name().call()
                                )
                            )

                            pool.submit(
                                lambda: self.coinsym.setText(
                                    self.c.functions.symbol().call()
                                )
                            )

                            pool.submit(
                                lambda: self.coindec.setText(
                                    str(self.c.functions.decimals().call())
                                )
                            )

                        self.continue_add_coin_btn.setEnabled(True)
                    except Exception:
                        self.errlbl.show()
                        print('err')
                        return

                else:
                    self.errlbl.hide()
                    self.continue_add_coin_btn.setEnabled(False)

            # Add entered coin button
            self.continue_add_coin_btn = QPushButton(
                text="Add coin",
                parent=self,
                icon=TigerWalletImage.plus
            )

            def launch_add_coin():
                self.add_coin(
                    self.coinname.text(),
                    self.coinaddr.text(),
                    self.coinsym.text()
                )

            self.continue_add_coin_btn.setFixedSize(240, 62)
            self.continue_add_coin_btn.setIconSize(QSize(32, 32))
            self.continue_add_coin_btn.move(560, 500)
            self.continue_add_coin_btn.show()
            self.continue_add_coin_btn.setEnabled(False)
            self.continue_add_coin_btn.clicked.connect(launch_add_coin)

            self.close_add_coin_btn = QPushButton(
                text="Close",
                parent=self,
                icon=TigerWalletImage.close
            )

            self.close_add_coin_btn.setFixedSize(240, 62)
            self.close_add_coin_btn.setIconSize(QSize(32, 32))
            self.close_add_coin_btn.move(300, 500)
            self.close_add_coin_btn.show()
            self.close_add_coin_btn.clicked.connect(
                lambda: [
                    self.coinaddr.close(),
                    self.errlbl.close(),
                    self.contractlbl.close(),
                    self.coinname.close(),
                    self.coinnamelbl.close(),
                    self.coinsym.close(),
                    self.coinsymlbl.close(),
                    self.coindec.close(),
                    self.coindeclbl.close(),
                    self.continue_add_coin_btn.close(),
                    self.close_add_coin_btn.close(),
                    self.add_coin_btn.show(),
                    self.del_coin_btn.show(),
                    self.default_coin_btn.show(),
                    self.table.show(),
                ]
            )

            self.coinaddr.textChanged.connect(_validate_address)

            if "default" in globalvar.configs["theme"]:
                self.continue_add_coin_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #6ca0dc;}"
                )

                self.close_add_coin_btn.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8px;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #6ca0dc;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                # Address
                self.coinaddr.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.contractlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #eff1f3;"
                    + "background: #1e1e1e;"
                )

                # Text that gets displayed when address is invalid
                self.errlbl.setStyleSheet(
                    "font-size: 17px;"
                    + "color: red;"
                    + "background: transparent;"
                )

                # Name
                self.coinname.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.coinnamelbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #eff1f3;"
                    + "background: #1e1e1e;"
                )

                # Symbol
                self.coinsym.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.coinsymlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #eff1f3;"
                    + "background: #1e1e1e;"
                )

                # Decimal
                self.coindec.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.coindeclbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: #eff1f3;"
                    + "background: #1e1e1e;"
                )

            elif globalvar.configs["theme"] == "default_light":
                # Address
                self.coinaddr.setStyleSheet(
                    "color: black;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.contractlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

                # Text that gets displayed when address is invalid
                self.errlbl.setStyleSheet(
                    "font-size: 17px;"
                    + "color: red;"
                    + "background: transparent;"
                )

                # Name
                self.coinname.setStyleSheet(
                    "color: black;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.coinnamelbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

                # Symbol
                self.coinsym.setStyleSheet(
                    "color: black;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.coinsymlbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

                # Decimal
                self.coindec.setStyleSheet(
                    "color: black;"
                    + "border: 1px solid #6ca0dc;"
                    + "font-size: 14px;"
                    + "border-radius: 16px;"
                    + "padding: 4px;"
                )

                self.coindeclbl.setStyleSheet(
                    "font-size: 20px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

        def init_rm_coin_window(self):
            self.rmcointab = True

            self.stop_thread()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()
            self.val.hide()

            self.uppermsg = QLabel(
                "Select which tokens you want to remove", self
            )
            self.uppermsg.resize(len(self.uppermsg.text()) + 540, 30)
            self.uppermsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.uppermsg.move(272, 40)
            self.uppermsg.show()

            # Cancel Button
            self.rm_coin_cancel = QPushButton(
                text="Cancel",
                parent=self,
                icon=TigerWalletImage.close
            )
            self.rm_coin_cancel.setFixedSize(200, 46)
            self.rm_coin_cancel.setIconSize(QSize(32, 32))
            self.rm_coin_cancel.move(300, 608)
            self.rm_coin_cancel.show()

            def cancel_rm_coin_btn_function():
                self.table.clearSelection()
                self.rm_coin_continue.close()
                self.rm_coin_cancel.close()
                self.uppermsg.close()
                self.table.setSelectionMode(
                    QtWidgets.QAbstractItemView.SelectionMode.NoSelection
                )
                self.thread.start()
                self.add_coin_btn.show()
                self.default_coin_btn.show()
                self.del_coin_btn.show()
                self.val.show()

            self.rm_coin_cancel.clicked.connect(
                cancel_rm_coin_btn_function
            )

            self.rm_coin_continue = QPushButton(
                text="Continue",
                parent=self,
                icon=TigerWalletImage.eth_img
            )
            self.rm_coin_continue.setFixedSize(200, 46)
            self.rm_coin_continue.setIconSize(QSize(32, 32))
            self.rm_coin_continue.move(580, 608)
            self.rm_coin_continue.show()
            self.rm_coin_continue.clicked.connect(self.rm_coin)

            self.table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
            )

            self.table.setSelectionBehavior(
                QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )

            if "default" in globalvar.configs["theme"]:
                self.rm_coin_continue.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.rm_coin_cancel.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.uppermsg.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #eff1f3;"
                    + "background: #1e1e1e;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.uppermsg.setStyleSheet(
                    "font-size: 30px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

        def init_side_bar(self):
            self.button_box = QWidget(self)
            self.button_box.resize(156, 700)
            self.button_box.setStyleSheet("background: transparent;")

            # Load up sidebar buttons
            self.sidebar_button = [
                QPushButton(self.button_box) for i in range(8)
            ]
            self.button_size = [156, 50]
            self.sidebar_button[0].setIconSize(QSize(64, 64))

            for i in range(8):
                self.sidebar_button[i].setFixedSize(*self.button_size)
                self.sidebar_button[i].setIconSize(QSize(32, 32))

            # Change wallet
            self.sidebar_button[0].setText(" Change wallet")
            self.sidebar_button[0].setIcon(TigerWalletImage.wallet_blue)
            self.sidebar_button[0].move(2, 50)
            self.sidebar_button[0].clicked.connect(self.show_tab1_contents)

            # Send
            self.sidebar_button[1].setText(" Send")
            self.sidebar_button[1].setIcon(TigerWalletImage.send_blue)
            self.sidebar_button[1].move(2, 110)
            self.sidebar_button[1].clicked.connect(self.show_tab2_contents)

            # Receieve
            self.sidebar_button[2].setText(" Receive")
            self.sidebar_button[2].setIcon(TigerWalletImage.receive_blue)
            self.sidebar_button[2].move(2, 170)
            self.sidebar_button[2].clicked.connect(self.show_tab3_contents)

            # Address book
            self.sidebar_button[3].setText(" Address Book")
            self.sidebar_button[3].setIcon(TigerWalletImage.address_book_blue)
            self.sidebar_button[3].move(2, 230)
            self.sidebar_button[3].clicked.connect(self.show_tab4_contents)

            # History
            self.sidebar_button[4].setText(" History")
            self.sidebar_button[4].setIcon(TigerWalletImage.history_blue)
            self.sidebar_button[4].move(2, 290)
            self.sidebar_button[4].clicked.connect(self.show_tab5_contents)

            # Settings
            self.sidebar_button[5].setText(" Settings")
            self.sidebar_button[5].setIcon(TigerWalletImage.settings_blue)
            self.sidebar_button[5].move(2, 350)
            self.sidebar_button[5].clicked.connect(self.show_tab6_contents)

            # Dark/light mode switch
            self.sidebar_button[6].move(2, 590)
            self.sidebar_button[6].clicked.connect(self.toggle_mode)

            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[6].setIcon(TigerWalletImage.moon_blue)
            else:
                self.sidebar_button[6].setIcon(TigerWalletImage.sun_blue)

            # Donation button
            self.sidebar_button[7].setIcon(TigerWalletImage.donate_blue)
            self.sidebar_button[7].move(2, 650)
            self.sidebar_button[7].clicked.connect(self.init_donate_window)

            self.button_box.show()

        # FIRST button
        def init_change_wallet_window(self):
            self.box1 = QWidget(self)
            self.box1.resize(790, 620)
            self.box1.move(166, 50)
            self.box1.hide()

            self.change_wallet_title = QLabel(
                text="Select your wallet", parent=self.box1
            )

            self.change_wallet_title.setFixedSize(380, 50)
            self.change_wallet_title.move(180, 40)
            self.change_wallet_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Wallet selection
            self.wallet_list = QListWidget(self.box1)
            self.wallet_list.resize(730, 412)
            self.wallet_list.move(30, 110)
            self.wallet_list.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.wallet_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.wallets = json_contents["wallets"]

            def replace_backslash(item):
                return item.replace("\\", "/")

            self.wallets = list(map(replace_backslash, self.wallets))

            for wallets in enumerate(self.wallets):
                self.wallet_list.insertItem(*wallets)

            for i in range(len(self.wallets)):
                self.wallet_list.item(i).setSizeHint(QSize(730, 50))

                if self.wallet_list.item(i).text() == globalvar.nameofwallet:
                    self.wallet_list.item(i).setText(
                        self.wallet_list.item(i).text() + " (current)"
                    )

            # Click event
            def _clicked(item):
                if "(current)" in item.text():
                    errbox("This is the current wallet")
                    self.wallet_list.clearSelection()
                    return

                self.item = item.text()

            self.wallet_list.itemClicked.connect(_clicked)
            self.item = None

            # Cancel button to return to the grid view
            self.cancel = QPushButton(
                text="Cancel", parent=self.box1, icon=TigerWalletImage.close
            )
            self.cancel.setFixedSize(240, 62)
            self.cancel.setIconSize(QSize(32, 32))
            self.cancel.move(120, 530)

            self.continue_btn = QPushButton(
                text="Use selected wallet",
                parent=self.box1,
                icon=TigerWalletImage.eth_img,
            )
            self.continue_btn.setFixedSize(240, 62)
            self.continue_btn.setIconSize(QSize(32, 32))
            self.continue_btn.move(390, 530)
            self.continue_btn.clicked.connect(self.launch_chosen_wallet)

            self.cancel.clicked.connect(self.clear_tab1_contents)

        # SECOND button
        def init_send_window(self):
            """ Send crypto window """
            self.box2 = QWidget(self)
            self.box2.resize(790, 620)
            self.box2.move(166, 0)
            self.box2.hide()

            self.names = globalvar.assets_details["name"]
            self.symbols = globalvar.assets_details["symbol"]
            self.assetsval = globalvar.assets_details["value"]
            self.assets_addr = globalvar.assets_addr
            self.index = 0

            bal2 = w3.from_wei(
                w3.eth.get_balance(self.address),
                "ether"
            )
            self.ethamount = f"~ {str(bal2)[:17]} ETH"

            self.is_valid_erc20_address = False
            self.lblsize = [78, 30]

            self.sendlabel = QLabel("Send crypto", self.box2)
            self.sendlabel.setFixedSize(210, 50)
            self.sendlabel.move(270, 37)
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
            self.asset_list.resize(400, 44)
            self.asset_list.move(132, 176)
            self.asset_list.show()
            self.asset_list.insertItem(0, "ETHER (ETH)")
            self.asset_list.setItemIcon(0, TigerWalletImage.eth_img)
            self.asset_list.setIconSize(QSize(24, 24))

            if os.name != "nt":
                pal = self.asset_list.palette()

                if globalvar.configs["theme"] == "default_dark":
                    pal.setColor(
                        QtGui.QPalette.ColorRole.ButtonText,
                        QtGui.QColor("#b0c4de"),
                    )

                elif globalvar.configs["theme"] == "default_light":
                    pal.setColor(
                        QtGui.QPalette.ColorRole.ButtonText,
                        QtGui.QColor("black"),
                    )

                self.asset_list.setPalette(pal)

            for i in range(0, len(self.names)):
                self.asset_list.insertItem(
                    i + 1,
                    f"{self.names[i]} ({self.symbols[i]})"
                )

                self.asset_list.setItemIcon(
                    i + 1,
                    QIcon(self.assets["image"][i])
                )

            """ Display the word 'Asset' before entry field """
            self.assetlbl = QLabel("Asset:", self.box2)
            self.assetlbl.resize(*self.lblsize)
            self.assetlbl.move(48, 182)

            """ Display user balance of chosen asset """
            self.estimate_amount = QLabel(self.box2)
            self.estimate_amount.resize(230, 40)
            self.estimate_amount.move(550, 176)

            if self.ethamount != 0:
                bal = w3.from_wei(
                    w3.eth.get_balance(self.address),
                    "ether"
                )
                self.estimate_amount.setText(f"~{str(bal)[:17]} ETH")

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
                            f"0.0 {elf.symbols[num - 1]}"
                        )

                    else:
                        amnt = str(w3.from_wei(self.c, "ether"))[:17]
                        self.estimate_amount.setText(
                            f"~{amnt} {self.symbols[num - 1]}"
                        )

            self.estimate_amount.show()
            self.asset_list.currentIndexChanged.connect(_update_avail)

            # Send to
            def _validate_address(inp):
                if len(inp) == 42:
                    if not w3.is_address(inp):
                        self.errlabel.setText(
                            "This is not a valid ERC-20 address"
                        )
                        self.errlabel.show()
                        return

                    else:
                        self.errlabel.hide()

                    try:
                        _contract = create_contract(HexBytes(inp))
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
            self.typeaddr.setPlaceholderText(" ERC-20 address")
            self.typeaddr.resize(400, 32)
            self.typeaddr.move(134, 260)
            self.typeaddr.setMaxLength(42)
            self.typeaddr.textChanged.connect(_validate_address)

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
            validator.setDecimals(21)
            validator.setTop(1000000000)
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
            self.slider.move(562, 326)
            self.slider.resize(180, 26)

            def _update(num):
                if self.asset_list.currentIndex() == 0:
                    self._bal = str(
                        w3.from_wei(w3.eth.get_balance(self.address), "ether")
                    )

                    if self.slider.value() == 0:
                        self.amount.setText("")

                    elif self.slider.value() == 100:
                        self.amount.setText(self._bal)

                    else:
                        self.amount.setText(
                            rm_scientific_notation(
                                str(float(self._bal) / float(100 / num))[:17]
                            )
                        )

                else:
                    if self.assetsval == "0.0":
                        return

                    self.amount.setText(
                        rm_scientific_notation(
                            str(float(self.assetsval) / float(100 / num))[:17]
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
            self.gasfee.setPlaceholderText(" Fetching gas price...")
            self.gasfee.setEnabled(False)

            def _update_gas(newprice):
                self.gasfee.setText(newprice)

            """
                This is needed so that the user doesn't
                    have to wait 10 seconds for the
                    gas fee to get displayed, initially
            """
            self._single_gas_worker = FetchGasWorker()
            self._one_time_thread = QThread()
            self._single_gas_worker.moveToThread(self._one_time_thread)
            self._one_time_thread.started.connect(
                self._single_gas_worker.work
            )
            self._single_gas_worker.gas.connect(_update_gas)
            self._one_time_thread.start()

            self._gasupdate.gas.connect(_update_gas)

            # Close/Send buttons
            self.close_send_btn = QPushButton(
                text="Close",
                parent=self.box2,
                icon=TigerWalletImage.close
            )
            self.close_send_btn.setFixedSize(240, 62)
            self.close_send_btn.setIconSize(QSize(32, 32))
            self.close_send_btn.move(120, 490)

            self.send_btn = QPushButton(
                text="Continue",
                parent=self.box2,
                icon=TigerWalletImage.eth_img,
            )
            self.send_btn.setFixedSize(240, 62)
            self.send_btn.setIconSize(QSize(32, 32))
            self.send_btn.move(390, 490)

            # Complete transaction
            class _EnterPass(QWidget):
                def __init__(self, master):
                    super().__init__()
                    self.opt = 1
                    self.master = master
                    self._gas = 0.0
                    self._priority = 0.0

                    self.init_confirmation()
                    self.init_buttons()

                    if "default" in globalvar.configs["theme"]:
                        self.frm.setStyleSheet(
                            "border: 2px solid #778ba5;"
                            + "border-radius: 16px;"
                            + "background: transparent;"
                        )

                        self.send.setStyleSheet(
                            "QPushButton{background-color:  #b0c4de;"
                            + "border-radius: 8px;"
                            + "font-size: 20px;"
                            + "color: black}"
                            + "QPushButton::hover{background-color: #99badd;}"
                        )

                        self.cancel.setStyleSheet(
                            "QPushButton{background-color:  #b0c4de;"
                            + "border-radius: 8px;"
                            + "font-size: 20px;"
                            + "color: black}"
                            + "QPushButton::hover{background-color: #99badd;}"
                        )

                    if globalvar.configs["theme"] == "default_dark":
                        self.setStyleSheet("background-color: #1e1e1e")

                        self.topmsg.setStyleSheet(
                            "font-size: 30px;"
                            + "color: #eff1f3;"
                            + "background: #1e1e1e;"
                        )

                        self.notice_msg.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #eff1f3;"
                            + "background: transparent;"
                            + "border: 1px solid #b0c4de;"
                            + "border-radius: 8px;"
                        )

                        self.assetlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #eff1f3;"
                            + "background: transparent;"
                        )

                        self.sendtolbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #eff1f3;"
                            + "background: transparent;"
                        )

                        self.send_to_address.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #b0c4de;"
                            + "background: transparent;"
                        )

                        self.user_asset.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #b0c4de;"
                            + "background: transparent;"
                        )

                        self.am.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #b0c4de;"
                            + "background: transparent;"
                        )

                        self.amlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #eff1f3;"
                            + "background: transparent;"
                        )

                        self.gaslbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: white;"
                            + "background: transparent;"
                        )

                        self.gas_amount.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #b0c4de;"
                            + "background: transparent;"
                        )

                        self.prioritylbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #eff1f3;"
                            + "background: transparent;"
                        )

                        self.priority.setStyleSheet(
                            "font-size: 17px;"
                            + "color: #b0c4de;"
                            + "background: transparent;"
                        )

                        self.total.setStyleSheet(
                            "font-size: 30px;"
                            + "color: white;"
                            + "background: transparent;"
                            + "border: 2px solid #b0c4de;"
                            + "border-radius: 16px;"
                        )

                    elif globalvar.configs["theme"] == "default_light":
                        self.setStyleSheet("background-color: #eff1f3")

                        self.topmsg.setStyleSheet(
                            "font-size: 30px;"
                            + "color: black;"
                            + "background: #eff1f3;"
                        )

                        self.notice_msg.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                            + "border: 1px solid #b0c4de;"
                            + "border-radius: 8px;"
                        )

                        self.assetlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.sendtolbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.send_to_address.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.user_asset.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.am.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.amlbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.gaslbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.gas_amount.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.prioritylbl.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.priority.setStyleSheet(
                            "font-size: 17px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

                        self.total.setStyleSheet(
                            "font-size: 30px;"
                            + "color: black;"
                            + "background: transparent;"
                            + "border: 2px solid #b0c4de;"
                            + "border-radius: 16px;"
                        )

                def init_confirmation(self):
                    if (
                        self.master.index == -1
                        or self.master.index == 0
                    ):
                        self.sym = "ETH"

                    else:
                        self.sym = self.master.symbols[self.master.index]

                    if (
                        self.master.index == -1
                        or self.master.index == 0
                    ):
                        self.asset = 'Ether'

                    else:
                        self.asset = self.master.names[self.master.index]

                    self.setFixedWidth(650)
                    self.setFixedHeight(530)
                    self.setWindowTitle("TigerWallet  -  Send confirmation")

                    align_to_center(self)

                    self.frm = QLabel(self)
                    self.frm.resize(598, 460)
                    self.frm.move(26, 54)

                    self.topmsg = QLabel("Send ERC-20 asset", self)
                    self.topmsg.resize(298, 28)
                    self.topmsg.move(164, 40)
                    self.topmsg.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    self.notice_msg = QLabel(
                        text="Below is a summary of your transaction:",
                        parent=self
                    )
                    self.notice_msg.resize(320, 46)
                    self.notice_msg.move(152, 82)
                    self.notice_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    self.assetlbl = QLabel("Asset:", self)
                    self.assetlbl.resize(50, 40)
                    self.assetlbl.move(70, 137)

                    self.user_asset = QLabel(self)
                    self.user_asset.resize(360, 40)
                    self.user_asset.move(158, 140)
                    self.user_asset.setText(f"<u>{self.asset}</u>")

                    self.sendtolbl = QLabel("Send to:", self)
                    self.sendtolbl.resize(100, 40)
                    self.sendtolbl.move(70, 177)

                    self.send_to_address = QLabel(self)
                    self.send_to_address.resize(460, 40)
                    self.send_to_address.move(158, 180)
                    self.send_to_address.setText(
                        f"<u>{self.master.typeaddr.text()}</u>"
                    )

                    self.amlbl = QLabel("Amount:", self)
                    self.amlbl.resize(100, 40)
                    self.amlbl.move(70, 217)

                    self.am = QLabel(self)
                    self.am.resize(400, 40)
                    self.am.move(158, 220)

                    def _quick_price_check():
                        self.p = float(get_price(self.sym))
                        amount = float(self.master.amount.text())
                        amount_total = self.p*amount
                        amount_as_str = rm_scientific_notation(amount_total)

                        self.am.setText(
                            f"<u>{self.master.amount.text()} {self.sym}</u>"
                            + f" (Value: ~${amount_as_str[:13]})"
                        )

                    _tmp = Thread(target=_quick_price_check)
                    _tmp.run()

                    self.gas_amount = QLabel(self)

                    if "(" in self.master.gasfee.text():
                        gfee = self.master.gasfee.text()

                        self.g = gfee[:gfee.find("(") - 1]
                        self.g = f"<u>{self.g.replace(' ' ,'', 1)}</u>"
                        self.g += " (This can change)"

                    else:

                        def _mini_gas_fetch():
                            self.g = self.master.gasfee.text()
                            self.g = float(self.g)
                            self.p = (
                                w3.from_wei(self.g, "ether") * 1000000000
                            )
                            self.p = float(self.p) * float(get_eth_price())
                            self.p *= 23000

                            self.fiat = str(round(self.p, 2))
                            return

                        _minigas = Thread(target=_mini_gas_fetch)
                        _minigas.run()

                        self.gas_amount.setText(
                            f"$<u>{self.fiat} ({self.g} GWEI</u>)"
                        )

                    self.gaslbl = QLabel("Gas:", self)
                    self.gaslbl.resize(100, 40)
                    self.gaslbl.move(70, 257)

                    self.gas_amount.resize(400, 40)
                    self.gas_amount.move(158, 260)
                    self.gas_amount.setText(self.g)

                    self.priority = QLabel(self)

                    def _quick_priority_check():
                        p = w3.eth.max_priority_fee
                        p = float(p) * 120

                        p_in_gwei = rm_scientific_notation(
                            w3.from_wei(p, "ether") * 1000000000
                        )

                        val = float(w3.from_wei(p, "ether"))
                        val = val * float(get_eth_price())
                        val *= 23000
                        val = round(val, 3)

                        self.priority.setText(
                            f"<u>{p_in_gwei} GWEI</u> (Value: ~${val})"
                        )

                    _tmp = Thread(target=_quick_priority_check)
                    _tmp.run()

                    self.prioritylbl = QLabel("Priority:", self)
                    self.prioritylbl.resize(100, 40)
                    self.prioritylbl.move(70, 297)

                    self.priority.resize(400, 40)
                    self.priority.move(158, 300)

                    self.total = QLabel(self)
                    self.total.resize(400, 46)
                    self.total.move(126, 350)
                    self.total.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    def calculate_total_value():
                        amount = self.am.text()
                        amount = amount[
                            amount.find('$')+1
                            : amount.find(')')-1
                        ]
                        amount = float(amount)

                        gas_text = self.gas_amount.text()
                        gas = gas_text[
                            gas_text.find("$")+ 1
                            : gas_text.rfind("<")- 1
                        ]
                        self._gas = gas
                        gas = float(gas)

                        priority = self.priority.text()
                        priority = priority[
                            priority.find("$")+1
                            : priority.rfind(")")-1
                        ]
                        self._priority = priority
                        priority = float(priority)

                        _total = amount + gas + priority
                        _total = round(_total, 5)

                        self.total.setText(f"TOTAL: ~${str(_total)}")

                    calculate_total_value()

                def init_buttons(self):
                    self.cancel = QPushButton(
                        text="Gotta make changes",
                        parent=self,
                        icon=TigerWalletImage.close,
                    )

                    self.cancel.setFixedSize(242, 62)
                    self.cancel.setIconSize(QSize(32, 32))
                    self.cancel.move(72, 418)
                    self.cancel.clicked.connect(self.close)

                    self.send = QPushButton(
                        text="Everything looks good",
                        parent=self,
                        icon=TigerWalletImage.continue_,
                    )

                    self.send.setFixedSize(242, 62)
                    self.send.setIconSize(QSize(32, 32))
                    self.send.move(340, 418)
                    self.send.clicked.connect(self.init_pass_window)

                def init_pass_window(self):
                    self.assetlbl.hide()
                    self.user_asset.hide()
                    self.sendtolbl.hide()
                    self.send_to_address.hide()
                    self.amlbl.hide()
                    self.am.hide()
                    self.gas_amount.hide()
                    self.gaslbl.hide()
                    self.priority.hide()
                    self.prioritylbl.hide()
                    self.total.hide()
                    self.notice_msg.hide()

                    self.cancel.setIcon(TigerWalletImage.back)
                    self.cancel.clicked.disconnect()

                    self.send.setText("Complete send")
                    self.send.clicked.disconnect()
                    self.send.clicked.connect(self.validate_pass)

                    msg = (
                        'Your password is required'
                        'to complete your transfer'
                    )

                    self.label = QLabel(text=msg, parent=self)
                    self.label.resize(500, 110)
                    self.label.move(70, 120)
                    self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.label.setWordWrap(True)
                    self.label.show()

                    self.init_passfield()

                    self.btn_showhide = QPushButton(
                        text=None,
                        parent=self,
                        icon=TigerWalletImage.closed_eye,
                    )

                    self.btn_showhide.setIconSize(QSize(28, 28))
                    self.btn_showhide.move(530, 242)
                    self.btn_showhide.clicked.connect(self.unhide)
                    self.btn_showhide.show()

                    self.cancel.clicked.connect(
                        lambda: [
                            self.assetlbl.show(),
                            self.user_asset.show(),
                            self.sendtolbl.show(),
                            self.send_to_address.show(),
                            self.amlbl.show(),
                            self.am.show(),
                            self.gas_amount.show(),
                            self.gaslbl.show(),
                            self.priority.show(),
                            self.prioritylbl.show(),
                            self.total.show(),
                            self.notice_msg.show(),
                            self.cancel.setIcon(TigerWalletImage.close),
                            self.send_field.close(),
                            self.label.close(),
                            self.btn_showhide.close(),
                            self.send.setText("Everything looks good"),
                            self.cancel.clicked.disconnect(),
                            self.cancel.clicked.connect(self.close),
                            self.send.clicked.disconnect(),
                            self.send.clicked.connect(self.init_pass_window),
                        ]
                    )

                    if globalvar.configs["theme"] == "default_dark":
                        self.label.setStyleSheet(
                            "font-size: 30px;"
                            + "color: #b0c4de;"
                            + "background: transparent;"
                        )

                        self.send_field.setStyleSheet(
                            "color: #eff1f3; "
                            + "font: 16px;"
                            + "border: 1px solid #778ba5;"
                            + "border-radius: 8px;"
                            + "padding: 7px;"
                        )

                        self.btn_showhide.setStyleSheet(
                            "QPushButton{background-color:  #778ba5;"
                            + "border-radius: 8;}"
                            + "QPushButton::hover{background-color: #99badd;}"
                        )

                    elif globalvar.configs["theme"] == "default_light":
                        self.label.setStyleSheet(
                            "font-size: 30px;"
                            + "color: #778ba5;"
                            + "background: transparent;"
                        )

                        self.send_field.setStyleSheet(
                            "color: black; "
                            + "font: 16px;"
                            + "border: 1px solid #778ba5;"
                            + "border-radius: 8px;"
                            + "padding: 7px;"
                        )

                        self.btn_showhide.setStyleSheet(
                            "QPushButton{background-color:  #778ba5;"
                            + "border-radius: 8px;}"
                            + "QPushButton::hover{background-color: #99badd;}"
                        )

                def init_passfield(self):
                    self.send_field = QLineEdit(self)
                    self.send_field.setEchoMode(QLineEdit.EchoMode.Password)
                    self.send_field.resize(430, 34)
                    self.send_field.move(80, 242)
                    self.send_field.returnPressed.connect(self.validate_pass)
                    self.send_field.show()

                def init_eth_transaction(
                    self, from_, to, amount, gas, priority
                ):
                    try:
                        self.transaction = {
                            "from": HexBytes(from_),
                            "to": HexBytes(to),
                            "value": w3.to_wei(amount, "wei"),
                            "nonce": w3.eth.get_transaction_count(
                                globalvar.account.address
                            ),
                            "gas": 230000,
                            "maxFeePerGas": gas,
                            "maxPriorityFeePerGas": priority,
                        }
                    except Exception:
                        pass

                def init_send_data(self):
                    self.gas = self.master._gasupdate.g

                    if self.asset != "Ether":
                        self.cc = create_contract(
                            globalvar.assets_addr[self.master.index]
                        )
                        self.tx2 = self.cc.functions.transfer(
                            self.master.typeaddr.text(),
                            w3.to_wei(float(self.master.amount.text()), "wei"),
                        )
                    else:
                        self.init_eth_transaction(
                            from_=globalvar.account.address,
                            to=self.master.typeaddr.text(),
                            amount=self.master.amount.text(),
                            gas=self._gas,
                            priority=self._priority,
                        )

                def init_send(self):
                    if self.asset != "Ether":
                        return w3.eth.account.sign_transaction(
                            self.tx2, globalvar.account.key
                        )

                    return w3.eth.account.sign_transaction(
                        self.transaction, globalvar.account.key
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
                    if len(self.send_field.text()) == 0:
                        errbox("Please enter a password")
                        return

                    with open(globalvar.nameofwallet, "r") as f:
                        try:
                            Account.decrypt(
                                json.load(f), password=self.send_field.text()
                            )

                        except ValueError:
                            errbox("Invalid password")
                            return

                    try:
                        self.complete_send()

                    except Exception:
                        errbox(
                            "insufficient funds for gas * price + send value"
                        )
                        return

                def complete_send(self):
                    if self.asset != "Ether":
                        self.tx2.transact(
                            {
                                "from": HexBytes(from_),
                                "gas": 230000,
                                "maxFeePerGas": self._gas,
                                "maxPriorityFeePerGas": self._priority,
                            }
                        )

                        self.tx_r = (
                            w3.eth.wait_for_transaction_receipt(self.tx2)
                        )

                        if (
                            self.tx_r["from"] == globalvar.account.address
                        ):
                            self.tx_receipt = self.tx_r
                            self.send_completed()

                        else:
                            errbox("Send action failed")
                            return

                    else:
                        self.tx = w3.eth.send_raw_transaction(
                            self.init_send().raw_transaction
                        )
                        self.tx_receipt = w3.eth.get_transaction(self.tx)

                        if (
                            self.tx_receipt["from"]
                            == globalvar.account.address
                        ):
                            self.send_completed()

                        else:
                            errbox("Send failed")
                            return

                def send_completed(self):
                    self.etherscan_link = (
                        "https://etherscan.io/tx/" + self.tx_receipt
                    )

                    self.send.hide()
                    self.btn_showhide.hide()
                    self.send_field.hide()

                    self.cancel.setText("Close")
                    self.cancel.move(200, 270)

                    self.completed_msg = QLabel(
                        text="Asset has been successfully sent. "
                        + "Transaction hash: "
                        + f"<a href='{self.etherscan_link}'>"
                        + f"{self.tx_receipt}</a>",
                        parent=self,
                    )

                    self.completed_msg.resize(500, 150)
                    self.completed_msg.move(72, 110)
                    self.completed_msg.setAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )
                    self.completed_msg.setWordWrap(True)
                    self.completed_msg.setTextInteractionFlags(
                        Qt.TextInteractionFlag.TextSelectableByMouse
                    )
                    self.completed_msg.show()
                    self.cancel.clicked.connect(
                        lambda: [
                            self.send_field.setText(""),
                            self.cancel.move(80, 260),
                            self.send.show(),
                            self.btn_showhide.show(),
                            self.send_field.show(),
                            self.completed_msg.close(),
                            self.close(),
                        ]
                    )

                    if globalvar.configs["theme"] == "default_dark":
                        self.completed_msg.setStyleSheet(
                            "font-size: 14px;"
                            + "color: #b0c4de;"
                            + "background: #1e1e1e;"
                        )

                    elif globalvar.configs["theme"] == "default_light":
                        self.completed_msg.setStyleSheet(
                            "font-size: 14px;"
                            + "color: black;"
                            + "background: transparent;"
                        )

            def _continue_send():
                if (
                    self.typeaddr.text() == ""
                    or self.amount.text() == ""
                    or (self.gasfee.isEnabled and self.gasfee.text() == "")
                ):
                    errbox("One or more of the entry fields are empty")
                    return

                if not self.errlabel.isHidden():
                    return

                self.ep = _EnterPass(self)
                self.ep.show()
                self.ep.init_send_data()

            self.send_btn.clicked.connect(_continue_send)
            self.close_send_btn.clicked.connect(self.clear_tab2_contents)

        # THIRD button
        def init_receive_window(self):
            """ Receive crypto window  """
            self.box3 = QWidget(self)
            self.box3.resize(790, 680)
            self.box3.move(166, 0)
            self.box3.hide()

            self.receive = QLabel("Receive", self.box3)
            self.receive.setFixedSize(178, 50)
            self.receive.move(300, 38)
            self.receive.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.label = QLabel(
                text="Only send ERC-20 assets to this address!",
                parent=self.box3,
            )

            self.label.resize(384, 61)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.move(198, 100)

            self.qrlabel = QLabel(self.box3)
            self.qrlabel.resize(340, 310)
            self.qrlabel.move(228, 180)

            buf = BytesIO()

            self.qrcode = segno.make(self.address)
            self.qrcode.save(
                buf,
                scale=10,
                border=2,
                light=(
                    None
                    if globalvar.configs["theme"] == "default_light"
                    else "white"
                ),
                kind="png",
            )

            self.qrimg = QPixmap()
            self.qrimg.loadFromData(buf.getvalue())
            self.qrlabel.setPixmap(self.qrimg)

            self.addr = QLineEdit(self.box3)
            self.addr.resize(425, 30)
            self.addr.move(178, 514)
            self.addr.setText(self.address)
            self.addr.setReadOnly(True)
            self.addr.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.closebtn = QPushButton(
                text="Close",
                parent=self.box3,
                icon=TigerWalletImage.close
            )

            self.closebtn.setFixedSize(240, 62)
            self.closebtn.setIconSize(QSize(32, 32))
            self.closebtn.move(276, 568)
            self.closebtn.clicked.connect(self.clear_tab3_contents)

            self.copy_address = QPushButton(
                text=None,
                parent=self.box3,
                icon=TigerWalletImage.copy_blue
            )

            self.copy_address.setIconSize(QSize(16, 16))
            self.copy_address.move(566, 519)
            self.copy_address.clicked.connect(
                lambda: [
                    QApplication.clipboard().setText(self.address),
                    msgbox("Address has been copied!"),
                ]
            )

        # FOURTH button
        def init_addressbook_window(self):
            self.contacts = globalvar.contactbook

            self.box4 = QWidget(self)
            self.box4.resize(790, 680)
            self.box4.move(166, 0)
            self.box4.hide()

            self.contactlbl = QLabel("Contact book", self.box4)
            self.contactlbl.resize(208, 30)
            self.contactlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.contactlbl.move(274, 46)

            self.tip = QLabel(
                text="Double click on a row to copy the contact's address",
                parent=self.box4,
            )
            self.tip.resize(790, 40)
            self.tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tip.move(0, 90)

            # Table
            # BEGIN
            self.contactbook_sz = len(globalvar.contactbook["name"])
            self.contact_table = QTableWidget(self.box4)
            self.contact_table.setRowCount(self.contactbook_sz)
            self.contact_table.setColumnCount(2)
            self.contact_table.setColumnWidth(0, 360)
            self.contact_table.setColumnWidth(1, 377)
            self.contact_table.verticalHeader().setVisible(False)
            self.contact_table.horizontalHeader().setVisible(True)
            self.contact_table.resize(739, 354)
            self.contact_table.move(20, 140)
            self.contact_table.setHorizontalHeaderItem(
                0, QTableWidgetItem("Contact Name")
            )
            self.contact_table.setHorizontalHeaderItem(
                1, QTableWidgetItem("Contact Address")
            )
            self.contact_table.setEditTriggers(
                QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.contact_table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.NoSelection
            )
            self.contact_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.contact_table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.contact_table.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.Fixed
            )

            for index in range(self.contactbook_sz):
                self.contact_table.setItem(
                    index,
                    0,
                    QTableWidgetItem(self.contacts["name"][index])
                )

                self.contact_table.setItem(
                    index,
                    1,
                    QTableWidgetItem(self.contacts["address"][index])
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
                text="Add contact",
                parent=self.box4,
                icon=TigerWalletImage.plus,
            )
            self.add_contact.setFixedSize(240, 40)
            self.add_contact.setIconSize(QSize(32, 32))
            self.add_contact.move(136, 518)
            self.add_contact.show()
            self.add_contact.clicked.connect(self.init_add_contact_window)

            # Remove contact
            self.del_contact = QPushButton(
                text="Delete contact",
                parent=self.box4,
                icon=TigerWalletImage.delete,
            )
            self.del_contact.setFixedSize(240, 40)
            self.del_contact.setIconSize(QSize(32, 32))
            self.del_contact.move(406, 518)
            self.del_contact.show()
            self.del_contact.clicked.connect(self.init_rm_contact_window)

            self.close_book = QPushButton(
                text="Close",
                parent=self.box4,
                icon=TigerWalletImage.close
            )
            self.close_book.setFixedSize(240, 62)
            self.close_book.setIconSize(QSize(32, 32))
            self.close_book.move(276, 568)
            self.close_book.clicked.connect(self.clear_tab4_contents)

        # FIFTH button
        def init_history_window(self):
            self.wh = WalletHistory()

        # SIXTH button
        def init_settings_window(self):
            """ Settings window """
            self.s = Settings(self)

        #
        def init_donate_window(self):
            """
            I just discovered QHBoxLayout.
            It is for this reason that this tab
            is the only one that uses it.

            Later on, all classes/functions
            will use QHBoxLayout, and
            QVBoxLayout, when needed.

            The same goes for list comprehensions;
            this is where I've found out about them.
            """
            self.selected_donobtn_style()

            if self.tab == 1:
                self.clear_tab1_contents()

            elif self.tab == 2:
                self.clear_tab2_contents()

            elif self.tab == 3:
                self.clear_tab3_contents()

            elif self.tab == 4:
                self.clear_tab4_contents()

            elif self.tab == 5:
                self.clear_tab5_contents()

            self.donation_window_active = True
            self.sidebar_button[7].setEnabled(False)

            self.val.hide()
            self.table.hide()
            self.stop_thread()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()

            self.dono_label = QLabel(text="Donate crypto", parent=self)

            self.dono_label.resize(220, 32)
            self.dono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dono_label.move(454, 44)
            self.dono_label.show()

            self.dono_msg = QLabel(
                text="If you like my work, buy me a coffee!",
                parent=self
            )

            self.dono_msg.resize(1100, 32)
            self.dono_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dono_msg.move(0, 88)
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

            self.qrs = [segno.make(self.dono_addrs[i]) for i in range(7)]
            [
                self.qrs[i].save(buf_list[i], kind="png", scale=4, border=1)
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
            self.widg1.move(308, 206)
            self.widg1.show()

            self.layout1 = QHBoxLayout()
            self.widg1.setLayout(self.layout1)

            for index in range(0, 3):
                self.layout1.addWidget(self.qr_holders[index])

            self.widg2 = QWidget(self)
            self.widg2.resize(540, 140)
            self.widg2.move(308, 422)
            self.widg2.show()

            self.layout2 = QHBoxLayout()
            self.widg2.setLayout(self.layout2)

            for index in range(3, 6):
                self.layout2.addWidget(self.qr_holders[index])

            # Name of chains
            self.assets_labels = [
                "BTC (SegWit Bench32)",
                "ETH/ARB/",
                "SOL",
                "LTC (Not MW)",
                "TRC-20",
                "ETC",
                "BCH (P2PKH)",
            ]

            self.widg3 = QWidget(self)
            self.widg3.resize(540, 52)
            self.widg3.move(286, 137)
            self.widg3.show()
            self.widg3.setStyleSheet("background: transparent;")

            self.layout3 = QHBoxLayout()
            self.widg3.setLayout(self.layout3)

            self.assets_row1 = [QLabel(self) for label in self.assets_labels]

            for index in range(0, 3):
                self.assets_row1[index].setText(self.assets_labels[index])
                self.assets_row1[index].setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.layout3.addWidget(self.assets_row1[index])
                self.assets_row1[index].setWordWrap(True)
                self.assets_row1[index].resize(50, 70)

                if globalvar.configs["theme"] == "default_dark":
                    self.assets_row1[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: #6495ed;"
                        + "background: transparent;"
                    )

                elif globalvar.configs["theme"] == "default_light":
                    self.assets_row1[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: black;"
                        + "background: transparent;"
                    )

            self.widg4 = QWidget(self)
            self.widg4.resize(540, 52)
            self.widg4.move(286, 350)
            self.widg4.show()
            self.widg4.setStyleSheet("background: transparent;")

            self.layout4 = QHBoxLayout()
            self.widg4.setLayout(self.layout4)

            self.assets_row2 = [QLabel(self) for label in self.assets_labels]

            for index in range(3, 6):
                self.assets_row2[index].setText(self.assets_labels[index])
                self.assets_row2[index].setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.layout4.addWidget(self.assets_row2[index])
                self.assets_row2[index].setWordWrap(True)
                self.assets_row2[index].resize(50, 70)

                if globalvar.configs["theme"] == "default_dark":
                    self.assets_row2[index].setStyleSheet(
                        "font-size: 17px;"
                        + "color: #6495ed;"
                        + "background: transparent;"
                    )

                elif globalvar.configs["theme"] == "default_light":
                    self.assets_row2[index].setStyleSheet(
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
            self.btnwidget1.move(286, 176)
            self.btnwidget1.show()

            self.btnlayout1 = QHBoxLayout(self.btnwidget1)

            def connect_copy_to_buttons():
                self.copyrow1[0].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[0]),
                        msgbox("BTC address copied to the clipboard"),
                    ]
                )

                self.copyrow1[1].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[1]),
                        msgbox("ETH address copied to the clipboard"),
                    ]
                )

                self.copyrow1[2].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[2]),
                        msgbox("SOL address copied to the clipboard"),
                    ]
                )

            connect_copy_to_buttons()

            for index in range(0, 3):
                self.btnlayout1.addWidget(self.copyrow1[index])
                self.copyrow1[index].show()

                if globalvar.configs["theme"] == "default_dark":
                    self.copyrow1[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 2px;"
                        + "font-size: 17px;"
                        + "color: #b0c4de}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

                elif globalvar.configs["theme"] == "default_light":
                    self.copyrow1[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 2px;"
                        + "font-size: 17px;"
                        + "color: #79829A}"
                        + "QPushButton::hover{background-color: #363636;}"
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
            self.btnwidget2.move(286, 389)
            self.btnwidget2.show()

            self.btnlayout2 = QHBoxLayout(self.btnwidget2)

            for index in range(3, 6):
                self.btnlayout2.addWidget(self.copyrow2[index])
                self.copyrow2[index].show()

                if globalvar.configs["theme"] == "default_dark":
                    self.copyrow2[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 2px;"
                        + "font-size: 17px;"
                        + "color: #b0c4de}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

                elif globalvar.configs["theme"] == "default_light":
                    self.copyrow2[index].setStyleSheet(
                        "QPushButton{background-color:  transparent;"
                        + "border-radius: 2px;"
                        + "font-size: 17px;"
                        + "color: #79829A}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

            # Didn't work when it was looped, so doing it the naive way
            def connect_copy_to_buttons2():
                self.copyrow2[0].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[3]),
                        msgbox("LTC address copied to the clipboard"),
                    ]
                )

                self.copyrow2[1].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[4]),
                        msgbox("TRC-20 address copied to the clipboard"),
                    ]
                )

                self.copyrow2[2].clicked.connect(
                    lambda: [
                        QApplication.clipboard().setText(self.dono_addrs[5]),
                        msgbox("ETC address copied to the clipboard"),
                    ]
                )

            connect_copy_to_buttons2()

            self.close_dono = QPushButton(
                text="Close",
                parent=self,
                icon=TigerWalletImage.close
            )
            self.close_dono.setFixedSize(200, 62)
            self.close_dono.setIconSize(QSize(32, 32))
            self.close_dono.move(458, 596)
            self.close_dono.show()
            self.close_dono.clicked.connect(self.clear_donation_tab)

            if "default" in globalvar.configs["theme"]:
                self.close_dono.setStyleSheet(
                    "QPushButton{background-color:  #6495ed;"
                    + "border-radius: 8px;"
                    + "font-size: 18px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #6ca0dc;}"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.dono_label.setStyleSheet(
                    "font-size: 30px;"
                    + "color: #6495ed;"
                    + "background: #1e1e1e;"
                )

                self.dono_msg.setStyleSheet(
                    "font-size: 22px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.dono_label.setStyleSheet(
                    "font-size: 30px;"
                    + "color: black;"
                    + "background: #eff1f3;"
                )

                self.dono_msg.setStyleSheet(
                    "font-size: 22px;"
                    + "color: black;"
                    + "background: transparent;"
                )

        #
        def init_add_contact_window(self):
            self.border.show()
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
            self.enter_details.resize(800, 100)
            self.enter_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.enter_details.move(160, 136)
            self.enter_details.show()

            self.cname = QLabel("Name:", self)
            self.cname.resize(200, 40)
            self.cname.move(296, 254)
            self.cname.show()
            self.form1 = QLineEdit(self)
            self.form1.resize(430, 38)
            self.form1.move(380, 260)
            self.form1.show()

            self.caddr = QLabel("Address: ", self)
            self.caddr.resize(90, 40)
            self.caddr.move(296, 319)
            self.caddr.show()
            self.form2 = QLineEdit(self)
            self.form2.resize(430, 38)
            self.form2.move(380, 320)
            self.form2.show()

            self.close_add = QPushButton(
                text="Cancel",
                parent=self,
                icon=TigerWalletImage.close
            )
            self.close_add.setFixedSize(240, 62)
            self.close_add.setIconSize(QSize(32, 32))
            self.close_add.move(310, 400)
            self.close_add.show()

            self.continue_add = QPushButton(
                text="Continue",
                parent=self,
                icon=TigerWalletImage.eth_img
            )
            self.continue_add.setFixedSize(240, 62)
            self.continue_add.setIconSize(QSize(32, 32))
            self.continue_add.move(560, 400)
            self.continue_add.show()
            self.continue_add.clicked.connect(
                lambda: self.add_contact_details(
                    self.form1.text(), self.form2.text()
                )
            )

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
                ]
            )

            if "default" in globalvar.configs["theme"]:
                self.close_add.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.continue_add.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.cname.setStyleSheet(
                    "font-size: 20px;" + "color: #6495ed;"
                )

                self.caddr.setStyleSheet(
                    "font-size: 20px;" + "color: #6495ed;"
                )

            if globalvar.configs["theme"] == "default_dark":
                self.form1.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "padding: 5px;"
                )

                self.form2.setStyleSheet(
                    "color: #eff1f3;"
                    + "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "padding: 5px;"
                )

                self.enter_details.setStyleSheet(
                    "font-size: 23px;"
                    + "color: #eff1f3;"
                    + "background: transparent;"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.form1.setStyleSheet(
                    "color: black;"
                    + "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "padding: 5px;"
                )

                self.form2.setStyleSheet(
                    "color: black;"
                    + "border: 2px solid #778ba5;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "padding: 5px;"
                )

                self.enter_details.setStyleSheet(
                    "font-size: 23px;"
                    + "color: black;"
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
                QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
            )

            self.contact_table.setSelectionBehavior(
                QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )

            self.contact_table.itemDoubleClicked.disconnect()

            self.close_rm = QPushButton(
                text="Cancel", parent=self, icon=TigerWalletImage.close
            )
            self.close_rm.setFixedSize(240, 62)
            self.close_rm.setIconSize(QSize(32, 32))
            self.close_rm.move(296, 518)
            self.close_rm.show()

            self.continue_rm = QPushButton(
                text="Continue", parent=self, icon=TigerWalletImage.eth_img
            )
            self.continue_rm.setFixedSize(240, 62)
            self.continue_rm.setIconSize(QSize(32, 32))
            self.continue_rm.move(566, 518)
            self.continue_rm.show()
            self.continue_rm.clicked.connect(self.rm_contact_details)

            self.close_rm.clicked.connect(
                lambda: [
                    self.continue_rm.close(),
                    self.close_rm.close(),
                    self.contact_table.setSelectionBehavior(
                        QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems
                    ),
                    self.contact_table.setSelectionMode(
                        QtWidgets.QAbstractItemView.SelectionMode.NoSelection
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

            if "default" in globalvar.configs["theme"]:
                self.close_rm.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

                self.continue_rm.setStyleSheet(
                    "QPushButton{background-color:  #b0c4de;"
                    + "border-radius: 8;"
                    + "font-size: 20px;"
                    + "color: black}"
                    + "QPushButton::hover{background-color: #99badd;}"
                )

        def init_sidebar_style(self):
            if globalvar.configs["theme"] == "default_dark":
                for i in range(6):
                    self.sidebar_button[i].setStyleSheet(
                        "QPushButton {background-color:  #1e1e1e;"
                        + "border-radius: 16px;"
                        + "font-size: 16px;"
                        + "color: #eff1f3;"
                        + "padding : 7px;"
                        + "text-align: left;}"
                        + "QPushButton::hover{background-color: #363636;}"
                    )

                self.sidebar_button[6].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

                self.sidebar_button[7].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                for i in range(6):
                    self.sidebar_button[i].setStyleSheet(
                        "QPushButton{background-color:  #eff1f3;"
                        + "border-radius: 16px;"
                        + "font-size: 16px;"
                        + "color: black;"
                        + "padding : 7px;"
                        + "text-align: left;}"
                        + "QPushButton::hover{background-color: #adb4bf;}"
                    )

                self.sidebar_button[6].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

                self.sidebar_button[7].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
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
            self.unlock_wallet_lbl.move(60, 40)

            def unhide():
                if self.opt == 1:
                    self.showhidepass.setIcon(TigerWalletImage.opened_eye)
                    self.unlock_wallet_pbox.setEchoMode(
                        QLineEdit.EchoMode.Normal
                    )
                    self.opt = 0

                elif self.opt == 0:
                    self.showhidepass.setIcon(TigerWalletImage.closed_eye)
                    self.unlock_wallet_pbox.setEchoMode(
                        QLineEdit.EchoMode.Password
                    )
                    self.opt = 1

            self.unlock_wallet_pbox = QLineEdit(self.unlock_wallet_box)
            self.unlock_wallet_pbox.setEchoMode(QLineEdit.EchoMode.Password)
            self.unlock_wallet_pbox.resize(386, 44)
            self.unlock_wallet_pbox.move(40, 110)
            self.unlock_wallet_pbox.setStyleSheet(
                "color: #eff1f3;"
                "border-radius: 8px;"
                "border: 1px solid lightgray;"
            )
            self.unlock_wallet_pbox.returnPressed.connect(self.unlock_wallet)

            self.showhidepass = QPushButton(self.unlock_wallet_box)
            self.showhidepass.setIcon(TigerWalletImage.closed_eye)
            self.showhidepass.setIconSize(QSize(32, 32))
            self.showhidepass.move(444, 113)
            self.showhidepass.clicked.connect(unhide)

            self.unlock_wallet_button = QPushButton(
                text=" Unlock wallet",
                parent=self.unlock_wallet_box,
                icon=TigerWalletImage.pass_blue,
            )

            self.unlock_wallet_button.setStyleSheet(
                "QPushButton {background-color:  #b0c4de;"
                "border-radius: 8px;"
                "font-size: 20px;"
                "color: black;}"
                "QPushButton::hover{background-color: #99badd;}"
            )

            self.unlock_wallet_button.setFixedSize(220, 46)
            self.unlock_wallet_button.setIconSize(QSize(32, 32))
            self.unlock_wallet_button.move(140, 188)
            self.unlock_wallet_button.clicked.connect(self.unlock_wallet)

            self.unlock_wallet_box.hide()

        def init_lock_wallet_button(self):
            self.lock_wallet_button = QPushButton(
                text=" Lock wallet",
                parent=self,
                icon=TigerWalletImage.pass_blue,
            )
            self.lock_wallet_button.move(966, 50)
            self.lock_wallet_button.resize(120, 44)
            self.lock_wallet_button.setIconSize(QSize(24, 24))
            self.lock_wallet_button.clicked.connect(
                lambda: [
                    self.unlock_wallet_box.show(),
                    self.setStyleSheet("background: black;"),
                    self.black_out_window(),
                ]
            )



        def clear_main_table_contents(self):
            sz = len(self.assets["name"])

            [
                self.table.takeItem(i, ii)
                for i in range(sz + 1)
                for ii in range(3)
            ]

        # new in v1.3
        def black_out_window(self):
            self.button_box.hide()
            self.border.hide()
            self.lock_wallet_button.hide()

            if self.tab == 0:
                if self.donation_window_active:
                    self.default_donobtn_style()
                    self.sidebar_button[7].setEnabled(True)
                    self.close_dono.close()
                    self.dono_msg.close()
                    self.dono_label.close()

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

                self.table.hide()
                self.val.hide()
                self.add_coin_btn.hide()
                self.default_coin_btn.hide()
                self.del_coin_btn.hide()
                self.button_box.hide()

            elif self.tab == 1:
                self.box1.hide()

            elif self.tab == 2:
                self.box2.hide()

            elif self.tab == 3:
                self.box3.hide()

            elif self.tab == 4:
                self.box4.hide()

        # new in v1.3
        def unlock_wallet(self):
            try:
                with open(globalvar.nameofwallet, "r") as f:
                    Account.decrypt(
                        json.load(f),
                        self.unlock_wallet_pbox.text()
                    )
            except Exception:
                errbox("Invalid password")
                return

            self.unlock_wallet_box.hide()
            self.unlock_wallet_pbox.clear()

            if globalvar.configs["theme"] == "default_dark":
                self.setStyleSheet(
                    ":enabled {background-color: #1e1e1e;}"
                    ":disabled {background-color: black;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.setStyleSheet(
                    ":enabled {background-color: #eff1f3;}"
                    ":disabled {background-color: black;}"
                )

            self.button_box.show()
            self.border.show()
            self.lock_wallet_button.show()

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

        def start_afk_timer(self, afk_time=500000):
            self.afk_time = afk_time

            if afk_time == None:
                return

            self.afk_timer.start(afk_time)

        # Show FIRST button contents
        def show_tab1_contents(self):
            self.selected_btn1_style()

            if self.tab == 2:
                self.clear_tab2_contents()

            elif self.tab == 3:
                self.clear_tab3_contents()

            elif self.tab == 4:
                self.clear_tab4_contents()

            elif self.tab == 5:
                self.clear_tab5_contents()

            elif self.donation_window_active:
                self.clear_donation_tab()

            self.tab = 1
            self.sidebar_button[0].setEnabled(False)

            self.table.hide()
            self.val.hide()
            self.stop_thread()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()

            self.box1.show()

        def show_tab2_contents(self):
            self.selected_btn2_style()

            if self.tab == 1:
                self.clear_tab1_contents()

            elif self.tab == 3:
                self.clear_tab3_contents()

            elif self.tab == 4:
                self.clear_tab4_contents()

            elif self.tab == 5:
                self.clear_tab5_contents()

            elif self.donation_window_active:
                self.clear_donation_tab()

            self.tab = 2
            self.sidebar_button[1].setEnabled(False)

            self.border.show()
            self.table.hide()
            self.val.hide()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()

            self.box2.show()

        # Show THIRD button contents
        def show_tab3_contents(self):
            self.selected_btn3_style()

            if self.tab == 1:
                self.clear_tab1_contents()

            elif self.tab == 2:
                self.clear_tab2_contents()

            elif self.tab == 4:
                self.clear_tab4_contents()

            elif self.tab == 5:
                self.clear_tab5_contents()

            elif self.donation_window_active:
                self.clear_donation_tab()

            self.tab = 3
            self.sidebar_button[2].setEnabled(False)

            self.border.show()
            self.table.hide()
            self.val.hide()
            self.stop_thread()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()

            self.box3.show()

        # Show FOURTH button contents
        def show_tab4_contents(self):
            self.selected_btn4_style()

            if self.tab == 1:
                self.clear_tab1_contents()

            elif self.tab == 2:
                self.clear_tab2_contents()

            elif self.tab == 3:
                self.clear_tab3_contents()

            elif self.tab == 5:
                self.clear_tab5_contents()

            elif self.donation_window_active:
                self.clear_donation_tab()

            self.tab = 4
            self.sidebar_button[3].setEnabled(False)

            self.border.show()
            self.table.hide()
            self.val.hide()
            self.stop_thread()
            self.add_coin_btn.hide()
            self.default_coin_btn.hide()
            self.del_coin_btn.hide()

            self.box4.show()

        def show_tab5_contents(self):
            if self.tab == 1:
                self.clear_tab1_contents()

            elif self.tab == 2:
                self.clear_tab2_contents()

            elif self.tab == 3:
                self.clear_tab3_contents()

            elif self.tab == 4:
                self.clear_tab4_contents()

            self.selected_btn5_style()

            self.tab = 5
            self.sidebar_button[4].setEnabled(False)
            self.selected_btn5_style()
            self.wh.show()

            def _check_if_active():
                while self.wh.isVisible():
                    """
                    Introduce a small delay to avoid system lag

                    Thread waits for the window to close
                    before the button's style gets restored.
                    """
                    time.sleep(0.1)

                    if not self.wh.isVisible():
                        self.default_btn5_style()
                        self.sidebar_button[4].setEnabled(True)
                        return
                return

            _thread = Thread(target=_check_if_active)
            _thread.start()

        def show_tab6_contents(self):
            self.s.show()
            self.black_out_window()
            self.setEnabled(False)

        ## Applies default_dark theme

        def apply_default_dark_theme(self):
            # Window background
            self.setStyleSheet(
                ":enabled {background-color: #1e1e1e;}"
                ":disabled {background-color: black;}"
            )

            self.init_sidebar_style()

            self.val.setStyleSheet(
                "font-size: 30px;" + "color: #6495ed;" + "background: #1e1e1e;"
            )

            self.table.setStyleSheet(
                "QTableView{font-size: 16px;"
                + "gridline-color: #1e1e1e;"
                + "color: #b0c4de;"
                + "border-radius: 16px;}"
                # Upper part of the table
                + "QHeaderView::section{background-color: #1e1e1e;"
                + "padding : 3px;"
                + "border-radius: 8px;"
                + "color: #b0c4de;"
                + "border: 1px solid gray;"
                + "margin: 1px;"
                + "font-size: 16px;}"
                # Will be used when removing coins
                + "QTableView:item:selected{background: #99badd;}"
            )

            self.change_wallet_title.setStyleSheet(
                "font-size: 30px;" + "color: #eff1f3;" + "background: #1e1e1e;"
            )

            self.wallet_list.setStyleSheet(
                "QListView {font-size: 18px;"
                + "color: #eff1f3;"
                + "padding: 16px;"
                + "border-radius: 16px;"
                + "background: transparent;}"
                + "QListView::item:hover{color: #b0c4de;"
                "background: #363636;"
                "border-radius: 8px;}"
            )

            self.addr.setStyleSheet(
                "color: #eff1f3;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.label.setStyleSheet(
                "font-size: 18px;" + "color: #6ca0dc;" + "background: #1e1e1e;"
            )

            self.receive.setStyleSheet(
                "font-size: 30px;" + "color: #eff1f3;" + "background: #1e1e1e;"
            )

            self.copy_address.setStyleSheet(
                "QPushButton{background-color: transparent;"
                + "border-radius: 4px;"
                + "background: transparent;}"
                + "QPushButton::hover{background-color: #363636;}"
            )

            self.contact_table.setStyleSheet(
                "QTableView{font-size: 15px;"
                + "gridline-color: #1e1e1e;"
                + "color: #eff1f3;"
                + "border: 1px solid #363636;"
                + "border-radius: 16px;}"
                # Upper part of the table
                + "QHeaderView::section{background-color: #1e1e1e;"
                + "padding : 3px;"
                + "color: #b0c4de;"
                + "border: 1px solid gray;"
                + "border-radius: 8px;"
                + "margin: 1px;"
                + "font-size: 17px;}"
                + "QHeaderView::section:checked{background-color: transparent;"
                + "font-size: 15px;"
                + "color: #b0c4de;}"
                + "QTableView:item:selected{background: #99badd;}"
            )

            self.contactlbl.setStyleSheet(
                "font-size: 25px;" + "color: #eff1f3;" + "background: #1e1e1e;"
            )

            self.tip.setStyleSheet(
                "font-size: 20px;"
                + "color: #6495ed;"
                + "background: transparent;"
            )

            self.topmsglabel.setStyleSheet(
                "font-size: 22px;"
                + "color: #b0c4de;"
                + "background: transparent;"
            )

            self.sendlabel.setStyleSheet(
                "font-size: 30px;" + "color: #eff1f3;" + "background: #1e1e1e;"
            )

            self.assetlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #eff1f3;"
                + "background: transparent;"
            )

            self.estimate_amount.setStyleSheet(
                "font-size: 17px;"
                + "color: #eff1f3;"
                + "background: transparent;"
            )

            if os.name == "nt":
                self.asset_list.setStyleSheet(
                    "QComboBox {border: 2px solid #778ba5;"
                    + "padding: 8px;"
                    + "font: 18px;"
                    + "border-radius: 4px;"
                    + "background: transparent;"
                    + "color: #b0c4de;}"
                    "QComboBox QAbstractItemView {background: #1e1e1e;"
                    + "color: #b0c4de;"
                    + "border: 2px solid #778ba5;"
                    + "border-radius: 4px;"
                    + "padding: 8px;}"
                )

            else:
                self.asset_list.setStyleSheet(
                    "QComboBox {border: 2px solid #778ba5;"
                    "border-radius: 4px;"
                    "color: #b0c4de;"
                    "font: 18px;}"
                    "QComboBox QAbstractItemView {background: #1e1e1e;}"
                )

            self.typeaddr.setStyleSheet(
                "color: #eff1f3;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.sendtolbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #eff1f3;"
                + "background: transparent;"
            )

            self.amount.setStyleSheet(
                "color: #eff1f3;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.amountlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #eff1f3;"
                + "background: transparent;"
            )

            self.slider.setStyleSheet(
                "font-size: 14px;"
                + "color: #eff1f3;"
                + "background: transparent;"
            )

            self.gasfeelbl.setStyleSheet(
                "font-size: 20px;"
                + "color: #eff1f3;"
                + "background: transparent;"
            )

            self.gasfee.setStyleSheet(
                "color: #eff1f3;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.lock_wallet_button.setStyleSheet(
                "QPushButton {background: transparent;"
                "font-size: 16px;"
                "color: #eff1f3;"
                "border-radius: 8px;}"
                "QPushButton::hover{background-color: #363636;}"
            )

        ## Applies default_light theme
        def apply_default_light_theme(self):
            self.setStyleSheet(
                ":enabled {background-color: #eff1f3;}"
                ":disabled {background-color: black;}"
            )

            self.init_sidebar_style()

            self.val.setStyleSheet(
                "font-size: 30px;" + "color: #6495ed;" + "background: #eff1f3;"
            )

            self.table.setStyleSheet(
                # The table its self
                "QTableView{font-size: 16px;"
                + "gridline-color: #eff1f3;"
                + "color: black;"
                + "border-radius: 16px;}"
                # Upper part of the table
                + "QHeaderView::section{background-color: #eff1f3;"
                + "padding : 3px;"
                + "border-radius: 8px;"
                + "color: black;"
                + "border: 1px solid gray;"
                + "margin: 1px;"
                + "font-size: 16px;}"
                # Will be used when removing coins
                + "QTableView:item:selected{background: #99badd;}"
            )

            self.change_wallet_title.setStyleSheet(
                "font-size: 30px;" + "color: black;" + "background: #eff1f3;"
            )

            self.wallet_list.setStyleSheet(
                "QListView {font-size: 18px;"
                + "color: black;"
                + "padding: 16px;"
                + "border-radius: 16px;"
                + "background: transparent;}"
                + "QListView::item:hover{color: black;"
                "background: #adb4bf;"
                "border-radius: 8px;}"
            )

            self.addr.setStyleSheet(
                "color: black;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.label.setStyleSheet(
                "font-size: 18px;" + "color: black;" + "background: #eff1f3;"
            )

            self.receive.setStyleSheet(
                "font-size: 30px;" + "color: black;" + "background: #eff1f3;"
            )

            self.copy_address.setStyleSheet(
                "QPushButton{background-color: transparent;"
                + "border-radius: 4px;"
                + "background: transparent;}"
                + "QPushButton::hover{background-color: #c9cdcd;}"
            )

            self.contact_table.setStyleSheet(
                # The table its self
                "QTableView{font-size: 15px;"
                + "gridline-color: #eff1f3;"
                + "color: black;"
                + "border: 1px solid #363636;"
                + "border-radius: 4px;}"
                # Upper part of the table
                + "QHeaderView::section{background-color: #eff1f3;"
                + "padding : 3px;"
                + "color: black;"
                + "border: 1px solid gray;"
                + "border-radius: 2px;"
                + "font-size: 15px;"
                + "margin: 1px;"
                + "font-size: 17px;}"
                + "QHeaderView::section:checked{background-color: transparent;"
                + "font-size: 15px;"
                + "color: black;}"
                + "QTableView:item:selected{background: #99badd;}"
            )

            self.contactlbl.setStyleSheet(
                "font-size: 25px;" + "color: black;" + "background: #eff1f3;"
            )

            self.tip.setStyleSheet(
                "font-size: 20px;"
                + "color: #6495ed;"
                + "background: transparent;"
            )

            self.topmsglabel.setStyleSheet(
                "font-size: 18px;"
                + "color: black;"
                + "background: transparent;"
            )

            self.sendlabel.setStyleSheet(
                "font-size: 30px;" + "color: black;" + "background: #eff1f3;"
            )

            self.assetlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: black;"
                + "background: transparent;"
            )

            self.estimate_amount.setStyleSheet(
                "font-size: 17px;"
                + "color: black;"
                + "background: transparent;"
            )

            if os.name == "nt":
                self.asset_list.setStyleSheet(
                    "QComboBox {border: 2px solid #778ba5;"
                    + "padding: 8px;"
                    + "font: 18px;"
                    + "border-radius: 4px;"
                    + "background: transparent;"
                    + "color: black;}"
                    "QComboBox QAbstractItemView {background: #eff1f3;"
                    + "color: black;"
                    + "border: 2px solid #778ba5;"
                    + "border-radius: 4px;"
                    + "padding: 8px;}"
                )

            else:
                self.asset_list.setStyleSheet(
                    "QComboBox {border: 2px solid #778ba5;"
                    "border-radius: 4px;"
                    "color: black;"
                    "font: 18px;}"
                    "QComboBox QAbstractItemView {background: #eff1f3;}"
                )

            self.typeaddr.setStyleSheet(
                "color: black;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.sendtolbl.setStyleSheet(
                "font-size: 20px;"
                + "color: black;"
                + "background: transparent;"
            )

            self.amount.setStyleSheet(
                "color: black;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.amountlbl.setStyleSheet(
                "font-size: 20px;"
                + "color: black;"
                + "background: transparent;"
            )

            self.slider.setStyleSheet(
                "font-size: 14px;"
                + "color: black;"
                + "background: transparent;"
            )

            self.gasfeelbl.setStyleSheet(
                "font-size: 20px;"
                + "color: black;"
                + "background: transparent;"
            )

            self.gasfee.setStyleSheet(
                "color: black;"
                + "border: 1px solid #6ca0dc;"
                + "font-size: 15px;"
                + "border-radius: 8;"
            )

            self.lock_wallet_button.setStyleSheet(
                "QPushButton {background: transparent;"
                "font-size: 16px;"
                "color: black;"
                "border-radius: 8px;}"
                "QPushButton::hover{background-color: #adb4bf;}"
            )

        # Change wallet
        def default_btn1_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

        # Send
        def default_btn2_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

        # Receive
        def default_btn3_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

        # Address book
        def default_btn4_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

        # History
        def default_btn5_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

        # Settings
        def default_btn6_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #adb4bf;}"
                )

        # Donate
        def default_donobtn_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton{background-color:  #1e1e1e;"
                    + "border-radius: 2px;"
                    + "color: #1e1e1e;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #1e1e1e;}"
                )

            if globalvar.configs["theme"] == "default_light":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton{background-color:  #eff1f3;"
                    + "border-radius: 2px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #eff1f3;}"
                )

        #
        def selected_btn1_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[0].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

            #
            def selected_btn2_style(self):
                self.btn2.setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            #
            def selected_btn3_style(self):
                self.btn3.setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            #
            def selected_btn4_style(self):
                self.btn4.setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            #
            def selected_btn5_style(self):
                self.btn5.setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            #
            def selected_btn6_style(self):
                self.btn6.setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

        #
        def selected_btn2_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[1].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

        #
        def selected_btn3_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[2].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

        #
        def selected_btn4_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[3].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

            #

        #
        def selected_btn5_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[4].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

            #

        #
        def selected_btn6_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[5].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;"
                    + "text-align: left;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

        #
        def selected_donobtn_style(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton{background-color:  #363636;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: #eff1f3;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #363636;}"
                )

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[7].setStyleSheet(
                    "QPushButton{background-color: #c9cdcd;"
                    + "border-radius: 16px;"
                    + "font-size: 16px;"
                    + "color: black;"
                    + "padding : 7px;}"
                    + "QPushButton::hover{background-color: #c9cdcd;}"
                )

        #
        def launch_chosen_wallet(self):
            if self.item is not None:
                globalvar.nameofwallet = self.item

                self.login = Login()
                self.login.show()
                self.close()
                self.deleteLater()

            else:
                errbox("You haven't selected a wallet!")
                return

        # Load up the list
        def fill_up_table(self):
            for pos in range(0, len(globalvar.assets_addr)):
                pos += 1

                # Asset name and symbol
                self.table.setItem(
                    pos,
                    0,
                    QTableWidgetItem(
                        f" {self.assets['name'][pos-1]} ({self.assets['symbol'][pos-1]})"
                    )
                )

                self.table.item(pos, 0).setIcon(
                    QIcon(globalvar.assets_details["image"][pos - 1])
                )

                # Amount of asset user holds
                if self.assets["value"][pos - 1] != "0.0":
                    self.table.setItem(
                        pos,
                        1,
                        QTableWidgetItem(
                            str(self.assets["value"][pos - 1])[:17]
                        )
                    )

                else:
                    self.table.setItem(pos, 1, QTableWidgetItem("0"))

                # Current valuation of asset
                self.table.setItem(
                    pos,
                    2,
                    QTableWidgetItem(' ' + self.assets["price"][pos - 1][:17]),
                )

                self.table.item(pos, 0).setSizeHint(QSize(278, 50))
                self.table.item(pos, 1).setSizeHint(QSize(220, 50))
                self.table.item(pos, 2).setSizeHint(QSize(218, 50))

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

        # Stop main thread (which stops the timer)
        def stop_thread(self):
            self.worker.quit()
            self.thread.quit()

        def toggle_mode(self):
            if globalvar.configs["theme"] == "default_dark":
                self.sidebar_button[6].setIcon(TigerWalletImage.sun_blue)
                globalvar.configs["theme"] = "default_light"
                self.apply_default_light_theme()

                """
                    Apply light/dark mode to settings window.
                    If settings window isn't initilized, do nothing
                """
                try:
                    self.s.apply_light_mode()
                except AttributeError:
                    pass

            elif globalvar.configs["theme"] == "default_light":
                self.sidebar_button[6].setIcon(TigerWalletImage.moon_blue)
                globalvar.configs["theme"] = "default_dark"
                self.apply_default_dark_theme()

                try:
                    self.s.apply_dark_mode()
                except AttributeError:
                    pass

            with open(globalvar.conf_file, "w") as f:
                json.dump(globalvar.configs, f, indent=4)

        # Update balance
        def update_balance(self, number):
            num = rm_scientific_notation(number)
            self.val.setText(f"Balance: ${str(num)}")

            '''
            if self.val.text() == "No internet connection":
                self.val.resize(550, +len(str(self.money)), 40)
                self.val.move(444, 38)
            '''

            if len(self.val.text() + str(self.money)) == 16:
                self.val.resize(224 + len(str(self.money)), 40)
                self.val.move(438, 38)

            else:
                self.val.resize(472 + len(str(self.money)), 40)
                self.val.move(306, 38)

        #
        def update_price(self):
            for pos in range(len(globalvar.assets_addr)):
                item = QTableWidgetItem(
                    globalvar.assets_details["price"][pos]
                )

                self.table.setItem(pos + 1, 2, item)

        def update_eth_price(self, new_price):
            self.table.setItem(
                0,
                2,
                QTableWidgetItem(f" {new_price}")
            )

        # Add coin function
        def add_coin(self,
            coin_name=None,
            coin_address=None,
            coin_symbol=None,
            invoked_from_worker=False
        ):
            token_image(coin_address)

            with ThreadPoolExecutor() as pool:
                contract = create_contract(coin_address)

                if not invoked_from_worker:
                    bal = pool.submit(
                        contract.functions.balanceOf(self.address).call
                    ).result()

                    bal = w3.from_wei(
                        float(bal),
                        'ether'
                    )

                    self.assets["value"].append(str(bal)[:17])
                    globalvar.assets_addr.append(coin_address)

                price = pool.submit(
                    lambda: get_price(coin_symbol)
                ).result()

                if price == "N/A":
                    price = 'N/A'

                self.assets["symbol"].append(coin_symbol.upper())
                self.assets["price"].append(price)
                self.assets["name"].append(coin_name.upper())

                sz = len(self.assets["name"])

                img = (
                    globalvar.tokenimgfolder
                    + globalvar.assets_details["symbol"][sz - 1].lower()
                    + ".png"
                )

                globalvar.assets_details["image"].append(
                    img
                )

            globalvar.assets_details = self.assets
            self.table.setRowCount(self.table.rowCount() + 1)

            # Clear table
            self.clear_main_table_contents()

            self.table.setItem(0, 0, QTableWidgetItem(" ETHER (ETH)"))
            self.table.setItem(0, 1, self.ethbal)
            self.table.setItem(0, 2, QTableWidgetItem(" " + self.eth_price))
            self.table.item(0, 0).setIcon(TigerWalletImage.eth_img)

            with ThreadPoolExecutor() as pool:
                asset_label = [
                    f" {self.assets['name'][i]} ({self.assets['symbol'][i]})"
                    for i in range(sz)
                ]

                pool.submit(
                    [
                        self.table.setItem(
                            i + 1,
                            0,
                            QTableWidgetItem(asset_label[i])
                        )
                        for i in range(sz)
                    ]
                )

                pool.submit(
                    [
                        self.table.item(i + 1, 0).setIcon(
                            QIcon(globalvar.assets_details["image"][i])
                        )
                        for i in range(sz)
                    ]
                )

                pool.submit(
                    [
                        self.table.setItem(
                            i + 1,
                            1,
                            QTableWidgetItem(self.assets["value"][i])
                        )
                        for i in range(sz)
                    ]
                )

                pool.submit(
                    [
                        self.table.setItem(
                            i + 1,
                            2,
                            QTableWidgetItem(f" {self.assets['price'][i]}"),
                        )
                        for i in range(sz)
                    ]
                )

                pool.submit(
                    [
                        self.table.item(i, 0).setSizeHint(QSize(278, 50))
                        for i in range(sz)
                    ]
                )

                pool.submit(
                    [
                        self.table.item(i, 1).setSizeHint(QSize(220, 50))
                        for i in range(sz)
                    ]
                )

                pool.submit(
                    [
                        self.table.item(i, 2).setSizeHint(QSize(218, 50))
                        for i in range(sz)
                    ]
                )

            with open(globalvar.assets_json, "w") as f:
                json.dump(
                    obj=globalvar.assets_addr,
                    fp=f,
                    indent=4
                )

            self.table.resizeColumnsToContents()
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
        def rm_coin(self):
            self.ind = self.table.selectionModel().selectedRows()

            amount_rows_selected = len(self.ind)

            if amount_rows_selected == 0:
                errbox("No coin was selected")
                return

            if 0 in self.ind:
                errbox("Ether cannot be removed")
                self.table.clearSelection()
                return

            # Get tokens' value(s)
            removed_items_value = [
                self.table.item(self.ind[i].row(), 1).text()
                for i in range(amount_rows_selected)
            ]

            # Get tokens' price
            removed_items_price = [
                self.table.item(self.ind[i].row(), 2).text()
                for i in range(amount_rows_selected)
            ]

            amount_to_deduct = [
                float(amount)
                * float(price) if not ' N/A' else 0.0
                for amount in removed_items_value
                for price in removed_items_price
            ]

            current_balance = float(
                self.val.text()[10:len(self.val.text())]
            )

            for item in amount_to_deduct:
                current_balance -= item

            current_balance = rm_scientific_notation(
                current_balance
            )

            self.val.setText(
                f"Balance: ${current_balance}"
            )

            # https://stackoverflow.com/questions/37786299/how-to-delete-row-rows-from-a-qtableview-in-pyqt
            for row in reversed(sorted(self.ind)):
                self.table.removeRow(row.row())
                del globalvar.assets_addr[row.row() - 1]

                try:
                    os.remove(globalvar.assets_details["image"][row.row() - 1])
                except FileNotFoundError:
                    pass

            with open(globalvar.assets_json, "w") as f:
                json.dump(
                    obj=globalvar.assets_addr,
                    fp=f,
                    indent=4
                )

            msgbox("Deletion complete")

            self.rm_coin_continue.close()
            self.rm_coin_cancel.close()
            self.uppermsg.close()
            self.table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.NoSelection
            )

            self.thread.start()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.val.show()

        def restore_default_coins(self):
            if globalvar.assets_addr == globalvar.addresses:
                errbox("List is the same as the default list")
                return

            self.res = questionbox(
                "This will restore the asset list to the default state. Continue?"
            )

            if not self.res:
                self.res = None
                return

            """
                This is a cheap way of doing this,
                but it works fine, so I'll keep it this way, for now
            """
            globalvar.assets_addr = globalvar.addresses
            self.alb = AssetLoadingBar()
            self.alb.show()
            self.close()
            self.deleteLater()

            # with open(globalvar.assets_json, w')

        # Add contact details
        def add_contact_details(self, name, a):
            if len(name) == 0:
                errbox("Empty name")
                return

            elif len(a) == 0:
                errbox("No address was provided")
                return

            if not w3.is_address(a):
                errbox("Invalid ERC-20 address")
                return

            elif w3.is_address(a) and len(a) < 42:
                errbox(
                    'You are trying to add a contract address, '
                    'not a wallet address!'
                )
                return

            if name in self.contacts["name"]:
                errbox("A contact with this name already exists")
                return

            elif a in self.contacts["address"]:
                errbox("This address is already in your contacts")
                return

            self.contacts["name"].append(name)
            self.contacts["address"].append(a)
            self.size = len(self.contacts["name"]) - 1

            self.contact_table.insertRow(self.size)
            self.contact_table.setItem(self.size, 0, QTableWidgetItem(name))

            self.contact_table.setItem(self.size, 1, QTableWidgetItem(a))

            with open(globalvar.contactsjson, "w") as f:
                json.dump(
                    obj=globalvar.contactbook,
                    fp=f,
                    indent=4
                )

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
                QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems
            )
            self.contact_table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.NoSelection
            )
            self.contact_table.clearSelection()
            self.add_contact.show()
            self.del_contact.show()
            self.close_book.show()

            with open(globalvar.contactsjson, "w") as f:
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

        #
        def clear_tab1_contents(self):
            self.default_btn1_style()
            self.sidebar_button[0].setEnabled(True)
            # self.sidebar_button[0].clicked.connect(self.show_tab1_contents)

            self.box1.hide()
            self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.tab = 0
            return

        def clear_tab2_contents(self):
            self.default_btn2_style()
            self.sidebar_button[1].setEnabled(True)

            self.box2.hide()
            self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.tab = 0
            return

        def clear_tab3_contents(self):
            self.default_btn3_style()
            self.sidebar_button[2].setEnabled(True)

            self.box3.hide()
            self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.tab = 0
            return

        def clear_tab4_contents(self):
            self.default_btn4_style()
            self.sidebar_button[3].setEnabled(True)

            self.box4.hide()
            self.thread.start()
            self.table.show()
            self.val.show()
            self.border.show()
            self.add_coin_btn.show()
            self.default_coin_btn.show()
            self.del_coin_btn.show()
            self.tab = 0

            # Add contact
            if self.add_contact_section2:
                self.cname.close()
                self.caddr.close()
                self.form1.close()
                self.form2.close()
                self.close_add.close()
                self.continue_add.close()
                self.enter_details.close()
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

                # self.add_contact_section2 = False

            # Remove contact
            elif self.add_contact_section3:
                self.close_rm.close()
                self.continue_rm.close()

                # Remove the piece of trash selection highlighting
                self.contact_table.setSelectionMode(
                    QtWidgets.QAbstractItemView.SelectionMode.NoSelection
                )

                self.contact_table.setSelectionBehavior(
                    QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems
                )

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
            return

        def clear_tab5_contents(self):
            self.wh.hide()
            self.tab = 0

        def clear_donation_tab(self):
            self.default_donobtn_style()
            self.sidebar_button[7].setEnabled(True)
            self.close_dono.close()
            self.dono_msg.close()
            self.dono_label.close()

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
            return

    import sys

    # Underlying root
    app = QApplication(sys.argv)
    app.setWindowIcon(TigerWalletImage.eth_img)

    json_contents = {}

    with open(globalvar.conf_file, "r") as f:
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

    updates.show()

    app.exec()

if __name__ == "__main__":
    main()
