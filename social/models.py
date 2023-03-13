from app import db
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from auth.models import User
from jdatetime import datetime





class Follower(db.Model):
    __tablename__ = 'followers'
    id = Column(Integer(), primary_key=True)
    follow_from = Column(Integer(), ForeignKey('users.id'))
    follow_to = Column(Integer(), ForeignKey('users.id'))
    follow_date = Column(DateTime(), default=datetime.now())

    def __repr__(self):
        return f'user {self.follow_from} follows user{self.follow_to} in {self.follow_date} time.'
        # return f'{self.id}'
        
        
    

class Post(db.Model):
    __tablename__ = 'social_posts'
    id = Column(Integer(), primary_key=True)
    text = Column(String(500))
    user_id = Column(Integer(), ForeignKey('users.id'))
    comments = db.relationship('SocialComment', backref='post')
    created_at = Column(DateTime(), default=datetime.now())

    def __repr__(self):
        return f'{self.user_id} publish {self.text[:20]} in {self.created_at} time.'

    def get_writer(self, user_id):
        return User.query.get(user_id).name
    
    def get_avatar(self, user_id):
        return User.query.get(user_id).avatar
    
    def user_likes(self, post_id):
        users = []
        usrs = SocialLike.query.filter_by(post_id=post_id).all()
        for u in usrs:
            users.append(u.user_id)
        
        return users

    


class SocialComment(db.Model):
    __tablename__ = 'social_comments'
    id = Column(Integer(), primary_key=True)
    text = Column(String(500))
    user_id = Column(Integer(), ForeignKey('users.id'))
    post_id = Column(Integer(), ForeignKey('social_posts.id'))
    replies = db.relationship('SocialReply', backref='comment')
    date = Column(DateTime(), default=datetime.now())

    def __repr__(self) -> str:
        return f'{self.id} --> {self.text[:20]}'
    
    def getWriter(self, user_id):
        return User.query.get(user_id).name
    
    def getWriterAvatar(self, user_id):
        return User.query.get(user_id).avatar
    
    def getPost(self,post_id):
        return Post.query.get(post_id).text
    


class SocialReply(db.Model):
    __tablename__ = 'social_replies'
    id = Column(Integer(), primary_key=True)
    text = Column(String(500))
    user_id = Column(Integer(), ForeignKey('users.id'))
    post_id = Column(Integer(), ForeignKey('social_posts.id'))
    comment_id = Column(Integer(), ForeignKey('social_comments.id'))
    date = Column(DateTime(), default=datetime.now())

    def __repr__(self) -> str:
        return f'{self.id} --> {self.text[:20]}'
    
    def getWriter(self, user_id):
        return User.query.get(user_id).name
    
    def getWriterAvatar(self, user_id):
        return User.query.get(user_id).avatar
    
    def getPost(self,post_id):
        return Post.query.get(post_id).text
    
    def getComment(self, comment_id):
        return SocialComment.query.get_or_404(comment_id).text
    


class SocialLike(db.Model):
    __tablename__ = 'social_likes'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    post_id = Column(Integer(), ForeignKey('posts.id'))
    date = Column(DateTime(), default=datetime.now())

    def __repr__(self) -> str:
        return f'user{self.user_id} likes post {self.post_id}'
    
    
    
    