import libtaxii as t
import libtaxii.messages as tm
from lxml import etree
from cStringIO import StringIO

from flask import request
from app import app, db, make_taxii_response
from models import Event
from json import loads

import xmltodict
import sys


def etree_to_dict(t):
    d = {t.tag: map(etree_to_dict, t.iterchildren())}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d['text'] = t.text
    return d


def formatXML(parent):
    """
    Recursive operation which returns a tree formated
    as dicts and lists.
    Decision to add a list is to find the 'List' word
    in the actual parent tag.
    """
    ret = {}
    if parent.items():
        ret.update(dict(parent.items()))
    if parent.text:
        ret['__content__'] = parent.text
    if 'List' in parent.tag:
        ret['__list__'] = []
        for element in parent:
            ret['__list__'].append(formatXML(element))
    else:
        for element in parent:
            ret[element.tag] = formatXML(element)
    return ret

@app.route('/discovery', methods=['POST'])
def discovery_service():
    """The Discovery Service provides a requester with a list of TAXII Services
    and how these Services can be invoked"""
    service_instance1 = tm.DiscoveryResponse.ServiceInstance(service_type=tm.SVC_INBOX,#Required
        services_version=t.VID_TAXII_SERVICES_10,#Required
        protocol_binding = t.VID_TAXII_HTTP_10,#Required
        service_address = 'http://127.0.0.1/inbox/',#Required
        message_bindings = [t.VID_TAXII_XML_10],#Required, must have at least one value in the list
        inbox_service_accepted_content = [t.CB_STIX_XML_10],#Optional for service_type=SVC_INBOX, prohibited otherwise
        #If this is absent and service_type=SVC_INBOX,
        #It means the inbox service accepts all content
        available=True,#Optional - defaults to None, which means 'Unknown'
        message = 'This is a message.')#Optional

    discovery_response1 = tm.DiscoveryResponse(message_id = tm.generate_message_id(),#Required
        in_response_to = tm.generate_message_id(),#Required. This should be the ID of the corresponding request
        service_instances = [service_instance1])#Optional.

    return discovery_response1.to_xml()


@app.route('/feeds', methods=['POST'])
def feeds():
    """The Feed Management Service is the mechanism by which a Consumer can request information about
    TAXII Data Feeds, request subscriptions to TAXII Data Feeds, request the status of a subscription, or
    terminate existing subscriptions to TAXII Data Feeds."""
    pass


@app.route('/poll', methods=['POST'])
def poll():
    """The Poll Service is the mechanism by which a Producer allows Consumer-initiated pulls from
    a TAXII Data Feed"""
    pass

@app.route('/inbox', methods=['POST'])
def inbox():
    """The Inbox Service is the mechanism by which a Consumer accepts messages from a Producer in
    Producer-initiated exchanges (i.e., push messaging)"""

    msg = tm.get_message_from_xml(request.data)
    dict = msg.to_dict()
    data = dict['content_blocks'][0]['content']
    print data
    #sys.exit(0)
    j = loads(data)
    print j
    #exit()
    new_events = []
    for event in j:
        print event
        exit()
        checkevent = Event.query.filter_by(uuid=event['uuid']).first()
        if checkevent is None:
            e = Event(event['date'], event['risk'], event['info'], event['published'],
                      event['uuid'], event['attribute'])
            new_events.append(e)
    #db.session.add_all(new_events)
    #db.session.commit()
    print new_events


    # for posting XML
    #msg = tm.get_message_from_xml(request.data)
    #dict = msg.to_dict()
    #c = xmltodict.parse(dict['content_blocks'][0]['content'])

    #new_events = []
    #for event in c['CyDefSIG']['Event']:
    #    checkevent = Event.query.filter_by(uuid=event['uuid']).first()
    #    if checkevent is None:
    #        e = Event(event['date'], event['risk'], event['info'], event['published'],
    #                  event['uuid'], event['Attribute'])
    #        new_events.append(e)
    #db.session.add_all(new_events)
    #db.session.commit()

    if request.headers.get('X-TAXII-Content-Type') == t.VID_TAXII_XML_10:

        status_message1 = tm.StatusMessage(
            #Required
            message_id=tm.generate_message_id(),
            #Required. Should be the ID of the corresponding request
            in_response_to=msg.message_id,
            #Required
            status_type=tm.ST_SUCCESS,
            #May be optional or not allowed, depending on status_type
            status_detail='Machine-processable info here!',
            #Optional
            message='This is a message.')

        return make_taxii_response(status_message1.to_xml())

    error_message = tm.StatusMessage(
        message_id=tm.generate_message_id(),
        in_response_to=msg.message_id,
        status_type=tm.ST_FAILURE)
    return make_taxii_response(error_message)