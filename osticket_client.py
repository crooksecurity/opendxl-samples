import logging, sys, os, time, threading
from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Message, Request, Response
# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)
SERVICE_TOPIC = "/open/service/ticket"
EVENT_TOPIC = "/open/threat/physical/DC/cabinets"

config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)
log_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

with DxlClient(config) as client:
    client.connect()
    print "Connected to DXL"
    class cabinet(EventCallback):
        def on_event(self, event):
            eventpayload = event.payload
            print "Received event %s" %eventpayload
            thread = threading.Thread(target=self.ticket, args=[eventpayload])
            thread.start()
        def ticket(self, msg):
            print "Filing ticket..."
            req = Request(SERVICE_TOPIC)
            req.payload = msg
            res = client.sync_request(req)
            if res.message_type != Message.MESSAGE_TYPE_ERROR:
                print "Create Ticket Number %s" %res
    client.add_event_callback(EVENT_TOPIC, cabinet())
    while True:
        time.sleep(60)
