from django.db import models
from base.models import BaseModel
from Books.models import Book
from django.contrib.auth.models import User


class Order(BaseModel):
	customer = models.ForeignKey(User, on_delete = models.CASCADE)
	name = models.CharField(max_length=30)
	email = models.EmailField()
	phone = models.CharField(max_length=16)
	address = models.CharField(max_length=150)
	country = models.CharField(max_length=30,default=0)
	state = models.CharField(max_length=30, default=0)
	district = models.CharField(max_length=30)
	pincode = models.CharField(max_length=6, default=0)
	payable = models.IntegerField()
	totalbook = models.IntegerField()
	paid = models.BooleanField(default=False)
	status = models.CharField(default="", editable=True, max_length=20)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return 'Order {}'.format(self.uid)

	def get_total_cost(self):
		return sum(item.get_cost() for item in self.items.all())


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
	

    def __str__(self):
        return '{}'.format(self.uid)

    def get_cost(self):
        return (self.price*self.quantity)
