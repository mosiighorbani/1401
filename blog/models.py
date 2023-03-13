from jdatetime import datetime
from app import db
from sqlalchemy import Column, ForeignKey, Text, Integer, String, Boolean, DateTime, event, Table
from auth.models import User
from slugify import slugify





# post_like = Table('posts-likes', db.metadata,
#     Column('post_id', Integer(), ForeignKey('posts.id', ondelete='cascade')),
#     Column('user_id', Integer(), ForeignKey('users.id', ondelete='cascade'))
#     )




class Post(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer(), primary_key=True)
    title = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False)
    content = Column(Text(), nullable=False)
    image = Column(String(100), nullable=False)
    publish = Column(Boolean(), default=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    views = Column(Integer(), default=0)
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now())
    # user_like_id = db.relationship('User', secondary=post_like, back_populates='posts')
    # likes = Column(Integer(), ForeignKey('postlikes.id'))
    # likes = db.relationship('PostLikes', backref='post', lazy='dynamic')
    likes = db.relationship('PostLikes', backref='post')
    comments = db.relationship('Comment', backref='post')

    def __repr__(self):
        return f'{self.title} as {self.user_id}'

    def getWriter(self, id):
        return User.query.get(id).name

    @staticmethod
    def generate_slug(cls, value, oldvalue, initiator):
        if value and (not cls.slug and value != oldvalue):
            cls.slug = slugify(value, allow_unicode=True)



class Comment(db.Model):
    __tablename__ = 'comments'
    id = Column(Integer(), primary_key=True)
    body = Column(String(200), nullable=False)
    publish = Column(Boolean(), default=False)
    created_at = Column(DateTime(), default=datetime.now())
    post_id = Column(Integer(), ForeignKey('posts.id'))
    user_id = Column(Integer(), ForeignKey('users.id'))
    replies = db.relationship('Reply', backref='comment')

    def __repr__(self):
        return f'comment {self.body[:20]} for {self.post_id}'

    def getWriter(self, id):
        return User.query.get(id).name

    def getWriterAvatar(self, id):
            return User.query.get(id).avatar




class Reply(db.Model):
    __tablename__ = 'replies'
    id = Column(Integer(), primary_key=True)
    body = Column(String(200), nullable=False)
    publish = Column(Boolean(), default=False)
    created_at = Column(DateTime(), default=datetime.now())
    comment_id = Column(Integer(), ForeignKey('comments.id'))
    user_id = Column(Integer(), ForeignKey('users.id'))

    def __repr__(self):
        return f'reply {self.id} for comment {self.comment_id} by {self.user_id}'

    def getWriter(self, id):
        return User.query.get(id).name

    def getWriterAvatar(self, id):
            return User.query.get(id).avatar




class PostLikes(db.Model): # when a user like a post
    __tablename__ = 'postlikes'
    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime(), default=datetime.now())
    post_id = Column(Integer(), ForeignKey('posts.id'))
    user_id = Column(Integer(), ForeignKey('users.id'))

    def __repr__(self):
        return f'user {self.user_id} likes post{self.post_id}'

    def get_user_id(self):
        return self.user_id
        







db.event.listen(Post.title, 'set', Post.generate_slug, retval=False)
