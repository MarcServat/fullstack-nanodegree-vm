from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import queries


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurant"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = queries.get_restaurants()
                output = """
                <html>
                    <body>
                        <h2>Hello</h2>
                """
                for restaurant in restaurants:
                    output += "<p>%s</p>" % restaurant.name
                output += """</body>
                </html>
                """
                self.wfile.write(output)
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hola!</body></html>"
                self.wfile.write(output)
                return
        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
                output = """
                <html>
                    <body>
                        <h2>Okay, how about this: </h2>
                        <h1> %s </h1>
                        <form method='POST' enctype='multipart/form-data'
                        action='/hello'>
                            <h2>What would you like me to say?</h2>
                            <input name='message' type='text'>
                            <input type='submit' value='Submit'>
                        </form>
                    </body>
                </html>
                """ % messagecontent[0]
                self.wfile.write(output)
                return
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()