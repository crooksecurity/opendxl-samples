################################################################################
# Copyright (c) 2017 Parker Crook - All Rights Reserved.
################################################################################
#This code listens for events from the arduino_switch_dxlevent.py code. In its current form it is 
#simply POC code, and just prints the event details to stdout. 
#Contact parker@crooksecurity.com with comments.

import time, logging
from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Event

#[CONFIG OPTIONS]#
CONFIG_FILE = "/usr/local/etc/opendxl/dxlclient.config"
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
    class cabinet(EventCallback):
        def on_event(self, event):
            print event.payload
    client.add_event_callback(EVENT_TOPIC, cabinet())
    while True:
        time.sleep(60)
