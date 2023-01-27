from Models.user_schema import db, User, ma, UserSchema, DocumentSchema, Document
from security import auth
from flask import request, make_response
import bcrypt
from flask_api import status
from flask_restful import Resource
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime
import pytz
import credentials
from werkzeug.utils import secure_filename
from boto3.dynamodb.conditions import Key, Attr
# logging info
import watchtower
import logging
import statsd
from datetime import datetime, timedelta
from boto3 import resource

import uuid
import json


dynamodb = resource(
    'dynamodb', region_name=credentials.aws_region)

start = datetime.utcnow()
logging.basicConfig(
    filename='csye6225.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='w'
)


client_statsd = statsd.StatsClient('localhost', 8125)

# bucket info
bucket_name = credentials.s3bucketname
s3_path = "s3://"+credentials.s3bucketname+"/"
user_schema = UserSchema()
users_schema = UserSchema(many=True)

document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)


class UserCatalogue(Resource):

    def get(self):
        users = User.query.all()
        logging.info('Getting all user ')
        client_statsd.incr('getalluser.api')
        return users_schema.dump(users)

    def post(self):
        logging.info('Adding a user ')
        client_statsd.incr('adduser.api')
        try:

            first_name = request.json['first_name']
            last_name = request.json['last_name']
            password_text = (request.json['password']).encode('utf-8')
            password_hash = bcrypt.hashpw(password_text, bcrypt.gensalt())
            password = password_hash.decode('utf-8')
            username = request.json['username']
            logging.info('Recieved data from post request ')
            all_users = User.query.all()
            for user in all_users:
                if (user.username == username):
                    return "Record already exists", status.HTTP_400_BAD_REQUEST

            logging.info('Creating new user')

            new_user = User(first_name=first_name, last_name=last_name,
                            username=username, password=password)
            logging.info('New user created in database')
            db.session.add(new_user)
            db.session.commit()

            logging.info('Inserting data in dynamodb')
            table = dynamodb.Table('csye-6225')
            token = str(uuid.uuid4())
            ttl = int(credentials.TimeToLive)*60
            table.put_item(
                Item={
                    'Email': username,
                    'TokenId': token,
                    'TTL': (datetime.now()+timedelta(seconds=ttl)).strftime("%Y/%m/%d %H:%M:%S"),
                    "Message_type": "Verification"
                }
            )
            logging.info('SNS service')
            message = {"Username": username,
                       "Subject": token,
                       "Message_type": "Verification"
                       }
            sns_client = boto3.client(
                'sns', region_name=credentials.aws_region)
            response = sns_client.publish(
                TopicArn=credentials.topic_arn,
                Message=json.dumps({'default': json.dumps(message)}),
                MessageStructure='json'
            )
            return user_schema.dump(new_user), 201
        except:
            return {"message": "bad request"}, 400


class AllDocs(Resource):
    def get(self):
        documents = Document.query.all()
        logging.info('Get all docs')
        client_statsd.incr('getalldocs.api')
        return documents_schema.dump(documents)


class DocumentCatalogue(Resource):

    @auth.login_required
    def get(self):
        logging.info('Getting user document')
        client_statsd.incr('getuserdocs.api')
        if ((auth.current_user()['email_verified']) == False):
            return {"message": "Verification Not Completed"}, 403
        try:

            docs = (Document.query.filter_by(
                userId=str(auth.current_user()['id'])))

            return documents_schema.dump(docs)
        except:
            return {"message": "Not authorized"}, 403

    @auth.login_required
    def post(self):
        logging.info('Adding a doc')
        client_statsd.incr('postdoc.api')
        if ((auth.current_user()['email_verified']) == False):
            return {"message": "Verification Not Completed"}, 403
        try:
            file = request.files['file']
            object_name = secure_filename(file.filename)
            client = boto3.client("s3")
            try:
                client.upload_fileobj(file, bucket_name, object_name, ExtraArgs={
                                      "ACL": "public-read"})
                s3_path_file = s3_path+object_name
                new_document = Document(name=object_name, userId=str(
                    auth.current_user()['id']), s3_bucket_path=s3_path_file)
                db.session.add(new_document)
                db.session.commit()

                return document_schema.dump(new_document), 201
            except:
                print(ClientError)
                return {"message": "Bad request"}, 400
        except:
            return {"message": "Bad request"}, 400


