from slm_histviz import app
from slm_histviz.data import User
from flask.ext import login as flask_login

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)