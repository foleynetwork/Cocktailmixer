import BaseHTTPServer
import CGIHTTPServer
import cgitb; cgitb.enable()

def hmm():
    print "hmm"

class RequestsHandler(CGIHTTPRequestHandler):
    cgi_directories = ["/"] #to run all scripts in '/www' folder
    def do_GET(self):
        try:
            f = open(curdir + sep + '/www' + self.path)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except IOError:
            self.send_error(404, "Page '%s' not found" % self.path)

def Test():
    server = BaseHTTPServer.HTTPServer
    handler = CGIHTTPServer.CGIHTTPRequestHandler
    server_address = ("", 8000)
    handler.cgi_directories = ["/"]
 
    httpd = server(server_address, handler)
    httpd.serve_forever()

Test()


