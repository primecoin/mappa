# Mappa

A minimalist explorer for Primecoin.

### Configurations

Configure the flask app by setting config.py and instance/config.py:

```
# config.py

# Configure mainnet/testnet
NETWORK = "mainnet"
```

```
# instance/config.py
#
# To open node rpc to the Internet, enable rpc settings in node configuration.
#
# For Satoshi 0.8 nodes (Primecoin 0.1.2 production):
# rpcuser=<rpc user name>
# rpcpassword=<rpc password>
# rpcallowip=*
#
# For Satoshi 0.16 nodes (Primecoin development)
# rpcauth=<output line from share/rpcauth/rpcauth.py>
# rpcallowip=0.0.0.0/0

MAINNET_RPC_URL = "http://<rpcuser>:<rpcpassword>@<nodedomain>:9912"
TESTNET_RPC_URL = "http://<rpcuser>:<rpcpassword>@<nodedomain>:9914"
```

Test locally:

```
flask run
```
