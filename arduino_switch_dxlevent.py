################################################################################
# Copyright (c) 2017 Parker Crook - All Rights Reserved.
################################################################################
'''This is POC code to test using IOT devices to add to security detection capabilities
Using OpenDXL as a messaging bus to send a message, and an Arduino with a Grove Shield
with a switch to create an alert when the changes to 'open'. In testing, this switch
is connected to a datacenter cabinet. When the cabinet is open, the button/switch state
changes to open, sending an alert. Contact parker@crooksecurity.com with comments.

This code should work with any digital switch, but this code has only been tested on the
Grove "Magnetic Switch v1.2" & Grove "Button v1.2".
'''

import mraa, time, datetime
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Event

#[CONFIG OPTIONS]#
CONFIG_FILE = "/usr/local/etc/opendxl/dxlclient.config"
CABINET = "LV|R9"
button = mraa.Gpio(3)

EVENT_TOPIC = "/open/threat/physical/DC/cabinets"
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)
previousstate = ''
messagepayload = {}
with DxlClient(config) as client:
    client.connect()
    event = Event(EVENT_TOPIC)
    while True:
        if (button.read() == 0):
            currentstate = 0
        else:
            currentstate = 1
        if (currentstate != previousstate):
            messagepayload['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            messagepayload['location'] = CABINET
            if (currentstate == 0):
                messagepayload['alert'] = "Cabinet Opened!"
                event.payload = messagepayload
            #else:
            #    messagepayload['alert'] = "Cabinet Closed!"
            #    event.payload = messagepayload
            client.send_event(event)
            previousstate = currentstate
            time.sleep(1) #will wait 1 second between evaluating state changes.
