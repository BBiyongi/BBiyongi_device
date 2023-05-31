import cv2
from PIL import Image
from torchvision import transforms
import numpy as np
import time
import subprocess
import torch
import keyboard
from datetime import datetime
import onnxruntime as rt

model = rt.InferenceSession('/home/kobot/BBiyongi/drive-download-20230531T081826Z-001/slowfast_base.onnx')
input1_name = sess.get_inputs()[0].name
input2_name = sess.get_inputs()[1].name


w, h = (640, 360)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
cap.set(cv2.CAP_PROP_FPS, 30)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

mean = [0.45, 0.45, 0.45]
std = [0.225, 0.225, 0.225]

cnt = 0

curr_time = datetime.today().strftime("%Y%m%d_%H%M")
video_out = f"./{curr_time}.mp4"
out = cv2.VideoWriter(f'{video_out}', fourcc, 30, (w, h))

# 앞에 96프레임 먼저 녹화
ret, frame = cap.read()
frame = cv2.resize(frame, (256, 256))
frames = frame.transpose(2, 0, 1).reshape(3, 1, 256, 256)

start = time.time()
while len(frames[0]) < 96:
	ret, frame = cap.read()
	
	out.write(frame)
	frame = cv2.resize(frame, (256, 256))
	frame = frame.transpose(2, 0, 1).reshape(3, 1, 256, 256)
	frames = np.append(frames, frame, axis=1)

output_labels = [0 for i in range(15)]

while True:
	ret, frame = cap.read()
	if not ret:
		break
	out.write(frame)
  cnt += 1
	frame = cv2.resize(frame, (256, 256))
	frame = frame.transpose(2, 0, 1).reshape(3, 1, 256, 256)
	frames = np.append(frames, frame, axis=1)
	
  # frames (1, 3, 8, 256, 256), (1, 3, 32, 256, 256) 로 전처리
	model_inputs = frames[:,-96:,:,:]
	slow_path = model_inputs[:, np.arange(0, 96, 12), :, :]
	fast_path = model_inputs[:, np.arange(0, 96, 3), :, :]

	# 전처리한 프레임 모델로 추론
	pred = sess.run(None, {input1_name:slow_path / 255., input2_name: fast_path / 255.})
	
  # 최신 15개 예측값 중 최빈값을 현재 클래스로 생각
	del output_labels[0]
	output_labels.append(np.argmax(pred, axis=1))
	count_list = [output_labels.count(0), output_labels.count(1), output_labels.count(2)]
	current_status = max(enumerate(count_list),key=lambda x: x[1])[0]
	
	if current_status == 1:
		out.release()
		filename = video_out
		curr_time = datetime.today().strftime("%Y%m%d_%H%M")
		subprocess.run(args=[sys.executable, './detection.py', "1", curr_time, filename])
	elif current_status == 2:
		out.release()
		filename = video_out
		curr_time = datetime.today().strftime("%Y%m%d_%H%M")
		subprocess.run(args=[sys.executable, './detection.py', "2", curr_time, filename])
	
	if cnt > 9000: # 5분마다 영상 저장
		cnt = 0
		out.release()
		curr_time = time.strftime('%Y%m%d-%H%M%D')
		video_out = f"./{curr_time}.mp4"
		out = cv2.VideoWriter(f'{video_out}', fourcc, 30, (w, h))
	
	if len(frames[0]) > 9000: # 5분 이전 프레임은 메모리 절약을 위해 변수에서 삭제
		frames = frames[:,1:,:,:]
		frame = frame.transpose(2, 0, 1).reshape(3, 1, 256, 256)
		frames = np.append(frames, frame, axis=1)
		
