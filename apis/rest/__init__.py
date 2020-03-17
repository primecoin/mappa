from flask_restplus import Api

from .blockchain import api as blockchainApi
from .mining import api as miningApi

api = Api(
    title='REST API',
    version='1.0',
    doc='/api/rest/'
)

api.add_namespace(blockchainApi, path='/api/rest/blockchain')
api.add_namespace(miningApi, path='/api/rest/mining')
