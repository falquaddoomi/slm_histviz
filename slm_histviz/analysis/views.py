from dateutil.parser import parse
import pytz
from flask import jsonify
from flask import render_template

from slm_histviz import app
from slm_histviz.models import db, ConnectLog, AccessLog, Session
from flask_login import login_required


@app.route('/analysis/timeline')
@login_required
def analysis_timeline():
    return render_template('analysis/timeline.html')


@app.route('/analysis/timeline_data')
def analysis_timeline_data():
    def get_span(username, timespan):
        return jsonify(points=
            AccessLog.query()
                .filter(AccessLog.username == username)
                .filter(AccessLog.created_at.between(timespan[0], timespan[1]))
                .all()
        )

    users = [
        {'username': 'faisal', 'span': map(parse_utc, ["9/21/2016 10:31am EST", "9/21/2016 10:48am EST"])},
        {'username': 'hongyi', 'span': map(parse_utc, ["9/21/2016 10:31am EST", "9/21/2016 10:31am EST"])},
        {'username': 'fabian', 'span': map(parse_utc, ["9/20/2016 11:15pm EST", "9/20/2016 11:32am EST"])}
    ]

    data = dict([
        (user['username'], get_span(user['username'], user['span'])) for user in users
    ])

    return jsonify(data=data)


def parse_utc(timestring):
    return parse(timestring).astimezone(pytz.utc)
