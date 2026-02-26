from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Practice 2 - Defining Models")


class Person(BaseModel):
    name: str
    last_name: str


@app.get("/", tags=["Health"])
async def read_root(name: str):
    return {"message": f"{name.title()} was here!"}


@app.post("/person", tags=["Person"])
async def salute_person(person: Person):
    return {"message": f"Hello there {person.last_name}, {person.name}"}
