################################################################################
# Copyright (c) 2017 Parker Crook - All Rights Reserved.
################################################################################
#Service
import logging, os, sys, time, subprocess, re
from dxlclient.callbacks import RequestCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Message, Request, Response
from dxlclient.service import ServiceRegistrationInfo

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
	class MyRequestCallback(RequestCallback):
		def on_request(self, request):
			# Extract information from request
			print "Service received request payload: " + request.payload.decode()
			# Create the response message
			res = Response(request)
			try:
				s = request.payload.decode()
				cmd = subprocess.Popen(re.split(r'\s+', s), stdout=subprocess.PIPE)
				cmd_out = cmd.stdout.read()
				# Process output
				res.payload = cmd_out.encode()
			except OSError:
				res.payload = 'Invalid command'.encode()
			# Send the response
			client.send_response(res)
	# Create service registration object
	info = ServiceRegistrationInfo(client, "myService")
	# Add a topic for the service to respond to
	info.add_topic(SERVICE_TOPIC, MyRequestCallback())
	# Register the service with the fabric (wait up to 10 seconds for registration to complete)
	client.register_service_sync(info, 10)
	logger.info("Command Service is running...")
	while True:
		time.sleep(60)
