import logging
import datetime as dt
import json

from flask import request
from flask_restplus import Resource
from restfulPy.api.restplus import api
from restfulPy.api.ProductionData.parsers import prodPerFuelTypeArgument

from restfulPy.api.ProductionData.getDataInMongo import getProdByFuelTypeInMongo
from restfulPy.api.ProductionData.RTE_API.production.getProd import saveProdByFuelType

log = logging.getLogger(__name__)

ns = api.namespace('ProductionData/prodPerFuelType', description='Operations related to fuel type prod')


@ns.route('/3test')
class CategoryCollection(Resource):

    def get(self):
        return 3

@ns.route('/GetProduction')
class GetProduction(Resource):

    @api.expect(prodPerFuelTypeArgument, validate=True)
    def get(self):
        args = prodPerFuelTypeArgument.parse_args(request)
        stFlowdate = args.get('flowdate')
        fd=dt.datetime.strptime(stFlowdate,"%Y%m%d")
        o=getProdByFuelTypeInMongo(fd.year,fd.month,fd.day)
        return o


@ns.route('/SaveProduction')
class SaveProduction(Resource):
    @api.expect(prodPerFuelTypeArgument, validate=True)
    def get(self):
        args = prodPerFuelTypeArgument.parse_args(request)
        stFlowdate = args.get('flowdate')
        fd = dt.datetime.strptime(stFlowdate, "%Y%m%d")
        o = saveProdByFuelType(fd.year, fd.month, fd.day)
        return json.dumps(o)
