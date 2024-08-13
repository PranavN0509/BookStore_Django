from django.contrib import admin
from accounts.models import *

class CartItemList(admin.TabularInline):
	list_display = ['book', 'book_in_cart']
	model = CartItems
	

class CartList(admin.ModelAdmin):
	list_display = ['uid', 'user', 'coupon', 'is_paid']
	list_filter = ['coupon']
	# exclude = ['name', 'email', 'phone']
	inlines = [CartItemList]
	class Meta:
		Model = Cart	

admin.site.register(Cart, CartList)

class ProfileShow(admin.ModelAdmin):
	list_display = ['user', 'age', 'gender', 'is_email_verified', 'email_token', 'profile_image']
	# inlines = [UserShow]
	class Meta:
		Model = Profile
	# model = Profile
admin.site.register(Profile, ProfileShow)
# admin.site.register(Cart)
# admin.site.register(CartItems)
