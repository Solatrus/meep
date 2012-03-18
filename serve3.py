import cgi, meep_example_app, time, meepcookie, sys, socket, thread

class ResponseObj:
    def __init__(self):
        self.status_code = None
        self.headers = None
    def start_response(self, status, headers):
        self.status_code = status
        self.headers = headers
        
def broadcast_data(sock, message):
    global CONNECTIONS
    
    for socket in CONNECTIONS:
        if socket != sock:
            socket.send(message)
            
def accept_connetion():
    global CONNECTIONS, BUFFER
    
    try:
        while 1:
            threadlock.acquire()
            
            try:
                sockfd, addr = server_socket.accept()
                sockfd.setblocking(0)
                CONNECTIONS.append(sockfd)
                print "Client (%s, %s) connected" % addr
                broadcast_data(sockfd, "Client (%s, %s) connected" % addr)
                
            except:
                pass
                
            threadlock.release()
            
    except:
        pass
        
def process_connection():
    global CONNECTIONS, BUFFER
    try:
        while 1:
            for sock in CONNECTIONS:
                threadlock.acquire()

                try:

                    data = sock.recv(BUFFER)
                    if data:
                        # The client sends some valid data, process it
                        if data == "q" or data == "Q":
                            broadcast_data(sock, "Client (%s, %s) quits" % sock.getpeername())
                            print "Client (%s, %s) quits" % sock.getpeername()
                            sock.close()
                            CONNECTIONS.remove(sock)
                        else:
                            broadcast_data(sock, data)
                except:
                    #Exception thrown, get the error code and do cleanup actions
                    socket_errorcode =  sys.exc_value[0]
                    if socket_errorcode == 10054:

                        # Connection reset by peer exception
                        # In Windows, sometimes when a TCP client program closes abruptly,
                        # or when you press Ctrl-C a "Connection reset by peer" exception will be thrown

                        broadcast_data(sock, "Client (%s, %s) quits" % sock.getpeername())
                        print "Client (%s, %s) quits" % sock.getpeername()
                        sock.close()
                        CONNECTIONS.remove(sock)
                    else:
                        # The socket is not ready for reading, which results in an exception,
                        # ignore this and pass on with the next client socket (without blocking)
                        # The exception you will see here is
                        # "The socket operation could not complete without blocking"
                        pass
                threadlock.release()

    except:
    #Handle the case when server program is terminated with Ctrl-C
    #catch the exception and exit
    pass
            

def handle_connection():
    global CONNECTIONS, BUFFER
    while 1:
        for sock in CONNECTIONS:
            
        data = None
        try:
            while 1:
                incoming = sock.recv(BUFFER)
                if (data == None):
                    data = incoming
                else:
                    data = data + incoming
                    
                
                if data[len(data)-4:] == "\r\n\r\n":
                    break

            if not data:
                break

            print 'Data recieved from: ', (sock.getsockname(),), '\n', (data,), '\n\n', 'Response:\n'
            
            meep_example_app.initialize()
            app = meep_example_app.MeepExampleApp()
            output = ""
            environ = {}
            
            lines = data.split('\r\n')

            protocol = lines[0].split(' ')

            environ['REQUEST_METHOD'] = protocol[0]
            environ['PATH_INFO'] = protocol[1]
            environ['SERVER_PROTOCOL'] = protocol[2]

            output += protocol[2].strip() + " "

            for line in lines:
                linedata = str(line).split(": ")
                if linedata[0] == "referer":
                    environ['SCRIPT_NAME'] = linedata[1]
                elif linedata[0] == "cookie":
                    environ['HTTP_COOKIE'] = linedata[1]
                    
            
            response = ResponseObj()
                    
            html = app(environ, response.start_response)

            output += response.status_code + '\r\n'
            responsehdrs = response.headers[0]

            output += "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) + "\r\n"
            output += "Server: WSGIServer/0.1 Python/" + sys.version[:3] + "\r\n"

            output += responsehdrs[0] + ": " + responsehdrs[1] + "\r\n"

            output += "\r\n" + str(html[0]).strip('\n').strip('\r') + "\r\n"
            print output
            
            sock.send(output)

            if data[len(data)-4:] == "\r\n\r\n":
                sock.close()
                break
        except socket.error:
            break

if __name__ == '__main__':
    interface, port = sys.argv[1:3]
    port = int(port)

    print 'Binding', interface, port
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(5)

    while 1:
        print 'Waiting for HTTP Request...'
        (client_sock, client_address) = sock.accept()
        print 'got connection', client_address
        handle_connection(client_sock)
