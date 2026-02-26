from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from db.schema import Token, TokenData, UserHash, UserNoHash, UserRegister
from db.utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_db_and_tables,
    get_session,
    hash_password,
    verify_password,
)

app = FastAPI(title="Practice 7 - OAuth2 + JWT")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SessionDep = Annotated[Session, Depends(get_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = session.exec(
        select(UserNoHash).where(UserNoHash.username == token_data.username)
    ).first()
    if user is None:
        raise credentials_exception
    return user


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", tags=["Health"])
async def read_root(name: str):
    return {"message": f"{name.title()} was here!"}


@app.post("/users/register", tags=["User"], status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, session: SessionDep):
    existing = session.exec(
        select(UserNoHash).where(UserNoHash.username == user_data.username)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_data.username}' is already taken",
        )
    new_user = UserNoHash(
        username=user_data.username,
        full_name=user_data.full_name,
        password=hash_password(user_data.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User created", "id": new_user.id, "username": new_user.username}


@app.get("/user/me", tags=["User"], response_model=UserHash)
async def read_current_user(current_user: UserNoHash = Depends(get_current_user)):
    return current_user


@app.get("/secret", tags=["Protected"])
async def secret_route(current_user: UserNoHash = Depends(get_current_user)):
    return {"message": "Secret open"}


@app.post("/token", tags=["Auth"], response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = session.exec(
        select(UserNoHash).where(UserNoHash.username == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/healthcheck", tags=["Public"])
async def public_route():
    return {"message": "Hello There, this is public. No auth required"}
