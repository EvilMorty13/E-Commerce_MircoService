from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from sqlalchemy.future import select
from database import *
from models import *
from schemas import *

app = FastAPI(lifespan=lifespan)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.post("/login")
async def login(auth_data: AuthRequest, db: AsyncSession = Depends(get_db)):

    async with db.begin():
        result = await db.execute(select(User).filter(User.email == auth_data.email))
        user = result.scalars().first()

    if not user or not verify_password(auth_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Return user data (email) to be used in the Gateway to create the token
    return {"email": user.email}


@app.post("/register")
async def register(auth_data: AuthRequest, db: AsyncSession = Depends(get_db)):
    hashed_password = hash_password(auth_data.password)
    
    result = await db.execute(select(User).filter(User.email == auth_data.email))
    existing_user = result.scalars().first() 
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = User(email=auth_data.email, password=hashed_password)
    db.add(db_user)
    await db.commit()
    return {"message": "User registered successfully"}
