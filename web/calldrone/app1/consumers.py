import json
from collections import deque
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer

# 장고 서버 실행시 WSConsumer class가 생성된다.
class WSConsumer(AsyncWebsocketConsumer):
    print("WSConsumer class생성완료")
    
    # 외부 드론으로부터 들어오는 위치정보 데이터를 담고있는 Queue자료구조
    data_from_drone = deque([])
    
    # 클라이언트 단에서 웹소켓 연결요청을 하면 connect함수가 실행 된다
    # 연결이 끊어지면 connect함수는 종료 된다
    async def connect(self):
        print('connect함수 실행')
        await self.accept()
        
        
        # 사용자가 새로 지도페이지에 접속했기 때문에
        # data_from_drone 내부값을 비워주고 새로 갱신한다.
        print('위치정보갱신')
        self.data_from_drone.clear()

        # 클링러 후 WHILE문 바로 진입시 len(self.data_from_drone) == 0:에 바로 걸리기 때문에 텀을 주고 진입
        await sleep(3)

        while True:
            # 사용자가 다른페이지로 GET요청시 빠져나가기
            if 'stop' in self.data_from_drone:
                self.data_from_drone.clear()
                break
            
            # 들어온은 좌표값이 있의면 브라우저로 보내주기
            if self.data_from_drone:
                x, y = self.data_from_drone.popleft()
                await self.send(json.dumps({'message1' : x, 'message2' : y }))
                await sleep(2)

            # 들어오는 좌표값이 없을 때 == 즉 아직 배송중 상태일 때
            if len(self.data_from_drone) == 0:
                break