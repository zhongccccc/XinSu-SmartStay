#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""离线验证 home_board 解析逻辑（在 K1 上跑，不需要硬件）。"""
import sys

sys.path.insert(0, "/opt/zhikong/app/backend/devices")
import home_board as hb  # noqa: E402

events = []
board = hb.HomeBoard(on_event=lambda e: events.append(e), log=lambda *_: None)

SAMPLES = [
    ("心跳", "[zh] alive #120 t=28.8 h=57.6 lux=112 gas=113 pir=0"),
    ("事件-有人", "ZH|EVT|PIR|1"),
    ("事件-无人", "ZH|EVT|PIR|0"),
    ("事件-灯关", "ZH|EVT|LIGHT|off"),
    ("事件-按键", "ZH|EVT|KEY|6"),
    ("命令回包", "ZH|ACK|ENV|OK|t=30.9|h=66.6|lux=19"),
    ("噪声-提示符", "OHOS # "),
    ("噪声-乱码", "5joh[:command not found"),
    ("心跳-负温", "[zh] alive #200 t=-3.5 h=40.0 lux=0 gas=88 pir=1"),
]

print("%-12s %-44s -> %s" % ("类型", "输入", "解析后"))
print("-" * 96)
for kind, line in SAMPLES:
    board._parse(line.strip())
    d = board.data
    print("%-12s %-44s -> t=%s h=%s lux=%s gas=%s pir=%s light=%s"
          % (kind, line[:44], d["temp"], d["hum"], d["lux"], d["gas"], d["pir"], d["light"]))

print()
print("事件回调:", events)
ok = True
if board.data["temp"] != -3.5:
    print("!! 温度解析异常"); ok = False
if board.data["pir"] != 1:
    print("!! pir 解析异常"); ok = False
if not any(e["type"] == "pir" for e in events):
    print("!! 未触发 pir 事件"); ok = False
if not any(e["type"] == "key" for e in events):
    print("!! 未触发 key 事件"); ok = False
print("结果:", "全部通过" if ok else "有异常")
