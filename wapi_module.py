from json import loads
import httplib, base64
import ConfigParser, logging
import ssl
#import requests

CONF = "config.ini"
parser = ConfigParser.SafeConfigParser()
parser.read(CONF)
GRID_VIP = parser.get('Default', 'GRID_VIP')
#USERNAME = parser.get('Default', 'USERNAME')
#PASSWORD = parser.get('Default', 'PASSWORD')
ADMIN_USERNAME = parser.get('Default', 'ADMIN_USERNAME')
ADMIN_PASSWORD = parser.get('Default', 'ADMIN_PASSWORD')
WAPI = parser.get('Default', 'WAPI_VERSION')
DEFAULT_OBJECT_TYPE = 'network'
URLENCODED = 'application/json'
DEFAULT_CONTENT_TYPE = URLENCODED
PATH = '/wapi/v' + WAPI + '/'

def wapi_request(operation, ref='', params='', fields='', \
                    object_type=DEFAULT_OBJECT_TYPE, \
                    content_type=DEFAULT_CONTENT_TYPE, username='admin', password='infoblox'):
    '''
    Send an HTTPS request to the NIOS server.
    '''
    # Create connection and request header.
    conn = httplib.HTTPSConnection(GRID_VIP)
    auth_header = 'Basic %s' % (':'.join([ADMIN_USERNAME, ADMIN_PASSWORD])
                                .encode('Base64').strip('\r\n'))
    request_header = {'Authorization':auth_header,
                      'Content-Type': content_type}
    if ref:
        url = PATH + ref
    else:
        url = PATH + object_type
    if params:
        url += params
    conn.request(operation, url, fields, request_header)
    response = conn.getresponse();
    if response.status >= 200 and response.status < 300:
        return handle_success(response)
    else:
        return handle_exception(response)

def handle_exception(response):
    '''
    If there was encountered an error while performing requested action,
    print response code and error message.
    '''
    logging.info('Request finished with error, response code: %i %s'\
            % (response.status, response.reason))
    json_object = loads(response.read())
    logging.info('Error message: %s' % json_object['Error'])
    raise Exception('WAPI Error message: %s' % json_object['Error'])
    return json_object


def handle_success(response):
    '''
    If the action requested by the client was received, understood, accepted
    and processed successfully, print response code and return response body.
    '''
    logging.info('Request finished successfully with response code: %i %s'\
            % (response.status, response.reason))
    return response.read()
