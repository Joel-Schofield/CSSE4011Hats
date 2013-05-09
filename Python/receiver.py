from socket import *
from struct import unpack
 
UDPSock = socket(AF_INET6,SOCK_DGRAM)
UDPSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
UDPSock.bind(("",4321)) 
 
while True:
    data,addr = UDPSock.recvfrom(1024)
    if not data:
        print "Client has exited!"
        break
    else:
        print "\nReceived message from"
 
# Close socket
UDPSock.close()

