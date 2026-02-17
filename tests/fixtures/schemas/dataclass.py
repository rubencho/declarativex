import dataclasses


@dataclasses.dataclass
class User:
    id: int
    name: str
    username: str
    email: str


@dataclasses.dataclass
class BaseUserSchema:
    name: str
    job: str


@dataclasses.dataclass
class UserCreateResponse(BaseUserSchema):
    id: int


@dataclasses.dataclass
class UserUpdateResponse(BaseUserSchema):
    id: int


@dataclasses.dataclass
class Post:
    userId: int
    id: int
    title: str
    body: str
