import json
import prop
import time
import pickle
from numpy import array
from building import BuildingType

CONFIG_FILE = './config.json'


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        ret = func(*args, **kw)
        print('Current function [%s] run time is %.2f' % (func.__name__, time.time() - local_time))
        return ret

    return wrapper


CONFIG_NAME_2_METHOD_NAME = {
    'swipe_interval_sec': '_swipe',
    'upgrade_interval_sec': '_upgrade',
    'good_interval_sec': '_check_good',
    'mission_interval_sec': '_match_mission'
}


class Reader:
    building_pos = None
    goods_2_building_seq = None
    upgrade_order = None
    interval_map = None
    upgrade_press_time_sec = None

    def _building_name_star_2_building_enum_star(self, building_name_star):
        assert len(building_name_star.split()) == 2
        name, star = building_name_star.split()
        star = int(star)
        for building in BuildingType:
            enum_name = str(building).split('.')[1]
            if enum_name == name:
                return building, star
        raise Exception(f'Wrong building name [{name}]')

    def _flatten_list(self, leveled_building_pos):
        tmp_list = array(leveled_building_pos[::-1]).flatten().tolist()
        return [self._building_name_star_2_building_enum_star(ele) for ele in tmp_list]

    def _generate_building_pos(self, flattened_building_pos):
        return [ele[0] for ele in flattened_building_pos]

    def _generate_goods_2_building_seq(self, building_pos, train_get_rank):
        mask_building_pos = list(filter(lambda building: prop.BUILDING_RANK[building] >= train_get_rank, building_pos))

        res = {}
        for i, building in enumerate(building_pos):
            building_seq = i + 1
            goods = prop.BUILDING_2_GOODS[building]
            if goods is not None and building in mask_building_pos:
                res[goods] = building_seq
        return res

    def _generate_upgrade_order(self, flattened_building_pos, building_pos):
        star_2_building = {}
        for building, star in flattened_building_pos:
            if star in star_2_building:
                star_2_building[star] |= set(prop.BUFF_PAIR[building])
            else:
                star_2_building[star] = set(prop.BUFF_PAIR[building])
        sorted_list = sorted(star_2_building.items(), key=lambda item: item[0], reverse=True)
        building_pos_set = set(building_pos)
        sorted_list = [ele[1] & building_pos_set for ele in sorted_list]
        # 把剩下的比如电厂之类的纳入最低优先级，万一有个一级的也很尴尬，不用担心重复，到时候是set合并
        sorted_list.append(set(self.building_pos))
        # 有可能有些建筑没有对应buff建筑，然后这个🌟段只有它一个
        return list(filter(lambda building_set: len(building_set) > 0, sorted_list))

    def refresh(self):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.interval_map = {}
        for config_name in CONFIG_NAME_2_METHOD_NAME.keys():
            self.interval_map[config_name] = config.get(config_name, -1)

        self.upgrade_press_time_sec = config['upgrade_press_time_sec']

        flattened_building_pos = self._flatten_list(config['building_pos'])
        self.building_pos = self._generate_building_pos(flattened_building_pos)
        self.goods_2_building_seq = self._generate_goods_2_building_seq(self.building_pos, config['train_get_rank'])
        self.upgrade_order = self._generate_upgrade_order(flattened_building_pos, self.building_pos)
        # print(self.goods_2_building_seq, self.upgrade_order)

    def to_string(self):
        return pickle.dumps(self)

    @staticmethod
    def from_string(b):
        return pickle.loads(b)
