from flask_httpauth import HTTPBasicAuth
from Models.user_schema import User
import bcrypt
from functools import wraps
from flask import request,jsonify
import json
auth=HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = (User.query.filter_by(username=username).first())
    print('user',user)
    if(user is not None):
       
        user=user.as_dict()

        if(user and  bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))):
            return user

        