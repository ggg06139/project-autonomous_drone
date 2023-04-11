"""
작성자 정보: 황승현 / 전남대학교 전자컴퓨터공학부 전자정보통신공학전공 / ggg06139@gmail.com
코드 기능: 서버와의 통신에 관련된 기능을 담당하는 모듈입니다. 데이터 수신, 전송, 목적 좌표 수신 등의 함수가 포함됩니다.
최종 수정 시간: 2023년 4월 10일 23:10 
"""

import cv2
import time
import socket

# 서버로부터 데이터를 수신하는 함수
def listen_data_from_django(client_socket):
    global target_q

    # 소켓으로부터 데이터를 수신
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            data = data.decode()
            target_q.append(data)
            print('receive data : ', data)

        except ConnectionResetError as e:
            break

    # 소켓 연결 종료
    print('Django disconnected')
    client_socket.close()


# 서버로 비디오를 전송하는 함수
def send_video_stream(UDP_IP='168.131.153.213', UDP_PORT=9505):
    # 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 비디오 캡처 시작
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        flattened_frame = frame.flatten()
        byte_string = flattened_frame.tobytes()

        for i in range(20):
            start_index = i * 46080
            end_index = (i + 1) * 46080
            sock.sendto(bytes([i]) + byte_string[start_index:end_index], (UDP_IP, UDP_PORT))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# 모바일로부터 목적 좌표를 얻어 반환하는 함수
def get_target_coordinate(client_socket, target_q):
    # 초기 메시지 전송
    message = '0 0'
    
    while True:
        client_socket.send(message.encode())
        time.sleep(2)
        print(target_q)

        # 큐에 하나의 데이터가 있는 경우, 그 값을 받아서 목적지 좌표로 설정
        if len(target_q) == 1:
            data = target_q[0]
            target_x, target_y = data.split()
            break

        # 큐에 여러개의 데이터가 있는 경우, 가장 마지막 데이터를 받아서 목적지 좌표로 설정
        if len(target_q) != 0:
            data = target_q.pop()
            target_x, target_y = map(float, data.split())
            print(target_x, target_y)
            break
    
    return target_x, target_y