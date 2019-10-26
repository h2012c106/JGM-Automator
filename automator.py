from target import TargetType
from building import BuildingType
from scheduler import Scheduler, CONFIG_PREFIX, METHOD_PREFIX, METHOD_SEP
from multiprocessing import Queue, Process
from config import Reader
from cv import UIMatcher
from random import choice
from operator import methodcaller
from datetime import datetime
from wrapcache import wrapcache
import uiautomator2 as u2
import logging
import time
import prop

MISSION_DONE = 'target/Mission_done.jpg'

BASIC_FORMAT = "[%(asctime)s] %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

chlr = logging.StreamHandler()  # 输出到控制台的handler
chlr.setFormatter(formatter)

fhlr = logging.FileHandler("logging.log")  # 输出到文件的handler
fhlr.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel('INFO')
logger.addHandler(chlr)
logger.addHandler(fhlr)

METHOD_ORDER = {
    '_swipe': 1,
    '_upgrade': 2,
    '_check_good': 1,
    '_match_mission': 0
}


def elect(order_list_len, iter_round):
    res = []
    for i in range(1, order_list_len + 1):
        if iter_round % i == 0:
            res.append(i - 1)
    return res


# u2的screenshot函数会由于长时间未操作的断连而抛出错误，click函数会试图重连
def my_screenshot(d, format="opencv"):
    res = None
    try_time = 0
    while res is None:
        try:
            res = d.screenshot(format=format)
        except Exception:
            try_time += 1
            logger.warning(f'Connection with simulator gone, try to reconnect, #{try_time} attempt')
            # 随便点哪里，click函数会试图重连
            d.click(*prop.BUILDING_POS[1])
    if try_time > 0:
        logger.info('Reconnect success, continue')
    return res


# @wrapcache(timeout=5)
def my_screenshot_with_cache(d, format="opencv"):
    return my_screenshot(d, format=format)


def make_scheduler(keyboard: Queue, pipe: Queue):
    scheduler = Scheduler(keyboard, pipe)
    scheduler.run()


