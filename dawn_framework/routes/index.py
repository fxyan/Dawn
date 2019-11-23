from .routes_basic import (
    current_user,
    redirect,
    html_response,
)

from models.User import User
from urllib.parse import unquote_plus


def route_login(request):
    form = request.form()
    user, session_id, result = User.login(form)
    header = {'Set-Cookie': 'session_id={}'.format(session_id)}
    return redirect('/?result={}'.format(result), headers=header)


def route_index_view(request):
    u = current_user(request)
    result = request.query.get('result', '')
    result = unquote_plus(result)
    return html_response('index.html', username=u.username, result=result)


def route_register_view(request):
    result = request.query.get('result', '')
    result = unquote_plus(result)
    return html_response('register.html', result=result)


def route_register(request):
    form = request.form()
    user, result = User.register(form)
    return redirect('/register/view?result={}'.format(result))


def route_dict():
    d = {
        '/login': route_login,
        '/': route_index_view,
        '/register/view': route_register_view,
        '/register': route_register,
    }
    return d
