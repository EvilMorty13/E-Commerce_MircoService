from fastapi import FastAPI, HTTPException,Request
import httpx
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv
from schema import *

load_dotenv()

USER_SERVICE_URL = os.getenv('USER_SERVICE_URL')
SECRET_KEY = os.getenv('SECRET_KEY') 
ALGORITHM = os.getenv('ALGORITHM')  
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
app = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login", response_model=Token)
async def login(auth_data: AuthRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/login", json={"email": auth_data.email, "password": auth_data.password})
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = response.json()
        access_token = create_access_token(data={"sub": user["email"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/register")
# async def register(auth_data: AuthRequest):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{USER_SERVICE_URL}/register", 
#                                      json={"email": auth_data.email, 
#                                            "password": auth_data.password})
        
#         if response.status_code != 200:
#             raise HTTPException(status_code=400, detail="Registration failed")
        
#         registration_response = response.json()
    
#     return {"message": registration_response["message"]}


# Endpoint to validate token
@app.post("/validate-token")
async def validate_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    token = auth_header.split(" ")[1]

    try:
        # Decode the token and return its payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")