from flask_restplus import Namespace, Resource
from app import node8Url
from ..jsonrpc.client import requestJsonRPC

api = Namespace(name='Mining', path='')

@api.route("/getwork")
class MinerGetWork(Resource):
    def get(self):
        response = requestJsonRPC(node8Url, "getwork", [])
        if "error" in response and response["error"] != None:
            return response
        import codecs, struct, hashlib
        # https://en.bitcoin.it/wiki/Getwork
        # (Quote) "data: Pre-processed SHA-2 input chunks, in little-endian order,
        #          as a hexadecimal-encoded string.
        #          Because getwork provides the data in little endian, and SHA256 works
        #          in big endian, for every 32-bit chunk you need to swap the byte order"
        # NOTE: the above quote of bitcoin wiki is wrong and very misleading!
        # data is NOT little-endian, as data is each 4-byte reversed from native format!
        # data should not be referred to as big-endian either. As the prev and merkle
        # uint256's inside data are not big-endian, it would be confusing to call it big-endian.
        # Also, double sha256 header hash is performed on NATIVE header which IS LITTLE-ENDIAN!
        data = codecs.decode(response["result"]["data"], 'hex_codec')
        header = struct.pack('<20I', *struct.unpack('!20I', data[:80]))
        (version, prev, merkle, epoch, bits, nonce) = struct.unpack('<I32s32s3I', header)
        headerHash = hashlib.sha256(hashlib.sha256(header).digest()).digest()
        response["result"]["header"] = codecs.encode(header, 'hex_codec').decode('utf-8')
        response["result"]["headerHash"] = codecs.encode(headerHash[::-1], 'hex_codec').decode('utf-8')
        response["result"]["version"] = version
        response["result"]["prev"] = codecs.encode(prev[::-1], 'hex_codec').decode('utf-8')
        response["result"]["merkle"] = codecs.encode(merkle[::-1], 'hex_codec').decode('utf-8')
        response["result"]["epoch"] = epoch
        response["result"]["bits"] = "%02x.%06x" % ((bits >> 24), (bits & 0xffffff))
        response["result"]["difficulty"] = bits / (float)(1<<24)
        response["result"]["nonce"] = nonce
        return response
    def put(self):
        import codecs, struct
        from flask import abort, request
        if not request.is_json:
            abort(400, 'JSON submission with matching MIME type expected.')
        try:
            submit = request.get_json()
        except Exception as e:
            abort(400, str(e))
        if 'data' not in submit or 'multiplier' not in submit:
            abort(400, 'Hex string fields data and multiplier are expected.')
        try:
            multiplier = codecs.decode(submit["multiplier"].zfill(64), 'hex_codec')[::-1]
            data = codecs.decode(submit["data"], 'hex_codec')
        except Exception as e:
            abort(400, str(e))
        native = struct.pack('<32I', *struct.unpack('!32I', data))
        (header, mid, tail) = struct.unpack('<80s32s16s', native)
        native = struct.pack('<80s32s16s', header, multiplier, tail)
        data = struct.pack('!32I', *struct.unpack('<32I', native))
        response = requestJsonRPC(node8Url, "getwork", [codecs.encode(data, 'hex_codec').decode('utf-8')])
        return response

