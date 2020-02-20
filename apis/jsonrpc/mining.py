from app import jsonrpc, node8Url
from .client import requestJsonRPC

@jsonrpc.method('getwork(data=str)')
def getWork(data = None):
    response = requestJsonRPC(node8Url, "getwork", [] if data == None else [data])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]

@jsonrpc.method('getblocktemplate(capabilities=dict)')
def getBlockTemplate(capabilities = None):
    response = requestJsonRPC(node8Url, "getblocktemplate", [capabilities] if capabilities else [])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]

@jsonrpc.method('submitblock(hexData=str, options=dict)')
def submitBlock(hexData, options = {}):
    response = requestJsonRPC(node8Url, "submitblock", [hexData, options])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]
