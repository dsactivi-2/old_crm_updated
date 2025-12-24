"""
Standalone Voice AI Sales Agent Module
======================================

Eigenständiges Modul für KI-gestützte Telefon-Sales-Agents.
Kann unabhängig oder in bestehende Systeme integriert werden.

Features:
- Multi-Provider Support (Vapi.ai, Retell.ai, Bland.ai)
- Multilingual (Deutsch, Bosnisch, Serbisch)
- Import/Export von Kontakten und Konfigurationen
- REST API für externe Anbindung
- Lead Scoring und Analyse

Usage:
    from standalone_voice_ai import VoiceAISalesAgent

    agent = VoiceAISalesAgent(
        provider='vapi',
        api_key='your-api-key',
        language='de'
    )

    # Kontakte importieren
    agent.import_contacts('contacts.csv')

    # Anruf starten
    result = agent.call(phone='+49123456789', name='Max Mustermann')
"""

__version__ = '1.0.0'
__author__ = 'Voice AI Sales System'

from .agent import VoiceAISalesAgent
from .config import VoiceAIConfig
from .importer import ContactImporter, ContactExporter
from .api_client import VoiceAIAPIClient
