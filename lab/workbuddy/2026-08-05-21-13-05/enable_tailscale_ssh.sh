#!/bin/bash
# macbook-lab 切换到非沙盒 Tailscale 后，一键启用并验证 Tailscale SSH
# 用法：bash enable_tailscale_ssh.sh
set -e

echo "== 检查 Tailscale 构建版本 =="
BID=$(mdls -name kMDItemCFBundleIdentifier /Applications/Tailscale.app 2>/dev/null | awk -F'"' '{print $2}')
echo "bundle id: $BID"

if [ "$BID" = "io.tailscale.ipn.macsys" ]; then
  echo "❌ 仍是沙盒版(App Store)，Tailscale SSH 无法启用。"
  echo "   请先从 https://tailscale.com/download/mac 下载非沙盒 .pkg 安装，再重跑本脚本。"
  exit 1
fi
echo "✅ 已是非沙盒版($BID)，继续..."

echo
echo "== 启用 Tailscale SSH (tailscale set --ssh) =="
tailscale set --ssh

echo
echo "== 当前状态 =="
tailscale status --self 2>/dev/null | head -5

echo
echo "✅ 本机 SSH server 已开启。"
echo "下一步(需你登录后台)："
echo "  1) 打开 https://login.tailscale.com/admin/machines/100.95.8.72/ssh-setup"
echo "  2) 点 Connect 加默认 ssh 策略规则(或手动在 Access Controls 粘贴 ssh 段)"
echo "  3) 从其他设备: ssh 100.95.8.72  (或 ssh macbook-lab)"
