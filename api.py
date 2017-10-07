from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

@app.route('/testracine')
def racine():
    return "Le chemin de 'racine' est : " + request.path

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)

#tuto for swagger
#http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/