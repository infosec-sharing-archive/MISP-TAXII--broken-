#!flask/bin/python
import os
import argparse
import datetime
from dateutil.tz import tzutc
import libtaxii as t
import libtaxii.messages as tm
import libtaxii.clients as tc
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String, Date, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker, class_mapper
from json import dumps
import warnings


PID_FILE = '/tmp/taxii_daemon.pid'
PROXY_ENABLED = True
PROXY_SCHEME = 'http'
PROXY_STRING = '127.0.0.1:8008'
TAXII_SERVICE_HOST = '127.0.0.1'
TAXII_SERVICE_PORT = 4242
TAXII_SERVICE_PATH = '/inbox'

# only required if you get data from a DB
Base = declarative_base()
db = create_engine('mysql://root@127.0.0.1:3309/CTI_db_test')
Session = sessionmaker(bind=db)


def is_process_running(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return
    else:
        return pid


def check_process(path):
    if os.path.exists(path):
        pid = int(open(path).read())
        if is_process_running(pid):
            print "Process %d is still running" % pid
            raise SystemExit
        else:
            os.remove(path)
    pid = os.getpid()
    open(path, 'w').write(str(pid))
    return pid


def serialize(model, exclude_fields=[]):
    warnings.warn('deprecated', DeprecationWarning)
    """Transforms a model into a dictionary which can be dumped to JSON."""
    columns = [c.key for c in class_mapper(model.__class__).columns if c not in exclude_fields]
    return dict((c, getattr(model, c).__str__()) if type(getattr(model, c)) is datetime.date
                else (c, getattr(model, c)) for c in columns)


def create_inbox_message(data, content_binding=t.VID_CERT_EU_JSON_10):
    """Creates TAXII message from data"""
    xml_content_block1 = tm.ContentBlock(
        content_binding=content_binding,
        content=data,
        timestamp_label=datetime.datetime.now(tzutc()))
    msg_id = tm.generate_message_id()

    inbox_message = tm.InboxMessage(
        message_id=msg_id,
        content_blocks=[xml_content_block1])

    return msg_id, inbox_message.to_json()


def load_db_data():
    session = Session()
    events = [e.serialize for e in session.query(Event).filter(Event.published == 1).all()]
    return dumps(events)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.datetime.now())
    risk = Column(String)
    info = Column(Text)
    published = Column(Integer)
    uuid = Column(String)
    attributes = relation('Attribute', backref='event')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "date": self.date.__str__(),
            "risk": self.risk,
            "info": self.info,
            "published": self.published,
            "uuid": self.uuid,
            "Attribute": self.serialize_attributes

        }

    @property
    def serialize_attributes(self):
        return [item.serialize for item in self.attributes]

    def __init__(self, date, risk, info, published, uuid, attrs):
        self.date = date
        self.risk = risk
        self.info = info
        self.published = published
        self.uuid = uuid

    def __repr__(self):
        return '<Event %r>' % self.uuid


class Attribute(Base):
    __tablename__ = 'attributes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    category = Column(String(255))
    value1 = Column(Text())
    value2 = Column(Text())
    to_ids = Column(Boolean)
    uuid = Column(String(255))
    revision = Column(Integer)
    private = Column(Boolean)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "category": self.category,
            "to_ids": self.to_ids,
            "value1": self.value1,
            "value2": self.value2,
            "uuid": self.uuid,
            "private": self.private,
            'revision': self.revision

        }

    def __init__(self, **kwargs):
        if kwargs:
            self.category = kwargs['category']
            self.to_ids = kwargs['to_ids']
            self.value1 = kwargs['value1']
            self.value2 = kwargs['value2']
            self.uuid = kwargs['uuid']
            self.private = kwargs['private']
            self.revision = kwargs['revision']

    def __repr__(self):
        return '<Attribute %r>' % self.value1


def main(**args):
    check_process(PID_FILE)
    client = tc.HttpClient()
    if PROXY_ENABLED:
        client.proxy_type = PROXY_SCHEME
        client.proxy_string = PROXY_STRING

    msg_id, msg = '', ''

    if args['data_type'] == 'string':
        msg_id, msg = create_inbox_message(args['data'])
    elif args['data_type'] == 'xml':
        print '[-] No more XML, use JSON'
        raise SystemExit
        #msg_id, msg = create_inbox_message(open(args['data']).read())
    elif args['data_type'] == 'json':
        msg_id, msg = create_inbox_message(load_db_data())
    http_response = client.callTaxiiService2(args['host'], args['path'],
                                             t.VID_CERT_EU_JSON_10, msg, args['port'])

    taxii_response = t.get_message_from_http_response(http_response, msg_id)
    print(taxii_response.to_json())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TAXII Client', epilog='DO NOT USE IN PRODUCTION',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--type", dest="data_type", required=True, default='json', help='Data type your posting')
    parser.add_argument("-d", "--data", dest="data", required=False, help='Data to be posted to TAXII Service')
    parser.add_argument("-th", "--taxii_host", dest="host", default=TAXII_SERVICE_HOST, help='TAXII Service Host')
    parser.add_argument("-tp", "--taxii_port", dest="port", default=TAXII_SERVICE_PORT, help='TAXII Service Port')
    parser.add_argument("-tpath", "--taxii_path", dest="path", default=TAXII_SERVICE_PATH, help='TAXII Service Path')
    args = parser.parse_args()

    main(**vars(args))

