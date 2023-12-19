from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, or_

Base = declarative_base()


class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender = Column(Integer, ForeignKey('users.id'))
    receiver = Column(Integer, ForeignKey('users.id'))
    message = Column(String)
    time = Column(DateTime)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)


class DBHandler:
    def __init__(self):
        self.engine = create_engine('sqlite:///msg_db.db', echo=True)
        Base.metadata.create_all(self.engine)

    def new_message(self, sender, receiver, message, time):
        with Session(self.engine) as s:
            s.add(Messages(sender=sender,
                           receiver=receiver,
                           message=message,
                           time=time))
            s.commit()

    def new_user(self, username, password):
        if self.get_user_id(username) != 0:
            return 0

        with Session(self.engine) as s:
            s.add(User(username=username,
                       password=password))
            s.commit()
        return self.get_user_id(username)

    def get_user_id(self, username):
        try:
            with Session(self.engine) as s:
                user = s.query(User).filter_by(username=username).first()
                return user.id
        except AttributeError:
            return 0

    def get_users(self, user_id=None):
        with Session(self.engine) as s:
            if user_id:
                return s.query(User).filter_by(id=user_id).first()
            else:
                return s.query(User).all()

    def check_password(self, username, password):
        try:
            with Session(self.engine) as s:
                user = s.query(User).filter_by(username=username).first()
                if user and user.password == password:
                    return True
                else:
                    return False
        except AttributeError:
            return False

    def get_chat(self, user1, user2):
        with Session(self.engine) as s:
            messages = s.query(Messages).filter(
                or_(
                    and_(Messages.sender == user1,
                         Messages.receiver == user2),
                    and_(Messages.sender == user2,
                         Messages.receiver == user1)
                )
            ).order_by(Messages.time).all()
            return [[self.get_users(message.sender).username,
                     message.message,
                     message.time] for message in messages]
