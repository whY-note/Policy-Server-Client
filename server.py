from src.tcp.tcp_server import TCPServer
from src.web.web_server import WebServer

import time
from src.utils.utils import  load_yaml, jpeg_to_img
import os
import h5py

import asyncio

def run_tcp(host, port, packaging_type):
    server = TCPServer(host, port, packaging_type)
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
                if packaging_type == "json":
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
                    
                elif packaging_type == "msgpack" or packaging_type == "pickle":
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

async def run_web(host, port, packaging_type):

    server = WebServer(host, port, packaging_type)

    # 启动 WebSocket 服务器
    server_task = asyncio.create_task(server.start())

    print("Waiting for client...")
    await server._connected_event.wait()
    print("Client connected!")

    # 模拟机器人控制循环
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
                if packaging_type == "json":
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
                elif packaging_type == "msgpack" or packaging_type == "pickle":
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


if __name__ == "__main__":

    config_path = "./config/config.yml"
    config = load_yaml(config_path)

    protocol = config["protocol"]
    packaging_type = config["packaging_type"]
    host = config["server"]["host"]
    port = config["server"]["port"]
    print("Config: ")
    print("Protocol: ", protocol)
    print("Packaging type: ", packaging_type)
    print("Host: ", host)
    print("Port: ", port)

    file_name = config["test_file_name"]
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_dir = os.path.join(BASE_DIR, "data")
    file_path = os.path.join(file_dir, file_name)
    print(f"Test file path: {file_path}")

    if protocol == "tcp":
        run_tcp(host = host, port = port, packaging_type = packaging_type)
    elif protocol == "web":
        asyncio.run(run_web(host=host, port=port, packaging_type=packaging_type))
    else:
        raise NotImplementedError(f"Unsupported protocol: {protocol}")
    


