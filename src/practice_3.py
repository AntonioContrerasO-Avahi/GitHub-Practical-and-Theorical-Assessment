from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Practice 3 - Edit Objects")

fake_users_db = {
    123: {
        "username": "Maxson59",
        "full_name": "Oscar Marin",
        "email": "oscar.marin@example.com",
    },
    231: {
        "username": "DrZoom513",
        "full_name": "Jose Luis",
        "email": "jose.luis@example.com",
    },
}


class Person(BaseModel):
    name: str
    last_name: str


class User(BaseModel):
    full_name: str
    username: str
    email: str


@app.get("/", tags=["Health"])
async def read_root(name: str):
    return {"message": f"{name.title()} was here!"}


@app.post("/person", tags=["Person"])
async def salute_person(person: Person):
    return {"message": f"Hello there {person.last_name}, {person.name}"}


@app.put("/user/{user_id}", tags=["User"])
async def edit_user(user_id: int, user: User):
    fake_user = fake_users_db.get(user_id)
    if not fake_user:
        raise HTTPException(status_code=404, detail="User not found")
    fake_user.update(user.model_dump())
    return {"message": "User edited", "id": user_id}


@app.get("/user", tags=["User"])
async def get_user(user_id: int):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": user}
