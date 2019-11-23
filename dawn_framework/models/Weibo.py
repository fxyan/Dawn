from models.model_basic import SQLModel
from models.Comment import Comment
from utils import log


class Weibo(SQLModel):
    def __init__(self, form):
        super().__init__(form)
        self.content = form.get('content', '')
        self.user_id = form.get('user_id', -1)

    @classmethod
    def add(cls, user_id, form):
        weibo = cls.new(form)
        weibo.update(weibo.id, user_id=user_id)

    @classmethod
    def update_weibo(cls, form):
        weibo_id = form.get('weibo_id')
        content = form.get('content')
        cls.update(weibo_id, content=content)

    def comments(self):
        comments = Comment.all(weibo_id=self.id)
        return comments
