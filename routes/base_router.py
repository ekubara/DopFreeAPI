from fastapi import APIRouter


class BaseRouter:
    def __init__(self, pathname: str):
        self.router = APIRouter(prefix='/' + pathname)
