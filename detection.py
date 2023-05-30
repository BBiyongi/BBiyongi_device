import pyrebase
import time
from datetime import datetime
import json
import os

aed_location = "seoul "
address = "seoul"
detect = "0"

config={
   "apiKey": "AIzaSyAX_Bgfl03nCEfCNOh1uiuxphveVAzNMxU", #webkey
   "authDomain": "alpha-92011.firebaseapp.com", 
   "databaseURL": "https://alpha-92011-default-rtdb.firebaseio.com/", #database url
   "storageBucket": "alpha-92011.appspot.com" #storage
}

firebase = pyrebase.initialize_app(config)



uploadfile = "./converted.mp4"

s = os.path.splitext(uploadfile)[1]

now = datetime.today().strftime("%Y%m%d_%H%M")
filename = now + s

#Upload files to Firebase
storage = firebase.storage()

storage.child(filename).put(uploadfile)
fileUrl = storage.child(filename).get_url(1) 
print (fileUrl)


 
#save files info in database
db = firebase.database()
if (detect =="2") :

   
   data= {"AED" : aed_location ,
      "address" : address , 
      "detect " : detect ,
      "time" : filename[:-4] ,
      "fileUrl" : fileUrl }
   db.child(str(filename).replace('.mp4', '')).set(data)

else : 
   data= {
      "address" : address , 
      "detect " : detect ,
      "time" : filename[:-4] ,
      "fileUrl" : fileUrl }
   db.child(str(filename).replace('.mp4', '')).set(data)



