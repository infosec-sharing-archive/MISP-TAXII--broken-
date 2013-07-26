#!/usr/bin/env python

import sys

activate_this = '/home/www/taxiiservice/flask/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, '/home/www/taxiiservice')

from flup.server.fcgi import WSGIServer
from app import app as application