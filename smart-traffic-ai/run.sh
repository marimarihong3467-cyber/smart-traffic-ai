#!/usr/bin/env bash
# 智游山城 · 一键启动
set -e
cd "$(dirname "$0")"

python3 -m pip install -q -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt

echo "🚀 启动中… 打开浏览器访问 http://127.0.0.1:8000"
exec python3 backend/main.py
