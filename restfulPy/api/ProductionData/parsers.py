from flask_restplus import reqparse

prodPerFuelTypeArgument = reqparse.RequestParser()
prodPerFuelTypeArgument.add_argument('flowdate', type=str, required=False, default="20170101")

