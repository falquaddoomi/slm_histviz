import flask.ext.restless
from slm_histviz.data import db, AccessLog, ConnectLog

from slm_histviz import app

# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.


manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(AccessLog, methods=['GET'])
manager.create_api(ConnectLog, methods=['GET'])
