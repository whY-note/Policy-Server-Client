from base_server import BaseServer
from websockets.server import serve
import numpy as np
import json
import asyncio
from utils import numpy_to_json, json_to_numpy
import time

import sys
import msgpack_numpy
import pickle

class WebServer(BaseServer):

    def __init__(self, host="0.0.0.0", port=8000, packaging_type = "json"):
        super().__init__()
        self.host = host
        self.port = port

        self._ws = None
        self._action_queue = asyncio.Queue()
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

                    if data.get("type") == "action":
                        if self.packaging_type == "json":
                            action = json_to_numpy(data["action"]) # json
                        elif self.packaging_type == "pickle" or self.packaging_type == "msgpack":
                            action = data["action"]  # msgpack, pickle
                        await self._action_queue.put(action)

            except Exception as e:
                print("Client disconnected:", e)

            finally:
                self._connected_event.clear()
                self._ws = None

        print(f"WebServer running on ws://{self.host}:{self.port}")
        async with serve(handler, self.host, self.port, max_size = None):
            await asyncio.Future()  # Run forever

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



if __name__ == "__main__":
    from utils import jpeg_to_img
    PACKAGING_TYPE = "json"
    async def main():
        server = WebServer(port=8000, packaging_type=PACKAGING_TYPE)

        # 启动 WebSocket 服务器
        server_task = asyncio.create_task(server.start())

        print("Waiting for client...")
        await server._connected_event.wait()
        print("Client connected!")

        # 模拟机器人控制循环
        try:
            import h5py
            import cv2
            with h5py.File("./data/episode0.hdf5", "r") as f:
                # load data from hdf5 file
                rgb_dataset_head_camera = f["observation/head_camera/rgb"]
                rgb_dataset_left_camera = f["observation/left_camera/rgb"] 
                rgb_dataset_right_camera = f["observation/right_camera/rgb"]

                left_arm_dataset = f["joint_action/left_arm"][:]
                left_gripper_dataset = f["joint_action/left_gripper"][:]
                right_arm_dataset = f["joint_action/right_arm"][:]
                right_gripper_dataset = f["joint_action/right_gripper"][:]

                test_num = min(100, len(rgb_dataset_head_camera))
                print("test_num: ", test_num)
                decode_time = 0
                start_time = time.monotonic()

                for idx in range(test_num):
                    if PACKAGING_TYPE == "json":
                        obs = {
                            "joint_action": {
                                "left_arm": left_arm_dataset[idx],
                                "left_gripper": left_gripper_dataset[idx],
                                "right_arm": right_arm_dataset[idx],
                                "right_gripper": right_gripper_dataset[idx],
                            },
                            "observation": {
                                "head_camera": bytes(rgb_dataset_head_camera[idx]), # type(rgb_dataset_head_camera[idx]) = np.bytes, cannot be transformed to json
                                "left_camera": bytes(rgb_dataset_left_camera[idx]), 
                                "right_camera": bytes(rgb_dataset_right_camera[idx]),
                            }
                        }
                    elif PACKAGING_TYPE == "msgpack" or PACKAGING_TYPE == "pickle":
                        decode_start_time = time.monotonic()

                        # print(f"size of rgb_data: {len(rgb_dataset_head_camera[idx])} bytes")
                        
                        img_head_camera = jpeg_to_img(rgb_dataset_head_camera[idx]) # np.ndarray
                        img_left_camera = jpeg_to_img(rgb_dataset_left_camera[idx]) # np.ndarray
                        img_right_camera = jpeg_to_img(rgb_dataset_right_camera[idx]) # np.ndarray

                        # print(f"size of img: {img_head_camera.nbytes} bytes")
                
                        decode_end_time = time.monotonic()
                        decode_time += (decode_end_time - decode_start_time)

                        obs = {
                                "joint_action": {
                                    "left_arm": left_arm_dataset[idx],
                                    "left_gripper": left_gripper_dataset[idx],
                                    "right_arm": right_arm_dataset[idx],
                                    "right_gripper": right_gripper_dataset[idx],
                                },
                                "observation": {
                                    # 已经是单张图片了，不用再取索引
                                    "head_camera": img_head_camera,
                                    "left_camera": img_left_camera,
                                    "right_camera": img_right_camera,
                                } 
                            }

                    await server.post_obs(obs)

                    try:
                        action = await server.get_action(timeout=10)
                        print("Received action:", action)
                    except TimeoutError:
                        print("No action received (timeout)")

                    # await asyncio.sleep(0.1)
                end_time = time.monotonic()
                print(f"Average decode time: {decode_time / test_num:.4f} seconds")
                print(f"Average round-trip time: {(end_time - start_time - decode_time) / test_num:.4f} seconds")

        except KeyboardInterrupt:
            print("Shutting down server...")
            server_task.cancel()

    asyncio.run(main())