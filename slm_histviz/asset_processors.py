"""Asset creation pipeline"""

from slm_histviz import app
from flask_assets import Environment, Bundle
from webassets.filter import get_filter

assets = Environment(app)

# babel filtering
from webassets.filter import register_filter
from webassets_babel import BabelFilter
register_filter(BabelFilter)

app.config.update(
    BABEL_PRESETS='es2015'
)

es6_bundle = Bundle('**/*.js', filters='babel')
assets.register('js_es6', es6_bundle)

# combining into a single thing
js = Bundle(es6_bundle, filters='jsmin', output='gen/packed.js')
assets.register('js_all', js)
