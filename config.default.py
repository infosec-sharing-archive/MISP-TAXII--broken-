from flask.ext.sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3309/CTI_db_test'

DEBUG = True
SECRET_KEY = 'random string from CSRF'


# administrator list
ADMINS = ['list@mails.com']
