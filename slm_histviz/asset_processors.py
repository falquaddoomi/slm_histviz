"""Asset creation pipeline"""

from slm_histviz import app
from flask_assets import Environment, Bundle
from webassets.filter import get_filter, register_filter

from webassets_react import React
register_filter(React)

app.config.update(
    BABEL_BIN='./node_modules/.bin/babel'
)

assets = Environment(app)
assets.manifest = None
assets.cache = False

# babel filtering
# from webassets_babel import BabelFilter
# register_filter(BabelFilter)

babel = get_filter('babel', presets='es2015')

# combining into a single thing
js = Bundle(
    # 'bower_components/**/*.js',
    Bundle('js/*.js'),
    Bundle(Bundle('jsx/*.jsx', filters=['react']), filters=babel),
    output='gen/packed.js' # filters='jsmin',
)

assets.register('js_all', js)
