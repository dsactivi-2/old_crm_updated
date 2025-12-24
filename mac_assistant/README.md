# Mac Remote Assistant 🤖

**Erweiterbarer KI-Assistent für macOS mit Plugin-System**

Ein intelligenter Mac-Assistent, der dir hilft, deinen Mac zu automatisieren. Mit KI-gestützten Antworten, Aktivitätsverfolgung und einem **erweiterbaren Plugin-System** für beliebige Apps.

---

## 🎯 Hauptfunktionen

### ✅ **Erweiterbar & Modular**
- **Plugin-System** - Einfaches Hinzufügen neuer App-Integrationen
- Unterstützt bereits: Mail, Slack, Viber, Telegram, Photos
- **Eigene Plugins erstellen** in wenigen Minuten ([Anleitung](HOW_TO_ADD_PLUGINS.md))

### 🤖 **KI-gestützte Automatisierung**
- Natürliche Sprache (Deutsch & Englisch)
- **Task Execution** - Führt Aufgaben automatisch aus
- **Multi-Step Tasks** - Komplexe Aufgaben mit mehreren Schritten

### ⏰ **Zeitreise-Funktion**
- Verfolgt alle Aktivitäten
- "Was habe ich vor 3 Tagen um 14 Uhr gemacht?"
- Durchsuchbare Aktivitätshistorie

### 📱 **Multi-App-Integration**
- E-Mails (Mail.app)
- Messaging (Slack, Viber, Telegram, Messages)
- Fotos (Photos.app)
- ...und du kannst **beliebige weitere Apps** hinzufügen!

---

## 🚀 Schnellstart

### Installation

```bash
# 1. Repository klonen
git clone <your-repo-url>
cd mac_assistant

# 2. Setup ausführen
chmod +x setup.sh
./setup.sh

# 3. API Key setzen
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# 4. App starten
source venv/bin/activate
python3 main.py
```

### Erste Schritte

```python
# In der App-GUI oder via Python:

# E-Mail senden
"Sende eine E-Mail an max@example.com mit Betreff 'Meeting'"

# Nachricht senden (automatisch richtige App wählen)
"Sende eine Nachricht an Max über Slack: Hallo!"

# Zeitreise
"Was habe ich gestern um 15 Uhr gemacht?"

# Fotos suchen
"Zeige mir Fotos vom Strand"

# Multi-App-Suche
"Suche überall nach 'Projekt X'"
```

---

## 📚 Dokumentation

### Plugin-System

Neue App-Integration hinzufügen:

1. **[HOW_TO_ADD_PLUGINS.md](HOW_TO_ADD_PLUGINS.md)** - Vollständige Anleitung
2. **[PLUGIN_TEMPLATE.py](plugins/PLUGIN_TEMPLATE.py)** - Template kopieren und anpassen
3. Fertig! 🎉

**Beispiel - WhatsApp Plugin:**

```python
from .base_plugin import MessagingPlugin

class WhatsAppPlugin(MessagingPlugin):
    def __init__(self):
        super().__init__('WhatsApp')

    def is_available(self) -> bool:
        return os.path.exists('/Applications/WhatsApp.app')

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        # AppleScript oder API-Call
        pass
```

### Task Execution

Aufgaben in natürlicher Sprache ausführen:

```python
core = MacAssistantCore()

# Einfache Aufgabe
result = core.execute_task("Sende Slack-Nachricht an Team: Meeting verschoben")

# Multi-Step Task
result = core.execute_multi_step_task("""
    1. Sende E-Mail an Max mit Betreff 'Bericht'
    2. Sende Slack-Nachricht an Team: E-Mail versendet
    3. Erstelle Notiz: Bericht an Max gesendet
""")
```

### Verfügbare Plugins

| Plugin | Typ | Funktionen |
|--------|-----|-----------|
| Mail | Email | Lesen, Senden, Suchen |
| Slack | Messaging | Nachrichten, Channels, Status |
| Viber | Messaging | Nachrichten, Suchen |
| Telegram | Messaging | Nachrichten, Suchen |
| Photos | Media | Suchen, Löschen, Alben |
| **Deine eigenen!** | ... | ... |

---

## 🎮 Verwendung

### GUI-Interface

Die App hat ein benutzerfreundliches Interface mit 5 Tabs:

**1. Assistent** - Chatinterface für alle Anfragen
**2. Aktivitäten** - Zeitreise-Funktion
**3. E-Mails** - Mail-Management
**4. Fotos** - Foto-Verwaltung
**5. Einstellungen** - API Key, Plugins verwalten

### Python API

```python
from mac_assistant.core_v2 import MacAssistantCore

core = MacAssistantCore(api_key='your-key')

# Task ausführen
result = core.execute_task("Sende Nachricht an Max")

# Plugin direkt nutzen
slack = core.get_plugin('Slack')
slack.send_message('channel-name', 'Hello!')

# Alle Nachrichten abrufen
messages = core.get_all_messages(limit=20)

# Plugin-Status
status = core.get_plugin_status()
```

---

## 🔌 Architektur

