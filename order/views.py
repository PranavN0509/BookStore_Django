from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from order.models import *
from accounts.models import *
# from order.forms import *
# from order.pdfcreator import *


def order_create(request):
	cart = Cart.objects.get(is_paid = False, user = request.user)
	if request.user.is_authenticated:
		profile1 = Profile.objects.get(uid = request.user.profile.uid)
		print("\n", profile1)
		customer = User.objects.filter(username=request.user)[0]
		# form = OrderCreateForm(request.POST or None, initial={"name": request.user.profile.get_fullname(), "email": customer.email})
		
		if request.method == 'POST':
			print("\n\n\n\n\n", "Hello we are inside post")
			try:
				# order = form.save(commit=False)
				customer1 = User.objects.get(username=request.user)
				name = request.POST.get('fname')+" "+request.POST.get("lname")
				email = request.POST.get('email')
				phone = request.POST.get('phone')
				address = request.POST.get('address')
				country = request.POST.get('country')
				state = request.POST.get('state')
				district = request.POST.get('district')
				pincode = request.POST.get('pin_code')
				# payment_method = request.POST.get('paymentMethod')
				
				if cart.coupon:
					payable = cart.get_cart_total()[1]
				else:
					payable = cart.get_cart_total()[1]
				totalbook = cart.get_cart_unique_items_count() # len(cart.cart) // number of individual book
				print("\n\n\n\n\n", "Hello we are inside post")
				order_obj = Order.objects.create(customer = customer1, name = name, email = email, phone = phone, address = address, country = country, state = state, district = district, pincode = pincode ,payable = payable, totalbook = totalbook, paid = True, status="Processing")
				print("Hello we are inside post")
				order_obj.save()
				print("Hello we are inside post")

				for item in cart.cart_items.all():
					OrderItem.objects.create(
						order=order_obj, 
						book=item.book, 
						price=item.get_book_price(), 
						quantity=item.book_in_cart
						)
					book = Book.objects.get(name = item.book)
					book.stock = book.stock-item.book_in_cart
					book.save()

				print("Hello cart items inserted")
				cart_items = CartItems.objects.filter(cart = cart)
				cart_items.delete()
				print("Hello cart clear")
				return render(request, "order/order-summary.html", {'order': order_obj})
			except Exception as e:
				print(e)

		if request.user.profile.get_cart_count() > 0:
			print("\n\n\nHello entered function\n\n\n", customer.first_name)
			return render(request, 'order/orderform_withcart.html', {"form_data": customer, "cart": cart, "cart_items_total": cart.get_cart_total()[0], "cart_items_total_afterdiscount":  cart.get_cart_total()[1]})
		else:
			return redirect('accounts:cart')
	else:
		return redirect("accounts:login")

def order_summary(request, context):
	return render(request, 'order/order_summary.html', context)

def order_buynow(request, uid):
	if request.user.is_authenticated:
		no_of_same_books = request.GET.get('no_of_books')
		customer = request.user
		book = Book.objects.get(uid = uid)
		return render(request, 'order/orderbuynow_withcart.html', {"form_data": customer, "book":book})
		pass



def order_list(request):
	my_order = Order.objects.filter(customer = request.user).order_by('-created_at')
	# print(dir(my_order[0]))
	# print(my_order[0].orderitem_set.all())
	# paginator = Paginator(my_order, 5)
	# page = request.GET.get('page')
	# myorder = paginator.get_page(page)

	return render(request, 'order/orderlist.html', {"myorders": my_order})

def order_details(request, id):
	order_summary = get_object_or_404(Order, id=id)

	if order_summary.customer_id != request.user.id:
		return redirect('store:index')

	orderedItem = OrderItem.objects.filter(order_id=id)
	context = {
		"o_summary": order_summary,
		"o_item": orderedItem
	}
	return render(request, 'order/details.html', context)

class pdf(View):
    def get(self, request, id):
        try:
            query=get_object_or_404(Order,id=id)
        except Exception as e:
            print(e)
        context={
            "order":query
        }
        article_pdf = renderPdf('order/pdf.html',context)
        return HttpResponse(article_pdf,content_type='application/pdf')

