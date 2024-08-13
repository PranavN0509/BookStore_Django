from Books.models import Book
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend(book_name):
    book=Book.objects.all()
    x=[] 
    y=[]
    #Books Data Frames
    for item in book:
        x=[item.name,item.uid,item.description,item.writer.name,item.category.name] 
        y+=[x]
    books_df = pd.DataFrame(y,columns=['Name','BookUid','Description','Writer','Category'])
    # print("Books DataFrame")
    # print("\n")
    # print(books_df)
    books_df['Tags'] = books_df['Category'] + " "+ books_df['Description']+" " + books_df['Writer']
    books_df['Tags'] = books_df['Tags'].apply(lambda x: x.lower())
    # print("\nBooks DataTypes\n",books_df.dtypes)
    # print(books_df['Name'][0])
    books_df = books_df.drop(columns=['Description', 'Category'])
    # print("\n\n")
    # print(books_df)
    # print("\nFinal Books DataTypes\n",books_df.dtypes)
    # print("\nSingle Tag Display\n",books_df['Tags'][15])



    cv=CountVectorizer(max_features=5000, stop_words='english')
    vector=cv.fit_transform(books_df['Tags'].values.astype('U')).toarray()
    # print("\nVector Shape: ",vector.shape,"\n")
    # print("Feeature Names:", cv.get_feature_names_out())
    similarity=cosine_similarity(vector)


    # The below is the sample of how the data is being fed and recommmendations are generated
    # books_df[books_df['title']=="The Godfather"].index[0]
    # distance = sorted(list(enumerate(similarity[2])), reverse=True, key=lambda vector:vector[1])
    # for i in distance[0:5]:
    #     print(books_df.iloc[i[0]].Name)
    books_recomm = []
    index_book=books_df[books_df['Name']==book_name].index[0]
    print("\nIndex: ", index_book)
    distance = sorted(list(enumerate(similarity[index_book])), reverse=True, key=lambda x:x[1])
    print("\n\n\nContent Based Recommendations of Books\n")
    for i in distance[0:7]:
        if books_df.iloc[i[0]].Name==book_name:
            continue
        print(books_df.iloc[i[0]].Name)
        books_recomm.append(Book.objects.get(name = books_df.iloc[i[0]].Name))
    return books_recomm

    # recommend("Mahabharata")