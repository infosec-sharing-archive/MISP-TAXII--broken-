from lxml import etree
import datetime
from dateutil.tz import tzutc
from cStringIO import StringIO
import libtaxii as t
import libtaxii.messages as tm
import libtaxii.clients as tc





'''
# discover available services
discover_request = tm.DiscoveryRequest(message_id=tm.generate_message_id())

http_response = c.callTaxiiService2('127.0.0.1', '/discovery_service', t.VID_TAXII_XML_10, discover_request.to_xml(), 4242)

taxii_message = t.get_message_from_http_response(http_response,
                                                 discover_request.message_id)
print(taxii_message.to_xml())
'''

'''
# send STIX message to /inbox
stix_etree = etree.parse(StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')).getroot()

xml_content_block1 = tm.ContentBlock(
    content_binding=t.CB_STIX_XML_10, #Required
    content=stix_etree,#Required. Can be etree or string
    padding='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',#Optional
    timestamp_label=datetime.datetime.now(tzutc()))#Optional

subscription_information1 = tm.InboxMessage.SubscriptionInformation(
    feed_name = 'SomeFeedName',#Required
    subscription_id = 'SubsId021',#Required
    inclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional - Absence means 'no lower bound'
    inclusive_end_timestamp_label = datetime.datetime.now(tzutc()))#Optional - Absence means 'no upper bound'


inbox_message1 = tm.InboxMessage(
    message_id = tm.generate_message_id(),#Required
    message = 'This is a message.',#Optional
    subscription_information = subscription_information1,#Optional
    content_blocks = [xml_content_block1])#Optional

http_response = c.callTaxiiService2('127.0.0.1', '/inbox', t.VID_TAXII_XML_10, inbox_message1.to_xml(), 4242)

taxii_message = t.get_message_from_http_response(http_response,
                                                 inbox_message1.message_id)
print(taxii_message.to_xml())
'''

c = tc.HttpClient()
c.proxy_type = 'http'
c.proxy_string = '127.0.0.1:8008'

xml_binding = 'http://www.w3.org/TR/xml/'

xml_string = '<?xml version="1.0" encoding="UTF-8"?><CyDefSIG><Event><id>24</id> <date>2011-08-15</date> <risk>Medium</risk> <info>Email with attachment &#13; RTF pFragments overflow - CVE-2010-3333</info> <published>1</published> <uuid>4f75a818-2e54-4ac1-a0a1-49b30a000b01</uuid> <Attribute> <id>39</id> <event_id>24</event_id> <category>Payload delivery</category> <type>email-src</type> <value1>jn.macholand@gmail.com</value1> <value2/> <to_ids>1</to_ids> <uuid>4f75a81a-27a4-4f1e-9f83-49b30a000b01</uuid> <revision>0</revision> <private>0</private> <value>jn.macholand@gmail.com</value> <category_order>c</category_order> </Attribute></Event></CyDefDIG>'

xml_content_block1 = tm.ContentBlock(
    content_binding=t.CB_STIX_XML_10, #Required
    content=xml_string,#Required. Can be etree or string
    #padding='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',#Optional
    timestamp_label=datetime.datetime.now(tzutc())) #Optional

subscription_information1 = tm.InboxMessage.SubscriptionInformation(
    feed_name = 'SomeFeedName',#Required
    subscription_id = 'SubsId021',#Required
    inclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional - Absence means 'no lower bound'
    inclusive_end_timestamp_label = datetime.datetime.now(tzutc()))#Optional - Absence means 'no upper bound'


inbox_message1 = tm.InboxMessage(
    message_id = tm.generate_message_id(),#Required
    message = 'This is a message.',#Optional
    #subscription_information = subscription_information1,#Optional
    content_blocks = [xml_content_block1])#Optional

http_response = c.callTaxiiService2('127.0.0.1', '/inbox', t.VID_TAXII_XML_10, inbox_message1.to_xml(), 4242)

taxii_response = t.get_message_from_http_response(http_response,
                                                 inbox_message1.message_id)
#print 'Originial ID: ' + inbox_message1.message_id
print(taxii_response.to_xml())