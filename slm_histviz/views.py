import flask
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import render_template, redirect, url_for, request
from slm_histviz import app
from slm_histviz.data import ConnectLog, AccessLog, Session, User
from slm_histviz.forms import LoginForm


@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    logout_user()
    return flask.render_template('logout.html')


@app.route('/datadump')
@login_required
def datadump():
    ctx = {
        'connections': ConnectLog.query.filter(ConnectLog.username == current_user.username),
        'accesses': AccessLog.query.filter(AccessLog.username == current_user.username).order_by(AccessLog.created_at.desc()).limit(100),
    }

    return render_template('datadump.html', **ctx)


@app.route('/history')
@login_required
def timeline():
    ctx = {
        'connections': ConnectLog.query.filter(ConnectLog.username == current_user.username),
        'sessions': Session.query.filter(Session.username == current_user.username),
        'accesses': (
            AccessLog.query
                # .filter(AccessLog.hostname.notilike("%1e100.net"))
                .filter(AccessLog.username == current_user.username)
                .filter(
                    AccessLog.hostname.ilike("%facebook%") |
                    AccessLog.hostname.ilike("%twitter%") |
                    AccessLog.hostname.ilike("%instagram%")
                )
                # .filter(AccessLog.hostname.notilike("%amazonaws.com"))
                .order_by(AccessLog.created_at.desc())
                .limit(100)
        ),
    }

    return render_template('history.html', **ctx)