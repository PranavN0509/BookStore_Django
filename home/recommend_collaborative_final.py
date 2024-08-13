from Books.models import Book, Review
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

def generateCollabRecommendation(request):
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
    books_df = pd.DataFrame(y,columns=['BookUid','Name','Category'])
    print("Books DataFrame")
    print("\n\n")
    print(books_df)
    print(books_df.shape)
    print(books_df.dtypes)
    print("\n\n")




    #Rating Data Frames
    print(rating)
    for item in rating:
        A=[item.customer.id,item.book.uid,item.review_star]
        B+=[A]
    # rating_df=pd.DataFrame(B,columns=['userId','movieId','rating'])
    rating_df=pd.DataFrame(B,columns=['UserUid','BookUid','rating'])
    print("Reviews Dataframe")
    print("\n\n")
    print(rating_df)
    rating_df['rating']=rating_df['rating'].astype(str).astype(np.float64)
    print(rating_df)
    print(rating_df.shape)
    print(rating_df.dtypes)
    print("\n\n")



    if request.user.is_authenticated:
        userid=request.user
        print("\n\n\nUser is this",userid,"\n\n\n")
        #select related is join statement in django.It looks for foreign key and join the table
        userInput=Review.objects.select_related('book').filter(customer=userid)
        if userInput.count()== 0:
            recommenderQuery=None
            userInput=None
        else:
            for item in userInput:
                C=[item.book.name,item.review_star]
                D+=[C]
            inputBooks=pd.DataFrame(D,columns=['Name','rating'])
            print("Read Books by user dataframe")
            inputBooks['rating']=inputBooks['rating'].astype(str).astype(np.float64)
            print(inputBooks.dtypes)

            #Filtering out the books by title
            inputId = books_df[books_df['Name'].isin(inputBooks['Name'].tolist())]
            #Then merging it so we can get the BookUid. It's implicitly merging it by title.
            inputBooks = pd.merge(inputId, inputBooks)
            #Final input dataframe
            #If a book you added in above isn't here, then it might not be in the original dataframe or it might spelled differently, please check capitalisation.
            print(inputBooks)

            #Filtering out users that have read books that the input has read and storing it
            userSubset = rating_df[rating_df['BookUid'].isin(inputBooks['BookUid'].tolist())]
            print(userSubset.head())

            #Groupb by creates several sub dataframes where they all have the same value in the column specified as the parameter
            userSubsetGroup = userSubset.groupby(['UserUid'])
            
            #print(userSubsetGroup.get_group(7))

            #Sorting it so users with book most in common with the input will have priority
            userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)

            print("\n\nUsersubsetgriup\n\n",userSubsetGroup[0:])


            userSubsetGroup = userSubsetGroup[0:]


            #Store the Pearson Correlation in a dictionary, where the key is the user Id and the value is the coefficient
            pearsonCorrelationDict = {}

        #For every user group in our subset
            for name, group in userSubsetGroup:
            #Let's start by sorting the input and current user group so the values aren't mixed up later on
                group = group.sort_values(by='BookUid')
                inputBooks = inputBooks.sort_values(by='BookUid')
                #Get the N for the formula
                nRatings = len(group)
                #Get the review scores for the books that they both have in common
                temp_df = inputBooks[inputBooks['BookUid'].isin(group['BookUid'].tolist())]
                #And then store them in a temporary buffer variable in a list format to facilitate future calculations
                tempRatingList = temp_df['rating'].tolist()
                #Let's also put the current user group reviews in a list format
                tempGroupList = group['rating'].tolist()
                #Now let's calculate the pearson correlation between two users, so called, x and y
                Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
                Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
                Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)
                
                #If the denominator is different than zero, then divide, else, 0 correlation.
                if Sxx != 0 and Syy != 0:
                    pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
                else:
                    pearsonCorrelationDict[name] = 0

            print(pearsonCorrelationDict.items())

            pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
            pearsonDF.columns = ['similarityIndex']
            pearsonDF['UserUid'] = pearsonDF.index
            pearsonDF.index = range(len(pearsonDF))
            print(pearsonDF.head())

            topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:]
            print("Topusershead",topUsers.head())
            print("Topusershead",topUsers.dtypes)
            topUsers['UserUid']=topUsers['UserUid'].apply(lambda x: x[0])
            topUsersRating=topUsers.merge(rating_df, left_on='UserUid', right_on='UserUid', how='inner')
            # topUsersRating=topUsers.(rating_df, left_on='UserUid', right_on='UserUid', how='inner')
            topUsersRating.head()

            #Multiplies the similarity by the user's ratings
            topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']
            topUsersRating.head()


            #Applies a sum to the topUsers after grouping it up by userId
            tempTopUsersRating = topUsersRating.groupby('BookUid').sum()[['similarityIndex','weightedRating']]
            tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']
            tempTopUsersRating.head()

            #Creates an empty dataframe
            recommendation_df = pd.DataFrame()
            #Now we take the weighted average
            recommendation_df['weighted_average_recommendation_score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
            recommendation_df['BookUid'] = tempTopUsersRating.index
            recommendation_df.head()
            recommendation_df = recommendation_df.sort_values(by='weighted_average_recommendation_score', ascending=False)
            print("\n\nRecommendation_df\n\n", recommendation_df.head())
            print(recommendation_df['BookUid'].tolist())
            return recommendation_df['BookUid'].tolist()[0:4]