#!/bin/bash
BASE="/e/zhikong/refs/tx_all/通晓开发板（鸿蒙南向轻量系统开发板）"
PDF="$BASE/04-产品手册/通晓开发板使用手册.pdf"
ls -l "$PDF" 2>/dev/null || echo "PDF 不存在"
cd /tmp && rm -f man-*.png
pdftoppm -png -r 110 "$PDF" man 2>&1 | head -3
ls -l /tmp/man-*.png 2>/dev/null | head -30
