from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from Books.models import *
from accounts.models import *

# Create your views here.
def login_page(request):
    if request.method == 'POST': 
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)


        if not user_obj.exists():
            messages.warning(request, "Account not found")
            return HttpResponseRedirect(request.path_info) #for redirecting to the same page
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, "Your account is not verified")
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email, password = password)
        if user_obj: 
            login(request, user_obj)
            return redirect('/')
        
        messages.warning(request, "Invalid Credentials.")
        return HttpResponseRedirect(request.path_info) #for redirecting to the same page

    return render(request, 'accounts/login.html' )

def logout_page(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("accounts:login")


def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        c_password = request.POST.get('confirm-password')

        if password == c_password:
            user_obj = User.objects.filter(username = email)

            if user_obj.exists():
                messages.warning(request, "Email is already taken")
                return HttpResponseRedirect(request.path_info) #for redirecting to the same page
            
            print(email)
            
            user_obj = User.objects.create(first_name = first_name, last_name = last_name, email = email, username = email)
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, "An email has been sent on your entered email")
            cart , _ = Cart.objects.get_or_create(user = user_obj, is_paid = False)
            return HttpResponseRedirect(request.path_info) #for redirecting to the same page
        else:
            messages.warning(request, "Password entered and confirm password do not match")


    return render(request, 'accounts/register.html')


def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        messages.success(request, "Your email has been verified")
        return redirect("/")
    except Exception as e:
        return HttpResponse("Invalid email token")


def cart(request):
    cart_obj = Cart.objects.get(is_paid = False, user = request.user)
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code = coupon)

        if not coupon_obj.exists():
            messages.warning(request, "Invalid Coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.coupon:
            messages.warning(request, "Coupon already exists")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj[0].minimum_amount > cart_obj.get_cart_total()[0]:
            messages.warning(request, f"Amount should be greater than {coupon_obj[0].minimum_amount}")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj[0].is_expired:
            messages.warning(request, "Coupon expired")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.success(request, "Coupon applied")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    if cart_obj.coupon:
        coupon = cart_obj.coupon.coupon_code
        coupon_obj = Coupon.objects.filter(coupon_code = coupon)
        if coupon_obj[0].minimum_amount > cart_obj.get_cart_total()[0]:
                cart_obj.coupon = None
                cart_obj.save()
                messages.warning(request, f"Amount should be greater than {coupon_obj[0].minimum_amount}")
   

    context = {'cart': cart_obj, 'cart_items_total': cart_obj.get_cart_total()[0], 'cart_items_total_afterdiscount':  cart_obj.get_cart_total()[1]}
    return render(request, 'accounts/cart.html', context)


def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid = cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon Removed.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_to_cart(request, uid):
    no_of_same_books = request.GET.get('no_of_books')
    book = Book.objects.get(uid = uid)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)
    cart_item = CartItems.objects.create(cart = cart, book = book, book_in_cart = no_of_same_books )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def update_cart(request, cart_item_uid, no_of_books):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.book_in_cart = no_of_books
        cart_item.save()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))