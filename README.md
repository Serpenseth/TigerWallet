What is TigerWallet?

TigerWallet is a non-custodial wallet, built in Python, that aims to be user-friendly, minimalistic, and easy to use.

It currently supports the Ethereum mainnet, meaning that most* Ethereum tokens can be sent from/sent to TigerWallet.

**Pros of using TigerWallet**:
1. Non-custodial. You own your crypto assets. Your private key is stored on your device, and it is also encrypted. Your private key does not leave your device while using TigerWallet as well.

2. Simple. The design choices were all geared towards simplicity.

3. Lightweight. TigerWallet barely comsumes any resources. It is quite light, and easy to run.

4. You can add any coin* that is listed on a centralized exhange.
   * TigerWallet currently uses an API that is free, and it only fetches the price from centralized exchanges.

5. TigerWallet runs on Windows, Linux, and Mac*
   * In theory, it should work in Mac, too, but that has not been tested, yet


**Cons of using TigerWallet**:
1. Only supports Ethereum mainnet
2. No NFT support
3. No dApps and WalletConnect support
4. No Buy/Sell tokens with fiat (from i.e Onramper)
5. No in-app staking
6. No QR code scanning
   
~~No ENS support (changing in next update)~~   
~~No in-app swap~~

# Requirements for running TigerWallet
TigerWallet requires `python3`. 

Windows users can get python from the official [python website](https://www.python.org/downloads/windows/)
Mac users can get the installer from the official [python website](https://www.python.org/downloads/macos/)

Once you have `python3`, you will need to install the dependencies. 
This is done by using the following command:
```
pip install -r requirements.txt
```

## Linux
Linux these days typically comes bundled with `python3` out of the box. You can check if you have `python3` by using the following command:
```
which python3
```
If nothing is written to the terminal, then you need to install `python3`

Install it using your distro's package manager, for example:
Ubuntu/Debian users install `python3` by issuing the following command:
```
sudo apt install python3
```

Ubuntu/Debian users require the following package to be installed: `libxcb-cursor-dev`
Install it using:
```
sudo apt install libxcb-cursor-dev
```

# Installation

TigerWallet is installed using:
```
pip install git+https://github.com/Serpenseth/TigerWallet.git
```

TigerWallet also includes a traditional Windows installer (which can be found [here](https://github.com/Serpenseth/TigerWallet/releases))

# Building from source code
In order to build TigerWallet, you will to install a few requirements

## Build requirements
1. You will need to install `setuptools`, which is installed by issuing the following command:
```
pip install setuptools
```

2. You will need `build`, which is installed by issuing the following command:
```
pip install build
```

3. Optional. You will need `git` if you don't want to download the source code as a `zip`.

Windows users: download and install `git` from the [official website](https://git-scm.com/downloads/win)
Linux users: install `git` by following the instructions from [official website](https://git-scm.com/downloads/linux)
Mac users: install `git` by following the instructions from [official website](https://git-scm.com/downloads/mac)


### Installation
Once you have the above requirements, you are ready to install TigerWallet

1. Use `git` to download the source code. This is done by issuing the following command:
```
git clone https://github.com/Serpenseth/TigerWallet.git
```
2. You will need to enter into the directory of the downloaded folder. Typically, this is in the `home` directory

**Linux/mac users**, issue the following command to change directories
```
cd ~/TigerWallet
```
**Windows users**, issue the following command to change directories
```
cd %userprofile%\\TigerWallet
```

3. Issue the following command to build the installer files:

**Windows users**
```
py -m build .
```
**Linux**
```
python3 -m build .
```

4. Issue the following command to install TigerWallet:
```
pip install .
```

To run tigerwallet, execute the following command:
```
tigerwallet
```

# Building the executables
To build the executables, you will need `pyinstaller`

1. Install `pyinstaller` by using the following command:
```
pip install pyinstaller
```

2. You will need to enter into the directory of the downloaded folder. Typically, this is in the `home` directory

**Linux/mac users**, issue the following command to change directories
```
cd ~/TigerWallet
```
**Windows users**, issue the following command to change directories
```
cd %userprofile%\\TigerWallet
```

3. Issue the following command to build tigerwallet
```
pyinstaller tigerwallet.py --onefile --add-data "images/:images" --add-data "images/token_images/*:images/token_images" --add-data "README.md:README.md" --add-data "LICENSE:LICENSE" -i "eth.ico" --windowed -n "tigerwallet-2.1-x86-64"
```
The `-n` command gives the executable a name. Make sure you change the numbers `2.1` to the current version

## Running the executables
To run tigerwallet, double click the executable

# Building the .exe installer

The steps required to build the installer are tedious, unfortunately.
This section is for **windows** only.

## Build requirements
1. Install `nsis` from the [official website](https://nsis.sourceforge.io/Download)
2. Install `pynsist` by using the following command:
```
pip install pynsist
```
3. Use `git` to download the source code. This is done by issuing the following command:
```
git clone https://github.com/Serpenseth/TigerWallet.git
```
4. You will need to enter into the directory of the downloaded folder. Typically, this is in the `home` directory
```
cd %userprofile%\\TigerWallet
```
5. Issue the following command to build the installer
```
pynsist pytest.cfg
```
6. Copy the `installer.nsi` file, and paste it into the following directory
```
cd %userprofile%\\TigerWallet\\build\\nsis
```
Overwrite the file that is already there
7. Right-click the `installer.nsi` file, and select `Compile NSIS Script`

You will now have the same installer as in the release section of TigerWallet

# Troubleshoot

If you double-click the `.AppImage`, and nothing happens, please read [this section](https://github.com/Serpenseth/TigerWallet?tab=readme-ov-file#linux)


# Contact
All comments are welcome!

Contact: <serpenseth@tuta.io>

