from flask_login import login_required, current_user, UserMixin

from slm_histviz import app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.dialects.postgresql.base import INET
import dateutil.relativedelta

from slm_histviz.filters import lookup_ip

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
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

    def is_connected(self):
        """
        Indicates whether the user has at least one non-disconnected connection.
        :return: true if we're connected, false otherwise
        """

        base = ConnectLog.query.filter(ConnectLog.username == self.username)
        connections = base.filter(ConnectLog.status == 'connected')
        disconnections = base.filter(ConnectLog.status == 'disconnected')

        return (connections.count() - disconnections.count()) > 0

    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def __unicode__(self):
        return self.username


class AccessLog(db.Model):
    __tablename__ = 'access_log'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, db.ForeignKey('user.username'))
    user = db.relationship('User')

    created_at = db.Column(db.DateTime, server_default=text("timezone('utc'::text, now())"))

    hostname = db.Column(db.String)
    sni = db.Column(db.String)
    protocol = db.Column(db.String)
    length = db.Column(db.Integer)

    @classmethod
    @login_required
    def query(cls):
        q = db.session.query(cls).filter(cls.user == current_user)
        return q

    def __str__(self):
        return "%s accessed %s (prot: %s, SNI: %s, len: %d) at %s" % (self.username, self.hostname, self.protocol, self.sni, self.length, self.created_at)

    def __repr__(self):
        return "AccessLog for %s to %s" % (self.username, self.hostname)

    def sni_or_reverse_ip(self):
        if self.sni == '<unknown>' or self.sni == '<http-unknown>':
            return lookup_ip(self.hostname)
        else:
            return self.sni

    def resolved_service(self):
        service = HostServiceMapping.query.filter(self.hostname.like(HostServiceMapping.pattern)).first()
        return service if service is not None else '<%s>' % self.hostname


class ConnectLog(db.Model):
    __tablename__ = 'connect_log'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, db.ForeignKey('user.username'))
    user = db.relationship('User')

    created_at = db.Column(db.DateTime, server_default=text("timezone('utc'::text, now())"))

    status = db.Column(db.String(30))
    interface = db.Column(db.String(30))
    local_ip = db.Column(INET)
    remote_ip = db.Column(INET)

    def __str__(self):
        return "%s (%s :: %s) %s on %s" % (self.username, self.local_ip, self.interface, self.status, self.created_at)

    def __repr__(self):
        return "ConnectLog (%s) for %s at %s" % (self.status, self.username, self.local_ip)


class HostServiceMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    service = db.Column(db.String)
    pattern = db.Column(db.String)


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
            ["%d%s" % (q, u) for q, u in zip((rd.hours, rd.minutes, rd.seconds), ("hr", "min", "sec")) if q > 0]
        )
