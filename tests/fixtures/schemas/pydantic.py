from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    username: str
    email: str


class BaseUserSchema(BaseModel):
    name: str
    job: str


class UserCreateResponse(BaseUserSchema):
    id: int


class UserUpdateResponse(BaseUserSchema):
    id: int


class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str
