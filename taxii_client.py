#!flask/bin/python
__version__ = '0.2'
import os
import argparse
import datetime
from dateutil.tz import tzutc
import libtaxii as t
import libtaxii.messages as tm
import libtaxii.clients as tc
try:
    import simplejson as json
except ImportError:
    import json


PID_FILE = '/tmp/taxii_client.pid'
PROXY_ENABLED = False
PROXY_SCHEME = 'http'
PROXY_STRING = '127.0.0.1:8008'
ATTACHMENTS_PATH_OUT = '/var/tmp/files_out'
"""Search for attachments in this path and attach them to the attribute"""
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


def create_inbox_message(data, content_binding=t.VID_CERT_EU_JSON_10):
    """Creates TAXII message from data"""
    content_block = tm.ContentBlock(
        content_binding=content_binding,
        content=data,
        timestamp_label=datetime.datetime.now(tzutc()))
    msg_id = tm.generate_message_id()

    inbox_message = tm.InboxMessage(
        message_id=msg_id,
        content_blocks=[content_block])

    return msg_id, inbox_message.to_json()


def main(**args):
    check_process(PID_FILE)
    client = tc.HttpClient()
    if PROXY_ENABLED:
        client.proxy_type = PROXY_SCHEME
        client.proxy_string = PROXY_STRING

    msg_id, msg = '', ''

    if args['data_type'] == 'string':
        msg_id, msg = create_inbox_message(args['data'])
    else:
        print '[-] Please use a JSON string'
        raise SystemExit

    http_response = client.callTaxiiService2(
        args['host'], args['path'],
        t.VID_CERT_EU_JSON_10, msg, args['port'])

    taxii_response = t.get_message_from_http_response(http_response, msg_id)
    print(taxii_response.to_json())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='TAXII Client',
        epilog='DO NOT USE IN PRODUCTION',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-t", "--type",
        dest="data_type",
        choices=['string'],
        default='string',
        help='Data type your posting, "sync" will read DB')
    parser.add_argument(
        "-d", "--data",
        dest="data",
        required=False,
        help='Data to be posted to TAXII Service')
    parser.add_argument(
        "-th", "--taxii_host",
        dest="host",
        default=TAXII_SERVICE_HOST,
        help='TAXII Service Host')
    parser.add_argument(
        "-tp", "--taxii_port",
        dest="port",
        default=TAXII_SERVICE_PORT,
        help='TAXII Service Port')
    parser.add_argument(
        "-tpath", "--taxii_path",
        dest="path",
        default=TAXII_SERVICE_PATH,
        help='TAXII Service Path')
    parser.add_argument(
        "-key", "--api_key",
        dest="api_key",
        help='MISP API Key')
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    main(**vars(args))
















