import flask.ext.restless
from slm_histviz.models import db, AccessLog, ConnectLog

from slm_histviz import app

# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.


manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(AccessLog, results_per_page=1000, methods=['GET'])
manager.create_api(ConnectLog, results_per_page=1000, methods=['GET'])
