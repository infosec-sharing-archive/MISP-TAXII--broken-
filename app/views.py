import libtaxii as t
import libtaxii.messages as tm

from flask import request
from config import TAXII_ROOT, CB_EVENTS_JSON_10
from app import app, db, make_taxii_response
from models import Event
from json import loads
import time
import warnings


def etree_to_dict(t):
    warnings.warn('deprecated', DeprecationWarning)
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
    warnings.warn('deprecated', DeprecationWarning)
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


@app.route('/taxii-discovery-service', methods=['POST'])
def discovery_service():
    """The Discovery Service provides a requester with a list of TAXII Services
    and how these Services can be invoked"""
    # be conservative in what you send and liberal in what you accept

    request_msg = tm.get_message_from_json(request.data)

    inbox_instance = tm.DiscoveryResponse.ServiceInstance(
        service_type=tm.SVC_INBOX,
        services_version=t.VID_TAXII_SERVICES_10,
        protocol_binding=t.VID_TAXII_HTTP_10,
        service_address=TAXII_ROOT + '/inbox/',
        message_bindings=[t.VID_CERT_EU_JSON_10],
        inbox_service_accepted_content=[CB_EVENTS_JSON_10],
        available=True,
        message='Inbox service')
    poll_instance = tm.DiscoveryResponse.ServiceInstance(
        service_type=tm.SVC_POLL,
        services_version=t.VID_TAXII_SERVICES_10,
        protocol_binding=t.VID_TAXII_HTTP_10,
        service_address=TAXII_ROOT + '/poll/',
        message_bindings=[t.VID_TAXII_XML_10,  t.VID_CERT_EU_JSON_10],
        inbox_service_accepted_content=[t.CB_STIX_XML_10, CB_EVENTS_JSON_10],
        available=True,
        message='Poll service')

    discovery_response = tm.DiscoveryResponse(
        message_id=tm.generate_message_id(),
        in_response_to=request_msg.message_id,
        service_instances=[inbox_instance, poll_instance])

    return discovery_response.to_json()


@app.route('/feeds', methods=['POST'])
def feeds():
    """The Feed Management Service is the mechanism by which a Consumer can request information
    about TAXII Data Feeds, request subscriptions to TAXII Data Feeds, request the status of a
    subscription, or terminate existing subscriptions to TAXII Data Feeds."""
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
    start = time.time()
    msg = tm.get_message_from_json(request.data)
    dict = loads(msg.to_json())
    data = dict['content_blocks'][0]['content']

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

    if request.headers.get('X-TAXII-Content-Type') == t.VID_CERT_EU_JSON_10:
        """status_message1 = tm.StatusMessage(
                message_id=tm.generate_message_id(),
                in_response_to=msg.message_id,
                status_type=tm.ST_SUCCESS,
                status_detail='Machine-processable info here!',
                message='This is a message.')

        return make_taxii_response(status_message1.to_json())"""

        try:
            c = loads(data)
        except ValueError as e:
            print '[-] ' + str(e)

        new_events = []
        for event in c:
            #print event
            checkevent = Event.query.filter_by(uuid=event['uuid']).first()
            if checkevent is None:
                e = Event(event['date'], event['risk'], event['info'], event['published'],
                          event['uuid'], event['distribution'], event['Attribute'])
                new_events.append(e)
        db.session.add_all(new_events)

        try:
            db.session.commit()
        except Exception as e:
            print '[-] ' + str(e)
            error_message = tm.StatusMessage(
                message_id=tm.generate_message_id(),
                in_response_to=msg.message_id,
                status_type=tm.ST_FAILURE,
                status_detail='Could not save session')
            return make_taxii_response(error_message)

        status_message1 = tm.StatusMessage(
            message_id=tm.generate_message_id(),
            in_response_to=msg.message_id,
            status_type=tm.ST_SUCCESS,
            status_detail="Total Time: %s" % (time.time() - start),
            message='This is a message.')

        return make_taxii_response(status_message1.to_json())

    error_message = tm.StatusMessage(
        message_id=tm.generate_message_id(),
        in_response_to=msg.message_id,
        message='This queue only accepts %s content type' % t.VID_CERT_EU_JSON_10,
        status_type=tm.ST_FAILURE)

    return make_taxii_response(error_message.to_json())