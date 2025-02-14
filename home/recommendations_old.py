from Books.models import Book, Review
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

def generateRecommendation(request):
    movie=Book.objects.all()
    rating=Review.objects.all()
    x=[] 
    y=[]
    A=[]
    B=[]
    C=[]
    D=[]
    #Movie Data Frames
    for item in movie:
        x=[item.uid,item.name,item.coverpage,item.category, item.slug, item.price] 
        y+=[x]
    # movies_df = pd.DataFrame(y,columns=['movieId','title','movieduration','image','genres'])
    movies_df = pd.DataFrame(y,columns=['BookUid','Name','Image','Category','slug', 'price'])
    print("Books DataFrame")
    print(movies_df)
    print(movies_df.dtypes)
    #Rating Data Frames
    print(rating)
    for item in rating:
        A=[item.customer.id,item.book.uid,item.review_star]
        B+=[A]
    # rating_df=pd.DataFrame(B,columns=['userId','movieId','rating'])
    rating_df=pd.DataFrame(B,columns=['UserUid','BookUid','rating'])
    print("Review data Frame", rating_df)
    # rating_df['UserUid']=rating_df['UserUid'].astype(str).astype(np.int64)
    # rating_df['BookUid']=rating_df['BookUid'].astype(str).astype(np.int64)
    rating_df['rating']=rating_df['rating'].astype(str).astype(np.float64)
    print(rating_df)
    print(rating_df.dtypes)
    if request.user.is_authenticated:
        userid=request.user
        print("\n\n\n\n\nUser is this",userid,"\n\n\n\n\n")
        #select related is join statement in django.It looks for foreign key and join the table
        userInput=Review.objects.select_related('book').filter(customer=userid)
        if userInput.count()== 0:
            recommenderQuery=None
            userInput=None
        else:
            for item in userInput:
                C=[item.book.name,item.review_star]
                D+=[C]
            inputMovies=pd.DataFrame(D,columns=['Name','rating'])
            print("Read Books by user dataframe")
            inputMovies['rating']=inputMovies['rating'].astype(str).astype(np.float64)
            print(inputMovies.dtypes)

            #Filtering out the movies by title
            inputId = movies_df[movies_df['Name'].isin(inputMovies['Name'].tolist())]
            #Then merging it so we can get the movieId. It's implicitly merging it by title.
            inputMovies = pd.merge(inputId, inputMovies)
            # #Dropping information we won't use from the input dataframe
            # inputMovies = inputMovies.drop('year', 1)
            #Final input dataframe
            #If a movie you added in above isn't here, then it might not be in the original 
            #dataframe or it might spelled differently, please check capitalisation.
            print(inputMovies)

            #Filtering out users that have watched movies that the input has watched and storing it
            userSubset = rating_df[rating_df['BookUid'].isin(inputMovies['BookUid'].tolist())]
            print(userSubset.head())

            #Groupby creates several sub dataframes where they all have the same value in the column specified as the parameter
            userSubsetGroup = userSubset.groupby(['UserUid'])
            
            #print(userSubsetGroup.get_group(7))

            #Sorting it so users with movie most in common with the input will have priority
            userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)

            print(userSubsetGroup[0:])


            userSubsetGroup = userSubsetGroup[0:]


            #Store the Pearson Correlation in a dictionary, where the key is the user Id and the value is the coefficient
            pearsonCorrelationDict = {}

        #For every user group in our subset
            for name, group in userSubsetGroup:
            #Let's start by sorting the input and current user group so the values aren't mixed up later on
                group = group.sort_values(by='BookUid')
                inputMovies = inputMovies.sort_values(by='BookUid')
                #Get the N for the formula
                nRatings = len(group)
                #Get the review scores for the movies that they both have in common
                temp_df = inputMovies[inputMovies['BookUid'].isin(group['BookUid'].tolist())]
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
            recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
            recommendation_df['BookUid'] = tempTopUsersRating.index
            recommendation_df.head()

            recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
            print("\n\nRecommendation_df\n\n", recommendation_df)
            recommender=movies_df.loc[movies_df['BookUid'].isin(recommendation_df.head(4)['BookUid'].tolist())]
            print("\n\n\n\n\nFinal recommendations",recommender)
            return recommender.to_dict('records')