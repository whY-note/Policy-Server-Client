from src.base.base_server import BaseServer
from websockets.server import serve
import numpy as np
import json
import asyncio
from src.utils.json_numpy import numpy_to_json, json_to_numpy
import time

import sys
import src.utils.msgpack_numpy as msgpack_numpy
import pickle

class WebServer(BaseServer):

    def __init__(self, host="0.0.0.0", port=8000, packaging_type = "json"):
        super().__init__()
        self.host = host
        self.port = port

        self._ws = None
        self._action_queue = asyncio.Queue()
        self._msg_queue = asyncio.Queue()
        self._connected_event = asyncio.Event()

        self.packaging_type = packaging_type

        self.packer = msgpack_numpy.Packer()

    async def start(self):
        # 启动服务器
        async def handler(websocket):
            # 处理客户端的连接和信息
            print("Client connected")
            self._ws = websocket
            self._connected_event.set() # 通知其他协程客户端已连接

            try:
                # 每次收到一个message, sever就会从中解析出action并放入队列中
                async for message in websocket:
                    if self.packaging_type == "json":
                        data = json.loads(message)  # json
                    elif self.packaging_type == "msgpack":
                        data = msgpack_numpy.unpackb(message)  # msgpack
                    elif self.packaging_type == "pickle":
                        data = pickle.loads(message) # pickle
                    else:
                        raise ValueError("Unsupported packaging type")
                    
                    if data.get("type") == "action":
                        if self.packaging_type == "json":
                            action = json_to_numpy(data["action"]) # json
                        elif self.packaging_type == "pickle" or self.packaging_type == "msgpack":
                            action = data["action"]  # msgpack, pickle
                        await self._action_queue.put(action)
                    else:
                        await self._msg_queue.put(data)


            except Exception as e:
                print("Client disconnected:", e)

            finally:
                print("Closing websocket...")
                if not websocket.closed:
                    await websocket.close()

                self._connected_event.clear()
                self._ws = None
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
            if self.packaging_type == "json":
                await self._ws.send(json.dumps(payload)) # json
            elif self.packaging_type == "msgpack":
                packed_payload = self.packer.pack(payload) # msgpack
                await self._ws.send(packed_payload) 
            elif self.packaging_type == "pickle":
                packed_payload = pickle.dumps(payload) # pickle
                print(f"size of packed_payload: {sys.getsizeof(packed_payload)} bytes")
                await self._ws.send(packed_payload) 

        except Exception as e:
            print("Send failed:", e)


    async def get_action(self, timeout=None) -> np.ndarray:
        try:
            action = await asyncio.wait_for(self._action_queue.get(), timeout=timeout)
            return action
        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for action")
