from src.base.base_server import BaseServer
from websockets.server import serve
import numpy as np
import json
import asyncio
import time

import sys

from src.utils.json_numpy import numpy_to_json, json_to_numpy
from src.serializer import create_serializer

class WebServer(BaseServer):

    def __init__(self, host="0.0.0.0", port=8000, packaging_type = "json"):
        super().__init__()
        self.host = host
        self.port = port

        self.ws = None
        self._action_queue = asyncio.Queue()
        self._msg_queue = asyncio.Queue()
        self._connected_event = asyncio.Event()

        self.packaging_type = packaging_type
        self.serializer = create_serializer(packaging_type)
        # self.packer = msgpack_numpy.Packer()

    async def start(self):
        # 启动服务器
        async def handler(websocket):
            # 处理客户端的连接和信息
            print("Client connected")
            self.ws = websocket
            self._connected_event.set() # 通知其他协程客户端已连接

            try:
                # 每次收到一个message, sever就会从中解析出action并放入队列中
                async for message in websocket:
                    data = self.serializer.deserialize(message)

                    if data.get("type") == "action":
                        if self.packaging_type == "json":
                            action = json_to_numpy(data["action"]) # json
                        elif self.packaging_type == "pickle" or self.packaging_type == "msgpack":
                            action = data["action"]  # msgpack, pickle
                        await self._action_queue.put(action)
                    else:
                        # 其他消息
                        await self._msg_queue.put(data)


            except Exception as e:
                print("Client disconnected:", e)

            finally:
                print("Closing websocket...")
                if not websocket.closed:
                    await websocket.close()

                self._connected_event.clear()
                self.ws = None
                print("Websocket closed.")

        print(f"WebServer running on ws://{self.host}:{self.port}")
        async with serve(handler, self.host, self.port, max_size = None):
            await asyncio.Future()  # Run forever

    async def _recv_msg(self):
        # 从队列中获取消息
        data = await self._msg_queue.get()
        return data
    
    # -------------------------------------------------
    # 发送 observation
    # -------------------------------------------------
    async def post_obs(self, obs: dict) -> None:
        await self._connected_event.wait()  # 等客户端真正连接

        if self.packaging_type == "json":
            payload = {
                "type": "obs",
                "obs": numpy_to_json(obs) # json
            }
        elif self.packaging_type == "msgpack" or self.packaging_type == "pickle":
            payload = {
                "type": "obs",
                "obs": obs  # msgpack, pickle
            }
        await self._send_msg(payload)

    async def _send_msg(self, payload):
        try:
            packed_payload = self.serializer.serialize(payload)
            await self.ws.send(packed_payload) 

        except Exception as e:
            print("Send failed:", e)


    async def get_action(self, timeout=None) -> np.ndarray:
        try:
            action = await asyncio.wait_for(self._action_queue.get(), timeout=timeout)
            return action
        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for action")
