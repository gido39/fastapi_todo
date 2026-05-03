from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    done: bool = False

class TodoResponse(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
