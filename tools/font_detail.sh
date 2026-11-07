#!/bin/bash
cd /home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home
echo "=== 24px 结构 ==="
sed -n '525,545p' lcd_font.h
echo
echo "=== 16px 现有汉字 ==="
sed -n '472,534p' lcd_font.h | grep -o '"[^"]*"' | tr -d '"' | tr '\n' ' '
echo
echo
echo "=== 12px 现有汉字 ==="
sed -n '446,468p' lcd_font.h | grep -o '"[^"]*"' | tr -d '"' | tr '\n' ' '
echo
echo
echo "=== 24px 现有汉字 ==="
sed -n '537,576p' lcd_font.h | grep -o '"[^"]*"' | tr -d '"' | tr '\n' ' '
echo
