# app.py

from flask import Flask, jsonify

import json
import requests

app = Flask(__name__)

# Node URL for JSON-RPC queries
nodeURL = "http://xpm:ZGkadYaDMKVyIQcVVw8D87njCJntSmRddM3FdmVcI6A=@rpc16.primecoin.org:9912"

@app.route('/api/rpc/searchrawtransactions/<address>')
def searchRawTransactions(address):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": "searchrawtransactions",
        "params": [address],
        "jsonrpc": "1.0",
        "id": "zappa-explorer",
    }
    response = requests.post(nodeURL, data=json.dumps(payload), headers=headers).json()
    return jsonify(response), 200


@app.route('/api/rpc/getaddressbalance/<address>')
def getAddressBalance(address):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": "getaddressbalance",
        "params": [ json.dumps({"addresses": [address]}) ],
        "jsonrpc": "1.0",
        "id": "zappa-explorer",
    }
    response = requests.post(nodeURL, data=json.dumps(payload), headers=headers).json()
    return jsonify(response), 200


@app.route('/api/rpc/getbestblock/')
def getBestBlock():
    headers = {'content-type': 'application/json'}
    payload = {
        "method": "getbestblockhash",
        "params": [],
        "jsonrpc": "1.0",
        "id": "zappa-explorer",
    }
    blockHash = requests.post(nodeURL, data=json.dumps(payload), headers=headers).json()["result"]
    payload = {
        "method": "getblock",
        "params": [ blockHash ],
        "jsonrpc": "1.0",
        "id": "zappa-explorer",
    }
    response = requests.post(nodeURL, data=json.dumps(payload), headers=headers).json()
    return jsonify(response), 200


# include this for local dev

if __name__ == '__main__':
    app.run()
