import os
import requests

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderCreateSerializer, OrderResponseSerializer, OrderUpdateSerializer


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")

def validate_token(auth_header):
    if not auth_header:
        raise Exception("Authorization header is missing")
    response = requests.post(f"{AUTH_SERVICE_URL}", headers={"Authorization": auth_header})
    if response.status_code != 200:
        raise Exception(response.json().get("detail"))
    return response.json()


class OrderListCreateView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization")
        
        try:
            user = validate_token(auth_header)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data.get("product_id")
            quantity = serializer.validated_data.get("quantity")  
            
            # Check if product exists in product_microservice
            product_microservice_url = f"{PRODUCT_SERVICE_URL}/{product_id}"
            headers = {"Authorization": auth_header}

            try:
                product_response = requests.get(product_microservice_url, headers=headers)
                
                if product_response.status_code == 404:
                    return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
                elif product_response.status_code != 200:
                    return Response({"detail": "Error verifying product"}, status=product_response.status_code)

                product_data = product_response.json()
                product_stock = product_data.get("stock")
                product_price = product_data.get("price")
                
                if quantity > product_stock:
                    return Response(
                        {"detail": f"Insufficient stock. Available: {product_stock}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                total_price = product_price * quantity
                print(f"Product Price: {product_price}")
                print(f"Quantity: {quantity}")
                print(f"Total Price: {total_price}")

                # Update product stock by calling the product microservice
                updated_stock = product_stock - quantity
                update_product_data = {
                    "name": product_data["name"],
                    "price": product_price,
                    "stock": updated_stock
                }

                update_product_url = f"{PRODUCT_SERVICE_URL}/{product_id}"
                update_product_response = requests.put(
                    update_product_url, 
                    headers=headers, 
                    json=update_product_data
                )
                
                if update_product_response.status_code != 200:
                    return Response(
                        {"detail": "Failed to update product stock"},
                        status=update_product_response.status_code
                    )

            except requests.RequestException:
                return Response(
                    {"detail": "Failed to connect to product service"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Proceed to create the order with the calculated total price
            order = Order.objects.create(
                product_id=serializer.validated_data['product_id'],
                quantity=serializer.validated_data['quantity'],
                user_id=user.get("user_id"),
                total_price=total_price
            )


            response_serializer = OrderResponseSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderDetailView(APIView):
    def get(self, request, order_id):
        auth_header = request.headers.get("Authorization")
        try:
            user = validate_token(auth_header)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            order = Order.objects.get(id=order_id, user_id=user.get("user_id"))
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderResponseSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, order_id):
        auth_header = request.headers.get("Authorization")
        try:
            user = validate_token(auth_header)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            order = Order.objects.get(id=order_id, user_id=user.get("user_id"))
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch product details from the product microservice
        product_microservice_url = f"{PRODUCT_SERVICE_URL}/{order.product_id}"
        headers = {"Authorization": auth_header}

        try:
            product_response = requests.get(product_microservice_url, headers=headers)
            if product_response.status_code != 200:
                return Response({"detail": "Failed to fetch product details"}, status=product_response.status_code)

            product_data = product_response.json()
            product_stock = product_data.get("stock")
        except requests.RequestException:
            return Response(
                {"detail": "Failed to connect to product service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Calculate the stock adjustment
        old_quantity = order.quantity
        new_quantity = request.data.get("quantity")
        if not new_quantity:
            return Response({"detail": "Quantity is required"}, status=status.HTTP_400_BAD_REQUEST)

        new_quantity = int(new_quantity)
        quantity_diff = new_quantity - old_quantity

        # Ensure stock adjustment is valid
        if quantity_diff > 0 and quantity_diff > product_stock:
            return Response(
                {"detail": f"Insufficient stock. Available: {product_stock}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update product stock in the product microservice
        updated_stock = product_stock - quantity_diff
        update_product_data = {
            "name": product_data["name"],
            "price": product_data["price"],
            "stock": updated_stock
        }

        try:
            update_product_response = requests.put(
                product_microservice_url,
                headers=headers,
                json=update_product_data
            )
            if update_product_response.status_code != 200:
                return Response(
                    {"detail": "Failed to update product stock"},
                    status=update_product_response.status_code
                )
        except requests.RequestException:
            return Response(
                {"detail": "Failed to connect to product service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Update the order with the new quantity
        serializer = OrderUpdateSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = OrderResponseSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        auth_header = request.headers.get("Authorization")
        try:
            user = validate_token(auth_header)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            order = Order.objects.get(id=order_id, user_id=user.get("user_id"))
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_200_OK)
