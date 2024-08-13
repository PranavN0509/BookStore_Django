from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from Books.models import *


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.IntegerField(default=0)
    gender = models.CharField(blank=True, default="", max_length=10)
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to="profile")

    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid = False, cart__user = self.user).count()
    
    def get_firstname(self):
        return self.user.first_name
    
    def get_lastname(self):
        return self.user.last_name
    
    def get_fullname(self):
        return self.user.first_name+"  "+self.user.last_name
    
    def get_userimage(self):
        return self.profile_image

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        for book in cart_items:
            if book.book_in_cart == 1:
                price.append(book.book.price)
            elif book.book_in_cart > 1:
                price.append(book.book.price*book.book_in_cart)

        if self.coupon:
            if sum(price) > self.coupon.minimum_amount:
                return [sum(price), sum(price)-self.coupon.discount_price]
        return [sum(price), sum(price)]
    
    def get_cart_unique_items_count(self):
        return CartItems.objects.filter(cart__is_paid = False, cart__user = self.user).count()
    

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    book_in_cart = models.IntegerField(default=1)

    def get_book_price(self):
        if self.book_in_cart == 1:
            return self.book.price
        elif self.book_in_cart > 1:
            return self.book.price*self.book_in_cart

@receiver(post_save, sender = User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance, email_token = email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
    except Exception as e:
        print(e)