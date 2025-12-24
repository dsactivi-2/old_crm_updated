# Mac Remote Assistant 🤖

Ein intelligenter KI-Assistent für macOS, der dir hilft, deinen Mac zu verwalten und automatisieren.

## 🎯 Was kann die App?

### 1. **E-Mail Management**
- Ungelesene E-Mails anzeigen
- Mit KI automatisch E-Mails beantworten
- E-Mails durchsuchen und filtern
- E-Mails kategorisieren (wichtig, spam, etc.)

### 2. **Nachrichten Management**
- Nachrichten aus Messages.app lesen
- Nachrichten senden
- Mit KI automatisch auf Nachrichten antworten

### 3. **Foto Management**
- Fotos durchsuchen
- Fotos nach Datum filtern
- KI-gestützte Foto-Analyse (Duplikate finden, etc.)
- Fotos löschen

### 4. **Aktivitätsverfolgung ("Zeitreise")**
- Verfolgt alle deine Aktivitäten
- Zeigt, was du vor X Tagen gemacht hast
- **Beispiel:** "Was habe ich vor 3 Tagen um 14 Uhr gemacht?"

### 5. **KI-Assistent**
- Natürliche Sprache (Deutsch)
- Intelligente Automatisierung
- Kontextbezogene Antworten

## 🚀 Installation

