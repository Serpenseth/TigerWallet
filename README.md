# TigerWallet

What is TigerWallet?

TigerWallet is a non-custodial wallet, 100% built in Python, that aims to be user-friendly, minimalistic, and easy to use.

It operates on the Ethereum mainnet, meaning that most* ERC-20 tokens can be sent from/sent to TigerWallet.

**Benefits of using TigerWallet**:
1. Non-custodial. You own your crypto assets. Your private key is stored on your device, and it is also encrypted. Your private key does not leave your device while using TigerWallet as well.

2. Simple. The design choices were all geared towards simplicity.

3. Lightweight. TigerWallet barely comsumes any resources. It is very light, and easy to run.

4. You can add any coin* that is listed on a centralized exhange.
   * TigerWallet currently use an API that is free, and it only fetches the price from centralized exchanges.

5. TigerWallet runs on Windows, Linux, and Mac*
   * In theory, it should work in Mac, too, but that has not been tested, yet


**Features that are currently missing:**

TigerWallet is currently missing the following features:
1. Only supports Ethereum mainnet (changing in next next update(sorry!))
2. No NFT support
~~3. No ENS support (changing in next update)~~
3. No dApps and WalletConnect support
~~5. No in-app swap~~
4. No Buy/Sell tokens with fiat (from i.e Onramper)
5. No in-app staking

TigerWallet also comes in a prebuilt package for both Windows and Linux.

The Windows prebuilt package does not does not require you to install anything. Simple double click the .exe and it launches.
If you get an error, or nothing happens, [click here for the fix](https://github.com/Serpenseth/TigerWallet?tab=readme-ov-file#windows)

The appimage requires you to install dependencies before running it succesfully.

# OS-specific requirements
The items below are required in order to run TigerWallet

## Linux
1. `libxcb-cursor-dev`

To install `libxcb-cursor-dev` on Debian, issue the following command:
```
sudo apt install libxcb-cursor-dev
```
Adjust the above command to your distro.

## Windows:
If you get the following error:
>Visual C++ or Cython not installed

You need to install [this packpage](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

# Installation

The simplest way to install TigerWallet is to use:

```
pip install git+https://github.com/Serpenseth/TigerWallet.git
```

## Building standalone executable
To build an executable that does not require you to have any Python dependencies installed, you will need `pyinstaller`

First, download the source code either via `git clone`, or by downloading the source code as a zip.

Install `pyinstaller` by using the following command:
```
pip install pyinstaller
```

Next, use the `cd` command to change the directory to the folder you have downloaded (or extracted, if downloaded the zip file)
```
cd /path/to/folder
```

You are now ready to build! Simply issue the following command:
```
pyinstaller tigerwallet.py --onefile --add-data "images/*:images" --add-data "README.md:README.md" --add-data "LICENSE:LICENSE" -i "eth.ico" --windowed -n "tigerwallet-2.0-x86-64"
```
The `-n` command gives the executable a name. Make sure you change the numbers `2.0` to the current version

Done!

## Building
To build TigerWallet straight from the `.git` folder, you will need the latest version of `build`.

You can install it by issuing the following command:
```
pip install build
```
If you already have `build` on your device, make sure that it's up to date by using:

**Linux**
```
python3 -m pip install --upgrade build
```

Next you will need `setuptools`.

You can install it by issuing the following command:
```
pip install setuptools
```
If you already have `setuptools` on your device, make sure that it's up to date by using:

**Linux**
```
python3 -m pip install --upgrade setuptools
```

Next, you will need `python3-venv`:

This is installed like any Linux package; i.e for `Debian`, you would use:
```
sudo apt install python3-venv
```

Now use the `cd` command to change the directory to the TigerWallet folder that you've cloned, for example:
```
cd pathtofolder/TigerWallet
```
for example `cd pathtofolder/TigerWallet` would look like /home/bob/TigerWallet on Linux (your path will be different)

Build the package using:

**Linux**
```
python3 -m build .
```

**Windows**
```
py -m build .
```
This will build the package.

Next, install the package using:
```
pip install .
```
Done!


# Running TigerWallet
From the `command promp` or `terminal`, simple use:
```
tigerwallet
```
to run the program. That's it! Now tigerwallet will launch, and you're ready to use it.

# Contact
All comments are welcome!

Contact: <serpenseth@tuta.io>

