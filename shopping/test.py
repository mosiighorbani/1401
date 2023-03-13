from app import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

class users(db.Model):

    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String, nullable=False)
    userEmail = db.Column(db.String, nullable=False)
    userPhone = db.Column(db.String, nullable=False)
    userPass = db.Column(db.String, nullable=False)

    friendsR = db.relationship('friendships', backref='friendships.friend_id', primaryjoin='users.id==friendships.user_id', lazy='joined')

    def __init__(self, userName, userEmail, userPhone, userPass):
        self.userName = userName
        self.userEmail = userEmail
        self.userPhone = userPhone
        self.userPass = userPass

    def __repr__(self):
        return '{}-{}-{}-{}'.format(self.id, self.userName, self.userEmail, self.userPhone)

class friendships(db.Model):

    __tablename__ = "Friendships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)
    friend_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)

    userR = relationship('users', foreign_keys='friendships.user_id')
    friendR = relationship('users', foreign_keys='friendships.friend_id')

    def __init__(self, user_id, friend_id):
        self.user_id = user_id
        self.friend_id = friend_id


    def __repr__(self):
        return '{}-{}-{}-{}'.format(self.user_id, self.friend_id)


class bestFriends(db.Model):

    __tablename__ = "BestFriends"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)
    best_friend_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)

    user = relationship('users', foreign_keys='bestFriends.user_id')
    best_friend = relationship('users', foreign_keys='bestFriends.best_friend_id')


    def __init__(self, user_id, best_friend_id):

        self.user_id = user_id
        self.best_friend_id = best_friend_id


    def __repr__(self):
        return '{}-{}-{}-{}'.format(self.user_id, self.best_friend_id)


@app.route('/friendList<int:page>', methods=['GET', 'POST'])
@app.route('/friends')
def friendList(page=1):

if not session.get('logged_in'):
        return render_template('login.html')
    else:
        userID = session['user_id']

        userList = users.query.join(friendships).add_columns(users.id, users.userName, users.userEmail, friendships.user_id, friendships.friend_id).filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)

        return render_template(
            'friends.html', userList=userList)
