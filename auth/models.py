from app import db
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin





class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    email = Column(String(128), nullable=False, unique=True)
    username = Column(String(100), nullable=True, unique=True)
    password = Column(String(128), nullable=False, unique=False)
    role = Column(Integer(), nullable=False, default=2)
    name = Column(String(128), nullable=True, unique=False)
    phone = Column(String(11), nullable=True, unique=True)
    phone_auth = Column(Boolean(), default=False)
    active = Column(Boolean(), default=True)
    avatar = Column(String(150), default='img/avatar.png')
    education = Column(String(150), default='')
    about_me = Column(String(300), default = '')
    skills = Column(String(200), default='')
    address = Column(String(200), default='')
    token = Column(String(150), default='')

    def __repr__(self):
        return f'{self.name} by {self.email}'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == 0

    def is_follow(self, user_id1, user_id2):
        from social.models import Follower
        response = Follower.query.filter_by(follow_from=user_id1,follow_to=user_id2).first()
        return True if response != None else False 
    
    def post_likes(self, user_id):
        from social.models import SocialLike
        return SocialLike.query.filter_by(user_id=user_id).all()
    
    def is_admin(self):
        return self.role <= 1
        
