#!/usr/bin/env bash
# 离屏渲染卡片 PNG，用于设计迭代与验收。不需要录屏权限。
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="$(cd "$(dirname "${1:-./previews}")" 2>/dev/null && pwd)/$(basename "${1:-previews}")"
mkdir -p "$OUT"
TMP=$(mktemp -d)
cp Resources/corpus.json "$TMP/"
cp scripts/RenderPreviews.swift "$TMP/main.swift"   # 顶层代码只允许出现在 main.swift
swiftc -swift-version 5 -target arm64-apple-macos14.0 \
  -framework AppKit -framework SwiftUI \
  Sources/Quote.swift Sources/Theme.swift Sources/CardView.swift "$TMP/main.swift" \
  -o "$TMP/preview"
( cd "$TMP" && ./preview "$OUT" )
rm -rf "$TMP"
