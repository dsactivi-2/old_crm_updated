"""
Voice AI Sales Agent - Beispiele
================================

Zeigt verschiedene Anwendungsfälle für den Voice AI Sales Agent.
"""

# =============================================================================
# BEISPIEL 1: Einfacher Standalone-Agent
# =============================================================================

def example_standalone():
    """
    Einfachster Anwendungsfall: Agent erstellen und Anruf tätigen.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    # Agent erstellen
    agent = VoiceAISalesAgent(
        provider='vapi',           # oder 'retell', 'bland'
        api_key='your-api-key',
        language='de'              # oder 'bs', 'sr'
    )

    # Einzelnen Anruf tätigen
    result = agent.call(
        phone='+49123456789',
        name='Max Mustermann'
    )

    print(f"Status: {result.status}")
    print(f"Dauer: {result.duration_seconds}s")
    print(f"Sentiment: {result.sentiment}")
    print(f"Zusammenfassung: {result.summary}")


# =============================================================================
# BEISPIEL 2: Kontakte aus CSV importieren
# =============================================================================

def example_csv_import():
    """
    Kontakte aus CSV importieren und alle anrufen.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    agent = VoiceAISalesAgent(
        provider='vapi',
        api_key='your-api-key',
        language='de'
    )

    # CSV Format erwartet: name,phone,email,company,language
    # Beispiel CSV:
    # name,phone,company,language
    # Max Mustermann,+49123456789,Firma GmbH,de
    # Emir Kovačević,+38761123456,Firma d.o.o.,bs

    agent.import_contacts('leads.csv')

    # Alle Kontakte anrufen (30 Sekunden Pause zwischen Anrufen)
    results = agent.call_all(delay=30, max_calls=10)

    # Statistiken
    stats = agent.get_stats()
    print(f"Anrufe gesamt: {stats['total_calls']}")
    print(f"Erfolgreich: {stats['completed']}")
    print(f"Positiv: {stats['positive_sentiment']}")


# =============================================================================
# BEISPIEL 3: Kontakte aus JSON importieren
# =============================================================================

def example_json_import():
    """
    Kontakte aus JSON importieren.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    agent = VoiceAISalesAgent(
        provider='retell',
        api_key='your-api-key'
    )

    # JSON Format:
    # [
    #   {"name": "Max", "phone": "+49123456789", "language": "de"},
    #   {"name": "Emir", "phone": "+38761123456", "language": "bs"}
    # ]

    agent.import_contacts('leads.json')

    # Nur deutsche Kontakte anrufen
    de_contacts = agent.get_contacts(language='de')
    for contact in de_contacts:
        result = agent.call(contact=contact)


# =============================================================================
# BEISPIEL 4: API-Integration (von externem CRM laden)
# =============================================================================

def example_api_import():
    """
    Kontakte von externer API laden.
    """
    from standalone_voice_ai import VoiceAISalesAgent
    from standalone_voice_ai.importer import ContactImporter

    importer = ContactImporter()

    # Kontakte von API laden
    contacts = importer.import_from_api(
        api_url='https://your-crm.com/api/leads',
        headers={'Authorization': 'Bearer your-token'},
        contacts_key='data'  # JSON-Key mit Kontakt-Array
    )

    agent = VoiceAISalesAgent(provider='vapi', api_key='your-key')
    agent.contacts = contacts

    agent.call_all(delay=30)


# =============================================================================
# BEISPIEL 5: Mehrsprachiger Agent (DE/BS/SR)
# =============================================================================

def example_multilingual():
    """
    Kontakte in verschiedenen Sprachen anrufen.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    agent = VoiceAISalesAgent(
        provider='vapi',
        api_key='your-api-key',
        language='de'  # Standard-Sprache
    )

    # Kontakte mit verschiedenen Sprachen hinzufügen
    agent.add_contact('+49123456789', 'Max Mustermann', language='de')
    agent.add_contact('+38761123456', 'Emir Kovačević', language='bs')
    agent.add_contact('+381641234567', 'Марко Марковић', language='sr')

    # Agent wählt automatisch die richtige Sprache pro Kontakt
    results = agent.call_all(delay=30)


# =============================================================================
# BEISPIEL 6: Benutzerdefinierter Sales-Prompt
# =============================================================================

def example_custom_prompt():
    """
    Mit eigenem Sales-Script arbeiten.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    custom_prompt = """
    Du bist Verkaufsberater für Solaranlagen.

    DEIN ZIEL:
    - Interesse an Solaranlage wecken
    - Kostenlose Beratung anbieten
    - Termin für Hausbesuch vereinbaren

    WICHTIG:
    - Sprich natürlich, wie ein Mensch
    - Nutze Füllwörter: "also", "ähm", "wissen Sie was"
    - Beantworte Fragen zu Kosten mit: "Das hängt von Ihrem Dach ab,
      deshalb würde ich gerne einen kostenlosen Vor-Ort-Termin anbieten"

    Bei Interesse: Termin für Hausbesuch vereinbaren
    Bei Ablehnung: Freundlich verabschieden, Flyer anbieten
    """

    agent = VoiceAISalesAgent(provider='vapi', api_key='your-key')
    agent.set_system_prompt(custom_prompt)

    # Anrufen mit benutzerdefiniertem Prompt
    result = agent.call('+49123456789', 'Herr Müller')


# =============================================================================
# BEISPIEL 7: Ergebnisse exportieren
# =============================================================================

def example_export():
    """
    Anruf-Ergebnisse und Kontakte exportieren.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    agent = VoiceAISalesAgent(provider='vapi', api_key='your-key')

    # ... Anrufe tätigen ...

    # Ergebnisse exportieren
    agent.export_results('call_results.json')

    # Kontakte mit aktualisiertem Status exportieren
    agent.export_contacts('contacts_updated.csv')

    # Nur erfolgreiche Kontakte exportieren
    from standalone_voice_ai.importer import ContactExporter

    completed = [c for c in agent.contacts if c.status == 'completed']
    exporter = ContactExporter(completed)
    exporter.to_csv('successful_contacts.csv')


