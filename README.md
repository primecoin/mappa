# Mappa

A minimalist explorer for Primecoin.

### Installation


```
git clone ssh://git@github.com/primecoin/mappa
cd mappa
pipenv shell
pipenv install zappa flask Flask-JSONRPC
pipenv install --dev awscli
```

### Configurations

Configure the flask app via configuration files `config.py` and `instance/config.py`:

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
MAINNET_RPC8_URL = "http://<rpcuser>:<rpcpassword>@<nodedomain>:9912"
TESTNET_RPC8_URL = "http://<rpcuser>:<rpcpassword>@<nodedomain>:9914"
```

Test locally:

```
flask run
```

By default the test server is located at `http://localhost:5000/`.

### Deployment

Amazon AWS deployment requires awscli.

```
zappa init
```

Add `certificate_arn` and `domain` settings to `zappa_settings.json`. To deploy the web service:

```
zappa deploy
zappa certify dev
```

To terminate the web service:

```
zappa undeploy
```
