""" views.py """
import re

import flask
import socket
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import render_template, request
from sqlalchemy import text, literal
import pytz

from slm_histviz import app
from slm_histviz.data import db, ConnectLog, AccessLog, Session, User, HostServiceMapping
from slm_histviz.forms import LoginForm


@app.route('/')
def index():
    """ index page """

    row = ConnectLog.query.filter(
        ConnectLog.username ==
        current_user.username).order_by(ConnectLog.created_at.desc()).limit(1)

    ctx = {'is_connected': row[0].status == 'connected'}

    return flask.render_template('index.html', **ctx)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ login page """
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        print str(form.data)

        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User.query.get(form.username.data)

        if user is None:
            raise

        login_user(user, remember=True)

        flask.flash('Logged in as %s' % user.username, 'info')

        next = flask.request.args.get('next')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        # if not next_is_valid(next):
        #     return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    """ logout user """
    logout_user()
    return flask.render_template('logout.html')


@app.route('/datadump')
@login_required
def datadump():
    """ dump all data on page """
    ctx = {
        'connections': ConnectLog.query.filter(
            ConnectLog.username ==
            current_user.username).order_by(ConnectLog.created_at.desc()).limit(100),
        'accesses': AccessLog.query.filter(
            AccessLog.username ==
            current_user.username).order_by(AccessLog.created_at.desc()).limit(100),
        'sessions': Session.query.filter(Session.username == current_user.username),
    }

    return render_template('datadump.html', **ctx)


@app.context_processor
def my_utility_processor():

    def resolve_hostname(hostname):
        service = HostServiceMapping.query.filter(
            literal(hostname).like(HostServiceMapping.pattern)).first()
        return service.service if service is not None else '<%s>' % hostname

    return dict(resolve_hostname=resolve_hostname)


@app.route('/timeline')
@login_required
def timeline():
    """ show timeline of data """
    ctx = {
        # 'connections': ConnectLog.query.filter(ConnectLog.username == current_user.username),
        'sessions': Session.query.filter(Session.username == current_user.username),
        # 'rolled_access': db.engine.execute(text(
        #     """select username, hostname, protocol, min(created_at) as started_at, max(created_at) as ended_at, count(*) as hits
        #     from access_log where username=:name GROUP BY username, hostname, protocol, date_trunc('second', created_at);"""
        # ).params(name=current_user.username)),
        'accesses': (
            AccessLog.query
                # .filter(AccessLog.hostname.notilike("%1e100.net"))
                .filter(AccessLog.username == current_user.username)
                .filter(
                    AccessLog.hostname.ilike("%facebook%")
                    # AccessLog.hostname.ilike("%twitter%") |
                    # AccessLog.hostname.ilike("%instagram%")
                )
                # .filter(AccessLog.hostname.notilike("%amazonaws.com"))
                .order_by(AccessLog.created_at.desc())
                .limit(100)
        ),
    }

    return render_template('timeline.html', **ctx)


@app.template_filter('to_nyc_timezone')
def _jinja2_filter_nyctime(date, fmt=None):
    return pytz.utc.localize(date).astimezone(pytz.timezone('America/New_York'))


@app.template_filter('fancy_datetime')
def _jinja2_strformat_datetime(date, fmt=None):
    return date.strftime('%Y/%m/%d, %-I:%M %p (%Z)')


is_ip_regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


@app.template_filter('lookup_ip')
def lookup_ip(in_ip):
    if not in_ip:
        return "(no value given)"
    elif not is_ip_regex.match(in_ip):
        return "(not an ip)"

    try:
        result = socket.gethostbyaddr(in_ip)
        return result[0]
    except:
        return "(unavailable)"

# TODO: add admin view to filter and see all users
