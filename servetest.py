# Testing duplicate of serve.py specifically for nosetests

from meep_example_app import MeepExampleApp, initialize
from wsgiref.simple_server import make_server

initialize()
app = MeepExampleApp()

httpd = make_server('', 8080, app)
print "Serving HTTP on port 8080..."

# Respond to requests until process is killed
httpd.serve_forever()

# Alternative: serve one request, then exit
httpd.handle_request()
