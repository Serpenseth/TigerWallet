# What is TigerWallet?

TigerWallet is a non-custodial wallet, built in Python

# Who is it for?

Everyone that is curious about Web3, and wants to try it out, 
while also having some features that advanced users would appreciate (custom RPC)

# What does it solve?

TigerWallet simplifies things by providing an easy to user interface. Every design element had "ease of use" in mind

# What platforms does it support?

Currently, TigerWallet supports Windows 10 (untested on Windows 11), Linux (tested on Ubuntu/Debian, so all flavors of said distros should work),
and MacOS Monterey and upper (untested on M series Macs, but it should work just fine)

##

It currently supports the Ethereum mainnet, and Base. 

**Pros of using TigerWallet**:
1. Non-custodial. You own your crypto assets. Your private key is stored on your device, and it is also encrypted. Your private key does not leave your device while using TigerWallet as well.

2. Simple. The design choices were all geared towards simplicity.

3. No signing when sending/swapping tokens. Forget having to sign transactions!

4. You can add any coin* that is listed on a centralized exhange.
   * TigerWallet currently uses an API that is free, and it only fetches the price from centralized exchanges.

5. TigerWallet runs on Windows, Linux, and MacOS*
   * Currently supports Monterey and higher. Untested on M series Macs


**Current cons of using TigerWallet (working on it!)**:
1. No NFT support
2. No dApps and WalletConnect support
3. No Buy/Sell tokens with fiat (i.e Onramper)
4. No in-app staking
5. No QR code scanning

~~Only supports Ethereum mainnet~~

~~No ENS support (changing in next update)~~   

~~No in-app swap~~

# Requirements for running TigerWallet
TigerWallet requires `python3.11`
The highest version that I have tested is `python3.12`

The latest version has not been tested, and may not work

If you have issues, download `python3.11`

