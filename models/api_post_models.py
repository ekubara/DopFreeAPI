import binascii
import datetime
import hashlib
import os
import re

from pydantic import BaseModel
from pydantic.class_validators import validator


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = b'__hash__' + hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000, dklen=20)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def is_hash(pw: str) -> bool:
    return pw.startswith('__hash__') and len(pw) == 112


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    salt = stored_password[:72]
    stored_password = stored_password[72:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000, dklen=20)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


class TokenModel(BaseModel):
    token: str


class RegUser(BaseModel):
    name: str
    email: str
    age: int
    password: str

    @validator('password')
    def hash_password(cls, pw: str) -> str:
        if is_hash(pw):
            return pw
        return hash_password(pw)


class LogIn(BaseModel):
    email: str
    password: str


class UpdateUser(BaseModel):
    token: str
    # остальные поля не обязательны
    name: str | None
    email: str | None
    age: int | None
    password: str | None

    @validator('password')
    def hash_password(cls, pw: str) -> str:
        if is_hash(pw):
            return pw
        return hash_password(pw)


class AddUserHabits(BaseModel):
    token: str
    name: str
    description: str
    min_description: str
    image: str | None
    streak: int


class AddUserComment(BaseModel):
    token: str
    comment: str
    user_status: int
    datet: datetime.datetime

    @validator('datet')
    def date_valid(cls, datet: datetime) -> datetime:
        naive = datet.replace(tzinfo=None)

        return datetime.datetime(year=naive.year, month=naive.month, day=naive.day)
class GetComment(BaseModel):
    token: str
    datet: datetime.datetime | None
    @validator('datet')
    def date(cls, datet: datetime) -> datetime:
        naive = datet.replace(tzinfo=None)

        return datetime.datetime(year=naive.year, month=naive.month, day=naive.day)
class CompleteHabit(BaseModel):
    token: str
    id: int
