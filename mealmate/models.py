from django.db import models

# Create your models here.
class Customer(models.Model):
    username = models.CharField(max_length = 50, unique=True)
    password = models.CharField(max_length = 50)
    email = models.CharField(unique=True)
    mobile = models.CharField(max_length = 10, unique=True)
    address = models.CharField(max_length = 200)

    def __str__(self):
        return f"{self.username} {self.password} {self.email} {self.mobile} {self.address}"
    

class Restaurant(models.Model):
    name = models.CharField(max_length = 200)
    picture = models.ImageField(upload_to="restaurant_images/", blank=True, null=True)
    cuisine = models.CharField(max_length = 200)
    rating = models.FloatField()

    def __str__(self):
        return f"{self.name} {self.cuisine} {self.rating}/5"
    
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = "menu_items")
    name = models.CharField(max_length = 20)
    picture = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    description = models.CharField(max_length = 200)
    price = models.FloatField()
    is_veg = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.name} {self.description} {self.price}"
    
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = "cart")
    items = models.ManyToManyField("MenuItem",related_name="carts", blank = True)

    def total_price(self):
        return sum(item.price for item in self.items.all())

    def total_items(self):
        return self.items.count()

    def __str__(self):
        return f"{self.customer.username} {self.total_price}"