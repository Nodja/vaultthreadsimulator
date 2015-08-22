from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey

db = SQLAlchemy()

class User(db.Model):
    """
    Contains all users.
    We separate users from posts so we can fetch a user at random.
    id is obviously not the forum user id
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    chain = None


class Post(db.Model):
    """
    Separate post from each user.
    We don't use the post number atm, but we might in the future.
    """
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer)
    number = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String)
