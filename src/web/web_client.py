from src.base.base_client import BaseClient
import websockets.sync.client
import numpy as np
import json
import struct
from src.utils.utils import numpy_to_json, json_to_numpy

import src.utils.msgpack_numpy as msgpack_numpy
import pickle

class WebClient(BaseClient):
    def __init__(self, server_url: str,  packaging_type="json"):
        super().__init__()
        self.server_url = server_url.rstrip('/')
        print(self.server_url)
        self.ws = websockets.sync.client.connect(self.server_url, max_size=None)

        self.packaging_type = packaging_type

        self.packer = msgpack_numpy.Packer()

    def get_obs(self):

        message = self.ws.recv()  # 阻塞等待

        if self.packaging_type == "json":
            data = json.loads(message) # json
        elif self.packaging_type == "msgpack":
            data = msgpack_numpy.unpackb(message) # msgpack
        elif self.packaging_type == "pickle":
            data = pickle.loads(message) # pickle

        if data.get("type") != "obs":
            raise ValueError("Unexpected message type")

        if self.packaging_type == "json":
            obs = json_to_numpy(data["obs"]) # json
        elif self.packaging_type == "msgpack" or self.packaging_type == "pickle":
            obs = data["obs"]  # msgpack, pickle

        return obs

    def post_action(self, action):
        # print(f"post_action: {action}")

        if self.packaging_type == "json":
            if isinstance(action, np.ndarray):
                action = action.tolist()

        if self.packaging_type == "json":
            payload = {
                "type": "action",
                "action": numpy_to_json(action) # json
            }        
        elif self.packaging_type == "msgpack" or self.packaging_type == "pickle":
            payload = {
                "type": "action",
                "action": action  # msgpack, pickle
            }

        if self.packaging_type == "json":
            self.ws.send(json.dumps(payload)) # json
        elif self.packaging_type == "msgpack":
            packed_payload = self.packer.pack(payload)  # msgpack
            self.ws.send(packed_payload) 
        elif self.packaging_type == "pickle":
            packed_payload = pickle.dumps(payload) # pickle
            self.ws.send(packed_payload) 

    def infer(self, obs) -> np.ndarray:
        return np.zeros(14, dtype=np.float64)

    def step(self):
        obs = self.get_obs()

        # print(f"Received obs: {obs}")
        action = self.infer(obs)
        
        self.post_action(action)

    def close(self):
        self.ws.close()

if __name__ == "__main__":
    PACKAGING_TYPE = "pickle"
    server_url = "ws://127.0.0.1:8000"
    # server_url = "ws://192.168.6.49:8000"
    # server_url = "ws://120.48.23.252:22"
    # server_url = "ws://localhost:9000"
    client = WebClient(server_url, packaging_type=PACKAGING_TYPE)
    try:
        while True:
            client.step()
    except KeyboardInterrupt:
        client.close()
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client.close()