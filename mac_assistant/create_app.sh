#!/bin/bash

# Create Native macOS App Bundle
# This script creates Mac Remote Assistant.app

set -e

echo "==================================="
echo "Creating Mac Remote Assistant.app"
echo "==================================="
echo ""

APP_NAME="Mac Remote Assistant"
BUNDLE_NAME="${APP_NAME}.app"
BUNDLE_DIR="$(pwd)/${BUNDLE_NAME}"

# Clean old build
if [ -d "$BUNDLE_DIR" ]; then
    echo "Removing old app bundle..."
    rm -rf "$BUNDLE_DIR"
fi

# Create app structure
echo "Creating app bundle structure..."
mkdir -p "$BUNDLE_DIR/Contents/MacOS"
mkdir -p "$BUNDLE_DIR/Contents/Resources"
mkdir -p "$BUNDLE_DIR/Contents/Frameworks"

# Copy Python files
echo "Copying application files..."
mkdir -p "$BUNDLE_DIR/Contents/Resources/mac_assistant"
cp -r ./*.py "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./plugins "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./tasks "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./database "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./utils "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./ui "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./scripts "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./autonomous "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./voice "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true
cp -r ./venv "$BUNDLE_DIR/Contents/Resources/mac_assistant/" 2>/dev/null || true

# Create launcher script
echo "Creating launcher script..."
cat > "$BUNDLE_DIR/Contents/MacOS/mac_assistant" << 'EOF'
#!/bin/bash

# Get the app directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Add to Python path
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"

# Run the app with menu bar launcher
cd "$RESOURCES_DIR/mac_assistant"
python3 launcher_menubar.py
EOF

chmod +x "$BUNDLE_DIR/Contents/MacOS/mac_assistant"

# Create Info.plist
echo "Creating Info.plist..."
cat > "$BUNDLE_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>de</string>
    <key>CFBundleExecutable</key>
    <string>mac_assistant</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.macassistant.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppleEventsUsageDescription</key>
    <string>Diese App benötigt Zugriff auf andere Apps um sie zu steuern.</string>
    <key>NSSystemAdministrationUsageDescription</key>
    <string>Diese App benötigt Administratorrechte für bestimmte Funktionen.</string>
</dict>
</plist>
EOF

# Create simple icon (optional - you can replace with a proper .icns file)
echo "App icon can be added to: $BUNDLE_DIR/Contents/Resources/AppIcon.icns"

echo ""
echo "==================================="
echo "✓ App Bundle erstellt!"
echo "==================================="
echo ""
echo "Location: $BUNDLE_DIR"
echo ""
echo "Installation:"
echo "  sudo cp -r \"$BUNDLE_DIR\" /Applications/"
echo ""
echo "Oder Doppelklick auf: $BUNDLE_DIR"
echo ""
