# -*- coding: utf-8 -*-
"""挑出 RFID 串口协议相关资料，复制成 ASCII 文件名。"""
import glob
import os
import shutil

ROOT = r"E:\zhikong\refs\idcard"
OUT = r"E:\zhikong\refs\key"
os.makedirs(OUT, exist_ok=True)

wanted = [
    ("串口说明.pdf", "rfid_serial_protocol.pdf"),
    ("高频读写器使用手册V1.0.5.pdf", "rfid_manual.pdf"),
    ("ConsoleApplication1.cpp", "rfid_sample.cpp"),
    ("SerialPort.cpp", "rfid_serialport.cpp"),
    ("SerialPort.h", "rfid_serialport.h"),
    ("说明.txt", "rfid_readme.txt"),
]

for frag, alias in wanted:
    hits = [p for p in glob.glob(os.path.join(ROOT, "**", "*"), recursive=True)
            if os.path.isfile(p) and frag in os.path.basename(p)]
    # 优先 RFID 目录下的
    hits.sort(key=lambda p: (0 if "RFID" in p else 1, len(p)))
    if not hits:
        print("MISSING", frag)
        continue
    src = hits[0]
    dst = os.path.join(OUT, alias)
    shutil.copyfile(src, dst)
    print("%-26s <- %s (%.0f KB)" % (alias, os.path.basename(src), os.path.getsize(dst) / 1024))
