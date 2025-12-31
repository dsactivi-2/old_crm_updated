# Mac Remote Assistant - Nutzungsanleitung

## 🚀 App Starten

```bash
open "/Applications/Mac Remote Assistant.app"
```

## 💬 Mit der App interagieren

### 1. GUI Dashboard (Hauptmethode)

Die App öffnet automatisch ein Dashboard mit 5 Tabs:

#### Tab 1: 🤖 Assistent (Chat)

Hier gibst du deine Befehle ein:

**Beispiele:**

```
- "Zeige meine ungelesenen E-Mails"
- "Liste alle Sender mit ungelesenen Mails auf"
- "Sende E-Mail an max@example.com mit Betreff 'Hallo'"
- "Was habe ich vor 3 Tagen gemacht?"
- "Suche Fotos vom Dezember 2024"
```

#### Tab 2: 📊 Aktivitäten

Zeigt deine täglichen Computer-Aktivitäten:

- Welche Apps du verwendet hast
- Zeiterfassung
- Zeitreise-Funktion ("Was habe ich am X gemacht?")

#### Tab 3: ✉️ E-Mails

Direkter Zugriff auf Mail.app:

- Ungelesene Mails anzeigen
- Nach Sender gruppiert
- Summe der ungelesenen Mails

#### Tab 4: 📸 Fotos

Integration mit Photos.app:

- Fotos durchsuchen
- Nach Datum filtern
- Medien verwalten

#### Tab 5: ⚙️ Einstellungen

- API Keys verwalten
- Plugins aktivieren/deaktivieren
- System-Status

---

### 2. Spracheingabe (In Entwicklung)

**Aktueller Status:**

- ✅ Text-to-Speech funktioniert (App kann sprechen)
- ❌ Speech-to-Text noch nicht implementiert (App kann noch nicht zuhören)

**Geplante Funktionen:**

```
- Wake-Word: "Hey Assistent"
- Kontinuierliches Zuhören
- Sprachbefehle wie: "Sende Nachricht an Max"
```

**Workaround:**
Du kannst Befehle aktuell nur schriftlich im Chat-Tab eingeben.

---

### 3. Python API (Für Entwickler)

```python
from core_v2 import MacAssistantCore

# Initialisieren
core = MacAssistantCore(api_key="dein-api-key")

# Query verarbeiten
result = core.process_user_query("Zeige meine E-Mails")
print(result)

# Task ausführen
task = core.execute_task("Sende E-Mail an max@example.com")
print(task)
```

---

## 🔧 Verfügbare Befehle

### E-Mail-Befehle

```
- "Zeige ungelesene E-Mails"
- "Liste alle Sender mit ungelesenen Mails"
- "Sende E-Mail an [email] mit Betreff [subject] und Text [body]"
- "Suche E-Mails von [sender]"
```

### Aktivitäts-Befehle

```
- "Was habe ich heute gemacht?"
- "Zeige meine Aktivitäten vom [Datum]"
- "Welche Apps habe ich am meisten genutzt?"
```

### Foto-Befehle

```
- "Zeige Fotos vom [Datum]"
- "Suche Fotos mit [Tag]"
- "Zeige meine neuesten Fotos"
```

### Messaging-Befehle (wenn Plugins aktiviert)

```
- "Sende Nachricht an [Name] über Slack: [Text]"
- "Zeige Telegram Nachrichten"
- "Sende Viber Nachricht"
```

---

## 🐛 Bekannte Einschränkungen

1. **Spracheingabe**
   - Speech-to-Text noch nicht implementiert
   - Nur schriftliche Befehle möglich

2. **Mail-Integration**
   - Benötigt Berechtigung für Apple Mail
   - Muss in Systemeinstellungen erlaubt werden

3. **Photos-Integration**
   - Benötigt Berechtigung für Photos.app
   - Erste Nutzung fragt nach Zugriff

---

## ⚙️ Berechtigungen erteilen

### Bedienungshilfen:

```
Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen
→ Mac Remote Assistant aktivieren
```

### Automation:

```
Systemeinstellungen → Datenschutz & Sicherheit → Automation
→ Mac Remote Assistant erlauben für:
   - Mail
   - Photos
   - Messages
```

---

## 🆘 Problemlösung

### App startet nicht?

```bash
# App-Signatur entfernen
xattr -cr "/Applications/Mac Remote Assistant.app"

# Neu starten
open "/Applications/Mac Remote Assistant.app"
```

### "API Key nicht gefunden"?

```bash
# In Einstellungen-Tab API Key eingeben oder:
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

### Import-Fehler?

```bash
# App wurde bereits mit korrigierten Imports neu gebaut
# Falls Probleme: App neu installieren
cd ~/activi-dev-repos/old_crm_updated/mac_assistant
./create_app.sh
cp -r "Mac Remote Assistant.app" /Applications/
```

---

## 📝 Nächste Schritte / Feature-Roadmap

### Priorität 1: Spracheingabe aktivieren

- [ ] macOS Dictation API integrieren
- [ ] Wake-Word Erkennung
- [ ] Kontinuierliches Zuhören

### Priorität 2: Weitere Plugins

- [ ] Calendar Integration
- [ ] Reminders/Notes
- [ ] Browser-Steuerung
- [ ] File-Manager-Integration

### Priorität 3: Autonome Features

- [ ] Proaktive Benachrichtigungen
- [ ] Automatische Aufgaben-Erkennung
- [ ] Smart Suggestions

---

**Version:** 2.0
**Letzte Aktualisierung:** 2025-12-24
**Status:** ✅ Funktionsfähig
