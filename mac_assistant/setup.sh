#!/bin/bash

# Mac Remote Assistant Setup Script

echo "=================================="
echo "Mac Remote Assistant - Setup"
echo "=================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Fehler: Diese App funktioniert nur auf macOS!"
    exit 1
fi

echo "✓ macOS erkannt"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python Version: $python_version"

# Create virtual environment
echo ""
echo "Erstelle virtuelle Umgebung..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo ""
echo "Installiere Abhängigkeiten..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=================================="
echo "✓ Installation abgeschlossen!"
echo "=================================="
echo ""
echo "WICHTIG: Berechtigungen einrichten"
echo "=================================="
echo ""
echo "Die App benötigt folgende Berechtigungen:"
echo ""
echo "1. Systemeinstellungen > Sicherheit > Datenschutz > Bedienungshilfen"
echo "   → Terminal.app (oder deine IDE) hinzufügen"
echo ""
echo "2. Systemeinstellungen > Sicherheit > Datenschutz > Automation"
echo "   → Terminal.app Zugriff auf Mail, Fotos, Messages erlauben"
echo ""
echo "3. API Key setzen:"
echo "   export ANTHROPIC_API_KEY='dein-api-key-hier'"
echo "   (Füge dies in ~/.zshrc oder ~/.bash_profile ein)"
echo ""
echo "=================================="
echo "App starten:"
echo "=================================="
echo ""
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo ""
