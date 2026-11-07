# -*- coding: utf-8 -*-
"""v18：新增 zk diag，逐项打印输出通道的返回值与电平。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

DIAG = '''/* ---------------- 输出通道诊断 ---------------- */
static void zk_diag(void)
{
    unsigned int r;
    IotGpioValue v1 = IOT_GPIO_VALUE0, v2 = IOT_GPIO_VALUE0;

    /* 1) 先把指示灯总线的两根线当输入读电平（判断有无上拉/短路） */
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_IN);
    IoTGpioSetDir(PIN_LED_SCL, IOT_GPIO_DIR_IN);
    usleep(5 * 1000);
    IoTGpioGetInputVal(PIN_LED_SDA, &v1);
    IoTGpioGetInputVal(PIN_LED_SCL, &v2);
    zk_print("ZK|DIAG|bus_idle|sda=%d|scl=%d\\r\\n", v1, v2);

    /* 2) PWM 初始化返回值 */
    r = IoTPwmInit(PWM_BUZZER);
    zk_print("ZK|DIAG|pwm_init|%u\\r\\n", r);
    if (r == IOT_SUCCESS) {
        r = IoTPwmStart(PWM_BUZZER, 50, 2700);
        zk_print("ZK|DIAG|pwm_start|%u\\r\\n", r);
        usleep(600 * 1000);
        IoTPwmStop(PWM_BUZZER);
    }

    /* 3) 蜂鸣器当普通 GPIO 直接拉高（有源蜂鸣器应该响） */
    IoTGpioSetDir(PIN_BUZZER, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_BUZZER, IOT_GPIO_VALUE1);
    usleep(600 * 1000);
    IoTGpioSetOutputVal(PIN_BUZZER, IOT_GPIO_VALUE0);
    zk_print("ZK|DIAG|buzzer_gpio|done\\r\\n");

    /* 4) 分别向 0x58 / 0x59 写配置，再读回输入寄存器看是否应答 */
    const unsigned char addrs[2] = {0x58, 0x59};
    for (int i = 0; i < 2; i++) {
        unsigned char a = addrs[i];
        si2c_start();
        si2c_write_byte((unsigned char)(a << 1));
        si2c_write_byte(0x04);
        si2c_write_byte(0x00);
        si2c_stop();
        usleep(3 * 1000);

        /* 读回：写指针指向 0x00 再读 1 字节 */
        si2c_start();
        si2c_write_byte((unsigned char)(a << 1));
        si2c_write_byte(0x00);
        si2c_stop();
        usleep(2 * 1000);
        si2c_start();
        si2c_write_byte((unsigned char)((a << 1) | 1));
        unsigned char rd = 0;
        unsigned char bit = 0;
        for (int b = 0; b < 8; b++) {
            IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE1);
            usleep(6);
            IotGpioValue s = IOT_GPIO_VALUE0;
            IoTGpioGetInputVal(PIN_LED_SDA, &s);
            if (s == IOT_GPIO_VALUE1) rd |= (1u << (7 - b));
            IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE0);
            usleep(6);
        }
        bit = rd;
        si2c_stop();
        zk_print("ZK|DIAG|aw9523_0x%02X|read=0x%02X\\r\\n", a, bit);
    }

    /* 5) 两个地址都点亮一遍，各保持 2 秒 */
    for (int i = 0; i < 2; i++) {
        unsigned int save = g_led_addr;
        g_led_addr = addrs[i];
        zk_print("ZK|DIAG|try_light|0x%02X\\r\\n", addrs[i]);
        aw9523_write(0x12, 0x00);
        aw9523_write(0x13, 0x00);
        aw9523_write(0x04, 0x00);
        aw9523_write(0x05, 0x00);
        aw9523_write(0x02, 0x00);   /* 全亮（低电平点亮） */
        aw9523_write(0x03, 0x00);
        usleep(2000 * 1000);
        aw9523_write(0x02, 0xFF);
        aw9523_write(0x03, 0xFF);
        g_led_addr = save;
    }
    zk_print("ZK|DIAG|DONE\\r\\n");
}

'''

anchor = "/* ---------------- 扫描 ---------------- */"
assert anchor in s
s = s.replace(anchor, DIAG + anchor, 1)

# 让 aw9523_write 使用可变地址
s = s.replace("static void aw9523_write(unsigned char reg, unsigned char val)\n{\n    si2c_start();\n    si2c_write_byte(AW9523_ADDR << 1);",
              "static unsigned int g_led_addr = AW9523_ADDR;\n\nstatic void aw9523_write(unsigned char reg, unsigned char val)\n{\n    si2c_start();\n    si2c_write_byte((unsigned char)((g_led_addr & 0x7F) << 1));", 1)

# 命令绑定
old = '''    } else if (strcmp(sub, "led") == 0) {'''
new = '''    } else if (strcmp(sub, "diag") == 0) {
        zk_diag();
        zk_print("ZK|ACK|DIAG|OK\\r\\n");
    } else if (strcmp(sub, "led") == 0) {'''
assert old in s
s = s.replace(old, new, 1)

s = s.replace("rk2206-lock-v17", "rk2206-lock-v18")
open(P, "w", encoding="utf-8").write(s)
print("patched v18")