class Automator:
    def __init__(self, device: str, keyboard: Queue):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.d = u2.connect(device)
        self.config = Reader()
        self.upgrade_iter_round = 0
        self.keyboard = keyboard
        self.schedule_keyboard = Queue()
        self.pipe = Queue()
        self.p = Process(target=make_scheduler, args=(self.schedule_keyboard, self.pipe))
        self.p.start()

    def _need_continue(self):
        if not self.keyboard.empty():
            txt = self.keyboard.get()
            if txt == prop.END:
                logger.info('End')
                return False
            logger.info('Pause')
            txt = self.keyboard.get()
            if txt == prop.END:
                logger.info('End')
                return False
            else:
                logger.info('Restart')
                return True
        else:
            return True

    def start(self):
        """
        启动脚本，请确保已进入游戏页面。
        """
        while True:
            # 检查是否有键盘事件
            if not self._need_continue():
                self.schedule_keyboard.put('')
                self.p.join()
                break

            msg = self.pipe.get()
            if isinstance(msg, bytes) or msg.startswith(CONFIG_PREFIX):
                msg = msg[len(CONFIG_PREFIX):] if not isinstance(msg, bytes) else msg
                self.config = Reader.from_string(msg)
            elif msg.startswith(METHOD_PREFIX):
                msg = msg[len(METHOD_PREFIX):]
                method_list = msg.split(METHOD_SEP)
                method_list = sorted(method_list, key=lambda item: METHOD_ORDER.get(item, float('inf')))
                # 简单粗暴的方式，处理 “XX之光” 的荣誉显示。
                # 当然，也可以使用图像探测的模式。
                self.d.click(550, 1650)
                logger.info(f'Scheduled method: [{", ".join(method_list)}]')
                for method_name in method_list:
                    methodcaller(method_name)(self)

        logger.info('Sub process end')

    def _swipe(self):
        """
        滑动屏幕，收割金币。
        """
        for i in range(3):
            # 横向滑动，共 3 次。
            sx, sy = self._get_position(i * 3 + 1)
            ex, ey = self._get_position(i * 3 + 3)
            self.d.swipe(sx, sy, ex, ey)

    @staticmethod
    def _get_position(key):
        """
        获取指定建筑的屏幕位置。

        ###7#8#9#
        ##4#5#6##
        #1#2#3###
        """
        return prop.BUILDING_POS.get(key)

    def _get_target_position(self, target: TargetType):
        """
        获取货物要移动到的屏幕位置。
        """
        return self._get_position(self.config.goods_2_building_seq.get(target))

    def _match_mission(self):
        screen = my_screenshot_with_cache(self.d, format="opencv")
        print(screen)
        result = UIMatcher.match(screen, TargetType.Mission_done)
        if result is None:
            return
        self.d.click(*prop.MISSION_BTN)
        time.sleep(1)
        self.d.click(*prop.MISSION_DONE_BTN)
        time.sleep(1)
        self.d.click(*prop.MISSION_CLOSE_BTN)

    def _match_target(self, screen, target: TargetType):
        """
        探测货物，并搬运货物。
        """
        # 由于 OpenCV 的模板匹配有时会智障，故我们探测次数实现冗余。
        counter = 6
        logged = False
        while counter != 0:
            counter = counter - 1

            # 使用 OpenCV 探测货物。
            result = UIMatcher.match(screen, target)

            # 若无探测到，终止对该货物的探测。
            # 实现冗余的原因：返回的货物屏幕位置与实际位置存在偏差，导致移动失效
            if result is None:
                break

            rank = result[-1]
            result = result[:2]
            sx, sy = result
            # 获取货物目的地的屏幕位置。
            ex, ey = self._get_target_position(target)

            if not logged:
                logger.info(f"Detect {target} at ({sx},{sy}), rank: {rank}")
                logged = True

            # 搬运货物。
            self.d.swipe(sx, sy, ex, ey)
        # 侧面反映检测出货物
        return logged

    def __find_selected_building_seq(self):
        selected_seq_list = elect(len(self.config.upgrade_order), self.upgrade_iter_round)
        tmp_set = set()
        for order_seq in selected_seq_list:
            tmp_set |= self.config.upgrade_order[order_seq]
        res = []
        for i, building in enumerate(self.config.building_pos):
            if building in tmp_set:
                res.append(i + 1)
        if len(res) == 0:
            return list(prop.BUILDING_POS.keys())
        else:
            return res

    def _select_min_building(self):
        screen = my_screenshot(self.d, format="opencv")
        screen = UIMatcher.pre(screen)
        min_level = float('inf')
        min_building_seq = None
        for key in self.__find_selected_building_seq():
            pos = prop.BUILDING_LEVEL_POS[key]
            tmp = UIMatcher.cut(screen, pos)
            tmp = UIMatcher.plain(tmp)
            tmp = UIMatcher.fill_color(tmp)
            tmp = UIMatcher.plain(tmp)
            txt = UIMatcher.image_to_txt(tmp, plus='-l chi_sim --psm 7')
            txt = UIMatcher.normalize_txt(txt)
            try:
                level = int(txt)
                logger.info(f'{self.config.building_pos[key - 1]} tesser -> {level}')
            except Exception:
                logger.warning(f'{self.config.building_pos[key - 1]} tesser -> {txt}')
                continue
            if level < min_level:
                min_level = level
                min_building_seq = key

        # 一个屋子的等级都没拿到
        if min_building_seq is None:
            res = choice(list(prop.BUILDING_POS.keys()))
            logger.warning(f'No tesseract result, random to {self.config.building_pos[res - 1]}')
            return res
        else:
            logger.info(f'Minimum level is {min_level} from {self.config.building_pos[min_building_seq - 1]}')
            return min_building_seq

    def _upgrade(self):
        # 迭代次数加一
        self.upgrade_iter_round += 1

        self.d.click(*prop.BUILDING_DETAIL_BTN)
        time.sleep(1)
        need_upgrade_building_seq = self._select_min_building()
        self.d.click(*self._get_position(need_upgrade_building_seq))
        time.sleep(1)
        self.d.long_click(prop.BUILDING_UPGRADE_BTN[0], prop.BUILDING_UPGRADE_BTN[1],
                          self.config.upgrade_press_time_sec)
        time.sleep(0.5)
        self.d.click(*prop.BUILDING_DETAIL_BTN)

    def _get_screenshot_while_touching(self, location, pressed_time=0.2, screen_before=None):
        '''
        Get screenshot with screen touched.
        '''
        if screen_before is None:
            screen_before = my_screenshot(self.d, format="opencv")
        h, w = len(screen_before), len(screen_before[0])
        x, y = (location[0] * w, location[1] * h)
        # 按下
        self.d.touch.down(x, y)
        # print('[%s]Tapped'%time.asctime())
        time.sleep(pressed_time)
        # 截图
        screen = my_screenshot(self.d, format="opencv")
        # print('[%s]Screenning'%time.asctime())
        # 松开
        self.d.touch.up(x, y)
        # 返回按下前后两幅图
        return screen_before, screen

    def _carry_good(self, _from, _to, _time=5):
        arg = _from + _to
        for _ in range(_time):
            self.d.swipe(*arg)

    def _check_good(self):
        screen_before = my_screenshot_with_cache(self.d, format="opencv")
        h = len(screen_before)
        w = len(screen_before[0])
        good_id_list = UIMatcher.detect_cross(screen_before)
        for good_id in good_id_list:
            two_screen = self._get_screenshot_while_touching(prop.GOODS_POSITIONS[good_id],
                                                             screen_before=screen_before)
            good_dest = UIMatcher.find_green_light(two_screen)
            if 1 <= good_dest <= 9 and good_dest in self.config.goods_2_building_seq.values():
                dx, dy = self._get_position(good_dest)

                sx, sy = prop.GOODS_POSITIONS[good_id]
                sx = sx * w
                sy = sy * h

                logger.info(f'Detect good {good_id} -> {good_dest}: ({sx},{sy}) -> ({dx},{dy})')
                self._carry_good((sx, sy), (dx, dy))
