from http.client import HTTPConnection

def http2wsgi(url):
    '''WSGI application that connects to a HTTP server and provides its API to a WSGI client.'''

    def wsgi(environ, start_response):
        my_headers = {}
        if 'CONTENT_LENGTH' in environ:
            my_headers['Content-Length'] = environ['CONTENT_LENGTH']

        if 'wsgi.input' in environ:
            body = b''.join(environ['wsgi.input'])
        else:
            body = b''

        conn = HTTPConnection(url)
        conn.request(environ['REQUEST_METHOD'], environ['PATH_INFO'],
                     headers=my_headers,
                     body=body)

        resp = conn.getresponse()
        body = resp.read()

        start_response('%i %s' % (resp.status, resp.reason), resp.getheaders())
        return [body]

    return wsgi
