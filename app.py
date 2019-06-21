# app.py

from flask import Flask, jsonify, render_template
from flask_jsonrpc import JSONRPC

import json
import requests

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
if 'NETWORK' not in app.config:
    raise RuntimeError("Setting 'NETWORK' is not configured")
if app.config['NETWORK'] != 'mainnet' and app.config['NETWORK'] != 'testnet':
    raise RuntimeError("Setting 'NETWORK' can only be 'mainnet' or 'testnet'")
if app.config['NETWORK'] == 'mainnet' and 'MAINNET_RPC_URL' not in app.config:
    raise RuntimeError("Setting 'MAINNET_RPC_URL' is not configured")
if app.config['NETWORK'] == 'mainnet' and 'MAINNET_RPC8_URL' not in app.config:
    raise RuntimeError("Setting 'MAINNET_RPC8_URL' is not configured")
if app.config['NETWORK'] == 'testnet' and 'TESTNET_RPC_URL' not in app.config:
    raise RuntimeError("Setting 'TESTNET_RPC_URL' is not configured")

jsonrpc = JSONRPC(app, '/jsonrpc/')


def requestJsonRPC(method, params, useProductionNode = False):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "1.0",
        "id": "mappa",
    }
    url = app.config['MAINNET_RPC_URL'] if app.config['NETWORK'] == 'mainnet' else app.config['TESTNET_RPC_URL']
    url = app.config['MAINNET_RPC8_URL'] if useProductionNode else url
    return requests.post(url, data=json.dumps(payload), headers=headers).json()

def requestBlock(heightOrAddress, useProductionNode = False):
    try:
        height = int(heightOrAddress)
        isHeight = True
    except:
        blockHash = heightOrAddress
        isHeight = False
    if isHeight:
        response = requestJsonRPC("getblockhash", [height], useProductionNode)
        if "error" in response and response["error"] != None:
            return response
        else:
            blockHash = response["result"]
    return requestJsonRPC("getblock", [blockHash] if useProductionNode else [blockHash, 2], useProductionNode)

def requestBestBlock(useProductionNode = False):
    if useProductionNode:
        response = requestJsonRPC("getinfo", [], useProductionNode)
        if "error" in response and response["error"] != None:
            return response
        else:
            blockHeight = response["result"]["blocks"]
            return requestBlock(blockHeight, useProductionNode)
    else:
        response = requestJsonRPC("getbestblockhash", [])
        if "error" in response and response["error"] != None:
            return response
        else:
            blockHash = response["result"]
            return requestBlock(blockHash, useProductionNode)

def checkConsensus(height):
    response = requestBlock(height)
    if "error" in response and response["error"] != None:
        return False
    response8 = requestBlock(height, useProductionNode = True)
    if "error" in response8 and response8["error"] != None:
        return False
    return response["result"]["hash"] == response8["result"]["hash"]


# JSON-RPC pass through to node

@jsonrpc.method('getwork(data=str)')
def getWork(data = None):
    response = requestJsonRPC("getwork", [] if data == None else [data], useProductionNode = True)
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]


# API based on node JSON-RPC

@app.route('/api/searchrawtransactions/<address>')
def searchRawTransactions(address):
    response = requestJsonRPC("searchrawtransactions", [address, 1, 0, 1000])
    return jsonify(response), 200

@app.route('/api/getaddressbalance/<address>')
def getAddressBalance(address):
    response = requestJsonRPC("getaddressbalance", [ json.dumps({"addresses": [address]}) ] )
    return jsonify(response), 200

@app.route('/api/getbestblock/')
def getBestBlock():
    return jsonify(requestBestBlock()), 200

@app.route('/api/getblock/<heightOrAddress>')
def getBlock(heightOrAddress):
    return jsonify(requestBlock(heightOrAddress)), 200

@app.route('/api/getrawtransaction/<txid>')
def getRawTransaction(txid):
    response = requestJsonRPC("getrawtransaction", [txid, True])
    return jsonify(response), 200

@app.route('/api/getblockchaininfo/')
def getBlockchainInfo():
    response = requestJsonRPC("getblockchaininfo", [])
    return jsonify(response), 200

@app.route('/api/getpeerinfo/')
def getPeerInfo():
    response = requestJsonRPC("getpeerinfo", [])
    return jsonify(response), 200

@app.route('/api/getinfo/')
def getBlockchainInfo8():
    response = requestJsonRPC("getinfo", [], useProductionNode = True)
    return jsonify(response), 200

@app.route('/api/getwork/')
def getMinerWork8():
    response = requestJsonRPC("getwork", [], useProductionNode = True)
    if "error" in response and response["error"] != None:
        return response
    import codecs, struct
    # https://en.bitcoin.it/wiki/Getwork
    data = codecs.decode(response["result"]["data"], 'hex_codec')
    header = struct.pack('<20I', *struct.unpack('>20I', data[:80]))
    (version, prev, merkle, epoch, bits, nonce) = struct.unpack('<I32s32s3I', header)
    response["result"]["header"] = codecs.encode(header, 'hex_codec').decode('utf-8')
    response["result"]["version"] = version
    response["result"]["prev"] = codecs.encode(prev[::-1], 'hex_codec').decode('utf-8')
    response["result"]["merkle"] = codecs.encode(merkle[::-1], 'hex_codec').decode('utf-8')
    response["result"]["epoch"] = epoch
    response["result"]["bits"] = "%02x.%06x" % ((bits >> 24), (bits & 0xffffff))
    response["result"]["difficulty"] = bits / (float)(1<<24)
    response["result"]["nonce"] = nonce
    return jsonify(response), 200

@app.route('/api/getbestblock8/')
def getBestBlock8():
    return jsonify(requestBestBlock(useProductionNode = True)), 200

@app.route('/api/consensus/')
def getCommonAncestor():
    response = requestBestBlock()
    if "error" in response and response["error"] != None:
        return response
    response8 = requestBestBlock(useProductionNode = True)
    if "error" in response8 and response8["error"] != None:
        return response
    upperHeight = min(response["result"]["height"], response8["result"]["height"])
    lowerHeight = 0
    if not checkConsensus(upperHeight):
        while lowerHeight < upperHeight:
            midHeight = max(lowerHeight + 1, (lowerHeight + upperHeight) // 2)
            if checkConsensus(midHeight):
                lowerHeight = midHeight
            else:
                upperHeight = midHeight - 1

    return jsonify(requestBlock(upperHeight)), 200

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

@app.route("/address/<address>")
def address(address):
    return render_template("address.html", **locals())

# include this for local dev
if __name__ == '__main__':
    app.run()
