# JGM Automator

> 这是基于 OpenCV 模板匹配的《家国梦》游戏自动化脚本。

## 安装与运行

```bash
# 安装依赖
pip3 install -r requirements.txt

# 安装tesseract (Mac)
brew install tesseract
# 安装中文语言包 (tesseract 4.1.0)
curl -o /usr/local/Cellar/tesseract/4.1.0/share/tessdata/chi_sim.traineddata -O https://github.com/tesseract-ocr/tessdata/raw/master/chi_sim.traineddata

# adb 连接
adb kill-server && adb server

# 在已完成 adb 连接后，在手机安装 ATX 应用
python3 -m uiautomator2 init

# 打开 ATX ，点击“启动 UIAutomator”选项，确保 UIAutomator 是运行的。

# 进入游戏页面，启动自动脚本。
python3 main.py
```

## 定制
目前火车货物并未全部收录，如果遇到未识别的新的货物，按照如下操作  
+ 修改火车货物对应的建筑：`prop.py` -> `BUILDING_2_GOODS` 
+ 新增火车货物：`target.py` & `target/`
+ 新增操作（比如自动升级政策）：`config.json`定义interval & `automator.py`定义方法（废话）+ 指定方法优先级`METHOD_ORDER` & `config.py`定义config名与方法名的对应

## 新增特性
+ 定时升级房屋，策略：按照配置文件优先升级高星建筑的对应buff建筑
+ 将硬编码部分配置文件化
+ 支持配置文件的热加载
+ 支持在命令行中以回车暂停/重启，以及优雅关闭，方便手动操作（如抽奖）
+ 抄了一波源仓库的货物检测实现，不用傻逼一样每次比对
+ 由于操作略多（收钱、火车、检测城市任务、升级建筑以及未来有可能继续抄的升级政策），原来的任务调度模式过于沙雕（每个interval需要对每个任务做一次是否需要执行的判断），引入scheduler执行一个阉割时间轮（实际上不是轮，是一个dict，长度无限，为了节省内存会把已经走过的时间key pop掉）

## 说明

+ Weditor

我们可以使用 Weditor 工具，获取屏幕坐标，以及在线编写自动化脚本。

```bash
# 安装依赖
python -m pip install --pre weditor

# 启动 Weditor
python -m weditor
```

## 操作方法
+ 配置文件 - `config.json`
```json
{
  "swipe_interval_sec": 扫金币interval,
  "upgrade_interval_sec": 升级建筑interval,
  "upgrade_press_time_sec": 升级建筑时长按时间,
  "building_pos": [
    ["木材厂 4", "电厂 3", "钢铁厂 2"],
    ["便利店 3", "民食斋 1", "五金店 3"],
    ["钢结构房 4", "居民楼 3", "木屋 3"]
  ], // 排布与游戏界面一致，以"[建筑名称] [建筑星级]"为模版
  "train_get_rank": 火车货物收什么品质以上的(≥)，0-普通/1-稀有/2-史诗
}
```
+ 命令行操作  
`python3 main.py` 启动  
`[回车]` 暂停/重启（会有日志提示）  
`end[回车]` 结束应用  

## TODO
+ 几个操作所使用的屏幕截图应当有重用关系，但是不知为何缓存用不上，估计是self.d没法做缓存键(?)