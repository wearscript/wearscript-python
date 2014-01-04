# Wearscript for Python #
<http://github.com/OpenShades/wearscript>

## About ##

Various hooks and command line tools for interacting with wearscript in Python.

Also includes 'wearscript' command line client for testing and shell-hackery.

## Requirements ##

  * libevent-dev 
  * pip
  * python 2.* ( Dependant libraries don't support 3 yet )
  * A running wearscript server to connect to
  * At least one connected Glass

## Installation ##

The easiest way to install with needed library dependencies is with pip

### Stable ###

```bash
pip install wearscript
```

### Development ###

```bash
pip install -e git+https://github.com/OpenShades/wearscript-python/#egg=wearscript
```

## Usage ##

Wearscript client libraries require the client endpoint of a connected glass
on a running wearscript server.

This is expected to be accessible via the WEARSCRIPT_ENDPOINT envirionment
variable.

Here is one way to set that up:

1. Visit a wearscript server (Demo: https://api.picar.us/wearscriptdev/)
2. Accept Google Authentication Permissions
3. Under endpoints, click QR.
4. Scan code via "Ok Glass, Setup Wearscript"
5. Say "OK Glass, Start Wearscript" and it should say "Connected"
6. Under endpoints, click "Client Endpoint" and copy URL
7. Put this in your .bashrc and source it:

    ```bash
    echo "WEARSCRIPT_ENDPOINT=wss://api.picar.us/wearscriptdev/ws/client/iHFr9Yuy9Rl9hnsr" >> ~/.bash_rc
    source .bashrc
    ```
8. Test sending yourself a card via the wearscript command line client

    ```bash
    wearscript --card "I am connected :D"
    ```
