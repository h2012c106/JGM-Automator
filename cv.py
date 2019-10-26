from target import TargetType
import os
import re
import cv2
import time
import subprocess
import numpy as np

import prop

TARGET_DIR = './assets/'
TMP_DIR = './tmp/'

SIMILAR = {
    '1': ['i', 'I', 'l', '|', ':', '!', '/', '\\', '丨'],
    '2': ['z', 'Z'],
    '3': [],
    '4': [],
    '5': ['s', 'S'],
    '6': [],
    '7': ['T'],
    '8': ['&'],
    '9': [],
    '0': ['o', 'O', 'c', 'C', 'D']
}


class UIMatcher:
    @staticmethod
    def match(screen, target: TargetType):
        """
        在指定快照中确定货物的屏幕位置。
        """
        # 获取对应货物的图片。
        # 有个要点：通过截屏制作货物图片时，请在快照为实际大小的模式下截屏。
        template = cv2.imread(target.value)
        # 获取货物图片的宽高。
        th, tw = template.shape[:2]

        # 调用 OpenCV 模板匹配。
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        rank = max_val

        # 矩形左上角的位置。
        tl = max_loc

        # 阈值判断。
        if rank < 0.9:
            return None

        # 这里，我随机加入了数字（15），用于补偿匹配值和真实位置的差异。
        return tl[0] + tw / 2 + 15, tl[1] + th / 2 + 15, rank

    @staticmethod
    def read(filepath: str):
        """
        工具函数，用于读取图片。
        """
        return cv2.imread(filepath)

    @staticmethod
    def write(image):
        """
        工具函数，用于读取图片。
        """
        ts = str(int(time.time()))
        return cv2.imwrite(f'{TARGET_DIR}{ts}.jpg', image)

    @staticmethod
    def image_to_txt(image, cleanup=False, plus=''):
        # cleanup为True则识别完成后删除生成的文本文件
        # plus参数为给tesseract的附加高级参数
        image_url = f'{TMP_DIR}tmp.jpg'
        txt_name = f'{TMP_DIR}tmp'
        txt_url = f'{txt_name}.txt'
        cv2.imwrite(image_url, image)

        subprocess.check_output('tesseract ' + image_url + ' ' +
                                txt_name + ' ' + plus, shell=True)  # 生成同名txt文件
        text = ''
        with open(txt_url, 'r') as f:
            text = f.read().strip()
        if cleanup:
            os.remove(txt_url)
            os.remove(image_url)
        return text

    @staticmethod
    def normalize_txt(txt: str):
        for key, sim_list in SIMILAR.items():
            for sim in sim_list:
                txt = txt.replace(sim, key)
        txt = re.sub(r'\D', '', txt)
        return txt

    @staticmethod
    def cut(image, left_up, len_width=(190, 50)):
        sx = left_up[0]
        sy = left_up[1]
        dx = left_up[0] + len_width[0]
        dy = left_up[1] + len_width[1]
        return image[sy:dy, sx:dx]

    @staticmethod
    def plain(image):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        erode = cv2.erode(image, kernel)
        dilate = cv2.dilate(erode, kernel)
        return dilate

    @staticmethod
    def fill_color(image):
        copy_image = image.copy()
        h, w = image.shape[:2]
        mask = np.zeros([h + 2, w + 2], np.uint8)
        cv2.floodFill(copy_image, mask, (0, 0), (255, 255, 255), (100, 100, 100), (50, 50, 50),
                      cv2.FLOODFILL_FIXED_RANGE)
        return copy_image

    @staticmethod
    def pre(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([103, 43, 46])
        upper_blue = np.array([103, 255, 255])
        image = cv2.inRange(image, lower_blue, upper_blue)
        return image

    @staticmethod
    def get_little_square(img, rel_pos, edge=0.01):
        '''
        截取rel_pos附近一个小方块
        '''
        rx, ry = rel_pos
        h = len(img)
        w = len(img[0])
        scale = h / w
        x0 = int((rx - edge * scale) * w)
        x1 = int((rx + edge * scale) * w)
        y0 = int((ry - edge) * h)
        y1 = int((ry + edge) * h)
        return img[y0:y1, x0:x1]

    @staticmethod
    def find_green_light(diff_screens):
        screen_before, screen_after = diff_screens
        # 转换成有符号数以处理相减后的负值
        screen_before = screen_before.astype(np.int16)
        screen_after = screen_after.astype(np.int16)

        diff = screen_after - screen_before
        h = len(diff)
        w = len(diff[0])
        B, G, R = cv2.split(diff)
        # 负值取0
        G[G < 0] = 0
        G = G.astype(np.uint8)
        # 二值化后相与, 相当于取中间范围内的值
        ret, G1 = cv2.threshold(G, 140, 255, cv2.THRESH_BINARY_INV)
        ret, G2 = cv2.threshold(G, 22, 255, cv2.THRESH_BINARY)
        img0 = G1 & G2
        # 均值模糊(降噪 好像也没啥卵用)
        img0 = cv2.medianBlur(img0, 9)

        buildings = []
        for building_id in range(1, 10):
            square = UIMatcher.cut(img0, prop.BUILDING_POS[building_id], (110, 55))
            buildings.append(np.mean(square))
        # 返回平均亮度最强的建筑物
        return buildings.index(max(buildings)) + 1

    @staticmethod
    def detect_cross(screen, th=5):
        '''
        探测叉叉是否出现, 先截取叉叉所在的小方块,然后对灰度图二值化,再求平均值判断
        '''
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        good_id_list = []
        for good_id in prop.CROSS_POSITIONS.keys():
            square = UIMatcher.get_little_square(screen, prop.CROSS_POSITIONS[good_id])
            ret, W = cv2.threshold(square, 250, 255, cv2.THRESH_BINARY)
            # import matplotlib.pyplot as plt
            # plt.imshow(W,cmap='gray')
            # plt.show()
            # 二值化后求平均值
            if np.mean(W) > th:
                good_id_list.append(good_id)
        # print(good_id_list)
        return good_id_list
