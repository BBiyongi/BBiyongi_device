import pyrebase
import time
from datetime import datetime
import json
import os
import pickle
import os.path
import requests
import json
from geopy.geocoders import Nominatim
import math
from gtts import gTTS 
from dotenv import load_dotenv
from playsound import playsound 

aed_location = "seoul "
address = "서울 중랑구 "
detect = "2"


# 주소를 위도, 경도로 반환하는 함수
def geocoding(address):
    try:
        geo_local = Nominatim(user_agent='South Korea')  # 지역설정
        location = geo_local.geocode(address)
        geo = [location.latitude, location.longitude]
        return geo

    except:
        return [0, 0]

# 두 지점 사이의 거리 계산 (Haversine 공식 사용)
def calculate_distance(lat1, lon1, lat2, lon2):
    # 지구의 반경 (단위: km)
    radius = 6371.0

    # 라디안 변환
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 좌표 간의 차이 계산
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine 공식 적용
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * \
        math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 거리 계산
    distance = radius * c
    return distance

# 주어진 위도, 경도에서 가장 가까운 장소 찾기
def find_nearest_place(latitude, longitude, places):

    min_distance = float('inf')
    nearest_place = None

    for place in places:
        place_latitude = float(place['WGS84LON'])
        place_longitude = float(place['WGS84LAT'])

        distance = calculate_distance(
            latitude, longitude, place_latitude, place_longitude)

        if distance < min_distance:
            min_distance = distance
            nearest_place = place

    return nearest_place

# AED API 호출을 위한 기본 정보
var = "67565a74456b69363936614c56504f"
base_url = f"http://openapi.seoul.go.kr:8088/{var}/json/tbEmgcAedInfo"
start_index = 1
end_index = 1000
total_data = []

# AED API를 반복 호출하여 데이터 받아오기
while True:
    # URL 설정
    url = f"{base_url}/{start_index}/{end_index}/"

    # API 호출
    response = requests.get(url)
    data = response.json()

    # 받아온 데이터 처리
    aed_list = data['tbEmgcAedInfo']['row']
    total_data.extend(aed_list)

    # 다음 페이지가 있는지 확인
    if len(aed_list) < end_index - start_index + 1:
        break

    # 다음 페이지로 이동
    start_index += 1000
    end_index += 1000

# 전체 데이터 출력


keys = ["BUILDADDRESS", "BUILDPLACE", "WGS84LON", "WGS84LAT"]
extracted_data = [{key: item[key] for key in keys} for item in total_data]





config={
   "apiKey": "AIzaSyAX_Bgfl03nCEfCNOh1uiuxphveVAzNMxU", #webkey
   "authDomain": "alpha-92011.firebaseapp.com", 
   "databaseURL": "https://alpha-92011-default-rtdb.firebaseio.com/", #database url
   "storageBucket": "alpha-92011.appspot.com" #storage
}

firebase = pyrebase.initialize_app(config)



uploadfile = "/home/kobot/BBiyongi/test_video.mp4"

s = os.path.splitext(uploadfile)[1]

now = datetime.today().strftime("%Y%m%d_%H%M")
filename = now + s

#Upload files to Firebase
storage = firebase.storage()

storage.child(filename).put(uploadfile)
fileUrl = storage.child(filename).get_url(1) 


 
#save files info in database
db = firebase.database()
address = db.child("cam1_address").get().val()
print(address)
           

if (detect =="2") :
   geo = geocoding(address)
   my_longitude = geo[0]
   my_latitude = geo[1]

   # 가장 가까운 장소 찾기
   nearest_place = find_nearest_place(my_latitude, my_longitude, extracted_data)
   aed_location = nearest_place['BUILDADDRESS'] + nearest_place['BUILDPLACE']
   
   data= {"AED" : aed_location ,
      "address" : address , 
      "detect " : detect ,
      "time" : filename[:-4] ,
      "fileUrl" : fileUrl }
   db.child(str(filename).replace('.mp4', '')).set(data)
   
   text = f"심정지 환자가 발생했습니다. AED의 위치는 {aed_location}입니다 빠르게 이동하세요 " 

   text_to_voice = gTTS(text = text , lang="ko")
   text_to_voice.save("text.mp3")
   playsound("siren.mp3")
   for i in range(0,5):
      playsound("text.mp3")

else : 
   data= {
      "address" : address , 
      "detect " : detect ,
      "time" : filename[:-4] ,
      "fileUrl" : fileUrl }
   db.child(str(filename).replace('.mp4', '')).set(data)




