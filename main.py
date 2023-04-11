"""
작성자 정보: 황승현 / 전남대학교 전자컴퓨터공학부 전자정보통신공학전공 / ggg06139@gmail.com
코드 기능: 모바일로부터 받은 좌표로 드론이 이동하며 라이다를 이용해 자율비행합니다. 또한 실시간으로 드론의 위치와 영상을 서버로 전송합니다.
최종 수정 시간: 2023년 4월 10일 23:23
"""

import socket
from collections import deque
from dronekit import connect
from _thread import *
from drone import *

lidar_q = deque()
target_q = deque()

# TCP/IP 소켓 연결
HOST = '168.131.153.213'  
PORT = 9999
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 스레드 생성
cap_thread = camera_thread()
start_new_thread(lidar, (0, 0))
start_new_thread(listen_data_from_django, (client_socket, ))
start_new_thread(send_video_stream, (0, ))

# 비행 변수 설정
target_x, target_y = get_target_coordinate(client_socket, target_q)
first_altitude = 10
airspeed = 10

# 연결
vehicle = connect('/dev/ttyUSB0', wait_ready=True, heartbeat_timeout=15)

# 시동
arm()

# 이륙
takeoffing(first_altitude)

# 이동
moving(client_socket, target_x, target_y, airspeed)

# 종료
vehicle.close()