from sqlalchemy.types import Date
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Homework(Base):
    __tablename__ = 'homework'
    id = Column(Integer, primary_key=True)
    lesson = Column(String(40))
    date = Column(Date())
    task = Column(String(100))


class HomeworkRequest(Base):
    __tablename__ = 'homework_request'
    id = Column(Integer, primary_key=True)
    lesson = Column(String(50))
    user_id = Column(Integer)
    date = Column(Date())


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    lesson = Column(String(50))
    monday = Column(String(3))
    tuesday = Column(String(3))
    wednesday = Column(String(3))
    thursday = Column(String(3))
    friday = Column(String(3))


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    viber_id = Column(String(50))
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship('Groups')
    agreement = relationship('MailingAgreement', back_populates='user_rel')


class Groups(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    access = relationship("Users")


class MailingAgreement(Base):
    __tablename__ = 'mailing_agreement'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('users.user_id'))
    status = Column(String(25))
    user_rel = relationship("Users", back_populates="agreement")


def seek_user(viber_request, d_session):
    user = d_session.query(Users).filter_by(viber_id=viber_request.user.id)
    if not user:
        user = viber_request.user
        d_session.add(Users(username=user.name, viber_id=user.id, access=3))
        d_session.commit()


class DBRepository(object):
    def __init__(self, session):
        self.database_session = session

    def get(self, lesson, date):
        return self.database_session.query(Homework).filter_by(lesson=lesson, date=date).all()

    def insert(self, lesson, date, task):
        self.database_session.add(Homework(lesson=lesson, date=date, task=task))
        self.database_session.commit()

    def change(self, lesson, date, new_value):
        ob = self.database_session.query(Homework).filter_by(lesson=lesson, date=date)
        ob.update({'task': new_value})
        self.database_session.commit()

    def get_schedule(self, lesson):
        return self.database_session.query(Schedule).filter_by(lesson=lesson).first()

    def write_schedule(self, lesson, mon, tue, wed, thu, fri):
        self.database_session.add(Schedule(lesson=lesson, monday=mon, tuesday=tue, wednesday=wed, thursday=thu,
                                           friday=fri))
        self.database_session.commit()

    def change_schedule(self, lesson, field, new_value):
        self.database_session.query(Schedule).filter_by(lesson=lesson).update({field: new_value})
        self.database_session.commit()

    def change_access(self, user_id, access_level):
        self.database_session.query(Users).filter_by(user_id=user_id).update({'group_num': access_level})
        self.database_session.commit()

    def get_request_group(self):
        return self.database_session.query(MailingAgreement).all()

    def get_homework_requests(self, lesson, date):
        return self.database_session.query(HomeworkRequest).filter_by(lesson=lesson, date=date).all()

    def get_group_id(self, viber_request):
        return self.database_session.query(Users).filter_by(viber_id=viber_request).first().group_id

    def write_homework_request(self, lesson, date, user_id):
        self.database_session.add(HomeworkRequest(lesson=lesson, date=date, user_id=user_id))
        self.database_session.commit()

    def get_list_users(self):
        users = self.database_session.query(Users).all()
        username_list = (f'{user.username} | {user.user_id} | {user.group_id}' for user in users)
        return '\n'.join(username_list)

    def add_user(self, viber_id, username):
        self.database_session.add(Users(username=username, viber_id=viber_id, group_id=3))
        self.database_session.commit()
