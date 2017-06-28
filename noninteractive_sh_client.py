################################################################################
# Copyright (c) 2017 Parker Crook - All Rights Reserved.
################################################################################
# -*- coding: utf-8 -*-
#client
import logging, os, sys, argparse
from dxlclient.callbacks import RequestCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Message, Request, Response

parser = argparse.ArgumentParser(description="Sends command line arguments to any computers listening on the topic with the appropriate service.")
parser.add_argument("-c", default="ls", dest="command", help="The command to execute on the system running the service")
args = parser.parse_args()
if args.command == 0:
	print "Required paramenter missing.  Please supply -c <command>.  This command will be executed by the remote system"
	quit()
else:
	command = args.command

#Setup Logging
log_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

#[CONFIG OPTIONS]#
SERVICE_TOPIC = "/studentname/nc/service/nc"
CONFIG_FILE = "/usr/local/etc/opendxl/dxlclient.config"

config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

with DxlClient(config) as client:
    client.connect()
    # Create the request message
    req = Request(SERVICE_TOPIC)
    # Populate the request payload
    req.payload = command.encode()
    # Send the request and wait for a response (synchronous)
    res = client.sync_request(req)
    # Extract information from the response (if an error did not occur)
    if res.message_type != Message.MESSAGE_TYPE_ERROR:
        print "Client received response payload: \n" + res.payload.decode()
