import cgi, meep_example_app, time, meepcookie, sys

# Use python miniapp.py filename-request.txt and you'll get filename-response.txt in the same directory

global _status
global _headers

def fake_start_response(status, headers):
    global _status
    _status = status
    global _headers
    _headers = headers

fp = open(sys.argv[1],"rb")

f = sys.argv[1].split('-')

filename = f[0]

lines = fp.readlines()

app = MeepExampleApp()

output = ""

environ = {}
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

output += _status + '\n'
responsehdrs = _headers[0]

output += "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) + "\n"
output += "Server: WSGIServer/0.1 Python/" + sys.version[:3] + "\n"

output += responsehdrs[0] + ": " + responsehdrs[1] + "\n"

output += "\n" + str(html[0]).strip('\r\n').strip('\t') + "\n"

outputFile = filename + "-response.txt"

fp = open(outputFile, 'wb')
fp.write(output)