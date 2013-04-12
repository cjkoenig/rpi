# Inspired by http://fragments.turtlemeat.com/pythonwebserver.php

# Required libraries:
# -wiringPi: 
# > git clone git://git.drogon.net/wiringPi
# -rcswitch-pi: 
# > git clone https://github.com/r10r/rcswitch-pi.git
#
# It is required to install them first. After that, you will find the 
# send binary in the rcswitch-pi directory. This can be used to test your 
# wiring to the transmitter and/or in shell scripts (e.g. cron...). 
# Place this python script there after you configured it completely and 
# run 
# > sudo python webserver.py 
#
# Finally, access your rpi via browser and switch your sockets :-)

import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import call

class RequestHandler(BaseHTTPRequestHandler):
    
    #Configure your system here
    #==========================
    #DNS name or IP of your rpi:
    hostname = "rpi.fritz.box"
    #first five dip switches (same for all sockets):
    systemcode = '11111'
    #individual id of each socket:
    socket_ids = {'A': 11, 'B': 12, 'C': 13, 'D': 14}; 
    
    #answer to _every_ request, usually no configuration required
    html_answer = '<html><head><title>Power socket control</title></head>\
                   <body><form method="POST" enctype="multipart/form-data"\
                   action="http://' + hostname + '/"><table border="1" \
                   bordercolor="#FFCC00" style="background-color:#FFFFCC" \
                   width="100" cellpadding="3" cellspacing="3"><tr><th>\
                   A</th><th>B</th><th>C</th><th>D</th></tr><tr><td><input\
                   type="submit" name="A" value="on"></td><td><input \
                   type="submit" name="B" value="on"></td><td><input \
                   type="submit" name="C" value="on"></td><td><input \
                   type="submit" name="D" value="on"></td></tr><tr><td>\
                   <input type="submit" name="A" value="off"></td><td>\
                   <input type="submit" name="B" value="off"></td><td>\
                   <input type="submit" name="C" value="off"></td><td>\
                   <input type="submit" name="D" value="off"></td></tr>\
                   </table></form></body></html>'

    def do_GET(self):
        try:
            if self.path.endswith(""):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(RequestHandler.html_answer)
                return
            return
            
        except IOError:
            #Should never occur
            self.send_error(404,'File not found: %s' % self.path)

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
                command = {'on': 1, 'off': 0};
                call(['sudo','./send', RequestHandler.systemcode, \
                str(RequestHandler.socket_ids[query.keys()[0]]), \
                str(command[query.values()[0][0]])])

            #send reply
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(RequestHandler.html_answer)
            return
        
        except:
            pass

def main():
    try:
        server = HTTPServer(('', 80), RequestHandler)
        print 'starting httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

