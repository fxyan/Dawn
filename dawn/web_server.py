import socket
import selectors
import datetime
import sys


class EventLoop:
    def __init__(self, selector=None):
        if selector is None:
            selector = selectors.DefaultSelector()
        self.selector = selector

    def run_forever(self):
        while True:
            events = self.selector.select()
            for key, mask in events:
                if mask == selectors.EVENT_READ:
                    callback = key.data
                    callback(key.fileobj)
                else:
                    callback, msg = key.data
                    callback(key.fileobj, msg)


class WSGIEchoServer:

    application = None
    num = 0

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self._loop = loop
        self.s = socket.socket()
        self.request_dict = {}

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application

    def run(self):
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.s.listen(128)
        self.s.setblocking(False)
        self._loop.selector.register(self.s, selectors.EVENT_READ, self._accept)
        self._loop.run_forever()

    def _accept(self, sock):
        self.num += 1
        conn, addr = sock.accept()
        conn.setblocking(False)
        self._loop.selector.register(conn, selectors.EVENT_READ, self._handle_request)

    def _handle_request(self, conn):
        data = self.recv_data(conn)
        data = data.decode('utf-8')
        if len(data.split()) > 2:
            self._handle_http(data)
            env = self.get_env()
            app_data = self.application(env, self.start_response)
            self._loop.selector.modify(conn, selectors.EVENT_WRITE, (self.finish_response, app_data))
        else:
            self._loop.selector.unregister(conn)
            conn.close()

    def recv_data(self, conn):
        data = b''
        while True:
            msg = conn.recv(1024)
            data += msg
            if len(msg) < 1024:
                break
        return data

    def _handle_http(self, data):
        self.path = data.split()[1]
        self.query = ''
        if self.path.find('?') != -1:
            self.path, self.query = self.path.split('?', 1)
        self.url_scheme = data.split()[2].split('/')[0]
        self.method = data.split()[0]
        self.body = data.split('\r\n\r\n')[1]
        self.add_header(data.split('\r\n\r\n')[0].split('\r\n')[1:])

    def add_header(self, data):
        for msg in data:
            k, v = msg.split(':', 1)
            self.request_dict[k] = v

    def get_env(self):
        env = {}
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = self.url_scheme
        env['wsgi.input'] = sys.stdin
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        env['REQUEST_METHOD'] = self.method
        env['PATH_INFO'] = self.path  # /hello
        env['SERVER_NAME'] = self.host  # localhost
        env['SERVER_PORT'] = str(self.port)  # 8888
        env['QUERY_STRING'] = self.query
        if self.body:
            env['BODY'] = self.body
        env['BODY'] = ''
        if self.request_dict.get('content-type') is None:
            env['CONTENT_TYPE'] = 'text/plain'
        else:
            env['CONTENT_TYPE'] = self.request_dict['content-type']

        length = self.request_dict.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        for k, v in self.request_dict.items():
            k=k.replace('-','_').upper(); v=v.strip()
            if k in env:
                continue                    # skip content length, type,etc.
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v

        return env

    def start_response(self, status, response_headers, exc_info=None):
        headers = [
            ('Date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('Server', 'RAPOWSGI0.1'),
        ]
        self.status = status
        self.headers = response_headers + headers

    def finish_response(self, conn, app_data):
        response = 'HTTP/1.1 {}\r\n'.format(self.status)
        for header in self.headers:
            response += '{}: {}\r\n'.format(header[0], header[1])
        response += '\r\n'
        response = response.encode(encoding=('utf-8'))
        for data in app_data:
            response += data
        conn.sendall(response)
        self._loop.selector.unregister(conn)
        conn.close()
        self.num -= 1


def make_server(address, port, application):
    event_loop = EventLoop()
    echo_server = WSGIEchoServer(address, port, event_loop)
    echo_server.set_app(application)
    return echo_server


if __name__ == '__main__':
    pass
    # module = 'flask_demo'
    # module = __import__(module)
    # app = 'app'
    # app = getattr(module, app)
    # print('app', app)
    # http = make_server('localhost', 2000, app)
    # http.run()
    # echo_server.set_app(app)
