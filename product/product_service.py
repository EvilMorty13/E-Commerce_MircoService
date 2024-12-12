from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx
import os
from dotenv import load_dotenv
from database import *
from models import *
from schemas import *

load_dotenv()

app = FastAPI(lifespan=lifespan)


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")  


async def validate_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}", headers={"Authorization": auth_header})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()  # Token payload




@app.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db), 
    user: dict = Depends(validate_token)):
    
    print(user)
    user_id = user.get("user_id")

    
    db_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        user_id=user_id
    )
    
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product



@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: dict = Depends(validate_token)):
    
    
    async with db.begin():
        result = await db.execute(select(Product).filter(Product.id == product_id))
        product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product



@app.get("/products", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db), user: dict = Depends(validate_token)):
    async with db.begin():
        result = await db.execute(select(Product))
        products = result.scalars().all()
    return products



@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, 
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db), 
    user: dict = Depends(validate_token)):
    
    print(user)
    user_id = user.get("user_id")

    async with db.begin():
        result = await db.execute(select(Product).filter(Product.id == product_id))
        db_product = result.scalars().first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # if db_product.user_id != user_id:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this product")

    db_product.name = product.name
    db_product.price = product.price
    db_product.stock = product.stock
    await db.commit()
    await db.refresh(db_product)

    return db_product



@app.delete("/products/{product_id}")
async def delete_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: dict = Depends(validate_token)):
    
    async with db.begin():
        result = await db.execute(select(Product).filter(Product.id == product_id))
        db_product = result.scalars().first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(db_product)
    await db.commit()
    return {"message": "Product deleted successfully"}
