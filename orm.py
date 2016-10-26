import sqlalchemy
from sqlalchemy import create_engine
import socket
if socket.gethostname() == 'sipoco':
    engine = create_engine(
        'mysql+pymysql://root:aiz1uvu0ibohKai4ohhu7aid deok3ohs7ieteeQua1shoosh@127.0.0.1/netwall_bot?charset=utf8',
        echo=False)
else:
    engine = create_engine('mysql+pymysql://root:1@127.0.0.1/netwall_bot?charset=utf8', echo=False)

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, Boolean

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    chat_id = Column(Integer)
    username = Column(String(50))
    first_name = Column(String(30))
    last_name = Column(String(30))
    mobile = Column(String(16))
    province = Column(String(32))
    city = Column(String(32))
    register_date = Column(Integer)
    comment = Column(String(200))

class Advertising(Base):
    __tablename__ = "advertisings"

    id = Column(Integer, primary_key=True)
    picture = Column(String(64))
    comment = Column(String(256))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="advertisings")


User.advertisings = relationship("Advertising", order_by=Advertising.id, back_populates="user")


Base.metadata.create_all(engine)

