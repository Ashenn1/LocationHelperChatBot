
import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import sqlite3
from re import finditer

#  ------------------------ Fill this with your page access token! -------------------------------

#PAGE_ACCESS_TOKEN = "EAADYT2qohbEBAB7z8eYxe8NXqmSry9qs53xHdKZAPKhk76hZCgeMtfHcQZBJXcLDPkzUG4OroYZBULeQNvuXucNIAScFcnnGZAwBOisXsWHz4m6xj64I8Bi4mZBnyzIKVZBwWTODinatzwYgCYE8sDt2Fk6S5Yk1sZAvBE1LJZCyrCQZDZD"
VERIFY_TOKEN = "1111552222"




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

        for word1 in place_name.split():
            if editDistDP(word1, word2, len(word1), len(word2)) <= 2:
                return True

    return  False


def putSynonym(message ):
    conn = sqlite3.connect("db.sqlite3")  # the name of the databases is db.
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









def post_facebook_message(fbid, recevied_message):
    flag=False
    conn = sqlite3.connect("db.sqlite3")  # the name of the databases is db.
    tokens=re.search(r"hi|hey|hello",recevied_message)
    if tokens:
        reply='Hi there ! iam a chatbot that can help with giving details/addresses of locations you want to know about, ask me anything'
        flag=True

    tokens = re.search(r"same as| equivalent | synonym ", recevied_message)
    if tokens:
        reply += 'in the else'
        if (putSynonym(recevied_message)):
            reply = 'Synonym is added'
            flag = True


    else:
        reply+='in the else'
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
        if flag == False:

            for row in cursor:
                placeName = str(row[0]).lower()
                if check_closeness(recevied_message, placeName):
                    reply = "Did you mean " + placeName + "?" + "\n" + "it's address is : " + str(row[1])
                    flag = True
                    break


        if flag==False:
            reply += 'I didnt understand, sorry'


    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAACgc9gL7bYBAMdaDOuH8V2pfYXJloBPuNDMWcZAAyKjf5ZA1m4coWd4amAE9nySHsCx8zEM6cf9cDqN2t3qmEsZBPrcWoPOe6z45Fe4hmkxSdmu4Vn4mZAgC6roRNXX2ozYjh12vOVpoHZCEgHNaDzQvzb9FKLKRP5zwxZBgIeQZDZD'
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":reply}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())


# Create your views here.
class locationHelperBotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)    
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])

        return HttpResponse()    