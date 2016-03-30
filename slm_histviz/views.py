from flask import render_template, redirect, url_for
from slm_histviz import app
from slm_histviz.data import ConnectLog, AccessLog


@app.route('/')
def index():
    return redirect(url_for('datadatump'))


@app.route('/datadump')
def datadatump():
    ctx = {
        'connections': ConnectLog.query.all(),
        'accesses': AccessLog.query.order_by(AccessLog.created_at.desc()).limit(100),
    }

    return render_template('datadump.html', **ctx)


@app.route('/history')
def history():
    ctx = {
        'connections': ConnectLog.query.all(),
        'accesses': AccessLog.query.order_by(AccessLog.created_at.desc()).limit(100),
    }

    return render_template('history.html', **ctx)