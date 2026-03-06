import numpy as np
import socket
import json
import struct
from src.base.base_server import BaseServer

import time
import sys
from src.utils.json_numpy import numpy_to_json, json_to_numpy
from src.utils import msgpack_numpy
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
        else:
            raise ValueError("Unsupported packaging type")

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
        else:
            raise ValueError("Unsupported packaging type")

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
