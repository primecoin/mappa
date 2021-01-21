# Mappa

A minimalist explorer for Primecoin.

### Installation


```sh
### Instructions for Ubuntu 18.04 LTS
### Clone repo:
$ git clone ssh://git@github.com/primecoin/mappa
$ cd mappa

### Set up pipenv:
$ sudo apt install python3-pip
$ sudo -H pip3 install --upgrade pipenv
$ pipenv shell
$ pipenv install
$ pipenv install --dev awscli
```

### Configurations

Configure the flask app via configuration file `instance/config.py`:

```sh
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

RPC = "http://<rpc-user>:<rpc-password>@<rpc-host>:<rpc-port>"
RPC8 = "http://<rpc-user>:<rpc-password>@<rpc-host>:<rpc-port>"
```

Test locally:

```sh
flask run
```

By default the test server is located at `http://localhost:5000/`.

### Deployment via AWS

Amazon AWS deployment requires awscli.

```sh
zappa init
```

Add `certificate_arn` and `domain` settings to `zappa_settings.json`. To deploy the web service:

```sh
zappa deploy
zappa certify dev
```

To terminate the web service:

```sh
zappa undeploy
```

### Deployment via Docker

```sh
docker run -p 5000:5000 -d \
    primecoin/mappa \
        --rpc=http://<rpc-user>:<rpc-password>@<rpc-host>:<rpc-port> \
        --rpc8=http://<rpc-user>:<rpc-password>@<rpc-host>:<rpc-port>
```
