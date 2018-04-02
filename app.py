from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from resources.upload_image import ImageFile
from security import authenticate, identity
from resources.user import UserRegister


app = Flask(__name__)
app.secret_key='some key'
api = Api(app)

# JWT creates a new endpoint /auth
jwt = JWT(app, authenticate, identity)

api.add_resource(ImageFile, '/image_file')
api.add_resource(UserRegister, '/register')

# @app.before_first_request
# def create_tables():
#     db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
