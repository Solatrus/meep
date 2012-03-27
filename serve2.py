import cgi, meep_example_app, time, meepcookie, sys, socket, StringIO, urllib

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
                incoming = sock.recv(1)

                if not incoming:
                    break

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
            output = []
            environ = {}
            
            lines = data.split('\r\n')
            

            protocol = lines[0].split(' ')

            environ['REQUEST_METHOD'] = protocol[0]
            path = protocol[1].split('?')
            environ['PATH_INFO'] = path[0]
            if len(path) > 1:
                environ['QUERY_STRING'] = path[1]
            environ['SERVER_PROTOCOL'] = protocol[2]

            output.append(protocol[2].strip() + " ")
            
            post = {}
            postin = ""
            postkey = ""
            postval = ""

            for line in lines:
                print line
                line = line.lower()
                linedata = str(line).split(": ")
                if linedata[0] == "referer":
                    environ['SCRIPT_NAME'] = linedata[1]
                elif linedata[0] == "cookie":
                    environ['HTTP_COOKIE'] = linedata[1]
                elif (protocol[0] == "POST" and linedata[0] == "content-length"):
                    #
                    i = 0
                    if int(linedata[1]) > 0:
                        readCount = int(linedata[1])
                        while (i < readCount):
                            incoming = sock.recv(1)
                            if incoming == "=":
                                postkey = postin
                                postin = ""
                                incoming = sock.recv(1)
                                i += 1
                            elif incoming == '&':
                                postval = postin
                                post[postkey] = postval
                                postin = ""
                                incoming = sock.recv(1)
                                i += 1
                            
                            if not incoming:
                                break
                                
                            postin = postin + incoming
                                
                            i += 1

                        if postin:
                            postval = postin
                        else:
                            postval = ""
                            
                        post[postkey] = postval

                        print post

                        s = urllib.urlencode(post)
                        
                        environ['wsgi.input'] = StringIO.StringIO(s)
            
            #print post
                    
            print "Response:\n"
            
            #print environ
            
            response = ResponseObj()
                    
            html = app(environ, response.start_response)

            #print '***********************\n', response.status_code, '\n************************'

            output.append(response.status_code + '\r\n')

            # If it's a 302 response, there's a 3rd header
            #if response.status_code == "302 Found":
            #output.append(response.headers[2][0] + ": " + response.headers[2][1] + "\r\n")

            output.append("Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) + "\r\n")
            output.append("Server: WSGIServer/0.1 Python/" + sys.version[:3] + "\r\n")

            for headerline in response.headers:
                output.append(headerline[0] + ": " + headerline[1] + "\r\n")

            #if (protocol[0] == "GET"):
            output.append("\r\n" + str(html[0]).strip('\n').strip('\r') + "\r\n")
            #elif (protocol[0] == "POST"):
                #output.append(post + "\r\n")

            final = "".join(output)
            print final
            
            sock.send(final)

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
