# Zappa Explorer

Zappa Explorer is a minimalist explorer for Primecoin.

### Configurations

Configure the flask app by setting config.py and instance/config.py:

```
# config.py

# Configure mainnet/testnet
NETWORK = "mainnet"
```

```
# instance/config.py

MAINNET_RPC_URL = "<mainnet url>"
TESTNET_RPC_URL = "<testnet url>"
```

Test locally:

```
flask run
```
