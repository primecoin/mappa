# app.py

from flask import Flask, jsonify

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


@app.route('/api/rpc/searchrawtransactions/<address>')
def searchRawTransactions(address):
    response = requestJsonRPC("searchrawtransactions", [ address])
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

@app.route('/api/rpc/getblockbyheight/<height>')
def getBlockByHeight(height):
    try:
        heightInteger = int(height)
    except:
        heightInteger = height
    response = requestJsonRPC("getblockhash", [ heightInteger ])
    if "error" in response and response["error"] != None:
        return jsonify(response), 200
    else:
        blockHash = response["result"]
        response = requestJsonRPC("getblock", [blockHash, 2])
        return jsonify(response), 200

@app.route('/api/rpc/getblockbyhash/<blockHash>')
def getBlockByHash(blockHash):
    response = requestJsonRPC("getblock", [ blockHash, 2])
    return jsonify(response), 200

@app.route('/api/rpc/getrawtransaction/<txid>')
def getRawTransaction(txid):
    response = requestJsonRPC("getrawtransaction", [txid, True])
    return jsonify(response), 200

# include this for local dev
if __name__ == '__main__':
    app.run()
