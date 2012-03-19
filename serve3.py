import cgi, meep_example_app, time, meepcookie, sys, socket, threading

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
        try:
            while 1:
                incoming = sock.recv(1)
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
            path = protocol[1].split('?')
            environ['PATH_INFO'] = path[0]
            if len(path) > 1:
                environ['QUERY_STRING'] = path[1]
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
    
    sock.setblocking(0)

    connections = []
    while 1:
        try:
            print 'Waiting for HTTP Request...'
            (client_sock, client_address) = sock.accept()
            print 'Got connection', client_address
            client_sock.setblocking(0)
            connections.append((client_sock, client_address))
        except socket.error:
            pass
            
        open_connections = []
        for (client_sock, client_address) in connections:
            print 'Processing response for', client_address
            do_connection = handle_connection(client_sock)
            
            if not do_connection:
                open_connections.append((client_sock, client_address))
                
        connections = open_connections
