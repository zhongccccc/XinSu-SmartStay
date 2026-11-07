#!/bin/bash
# 一键把「芯宿·智控」门锁应用装进 OpenHarmony 源码树
# 用法： bash setup_zk_app.sh [/你的/源码/根目录]
set -u
SRV="http://192.168.60.40:8899"

ROOT="${1:-}"
if [ -z "$ROOT" ]; then
  for cand in "$HOME/txsmartropenharmony" "/home/OpenHarmony/txsmartropenharmony" \
              "$HOME/OpenHarmony/txsmartropenharmony" "/home/OpenHarmony" \
              "$HOME/lockzhiner-rk2206-OpenHarmony3.0lts" ; do
    if [ -d "$cand/applications/sample/wifi-iot/app" ]; then ROOT="$cand"; break; fi
  done
fi

if [ -z "$ROOT" ] || [ ! -d "$ROOT/applications/sample/wifi-iot/app" ]; then
  echo "!! 没找到源码根目录。请手动指定，例如："
  echo "   bash setup_zk_app.sh /home/OpenHarmony/txsmartropenharmony"
  exit 1
fi

APP="$ROOT/applications/sample/wifi-iot/app"
echo "源码根目录: $ROOT"
echo "应用目录  : $APP/zhikong_lock"

mkdir -p "$APP/zhikong_lock" || exit 1

fetch() {   # $1=文件名  $2=目标路径
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --noproxy '*' "$SRV/$1" -o "$2"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$2" "$SRV/$1"
  else
    echo "!! 没有 curl 也没有 wget"; return 1
  fi
}

echo "-- 下载 zk_lock.c"
fetch zk_lock.c "$APP/zhikong_lock/zk_lock.c" || { echo "下载失败，检查网络"; exit 1; }
echo "-- 下载 BUILD.gn"
fetch BUILD.gn "$APP/zhikong_lock/BUILD.gn" || exit 1

echo "-- 修改 app/BUILD.gn"
python3 - "$APP/BUILD.gn" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
if "zhikong_lock" in s:
    print("   已经有 zhikong_lock，跳过")
else:
    s = s.replace("features = [", 'features = [\n        "zhikong_lock:zk_lock",', 1)
    open(p, "w", encoding="utf-8").write(s)
    print("   已加入 features")
PY

echo
echo "== 结果 =="
ls -l "$APP/zhikong_lock"
echo "-- app/BUILD.gn 内容 --"
cat "$APP/BUILD.gn"
echo
echo "== 下一步 =="
echo "  cd $ROOT"
echo "  pip install build/lite      # 首次，把 hb 降到 0.4.3"
echo "  hb set                      # root path 输入 . ，然后选 rk2206"
echo "  hb build -f                 # 编译"
