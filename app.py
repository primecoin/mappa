from flask import Flask, jsonify, render_template

app = Flask(__name__, instance_relative_config=True)
try:
    app.config.from_pyfile('config.py')
except FileNotFoundError:
    pass

# JSON-RPC pass through to node

from flask_jsonrpc import JSONRPC
jsonrpc = JSONRPC(app, '/api/jsonrpc', enable_web_browsable_api=True)
import apis.jsonrpc.mining

# Blockchain functions

from apis.jsonrpc.client import requestJsonRPC

def requestBlock(heightOrAddress, useProductionNode = False):
    try:
        height = int(heightOrAddress)
        isHeight = True
    except:
        blockHash = heightOrAddress
        isHeight = False
    if isHeight:
        response = requestJsonRPC(app.config["RPC8"] if useProductionNode else app.config["RPC"], "getblockhash", [height])
        if "error" in response and response["error"] != None:
            return response
        blockHash = response["result"]

    response = requestJsonRPC(app.config["RPC8"] if useProductionNode else app.config["RPC"], "getblock", [blockHash] if useProductionNode else [blockHash, 2])
    if "error" in response and response["error"] != None:
        return response
    chain = response["result"]["primechain"]
    origin = int(response["result"]["primeorigin"], 10)
    chainType = chain[:3]
    chainLength = int(chain[3:5], 16)
    primes = []
    delta = -1 if chainType == '1CC' else 1
    for i in range(chainLength):
        delta *= (-1) if chainType == 'TWN' else 1
        primes.append(str(origin + delta))
        origin *= 1 if chainType == 'TWN' and delta == -1 else 2
    response["result"]["primes"] = primes
    return response

def requestBestBlock(useProductionNode = False):
    if useProductionNode:
        response = requestJsonRPC(app.config["RPC8"], "getinfo", [])
        if "error" in response and response["error"] != None:
            return response
        else:
            blockHeight = response["result"]["blocks"]
            return requestBlock(blockHeight, useProductionNode)
    else:
        response = requestJsonRPC(app.config["RPC"], "getbestblockhash", [])
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


# API based on node JSON-RPC

@app.route('/api/searchrawtransactions/<address>/<int:skip>')
def searchRawTransactions(address, skip):
    response = requestJsonRPC(app.config["RPC"], "searchrawtransactions", [address, 1, skip])
    while len(response["result"]) > 0 and len(jsonify(response).get_data()) > 5000000:
        # work around AWS 6MB body size limit
        transactions = response["result"]
        half = transactions[:len(transactions)//2]
        response["result"] = half
    return jsonify(response), 200

@app.route('/api/getaddressbalance/<address>')
def getAddressBalance(address):
    from json import dumps
    response = requestJsonRPC(app.config["RPC"], "getaddressbalance", [ dumps({"addresses": [address]}) ] )
    return jsonify(response), 200

@app.route('/api/getbestblock/')
def getBestBlock():
    return jsonify(requestBestBlock()), 200

@app.route('/api/getblock/<heightOrAddress>')
def getBlock(heightOrAddress):
    return jsonify(requestBlock(heightOrAddress)), 200

@app.route('/api/syncblock/')
def syncBlock():
    response = requestJsonRPC(app.config["RPC"], "getblockchaininfo", [])
    if "error" in response and response["error"] != None:
        return response
    else:
        blockHeight = response["result"]["blocks"]
        blockHeight = (blockHeight // 2016) * 2016
        return jsonify(requestBlock(blockHeight))

@app.route('/api/getrawtransaction/<txid>')
def getRawTransaction(txid):
    response = requestJsonRPC(app.config["RPC"], "getrawtransaction", [txid, True])
    return jsonify(response), 200

@app.route('/api/getblockchaininfo/')
def getBlockchainInfo():
    response = requestJsonRPC(app.config["RPC"], "getblockchaininfo", [])
    return jsonify(response), 200

@app.route('/api/availability/')
def getAvailability():
    try:
        # Get current blockchain information
        blockchain_response = requestJsonRPC(app.config["RPC"], "getblockchaininfo", [])
        if "error" in blockchain_response and blockchain_response["error"] != None:
            return jsonify(blockchain_response), 200

        current_height = blockchain_response["result"]["headers"]

        # Define time periods and corresponding block counts
        periods = [
            {"name": "8h", "hours": 8, "blocks": 480},      # 8 hours = 480 blocks
            {"name": "1d", "hours": 24, "blocks": 1440},    # 1 day = 1440 blocks
            {"name": "1w", "hours": 168, "blocks": 10080},  # 1 week = 10080 blocks
            {"name": "1y", "hours": 8760, "blocks": 525600} # 1 year = 525600 blocks
        ]

        # Get current block information to get current time
        current_block_response = requestBlock(str(current_height))
        if "error" in current_block_response and current_block_response["error"] != None:
            return jsonify(current_block_response), 200

        current_time = current_block_response["result"]["time"]
        results = []

        for period in periods:
            # Calculate target height for this period
            target_height = current_height - period["blocks"]

            # Get block information from the target height
            past_block_response = requestBlock(str(target_height))
            if "error" in past_block_response and past_block_response["error"] != None:
                continue

            past_time = past_block_response["result"]["time"]

            # Calculate actual hours elapsed
            actual_hours = (current_time - past_time) / 3600

            # Calculate health percentage
            if actual_hours <= period["hours"]:
                availability = 100.0
            else:
                availability = (period["hours"] / actual_hours) * 100

            results.append({
                "period": period["name"],
                "actual_hours": round(actual_hours, 2),
                "availability": round(availability, 2)
            })

        return jsonify({"result": results}), 200

    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@app.route('/api/getpeerinfo/')
def getPeerInfo():
    response = requestJsonRPC(app.config["RPC"], "getpeerinfo", [])
    return jsonify(response), 200

@app.route('/api/getinfo/')
def getBlockchainInfo8():
    response = requestJsonRPC(app.config["RPC8"], "getinfo", [])
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


# Restful API

from apis.rest import api
api.init_app(app)


# include this for local dev
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--rpc")
    parser.add_argument("--rpc8")
    parser.add_argument("--host")
    args = vars(parser.parse_args())
    if args["rpc"]:
        app.config["RPC"] = args["rpc"]
    if args["rpc8"]:
        app.config["RPC8"] = args["rpc8"]
    app.run(host=(args["host"] if "host" in args else "127.0.0.1"))