class UserProfile(Resource):

    @auth.login_required
    def get(self, id):
        logging.info('Getting user details')
        client_statsd.incr('userget.api')
        if (str(auth.current_user()['id']) != id):

            return {"message": "Not authorized"}, 403
        if (str(auth.current_user()['id']) == id and (auth.current_user()['email_verified']) == False):
            return {"message": "Verification Not Completed"}, 403

        try:

            result = User.query.get(id)
            if (result):
                return user_schema.dump(result)
            else:
                return {"message": "Incorrect user id"}, 403
        except:
            return {"message": "Incorrect user id"}, 403

    @auth.login_required
    def put(self, id):

        if (str(auth.current_user()['id']) != id):

            return {"message": "Not authorized"}, 403
        if (str(auth.current_user()['id']) == id and (auth.current_user()['email_verified']) == False):
            return {"message": "Verification Not Completed"}, 403

        logging.info('Updating user details')
        client_statsd.incr('userupdate.api')

        result = User.query.get_or_404(id)

        data_update = request.get_json()
        required_keys = ['first_name', 'last_name', 'password']

        if "username" in data_update.keys():
            return "Username can not be updated", status.HTTP_403_FORBIDDEN
        try:
            if (len(data_update) == 3):
                result.first_name = request.json['first_name']
                result.last_name = request.json['last_name']

                password_text = (request.json['password']).encode('utf-8')
                password_hash = bcrypt.hashpw(password_text, bcrypt.gensalt())
                password = password_hash.decode('utf-8')

                result.password = password

                result.account_updated = datetime.now(
                    pytz.timezone("America/New_York"))
                db.session.commit()
                return make_response("Updated Successfully", 204)
            else:
                return "Record can not be updated", status.HTTP_400_BAD_REQUEST

        except:
            return "Record can not be updated", status.HTTP_400_BAD_REQUEST


class DocumentOps(Resource):
    @auth.login_required
    def get(self, id):
        if ((auth.current_user()['email_verified']) == False):
            return {"message": "Verification Not Completed"}, 403
        logging.info('Retrieving document')
        client_statsd.incr('documentget.api')
        try:
            result = Document.query.get(id)
            if (result and result.userId != str(auth.current_user()['id'])):
                return {"message": "Not authorized"}, 403

            if (result):

                return document_schema.dump(result)
            else:
                return {"message": "Doc not found"}, 403
        except:
            return {"message": "Doc not found"}, 403

    @auth.login_required
    def delete(self, id):
        if ((auth.current_user()['email_verified']) == False):
            return {"message": "Verification Not Completed"}, 403
        logging.info('Deleting document')
        client_statsd.incr('documentdelete.api')
        try:
            result = Document.query.get(id)
            if (result and result.userId != str(auth.current_user()['id'])):
                return {"message": "Not authorized"}, 404

            if (result):
                try:
                    client = boto3.client("s3")
                    client.delete_object(Bucket=bucket_name, Key=result.name)
                    db.session.delete(result)
                    db.session.commit()

                    return {"message": "Delete complete"}, 204
                except:
                    return {"message": "Doc not found"}, 404
            else:
                return {"message": "Doc not found"}, 404
        except:
            return {"message": "Doc not found"}, 404


class Healthz(Resource):
    def get(self):
        logging.info('Checking health')
        client_statsd.incr('healthz.api')
        client_statsd.timing('healthz.timer', datetime.utcnow()-start)
        return {"message": "200 OK"}


class UserVerification(Resource):
    def get(self):
        try:
            email = request.args.get('email')
            logging.info(email)
            token = request.args.get('token')
            logging.info(token)
            logging.info('Verifying the user')
            try:
                table = dynamodb.Table('csye-6225')
                response = table.query(
                    KeyConditionExpression=Key('Email').eq(email))
                logging.info(response)
                if (response['Count'] == 1):
                    if (response['Items'][0]['TokenId'] == token and response['Items'][0]['Email'] == email):
                        if (datetime.now() < (datetime.strptime(response['Items'][0]['TTL'], "%Y/%m/%d %H:%M:%S"))):
                            result = User.query.filter_by(username=email).first()
                            if(result.email_verified == False):
                                result.email_verified = True
                                db.session.commit()
                                return {"message": "Verification done."}
                            else:
                                return {"message": "user already verified "}, 201
                        else:
                            return {"message": "Token expired "}, 400
                    else:
                        return {"message": "Token and email do not match"}, 400
                else:
                    return {"message": "Invalid link"}, 400
            except:
                return {"message": "Unable to access Dynamo DB"}
        except:
            return {"message": "Bad Request"}, 400
