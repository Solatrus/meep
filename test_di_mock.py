import sys, os, socket

if __name__ == '__main__':
    msg, interface, port = sys.argv[1:4]
    
    port = int(port)
    
    sock = socket.socket()
    
    sock.connect((interface,port))
    
    print "Connected to: ", interface, port
    
    print "Sending: " + msg
    print "Byte size of message: " + str(len(msg))
    
    sendmsg = msg + "\r\n\r\n"
    
    sock.sendall(str(len(sendmsg)) + ":" + sendmsg)
    
    print "Message received. Response: "
    
    response = sock.recv(4096)
    
    print (response,)
    
    
        