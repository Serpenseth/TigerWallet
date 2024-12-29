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

# Installation

The simplest way to install TigerWallet is to use:

```
pip install git+https://github.com/Serpenseth/TigerWallet.git
```

<u>However, there are a few things that are required to run TigerWallet, based on your Operating System:</u>

## Windows:
Window users need to install [this packpage](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Linux
`libxcb-cursor-dev` is required on *nix to run TigerWallet.

This is installed like any Linux package; i.e for `Debian`, you would use:
```
sudo apt install libxcb-cursor-dev
```

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

**Windows**
```
py -m pip install --upgrade setuptools
```
Next, you will need `python3-venv`:

This is installed like any Linux package; i.e for `Debian`, you would use:
```
sudo apt install python3-venv
```
Now use the `cd` command to change the directory to the TigerWallet folder that you've cloned, i.e:
```
cd pathtofolder/TigerWallet-1.0
```
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
to run the program.

# Contact
All comments are welcome!

Contact: <serpenseth@tuta.io>

