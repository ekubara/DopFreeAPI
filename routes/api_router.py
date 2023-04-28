import asyncio
import json
import os
from datetime import datetime, timedelta
from calendar import monthrange
from dateutil.relativedelta import *
from secrets import token_hex
from collections import OrderedDict

from fastapi import Depends, HTTPException
from fastapi.openapi.models import Response

from models.api_post_models import RegUser, LogIn, is_hash, verify_password, UpdateUser, TokenModel, AddUserHabits, \
    AddUserComment, CompleteHabit, GetComment

from routes.base_router import BaseRouter


# наследуемся от baseroute
class ApiRouter(BaseRouter):
    def __init__(self, pathname: str, repo):
        super().__init__(pathname)

        # в селф заносим объекс для работы с бд (круд операции)
        self.repo = repo

        #
        self.router.add_api_route(path="/reg",
                                  endpoint=self.register,
                                  methods=["POST"])
        self.router.add_api_route(path="/login",
                                  endpoint=self.login,
                                  methods=["POST"])
        self.router.add_api_route(path="/update_user",
                                  endpoint=self.update_user,
                                  methods=["PUT"])
        self.router.add_api_route(path="/get_user",
                                  endpoint=self.get_user,
                                  methods=["POST"])
        self.router.add_api_route(path="/get_habits",
                                  endpoint=self.get_user_habits,
                                  methods=["POST"])
        self.router.add_api_route(path="/add_habit",
                                  endpoint=self.add_user_habits,
                                  methods=["POST"])
        self.router.add_api_route(path="/add_comment",
                                  endpoint=self.add_user_comment,
                                  methods=["POST"])
        self.router.add_api_route(path="/complete_habit",
                                  endpoint=self.complete_habit,
                                  methods=["POST"])
        self.router.add_api_route(path="/get_comment",
                                  endpoint=self.get_comment,
                                  methods=["POST"])
        self.router.add_api_route(path="/get_stat_fromreg",
                                  endpoint=self.get_stat_fromreg,
                                  methods=["POST"])
        self.router.add_api_route(path="/get_week_stat",
                                  endpoint=self.get_week_stat,
                                  methods=["POST"])
        self.router.add_api_route(path="/get_six_month_stat",
                                  endpoint=self.get_six_month_stat,
                                  methods=["POST"])

    async def register(self, user: RegUser):
        """register user if email is not in db"""

        # заносим юзера в бд
        is_reg = await self.repo.register_user(user)

        # если он уже зареган
        if is_reg:
            # получем юзера из бд - все его данные
            db_user = await self.repo.get_user_byemail(user.email)

            # создаем токен
            token = token_hex(20)

            # регистрируем токен
            is_token = await self.repo.register_user_token(db_user.id, token)

            # получем уже созданные хэбиты и присоединяем их к юзеру
            default_habits = await self.repo.get_default_habits()
            for habitc in default_habits:
                habit = habitc[0]
                add_habit = AddUserHabits(token='empty', name=habit.name, description=habit.description,
                                          min_description=habit.min_description, image=habit.image, streak=habit.streak)

                await self.repo.add_user_habit(db_user.id, add_habit)
            if is_token:
                return {'token': token, 'name': db_user.name, 'age': db_user.age, "email": db_user.email}
        else:
            # the user is already in db
            raise HTTPException(status_code=409, detail="User already exists")

    async def login(self, user: LogIn):
        """log in and return token"""
        db_user = await self.repo.get_user_byemail(user.email)
        if not db_user:
            raise HTTPException(status_code=403, detail="Email or password are not correct")
        stored_pw_hash = db_user.password
        if verify_password(stored_pw_hash, user.password):
            # success
            token = token_hex(20)
            is_token = await self.repo.update_token(db_user.id, token)
            if is_token:
                return {'token': token, 'name': db_user.name, 'age': db_user.age, "email": db_user.email}
            else:
                raise HTTPException(status_code=404, detail="Token is not exists")
        else:
            raise HTTPException(status_code=403, detail="Email or password are not correct")

    async def update_user(self, user_update: UpdateUser):
        reqtoken = user_update.token
        user_token = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token:
            raise HTTPException(status_code=403, detail="Token not accetable")
        db_user = await self.repo.get_user_byid(user_token.userid)
        values_dict = dict()
        if user_update.name:
            values_dict['name'] = user_update.name
        if user_update.age:
            values_dict['age'] = user_update.age
        if user_update.email:
            values_dict['email'] = user_update.email
        if user_update.password:
            values_dict['password'] = user_update.password
        if len(values_dict) > 0:
            is_update_db = await self.repo.update_user_data(db_user.email, values_dict)
        else:
            return {}
        if is_update_db:
            values_dict['password'] = '****'
            return values_dict
        else:
            raise HTTPException(status_code=400, detail="Db error")

    async def get_user(self, token_model: TokenModel):
        reqtoken = token_model.token
        user_token = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token:
            raise HTTPException(status_code=403, detail="Token not accetable")
        db_user = await self.repo.get_user_byid(user_token.userid)
        db_user.password = '****'
        return db_user

    async def get_user_habits(self, token_model: TokenModel):
        # todo percentage on every week day mon
        today = datetime.now()
        cur_date = datetime(year=today.year, month=today.month, day=today.day)
        reqtoken = token_model.token
        user_token = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token:
            raise HTTPException(status_code=403, detail="Token not accetable")
        db_user_habits = await self.repo.get_habits_byuserid(user_token.userid)
        habits_lst = [i[0].__dict__ for i in db_user_habits]
        completed_habits_rows = await self.repo.get_completed_habitids(user_token.userid, datet=cur_date)
        completed_habits_ids = [i[0].habitid for i in completed_habits_rows]
        for hab in habits_lst:
            # удаляем лишнюю информацию
            del hab['_sa_instance_state']

            if hab['id'] in completed_habits_ids:
                hab['completed'] = True
            else:
                hab['completed'] = False

            # streak записываем
            streak = 0 if hab['completed'] == False else 1

            today = datetime.now() - timedelta(days=1)
            datet_check = datetime(year=today.year, month=today.month, day=today.day)
            while True:
                is_habit = await self.repo.get_completed_habitids_byid_byuserid_bydate(userid=user_token.userid,
                                                                                       habitid=hab['id'],
                                                                                       datet=datet_check)
                if is_habit:
                    streak += 1
                else:
                    break
                datet_check = datet_check - timedelta(days=1)
            hab['streak'] = streak
        return habits_lst

    async def add_user_habits(self, habit: AddUserHabits):
        reqtoken = habit.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")
        status = await self.repo.add_user_habit(user_token_obj.userid, habit)
        if status:
            return {'name': habit.name}
        else:
            raise HTTPException(status_code=400, detail="Db error")

    async def add_user_comment(self, comment: AddUserComment):
        reqtoken = comment.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")
        status = await self.repo.add_user_comment(user_token_obj.userid, comment)
        if status:
            return {'Comment': comment.comment}
        else:
            raise HTTPException(status_code=400, detail="Db error")

    async def complete_habit(self, complete_habit: CompleteHabit):
        reqtoken = complete_habit.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")
        status = await self.repo.complete_habit(user_token_obj.userid, complete_habit.id)
        if status:
            return {'Completed': complete_habit.id}
        else:
            raise HTTPException(status_code=400, detail="Db error")

    async def get_comment(self, comment_req: GetComment):
        reqtoken = comment_req.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")
        if comment_req.datet:
            status = await self.repo.get_comment_byuserid_date(user_token_obj.userid, comment_req.datet)

            result = {"id": status.id, 'comment': status.comment, 'user_status': status.user_status,
                      'datet': str(status.datet)}
        else:
            status = await self.repo.get_allcomment_byuserid(user_token_obj.userid)
            result = [
                {"id": i[0].id, 'comment': i[0].comment, 'user_status': i[0].user_status, 'datet': str(i[0].datet)} for
                i in status]
        if status:
            return result
        else:
            raise HTTPException(status_code=400, detail="Db error")

    async def get_week_stat(self, token_model: TokenModel):
        """log in and return token"""
        reqtoken = token_model.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")
        user_reg = await self.repo.get_user_byid(user_token_obj.userid)
        completed_habitids = {}

        # take today date without time - we use date without time in table
        today = datetime.now()
        cur_date = datetime(year=today.year, month=today.month, day=today.day)

        while True:
            if cur_date.strftime("%A") == 'Sunday':
                break
            cur_date = cur_date + timedelta(days=1)

        # creaet dict with day: completed habits
        for i in range(7):
            completed_habitids_curdate = await self.repo.get_completed_habitids(user_token_obj.userid,
                                                                                datet=cur_date)
            db_user_habits = await self.repo.get_habits_byuserid(user_token_obj.userid)
            all_habits = [i[0].__dict__ for i in db_user_habits]
            completed_habitids[cur_date.strftime("%A")] = int((len(completed_habitids_curdate) / len(all_habits)) * 100)
            cur_date = cur_date - timedelta(days=1)
        # for in new dict and get habit from id

        return completed_habitids

    async def get_six_month_stat(self, token_model: TokenModel):
        """log in and return token"""
        reqtoken = token_model.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")
        user_reg = await self.repo.get_user_byid(user_token_obj.userid)

        to_push = datetime.now()
        to_push_m = datetime(year=to_push.year, month=to_push.month, day=to_push.day) - relativedelta(months=6)
        # today - to cycle
        today = datetime.now()
        today = datetime(year=today.year, month=today.month, day=today.day)
        result = {}  # {'datetime.month':'count'}
        month_days_count = {}  # {'datetime.month':'count'}
        while to_push_m <= today:
            result[to_push_m.strftime("%B")] = 0

            m_count = monthrange(to_push_m.year, to_push_m.month)[1]
            month_days_count[to_push_m.strftime("%B")] = m_count
            to_push_m = to_push_m + relativedelta(months=1)

        completed_habitids = await self.repo.get_completed_habitids(user_token_obj.userid)
        completed_habitids_lst = [i[0] for i in completed_habitids]

        for habit_id in completed_habitids_lst:
            datetime_dt = habit_id.datet
            month_dt = datetime(year=datetime_dt.year, month=datetime_dt.month, day=datetime_dt.day)
            result[month_dt.strftime("%B")] += 1

        db_user_habits = await self.repo.get_habits_byuserid(user_token_obj.userid)
        all_habits = [i[0].__dict__ for i in db_user_habits]
        res_lst = []
        for k, v in result.items():
            m_count = month_days_count[k]
            res_lst.append({'month': k, 'percent': int((v / (len(all_habits) * m_count)) * 100)})
        return res_lst

    async def get_stat_fromreg(self, token_model: TokenModel):
        """log in and return token"""
        reqtoken = token_model.token
        user_token_obj = await self.repo.get_userid_bytoken(reqtoken)
        if not user_token_obj:
            raise HTTPException(status_code=403, detail="Token not accetable")

        user_reg = await self.repo.get_user_byid(user_token_obj.userid)

        # create 0 for all month from user registration

        # user_reg year and month - from cycle
        to_push = user_reg.datet
        to_push_m = datetime(year=to_push.year, month=to_push.month, day=1)
        # today - to cycle
        today = datetime.now()
        result = OrderedDict()  # {'datetime.month':'count'}
        while to_push_m.year <= today.year and to_push_m.month <= today.month:
            result[to_push_m] = 0
            to_push_m = to_push_m + relativedelta(months=1)

        completed_habitids = await self.repo.get_completed_habitids(user_token_obj.userid)
        completed_habitids_lst = [i[0] for i in completed_habitids]

        for habit_id in completed_habitids_lst:
            datetime_dt = habit_id.datet
            month_dt_m = datetime(year=datetime_dt.year, month=datetime_dt.month, day=1)
            result[month_dt_m] += 1

        for k, v in result.items():
            m_count = monthrange(k.year, k.month)
            result[k] = (v / m_count[1]) * 100
        return Response(content=json.dumps(result), media_type="application/json")
