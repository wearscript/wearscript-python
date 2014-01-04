# WearScript for Python #
<http://github.com/OpenShades/wearscript>

## About ##

Various hooks and command line tools for interacting with WearScript in Python.

Also includes 'wearscript' command line client for testing and shell-hackery.

## Requirements ##

  * libevent-dev 
  * pip
  * python 2.* ( Dependant libraries don't support 3 yet )
  * A running WearScript server to connect to
  * At least one connected Glass

## Installation ##

The easiest way to install with needed library dependencies is with pip

### Stable ###

```bash
sudo pip install wearscript
```

### Development ###

```bash
sudo pip install -e git+https://github.com/OpenShades/wearscript-python/#egg=wearscript
```

## Usage ##

Wearscript client libraries require the client endpoint of a connected glass
on a running wearscript server.

This is expected to be accessible via the WEARSCRIPT_ENDPOINT envirionment
variable.

Here is one way to set that up:

1. Visit a WearScript server (Demo: https://api.picar.us/wearscriptdev/)
2. Accept Google Authentication Permissions
3. Under endpoints, click QR.
4. Scan code via "Ok Glass, Setup Wearscript"
5. Say "OK Glass, Start Wearscript" and it should say "Connected"
6. Under endpoints, click "Client Endpoint" and copy URL
7. Put this in your .bashrc and source it:

    ```bash
    echo "WEARSCRIPT_ENDPOINT=wss://api.picar.us/wearscriptdev/ws/client/iHFr9Yuy9Rl9hnsr" >> ~/.bashrc
    source .bashrc
    ```
8. Test sending yourself a card via the WearScript command line client

    ```bash
    wearscript --card "I am connected :D"
    ```

From here, feel free to explore the CLI:

```bash
wearscript --help
```


