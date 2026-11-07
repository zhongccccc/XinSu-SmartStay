# -*- coding: utf-8 -*-
"""全局配置：路径、房型、设备识别规则。"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # app/backend
APP_DIR = os.path.dirname(BASE_DIR)                             # app
WORK_DIR = os.environ.get("ZHIKONG_HOME", "/opt/zhikong")
WEB_DIR = os.path.join(APP_DIR, "web")
ASSET_DIR = os.path.join(APP_DIR, "assets")
VOICE_DIR = os.path.join(ASSET_DIR, "voice")
DATA_DIR = os.environ.get("ZHIKONG_DATA", os.path.join(WORK_DIR, "data"))
LOG_DIR = os.path.join(WORK_DIR, "logs")
CONF_FILE = os.environ.get("ZHIKONG_CONF", os.path.join(WORK_DIR, "etc", "config.json"))

for _d in (DATA_DIR, LOG_DIR, VOICE_DIR):
    os.makedirs(_d, exist_ok=True)

HOTEL = {
    "name": "芯宿·智控",
    "sub": "深圳湾科技园店",
    "brand": "RISC-V SpacemiT K1",
    "wifi": "XINSU-GUEST",
}

# 房型 / 房价 / 库存 —— 一体机选房用
ROOMS = [
    {"no": "8801", "type": "高级大床房", "price": 468, "floor": 8, "tags": ["园景", "1.8m"]},
    {"no": "8802", "type": "高级大床房", "price": 468, "floor": 8, "tags": ["园景", "1.8m"]},
    {"no": "8803", "type": "高级双床房", "price": 508, "floor": 8, "tags": ["高层"]},
    {"no": "8805", "type": "高级双床房", "price": 508, "floor": 8, "tags": ["高层"]},
    {"no": "8806", "type": "行政大床房", "price": 668, "floor": 8, "tags": ["行政酒廊"]},
    {"no": "8808", "type": "行政大床房", "price": 668, "floor": 8, "tags": ["行政酒廊"]},
    {"no": "9901", "type": "亲子家庭房", "price": 728, "floor": 9, "tags": ["双卧"]},
    {"no": "9902", "type": "亲子家庭房", "price": 728, "floor": 9, "tags": ["双卧"]},
    {"no": "9903", "type": "智能影音房", "price": 598, "floor": 9, "tags": ["投影"]},
    {"no": "9905", "type": "智能影音房", "price": 598, "floor": 9, "tags": ["投影"]},
    {"no": "9906", "type": "无障碍房", "price": 468, "floor": 9, "tags": ["无障碍"]},
    {"no": "9908", "type": "套房", "price": 988, "floor": 9, "tags": ["客厅分离"]},
]

# 设备识别：默认按名称/VID 判定；可被 etc/config.json 覆盖
DEFAULT_DEVICE_RULES = {
    # 键盘型 HID 扫码器 / 读卡器（USB HID keyboard emulation）
    "scanner_name_re": r"(?i)(barcode|bar code|scanner|扫码|rfid|reader|读卡|二维码|id card|ic card|pos)",
    "scanner_vid_pid": [
        # 常见扫码枪 / 韦根读卡器芯片
        "0c2e:0b01",  # Honeywell/新大陆 类
        "1eab:", "040b:", "05fe:", "1cc7:", "28e9:", "238b:",
    ],
    "camera_exclude_name_re": r"(?i)(vivi|mvx|dec0|codec)",
    "lock": {"transport": "auto", "port": "/dev/ttyUSB1", "baud": 115200,
             "serial": "/dev/ttyUSB0",
             "http": "http://127.0.0.1:9001", "token": "k1-lock"},
}

# 语音指令词表（端侧关键词路由，后续可替换为 ASR+NLU）
VOICE_COMMANDS = {
    "灯光": ["开灯", "关灯", "灯光", "亮一点", "暗一点", "阅读灯", "睡眠模式"],
    "空调": ["空调", "制冷", "制热", "温度", "26度", "24度", "风速"],
    "窗帘": ["窗帘", "窗帘打开", "窗帘关闭", "遮光"],
    "服务": ["拖鞋", "牙刷", "毛巾", "矿泉水", "打扫", "送水", "被子", "枕头"],
    "查询": ["退房", "早餐", "wifi", "WiFi", "停车", "发票", "健身房", "早餐时间"],
}


def load_config():
    cfg = {
        "hotel": HOTEL,
        "rooms": ROOMS,
        "devices": json.loads(json.dumps(DEFAULT_DEVICE_RULES)),
        "idcard": {"mode": "auto", "url": "http://127.0.0.1:7846", "interval": 1.5},
        "rfid": {"enabled": True, "transport": "serial", "port": "/dev/ttyUSB0", "baud": 9600},
        "camera": {
            "config": "/usr/share/camera_json/csi3_camera_auto.json",
            "pipeline": ("spacemitsrc location={cfg} close-dmabuf=1 ! "
                         "video/x-raw,format=NV12,width=1920,height=1080 ! "
                         "videoconvert ! video/x-raw,format=BGR ! "
                         "appsink drop=true max-buffers=1 sync=false"),
        },
        "kiosk": {"port": 8080, "idle_timeout": 60, "face_required": True},
    }
    if os.path.exists(CONF_FILE):
        try:
            with open(CONF_FILE, "r", encoding="utf-8") as f:
                user = json.load(f)
            for k, v in user.items():
                if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
        except Exception as e:  # 配置损坏不影响启动
            print("[config] load failed:", e)
    return cfg


CONF = load_config()
