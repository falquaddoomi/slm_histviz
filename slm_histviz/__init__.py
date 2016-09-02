from flask import Flask

from slm_histviz.utils import ReverseProxied

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_object('slm_histviz.config')

# from flask_bower import Bower
# Bower(app)

# preprocesses assets (js, css, etc.) to produce combined/processed includes
import  slm_histviz.asset_processors

import slm_histviz.tasks
import slm_histviz.auth
import slm_histviz.filters
import slm_histviz.views
import slm_histviz.api
