"""
작성자 정보: 황승현 / 전남대학교 전자컴퓨터공학부 전자정보통신공학전공 / ggg06139@gmail.com
코드 기능: 라이다를 구동하는 기능을 담당하는 모듈입니다.
최종 수정 시간: 2023년 4월 10일 23:25 
"""

import time
import PyLidar2

# 라이다 구동
def lidar(queue, port="/dev/ttyUSB0", timeout=30):
    lidar = PyLidar2.YdLidarX4(port)

    try:
        if lidar.Connect():
            # 디바이스 정보 출력
            print(lidar.GetDeviceInfo())
            gen = lidar.StartScanning()

            start_time = time.monotonic()
            while time.monotonic() - start_time < timeout:
                data = next(gen)
                queue.put(data[0])
                print(data[0])

            lidar.StopScanning()
            lidar.Disconnect()
            print('Lidar scanning completed!')
        else:
            print("Error occurred! - connecting to device")
            lidar.StopScanning()
            lidar.Disconnect()

    except:
        print('Error occurred! - scanning with Lidar')
        lidar.StopScanning()
        lidar.Disconnect()

    while True:
        queue.put(2000)
        time.sleep(2)