import libtaxii as t
import libtaxii.messages as tm

from flask import request
from config import TAXII_ROOT, CB_EVENTS_JSON_10
from app import app, make_taxii_response
import json
import urllib2
import time

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
    dict = json.loads(msg.to_json())
    data = dict['content_blocks'][0]['content']

    posted_data = json.loads(data)
    api_key = posted_data['api_key']
    server_url = posted_data['server_url']

    if request.headers.get('X-TAXII-Content-Type') != t.VID_CERT_EU_JSON_10:
        sm = tm.StatusMessage(
            message_id=tm.generate_message_id(),
            in_response_to=msg.message_id,
            status_type=tm.ST_UNSUPPORTED_PROTOCOL,
            message='This service only accepts %s ' % t.VID_CERT_EU_JSON_10)

        return make_taxii_response(sm.to_json())

    if request.headers.get('X-TAXII-Content-Type') == t.VID_CERT_EU_JSON_10:
        headers = {'Authorization': api_key, 'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        req = urllib2.Request(server_url, data, headers)

        try:
            response = urllib2.urlopen(req)
        except Exception as e:
            print str(e)

        status_message1 = tm.StatusMessage(
            message_id=tm.generate_message_id(),
            in_response_to=msg.message_id,
            status_type=tm.ST_SUCCESS,
            status_detail="Total Time: %s" % (time.time() - start),
            message=str(response.read()))

        return make_taxii_response(status_message1.to_json())

    error_message = tm.StatusMessage(
        message_id=tm.generate_message_id(),
        in_response_to=msg.message_id,
        message='This queue only accepts %s content type' % t.VID_CERT_EU_JSON_10,
        status_type=tm.ST_FAILURE)

    return make_taxii_response(error_message.to_json())
