#!flask/bin/python
import os
import argparse
import datetime
from dateutil.tz import tzutc
import libtaxii as t
import libtaxii.messages as tm
import libtaxii.clients as tc


PID_FILE = '/tmp/taxii_daemon.pid'
PROXY_ENABLED = True
PROXY_SCHEME = 'http'
PROXY_STRING = '127.0.0.1:8008'
CB_XML_112608 = 'http://www.w3.org/TR/xml'
#TAXII_SERVICE_HOST = 'misplab.cert.europa.eu'
#TAXII_SERVICE_PORT = 80
#TAXII_SERVICE_PATH = '/taxii/inbox'
TAXII_SERVICE_HOST = '127.0.0.1'
TAXII_SERVICE_PORT = 4242
TAXII_SERVICE_PATH = '/inbox'


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


def create_inbox_message(data, content_binding=CB_XML_112608):
    """Creates TAXII message from data"""
    xml_content_block1 = tm.ContentBlock(
        content_binding=content_binding,
        content=data,
        timestamp_label=datetime.datetime.now(tzutc()))

    msg_id = tm.generate_message_id()

    inbox_message = tm.InboxMessage(
        message_id=msg_id,
        content_blocks=[xml_content_block1])
    return msg_id, inbox_message.to_xml()


def main(**args):
    check_process(PID_FILE)
    client = tc.HttpClient()
    if PROXY_ENABLED:
        client.proxy_type = PROXY_SCHEME
        client.proxy_string = PROXY_STRING
    x = open(args['data']).read()
    #msg_id, msg = create_inbox_message(args['data'])
    msg_id, msg = create_inbox_message(x)
    http_response = client.callTaxiiService2(args['host'], args['path'],
                                             t.VID_TAXII_XML_10, msg, args['port'])

    taxii_response = t.get_message_from_http_response(http_response, msg_id)
    print(taxii_response.to_xml())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TAXII Client', epilog='DO NOT USE IN PRODUCTION',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--data", dest="data", required=True, help='Data to be posted to TAXII Service')
    parser.add_argument("-th", "--taxii_host", dest="host", default=TAXII_SERVICE_HOST, help='TAXII Service Host')
    parser.add_argument("-tp", "--taxii_port", dest="port", default=TAXII_SERVICE_PORT, help='TAXII Service Port')
    parser.add_argument("-tpath", "--taxii_path", dest="path", default=TAXII_SERVICE_PATH, help='TAXII Service Path')
    args = parser.parse_args()

    main(**vars(args))

