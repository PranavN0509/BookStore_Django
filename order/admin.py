from django.contrib import admin
from order.models import *

class OrderItemList(admin.TabularInline):
	model = OrderItem
	list_display = ['uid', 'book', 'price', 'quantity']

	extra = 0



class OrderList(admin.ModelAdmin):
	list_display = ['uid', 'created_at', 'updated_at', 'customer', 'name', 'email', 'phone', 'address', 'country', 'state', 'district', 'pincode', 'totalbook', 'paid', 'status']
	list_filter = ['paid']
	# exclude = ['name', 'email', 'phone']
	inlines = [OrderItemList]
	class Meta:
		Model = Order

admin.site.register(Order, OrderList)


