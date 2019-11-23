import hashlib
from .model_basic import SQLModel
from .Session import random_string, Session


class User(SQLModel):

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2

    @classmethod
    def validate_login(cls, form):
        username = form.get('username')
        password = form.get('password')
        password = cls.salted_password(password)
        user = User.one(username=username, password=password)
        if user is not None:
            return user
        return None

    @classmethod
    def login(cls, form):
        user = cls.validate_login(form)
        if user is not None:
            session = {
                'session_id': random_string(),
                'user_id': user.id,
            }
            Session.new(session)
            result = '登录成功'
        else:
            session = {
                'session_id': None,
            }
            result = '登陆失败'

        return user, session['session_id'], result

    @classmethod
    def salted_password(cls, password):
        salt = 'fjioewdksietewdf'
        salted = password + salt
        hashed = hashlib.sha256(salted.encode()).hexdigest()
        return hashed

    @classmethod
    def register(cls, form):
        user = cls(form)
        if user.validate_register():
            password = user.password
            hashed = cls.salted_password(password)
            user.password = hashed
            cls.new(user.__dict__)
            return user, '注册成功'

    @classmethod
    def guest(cls):
        form = {
            'id': -1,
            'username': '【游客】'
        }
        u = cls(form)
        print('u', u)
        return u
