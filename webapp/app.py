from flask import Flask
from flask_restful import Api
from Models.user_schema import db, User, ma, UserSchema
from Resources.user_resource import UserCatalogue, Healthz, UserProfile, DocumentCatalogue, AllDocs, DocumentOps, UserVerification
from Resources.user_resource import Healthz
import credentials


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_kunalmishra:abc123@localhost/cloud_db'
my_string = "postgresql://"+credentials.username+":"+credentials.password + \
    "@"+credentials.host+':'+credentials.port+'/'+credentials.db_name
app.config['SQLALCHEMY_DATABASE_URI'] = my_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
ma.init_app(app)
api = Api(app)

api.add_resource(UserCatalogue, '/v2/account')
api.add_resource(UserProfile, '/v2/account/<string:id>')
api.add_resource(Healthz, '/healthz')
api.add_resource(AllDocs, '/v1/all_documents')
api.add_resource(DocumentCatalogue, '/v1/documents')
api.add_resource(DocumentOps, '/v1/documents/<string:id>')
api.add_resource(UserVerification, '/verify')

if __name__ == "main":
    app.run(port=5000, debug=True, host="0.0.0.0")
