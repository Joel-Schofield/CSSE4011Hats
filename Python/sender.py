from socket import *
from struct import pack
 
UDPSock = socket(AF_INET6,SOCK_DGRAM)
address = raw_input("Enter mote ip address:")
UDPSock.connect((address,1234))
led = pack('xB',int(raw_input("Enter red: "))
			   ,int(raw_input("Enter Green: "))
			   ,int(raw_input("Enter Blue: ")))
UDPSock.send(led)
