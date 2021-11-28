from app import jsonrpc
from flask import current_app as app, request
from json import dumps
from struct import pack, unpack
from sys import stderr
from .client import requestJsonRPC

@jsonrpc.method('getdifficulty()')
def getDifficulty():
    response = requestJsonRPC(app.config["RPC"], "getdifficulty", [])
    if "error" in response and response["error"] is not None:
        raise ValueError(response["error"])
    else:
        return response["result"]

@jsonrpc.method('getwork(data=str)')
def getWork(data = None):
    if not request.get_json():
        raise ValueError(f'Requires JSON RPC, mime type is {request.mimetype}, should be application/json')
    minerAddress = request.get_json().get("address", None)
    response = requestJsonRPC(app.config["RPC"], "getwork", [] if data == None else [data])
    if "error" in response and response["error"] is not None:
        raise ValueError(response["error"])
    else: # node responded with success
        if data and minerAddress: # getwork submit with miner address
            dataBytes = bytes.fromhex(data)
            header = pack('<20I', *unpack('!20I', dataBytes[:80]))
            (version, prev, merkle, epoch, bits, nonce) = unpack('<I32s32s3I', header)
            mined = (1 << 48) * 999 // (bits * bits) + 1
            txResponse = requestJsonRPC(app.config["RPC"], "sendtoaddress", [minerAddress, mined])
            if "error" in txResponse and txResponse["error"] is not None:
                raise ValueError(txResponse["error"])
        response["result"]["original"] = response
        return response["result"]

@jsonrpc.method('getblocktemplate(capabilities=dict)')
def getBlockTemplate(capabilities = None):
    response = requestJsonRPC(app.config["RPC"], "getblocktemplate", [capabilities] if capabilities else [])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]

@jsonrpc.method('submitblock(hexData=str, options=dict)')
def submitBlock(hexData, options = {}):
    response = requestJsonRPC(app.config["RPC"], "submitblock", [hexData, options])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        response["result"]["original"] = response
        return response["result"]
