from django.db import models


class FoodCategory(models.Model):
    canteen = models.ForeignKey('canteens.Canteen', on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Food Categories'

    def __str__(self):
        return f"{self.canteen.name} - {self.name}"


class FoodItem(models.Model):
    canteen = models.ForeignKey('canteens.Canteen', on_delete=models.CASCADE, related_name='food_items')
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    preparation_time = models.IntegerField(default=15, help_text='In minutes')
    stock_quantity = models.IntegerField(null=True, blank=True, help_text='Null means unlimited')
    total_orders = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name
