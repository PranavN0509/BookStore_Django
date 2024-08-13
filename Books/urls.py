from django.urls import path
from Books.views import *

app_name = "Books"
urlpatterns = [
    path('<slug>/', get_book, name="get_book"),
    path('writers/<slug>/', get_writer, name="get_writer"),
    # path('book-review/', book_review_submit, name="submit-review")
    
]
