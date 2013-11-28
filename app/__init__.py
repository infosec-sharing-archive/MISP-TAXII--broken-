from flask import Flask, render_template, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from libtaxii import VID_CERT_EU_JSON_10
from logging import Formatter

app = Flask(__name__)
app.config.from_object('config')

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('taxii.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)

db = SQLAlchemy(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


def make_taxii_response(*args, **kwargs):
    if len(args) == 1:
        args = args[0]

    response = make_response(args)
    response.headers["Content-Type"] = kwargs.get("Content-Type", "application/xml")
    response.headers['X-TAXII-Content-Type'] = kwargs.get(
        "X-TAXII-Content-Type",
        VID_CERT_EU_JSON_10)

    return response


from app import views
