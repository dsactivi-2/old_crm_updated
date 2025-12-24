# Voice AI Sales Agent

KI-gestützter Telefon-Sales-Agent für automatisierte Kundenanrufe.

**Sprachen:** Deutsch, Bosnisch, Serbisch
**Provider:** Vapi.ai, Retell.ai, Bland.ai

---

## Schnellstart

### 1. CRM-Integration (bereits im CRM integriert)

```bash
# Dependencies installieren
pip install -r requirements.txt

# Server starten
python app.py

# Voice AI Dashboard öffnen
# http://localhost:5000/voice-ai
```

### 2. Standalone-Modul (eigenständig nutzbar)

```python
from standalone_voice_ai import VoiceAISalesAgent

# Agent erstellen
agent = VoiceAISalesAgent(
    provider='vapi',        # oder 'retell', 'bland'
    api_key='your-key',
    language='de'           # oder 'bs', 'sr'
)

# Kontakte importieren
agent.import_contacts('leads.csv')

# Alle anrufen
results = agent.call_all(delay=30)

# Statistiken
print(agent.get_stats())
```

---

## Provider-Vergleich

| Feature | Vapi.ai | Retell.ai | Bland.ai |
|---------|---------|-----------|----------|
| Latenz | ~500-800ms | ~300-500ms | ~600-900ms |
| Deutsch | Sehr gut | Sehr gut | Gut |
| Bosnisch/Serbisch | Via Azure | Via Azure | Begrenzt |
| Preis/Minute | ~$0.05 | ~$0.07 | ~$0.09 |
| Setup | Mittel | Einfach | Einfach |

**Empfehlung:**
- Beste Latenz: **Retell.ai**
- Beste Flexibilität: **Vapi.ai**
- Sales-fokussiert: **Bland.ai**

---

## API-Keys beschaffen

### Vapi.ai
1. https://vapi.ai registrieren
2. Dashboard → API Keys → Create Key

### Retell.ai
1. https://retell.ai registrieren
2. Settings → API Keys

### Bland.ai
1. https://bland.ai registrieren
2. Account → API Key

### ElevenLabs (für beste deutsche Stimmen)
1. https://elevenlabs.io registrieren
2. Profile → API Key

### Twilio (für Telefonie)
1. https://twilio.com registrieren
2. Account SID + Auth Token kopieren
3. Telefonnummer kaufen

---

## Konfiguration

### Umgebungsvariablen (.env)

```env
# Provider
VOICE_AI_PROVIDER=vapi
VOICE_AI_API_KEY=your-vapi-key

# Sprache
VOICE_AI_LANGUAGE=de

# TTS (Text-to-Speech)
TTS_PROVIDER=elevenlabs
TTS_VOICE_ID=pNInz6obpgDQGcFmaJgB

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Telefonie
TELEPHONY_PROVIDER=twilio
PHONE_NUMBER=+49123456789
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token

# Webhooks
VOICE_AI_WEBHOOK_URL=https://your-server.com/api/voice/webhooks/vapi
```

---

## CSV-Format für Import

```csv
name,phone,email,company,language,priority
Max Mustermann,+49123456789,max@example.de,Firma GmbH,de,1
Emir Kovačević,+38761123456,emir@example.ba,Firma d.o.o.,bs,2
Марко Марковић,+381641234567,marko@example.rs,Фирма д.о.о.,sr,3
```

**Spalten:**
- `name` (Pflicht): Kundenname
- `phone` (Pflicht): Telefonnummer mit Ländervorwahl
- `email`: E-Mail-Adresse
- `company`: Firmenname
- `language`: de, bs, sr (Standard: de)
- `priority`: 1-10 (1 = höchste)

---

## API-Endpunkte (CRM-Integration)

### Agents
```
GET  /api/voice/agents          - Liste aller Agents
POST /api/voice/agents          - Agent erstellen
GET  /api/voice/agents/{id}     - Agent-Details
```

### Calls
```
POST /api/voice/calls/start     - Anruf starten
GET  /api/voice/calls           - Anruf-Liste
GET  /api/voice/calls/{id}      - Anruf-Details
```

### Queue
```
GET  /api/voice/queue           - Queue abrufen
POST /api/voice/queue           - Zur Queue hinzufügen
```

### Webhooks (für Provider)
```
POST /api/voice/webhooks/vapi   - Vapi.ai Webhook
POST /api/voice/webhooks/retell - Retell.ai Webhook
POST /api/voice/webhooks/bland  - Bland.ai Webhook
```

---

## Stimmen-Empfehlungen

### Deutsch
| Provider | Voice ID | Name | Geschlecht |
|----------|----------|------|------------|
| ElevenLabs | pNInz6obpgDQGcFmaJgB | Adam | Männlich |
| ElevenLabs | 21m00Tcm4TlvDq8ikWAM | Rachel | Weiblich |
| Azure | de-DE-ConradNeural | Conrad | Männlich |
| Azure | de-DE-KatjaNeural | Katja | Weiblich |

### Bosnisch
| Provider | Voice ID | Name | Geschlecht |
|----------|----------|------|------------|
| Azure | bs-BA-VesnaNeural | Vesna | Weiblich |
| Azure | bs-BA-GoranNeural | Goran | Männlich |

### Serbisch
| Provider | Voice ID | Name | Geschlecht |
|----------|----------|------|------------|
| Azure | sr-RS-SophieNeural | Sophie | Weiblich |
| Azure | sr-RS-NicholasNeural | Nicholas | Männlich |

---

## Tipps für menschlich klingende Agents

### Im System-Prompt:
```
WICHTIG - Klinge menschlich:
- Nutze Füllwörter: "also", "ähm", "ja genau", "wissen Sie was"
- Mache kurze Pausen beim Nachdenken
- Reagiere empathisch auf Einwände
- Stelle Rückfragen
- Sprich in kurzen, natürlichen Sätzen

VERMEIDE:
- Roboter-Phrasen wie "Ich werde nun..."
- Zu formelle Sprache
- Lange Monologe
```

### Technische Einstellungen:
- **Backchannel aktivieren:** Agent sagt "Mhm", "Ja" während Kunde spricht
- **Background Sound:** Büro-Ambiente für Authentizität
- **Interruption Sensitivity:** Hoch (Agent reagiert auf Unterbrechungen)
- **Latenz minimieren:** < 500ms für natürlichen Gesprächsfluss

---

## Kosten-Kalkulation

| Komponente | Kosten/Minute |
|------------|---------------|
| Vapi.ai | ~$0.05 |
| ElevenLabs TTS | ~$0.01 |
| OpenAI GPT-4o-mini | ~$0.002 |
| Twilio | ~$0.014 |
| **Gesamt** | **~$0.08/Min** |

**Pro 3-Minuten-Call:** ~$0.25
**100 Calls/Tag:** ~$25

---

## Fehlerbehebung

### "No phone number"
- Kontakt hat keine Telefonnummer
- CSV-Spalte prüfen (phone, telefon, tel)

### "Invalid API key"
- API-Key prüfen
- Provider-Dashboard checken

### "Call failed"
- Telefonnummer-Format prüfen (+49...)
- Twilio-Guthaben prüfen
- Webhook-URL erreichbar?

### Schlechte Sprachqualität
- ElevenLabs statt Azure für Deutsch
- Voice ID prüfen
- Niedrigere Geschwindigkeit testen

---

## Support

Bei Fragen oder Problemen:
- GitHub Issues: [Repository]
- Dokumentation: Siehe `standalone_voice_ai/examples.py`
