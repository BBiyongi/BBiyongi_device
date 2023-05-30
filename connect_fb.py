from module import firebase_db

import pickle
import os.path

import requests
import json

from geopy.geocoders import Nominatim
import math


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

# db_data 파일에 있는, 이미 검사한 데이터인지 확인


def fileopen(file, target):
    with open(file, 'r', encoding='UTF8') as file:
        text = file.read()

        if target in text:
            flag = True
        else:
            flag = False

    return flag


# AED API 호출을 위한 기본 정보
base_url = "http://openapi.seoul.go.kr:8088/67565a74456b69363936614c56504f/json/tbEmgcAedInfo"
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
print(total_data)
print(len(total_data))

keys = ["BUILDADDRESS", "BUILDPLACE", "WGS84LON", "WGS84LAT"]
extracted_data = [{key: item[key] for key in keys} for item in total_data]
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
print(extracted_data)
print(len(extracted_data))


fb = firebase_db.FirebaseDB()

filename = 'db_data.pickle'

print(fb.get())  # dict 형태
print(fb.get().keys())

# 사건 data 담을 파일 생성
if os.path.isfile(filename):
    print("파일이 이미 생성되어 있음")
else:
    open(filename, "w")

total_key = fb.get().keys()  # key 값만 저장
for k in total_key:
    if fileopen(filename, k):
        continue
    else:
        detect_data = fb.get(k).get('detect')
        if detect_data == '2':
            address_data = fb.get(k).get('address')
            print(address_data)

            geo = geocoding(address_data)
            print(geo[0])
            print(geo[1])

            my_longitude = geo[0]
            my_latitude = geo[1]

            # 가장 가까운 장소 찾기
            nearest_place = find_nearest_place(
                my_latitude, my_longitude, extracted_data)
            print(nearest_place)

            aed_place = nearest_place['BUILDADDRESS'] + \
                nearest_place['BUILDPLACE']
            print(aed_place)

            # 추가할 데이터
            data = {'AED': aed_place}

            # 데이터를 추가할 컬렉션 경로
            collection_path = '/' + k
            print(collection_path)

            # 데이터 추가
            fb.add_data(collection_path, data)


'''
# 해당 사건 data를 불러온 적이 있다면, load 해오고 없다면 새로 추가함
if os.path.isfile(filename):
    with open(filename, 'rb') as f:
        current_data = str(pickle.load(f))
else:
    if fileopen(filename, list(fb.get().keys())[-1]) == False:

    with open(filename, 'wb') as f:
        pickle.dump(list(fb.get().keys())[-1], f)
    # 파일에서 디바이스 uuid 로드
    with open(filename, 'rb') as f:
        current_data = str(pickle.load(f))
'''
