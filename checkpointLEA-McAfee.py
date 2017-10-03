import logging, threading
from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlmarclient import MarClient
from dxlmarclient.constants import ProjectionConstants, ConditionConstants
from dxltieclient import TieClient
from dxltieclient.constants import HashType
from dxlepoclient import EpoClient

# Import common logging and configuration
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
#from common import *
CONFIG_FILE = "/usr/local/etc/opendxl/dxlclient.config"

# Configure local logger
log_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)
EVENT_TOPIC = "/open/threat/fw/checkpoint/threatemulation"

with DxlClient(config) as client:
    # Connect to the fabric
    client.connect()
    class CheckpointEvent(EventCallback):
        def on_event(self, event):
            evt = event.payload.decode() #read event... need to parse, or identify fields we'll use... thoughts below:
            print "Received Event: %s" %evt
            filedict = {"MD5": evt["filemd5"], "SHA1": evt["filehash"], "filename": evt["filename"]}
            thread = threading.Thread(target=self.mar_search, args=[filedict]) #MAR Search
            thread.start()
            if filedict["MD5"]:
                thread = threading.Thread(target=self.tie_set_rep, args=[filedict]) #TIE Reputation Set
                thread.start()

        #This function will use MAR to search all computers with MAR installed
	def mar_search(self, filedict):
            hostlist = []
            mar_client = MarClient(client)
            result_context = \
                mar_client.search(
                    projections=[
                        {
                            ProjectionConstants.NAME: "HostInfo",
                            ProjectionConstants.OUTPUTS: ["hostname", "ip_address"]
                        },
                        {
                            ProjectionConstants.NAME: "Files",
                            ProjectionConstants.OUTPUTS: ["dir", "name", "status"]
                        }],
                    conditions={
                        "or": [{
                            "and": [{
                                ConditionConstants.COND_NAME: "File",
                                ConditionConstants.COND_OUTPUT: "md5",
                                ConditionConstants.COND_OP: "EQUALS",
                                ConditionConstants.COND_VALUE: filedict["MD5"]
                            }]
                        }],
                        [{
                            "and": [{
                                ConditionConstants.COND_NAME: "File",
                                ConditionConstants.COND_OUTPUT: "name",
                                ConditionConstants.COND_OP: "EQUALS",
                                ConditionConstants.COND_VALUE: filedict["filename"]
                            }]
                        }]
		    }
                )
            if result_context.has_results:
                search_result = result_context.get_results(limit=5000)
                for item in search_result["items"]:
                    print "Host: %s, %s" %(item["output"]['HostInfo|hostname'], item["output"]['HostInfo|ip_address'])
                    print "--File: %s, %s, Status: %s" %(item["output"]['File|dir'], item["output"]['File|name'], item["output"]['File|status'])
		    hostlist.append(item["output"]['HostInfo|hostname'])
                hosts = ','.join(str(x) for x in hostlist)
                #apply tag to hosts
		thread = threading.Thread(target=self.epo_set_flag, args=[hosts, "CheckpointEvent"]) #ePO Tagging
		thread.start()
                
	#This function will take a list of hostnames and apply a tag to them.
	def epo_set_flag(self, hosts, tag):
            epo_client = EpoClient(client)
            res = epo_client.run_command("system.applyTag", {"names": hosts}, {"tagName": tag})
            res_dict = json.loads(res, encoding='utf-8')
            print json.dumps(res_dict, sort_keys=True, indent=4, separators=(',', ': '))

	#This function will set the reputation of an MD5 to known malicious.
        def tie_set_rep(self, filedict):

            tie_client = TieClient(client)
            #Should consider use case... and whether or not a lookup should be made for FP mitigation before setting a rep
            else:
                '''following code can replace the static reputation setting if CP reports on trusted & malicious files,
                or provides granularity'''
                #if checkpoint_trust == "Trusted":
                #    target_trustlevel = TrustLevel.KNOWN_TRUSTED
                #else:
                #    target_trustlevel = TrustLevel.KNOWN_MALICIOUS
                target_trustlevel = TrustLevel.KNOWN_MALICIOUS
                tie_client.set_file_reputation(
                    target_trustlevel, {
                        HashType.MD5: filedict["MD5"],
                        HashType.SHA1: filedict["SHA1"]
                    },
                    filename = filedict["filename"],
                    comment="Reputation set via Checkpoint Integration"
                )
                print "Reputations for %s set to %s" %(filedict["MD5"], target_trustlevel)
    client.add_event_callback(EVENT_TOPIC, CheckpointEvent())
    while True:
        time.sleep(60)
