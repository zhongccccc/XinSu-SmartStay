#!/bin/bash
cd /home/openharmony/txsmartropenharmony/vendor/isoftstone/rk2206/samples || exit 1
for d in b9_rgb_led b7_beep b8_electrical_machinery c5_sht30 c6_bh1750 c7_mpu6050 c1_gas_sensor b2_gpio_interrupt b3_adc_key c2_lcd c4_nfc c3_eeprom; do
  echo "=== $d ==="
  grep -h -E 'define +[A-Z_]+ +(GPIO|I2C|PWM|ADC|EPWM|EI2C|EADC)|IoTI2cInit|IoTPwmInit|IoTAdcInit' "$d"/*.c 2>/dev/null | head -10
done
