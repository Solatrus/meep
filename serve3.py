import cgi, meep_example_app, time, meepcookie, sys, socket, threading, ResponseBuilder

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
        print 'Got connection', client_address
        t = threading.Thread(target=ResponseBuilder.handle_connection, args=(client_sock,))

        print 'Starting thread...'
        t.start()
