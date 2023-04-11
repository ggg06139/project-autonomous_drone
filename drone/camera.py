"""
작성자 정보: 황승현 / 전남대학교 전자컴퓨터공학부 전자정보통신공학전공 / ggg06139@gmail.com
코드 기능: 카메라 프레임을 통해 드론 정면의 사람 객체를 발견하는 함수가 포함되어 있습니다.
최종 수정 시간: 2023년 4월 10일 23:20
"""

import cv2
import torch

# YOLOv5s 모델 다운로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 사람 검출 함수
def person_detection(frame):
    # 프레임 크기 조정
    resized_frame = cv2.resize(frame, (640, 480))

    # YOLOv5s 모델에 프레임 입력
    results = model(resized_frame)

    for result in results.xyxy[0]:
        # 검출된 객체가 사람일 때
        if result[5] == 0:
            # 객체 중심점 좌표 계산
            center_x = (result[0] + result[2]) / 2
            center_y = (result[1] + result[3]) / 2

            # 객체 중심과 프레임 중심의 거리를 계산
            distance = ((center_x - 320) ** 2 + (center_y - 240) ** 2) ** 0.5

            # 프레임 중심과 일정 거리 이내에 객체가 있으면 True를 반환
            if distance < 100:
                return True

    # 검출된 사람이 없으면 False를 반환
    return False


# 카메라 스레드 함수 정의
def camera_thread():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)

    while True:
        # 카메라에서 프레임 추출
        ret, frame = cap.read()
        if not ret:
            continue
        yield frame