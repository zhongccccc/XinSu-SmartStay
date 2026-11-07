#!/bin/bash
set -e
SRC=/home/openharmony/txsmartropenharmony/vendor/isoftstone/rk2206/samples/c2_lcd
DST=/home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home
cp "$SRC/src/lcd.c" "$DST/lcd.c"
cp "$SRC/include/lcd.h" "$DST/lcd.h"
cp "$SRC/include/lcd_font.h" "$DST/lcd_font.h"
ls -l "$DST"
