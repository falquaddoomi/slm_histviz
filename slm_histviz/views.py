import flask
from flask import render_template
from flask.ext.login import current_user, login_required, login_user, logout_user
from sqlalchemy import literal

from slm_histviz import app
from slm_histviz.data import ConnectLog, AccessLog, Session, User, HostServiceMapping
from slm_histviz.forms import LoginForm

@app.route('/')
def home():
    """ index page """
    ctx = {}

    if current_user and current_user.is_authenticated:
        ctx.update({'is_connected': current_user.is_connected()})

    return flask.render_template('home.html', **ctx)


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
                    AccessLog.hostname.ilike("%facebook%") | AccessLog.sni.ilike("%facebook%")
                    # AccessLog.hostname.ilike("%twitter%") |
                    # AccessLog.hostname.ilike("%instagram%")
                )
                # .filter(AccessLog.hostname.notilike("%amazonaws.com"))
                .order_by(AccessLog.created_at.desc())
                .limit(100)
        ),
    }

    return render_template('timeline.html', **ctx)


@app.route('/dashboard')
@login_required
def dashboard():
    ctx = {}
    return render_template('dashboard.html', **ctx)


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

        return flask.redirect(next or flask.url_for('home'))
    return flask.render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    """ logout user """
    logout_user()
    return flask.render_template('logout.html')


@app.context_processor
def my_utility_processor():

    def resolve_hostname(hostname):
        service = HostServiceMapping.query.filter(
            literal(hostname).like(HostServiceMapping.pattern)).first()
        return service.service if service is not None else '<%s>' % hostname

    return dict(resolve_hostname=resolve_hostname)


# TODO: add admin view to filter and see all users
