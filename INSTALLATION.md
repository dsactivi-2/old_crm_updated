# Mac Remote Assistant v2.0 - Installation

## Schnellstart

### 1. ZIP entpacken

```bash
unzip mac_assistant_v2.0.zip
cd mac_assistant
```

### 2. Setup ausführen

```bash
chmod +x setup.sh
./setup.sh
```

### 3. API Key setzen

```bash
export ANTHROPIC_API_KEY='sk-ant-dein-api-key-hier'

# Oder permanent in ~/.zshrc:
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.zshrc
```

### 4. App starten

```bash
source venv/bin/activate
python3 main.py
```

## macOS Berechtigungen einrichten

### Systemeinstellungen → Sicherheit → Datenschutz:

1. **Bedienungshilfen**
   - Terminal.app hinzufügen (oder deine IDE)

2. **Automation**
   - Terminal.app → Mail erlauben
   - Terminal.app → Fotos erlauben
   - Terminal.app → Messages erlauben
   - Terminal.app → Kalender erlauben
   - Terminal.app → Notizen erlauben

## Erste Schritte

### GUI starten:

```bash
python3 main.py
```

### Beispiel-Abfragen:

```
"Was habe ich gestern gemacht?"
"Sende E-Mail an max@example.com"
"Suche Fotos von letzter Woche"
"Sende Slack-Nachricht an #team: Hello!"
```

## Neue Plugins hinzufügen

Siehe `HOW_TO_ADD_PLUGINS.md` für detaillierte Anleitung.

```bash
# 1. Template kopieren
cd plugins
cp PLUGIN_TEMPLATE.py meine_app_plugin.py

# 2. Anpassen
# 3. In core_v2.py registrieren
# 4. Fertig!
```

## Systemanforderungen

- macOS 10.14+
- Python 3.8+
- Anthropic API Key (https://www.anthropic.com)

## Dokumentation

- `README.md` - Vollständige Dokumentation (Englisch)
- `README_DE.md` - Deutsche Version
- `HOW_TO_ADD_PLUGINS.md` - Plugin-Entwicklung

## Support

Bei Problemen:

1. Berechtigungen prüfen (siehe oben)
2. API Key prüfen: `echo $ANTHROPIC_API_KEY`
3. Python Version prüfen: `python3 --version`

## Features

✅ Plugin-System für beliebige Apps
✅ KI-gestützte Task-Automation
✅ Aktivitätsverfolgung ("Zeitreise")
✅ Multi-App-Integration
✅ GUI mit tkinter
✅ Natural Language Processing

## Verfügbare Plugins

- Mail.app (E-Mail)
- Slack (Team-Messaging)
- Viber (Messaging)
- Telegram (Messaging)
- Photos.app (Foto-Management)

**Eigene Plugins hinzufügen in wenigen Minuten!**

---

Viel Spaß mit deinem Mac Remote Assistant! 🚀
