import datetime

from core import User, UserToken, Habit, UserComment, HabitComplited, DefaultHabits

from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
import logging

from models.api_post_models import LogIn, RegUser, AddUserHabits, AddUserComment
# декоратор открытия сессии к базе данных и автокоммитит все
from utils.session_decorator import db_session_with
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession


class Repo:
    """Db abstraction layer
    Выдача пула по декоратору @db_session_with
    декоратор из селфа берет self.pool и отдает сессия в db_session: AsyncSession каждой функции
    """

    def __init__(self, pool):
        """тут себе записываем пул. а через декоратор мы октрываем соединение из пула поток"""
        self.pool = pool

    # USER
    @db_session_with
    async def _check_email_exists(self, email: str, db_session: AsyncSession):
        emails_iter = await db_session.execute(select(User).where(User.email == email))
        emails_all = emails_iter.all()
        if not emails_all:
            return False
        else:
            return emails_all[0]

    @db_session_with
    async def register_user(self, user: RegUser, db_session: AsyncSession):
        """Register user"""

        email_check = await self._check_email_exists(email=user.email)
        if not email_check:
            #
            await db_session.execute(
                insert(User).values(
                    {"name": user.name, "age": user.age, "email": user.email,
                     "password": user.password}).on_conflict_do_nothing())

            logging.info(f"+{user.email} has been added into database")

            return True
        else:
            return False

    @db_session_with
    async def update_user_data(self, email: str, values_dict, db_session: AsyncSession) -> bool:
        """update clients status is_banned"""
        # update db with user_id
        await db_session.execute(
            update(User).where(User.email == email).values(values_dict))
        return True

    @db_session_with
    async def get_user_byemail(self, email: str, db_session: AsyncSession):
        """Get client (account) from path"""
        # update db with user_id
        client_all = await db_session.execute(
            select(User).where(User.email == email))
        client_dict = client_all.all()
        if not client_dict:
            return
        client = client_dict[0][0]
        # get user models
        return client

    @db_session_with
    async def get_user_byid(self, id: int, db_session: AsyncSession):
        """Get client (account) from path"""
        # update db with user_id
        client_all = await db_session.execute(
            select(User).where(User.id == id))
        user_dict = client_all.all()
        if not user_dict:
            return
        user = user_dict[0][0]
        # get user models
        return user

    # UserToken
    @db_session_with
    async def _check_token_exists(self, token: str, db_session: AsyncSession):
        tokens_iter = await db_session.execute(select(UserToken).where(UserToken.token == token))
        tokens_all = tokens_iter.all()
        if not tokens_all:
            return False
        else:
            return tokens_all[0]

    @db_session_with
    async def register_user_token(self, userid, token: str, db_session: AsyncSession):
        """Register user"""
        token_check = await self._check_token_exists(token=token)

        if not token_check:
            await db_session.execute(
                insert(UserToken).values(
                    {"token": token, "userid": userid}).on_conflict_do_nothing())

            logging.info(f"{userid} created token")
            return True
        else:
            return False

    @db_session_with
    async def update_token(self, userid: int, token: str, db_session: AsyncSession) -> bool:
        """update clients status is_banned"""
        # update db with user_id
        await db_session.execute(
            update(UserToken).where(UserToken.userid == userid).values({'token': token}))
        return True

    @db_session_with
    async def get_token_byuserid(self, userid, db_session: AsyncSession):
        # update db with user_id
        tokens = await db_session.execute(
            select(UserToken).where(UserToken.userid == userid))
        tokens_all = tokens.all()
        if not tokens_all:
            return
        token = tokens_all[0][0]
        # get user models
        return token

    @db_session_with
    async def get_userid_bytoken(self, token, db_session: AsyncSession):
        # update db with user_id
        tokens = await db_session.execute(
            select(UserToken).where(UserToken.token == token))
        tokens_all = tokens.all()
        if not tokens_all:
            return
        token = tokens_all[0][0]
        # get user models
        return token

    # HABITS
    @db_session_with
    async def get_habits_byuserid(self, userid: int, db_session: AsyncSession):
        # update db with user_id
        client_all = await db_session.execute(
            select(Habit).where(Habit.userid == userid))
        habits_dict = client_all.all()
        return habits_dict

    @db_session_with
    async def get_habits_byid(self, habitid: int, db_session: AsyncSession):
        # update db with user_id
        client_all = await db_session.execute(
            select(Habit).where(Habit.id == habitid))
        habits_dict = client_all.all()
        return habits_dict[0]

    @db_session_with
    async def get_default_habits(self, db_session: AsyncSession):
        client_all = await db_session.execute(
            select(DefaultHabits))
        habits_dict = client_all.all()
        return habits_dict

    @db_session_with
    async def add_user_habit(self, userid: int, habit: AddUserHabits, db_session: AsyncSession):
        """Register user"""
        value_dict = {"userid": userid,
                      "name": habit.name, "description": habit.description,
                      "min_description": habit.min_description,
                      "streak": habit.streak}
        if habit.image:
            value_dict["image"] = habit.image
        await db_session.execute(
            insert(Habit).values(value_dict).on_conflict_do_nothing())

        logging.info(f"{userid} habit have been added")
        return True

    @db_session_with
    async def add_user_comment(self, userid: int, comment: AddUserComment, db_session: AsyncSession):
        """Register user"""
        await db_session.execute(
            insert(UserComment).values({"userid": userid,
                                        "comment": comment.comment, "user_status": comment.user_status,
                                        'datet': comment.datet}).on_conflict_do_nothing())

        logging.info(f"{userid} comment have been added")
        return True

    @db_session_with
    async def get_habit_byid(self, habitid, db_session: AsyncSession):
        # update db with user_id
        tokens = await db_session.execute(
            select(Habit).where(Habit.id == habitid))
        tokens_all = tokens.all()
        if not tokens_all:
            return
        token = tokens_all[0][0]
        # get user models
        return token

    @db_session_with
    async def complete_habit(self, userid: int, habitid: int, db_session: AsyncSession, datet: datetime = None):
        """Register user"""
        values_dict = {"userid": userid,
                       "habitid": habitid}
        if datet:
            values_dict['datet'] = datetime.datetime(year=datet.year, month=datet.month, day=datet.day)
        else:
            today = datetime.datetime.now()
            values_dict['datet'] = datetime.datetime(year=today.year, month=today.month, day=today.day)
        await db_session.execute(
            insert(HabitComplited).values(values_dict).on_conflict_do_nothing())

        logging.info(f"{habitid} habitid have been added")
        return True

    @db_session_with
    async def get_completed_habitids(self, userid: int, db_session: AsyncSession, datet: datetime = None):
        if datet:
            datet = datetime.datetime(year=datet.year, month=datet.month, day=datet.day)
            habits_all = await db_session.execute(
                select(HabitComplited).where(HabitComplited.userid == userid, HabitComplited.datet == datet))

        else:
            # update db with user_id
            habits_all = await db_session.execute(
                select(HabitComplited).where(HabitComplited.userid == userid))
        habits_dict = habits_all.all()
        return habits_dict

    @db_session_with
    async def get_allcomment_byuserid(self, userid: int, db_session: AsyncSession):
        # update db with user_id
        comment_all = await db_session.execute(
            select(UserComment).where(UserComment.userid == userid))
        comments_dict = comment_all.all()
        return comments_dict

    @db_session_with
    async def get_comment_byuserid_date(self, userid: int, datet: datetime.datetime, db_session: AsyncSession):
        # update db with user_id
        comment_all = await db_session.execute(
            select(UserComment).where(UserComment.userid == userid, UserComment.datet == datet))
        comments_dict = comment_all.all()
        if comments_dict:
            return comments_dict[0][0]

    @db_session_with
    async def get_stat_db(self, userid: int, datet: datetime.datetime, db_session: AsyncSession):
        pass