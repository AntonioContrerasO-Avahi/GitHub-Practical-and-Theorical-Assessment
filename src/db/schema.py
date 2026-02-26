from sqlmodel import Field, SQLModel
from pydantic import BaseModel, model_validator


class UserNoHash(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    full_name: str = Field(default=None)
    password: str = Field(default=None)


class UserHash(BaseModel):
    id: int
    username: str
    full_name: str
    password: str  # bcrypt hashed password


class UserRegister(BaseModel):
    username: str
    full_name: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
