import os, sys, json, requests, time
from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlclient.service import ServiceRegistrationInfo
from dxlclient.callbacks import RequestCallback
from dxlclient.message import Request, Response
# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)
SERVICE_TOPIC = "/open/service/ticket"

def openticket(msg):
    xmlpayload = '<?xml version="1.0" encoding="UTF-8"?><ticket alert="true" autorespond="true" source="API"> \
        <name>Angry User</name> \
        <email>api@osticket.com</email> \
        <subject>Testing API</subject> \
        <message type="text/plain"><![CDATA[%s]]></message> \
        </ticket>' %msg
    URL = "https://<YOURURIHERE>/api/tickets.xml"
    API_KEY = "<YOURAPIKEYHERE>" #passed as X-API-Key
    headers = {
        'X-API-Key': API_KEY
    }
    r = requests.post(URL, xmlpayload, headers=headers)
    return r.text

with DxlClient(config) as client:
    # Connect to the fabric
    client.connect()
    print "Connected to DXL"
    class tickethandler(RequestCallback):
        def on_request(self, request):
            print "Received request %s" %request.payload
            res = Response(request)
            res.payload = openticket(request.payload)
            print "Received Response from Service: %s" %res.payload
            client.send_response(res)
    info = ServiceRegistrationInfo(client, SERVICE_TOPIC)
    info.add_topic(SERVICE_TOPIC, tickethandler())
    client.register_service_sync(info, 10)
    while True:
        time.sleep(60)
