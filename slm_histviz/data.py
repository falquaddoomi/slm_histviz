from slm_histviz import app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.dialects.postgresql.base import INET

import os
filepath = os.path.dirname(os.path.realpath(__file__))

app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///%s/database.db' % filepath,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_BINDS={
        'connect_log': 'postgresql:///slm_distraction'
    }
)

db = SQLAlchemy(app)


# class User(flask_login.UserMixin):
#     email = db.Column(db.String, primary_key=True)
#     authenticated = db.Column(db.Boolean, default=False)
#     credentials = db.Column(db.String, nullable=True)
#
#     def is_authenticated(self):
#         return self.authenticated
#
#     def get_id(self):
#         return unicode(self.email)
#
#     def __init__(self, email):
#         self.email = email
#
#     def __repr__(self):
#         return '<User %r>' % self.email
#
#     def __unicode__(self):
#         return self.email

class AccessLog(db.Model):
    __tablename__ = 'access_log'
    __bind_key__ = "connect_log"

    id = db.Column(db.Integer, primary_key=True, server_default=text("nextval('access_log_id_seq'::regclass)"))
    created_at = db.Column(db.DateTime, server_default=text("timezone('utc'::text, now())"))
    username = db.Column(db.String)
    hostname = db.Column(db.String)
    protocol = db.Column(db.String)

    def __str__(self):
        return "%s accessed %s (prot: %s) at %s" % (self.username, self.hostname, self.protocol, self.created_at)

    def __repr__(self):
        return "AccessLog for %s to %s" % (self.username, self.hostname)


class ConnectLog(db.Model):
    __tablename__ = 'connect_log'
    __bind_key__ = "connect_log"

    id = db.Column(db.Integer, primary_key=True, server_default=text("nextval('connect_log_id_seq'::regclass)"))
    created_at = db.Column(db.DateTime, server_default=text("timezone('utc'::text, now())"))
    status = db.Column(db.String(30))
    interface = db.Column(db.String(30))
    username = db.Column(db.String)
    local_ip = db.Column(INET)
    remote_ip = db.Column(INET)

    def __str__(self):
        return "%s (%s :: %s) %s on %s" % (self.username, self.local_ip, self.interface, self.status, self.created_at)

    def __repr__(self):
        return "ConnectLog (%s) for %s at %s" % (self.status, self.username, self.local_ip)


# init the db if it hasn't already been init'd
db.create_all()
