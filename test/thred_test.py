
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

def a():
    while True:
        a = person_detection(next(cap_thread))
        print(a)

# 카메라 스레드 객체 생성
cap_thread = camera_thread()
a()
