from functools import wraps

from flask import current_app
from flask_login import current_user

from slm_histviz import app
from slm_histviz.models import User
import flask_login

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


def role_required(role="ANY"):
    """
    Requires that the user be logged in and have the specific role mentioned in the 'role' parameter.
    :param role: the role to check for, or ANY to allow any authenticated user
    :return: a view protected by login and role predicates
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated():
               return current_app.login_manager.unauthorized()
            urole = current_app.login_manager.reload_user().get_urole()
            if (urole != role) and (role != "ANY"):
                return current_app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
