"""Asset creation pipeline"""

from slm_histviz import app
from flask_assets import Environment, Bundle
from webassets.filter import get_filter, register_filter

from webassets_react import React
register_filter(React)

# app.config.update(
#     BABEL_BIN='./node_modules/.bin/babel'
# )

assets = Environment(app)
assets.manifest = None
assets.cache = False

# babel filtering
# from webassets_babel import BabelFilter
# register_filter(BabelFilter)

babel = get_filter('babel', presets='es2015')

# explicitly-declared imports from bower, as there's stuff in there that we definitely don't want or need
# these files are just normal js; they don't need transpiling
bower_js_paths = [
    "bower_components/d3/d3.min.js",
    "bower_components/d3-timeline/src/d3-timeline.js",
    "bower_components/d3pie/d3pie/d3pie.min.js",
    "bower_components/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js",
    "bower_components/moment/min/moment-with-locales.min.js"
    # "bower_components/react/react.js",
    # "bower_components/react/react-dom.js"
]

# combine into a single thing and register
assets.register('js_all', Bundle(
    Bundle(*bower_js_paths),
    Bundle('js/*.js', filters=[babel]),
    # Bundle('jsx/*.jsx', filters=['react']), # FA: omitting react files for now
    output='gen/packed.js' #, filters='jsmin'
))

# make a css include as well, just for kicks
bower_css_paths = [
    "bower_components/bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css"
]

assets.register('css_all', Bundle(
    Bundle(*bower_css_paths),
    Bundle('css/*.css'),
    output='gen/packed.css'
))