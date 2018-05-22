import re
import sqlite3
from re import finditer


def editDistDP (str1 , str2 , len1 , len2): # returns the min edit operations to turn str1 to str2 or vice versa.
    dp=[[0 for x in range(len2+1)] for x in range(len1+1)]   #initializing 2D array/list


    for i in range(len1+1):
        for j in range(len2+1):

            if i == 0:
                dp[i][j]=j

            elif j == 0:
                dp[i][j]=i

            elif str1[i-1] == str2[j-1]:
                dp[i][j]=dp[i-1][j-1]

            else:
                dp[i][j]= 1 + min(dp[i][j-1], dp[i-1][j] , dp[i-1][j-1])


    return dp[len1][len2]




def check_closeness (message , place_name ):
    for word2 in message.split():

        for word1 in placeName.split():
            print("Edit distance : " + str(editDistDP(word1, word2, len(word1), len(word2))))
            print("word 1 : " + word1)
            print("word 2 : " + word2)
            if editDistDP(word1, word2, len(word1), len(word2)) <= 2:
                return True

    return  False



def putSynonym(message ):
    matchedPlace=""
    tup=()
    words=message.split()
    cursor=conn.execute(''' select PlaceName,Address from Places  ''')
    for row in cursor:
        placeName=str(row[0]).lower()
        for match in finditer(placeName,message):
            tup=match.span() # gets the start and end index of the match in a tuple ex: (21,45)
            matchedPlace=placeName

    try:
        print("matched place : ",matchedPlace.rstrip())
        print("Synonym : ",words[0].strip())
        cursor = conn.execute(''' insert into Synonyms  (placeID, Synonym) values 
        ( (select Places.PlaceId from Places where PlaceName = ? COLLATE NOCASE ) , ?)''', ( matchedPlace.strip() , words[0].strip() ) )
        conn.commit()
        return True
    except:
        return False







recevied_message="kjrkf"


recevied_message=recevied_message.lower()

print(recevied_message)

reply=""

flag=False
conn = sqlite3.connect("db.sqlite3")  # the name of the databases is db.
tokens=re.search(r"hi|hey|hello",recevied_message)
if tokens:
        reply='Hi there ! iam a chatbot that can help with giving details/addresses of locations you want to know about, ask me anything'
        flag=True


tokens=re.search(r"same as| equivalent | synonym ",recevied_message)
if tokens:
    if(putSynonym(recevied_message)):
        reply ='Synonym is added'
        flag=True


else:
        cursor = conn.execute(''' select PlaceName,Address from Places  ''')
        for row in cursor:
            placeName = str(row[0]).lower()
            tokens = re.search(placeName, recevied_message)
            if tokens:
                reply=str(row[1])
                flag=True

        if flag==False:
            cursor =conn.execute(''' select PlaceID,Synonym from Synonyms  ''')
            for row in cursor:
                syn = str(row[1]).lower()
                tokens=re.search(syn, recevied_message)
                if tokens:
                   cur2=conn.execute('''select Address from Places where Places.PlaceID= ? ''', (int(row[0]),) )
                   for r in cur2 :
                       reply=r[0]
                       flag=True




        cursor = conn.execute(''' select PlaceName,Address from Places  ''')
        if flag==False :

            for row in cursor:
                placeName = str(row[0]).lower()
                if check_closeness(recevied_message,placeName) :
                    reply="Did you mean "+ placeName + "?" +"\n"+ "it's address is : " + str(row[1])
                    flag=True
                    break


if flag==False:
            reply+= 'I didnt understand, sorry'
            received_former=recevied_message # to save up older messages.



print(reply)



#msg="cfc is equivalent to cairo festival city mall"



#tokens=re.search(r"same as| equivalent | synonym ",msg)

#tup1=()

#for match in finditer(r"cairo festival city mall" , "cfc is equivalent to cairo festival city mall" ):
   # print(match.span(),match.group())
   # tup1=match.span()

#print(msg[ tup1[0] : tup1[1] ] )


