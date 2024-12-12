from django.db import models

class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField()
    total_price = models.FloatField()
    user_id = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)