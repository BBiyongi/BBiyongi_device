from module import firebase_db
import datetime

fb = firebase_db.FirebaseDB()

# print(datetime.datetime.now())
# print(str(datetime.datetime.now()))

fb.update({"datetime1": {
    "info": {
        "camID": "id"
    },
    "content": {
        "detect": "1",
        "video": "video_link",
        "time": "datetime",
    }
}})
