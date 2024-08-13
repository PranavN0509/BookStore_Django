from django.shortcuts import render, redirect
from Books.models import Book
from accounts.models import *
from django.contrib.auth.models import User
from .recomm_collab import generateCollabRecommendation

# Create your views here.
def get_book(request, slug):
    reviewPermit = False
    if request.user.is_authenticated:
        print("\n\n\n\n\n", "Hello we are inside authenticated")
        book = Book.objects.get(slug = slug)
        review_obj_forcheck = Review.objects.filter(customer = request.user, book = book)
        if review_obj_forcheck.exists():
            reviewPermit = False
        else:
            reviewPermit = True
        if request.method == 'POST':
            print("\n\n\n\n\n", "Hello we are inside post")
            try:
                print("\n\n\n\n\n", "Hello we are inside try")
                customer = User.objects.get(username=request.user)
                uid = request.POST.get('Book_uid')
                book = Book.objects.get(uid = uid)
                ratingnum = request.POST.get('Rating_num')
                reviewtext = request.POST.get('Review_text')
                review_obj = Review.objects.create(customer = customer, book = book, review_star = ratingnum, review_text= reviewtext)
                print("Review object created")
                review_obj.save()
                print("Review object saved")
                book.totalrating = book.get_average_rating()
                book.totalreview+=1
                book.save()
                print("Book object saved")

            except Exception as e:
                print(e)
            finally:
                print("\n\nHello object saved")
                return redirect(f"/book/{book.slug}")
            
            
    try:
        print("Inside try book 1")
        book = Book.objects.get(slug = slug)
        recommended = []
        review_obj_all = {}
        review_count = 0
        if book.totalreview !=0:
            review_obj_all = Review.objects.filter(book = book)
            review_count = Review.objects.filter(book = book)[0]
            print("Inside try book 2")
            recommended = generateCollabRecommendation(book.name)
        context={'book':book, "reviewPermit": reviewPermit, 'review_obj_all':review_obj_all, 'review_count':review_count, 'Recommendations':recommended}
        return render(request, 'Book/book.html', context)
    except Exception as e:
        print("Error in get_books function ",e)
    


def get_writer(request, slug):
    try:
        print("inside try writer")
        writer = Writer.objects.get(slug = slug)
        books = Book.objects.filter(writer = writer)
        context = {'writer':writer, "Books":books}
        return render(request, 'Book/writer.html', context)
    except Exception as e:
        print("\n\nError in get_writer function ",e)
    