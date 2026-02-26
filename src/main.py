from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets


class Person(BaseModel):
    name: str
    last_name: str


class User(BaseModel):
    username: str
    full_name: str
    email: str


fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "secret123",
    },
    "oscar": {
        "username": "oscar",
        "full_name": "Oscar Marin",
        "email": "oscar@example.com",
        "password": "password123",
    },
}

app = FastAPI()
security = HTTPBasic()


# Dependency function to verify credentials
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)
    # Check if user exists and password matches
    if not user or not secrets.compare_digest(
        credentials.password.encode("utf8"), user["password"].encode("utf8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


## TASK 1
@app.get(
    "/",
    tags=["Health"],
    name="health_check",
    summary="Health Check",
    description="Verify the API service is running.",
)
async def read_root(name: str):
    """Health check endpoint."""
    return {"message": f"{name.title()} was here!"}


## TASK 2


@app.post("/person", tags=["Person"])
async def salute_person(person: Person, current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello there {person.last_name}, {person.name}"}


## TASK 3


# @app.put("/user/{user_id}", tags=["User"])
# async def edit_user(user_id: int, user: User):
#     fake_user = fake_users_db.get(user_id)
#     fake_user.update(user.model_dump())
#     return {"message": "User edited", "id": user_id}


# @app.get("/user", tags=["User"])
# async def get_user(user_id: int):
#     return {"message": fake_users_db.get(user_id)}


## TASK 4


@app.get("/user/me", tags=["User"])
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
    }


@app.get("/healthcheck", tags=["Public"])
async def public_route():
    return {"message": "Hello There, this is public. No auth required"}
