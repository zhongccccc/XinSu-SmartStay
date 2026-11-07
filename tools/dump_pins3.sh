#!/bin/bash
cd /home/openharmony/txsmartropenharmony/vendor/isoftstone/rk2206/samples || exit 1
echo "===== SHT30 ====="
grep -h -E 'define|I2c|IOT_I2C|Init' c5_sht30/sht30_example.c c5_sht30/src/*.c 2>/dev/null | head -20
echo
echo "===== BH1750 ====="
grep -h -E 'define|I2c|IOT_I2C|Init' c6_bh1750/bh1750_example.c c6_bh1750/src/*.c 2>/dev/null | head -16
echo
echo "===== MPU6050 ====="
grep -h -E 'define|I2c|IOT_I2C|Init' c7_mpu6050/mpu6050_example.c c7_mpu6050/src/*.c 2>/dev/null | head -16
echo
echo "===== GAS ====="
grep -h -E 'define|Adc|ADC' c1_gas_sensor/gas_sensor_example.c 2>/dev/null | head -12
