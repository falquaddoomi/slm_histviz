from flask import Flask

from slm_histviz.utils import ReverseProxied
from flask.ext.bower import Bower

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_object('slm_histviz.config')

# Bower(app)

import slm_histviz.tasks
import slm_histviz.views
import slm_histviz.api
