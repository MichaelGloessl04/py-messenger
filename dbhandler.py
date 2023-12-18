from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

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

    def get_users(self, user_id=None):
        with Session(self.engine) as s:
            if user_id:
                users = s.query(User).filter_by(id=user_id).one()
            else:
                users = s.query(User).all()
            return users

    def get_chat(self, user1, user2):
        with Session(self.engine) as s:
            messages = s.query(Messages).filter_by(
                sender=user1,
                receiver=self.get_user_id(user2)).all()
            messages += s.query(Messages).filter_by(
                sender=self.get_user_id(user2),
                receiver=user1).all()
            messages.sort(key=lambda x: x.time)
            return messages
