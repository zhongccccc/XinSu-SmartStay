# 门锁板协议（K1 ⇄ 通晓 RK2206）

- 物理层：UART 115200 8N1，无流控（板子丝印 A6/A7，`IoTUart id 0`）
- 下行：**shell 子命令**，以 `\r` 结尾
- 上行：板子用 `printf` 打印，行首 `ZK|`，K1 只认这种行

> 为什么下行走 shell：日志串口被系统 shell 占用，应用直接读会和 shell 抢字节。
> 用 `osCmdReg()` 把协议注册成 `zk` 子命令，由 shell 解析完再交给应用，字节不会被吞。

## 下行（K1 → 板子）

| 命令 | 说明 |
|---|---|
| `zk ping` | 探活 |
| `zk issue <room> <code> <card\|-> <ttl_min>` | 下发临时码与房卡 |
| `zk open <room>` | 远程开门 |
| `zk revoke <room>` | 作废凭证 |
| `zk code <code>` | 调试用：模拟键盘输入一串码 |

## 上行（板子 → K1）

| 输出 | 说明 |
|---|---|
| `ZK\|ACK\|PING\|OK\|<ver>` | 探活应答，`<ver>` 带固件版本 |
| `ZK\|ACK\|ISSUE\|OK\|room=8801` | 下发成功 |
| `ZK\|ACK\|OPEN\|OK` / `ZK\|ACK\|REVOKE\|OK` | 开门/作废成功 |
| `ZK\|ACK\|<cmd>\|ERR\|<reason>` | 失败 |
| `ZK\|EVT\|KEY\|<keys>` | 键盘按键序列 |
| `ZK\|EVT\|CARD\|<uid>` | NFC 房卡 |
| `ZK\|EVT\|FP\|<id>` | 指纹 |
| `ZK\|EVT\|CODE\|<ok\|bad>` | 本地校验结果 |
| `ZK\|EVT\|DOOR\|<open\|close>` | 门磁 |
| `ZK\|EVT\|ALARM\|<tamper\|lowbat>` | 防撬 / 低电 |
| `ZK\|BOOT\|<version>` | 应用启动 |

## 时序

```
K1                                  板子（shell）
 |-- "zk issue 8801 123456 CARD01 1440\r" -->|
 |<-- "OHOS # " (回显/提示符，忽略) ----------|
 |<-- "ZK|ACK|ISSUE|OK|room=8801" ----------|
 |                                           |  客人键盘输入 123456#
 |<-- "ZK|EVT|KEY|1,2,3,4,5,6,#" ------------|
 |<-- "ZK|EVT|CODE|ok" ----------------------|
 |<-- "ZK|EVT|DOOR|open" --------------------|
```

K1 侧：`app/backend/devices/lock_board.py`（4 秒等 ACK，发送前清旧应答）；
上层适配：`app/backend/devices/lock.py` 的 `BoardLockAdapter`（`auto` 时离线退化为 mock）。
