# Native macOS App erstellen

Es gibt **3 Methoden** um eine native .app zu erstellen:

---

## Method 1: Simple App Bundle (Schnell & Einfach) ⚡

```bash
cd mac_assistant
chmod +x create_app.sh
./create_app.sh
```

Das erstellt: `Mac Remote Assistant.app`

**Installation:**
```bash
sudo cp -r "Mac Remote Assistant.app" /Applications/
```

**Oder:** Einfach Doppelklick auf die .app!

---

## Method 2: py2app (Professionell) 🎯

### 1. py2app installieren:
```bash
pip install py2app
```

### 2. App erstellen:
```bash
cd mac_assistant
python3 setup_py2app.py py2app
```

Das erstellt: `dist/Mac Remote Assistant.app`

### 3. Installieren:
```bash
cp -r dist/"Mac Remote Assistant.app" /Applications/
```

**Vorteile:**
- ✅ Alle Python-Dependencies eingebettet
- ✅ Standalone - kein Python installiert nötig
- ✅ Professionelles App-Bundle
- ✅ Code-Signing möglich

---

## Method 3: Automator Wrapper (Einfachste) 🚀

### 1. Öffne Automator.app
### 2. Wähle "Programm" (Application)
### 3. Füge "Shell-Skript ausführen" hinzu
### 4. Füge ein:

```bash
#!/bin/bash
cd /Applications/Mac\ Remote\ Assistant
source venv/bin/activate
python3 launcher.py
```

### 5. Speichere als "Mac Remote Assistant.app"

**Vorteile:**
- ✅ Sehr einfach
- ✅ Kein Scripting nötig
- ✅ macOS-Standard-Tool

---

## Nach der Installation

### API Key setzen:

**Option A:** In der App (Einstellungen)
1. Öffne App
2. Klicke "⚙️ Einstellungen"
3. Gib deinen API Key ein
4. Klicke "💾 API Key speichern"
5. Starte App neu

**Option B:** System-weit (empfohlen)
```bash
# In ~/.zshrc oder ~/.bash_profile:
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

### Berechtigungen erteilen:

**Systemeinstellungen → Sicherheit → Datenschutz:**

1. **Bedienungshilfen**: App hinzufügen
2. **Automation**: Zugriff auf Mail, Photos, Messages erlauben

---

## Testen

```bash
# Direkt starten (ohne .app)
cd mac_assistant
python3 launcher.py

# Als .app starten
open "/Applications/Mac Remote Assistant.app"
```

---

## Troubleshooting

### "App kann nicht geöffnet werden"
```bash
# Code-Signing entfernen:
xattr -cr "/Applications/Mac Remote Assistant.app"
```

### "Python nicht gefunden"
→ Nutze Method 2 (py2app) für standalone App

### "API Key nicht gefunden"
→ Setze in ~/.zshrc oder in App-Einstellungen

---

## Distribution

### Als DMG verpacken:

```bash
# DMG erstellen
hdiutil create -volname "Mac Remote Assistant" \
  -srcfolder "Mac Remote Assistant.app" \
  -ov -format UDZO \
  MacRemoteAssistant-v2.0.dmg
```

### Als ZIP verpacken:

```bash
ditto -c -k --sequesterRsrc --keepParent \
  "Mac Remote Assistant.app" \
  MacRemoteAssistant-v2.0-app.zip
```

---

**Fertig!** 🎉

Deine App ist jetzt eine echte native macOS Anwendung!
