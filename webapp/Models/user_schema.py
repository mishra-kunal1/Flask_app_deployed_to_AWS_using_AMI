from flask_sqlalchemy import SQLAlchemy
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from flask_marshmallow import Marshmallow
import pytz
db = SQLAlchemy()
ma = Marshmallow()



class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(128),nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    account_created = db.Column(db.DateTime, default = datetime.now(pytz.timezone("America/New_York")))
    account_updated = db.Column(db.DateTime, default = datetime.now(pytz.timezone("America/New_York")))
    email_verified = db.Column(db.Boolean, default=False,nullable=False)
    

    def _repr_(self):
        return self.id
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name","username","account_created","account_updated","email_verified")


class Document(db.Model):
    doc_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId=db.Column(db.String(150),nullable=False)
    name = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    s3_bucket_path = db.Column(db.String(100), nullable=False)

class DocumentSchema(ma.Schema):
    class Meta:
        fields = ('doc_id','userId', 'name', 's3_bucket_path','date_created')

