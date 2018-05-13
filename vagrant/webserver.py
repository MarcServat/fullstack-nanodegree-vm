from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import queries


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # list restaurants
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = queries.get_restaurants()
                output = """
                <html>
                    <body>
                        <h2>Restaurants</h2>
                        <a href='/restaurants/new'>Make a new restaurant</a>
                """
                for restaurant in restaurants:
                    output += "<p>%s</p>" % restaurant.name
                    output += """<a href='/restaurants/%s/edit'>
                    Edit</a><br>""" % restaurant.id
                    output += """<a 
                    href='/restaurants/%s/delete'>Delete</a>""" % restaurant.id
                output += """</body>
                </html>
                """
                self.wfile.write(output)
                return
            # Make new restaurant
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = """
                <html>
                    <body>
                    <h2>Make a new restaurant</h2>
                        <form   method='POST'
                                enctype='multipart/form-data'
                                action='/restaurants/new'>
                            <input name='newRestaurant' type='text'
                            placeholder='New Restaurant Name'>
                            <input type='submit' value='Create'>
                        <form>
                    </body>
                </html>"""
                self.wfile.write(output)
                return
            # Edit restaurants
            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurant_id = self.path.split("/")[2]

                output = """
                <html>
                    <body>
                    <h2>Edit a new restaurant</h2>
                        <form   method='POST'
                                enctype='multipart/form-data'
                                action='/restaurants/%s/edit'>
                            <input name='editRestaurant' type='text'
                            placeholder='Edit Restaurant Name'>
                            <input type='submit' value='Edit'>
                        <form>
                    </body>
                </html>""" % restaurant_id
                self.wfile.write(output)
                return
            # Delete restaurant
            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurant_id = self.path.split("/")[2]
                output = """
                <html>
                    <body>
                    <h2>Are you sure, Do you want to delete a restaurant</h2>
                        <form   method='POST'
                                enctype='multipart/form-data'
                                action='/restaurants/%s/delete'>
                            <input name='deleteRestaurant'
                            type='submit' value='Delete'>
                            <input type='submit' value='Cancel'>
                        <form>
                    </body>
                </html>""" % restaurant_id
                self.wfile.write(output)
                return
            
        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurant')
                    queries.add_restaurant(messagecontent[0])
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return
            if self.path.endswith("/edit"):        
                restaurant_id = self.path.split("/")[2]
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('editRestaurant')
                    queries.update_restaurant(messagecontent[0], restaurant_id)
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return
            
            if self.path.endswith("/delete"):        
                restaurant_id = self.path.split("/")[2]
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('deleteRestaurant')
                    queries.delete_restaurant(restaurant_id)
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
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
