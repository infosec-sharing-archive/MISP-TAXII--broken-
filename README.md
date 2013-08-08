Overview
========

Simple JSON implementation of Trusted Automated eXchange of Indicator 
Information (TAXII).
Although this implementation is MISP specific it can be easily adapted for a broader audience.
Currently only the Inbox service is supported.

ASSUMPTION
==========
you have a running MISP instance (develop or CTI branch) on an Ubuntu 12.04 or higher server

SERVICE INSTALL
===============
For a quick testing environment you can use https://github.com/MISP/MISP-TAXII-Vagrant
install dependencies
---------------------
    apt-get update
    apt-get install python-flup python-virtualenv libapache2-mod-wsgi python-dev libxslt1-dev
    libxml2-dev git libmysqlclient-dev

clone the service and setup the Virtual Python Environment
------------------------------------
    cd /home/www
    git clone https://github.com/MISP/MISP-TAXII.git taxiiservice
    cd taxiiservice
    virtualenv flask
    flask/bin/pip install -r requirements.txt

alternatively you can activate the virtual environment and install:

    source flask/bin/activate
    pip install -r requirements.txt

service configuration
----------------------
    mv config.default.py config.py
    vi config.py

minimal required changes:
* change SQLALCHEMY_DATABASE_URI to reflect your database configuration
* edit TAXII_ROOT to add your taxii document root
* edit ATTACHMENTS_PATH_IN, this is where attribute attachments will be saved

edit your apache.misp configuration and add
--------------------------------------------
    WSGIDaemonProcess taxii processes=2 threads=15 display-name=%{GROUP}
    WSGIProcessGroup taxii
    WSGIScriptAlias /taxii /home/www/taxiiservice/taxii_service.wsgi

Tweak configuration as needed.

restart apache
--------------

    service apache2 restart

CLIENT CONFIGURATION
====================

taxii_client.py configuration:

    TAXII_SERVICE_HOST = '127.0.0.1'
    TAXII_SERVICE_PORT = 8888
    TAXII_SERVICE_PATH = '/taxii/inbox'
    ATTACHMENTS_PATH_IN = '/var/tmp/files_out'
    DB = create_engine('mysql://user:pass@host:port/db')


RUN
===

Executing the client without parameters will push all events, associated attributes and
attribute attachments from DB to TAXII_SERVICE_HOST. You can bypass this by providing
parameteres to the client.
For details:

    python taxii_client.py -h

LICENSE
=======

taxii_service: synchronize MISP events and attributes

Copyright (c) 2013 CERT-EU

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
