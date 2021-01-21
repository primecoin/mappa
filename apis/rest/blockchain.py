from flask import current_app as app
from flask_restplus import Namespace, Resource
from ..jsonrpc.client import requestJsonRPC

api = Namespace(name='Blockchain', path='')

@api.route("/getdifficulty")
class GetDifficulty(Resource):
    def get(self):
        return requestJsonRPC(app.config["RPC8"], "getdifficulty", [])

@api.route("/getblock/<string:heightOrHash>")
class GetBlock(Resource):
    def get(self, heightOrHash):
        try:
            height = int(heightOrHash)
            isHeight = True
        except:
            blockHash = heightOrHash
            isHeight = False
        if isHeight:
            response = requestJsonRPC(app.config["RPC"], "getblockhash", [height])
            if "error" in response and response["error"] != None:
                return response
            blockHash = response["result"]
        # First get raw block hex
        response = requestJsonRPC(app.config["RPC"], "getblock", [blockHash, 0])
        if "error" in response and response["error"] != None:
            return response
        import codecs, hashlib
        blockRawHex = response["result"]
        blockBytes = codecs.decode(blockRawHex, 'hex_codec')
        headerBytes = blockBytes[:80]
        headerHash = hashlib.sha256(hashlib.sha256(headerBytes).digest()).digest()
        # Next get deserialized block
        response = requestJsonRPC(app.config["RPC"], "getblock", [blockHash, 2])
        if "error" in response and response["error"] != None:
            return response
        # Fill in serialized block and header
        response["result"]["hex"] = blockRawHex
        response["result"]["header"] = codecs.encode(headerBytes, 'hex_codec').decode('utf-8')
        response["result"]["headerHash"] = codecs.encode(headerHash[::-1], 'hex_codec').decode('utf-8')
        # Fill in multiplier
        multiplierLength = blockBytes[80]
        multiplierBytes = blockBytes[81:81+multiplierLength]
        multiplierHex = codecs.encode(multiplierBytes[::-1], 'hex_codec').decode('utf-8')
        response["result"]["multiplierHex"] = multiplierHex
        origin = int(response["result"]["primeorigin"], 10)
        if origin != int(multiplierHex, 16) * int(response["result"]["headerHash"], 16):
            response["error"] = "Invalid proof-of-work: origin mismatch"
        blockHash = hashlib.sha256(hashlib.sha256(blockBytes[:81+multiplierLength]).digest()).digest()
        if response["result"]["hash"] != codecs.encode(blockHash[::-1], 'hex_codec').decode('utf-8'):
            response["error"] = "Block hash mismatch"
        # Derive primes in primechain
        chain = response["result"]["primechain"]
        chainType = chain[:3]
        chainLength = int(chain[3:5], 16)
        primes = []
        delta = -1 if chainType == '1CC' else 1
        for i in range(chainLength):
            delta *= (-1) if chainType == 'TWN' else 1
            primes.append(str(origin + delta))
            origin *= 2 if chainType != 'TWN' or delta == 1 else 1
        response["result"]["primes"] = primes
        return response
