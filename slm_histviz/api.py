import dateutil.parser
import flask
import flask_restless
from flask import request
from flask_login import login_required, current_user
from slm_histviz.models import db, AccessLog, ConnectLog

from slm_histviz import app

# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(AccessLog, results_per_page=1000, methods=['GET'])
manager.create_api(ConnectLog, results_per_page=1000, methods=['GET'])

@app.route('/dashboard/accesses')
@login_required
def access_sessions():
    try:
        start_date = dateutil.parser.parse(request.args.get('start_date'))
        end_date = dateutil.parser.parse(request.args.get('end_date'))
    except KeyError:
        raise InvalidUsage('Requires both start_date and end_date to be specified')

    accesses = AccessLog.query.filter(AccessLog.user == current_user and AccessLog.created_at.between(start_date, end_date))

    # todo: for this user and a given start, end date, produce the following:
    # 1) a set of timespans of the form (hostname, start, end) <- perhaps should be service?
    # 2) an aggregation of seconds per hostname for the entire period
    # 3) a list of accesses

    return flask.jsonify(data=accesses.all())