Windows users can get `python3.11` from the official [python website](https://www.python.org/downloads/windows/)

Mac users will need to install it using `homebrew`. Read the Mac section

## Linux
Linux these days typically comes bundled with `python3` out of the box. 

Check the system's python by using the following command:

```
python3 --version
```

If the version is lower than `python3.11`, then you will need to update your Python.

Try the following command:
```bash
sudo apt install python3.11
```

If you get an error, then execute the following list of commands by pasting them into the terminal (if you execute them one by one, remove `&& \` for every command):

```bash
sudo add-apt-repository ppa:deadsnakes/ppa && \
sudo apt update && \
sudo apt install python3.11 && \
sudo apt install python3.11-dev && \
sudo apt install python3.11-venv && \
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
exec /usr/bin/env python3.11 -m pip install --upgrade setuptools
```

You now have `python3.11` installed.

For every command that says `python3`, replace it with `python3.11`

Ubuntu/Debian users require the following package to be installed: `libxcb-cursor-dev`
Install it using:
```
sudo apt install libxcb-cursor-dev
```

## Mac
While Macs tend to come with Python, it's recommended to install it using `homebrew`

Here are the steps:

1. Execute the following command in the terminal:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Once the installation has completed, execute the following command:
```
brew install python@3.11
```

Once it's installed, you are ready to go!

# Installation

TigerWallet is installed using:

**Windows**:
```
pip install git+https://github.com/Serpenseth/TigerWallet.git
```

**Linux**:
```
python3 -m pip install git+https://github.com/Serpenseth/TigerWallet.git
```

**Mac**:
```
pip3.11 install git+https://github.com/Serpenseth/TigerWallet.git
```

To run tigerwallet, type
```
tigerwallet
```

into the terminal and press enter

TigerWallet also includes a traditional Windows installer (which can be found [here](https://github.com/Serpenseth/TigerWallet/releases))

# Building from source code
In order to build TigerWallet, you will to install a few requirements

## Build requirements
1. You will need to install build tools `setuptools` and `build`, which you can install by issuing the following command:

**Windows**
```
pip install setuptools && pip install build
```
**Linux**
```
python3 -m pip install setuptools && pip install build
```
On mac, `setuptools` gets installed automatically. You'll need to install `build`

**Mac**
```
pip3.11 install build
```

2. Optional. You will need `git` if you don't want to download the source code as a `zip`.

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

**Linux/mac**, issue the following command to change directories
```
cd ~/TigerWallet
```
**Windows**, issue the following command to change directories

command prompt:
```
cd %userprofile% && cd TigerWallet
```
powershell:
```powershell
cd ~\\TigerWallet
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

**Mac**
```
python3.11 -m build .
```

4. Issue the following command to install TigerWallet:

**Windows users**
```
py install .
```
**Linux**
```
python3 -m pip install .
```

**Mac**
```
pip3.11 install .
```

To run tigerwallet, execute the following command:
```
tigerwallet
```

# Building the pyinstaller executables

To build the executables, you will need `pyinstaller`

1. Install `pyinstaller` by using the following command:

**Windows users**
```
py install pyinstaller
```

**Linux**
```
python3 -m pip install pyinstaller
```

**Mac**
```
pip3.11 install pyinstaller
```

2. You will need to enter into the directory of the downloaded folder. Typically, this is in the `home` directory

**Linux**, issue the following command to change directories
```
cd ~/TigerWallet
```

**Windows**, issue the following command to change directories

command prompt:
```
cd %userprofile% && cd TigerWallet
```
powershell:
```powershell
cd ~\\TigerWallet
```

In order to use TigerWallet on another version of your OS you will need all of the requirements installed

You can either do this with 

**Windows**
```
pip install git+https://github.com/Serpenseth/TigerWallet.git
```

or
```
pip install -r requirements.txt
```

**Linux**:
```
python3 -m pip install git+https://github.com/Serpenseth/TigerWallet.git
```

or
```
python3 -m pip install -r requirements.txt
```

**Mac**:
```
pip3.11 install git+https://github.com/Serpenseth/TigerWallet.git
```

or
```
pip3.11 install -r requirements.txt
```


4. Issue the following command to build tigerwallet

**Windows**

powershell:
```powershell
`
py -m PyInstaller src/TigerWallet/tigerwallet.py --onedir `
--add-data "src/TigerWallet/images/:images" `
--add-data "src/TigerWallet/images/token_images/*:images/token_images" `
--add-data "README.md:." `
--add-data "LICENSE:." `
--add-data "src/TigerWallet/dark.css:." `
--add-data "src/TigerWallet/light.css:." `
--add-data "english.txt:eth_account/hdaccount/wordlist" `
--hidden-import="web3.utils.subscriptions" `
--icon "src/TigerWallet/tigerwallet_logo.ico" `
--windowed `
--name "tigerwallet-3.1-x86-64-windows"
```
command prompt:
```cmd
py -m PyInstaller src/TigerWallet/tigerwallet.py --onedir ^
--add-data "src/TigerWallet/images/:images" \
--add-data "src/TigerWallet/images/token_images/*:images/token_images" ^
--add-data "README.md:." ^
--add-data "LICENSE:." ^
--add-data "src/TigerWallet/dark.css:." ^
--add-data "src/TigerWallet/light.css:." ^
--add-data "english.txt:eth_account/hdaccount/wordlist" ^
--hidden-import="web3.utils.subscriptions" ^
--icon "src/TigerWallet/tigerwallet_logo.ico" ^
--windowed ^
--name "tigerwallet-3.1-x86-64-windows"
```

**Linux**

```bash
python3 -m PyInstaller src/TigerWallet/tigerwallet.py --onedir \
--add-data "src/TigerWallet/images/:images" \
--add-data "src/TigerWallet/images/token_images/*:images/token_images" \
--add-data "README.md:." \
--add-data "LICENSE:." \
--add-data "src/TigerWallet/dark.css:." \
--add-data "src/TigerWallet/light.css:." \
--add-data "english.txt:eth_account/hdaccount/wordlist" \
--hidden-import="web3.utils.subscriptions" \
--icon "src/TigerWallet/tigerwallet_logo.ico" \
--windowed \
--name "tigerwallet-3.1-x86-64-linux"
```

**Mac**

```zsh
python3.11 -m PyInstaller src/TigerWallet/tigerwallet.py --onedir \
--add-data "src/TigerWallet/images/:images" \
--add-data "src/TigerWallet/images/token_images/*:images/token_images" \
--add-data "README.md:." \
--add-data "LICENSE:." \
--add-data "src/TigerWallet/dark.css:." \
--add-data "src/TigerWallet/light.css:." \
--add-data "english.txt:eth_account/hdaccount/wordlist" \
--hidden-import="web3.utils.subscriptions" \
--icon "src/TigerWallet/tigerwallet_logo.ico" \
--windowed \
--name "tigerwallet-3.11-macos"
```

The `-n` command gives the executable a name.

The `--add-data "english.txt:eth_account/hdaccount/wordlist"` line is required, because pyinstaller has issues with adding that file automatically

Same applies to `--hidden-import="web3.utils.subscriptions"`. Pyinstaller doesn't automatically include it in the finished executable

## Running the executables
To run tigerwallet, double click the executable

# Building the .exe installer

The steps required to build the installer are tedious, unfortunately.
This section is for **Windows** only.

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

command prompt:
```
cd %userprofile% && cd TigerWallet
```
powershell:
```powershell
cd ~\\TigerWallet
```
5. Issue the following command to build the installer:
```
pynsist pytest.cfg
```
6. Copy the `installer.nsi` file into the build directory using the following command:
```
copy installer.nsi build\\nsis\\
```
Overwrite the file that is already there

7. Copy the TigerWallet logo into the build directory using the following command:
```
copy src\\TigerWallet\\tigerwallet_logo.ico build\\nsis\\
```

8. Right-click the `installer.nsi` file, and select `Compile NSIS Script`

You will now have the same installer as in the release section of TigerWallet

# Troubleshoot

1. If you double-click the `.AppImage` or the executable and nothing happens, please read [this section](https://github.com/Serpenseth/TigerWallet?tab=readme-ov-file#linux)

2. You might be missing dependencies.
Install them using the following command:

**Windows users**
```
pip install -r requirements.txt.
```
**Linux**
```
python3 -m pip install -r requirements.txt.
```

**Mac**
```
pip3.11 install -r requirements.txt.
```

# Contact
All comments are welcome!

Contact: <serpenseth@tuta.io>

