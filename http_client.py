from base_client import BaseClient
import numpy as np
import requests
import json
import struct
from utils import numpy_to_json, json_to_numpy

class HTTPClient(BaseClient):
    def __init__(self, server_url: str):
        super().__init__()
        self.server_url = server_url.rstrip('/')

    def _recv_msg(self):
        response = requests.get(f"{self.server_url}/get_obs")
        response.raise_for_status()
        data = response.json()
        return data

    def _send_msg(self, obj, obj_name = "action"):
        payload = {
            obj_name: obj
        }

        response = requests.post(
            f"{self.server_url}/post_{obj_name}",
            json=payload
        )

        response.raise_for_status()
    
    def get_obs(self):
        obs = self._recv_msg()
        return obs

    def post_action(self, action) -> None:

        if isinstance(action, np.ndarray):
            action = action.tolist()
        self._send_msg(action, obj_name="action")
        
    def infer(self, obs) -> np.ndarray:
        # TODO: use policy to infer action according to obs
        action = np.zeros(7, dtype=np.float32) # dummy action, 6-DoF + gripper
        return action
    
    def step(self):
        obs = self.get_obs()
        # print(f"Received obs: {obs}")
        action = self.infer(obs)
        self.post_action(action)

if __name__ == "__main__":
    client = HTTPClient("http://localhost:8000")
    while True:
        client.step()