#!/bin/bash
cd /home/openharmony/txsmartropenharmony/vendor/isoftstone/rk2206/samples || exit 1
for d in c5_sht30 c6_bh1750 c7_mpu6050 c1_gas_sensor b3_adc_key c3_eeprom c4_nfc c2_lcd; do
  echo "=== $d ==="
  ls "$d" 2>/dev/null | tr '\n' ' '
  echo
  grep -h -E 'IoTI2cInit|IoTAdcInit|ADDR|CHANNEL|_PORT|_ID|handle' "$d"/*.c 2>/dev/null | head -12
  echo
done
