import numpy as np
import cv2

def jpeg_to_img(jpeg_bytes):
    ''' 将 JPEG bytes 解码为 原始帧'''
    img_array = np.frombuffer(jpeg_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR) # np.ndarray
    return img
