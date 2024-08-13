from django.urls import path
from order.views import *

app_name = "order"
urlpatterns = [
	path('', order_list, name="order_list"),
	path('<int:id>', order_details, name="order_details"),
	path('order-list/', order_list, name="order-list"),
	path('order-checkout/', order_create, name="order-create"),
	path('order-buynow/<uid>', order_buynow, name="order-buynow"),
	path('order-summary/<uid>/', order_summary, name="order-summary"),
	path('pdf/<int:id>', pdf.as_view(), name="pdf"),
]