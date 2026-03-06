from src.tcp.tcp_server import TCPServer
import time
from src.utils.utils import jpeg_to_img
import os
import h5py
import cv2

def main(host, port):
    server = TCPServer(host, port, packaging_type=PACKAGING_TYPE)
    server.accept_connection()

    try:
        with h5py.File(file_path, "r") as f:
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
                
                # print("jpeg size:", len(rgb_dataset_head_camera[idx]))
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
                    # decode_start_time = time.monotonic()

                    # # print(f"size of rgb_data: {len(rgb_dataset_head_camera[idx])} bytes")
                    
                    # img_head_camera = jpeg_to_img(rgb_dataset_head_camera[idx]) # np.ndarray
                    # img_left_camera = jpeg_to_img(rgb_dataset_left_camera[idx]) # np.ndarray
                    # img_right_camera = jpeg_to_img(rgb_dataset_right_camera[idx]) # np.ndarray

                    # # print(f"size of img: {img_head_camera.nbytes} bytes")
            
                    # decode_end_time = time.monotonic()
                    # decode_time += (decode_end_time - decode_start_time)

                    # obs = {
                    #         "joint_action": {
                    #             "left_arm": left_arm_dataset[idx],
                    #             "left_gripper": left_gripper_dataset[idx],
                    #             "right_arm": right_arm_dataset[idx],
                    #             "right_gripper": right_gripper_dataset[idx],
                    #         },
                    #         "observation": {
                    #             # 已经是单张图片了，不用再取索引
                    #             "head_camera": img_head_camera,
                    #             "left_camera": img_left_camera,
                    #             "right_camera": img_right_camera,
                    #         } 
                    #     }
                

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
                    
                server.post_obs(obs)
                action = server.get_action()

            end_time = time.monotonic()

            print(f"Average decode time: {decode_time / test_num:.4f} seconds")
            print(f"Average round-trip time: {(end_time - start_time - decode_time) / test_num:.4f} seconds")

    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.close()


if __name__== "__main__":

    PACKAGING_TYPE = "json"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_dir = os.path.join(BASE_DIR, "data")
    file_name = "episode0.hdf5"
    file_path = os.path.join(file_dir, file_name)
    print(f"file path: {file_path}")
    
    main(host="0.0.0.0", port=9000)