from base_server import BaseServer
import numpy as np
import socket
import json
import struct
from utils import numpy_to_json, json_to_numpy

import time
import sys
import msgpack_numpy
import pickle

class TCPServer(BaseServer):
    def __init__(self, host = "0.0.0.0", port = 12000, packaging_type="json"):
        super().__init__()
        self.host = host
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)

        print(f"TCP Server listening on {self.host}:{self.port}")

        self.conn = None
        self.addr = None

        self.packaging_type = packaging_type
    def accept_connection(self):
        print("Waiting for a client to connect...")
        self.conn, self.addr = self.server_socket.accept()
        print(f"Client connected from {self.addr}")

    def _recv_all(self, size):
        data = b''
        while len(data) < size:
            packet = self.conn.recv(size - len(data))
            if not packet:
                raise ConnectionError("Client disconnected")
            data += packet
        return data
    
    def _send_msg(self, obj):
        if self.packaging_type == "json":
            payload = numpy_to_json(obj).encode("utf-8") # json
        elif self.packaging_type == "msgpack":
            payload = msgpack_numpy.packb(obj) # msgpack
        elif self.packaging_type == "pickle":
            payload = pickle.dumps(obj) # pickle

        msg = struct.pack('!I', len(payload)) + payload # '!I' means big-endian unsigned int
        print("msg size:", len(msg))
        self.conn.sendall(msg)

    def _recv_msg(self):
        raw_len = self._recv_all(4)
        msg_len = struct.unpack('!I', raw_len)[0]
        data = self._recv_all(msg_len)

        if self.packaging_type == "json":
            return json_to_numpy(data.decode("utf-8")) # json
        elif self.packaging_type == "msgpack":
            return msgpack_numpy.unpackb(data) # msgpack
        elif self.packaging_type == "pickle":
            return pickle.loads(data) # pickle

    def post_obs(self, obs: dict) -> None:
        self._send_msg(obs)
    
    def get_action(self):
        action = self._recv_msg()
        print(f"Received action: {action}")
        return action
        
    def close(self):
        if self.conn:
            self.conn.close()
        self.server_socket.close()


if __name__== "__main__":
    from utils import jpeg_to_img
    PACKAGING_TYPE = "json"
    
    server = TCPServer(host = "0.0.0.0", port = 12000, packaging_type=PACKAGING_TYPE)
    server.accept_connection()

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
                
                print("jpeg size:", len(rgb_dataset_head_camera[idx]))
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

                    print(f"size of rgb_data: {len(rgb_dataset_head_camera[idx])} bytes")
                    
                    img_head_camera = jpeg_to_img(rgb_dataset_head_camera[idx]) # np.ndarray
                    img_left_camera = jpeg_to_img(rgb_dataset_left_camera[idx]) # np.ndarray
                    img_right_camera = jpeg_to_img(rgb_dataset_right_camera[idx]) # np.ndarray

                    print(f"size of img: {img_head_camera.nbytes} bytes")
            
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
                    
                server.post_obs(obs)
                action = server.get_action()

            end_time = time.monotonic()

            print(f"Average decode time: {decode_time / test_num:.4f} seconds")
            print(f"Average round-trip time: {(end_time - start_time - decode_time) / test_num:.4f} seconds")

    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.close()