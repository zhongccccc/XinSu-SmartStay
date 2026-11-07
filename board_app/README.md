# 芯宿·智控 智能门锁板应用（OpenHarmony 轻量系统）

与 K1 一体机通过日志串口对接。**K1 侧已经写好并验证**，只差把这份固件刷进板子。

## 一、文件

| 文件 | 说明 |
|---|---|
| `zk_lock.c` | 板子端应用：注册 `zk` shell 命令、电机、门磁、键盘/NFC/指纹挂载点 |
| `BUILD.gn` | 构建脚本 |
| `PROTOCOL.md` | 协议速查（和 `app/backend/devices/lock_board.py` 对应） |

## 二、放到源码树

```
applications/sample/wifi-iot/app/zhikong_lock/
├── BUILD.gn
└── zk_lock.c
```

并改 `applications/sample/wifi-iot/app/BUILD.gn`：

```gn
lite_component("app") {
    features = [
        "startup",
        "zhikong_lock:zk_lock",     # ← 新增
    ]
}
```

（我已经在你解压出来的那份源码里改好了。）

## 三、引脚（已按引脚表现成配置）

来源：`02-电路原理图/通晓开发板引脚使用.xlsx` + `device/rockchip/rk2206/adapter/include/lz_hardware/gpio.h`

| 部件 | 丝印 | 宏 | 值 |
|---|---|---|---|
| 电机（锁体） | C6 | `PIN_MOTOR` | 22 (`GPIO0_PC6`) |
| 键盘 | C7 | `PIN_KEY_ADC` | 23 (`GPIO0_PC7`, KEY_ADC) |
| 人体感应/门磁 | A3 | `PIN_PIR` | 3 (`GPIO0_PA3`) |
| 蜂鸣器 | C5 | `PIN_BUZZER` | 21 (`GPIO0_PC5`) |
| 报警灯 | A5 | `PIN_LED_ALARM` | 5 (`GPIO0_PA5`) |
| NFC | D5/D6 | — | 29/30 (`I2C0`) |

编号规则：`PA0..PA7=0..7`，`PB0..PB7=8..15`，`PC0..PC7=16..23`，`PD0..PD7=24..31`。

**电机驱动方式**要确认：引脚表写的是 `电机_PWM6_M0`，若锁体是舵机/直流电机，
可能需要改成 PWM 驱动（`IoTPwmStart(6, duty, freq)`）而不是 GPIO 电平。先按 GPIO 试，
不动再换 PWM，两行代码的事。

## 四、编译烧录（Ubuntu VM）

```bash
cd txsmartropenharmony
hb set          # 选 rk2206
hb build -f
```

产物在 `out/rk2206/`，用 `05-工具/烧录固件工具` 烧写。重启后串口打印：

```
[zk] lock app ready (motor=PC6/22, key=PC7/23, nfc=PD5-PD6)
ZK|BOOT|rk2206-zk-v1
```

然后在串口里手敲 `zk ping`，应回 `ZK|ACK|PING|OK|rk2206-zk-v1`。

## 五、验证（K1 侧）

```bash
# 板子在线后，一体机自动切换
zhikong status
curl -s 192.168.60.40:8080/api/health | python3 -m json.tool | grep -A5 lock
```

或直接跑驱动自测：

```bash
python3 /opt/zhikong/app/backend/devices/lock_board.py /dev/ttyUSB1
```

## 六、键盘 / NFC / 指纹

`zk_lock.c` 底部留了实现位：

| 部件 | 做法 |
|---|---|
| 键盘 | PC7 是 ADC 键梯：`IoTAdcRead(7, &val)`，按实测电压分档映射 16 键；`#` 确认调 `cred_check()` |
| NFC | PD5/PD6 I2C0，按 `04-产品手册/datasheet/nfc/` 初始化，读卡后 `ZK\|EVT\|CARD\|<uid>` |
| 指纹 | 按模块手册（多为 UART 指令包），匹配成功 `ZK\|EVT\|FP\|<id>` |

匹配成功统一走 `lock_open()` + 对应 `ZK|EVT|...` 上报，K1 侧自动记审计并弹提示。
