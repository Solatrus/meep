import cgi, meep_example_app, time, meepcookie, sys, socket

class ResponseObj:
    def __init__(self):
        self.status_code = None
        self.headers = None
    def start_response(self, status, headers):
        self.status_code = status
        self.headers = headers

def handle_connection(sock):
    while 1:
        data = None
        query = None
        headerdone = False
        try:
            while 1:
                incoming = sock.recv(2)

                if (data == None):
                    data = incoming
                else:
                    data = data + incoming
                    
                if "\r\n\r\n" == data[-4:]:
                    break

            if not data:
                break

            print 'Data recieved from: ', sock.getsockname(), '\n'
            
            meep_example_app.initialize()
            app = meep_example_app.MeepExampleApp()
            output = ""
            environ = {}
            
            lines = data.split('\r\n')
            

            protocol = lines[0].split(' ')

            environ['REQUEST_METHOD'] = protocol[0]
            path = protocol[1].split('?')
            environ['PATH_INFO'] = path[0]
            if len(path) > 1:
                environ['QUERY_STRING'] = path[1]
            environ['SERVER_PROTOCOL'] = protocol[2]

            output += protocol[2].strip() + " "
            
            post = ''

            for line in lines:
                print line
                line = line.lower()
                linedata = str(line).split(": ")
                if linedata[0] == "referer":
                    environ['SCRIPT_NAME'] = linedata[1]
                elif linedata[0] == "cookie":
                    environ['HTTP_COOKIE'] = linedata[1]
                elif linedata[0] == "content-length":
                    if int(linedata[1]) > 0:
                        print "Input found"
                        while 1:
                            incoming = sock.recv(2)
                            if not incoming:
                                break
                                
                            post = post + incoming
                            
                            print post
                                
                            if len(incoming) < 2:
                                break
                        
                        environ['wsgi.input'] = post
            
            print post
                    
            print "Response:\n"
            
            print environ
            
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

            if "\r\n\r\n" == data[-4:]:
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
