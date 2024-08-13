from Books.models import Book, Review
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

def generateCollabRecommendation(book_name):
    book=Book.objects.all()
    rating=Review.objects.all()
    x=[] 
    y=[]
    A=[]
    B=[]
    C=[]
    D=[]
 
    #Books Data Frames
    for item in book:
        x=[item.uid,item.name,item.category] 
        y+=[x]
    # movies_df = pd.DataFrame(y,columns=['movieId','title','movieduration','image','genres'])
    books_df = pd.DataFrame(y, columns=['BookUid','Name','Category'])
    print("Books DataFrame")
    print(books_df)
    print("\nBook DataType")
    print(books_df.dtypes)
    print("Book DataFrame Shape: ")
    print(books_df.shape)


    #Rating Data Frames
    for item in rating:
        A=[item.customer.id,item.customer.first_name,item.book.uid,item.review_star]
        B+=[A]
    # rating_df=pd.DataFrame(B,columns=['userId','movieId','rating'])
    rating_df=pd.DataFrame(B, columns=['UserUid','UserF_Name','BookUid','Rating'])
    rating_df['Rating']=rating_df['Rating'].astype(str).astype(np.float64)
    print("\n\nReview data Frame\n")
    print(rating_df)
    print("Review DataType: ")
    print(rating_df.dtypes)
    print("Review DataFrame Shape: ")
    print(rating_df.shape)

    Reviews_merge_with_books = rating_df.merge(books_df, on="BookUid")
    print("\nReviews_merge_with_books\n")
    print(Reviews_merge_with_books.head())
    print("\nReviews_merge_with_books datatypes\n")
    print(Reviews_merge_with_books.dtypes)
    
    
    book_pivot = Reviews_merge_with_books.pivot_table(columns='UserUid', index = "Name", values="Rating")
    book_pivot.fillna(0, inplace=True)
    print("\n\nBook_pivot\n")
    print(book_pivot)
    print("\nBook_pivot Shape: ")
    print(book_pivot.shape)
    book_recommendations = []
    book_index = None
    try:
        book_index = np.where(book_pivot.index == book_name)[0][0]
        print("Book Index: ",book_index)
    except Exception as e:
        print(e)
    finally:
        if(book_index==0):
            book_sparse = csr_matrix(book_pivot)
            model = NearestNeighbors(algorithm='brute')
            model.fit(book_sparse)
            
            distance, suggestion = model.kneighbors(book_pivot.iloc[book_index].values.reshape(1, -1), n_neighbors=5)

            print("distance: ", distance)
            print("suggestion: ", suggestion)

            for i in range(len(suggestion)):
                print("hello")
                print("Name_of_books:",book_pivot.index[suggestion[i]])
                for book in book_pivot.index[suggestion[i]]:
                    if book == book_name:
                        continue
                    book_obj = Book.objects.get(name = book)
                    book_recommendations.append(book_obj)
        elif(book_index):
            book_sparse = csr_matrix(book_pivot)
            model = NearestNeighbors(algorithm='brute')
            model.fit(book_sparse)
            
            distance, suggestion = model.kneighbors(book_pivot.iloc[book_index].values.reshape(1, -1), n_neighbors=5)

            print("distance: ", distance)
            print("suggestion: ", suggestion)

            for i in range(len(suggestion)):
                print("hello")
                print("Name_of_books:",book_pivot.index[suggestion[i]])
                for book in book_pivot.index[suggestion[i]]:
                    if book == book_name:
                        continue
                    book_obj = Book.objects.get(name = book)
                    book_recommendations.append(book_obj)
    return book_recommendations





