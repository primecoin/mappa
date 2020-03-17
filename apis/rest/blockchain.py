from flask_restplus import Namespace, Resource
from app import node8Url
from ..jsonrpc.client import requestJsonRPC

api = Namespace(name='Blockchain', path='')

@api.route("/getdifficulty")
class GetDifficulty(Resource):
    def get(self):
        return requestJsonRPC(node8Url, "getdifficulty", [])
