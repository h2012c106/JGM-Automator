from building import BuildingType
from target import TargetType

# 坐标相关
# 每个建筑等级显示的左上角坐标
BUILDING_LEVEL_POS = {
    1: (219, 1205),
    2: (469, 1078),
    3: (719, 950),
    4: (216, 947),
    5: (467, 822),
    6: (728, 697),
    7: (215, 696),
    8: (468, 570),
    9: (725, 445)
}
# 建筑坐标
BUILDING_POS = {
    1: (294, 1184),
    2: (551, 1061),
    3: (807, 961),
    4: (275, 935),
    5: (535, 810),
    6: (799, 687),
    7: (304, 681),
    8: (541, 568),
    9: (787, 447)
}
# 查看每个建筑等级的按钮坐标
BUILDING_DETAIL_BTN = (982, 1151)
# 建筑升级按钮坐标
BUILDING_UPGRADE_BTN = (863, 1756)

# 游戏属性相关
# 建筑对应加buff的对象
BUFF_PAIR = {
    BuildingType.木屋: [BuildingType.木材厂],
    BuildingType.居民楼: [BuildingType.便利店],
    BuildingType.钢结构房: [BuildingType.钢铁厂],
    BuildingType.平房: [],
    BuildingType.小型公寓: [],
    BuildingType.人才公寓: [],
    BuildingType.花园洋房: [BuildingType.商贸中心],
    BuildingType.中式小楼: [],
    BuildingType.空中别墅: [BuildingType.民食斋],
    BuildingType.复兴公馆: [],
    BuildingType.便利店: [BuildingType.居民楼],
    BuildingType.五金店: [BuildingType.零件厂],
    BuildingType.服装店: [BuildingType.纺织厂],
    BuildingType.菜市场: [BuildingType.食品厂],
    BuildingType.学校: [BuildingType.图书城],
    BuildingType.图书城: [BuildingType.学校, BuildingType.造纸厂],
    BuildingType.商贸中心: [BuildingType.花园洋房],
    BuildingType.加油站: [BuildingType.人民石油],
    BuildingType.民食斋: [BuildingType.空中别墅],
    BuildingType.媒体之声: [],
    BuildingType.木材厂: [BuildingType.木屋],
    BuildingType.食品厂: [BuildingType.菜市场],
    BuildingType.造纸厂: [BuildingType.图书城],
    BuildingType.水厂: [],
    BuildingType.电厂: [],
    BuildingType.钢铁厂: [BuildingType.钢结构房],
    BuildingType.纺织厂: [BuildingType.服装店],
    BuildingType.零件厂: [BuildingType.五金店],
    BuildingType.企鹅机械: [BuildingType.零件厂],
    BuildingType.人民石油: [BuildingType.加油站],
}
# 建筑品质
_RANK_NORMAL = 0
_RANK_RARE = 1
_RANK_EPIC = 2
BUILDING_RANK = {
    BuildingType.木屋: _RANK_NORMAL,
    BuildingType.居民楼: _RANK_NORMAL,
    BuildingType.钢结构房: _RANK_NORMAL,
    BuildingType.平房: _RANK_NORMAL,
    BuildingType.小型公寓: _RANK_NORMAL,
    BuildingType.人才公寓: _RANK_RARE,
    BuildingType.花园洋房: _RANK_RARE,
    BuildingType.中式小楼: _RANK_RARE,
    BuildingType.空中别墅: _RANK_EPIC,
    BuildingType.复兴公馆: _RANK_EPIC,
    BuildingType.便利店: _RANK_NORMAL,
    BuildingType.五金店: _RANK_NORMAL,
    BuildingType.服装店: _RANK_NORMAL,
    BuildingType.菜市场: _RANK_NORMAL,
    BuildingType.学校: _RANK_NORMAL,
    BuildingType.图书城: _RANK_RARE,
    BuildingType.商贸中心: _RANK_RARE,
    BuildingType.加油站: _RANK_RARE,
    BuildingType.民食斋: _RANK_EPIC,
    BuildingType.媒体之声: _RANK_EPIC,
    BuildingType.木材厂: _RANK_NORMAL,
    BuildingType.食品厂: _RANK_NORMAL,
    BuildingType.造纸厂: _RANK_NORMAL,
    BuildingType.水厂: _RANK_NORMAL,
    BuildingType.电厂: _RANK_NORMAL,
    BuildingType.钢铁厂: _RANK_RARE,
    BuildingType.纺织厂: _RANK_RARE,
    BuildingType.零件厂: _RANK_RARE,
    BuildingType.企鹅机械: _RANK_EPIC,
    BuildingType.人民石油: _RANK_EPIC,
}
# 建筑对应火车货物
BUILDING_2_GOODS = {
    BuildingType.木屋: TargetType.Chair,
    BuildingType.居民楼: TargetType.Box,
    BuildingType.钢结构房: TargetType.Sofa,
    BuildingType.平房: None,
    BuildingType.小型公寓: None,
    BuildingType.人才公寓: None,
    BuildingType.花园洋房: None,
    BuildingType.中式小楼: TargetType.Quilt,
    BuildingType.空中别墅: None,
    BuildingType.复兴公馆: None,
    BuildingType.便利店: TargetType.Bottle,
    BuildingType.五金店: TargetType.Screw,
    BuildingType.服装店: TargetType.Cloth,
    BuildingType.菜市场: TargetType.Vegetable,
    BuildingType.学校: None,
    BuildingType.图书城: TargetType.Book,
    BuildingType.商贸中心: None,
    BuildingType.加油站: None,
    BuildingType.民食斋: None,
    BuildingType.媒体之声: None,
    BuildingType.木材厂: TargetType.Wood,
    BuildingType.食品厂: TargetType.Food,
    BuildingType.造纸厂: TargetType.Straw,
    BuildingType.水厂: None,
    BuildingType.电厂: TargetType.Mine,
    BuildingType.钢铁厂: TargetType.Coal,
    BuildingType.纺织厂: TargetType.Cotton,
    BuildingType.零件厂: None,
    BuildingType.企鹅机械: None,
    BuildingType.人民石油: None,
}