### Voraussetzungen
- **macOS** (10.14 oder neuer)
- **Python 3.8+**
- **Anthropic API Key** ([hier registrieren](https://www.anthropic.com))

### Schritt 1: Repository klonen

```bash
git clone <repository-url>
cd mac_assistant
```

### Schritt 2: Setup ausführen

```bash
chmod +x setup.sh
./setup.sh
```

### Schritt 3: API Key einrichten

Füge deinen Anthropic API Key als Umgebungsvariable hinzu:

```bash
# In ~/.zshrc oder ~/.bash_profile
export ANTHROPIC_API_KEY='sk-ant-dein-api-key-hier'
```

Oder setze ihn temporär:

```bash
export ANTHROPIC_API_KEY='sk-ant-dein-api-key-hier'
```

### Schritt 4: Berechtigungen erteilen

Die App benötigt folgende macOS-Berechtigungen:

1. **Systemeinstellungen** → **Sicherheit** → **Datenschutz** → **Bedienungshilfen**
   - Füge `Terminal.app` (oder deine IDE wie PyCharm, VS Code) hinzu

2. **Systemeinstellungen** → **Sicherheit** → **Datenschutz** → **Automation**
   - Erlaube `Terminal.app` Zugriff auf:
     - Mail
     - Fotos
     - Messages
     - Kalender
     - Notizen

## 📱 App starten

```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate

# App starten
python3 main.py
```

## 🎮 Verwendung

### Chat-Interface

Die App hat ein benutzerfreundliches GUI mit mehreren Tabs:

#### 1. **Assistent-Tab**
Stelle Fragen in natürlicher Sprache:

```
"Was habe ich vor 3 Tagen um 14 Uhr gemacht?"
"Zeige mir meine neuen E-Mails"
"Welche Fotos habe ich diese Woche gemacht?"
"Suche nach Fotos vom Strand"
```

#### 2. **Aktivitäten-Tab**
- Wähle ein Datum (vor X Tagen)
- Optional: Wähle eine bestimmte Uhrzeit
- Sieh alle Aktivitäten aus dieser Zeit

#### 3. **E-Mails-Tab**
- Ungelesene E-Mails laden
- E-Mails mit KI beantworten
- E-Mails durchsuchen

#### 4. **Fotos-Tab**
- Fotos suchen
- Letzte 7/30 Tage anzeigen
- Fotos löschen
- KI-Analyse für Löschvorschläge

#### 5. **Einstellungen-Tab**
- API Key verwalten
- Aktivitätsverfolgung ein/aus
- Automatische Antworten ein/aus

## 💡 Beispielabfragen

### Zeitreise-Funktion
```
"Was habe ich gestern gemacht?"
"Was habe ich vor 3 Tagen um 14 Uhr gemacht?"
"Zeige mir meine Aktivitäten von heute"
```

### E-Mails
```
"Zeige mir meine neuen E-Mails"
"Habe ich E-Mails von Max?"
"Beantworte die letzte E-Mail"
```

### Fotos
```
"Zeige Fotos von dieser Woche"
"Suche nach Fotos vom Strand"
"Welche Fotos kann ich löschen?"
```

### Nachrichten
```
"Zeige meine letzten Nachrichten"
"Schreibe eine Nachricht an Anna"
```

## 🔧 Architektur

```
mac_assistant/
├── main.py                 # Haupteinstiegspunkt
├── core.py                 # Kernlogik
├── database/
│   └── activity_tracker.py # Aktivitätsdatenbank
├── scripts/
│   └── applescript_bridge.py # AppleScript-Integration
├── utils/
│   └── ai_assistant.py     # KI-Integration (Claude)
└── ui/
    └── main_window.py      # GUI (Tkinter)
```

### Komponenten

1. **ActivityTracker** - SQLite-Datenbank für Aktivitätsverfolgung
2. **AppleScriptBridge** - Interaktion mit macOS-Apps
3. **AIAssistant** - Claude API Integration
4. **MacAssistantCore** - Verbindet alle Komponenten
5. **MacAssistantGUI** - Benutzeroberfläche

## 🔒 Datenschutz & Sicherheit

- **Alle Daten bleiben lokal** auf deinem Mac
- Datenbank wird in `~/.mac_assistant/activities.db` gespeichert
- Nur KI-Anfragen werden an Anthropic API gesendet
- Keine Cloud-Synchronisation
- Kein Tracking

## 🐛 Fehlerbehebung

### "ANTHROPIC_API_KEY nicht gesetzt"
```bash
export ANTHROPIC_API_KEY='dein-key-hier'
```

### "AppleScript-Fehler: Operation nicht erlaubt"
→ Überprüfe Berechtigungen in Systemeinstellungen → Sicherheit → Datenschutz

### "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### GUI startet nicht
Stelle sicher, dass Python auf macOS tkinter unterstützt:
```bash
python3 -m tkinter
```

## 📊 Datenbank-Schema

### Activities Table
- `timestamp` - Zeitstempel
- `app_name` - App-Name
- `activity_type` - Aktivitätstyp
- `title` - Titel/Window
- `content` - Inhalt
- `metadata` - JSON-Metadaten

### Mail Activities Table
- E-Mail-spezifische Felder (sender, recipient, subject, body)

### WhatsApp Activities Table
- Nachrichten-spezifische Felder (contact, message, chat_name)

### Photo Activities Table
- Foto-spezifische Felder (file_path, file_name, tags, date_taken)

## 🤝 Mitwirken

Contributions sind willkommen! Bitte erstelle einen Pull Request.

## 📄 Lizenz

MIT License - siehe LICENSE-Datei

## ⚠️ Disclaimer

Diese App ist ein Proof-of-Concept. Verwende sie verantwortungsvoll und beachte die Privatsphäre anderer.

## 🙋 Support

Bei Fragen oder Problemen:
- Erstelle ein GitHub Issue
- Überprüfe die Dokumentation
- Überprüfe macOS-Berechtigungen

## 🔮 Roadmap

- [ ] Unterstützung für weitere Apps (Safari, Chrome, etc.)
- [ ] Export von Aktivitätsdaten
- [ ] Erweiterte Automatisierungsregeln
- [ ] Sprachbefehle (Siri Integration)
- [ ] iOS Companion App
- [ ] Dashboard mit Statistiken
- [ ] Intelligente Erinnerungen

---

**Viel Spaß mit deinem Mac Remote Assistant! 🚀**
