import math
import time
from multiprocessing import Queue

from config import Reader, CONFIG_NAME_2_METHOD_NAME

CONFIG_PREFIX = 'THIS IS CONFIG'
METHOD_PREFIX = 'THIS IS METHOD'
METHOD_SEP = ','


def list_gcd(li):
    copy_li = list(li)[:]
    while len(copy_li) >= 2:
        x = copy_li.pop()
        y = copy_li.pop()
        gcd = math.gcd(x, y)
        copy_li.append(gcd)
    assert len(copy_li) == 1
    return copy_li[0]


class Scheduler:
    def __init__(self, keyboard: Queue, pipe: Queue):
        self.config = Reader()
        self.keyboard = keyboard
        self.pipe = pipe

    def _generate_do_2_time(self):
        res = {}
        for config_name in CONFIG_NAME_2_METHOD_NAME.keys():
            res[config_name] = set()
        return res

    # 判断哪些任务需要重新放回调度队列，有可能出现关闭一个任务后重启，而此时这个任务将会饿死，因为没有trigger
    def _generate_restart_list(self, do_2_time: dict, interval_map: dict):
        res = []
        for config_name in interval_map.keys():
            if interval_map[config_name] > 0 and len(do_2_time[config_name]) == 0:
                res.append(config_name)
        return res

    def _add_time_2_do(self, time_2_do: dict, new_time: int, do: str):
        if new_time not in time_2_do:
            time_2_do[new_time] = {do}
        else:
            time_2_do[new_time].add(do)

    def run(self):
        default_loop_interval = 5
        loop_time = 0
        # 记录哪个时间干哪些事（实际上只是塞队列）
        time_2_do = {}
        # 记录哪些事在哪些时候干
        do_2_time = self._generate_do_2_time()
        while self.keyboard.empty():
            # 更新配置
            self.config.refresh()

            # self.pipe.put(f'{CONFIG_PREFIX}{self.config.to_string()}')
            self.pipe.put(self.config.to_string())

            interval_map = self.config.interval_map
            pipe_msg = []
            for config_name, interval in interval_map.items():
                if interval <= 0:
                    interval_map.pop(config_name)
                    # 如果一个任务被置于<=0的值代表不希望被执行，那么同时需要把它移出任务队列
                    for _time in do_2_time[config_name]:
                        time_2_do.get(_time, set()).discard(config_name)
                    do_2_time[config_name] = set()
            # print(interval_map)
            if len(interval_map) == 0:
                loop_interval = default_loop_interval
            else:
                loop_interval = list_gcd(interval_map.values())

                to_do_set = time_2_do.get(loop_time, set()) | set(self._generate_restart_list(do_2_time, interval_map))
                # print(to_do_set)
                for config_name in to_do_set:
                    # 塞入调度队列
                    pipe_msg.append(CONFIG_NAME_2_METHOD_NAME[config_name])
                    # 计算这个任务下一次何时调度
                    next_time = interval_map[config_name] / loop_interval + loop_time
                    # 更新time_2_do
                    self._add_time_2_do(time_2_do, next_time, config_name)
                    # 更新do_2_time
                    do_2_time[config_name].discard(loop_time)
                    do_2_time[config_name].add(next_time)
                # 把当前时间的任务队列销掉，节省内存
                time_2_do.pop(loop_time, '')
            # print(pipe_msg)
            if len(pipe_msg) != 0:
                pipe_msg = f"{METHOD_PREFIX}{METHOD_SEP.join(pipe_msg)}"
                self.pipe.put(pipe_msg)
            loop_time += 1
            time.sleep(loop_interval)
