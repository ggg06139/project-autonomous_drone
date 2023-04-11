"""
작성자 정보: 황승현 / 전남대학교 전자컴퓨터공학부 전자정보통신공학전공 / ggg06139@gmail.com
코드 기능: 드론 비행과 관련된 기능을 담당하는 모듈입니다. 드론 시동, 이륙, 착륙, 이동, 복귀 등의 함수가 포함됩니다.
최종 수정 시간: 2023년 4월 11일 01:20
"""

import time
import math
from dronekit import VehicleMode, LocationGlobalRelative
from camera import *
from communication import *

# 드론 시동 함수
def arm():
    # pre-arm 체크
    print("Starting pre-arm check")
    while not vehicle.is_armable:
        print(" Waiting for pre-arm check ...")
        time.sleep(1)
    print("Pre-arm check completed!")

    # 자율 비행 모드로 변경
    print("Set Vehicle.mode = GUIDED (currently: %s)" % vehicle.mode.name)
    vehicle.mode = VehicleMode("GUIDED")
    while not vehicle.mode.name == 'GUIDED':
        print(" Waiting for mode change ...")
        time.sleep(1)
    print("Mode change completed!")

    # arm 시작
    print("Set Vehicle.armed = True (currently: %s)" % vehicle.armed)
    vehicle.armed = True
    while not vehicle.armed == True:
        print(" Waiting for arming ...")        
        time.sleep(1)
    print("Vehicle arming completed!")


# 드론 이륙 함수
def takeoffing(altitude):
    # 이륙 시작
    print("Taking off!")
    vehicle.simple_takeoff(altitude)

    # 지정된 고도까지 상승
    while True:
        print("Altitude:", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= altitude*0.95:
            print("Reached target altitude!")
            break
        time.sleep(1)


# 드론 착륙 함수
def landing():
    # 착륙 시작
    vehicle.mode = VehicleMode("LAND")
    print("Starting landing")

    # 지면까지 착륙
    while True:
        print("Altitude:", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt <= 0:
            print("Landing Complete!")
            break
        time.sleep(1)


# 드론 이동 후 위치를 반환하는 함수
def get_location_metres(original_location, dNorth, dEast):
    # 지구의 반지름
    R = 6378137.0

    # 좌표의 이동 거리, 방향
    dLat = dNorth/R
    dLon = dEast/(R*math.cos(math.pi*original_location.lat/180))

    # 새로운 위치
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)

    return LocationGlobalRelative(newlat, newlon, original_location.alt)


# 드론 이동 함수
def moving(client_socket, lat, lon, alt, speed=10):
    global lidar_q

    try:
        # 이동 시작
        print("Going towards point!")
        target_point = LocationGlobalRelative(float(lat), float(lon), alt)
        print(f'moving : {lat}, {lon}')
        vehicle.simple_goto(target_point, airspeed=speed)

        # 목표 지점까지 이동
        while True:
            print(f"Altitude: {vehicle.location.global_relative_frame.lat}")
            print(f"Longitude: {vehicle.location.global_relative_frame.lon}")

            # 현재 위치 정보
            current_location = vehicle.location.global_relative_frame
            current_latitude = current_location.lat
            current_longitude = current_location.lon

            # 실시간 좌표 전송
            data = f"{current_latitude} {current_longitude}"
            client_socket.send(data.encode())
            
            # 도착 종료 조건 확인
            if (current_latitude >= lat*0.9999995 and current_latitude <= lat*1.0000005 and 
                current_longitude >= lon*0.9999995 and current_longitude <= lon*1.0000005):
                print("Target place reached!")
                break
            
            # 카메라로 전방 사람 객체를 발견하면 착륙
            if person_detection(next(cap_thread)):
                print("Person detected!")
                landing()
                break

            # 라이다로 전방 물체를 탐지하면 회피
            if len(lidar_q) > 0:
                dist = lidar_q.popleft()

                if dist < 3000:
                    while dist > 3000:
                        # 왼쪽으로 이동할 포인트 계산
                        d_north, d_east = 0, -2
                        left_point = get_location_metres(current_location, d_north, d_east)

                        # 회피 이동
                        vehicle.simple_goto(left_point)

                        # 이동 후 LIDAR 거리 다시 측정
                        time.sleep(0.5)
                        dist = lidar_q.popleft() if lidar_q else 999999

                    # 회피 후 목표 지점 이동 명령
                    vehicle.simple_goto(target_point)

            time.sleep(1)
        landing

    # 긴급 상황 대비 조종기 조작 모드 변경
    except KeyboardInterrupt:
        vehicle.mode = VehicleMode("LOITER")
        try:
            while True:
                print("Now Loiter Mode")
                time.sleep(1)

        # 긴급 상황 대비 호버링 모드 변경
        except KeyboardInterrupt:
            vehicle.mode = VehicleMode("STABILIZE")
            while True:
                print("Now Stabilize Mode")
                time.sleep(1)


# 드론 복귀 함수
def returning():
    # 복귀 시작
    print("Returning to launch")

    # waypoints 다운로드
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

    # 모드 변경
    print("Set Vehicle.mode = RTL (currently: %s)" % vehicle.mode.name)
    vehicle.mode = VehicleMode("RTL")
    while not vehicle.mode.name == 'RTL':
        print(" Waiting for mode change ...")
        time.sleep(1)
    print("Mode change completed!")

    # waypoints까지 이동
    while True:
        print("Altitude:", vehicle.location.global_relative_frame.lat)
        print("Longitude:", vehicle.location.global_relative_frame.lon)
        if vehicle.armed == False:
            print("Reached target place!")
            break
        time.sleep(1)