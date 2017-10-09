# OpenDXL Samples
This repository consists of sample scripts, and POC scripts that utilize OpenDXL for messaging that I have written for my own personal learning and use case development.  Projects are posted here for prosperity.

## Arduino Switch Event Generator
The concept is that an Arduino with a button or a magnetic switch could be used to detect when a cabinet is opened and send a message to a central logging location using OpenDXL. This project resulted in the creation of two scripts:

arduino_switch_dxlevent.py

arduino_switch_listener.py

## Non-Interactive Remote Shell
This concept was borrowed from netcat.  Where in netcat/nc, you can get a shell/reverse-shell over any protocol, here we're leveraging the existing protocol and communications in place by being an OpenDXL client.  The client sends a command to run on the host running the service; the service executes the command, and any stdout output is returned to the client.  This is not intended for production, and was only developed as a proof of concept, and to illustrate the load-balancing of DXL service requests (best demonstrated when you issue the 'hostname' command.  This project consists of the following scripts:

noninteractive_sh_client.py

noninsteractive_sh_service.py

## Checkpoint LEA / McAfee TIE & MAR Connector
This use case was written to address the consumption of Checkpoint LEA events on the DXL message bus, specifically on the following topic:
/open/threat/fw/checkpoint/threatemulation. For background please see https://supportcenter.checkpoint.com/supportcenter/portal?eventSubmit_doGoviewsolutiondetails=&solutionid=sk116678.

When a checpoint event is seen on the above topic, a MAR search will be executed looking for the MD5 hash, the SHA1 hash, or the filename on any hosts in the environment that have a MAR client, and subsequently tagging them with the value set in the ePO_TAG variable; in a separate thread, the MD5 will be set to malicious in the McAfee TIE database. 
