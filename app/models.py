import os
import datetime
from base64 import b64decode
from app import db
from config import ATTACHMENTS_PATH_IN
from flask.ext.sqlalchemy import event


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, default=datetime.datetime.now())
    risk = db.Column(db.String)
    info = db.Column(db.Text)
    published = db.Column(db.Integer)
    uuid = db.Column(db.String)
    distribution = db.Column(db.Integer)
    attributes = db.relationship('Attribute', backref='event', lazy='dynamic')

    def __init__(self, date, risk, info, published, uuid, distribution, attrs):
        self.date = date
        self.risk = risk
        self.info = info
        self.published = published
        self.uuid = uuid
        self.distribution = distribution

        for attr in attrs:
            if 'uuid' in attr:
                try:
                    attrcheck = Attribute.query.filter_by(uuid=attr['uuid']).first()
                    if attrcheck is None:
                        a2 = Attribute(**attr)
                        self.attributes.append(a2)
                    else:
                        pass
                        # attach existing attr?
                        #self.attributes.append(attrcheck)
                except TypeError as e:
                    print '[-]' + str(e)
                    print '[-]' + attr

    def __repr__(self):
        return '<{}, {}>'.format(self.uuid, ":".join([a.uuid for a in self.attributes]))


class Attribute(db.Model):
    __tablename__ = 'attributes'
    __mapper_args__ = {
        'exclude_properties': ['attachment']
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    category = db.Column(db.String(255))
    value1 = db.Column(db.Text())
    value2 = db.Column(db.Text())
    to_ids = db.Column(db.Boolean)
    uuid = db.Column(db.String(255))
    revision = db.Column(db.Integer)
    distribution = db.Column(db.Integer)
    attachment = None

    def __init__(self, **kwargs):
        if kwargs:
            self.category = kwargs['category']
            self.to_ids = kwargs['to_ids']
            self.value1 = kwargs['value1']
            self.value2 = kwargs['value2']
            self.uuid = kwargs['uuid']
            self.revision = kwargs['revision']
            self.distribution = kwargs['distribution']
            self.attachment = kwargs['attachment']
            #if kwargs['attachment'] is not None:
                #print os.path.join(ATTACHMENTS_PATH_IN, str(self.event_id))
                #os.makedirs(os.path.join(ATTACHMENTS_PATH_IN, str(self.event_id)), 0755)
                #with open(os.path.join(ATTACHMENTS_PATH_IN, str(self.event_id), str(self.id)),
                #          'wb') as f:
                #    f.write(b64decode(kwargs['attachment']))

    def __repr__(self):
        return '<Attribute %r>' % self.category


def update_distribution(mapper, connection, target):
    pass


def save_attachment(mapper, connection, target):
    if target.attachment is not None:
        npath = os.path.join(ATTACHMENTS_PATH_IN, str(target.event_id))
        if not os.path.exists(npath):
            os.makedirs(npath, 0755)
        with open(os.path.join(npath, str(target.id)), 'wb') as f:
            f.write(b64decode(target.attachment))

event.listen(Attribute, 'before_insert', update_distribution)
event.listen(Event, 'before_insert', update_distribution)
event.listen(Attribute, 'after_insert', save_attachment)