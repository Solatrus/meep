import cgi, meep_example_app, time, meepcookie, sys, socket

global _status
global _headers

def fake_start_response(status, headers):
    global _status
    _status = status
    global _headers
    _headers = headers

def handle_connection(sock):
    while 1:
        try:
            data = sock.recv(4096)
            if not data:
                break

            print 'Data recieved from: ', (sock.getsockname(),), '\n', (data,), '\n\n', 'Response:\n'
            
            meep_example_app.initialize()
            app = meep_example_app.MeepExampleApp()
            output = ""
            environ = {}
            
            lines = data.split('\n\r')

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
                    
            html = app(environ, fake_start_response)

            output += _status + '\n\r'
            responsehdrs = _headers[0]

            output += "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) + "\n\r"
            output += "Server: WSGIServer/0.1 Python/" + sys.version[:3] + "\n\r"

            output += responsehdrs[0] + ": " + responsehdrs[1] + "\n\r"

            output += "\n\r" + str(html[0]).strip('\n').strip('\r') + "\n\r"
            print output
            sock.send(output)

            if '.\r\n' in data:
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
