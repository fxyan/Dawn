from models.model_basic import SQLModel
from models.User import User


class Comment(SQLModel):
    def __init__(self, form):
        super().__init__(form)
        self.content = form.get('content', '')
        self.user_id = form.get('user_id', -1)
        self.weibo_id = form.get('weibo_id', -1)

    def user(self):
        u = User.one(id=self.user_id)
        return u

    @classmethod
    def add(cls, user_id, form):
        comment = cls.new(form)
        comment.update(comment.id, user_id=user_id)

    @classmethod
    def update_comment(cls, form):
        id = int(form.get('comment_id'))
        content = form.get('content')
        cls.update(id, content=content)

