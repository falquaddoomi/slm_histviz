from slm_histviz import app

from flask_sqlalchemy import SQLAlchemy
from flask.ext import login as flask_login
from sqlalchemy import text
from sqlalchemy.dialects.postgresql.base import INET

import datetime
import dateutil.relativedelta

import os
filepath = os.path.dirname(os.path.realpath(__file__))

app.config.update(
    # SQLALCHEMY_DATABASE_URI='sqlite:///%s/database.db' % filepath,
    SQLALCHEMY_DATABASE_URI="postgresql:///slm_distraction",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    # SQLALCHEMY_BINDS={
    #     'connect_log': 'postgresql:///slm_distraction'
    # }
)

db = SQLAlchemy(app)


class User(db.Model, flask_login.UserMixin):
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    role = db.Column(db.String, default="user")

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return unicode(self.username)

    def get_urole(self):
        return unicode(self.role)

    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def __unicode__(self):
        return self.username


class AccessLog(db.Model):
    __tablename__ = 'access_log'
    # __bind_key__ = "connect_log"

    id = db.Column(db.Integer, primary_key=True, server_default=text("nextval('access_log_id_seq'::regclass)"))

    username = db.Column(db.String, db.ForeignKey('user.username'))
    # user = db.relationship('User', backref=db.backref('accesses', lazy='dynamic'))

    created_at = db.Column(db.DateTime, server_default=text("timezone('utc'::text, now())"))

    hostname = db.Column(db.String)
    protocol = db.Column(db.String)

    def __str__(self):
        return "%s accessed %s (prot: %s) at %s" % (self.username, self.hostname, self.protocol, self.created_at)

    def __repr__(self):
        return "AccessLog for %s to %s" % (self.username, self.hostname)


class ConnectLog(db.Model):
    __tablename__ = 'connect_log'
    # __bind_key__ = "connect_log"

    id = db.Column(db.Integer, primary_key=True, server_default=text("nextval('connect_log_id_seq'::regclass)"))

    username = db.Column(db.String, db.ForeignKey('user.username'))
    # user = db.relationship('User', backref=db.backref('connects', lazy='dynamic'))

    created_at = db.Column(db.DateTime, server_default=text("timezone('utc'::text, now())"))

    status = db.Column(db.String(30))
    interface = db.Column(db.String(30))
    local_ip = db.Column(INET)
    remote_ip = db.Column(INET)


    def __str__(self):
        return "%s (%s :: %s) %s on %s" % (self.username, self.local_ip, self.interface, self.status, self.created_at)

    def __repr__(self):
        return "ConnectLog (%s) for %s at %s" % (self.status, self.username, self.local_ip)


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    username = db.Column(db.String, db.ForeignKey('user.username'))
    # user = db.relationship('User', backref=db.backref('connects', lazy='dynamic'))

    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)

    interface = db.Column(db.String(30))
    local_ip = db.Column(INET)
    remote_ip = db.Column(INET)

    def duration(self):
        rd = dateutil.relativedelta.relativedelta(self.ended_at, self.started_at)
        return ", ".join(
            [ "%d%s" % (q, u) for q, u in zip((rd.hours, rd.minutes, rd.seconds), ("hr","min","sec")) if q > 0 ]
        )

# init the db if it hasn't already been init'd
# db.create_all()
