# -*- coding: utf-8 -*-
"""可关闭摄像头：人脸已自动放行，不需要摄像头，避免 ISP 报错拖垮系统。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

OLD = '''        self.camera.probe()'''
NEW = '''        if CONF["devices"].get("camera_disabled"):
            log("[camera] 已按配置停用（人脸为自动放行，不需要摄像头）")
        else:
            self.camera.probe()'''

if "camera_disabled" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("main.py: 支持 camera_disabled")
else:
    print("状态:", "已存在" if "camera_disabled" in s else "未匹配")
