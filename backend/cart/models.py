from django.db import models


class Cart(models.Model):
    student = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='cart')
    canteen = models.ForeignKey('canteens.Canteen', on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.student.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('menu.FoodItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'food_item']

    @property
    def subtotal(self):
        return self.food_item.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"