```
mac_assistant/
├── core_v2.py              # Kern mit Plugin-Integration
├── plugins/
│   ├── base_plugin.py      # Plugin-Basisklassen
│   ├── plugin_manager.py   # Plugin-Verwaltung
│   ├── mail_plugin.py      # Mail.app
│   ├── slack_plugin.py     # Slack
│   ├── viber_plugin.py     # Viber
│   ├── telegram_plugin.py  # Telegram
│   ├── photos_plugin.py    # Photos.app
│   └── PLUGIN_TEMPLATE.py  # Template für neue Plugins
├── tasks/
│   ├── task_executor.py    # Task-Ausführung
│   └── task_parser.py      # NLP Task-Parsing
├── database/
│   └── activity_tracker.py # Aktivitätsverfolgung
├── utils/
│   └── ai_assistant.py     # Claude AI Integration
└── ui/
    └── main_window.py      # GUI
```

### Plugin-Basisklassen

- **MessagingPlugin** - Chat-Apps (Slack, WhatsApp, etc.)
- **EmailPlugin** - E-Mail-Clients
- **MediaPlugin** - Foto/Video-Apps
- **ProductivityPlugin** - Notizen, Kalender, etc.
- **BasePlugin** - Für alles andere

---

## 💡 Beispiele

### E-Mail Management

```python
# Ungelesene E-Mails
"Zeige mir meine neuen E-Mails"

# E-Mail senden
"Sende E-Mail an max@example.com: Betreff 'Meeting', Text 'Hallo Max, ...'"

# Mit KI antworten
"Beantworte die letzte E-Mail von Sarah"
```

### Messaging

```python
# Automatische App-Auswahl
"Sende Nachricht an Max: Kommst du zum Meeting?"

# Spezifische App
"Sende Slack-Nachricht an #team: Deployment läuft"
"Sende Viber-Nachricht an Anna: Bin unterwegs"

# Alle Nachrichten
"Zeige mir alle neuen Nachrichten"
```

### Fotos

```python
# Suchen
"Suche Fotos vom Strand"
"Zeige Fotos von letzter Woche"

# Löschen
"Lösche Foto mit Namen 'IMG_1234.jpg'"

# KI-Analyse
"Welche Fotos sind Duplikate?"
```

### Multi-Step Tasks

```python
"Sende E-Mail an Team und dann poste in Slack dass die E-Mail raus ist"

"Suche Fotos vom Meeting und sende sie per Mail an Max"

"Erstelle Zusammenfassung meiner heutigen Aktivitäten und sende sie per Slack"
```

---

## 🔒 Datenschutz & Sicherheit

- ✅ **Alle Daten bleiben lokal** auf deinem Mac
- ✅ Datenbank: `~/.mac_assistant/activities.db`
- ✅ Nur KI-Anfragen gehen an Anthropic API
- ✅ Keine Cloud-Synchronisation
- ✅ Kein Tracking

---

## 🛠️ Entwicklung

### Neues Plugin erstellen

```bash
# 1. Template kopieren
cd plugins
cp PLUGIN_TEMPLATE.py discord_plugin.py

# 2. Anpassen (siehe HOW_TO_ADD_PLUGINS.md)
# 3. In core_v2.py registrieren
# 4. Fertig!
```

### Testing

```python
# Plugin testen
plugin = core.get_plugin('Discord')
print(plugin.is_available())
plugin.send_message('#general', 'Test')

# Task testen
result = core.execute_task("sende Discord-Nachricht")
print(result)
```

---

## ⚙️ Konfiguration

### macOS-Berechtigungen

**Systemeinstellungen → Sicherheit → Datenschutz:**

1. **Bedienungshilfen**: Terminal.app (oder IDE) hinzufügen
2. **Automation**: Zugriff auf Mail, Messages, Photos, etc. erlauben

### API-Konfiguration

```bash
# Temporär
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Permanent (~/.zshrc oder ~/.bash_profile)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.zshrc
```

---

## 🐛 Fehlerbehebung

### "Plugin nicht verfügbar"
→ App in `/Applications/` installieren

### "AppleScript-Fehler"
→ Berechtigungen in Systemeinstellungen prüfen

### "ANTHROPIC_API_KEY nicht gesetzt"
→ `export ANTHROPIC_API_KEY='...'`

### GUI startet nicht
→ `python3 -m tkinter` zum Testen

---

## 📦 Abhängigkeiten

- Python 3.8+
- macOS 10.14+
- Anthropic API Key
- tkinter (in Python auf macOS enthalten)

```bash
pip install anthropic
```

---

## 🗺️ Roadmap

- [x] Plugin-System
- [x] Task Execution
- [x] Multi-App-Integration
- [x] Aktivitätsverfolgung
- [ ] WhatsApp Web API
- [ ] Discord Integration
- [ ] Browser-Automation (Chrome, Safari)
- [ ] Sprachbefehle (Siri)
- [ ] iOS Companion App
- [ ] Export/Import von Aktivitäten
- [ ] Dashboard mit Statistiken

---

## 🤝 Mitwirken

Contributions willkommen!

1. Fork das Repo
2. Erstelle Feature-Branch
3. Commit deine Changes
4. Push und erstelle PR

---

## 📄 Lizenz

MIT License

---

## 🙋 Support

- **Anleitung**: [HOW_TO_ADD_PLUGINS.md](HOW_TO_ADD_PLUGINS.md)
- **Issues**: GitHub Issues
- **Dokumentation**: Siehe README und Inline-Kommentare

---

**Viel Spaß mit deinem erweiterbaren Mac-Assistenten! 🚀**
