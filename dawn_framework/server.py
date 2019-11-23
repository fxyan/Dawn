import socket
import urllib.parse

from utils import log

from routes.routes_basic import (
    error,
)
from routes.index import route_dict as index
from routes.weibo import route_dict as weibo


class BaseRequest(object):
    def __init__(self):
        self.body = ''
        self.method = ''
        self.path = ''
        self.query = {}
        self.headers = {}
        self.cookies = {}

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f


class Request(BaseRequest):
    def __init__(self, raw_data):
        super().__init__()
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.parse_path(path)
        log('请求 path 和 query', self.path, self.query)

        self.add_headers(h[1:])
        log('请求 headers', self.headers)
        log('请求 cookies', self.cookies)

    def add_headers(self, header):
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            parts = cookies.split('; ')
            for part in parts:
                k, v = part.split('=', 1)
                self.cookies[k] = v

    def parse_path(self, path):
        index = path.find('?')
        if index == -1:
            self.path = path
            self.query = {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            self.path = path
            self.query = query


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        if len(r) < buffer_size:
            return request


def response_for_path(request, route):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    # 注册外部的路由
    response = route.get(request.path, error)
    return response(request)


def process_connection(connection, route):
    with connection:
        r = request_from_connection(connection)
        log('http 请求:<\n{}\n>'.format(r.decode()))
        r = r.decode()
        if len(r) > 0:
            request = Request(r)
            response = response_for_path(request, route)
            index = response.find(b'Content-Type: text/html')
            if index == -1:
                start = response.find(b'\r\n\r\n')
                gif_length = len(response[start:])
                gif_header = response[:start]
                log('http 响应头部: <{}> 内容长度：<{}>'.format(gif_header, gif_length))
            else:
                log("http 响应:<\n{}\n>".format(response.decode()))
            connection.sendall(response)
        else:
            connection.sendall(b'')


def run(host, port, route):
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('请求 ip 和 端口 <{}>\n'.format(address))
            process_connection(connection, route)


if __name__ == '__main__':
    # 生成配置并且运行程序
    route = {}
    route.update(index())
    route.update(weibo())
    config = dict(
        host='localhost',
        port=3000,
        route=route,
    )
    run(**config)

# class WsgiRequest(BaseRequest):
#     def __init__(self, environ):
#         super().__init__()
#         self.raw = environ
#         self.path = environ['PATH_INFO']
#         self.add_query(environ['QUERY_STRING'])
#         log('请求 path 和 query', self.path, self.query)
#         from gunicorn.http.body import Body
#         body: Body = environ['wsgi.input']
#         log('body', body.read())
#         self.body = body.read().decode(encoding='utf-8')
#         self.headers = environ
#         self.cookies = {}
#         self.add_cookie(environ.get('HTTP_COOKIE', ''))
#         log('请求 headers', self.headers)
#         log('请求 cookies', self.cookies)
#
#
#     def add_query(self, raw_query):
#         if len(raw_query) > 0:
#             args = raw_query.split('&')
#             query = {}
#             for arg in args:
#                 k, v = arg.split('=')
#                 query[k] = v
#             self.query = query
#
#     def add_cookie(self, raw_cookie):
#         if len(raw_cookie) > 0:
#             parts = raw_cookie.split('; ')
#             for part in parts:
#                 k, v = part.split('=', 1)
#                 self.cookies[k] = v
#
#
# class WsgiResponse(object):
#     def __init__(self, raw_data: bytes):
#         data = raw_data.decode(encoding='utf-8')
#         raw_header, self.body = raw_data.split(b'\r\n\r\n', 1)
#         header = raw_header.decode()
#         h = header.split('\r\n')
#
#         parts = h[0].split()
#         self.status = '{} {}'.format(parts[1], parts[2])
#         log('响应状态', self.status)
#
#         self.headers = {}
#         self.add_headers(h[1:])
#         log('响应 headers', self.headers)
#
#     def add_headers(self, header):
#         """
#         Cookie: user=gua
#         """
#         lines = header
#         for line in lines:
#             k, v = line.split(': ', 1)
#             self.headers[k] = v
#
#
# def configured_wsgi_app(route):
#     def wsgi_app(environ, start_response):
#         log('raw environ request', environ)
#         request = WsgiRequest(environ)
#         raw_response = response_for_path(request, route=route)
#         response = WsgiResponse(raw_response)
#         log('response', response.status, response.headers, response.body)
#         # data = b"Hello, World!\n"
#         # start_response("200 OK", [
#         #     ("Content-Type", "text/plain"),
#         #     ("Content-Length", str(len(data)))
#         # ])
#         data = response.body
#         headers = list(response.headers.items())
#         status = response.status
#         start_response(status, headers)
#         return iter([data])
#
#     return wsgi_app
