#!/bin/bash
ROOT=/opt/zhikong/idreader/rootfs
exec /usr/bin/qemu-aarch64-static -L "$ROOT" /opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/
