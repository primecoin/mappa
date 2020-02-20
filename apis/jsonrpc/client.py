import json, requests

# JSON-RPC 1.0 client access to node api
def requestJsonRPC(url, method, params):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "1.0",
        "id": "mappa",
    }
    return requests.post(url, data=json.dumps(payload), headers=headers).json()
