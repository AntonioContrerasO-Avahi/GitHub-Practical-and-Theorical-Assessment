import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, model_validator

app = FastAPI(title="Practice 6 - Password Hashing")
security = HTTPBasic()


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": hash_password("secret123"),
    },
    "oscar": {
        "username": "oscar",
        "full_name": "Oscar Marin",
        "email": "oscar@example.com",
        "password": hash_password("password123"),
    },
}


class UserRegister(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@app.get("/", tags=["Health"])
async def read_root(name: str):
    return {"message": f"{name.title()} was here!"}


@app.post("/users/register", tags=["User"], status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_data.username}' is already taken",
        )
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "full_name": user_data.full_name,
        "email": user_data.email,
        "password": hash_password(user_data.password),
    }
    return {"message": "User created", "username": user_data.username}


@app.get("/user/me", tags=["User"])
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "password": current_user["password"],
    }


@app.get("/healthcheck", tags=["Public"])
async def public_route():
    return {"message": "Hello There, this is public. No auth required"}
