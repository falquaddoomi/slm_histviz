import flask
import flask_restless
from flask_login import login_required, current_user
from slm_histviz.models import db, AccessLog, ConnectLog

from slm_histviz import app

# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.


manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(AccessLog, results_per_page=1000, methods=['GET'])
manager.create_api(ConnectLog, results_per_page=1000, methods=['GET'])

@app.route('/dashboard/accesses')
@login_required
def access_sessions():
    accesses = AccessLog.query.filter(AccessLog.user == current_user)

    # todo: for this user and a given start, end date, produce the following:
    # 1) a set of timespans of the form (hostname, start, end) <- perhaps should be service?
    # 2) an aggregation of seconds per hostname for the entire period
    # 3) a list of accesses

    return flask.jsonify(data=accesses)
