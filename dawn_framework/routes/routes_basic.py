import json
import os

from jinja2 import FileSystemLoader, Environment

from dawn_framework.utils import log
from models.User import User
from models.Session import Session


def current_user(request):
    if 'session_id' in request.cookies:
        log('request', request.headers)
        session_id = request.cookies['session_id']
        log('user', session_id)
        session = Session.one(session_id=session_id)
        user = User.one(id=session.user_id)
        return user
    else:
        log('user', User.guest())
        return User.guest()


# noinspection PyUnusedLocal
def error(request):
    return b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>'


def response_with_headers(headers, code=200):
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    header = 'HTTP/1.1 {} OK\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def redirect(url, result='', headers=None):
    if len(result) > 0:
        formatted_url = '{}?result={}'.format(
            url, result
        )
    else:
        formatted_url = url
    h = {
        'Location': formatted_url,
    }
    if isinstance(headers, dict):
        h.update(headers)
    r = response_with_headers(h, 302) + '\r\n'
    return r.encode()


def html_response(filename, **kwargs):
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    body = GuaTemplate.render(filename, **kwargs)
    r = header + '\r\n' + body
    return r.encode()


def json_response(data):
    headers = {
        'Content-Type': 'application/json',
    }
    header = response_with_headers(headers)
    body = json.dumps(data, indent=2, ensure_ascii=False)
    r = header + '\r\n' + body
    return r.encode()


def login_required(route_function):
    def f(request):
        log('login_required', route_function)
        u = current_user(request)
        if u.username == '【游客】':
            log('login_required is_guest', u)
            return redirect('/')
        else:
            return route_function(request)
    return f


def _initialized_environment():
    path = 'templates'
    log('initialized_environment', path, os.path.abspath(path))
    loader = FileSystemLoader(path)
    e = Environment(loader=loader)
    return e


class GuaTemplate:
    env = _initialized_environment()

    @classmethod
    def render(cls, filename, **kwargs):
        t = cls.env.get_template(filename)
        return t.render(**kwargs)
