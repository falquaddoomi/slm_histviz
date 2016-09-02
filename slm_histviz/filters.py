import pytz
import re
import socket

from slm_histviz import app


@app.template_filter('to_nyc_timezone')
def _jinja2_filter_nyctime(date, fmt=None):
    return pytz.utc.localize(date).astimezone(pytz.timezone('America/New_York'))


@app.template_filter('fancy_datetime')
def _jinja2_strformat_datetime(date, fmt=None):
    return date.strftime('%Y/%m/%d, %I:%M %p (%Z)')


is_ip_regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

@app.template_filter('lookup_ip')
def lookup_ip(in_ip):
    if not in_ip:
        return "(no value given)"
    elif not is_ip_regex.match(in_ip):
        return "(not an ip)"

    try:
        result = socket.gethostbyaddr(in_ip)
        return result[0]
    except:
        return "(unavailable)"
