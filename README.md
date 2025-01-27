# TigerWallet

What is TigerWallet?

TigerWallet is a non-custodial wallet, 100% built in Python, that aims to be user-friendly, minimalistic, and easy to use.

It operates on the Ethereum mainnet, meaning that most* ERC-20 tokens can be sent from/sent to TigerWallet.

*Benefits of using TigerWallet*:
1. Non-custodial. You own your crypto assets. Your private key is stored on your device, and it is also encrypted. Your private key does not leave your device while using TigerWallet as well.

2. Simple. The design choices were all geared towards simplicity.

3. Lightweight. TigerWallet barely comsumes any resources. It is very light, and easy to run.

4. You can add any coin* that is listed on a centralized exhange.
    * TigerWallet currently use an API that is free, and it only fetches the price from centralized exchanges.

5. TigerWallet runs on Windows, Linux, and Mac


*Features that are currently missing*
TigerWallet is currently missing the following features:
1. Currently, it only supports Ethereum mainnet (changing in next update)
2. No NFT support
3. No ENS support (chaing in next update)
4. No dApps and WalletConnect support

TigerWallet also comes in a prebuilt package for both Windows and Linux.

The Windows prebuilt package does not does not require you to install anything. Simple double click the .exe and it launches.
If you get an error, [click here for the fix](https://github.com/Serpenseth/TigerWallet?tab=readme-ov-file#windows)

The appimage requires you to install dependencies before running it succesfully.

# Installation

The simplest way to install TigerWallet is to use:

```
pip install git+https://github.com/Serpenseth/TigerWallet.git
```

## OS-specific requirements
The items below are required in order to run TigerWallet

### Linux
1. `libxcb-cursor-dev`

To install `libxcb-cursor-dev` on Debian, issue the following command:
```
sudo apt install libxcb-cursor-dev
```
Adjust the above command to your distro.

### Windows:
If you get the following error:
>Visual C++ or Cython not installed

You need to install [this packpage](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

# Building
To build TigerWallet straight from the `.git` folder, you will need the latest version of `setuptools`.

You can install it by issuing the following command:
```
pip install setuptools
```
If you already have `setuptools` on your device, make sure that it's up to date by using:

**Linux/Mac**
```
python3 -m pip install --upgrade setuptools
```
Next, you will need `python3-venv`:

This is installed like any Linux package; i.e for `Debian`, you would use:
```
sudo apt install python3-venv
```

**Windows**
```
py -m pip install --upgrade setuptools
```
Finally, you will need `build`. This can be installed using:
```
pip install build
```
Now use the `cd` command to change the directory to the TigerWallet folder that you've cloned, for example:
```
cd pathtofolder/TigerWallet-x.x
```
where `x.x` is the version that you have cloned (for example `cd /home/bob/TigerWallet-1.0`)

Build the package using:

**Linux/Mac**
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

