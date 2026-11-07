#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""芯宿·智控 —— 外设自检工具（现场插拔时用来确认识别结果）。

用法：
  python3 /opt/zhikong/app/tools/selftest.py            # 一次性自检
  python3 /opt/zhikong/app/tools/selftest.py --hid 20   # 监听 HID 输入 20 秒（插扫码枪时用）
  python3 /opt/zhikong/app/tools/selftest.py --cam      # 逐个尝试摄像头节点并抓帧
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/opt/zhikong/app")

USBCLASS = {
    "03": "HID", "08": "MassStorage", "0e": "Video", "01": "Audio",
    "02": "CDC/Serial", "0a": "CDC",
}


def sh(cmd, timeout=8):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()
    except Exception as e:
        return "ERR %s" % e


def read(p, d=""):
    try:
        with open(p, encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return d


def usb():
    rows = []
    for d in sorted(glob.glob("/sys/bus/usb/devices/*")):
        vid = read(os.path.join(d, "idVendor"))
        if not vid:
            continue
        rows.append({
            "id": "%s:%s" % (vid, read(os.path.join(d, "idProduct"))),
            "name": read(os.path.join(d, "product")),
            "mfr": read(os.path.join(d, "manufacturer")),
            "cls": read(os.path.join(d, "bDeviceClass")),
        })
    return rows


def inputs():
    out = []
    for ev in sorted(glob.glob("/dev/input/event*"), key=lambda p: int(p.rsplit("event", 1)[-1])):
        b = ev.replace("/dev/input/", "/sys/class/input/")
        out.append({"node": ev, "name": read(os.path.join(b, "device", "name")),
                    "key": read(os.path.join(b, "device", "capabilities", "key"))[:16],
                    "abs": read(os.path.join(b, "device", "capabilities", "abs"))[:16]})
    return out


def videos():
    out = []
    for v in sorted(glob.glob("/dev/video*")):
        idx = v.rsplit("video", 1)[-1]
        out.append({"node": v, "name": read("/sys/class/video4linux/video%s/name" % idx)})
    return out


def audio():
    return read("/proc/asound/cards")


def report():
    data = {"ts": time.strftime("%F %T"), "usb": usb(), "input": inputs(),
            "video": videos(), "audio": audio(), "serial": sorted(
                glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))}
    print("=" * 72)
    print("芯宿·智控 外设自检  %s" % data["ts"])
    print("=" * 72)
    print("\n[USB]")
    for u in data["usb"]:
        print("  %-12s %-28s %-24s class=%s" % (u["id"], u["name"][:28], u["mfr"][:24], u["cls"]))
    print("\n[输入设备]")
    for i in data["input"]:
        has_abs = i["abs"].strip("0") != ""
        has_key = i["key"].strip("0") != ""
        kind = "触摸屏" if has_abs else ("键盘型(扫码/读卡)" if has_key else "其他")
        print("  %-20s %-30s %s" % (i["node"], i["name"][:30], kind))
    print("\n[视频设备]")
    for v in data["video"]:
        print("  %-20s %s" % (v["node"], v["name"]))
    print("\n[声卡]")
    print("  " + (audio().replace("\n", "\n  ") or "无"))
    print("\n[串口]")
    print("  " + (", ".join(data["serial"]) or "无"))
    os.makedirs("/opt/zhikong/data", exist_ok=True)
    with open("/opt/zhikong/data/selfcheck.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n已保存 /opt/zhikong/data/selfcheck.json")
    return data


def hid_watch(seconds):
    print("监听 HID 输入 %d 秒，请现在插上扫码枪/读卡器并扫一次卡…" % seconds)
    before = {i["node"]: i["name"] for i in inputs()}
    for n, name in before.items():
        print("  已有: %s %s" % (n, name))
    try:
        from evdev import InputDevice, categorize, ecodes  # 若安装了 python3-evdev
        have_evdev = True
    except Exception:
        have_evdev = False
    if not have_evdev:
        print("\n未安装 python3-evdev，改用裸读方式（仅显示新设备与按键流）")
    import fcntl
    import select
    import struct
    FMT = "llHHi"
    SIZE = struct.calcsize(FMT)
    KEYMAP = {2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9",
              11: "0", 28: "<ENTER>", 16: "q", 17: "w", 18: "e", 19: "r", 20: "t", 21: "y",
              22: "u", 23: "i", 24: "o", 25: "p", 30: "a", 31: "s", 32: "d", 33: "f",
              34: "g", 35: "h", 36: "j", 37: "k", 38: "l", 44: "z", 45: "x", 46: "c",
              47: "v", 48: "b", 49: "n", 50: "m", 57: " "}
    fds = {}
    end = time.time() + seconds
    while time.time() < end:
        for i in inputs():
            if i["node"] not in fds and i["node"] not in before:
                try:
                    fd = os.open(i["node"], os.O_RDONLY | os.O_NONBLOCK)
                    fds[i["node"]] = fd
                    print("\n>>> 新设备: %s %s" % (i["node"], i["name"]))
                    print(">>> 对应 VID/PID: 见 lsusb；把该名称加入 config.json 的 scanner_name_re 即可自动识别")
                except Exception as e:
                    print("打开 %s 失败: %s" % (i["node"], e))
        if not fds:
            time.sleep(0.5)
            continue
        r, _, _ = select.select(list(fds.values()), [], [], 0.5)
        for fd in r:
            try:
                data = os.read(fd, SIZE * 32)
            except BlockingIOError:
                continue
            line = []
            for k in range(0, len(data) - SIZE + 1, SIZE):
                _, _, t, code, val = struct.unpack(FMT, data[k:k + SIZE])
                if t == 1 and val == 1:
                    line.append(KEYMAP.get(code, ""))
            if line:
                print("   输入: %s" % "".join(line))
    print("\n监听结束")


def cam_test():
    try:
        import cv2
    except Exception:
        print("未安装 opencv，跳过")
        return
    for v in videos():
        n = v["node"]
        if "vivi" in v["name"] or "mvx" in v["name"]:
            continue
        cap = cv2.VideoCapture(n, cv2.CAP_V4L2)
        if not cap.isOpened():
            print("  %-16s 打不开" % n)
            cap.release()
            continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ok, fr = cap.read()
        if ok and fr is not None:
            out = "/opt/zhikong/data/cam_%s.jpg" % os.path.basename(n)
            cv2.imwrite(out, fr)
            print("  %-16s OK %s -> %s" % (n, fr.shape, out))
        else:
            print("  %-16s 打开但取不到帧" % n)
        cap.release()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hid", type=int, default=0, help="监听 HID 秒数")
    ap.add_argument("--cam", action="store_true", help="测试摄像头")
    a = ap.parse_args()
    report()
    if a.cam:
        print("\n[摄像头取帧测试]")
        cam_test()
    if a.hid:
        print()
        hid_watch(a.hid)
