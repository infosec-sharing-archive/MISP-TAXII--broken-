#!/usr/bin/env python
import os
import sys

activate_this = '/home/www/taxiiservice/flask/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

#sys.path.insert(0, '/home/www/taxiiservice')
sys.path.append('/home/www/taxiiservice')
#path = os.path.join(os.path.dirname(__file__), os.pardir)
#if path not in sys.path:
#    sys.path.append(path)

from flup.server.fcgi import WSGIServer
from app import app as application

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/var/run/taxii.sock', umask=000).run()
