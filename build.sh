#!/usr/bin/env bash
# 纯 swiftc 构建：无 Xcode 工程、无第三方依赖，产出可直接运行的 .app
set -euo pipefail
cd "$(dirname "$0")"

APP="镇纸.app"
BIN="Paperweight"
ID="co.mindorigin.paperweight"
CONTENTS="$APP/Contents"

rm -rf "$APP"
mkdir -p "$CONTENTS/MacOS" "$CONTENTS/Resources"

cat > "$CONTENTS/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>镇纸</string>
  <key>CFBundleDisplayName</key><string>镇纸</string>
  <key>CFBundleExecutable</key><string>$BIN</string>
  <key>CFBundleIdentifier</key><string>$ID</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>LSMinimumSystemVersion</key><string>14.0</string>
  <key>LSUIElement</key><true/>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSHumanReadableCopyright</key><string>语料出处见 Resources/corpus.json</string>
</dict></plist>
PLIST

echo "▸ 编译"
swiftc -O -swift-version 5 \
  -target arm64-apple-macos14.0 \
  -framework AppKit -framework SwiftUI -framework Carbon -framework ServiceManagement \
  Sources/*.swift \
  -o "$CONTENTS/MacOS/$BIN"

cp Resources/corpus.json "$CONTENTS/Resources/"
[ -f Resources/AppIcon.icns ] && cp Resources/AppIcon.icns "$CONTENTS/Resources/"

echo "▸ 签名（ad-hoc）"
codesign --force --sign - --timestamp=none "$APP" >/dev/null 2>&1

echo "✓ $APP"
du -sh "$APP" | awk '{print "  体积 " $1}'
