# -*- coding: utf-8 -*-
"""v15：软件 I2C 驱动 AW9523B 键灯，按键时点亮对应 LED。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

SOFT_I2C = '''/* ---------------- AW9523B 键灯（软件 I2C） ---------------- */
#define PIN_LED_SDA       12      /* GPIO0_B4 */
#define PIN_LED_SCL       13      /* GPIO0_B5 */
#define AW9523_ADDR       0x58

static void si2c_delay(void)
{
    usleep(6);
}

static void si2c_start(void)
{
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED_SDA, IOT_GPIO_VALUE1);
    IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE1);
    si2c_delay();
    IoTGpioSetOutputVal(PIN_LED_SDA, IOT_GPIO_VALUE0);
    si2c_delay();
    IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE0);
    si2c_delay();
}

static void si2c_stop(void)
{
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED_SDA, IOT_GPIO_VALUE0);
    si2c_delay();
    IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE1);
    si2c_delay();
    IoTGpioSetOutputVal(PIN_LED_SDA, IOT_GPIO_VALUE1);
    si2c_delay();
}

static void si2c_write_byte(unsigned char b)
{
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_OUT);
    for (int i = 0; i < 8; i++) {
        IoTGpioSetOutputVal(PIN_LED_SDA, (b & 0x80) ? IOT_GPIO_VALUE1 : IOT_GPIO_VALUE0);
        si2c_delay();
        IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE1);
        si2c_delay();
        IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE0);
        b <<= 1;
    }
    /* 第 9 个时钟：释放 SDA 让从机应答，不检查 */
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_IN);
    si2c_delay();
    IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE1);
    si2c_delay();
    IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE0);
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_OUT);
}

static void aw9523_write(unsigned char reg, unsigned char val)
{
    si2c_start();
    si2c_write_byte(AW9523_ADDR << 1);
    si2c_write_byte(reg);
    si2c_write_byte(val);
    si2c_stop();
}

static void led_init(void)
{
    IoTGpioInit(PIN_LED_SCL);
    IoTGpioSetDir(PIN_LED_SCL, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED_SCL, IOT_GPIO_VALUE1);
    IoTGpioInit(PIN_LED_SDA);
    IoTGpioSetDir(PIN_LED_SDA, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED_SDA, IOT_GPIO_VALUE1);

    aw9523_write(0x04, 0x00);      /* P0 全输出 */
    aw9523_write(0x05, 0x00);      /* P1 全输出 */
    aw9523_write(0x02, 0xFF);      /* P0 灭（低电平点亮，故写 1 灭） */
    aw9523_write(0x03, 0xFF);      /* P1 灭 */
}

static void led_show(unsigned int mask)
{
    /* 按位点亮：bit n → 对应 LED */
    unsigned int p0 = mask & 0xFF;
    unsigned int p1 = (mask >> 8) & 0xFF;
    aw9523_write(0x02, (unsigned char)(~p0));
    aw9523_write(0x03, (unsigned char)(~p1));
}

static void led_off(void)
{
    aw9523_write(0x02, 0xFF);
    aw9523_write(0x03, 0xFF);
}

'''

anchor = "/* ---------------- TTP229 两线读 ---------------- */"
assert anchor in s, "锚点未找到"
s = s.replace(anchor, SOFT_I2C + anchor, 1)

# 按键时点亮
old = '''                    g_keys++;
                    g_beep_left = 3;
                    zk_print("ZK|EVT|KEY|%c|bit=%d|mask=0x%04X\\r\\n", k, bit, m);'''
new = '''                    g_keys++;
                    g_beep_left = 3;
                    led_show(m);          /* 点亮相按的键灯 */
                    zk_print("ZK|EVT|KEY|%c|bit=%d|mask=0x%04X\\r\\n", k, bit, m);'''
assert old in s
s = s.replace(old, new, 1)

# 松手灭灯
old2 = '''            if (m != last_mask) {
                last_mask = m;
                char k = ttp229_key(m);'''
new2 = '''            if (m != last_mask) {
                last_mask = m;
                if (m == 0) {
                    led_off();
                }
                char k = ttp229_key(m);'''
assert old2 in s
s = s.replace(old2, new2, 1)

# 启动时初始化 LED
old3 = '''    g_print_mutex = osMutexNew(NULL);'''
new3 = '''    led_init();

    g_print_mutex = osMutexNew(NULL);'''
assert old3 in s
s = s.replace(old3, new3, 1)

s = s.replace("rk2206-lock-v14", "rk2206-lock-v15")
open(P, "w", encoding="utf-8").write(s)
print("patched v15")
