from django.urls import path
from home.views import *

app_name = "home"
urlpatterns = [
    path('', index, name="index"),
    path('allbooks/', allbooks, name="allbooks"),
    path('search/', book_search, name="search"),
    path('allbooks/category/<cat_id>', get_book_category, name="category_filter"),

]
