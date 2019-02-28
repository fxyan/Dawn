from jinja2 import Environment, PackageLoader
from web_server import make_server
from urls.resolvers import re_route
import logging


logging.basicConfig(level=logging.INFO,
                    filename='output.log',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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
        return Response(['<h1>NOT FOUND</h1>'], 404)

    def handle(self, path, r):
        path = path.split('/')
        for url in r:
            url_list = url.split('/')
            if len(url_list) == len(path):
                self.match(path, url_list)

    def match(self, path, url_list):
        result = {}
        if len(url_list) == len(path):
            for i in range(len(url_list)):
                result = {}
                if url_list[i][0] == '<' and url_list[i][-1] == '>':
                    utype, var = url_list[i][1:-1].split(':')
                    try:
                        result[var] = utype(path[i])
                    except Exception as e:
                        logging.error('')

        return

    def run(self, host='localhost', port=2000):
        http = make_server(host, port, self)
        http.run()

    def response_for_path(self, request, path):
        r = {
        }
        from route import route_dict
        r.update(route_dict)
        path, kwarg = re_route(path, r)
        response = r.get(path)
        # print('debug', response(request, **kwarg))
        try:
            if response is None:
                logging.warning('Invalid routing address {}'.format(path))
                response = self.error
                return response(request)
            return response(request, **kwarg)
        except Exception as e:
            logging.error('The routing application has errors', exc_info=True)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.response_for_path(request, request.path)
        print('debug', response)
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

