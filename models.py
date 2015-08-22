from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///simulator.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)


class Post(Base):
    __tablename__ = 'post'
    thread_id = Column(Integer, primary_key=True)
    number = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    content = Column(String)

Base.metadata.create_all(engine)