# =============================================================================
# BEISPIEL 8: Callback bei jedem Anruf
# =============================================================================

def example_callback():
    """
    Callback-Funktion nach jedem Anruf ausführen.
    """
    from standalone_voice_ai import VoiceAISalesAgent

    def on_call_complete(result):
        """Wird nach jedem Anruf aufgerufen."""
        print(f"Anruf zu {result.contact.name} beendet: {result.status}")

        if result.sentiment == 'positive':
            print(f"  -> Interesse vorhanden!")
            # Hier z.B. E-Mail senden oder CRM aktualisieren

        if result.outcome == 'appointment':
            print(f"  -> Termin vereinbart: {result.next_action}")

    agent = VoiceAISalesAgent(provider='vapi', api_key='your-key')
    agent.import_contacts('leads.csv')

    results = agent.call_all(
        delay=30,
        on_call_complete=on_call_complete
    )


# =============================================================================
# BEISPIEL 9: CRM-Integration über API-Client
# =============================================================================

def example_crm_integration():
    """
    Integration mit bestehendem CRM über API.
    """
    from standalone_voice_ai.api_client import VoiceAIAPIClient

    # Client für CRM mit Voice AI erstellen
    client = VoiceAIAPIClient(
        base_url='https://your-crm.com/api/voice',
        api_key='your-crm-api-key'
    )

    # Verfügbare Agents abrufen
    agents = client.get_agents()
    print(f"Verfügbare Agents: {agents.data}")

    # Anruf über CRM starten (mit Customer-ID)
    result = client.start_call(
        agent_id=1,
        customer_id=42  # CRM Customer ID
    )
    print(f"Call ID: {result.data['call_id']}")

    # Status abfragen
    status = client.get_call_status(result.data['call_id'])
    print(f"Status: {status.data['status']}")


# =============================================================================
# BEISPIEL 10: QuickConnect für schnelle Integration
# =============================================================================

def example_quick_connect():
    """
    Schnelle Integration für bestehende Systeme.
    """
    from standalone_voice_ai.api_client import QuickConnect

    qc = QuickConnect(
        crm_api_url='https://your-crm.com/api',
        crm_api_key='crm-key',
        voice_provider='vapi',
        voice_api_key='vapi-key'
    )

    # Leads aus CRM abrufen
    leads = qc.get_leads(status='lead', limit=10)

    # Alle Leads anrufen
    results = qc.call_all_leads(
        status='lead',
        max_calls=10,
        delay=30
    )


# =============================================================================
# BEISPIEL 11: Konfiguration speichern/laden
# =============================================================================

def example_config():
    """
    Konfiguration speichern und laden.
    """
    from standalone_voice_ai import VoiceAISalesAgent
    from standalone_voice_ai.config import VoiceAIConfig

    # Konfiguration erstellen
    config = VoiceAIConfig(
        provider='vapi',
        api_key='your-api-key',
        primary_language='de'
    )
    config.llm.model = 'gpt-4o'
    config.voice.provider = 'elevenlabs'
    config.voice.voice_id = 'your-voice-id'

    # Speichern
    config.save('agent_config.json')

    # Später laden und Agent erstellen
    agent = VoiceAISalesAgent.load_config('agent_config.json')


# =============================================================================
# BEISPIEL 12: Webhook-Server
# =============================================================================

def example_webhook_server():
    """
    Webhook-Server für Provider-Callbacks.
    """
    from standalone_voice_ai.api_client import create_webhook_server

    def handle_call_event(data):
        """Verarbeitet Webhook-Events."""
        print(f"Event: {data['event_type']}")
        print(f"Call ID: {data['call_id']}")

        if data['event_type'] == 'end-of-call-report':
            print(f"Transcript: {data['transcript']}")
            print(f"Summary: {data['summary']}")

            # Hier: CRM aktualisieren, E-Mail senden, etc.

    # Server starten
    app = create_webhook_server(callback=handle_call_event)
    app.run(host='0.0.0.0', port=8080)

    # Webhook-URL für Provider: http://your-server:8080/webhook/vapi


if __name__ == '__main__':
    # Beispiel ausführen
    print("Voice AI Sales Agent - Beispiele")
    print("=" * 50)
    print("\nVerfügbare Beispiele:")
    print("  example_standalone()      - Einfacher Agent")
    print("  example_csv_import()      - CSV Import")
    print("  example_json_import()     - JSON Import")
    print("  example_multilingual()    - Mehrsprachig")
    print("  example_custom_prompt()   - Eigenes Script")
    print("  example_crm_integration() - CRM Integration")
    print("  example_quick_connect()   - Schnelle Integration")
