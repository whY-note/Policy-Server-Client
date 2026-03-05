import h5py
import numpy as np
import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_dir = os.path.join(BASE_DIR, "../data")
file_name = "episode0.hdf5"
file_path = os.path.join(file_dir, file_name)
print(f"file path: {file_path}")

with h5py.File(file_path, "r") as f:

    left_arm = f["joint_action/left_arm"][:]          # (678,6)
    print(left_arm.shape)
    print(type(left_arm))
    left_gripper = f["joint_action/left_gripper"][:]  # (678,)
    print(left_gripper.shape)
    print(type(left_gripper))
    
    rgb_bytes = f["observation/head_camera/rgb"][0]  # 第0帧
    
    print(type(rgb_bytes)) # type: np.bytes_
    # ⚠ 这是 bytes，不是图像

    img_array = np.frombuffer(rgb_bytes, dtype=np.uint8)

    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    print(type(img)) # type: np.ndarray
    print(img.shape)