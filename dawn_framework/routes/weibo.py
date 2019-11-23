from .routes_basic import (
    current_user,
    redirect,
    html_response,
    login_required,
)

from models.Weibo import Weibo
from models.Comment import Comment


def weibo_index(request):
    u = current_user(request)
    res_u = request.query.get('user_id', '')
    if res_u != '':
        weibos = Weibo.all(user_id=int(res_u))
    else:
        weibos = Weibo.all(user_id=u.id)
    return html_response('weibo_index.html', weibos=weibos, user=u, res=res_u)


def add(request):
    form = request.form()
    u = current_user(request)
    Weibo.add(u.id, form)
    return redirect('/weibo')


def delete(request):
    weibo_id = int(request.query['weibo_id'])
    Weibo.delete(weibo_id)
    comments = Comment.all(weibo_id=weibo_id)
    for comment in comments:
        Comment.delete(comment.id)
    return redirect('/weibo')


def edit(request):
    weibo_id = int(request.query['weibo_id'])
    weibo = Weibo.one(id=weibo_id)
    return html_response('weibo_edit.html', weibo=weibo)


def update(request):
    form = request.form()
    Weibo.update_weibo(form)
    return redirect('/weibo')


def comment_add(request):
    form = request.form()
    u = current_user(request)
    Comment.add(u.id, form)
    return redirect('/weibo')


def comment_edit(request):
    comment_id = int(request.query['comment_id'])
    comment = Comment.one(id=comment_id)
    return html_response('comment_edit.html', comment=comment)


def comment_update(request):
    form = request.form()
    Comment.update_comment(form)
    return redirect('/weibo')


def comment_delete(request):
    comment_id = int(request.query['comment_id'])
    Comment.delete(comment_id)
    return redirect('/weibo')


def route_dict():
    d = {
        '/weibo': login_required(weibo_index),
        '/weibo/add': login_required(add),
        '/weibo/delete': login_required(delete),
        '/weibo/edit': edit,
        '/weibo/update': login_required(update),
        '/comment/add': login_required(comment_add),
        '/comment/edit': comment_edit,
        '/comment/update': login_required(comment_update),
        '/comment/delete': comment_delete,
    }
    return d