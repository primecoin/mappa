from flask_restplus import Namespace, Resource
from app import node8Url, node16Url
from ..jsonrpc.client import requestJsonRPC

api = Namespace(name='Blockchain', path='')

@api.route("/getdifficulty")
class GetDifficulty(Resource):
    def get(self):
        return requestJsonRPC(node8Url, "getdifficulty", [])

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
            response = requestJsonRPC(node16Url, "getblockhash", [height])
            if "error" in response and response["error"] != None:
                return response
            blockHash = response["result"]
        # First get raw block hex
        response = requestJsonRPC(node16Url, "getblock", [blockHash, 0])
        if "error" in response and response["error"] != None:
            return response
        blockRawHex = response["result"]
        headerRawHex = blockRawHex[:160]
        import codecs, struct, hashlib
        header = codecs.decode(headerRawHex, 'hex_codec')
        headerHash = hashlib.sha256(hashlib.sha256(header).digest()).digest()
        # Next get deserialized block
        response = requestJsonRPC(node16Url, "getblock", [blockHash, 2])
        if "error" in response and response["error"] != None:
            return response
        # Next derive primes in primechain
        chain = response["result"]["primechain"]
        origin = int(response["result"]["primeorigin"], 10)
        chainType = chain[:3]
        chainLength = int(chain[3:5], 16)
        primes = []
        delta = -1 if chainType == '1CC' else 1
        for i in range(chainLength):
            delta *= (-1) if chainType == 'TWN' else 1
            primes.append(str(origin + delta))
            origin *= 2 if chainType != 'TWN' or delta == 1 else 1
        response["result"]["primes"] = primes
        # Fill in serialized block and header
        response["result"]["hex"] = blockRawHex
        response["result"]["header"] = codecs.encode(header, 'hex_codec').decode('utf-8')
        response["result"]["headerHash"] = codecs.encode(headerHash[::-1], 'hex_codec').decode('utf-8')
        # Fill in multiplier
        multiplier = origin // int(response["result"]["headerHash"], 16)
        remainder = origin % int(response["result"]["headerHash"], 16)
        response["result"]["multiplierHex"] = hex(multiplier)[2:]
        response["result"]["multiplierValid"] = (remainder == 0)
        return response
