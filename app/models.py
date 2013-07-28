from app import db
import datetime


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, default=datetime.datetime.now())
    risk = db.Column(db.String)
    info = db.Column(db.Text)
    published = db.Column(db.Integer)
    uuid = db.Column(db.String)
    attributes = db.relationship('Attribute', backref='event', lazy='dynamic')

    def __init__(self, date, risk, info, published, uuid, attrs):
        self.date = date
        self.risk = risk
        self.info = info
        self.published = published
        self.uuid = uuid

        if attrs:
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    category = db.Column(db.String(255))
    value1 = db.Column(db.Text())
    value2 = db.Column(db.Text())
    to_ids = db.Column(db.Boolean)
    uuid = db.Column(db.String(255))
    revision = db.Column(db.Integer)
    private = db.Column(db.Boolean)
    #value = db.Column(db.String(255))?
    #category_order = db.Column(db.String)?

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
        return '<Attribute %r>' % self.category

