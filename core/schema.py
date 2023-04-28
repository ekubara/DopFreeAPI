import datetime

# для таймзоны
import pytz as pytz

# импорт типов данных базы данных
from sqlalchemy import Column, DateTime, String, TEXT, Integer, ForeignKey

from sqlalchemy.ext.declarative import declarative_base

#
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String, unique=True)
    password = Column(String(200))
    datet = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __repr__(self):
        return 'id: {}, name: {}, age: {}, email: {}'.format(self.id, self.name, self.age, self.email)


class UserToken(Base):
    __tablename__ = 'tokens'
    token = Column(String, primary_key=True)
    userid = Column(ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'), unique=True)


class Habit(Base):
    __tablename__ = 'habits'
    id = Column(Integer, primary_key=True)
    userid = Column(ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'))
    name = Column(String)
    description = Column(TEXT)
    min_description = Column(TEXT)
    image = Column(TEXT, nullable=False, default='other_icon_155053')
    streak = Column(Integer)

    def __repr__(self):
        return 'id: {}, name: {}, userid: {}, streak: {}'.format(self.id, self.name, self.userid, self.streak)


class DefaultHabits(Base):
    __tablename__ = 'default_habits'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(TEXT)
    min_description = Column(TEXT)
    image = Column(TEXT)
    streak = Column(Integer)

    def __repr__(self):
        return 'id: {}, name: {}, userid: {}, streak: {}'.format(self.id, self.name, self.userid, self.streak)


class HabitComplited(Base):
    __tablename__ = 'habits_complited'
    id = Column(Integer, primary_key=True)
    userid = Column(ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    habitid = Column(ForeignKey(Habit.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    datet = Column(DateTime, nullable=False, default=datetime.datetime.now())


class UserComment(Base):
    # (Максимум 1 самочувствие за день от 1 юзера)
    __tablename__ = 'user_comment'
    id = Column(Integer, primary_key=True)
    userid = Column(ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'))
    comment = Column(TEXT)

    # (от нулья до двух)
    user_status = Column(Integer)

    datet = Column(DateTime, default=datetime.datetime.now(tz=pytz.timezone('Europe/London')))
