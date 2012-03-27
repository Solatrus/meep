import cgi, meep_example_app, time, meepcookie, sys, socket, StringIO, urllib, ResponseBuilder



if __name__ == '__main__':
    meep_example_app.initialize()
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
        ResponseBuilder.handle_connection(client_sock)
