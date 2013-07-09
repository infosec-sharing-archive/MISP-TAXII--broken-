from flask import Flask, render_template, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from libtaxii import VID_TAXII_XML_10

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


def make_taxii_response(*args, **kwargs):
    if len(args) == 1:
        args = args[0]

    response = make_response(args)
    response.headers["Content-Type"] = kwargs.get("Content-Type", "application/xml")
    response.headers['X-TAXII-Content-Type'] = kwargs.get("X-TAXII-Content-Type", VID_TAXII_XML_10)

    return response


from app import views
