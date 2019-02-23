import http.client
from jinja2 import Environment, PackageLoader
from web_server import make_server
# from jinja2 import Environment, FileSystemLoader
import os.path


class Dawn(object):
    def __init__(self, package_name):
        self.package_name = package_name
        self.jinjia_env = Environment(
            loader=PackageLoader(self.package_name, 'templates'),
            autoescape=True,
        )

    def render_templates(self, template, **options):
        template = self.jinjia_env.get_template(template).render(options)
        return Response([template])

    def error(self, request):
        return Response(['<h1>NOT FOUND</h1>'])

    def run(self, host='localhost', port=2000):
        http = make_server(host, port, self)
        http.run()

    def response_for_path(self, request, path):
        r = {
        }
        from route import route_dict
        r.update(route_dict)
        response = r.get(path, self.error)
        return response(request)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        response = self.response_for_path(request, request.path)

        start_response(
            response.status,
            response.items()
        )
        return iter(response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


class Request():
    def __init__(self, environ):
        self.environ = environ
        self.handle_request(self.environ)

    def handle_request(self, environ):
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']
        self.body = environ['BODY']
        self.query = self.handle_query(environ)

    def handle_query(self, environ):
        query_dict = {}
        if environ['QUERY_STRING']:
            query = environ['QUERY_STRING'].split('&')
            for args in query:
                k, v = args.split('=')
                query_dict[k] = v
        return query_dict

    def header(self, key):
        key = key.upper().replace('-', '_')
        if self.environ['HTTP_'+key]:
            return self.environ['HTTP_'+key]
        elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            return self.environ[key]
        return None


class Response():
    def __init__(self, response=None, status=200, charset='utf-8', content_type='text/html'):
        self.response = response if response is not None else []
        self.charset = charset
        self.status = status
        self.headers = self.handle_content_type(content_type)

    def handle_content_type(self, content_type):
        response_header = [
            ('Content-Type', str(content_type + '; ' + 'charset=' + self.charset)),
            ('Content-Length', str(len(self.response[0].encode(encoding=self.charset))))
        ]
        return response_header

    def items(self):
        return self.headers[:]

    def __iter__(self):
        for i in self.response:
            if isinstance(i, bytes):
                yield i
            else:
                yield i.encode(encoding=self.charset)

