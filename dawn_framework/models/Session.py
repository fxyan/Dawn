from .model_basic import SQLModel
import time, random


class Session(SQLModel):
    """
    Session 是用来保存 session 的 model
    """

    def __init__(self, form):
        super().__init__(form)
        self.session_id = form.get('session_id', '')
        self.user_id = form.get('user_id', -1)


def random_string():
    string = 'fjewijgohwuidhfkmkewguiew'
    s = ''
    for i in range(16):
        x = random.randint(0, len(string)-2)
        s += string[x]
    return s
