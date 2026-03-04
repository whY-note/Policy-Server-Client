from base_client import BaseClient
import numpy as np
import socket
import json
import struct
from utils import numpy_to_json, json_to_numpy

import msgpack_numpy
import pickle

class TCPClient(BaseClient):
    def __init__(self, packaging_type):
        super().__init__()
        self.packaging_type = packaging_type

    def connect(self, host, port):
        self.host = host
        self.port = port

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        print(f"Connected to TCP Server at {self.host}:{self.port}")
        
    def _recv_all(self, size):
        data = b""
        while len(data) < size:
            packet = self.client_socket.recv(size - len(data))
            if not packet:
                raise ConnectionError("Server disconnected")
            data += packet
        return data

    def _recv_msg(self):
        raw_len = self._recv_all(4) # 前4字 bytes表示消息长度
        (msg_len,) = struct.unpack("!I", raw_len)
        data = self._recv_all(msg_len)

        if self.packaging_type == "json":
            return json_to_numpy(data.decode("utf-8")) # json
        elif self.packaging_type == "msgpack":
            return msgpack_numpy.unpackb(data) # msgpack
        elif self.packaging_type == "pickle":
            return pickle.loads(data) # pickle

    def _send_msg(self, obj):
        if self.packaging_type == "json":
            payload = numpy_to_json(obj).encode("utf-8") # json
        elif self.packaging_type == "msgpack":
            payload = msgpack_numpy.packb(obj) # msgpack
        elif self.packaging_type == "pickle":
            payload = pickle.dumps(obj) # pickle

        msg = struct.pack("!I", len(payload)) + payload
        self.client_socket.sendall(msg)

    def get_obs(self):
        obs = self._recv_msg()
        return obs
    
    def post_action(self, action):
        if isinstance(action, np.ndarray):
            action = action.tolist()
        self._send_msg(action)

    def infer(self, obs):
        # TODO: use policy to infer action according to obs
        action = np.zeros(14, dtype=np.float64) # dummy action, (6-DoF + 1 gripper)*2
        return action

    def step(self):
        obs = self.get_obs()
        # print(f"Received obs: {obs}")
        action = self.infer(obs)
        self.post_action(action)
        
    def close(self):
        self.client_socket.close()

if __name__ =="__main__":
    PACKAGING_TYPE = "pickle"

    client = TCPClient(packaging_type = PACKAGING_TYPE)

    # host = "localhost"
    # port = 12000

    host = "192.168.6.49"
    port = 9000

    try:
        client.connect(host, port)
        print("[INFO] Connected.")
        while True:
            client.step()

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        print("[INFO] Closing connection.")
        client.close()
        print("[INFO] Client exited.")