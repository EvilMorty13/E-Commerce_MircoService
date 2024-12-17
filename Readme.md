
# E-Commerce Web App

## Table of Contents 
- [Introduction](#introduction) 
- [Prerequisite](#prerequisite) 
- [Installation](#installation) 
- [Database](#database)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Docker Compose](#docker-compose)
- [API Endpoints](#api-endpoints) 
    - [Gateway Endpoints](#gateway-endpoints) 
    - [User Endpoints](#user-endpoints) 
    - [Product Endpoints](#product-endpoints) 
    - [Order Endpoints](#order-endpoints) 
- [Authentication](#authentication) 



## Introdcution

This is a dummy e-commerce web app with 4 microservice. These are 
- Gateway (Used for JWT token generation and verification)
- User (For Login and Registration and handling user data)
- Product (CRUD operations with authentication and handling product data)
- Order (CRUD operations with authentication and handling order data)

Gateway,User and Product microservices are made with Fastapi and Order microservice is made with Django Rest Framework.


## Prerequisite

- Python 3.12
- Local postgresql Server


## Installation

 
- **Clone the repository**  
   Clone the project repository to your local machine:
   ```bash
   git clone https://github.com/EvilMorty13/E-Commerce_MircoService
   cd E-Commerce_MircoService
   ```
 
- **Create and Activate virtual enviroment for each microservice**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
- **Install Requirements for each microservice**
    ```bash
    pip install -r requirements.txt
   ```

## Database
Create seperate postgresql databases in your local pc and add the urls in the code.

## Environment Variables 

Microservice Urls, Secret key, Algorithm and Token lifetime are hidden using .env file. Make sure to add that in the project.

## Running the Project

- **Start the gateway server**
    ```bash
   uvicorn gateway_service:app --reload --port 8000
   ```

- **Start the user server**
    ```bash
   uvicorn user_service:app --reload --port 8001
   ```

- **Start the product server**
    ```bash
   uvicorn product_service:app --reload --port 8002
   ```

- **Start the order server**
    ```bash
   python manage.py runserver 127.0.0.1:8003
   ```


## Docker Compose

It's also possible to run the project using Docker compose after setting up the Database and Enviroment Variables.
   ```bash
      sudo docker compose up --build
   ```

## API Endpoints

### Gateway Endpoints

- **User login[POST]**
    ```bash
   http://127.0.0.1:8000/login
   ```
- **Token verification[POST]**
    ```bash
   http://127.0.0.1:8000/validate-token
   ```

### User Endpoints

- **User Login[POST]**
    ```bash
   http://127.0.0.1:8001/login
   ```

- **User Registration[POST]**
    ```bash
   http://127.0.0.1:8001/register
   ```

### Product Endpoints

- **Create Product[POST]**
    ```bash
   http://127.0.0.1:8002/products
   ```
- **Get All Product[GET]**
    ```bash
   http://127.0.0.1:8002/products
   ```

- **Get Single Product[GET]**
    ```bash
   http://127.0.0.1:8002/products/{product_id}
   ```

- **Update Product[PUT]**
    ```bash
   http://127.0.0.1:8002/products/{product_id}
   ```
- **Delete Product[DELETE]**
    ```bash
   http://127.0.0.1:8002/products/{product_id}
   ```



### Order Endpoints

- **Create Order[POST]**
    ```bash
   http://127.0.0.1:8002/orders
   ```

- **Get Single Order[GET]**
    ```bash
   http://127.0.0.1:8003/orders/{order_id}
   ```

- **Update Order[PUT]**
    ```bash
   http://127.0.0.1:8003/orders/{order_id}
   ```

- **Delete Order[DELETE]**
    ```bash
   http://127.0.0.1:8003/orders/{order_id}
   ```

## Authentication
After login, a jwt token will be generated. Use this for authentication.

- **Using Token**
    ```bash
   Authentication : Bearer <Token>
   ```


