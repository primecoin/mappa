# app.py

from flask import Flask, jsonify, render_template

import json
import requests

app = Flask(__name__)

# Node URL for JSON-RPC queries
nodeURL = "http://xpm:ZGkadYaDMKVyIQcVVw8D87njCJntSmRddM3FdmVcI6A=@rpc16.primecoin.org:9912"

def requestJsonRPC(method, params):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "1.0",
        "id": "zappa-explorer",
    }
    return requests.post(nodeURL, data=json.dumps(payload), headers=headers).json()


# API based on node JSON-RPC

@app.route('/api/rpc/searchrawtransactions/<address>')
def searchRawTransactions(address):
    response = requestJsonRPC("searchrawtransactions", [address])
    return jsonify(response), 200

@app.route('/api/rpc/getaddressbalance/<address>')
def getAddressBalance(address):
    response = requestJsonRPC("getaddressbalance", [ json.dumps({"addresses": [address]}) ] )
    return jsonify(response), 200

@app.route('/api/rpc/getbestblock/')
def getBestBlock():
    response = requestJsonRPC("getbestblockhash", [])
    if "error" in response and response["error"] != None:
        return jsonify(response), 200
    else:
        blockHash = response["result"]
        response = requestJsonRPC("getblock", [blockHash, 2])
        return jsonify(response), 200

@app.route('/api/rpc/getblock/<heightOrAddress>')
def getBlock(heightOrAddress):
    try:
        height = int(heightOrAddress)
        isHeight = True
    except:
        blockHash = heightOrAddress
        isHeight = False
    if isHeight:
        response = requestJsonRPC("getblockhash", [height])
        if "error" in response and response["error"] != None:
            return jsonify(response), 200
        else:
            blockHash = response["result"]
    response = requestJsonRPC("getblock", [blockHash, 2])
    return jsonify(response), 200

@app.route('/api/rpc/getrawtransaction/<txid>')
def getRawTransaction(txid):
    response = requestJsonRPC("getrawtransaction", [txid, True])
    return jsonify(response), 200

@app.route('/api/rpc/getblockchaininfo/')
def getBlockchainInfo():
    response = requestJsonRPC("getblockchaininfo", [])
    return jsonify(response), 200


# Web Pages

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/block/<heightOrAddress>")
def block(heightOrAddress):
    return render_template("block.html", **locals())

@app.route("/transaction/<txid>")
def transaction(txid):
    return render_template("transaction.html", **locals())

# include this for local dev
if __name__ == '__main__':
    app.run()
