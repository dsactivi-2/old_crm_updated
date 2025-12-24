"""
Voice AI Sales Agent - Hauptmodul
Eigenständiger Agent für KI-gestützte Sales Calls
"""

import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field

from .config import VoiceAIConfig, DEFAULT_PROMPTS
from .importer import Contact, ContactImporter, ContactExporter, import_contacts


# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VoiceAI')


@dataclass
class CallResult:
    """Ergebnis eines Anrufs."""
    call_id: str = ''
    contact: Contact = None
    status: str = 'unknown'  # completed, failed, no_answer, busy
    duration_seconds: int = 0
    transcript: str = ''
    summary: str = ''
    sentiment: str = 'neutral'  # positive, neutral, negative
    outcome: str = ''  # interested, not_interested, callback, appointment
    next_action: str = ''
    recording_url: str = ''
    cost: float = 0.0
    error: str = ''
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        result = {
            'call_id': self.call_id,
            'status': self.status,
            'duration_seconds': self.duration_seconds,
            'transcript': self.transcript,
            'summary': self.summary,
            'sentiment': self.sentiment,
            'outcome': self.outcome,
            'next_action': self.next_action,
            'recording_url': self.recording_url,
            'cost': self.cost,
            'error': self.error,
            'timestamp': self.timestamp
        }
        if self.contact:
            result['contact'] = self.contact.to_dict()
        return result


class VoiceAISalesAgent:
    """
    Standalone Voice AI Sales Agent.

    Unterstützt Vapi.ai, Retell.ai und Bland.ai als Provider.
    Multilingual: Deutsch, Bosnisch, Serbisch.

    Beispiel:
        agent = VoiceAISalesAgent(
            provider='vapi',
            api_key='your-api-key',
            language='de'
        )

        # Kontakte importieren
        agent.import_contacts('contacts.csv')

        # Einzelnen Anruf tätigen
        result = agent.call('+49123456789', 'Max Mustermann')

        # Alle Kontakte anrufen
        results = agent.call_all(delay=30)
    """

    def __init__(self, provider: str = 'vapi', api_key: str = '',
                 language: str = 'de', config: VoiceAIConfig = None):
        """
        Initialisiert den Agent.

        Args:
            provider: 'vapi', 'retell' oder 'bland'
            api_key: API-Key des Providers
            language: 'de', 'bs' oder 'sr'
            config: Optionale vollständige Konfiguration
        """
        if config:
            self.config = config
        else:
            self.config = VoiceAIConfig(
                provider=provider,
                api_key=api_key,
                primary_language=language
            )

        self.contacts: List[Contact] = []
        self.call_results: List[CallResult] = []
        self.provider_client = None

        # Provider initialisieren
        self._init_provider()

        logger.info(f"VoiceAI Agent initialisiert: {provider} / {language}")

    def _init_provider(self):
        """Initialisiert den Provider-Client."""
        try:
            import requests
            self._requests = requests
        except ImportError:
            raise ImportError("requests library required: pip install requests")

        self.provider_client = self._create_provider_client()

    def _create_provider_client(self):
        """Erstellt Provider-spezifischen Client."""
        provider = self.config.provider.lower()

        if provider == 'vapi':
            return VapiClient(self.config)
        elif provider == 'retell':
            return RetellClient(self.config)
        elif provider == 'bland':
            return BlandClient(self.config)
        else:
            raise ValueError(f"Unbekannter Provider: {provider}")

    # =========================================================================
    # KONTAKT-MANAGEMENT
    # =========================================================================

    def import_contacts(self, source: str, format: str = 'auto') -> int:
        """
        Importiert Kontakte aus Datei oder URL.

        Args:
            source: Dateipfad, URL oder String
            format: 'csv', 'json', 'api' oder 'auto'

        Returns:
            Anzahl importierter Kontakte
        """
        new_contacts = import_contacts(source, format)
        self.contacts.extend(new_contacts)
        logger.info(f"{len(new_contacts)} Kontakte importiert")
        return len(new_contacts)

    def add_contact(self, phone: str, name: str = '', **kwargs) -> Contact:
        """
        Fügt einzelnen Kontakt hinzu.

        Args:
            phone: Telefonnummer
            name: Name des Kontakts
            **kwargs: Weitere Felder (email, company, language, etc.)

        Returns:
            Contact-Objekt
        """
        contact = Contact(
            phone=phone,
            name=name or 'Unbekannt',
            language=kwargs.get('language', self.config.primary_language),
            **{k: v for k, v in kwargs.items() if k != 'language'}
        )
        self.contacts.append(contact)
        return contact

    def get_contacts(self, status: str = None,
                    language: str = None) -> List[Contact]:
        """Gibt Kontakte gefiltert zurück."""
        contacts = self.contacts

        if status:
            contacts = [c for c in contacts if c.status == status]

        if language:
            contacts = [c for c in contacts if c.language == language]

        return contacts

    def export_contacts(self, filepath: str, format: str = 'auto') -> str:
        """Exportiert Kontakte in Datei."""
        exporter = ContactExporter(self.contacts)
        if format == 'auto':
            format = 'json' if filepath.endswith('.json') else 'csv'

        if format == 'csv':
            return exporter.to_csv(filepath)
        else:
            return exporter.to_json(filepath)

    def clear_contacts(self):
        """Löscht alle Kontakte."""
        self.contacts = []

    # =========================================================================
    # ANRUF-FUNKTIONEN
    # =========================================================================

    def call(self, phone: str = None, name: str = None,
            contact: Contact = None, wait_for_completion: bool = True,
            timeout: int = 600) -> CallResult:
        """
        Tätigt einen Anruf.

        Args:
            phone: Telefonnummer (wenn kein Contact übergeben)
            name: Name (wenn kein Contact übergeben)
            contact: Contact-Objekt
            wait_for_completion: Warten bis Anruf beendet
            timeout: Maximale Wartezeit in Sekunden

        Returns:
            CallResult mit Ergebnis
        """
        if contact is None:
            if not phone:
                raise ValueError("phone oder contact erforderlich")
            contact = Contact(phone=phone, name=name or 'Unbekannt',
                            language=self.config.primary_language)

        logger.info(f"Starte Anruf: {contact.name} ({contact.phone})")

        try:
            # Anruf über Provider starten
            result = self.provider_client.start_call(contact)

            # Warten auf Abschluss wenn gewünscht
            if wait_for_completion and result.status not in ['completed', 'failed']:
                result = self._wait_for_completion(result.call_id, timeout)

            # Kontakt-Status aktualisieren
            contact.status = 'completed' if result.status == 'completed' else 'failed'
            contact.call_count += 1
            contact.last_called = datetime.now().isoformat()

            result.contact = contact
            self.call_results.append(result)

            logger.info(f"Anruf beendet: {result.status} ({result.duration_seconds}s)")

        except Exception as e:
            logger.error(f"Anruf fehlgeschlagen: {e}")
            result = CallResult(
                contact=contact,
                status='failed',
                error=str(e)
            )
            self.call_results.append(result)

        return result

    def call_all(self, delay: int = 30,
                max_calls: int = None,
                on_call_complete: Callable[[CallResult], None] = None,
                filter_status: str = 'pending') -> List[CallResult]:
        """
        Ruft alle Kontakte an.

        Args:
            delay: Pause zwischen Anrufen in Sekunden
            max_calls: Maximale Anzahl Anrufe
            on_call_complete: Callback nach jedem Anruf
            filter_status: Nur Kontakte mit diesem Status anrufen

        Returns:
            Liste von CallResults
        """
        contacts = [c for c in self.contacts if c.status == filter_status]

        if max_calls:
            contacts = contacts[:max_calls]

        results = []

        for i, contact in enumerate(contacts):
            logger.info(f"Anruf {i+1}/{len(contacts)}: {contact.name}")

            result = self.call(contact=contact)
            results.append(result)

            if on_call_complete:
                on_call_complete(result)

            # Pause zwischen Anrufen
            if i < len(contacts) - 1:
                logger.info(f"Warte {delay} Sekunden...")
                time.sleep(delay)

        return results

    def _wait_for_completion(self, call_id: str, timeout: int = 600) -> CallResult:
        """Wartet auf Anruf-Abschluss."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.provider_client.get_call_status(call_id)

            if result.status in ['completed', 'failed', 'no_answer', 'busy']:
                return result

            time.sleep(2)

        return CallResult(call_id=call_id, status='timeout', error='Timeout erreicht')

    # =========================================================================
    # ERGEBNISSE & STATISTIKEN
    # =========================================================================

    def get_results(self, status: str = None) -> List[CallResult]:
        """Gibt Anruf-Ergebnisse zurück."""
        if status:
            return [r for r in self.call_results if r.status == status]
        return self.call_results

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück."""
        total = len(self.call_results)
        if total == 0:
            return {'total': 0}

        completed = len([r for r in self.call_results if r.status == 'completed'])
        positive = len([r for r in self.call_results if r.sentiment == 'positive'])

        durations = [r.duration_seconds for r in self.call_results if r.duration_seconds > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0

        costs = [r.cost for r in self.call_results if r.cost > 0]
        total_cost = sum(costs)

        return {
            'total_calls': total,
            'completed': completed,
            'failed': total - completed,
            'success_rate': completed / total if total > 0 else 0,
            'positive_sentiment': positive,
            'positive_rate': positive / completed if completed > 0 else 0,
            'average_duration': avg_duration,
            'total_cost': total_cost,
            'contacts_pending': len([c for c in self.contacts if c.status == 'pending']),
            'contacts_completed': len([c for c in self.contacts if c.status == 'completed'])
        }

    def export_results(self, filepath: str) -> str:
        """Exportiert Anruf-Ergebnisse als JSON."""
        data = {
            'exported_at': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'results': [r.to_dict() for r in self.call_results]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    # =========================================================================
    # KONFIGURATION
    # =========================================================================

    def set_system_prompt(self, prompt: str):
        """Setzt benutzerdefinierten System Prompt."""
        self.config.system_prompt = prompt
        self.provider_client.update_config(self.config)

    def set_language(self, language: str):
        """Ändert Hauptsprache und lädt Standard-Prompt."""
        self.config.primary_language = language
        self.config.system_prompt = DEFAULT_PROMPTS.get(language, DEFAULT_PROMPTS['de'])
        self.provider_client.update_config(self.config)

    def save_config(self, filepath: str):
        """Speichert Konfiguration."""
        self.config.save(filepath)

    @classmethod
    def load_config(cls, filepath: str) -> 'VoiceAISalesAgent':
        """Lädt Agent mit Konfiguration aus Datei."""
        config = VoiceAIConfig.load(filepath)
        return cls(config=config)


# =============================================================================
# PROVIDER CLIENTS
# =============================================================================

class BaseProviderClient:
    """Basis-Klasse für Provider-Clients."""

    def __init__(self, config: VoiceAIConfig):
        self.config = config
        import requests
        self._requests = requests

    def update_config(self, config: VoiceAIConfig):
        self.config = config

    def start_call(self, contact: Contact) -> CallResult:
        raise NotImplementedError

    def get_call_status(self, call_id: str) -> CallResult:
        raise NotImplementedError


class VapiClient(BaseProviderClient):
    """Vapi.ai Client."""

    BASE_URL = "https://api.vapi.ai"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

    def start_call(self, contact: Contact) -> CallResult:
        """Startet Anruf über Vapi."""
        payload = {
            "phoneNumberId": self.config.telephony.phone_number,
            "customer": {
                "number": contact.phone,
                "name": contact.name
            },
            "assistant": {
                "model": {
                    "provider": self.config.llm.provider,
                    "model": self.config.llm.model,
                    "messages": [{"role": "system", "content": self.config.system_prompt}]
                },
                "voice": {
                    "provider": self.config.voice.provider,
                    "voiceId": self.config.voice.voice_id
                },
                "transcriber": {
                    "provider": "deepgram",
                    "language": contact.language
                },
                "firstMessage": self._get_greeting(contact),
                "silenceTimeoutSeconds": 30,
                "maxDurationSeconds": self.config.max_call_duration,
                "backgroundSound": "office",
                "backchannelingEnabled": self.config.enable_backchannel
            }
        }

        try:
            response = self._requests.post(
                f"{self.BASE_URL}/call/phone",
                headers=self._headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return CallResult(
                call_id=data.get('id', ''),
                status='initiated',
                contact=contact
            )
        except Exception as e:
            return CallResult(status='failed', error=str(e), contact=contact)

    def get_call_status(self, call_id: str) -> CallResult:
        """Holt Anruf-Status."""
        try:
            response = self._requests.get(
                f"{self.BASE_URL}/call/{call_id}",
                headers=self._headers()
            )
            response.raise_for_status()
            data = response.json()

            return CallResult(
                call_id=call_id,
                status=data.get('status', 'unknown'),
                duration_seconds=data.get('duration', 0),
                transcript=data.get('transcript', ''),
                recording_url=data.get('recordingUrl', ''),
                cost=data.get('cost', 0)
            )
        except Exception as e:
            return CallResult(call_id=call_id, status='error', error=str(e))

    def _get_greeting(self, contact: Contact) -> str:
        greetings = {
            'de': f"Hallo {contact.name}, guten Tag!",
            'bs': f"Zdravo {contact.name}, dobar dan!",
            'sr': f"Здраво {contact.name}, добар дан!"
        }
        return greetings.get(contact.language, greetings['de'])


class RetellClient(BaseProviderClient):
    """Retell.ai Client."""

    BASE_URL = "https://api.retellai.com"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

    def start_call(self, contact: Contact) -> CallResult:
        """Startet Anruf über Retell."""
        payload = {
            "from_number": self.config.telephony.phone_number,
            "to_number": contact.phone,
            "override_agent_id": None,  # Verwende konfigurierten Agent
            "retell_llm_dynamic_variables": {
                "customer_name": contact.name,
                "customer_language": contact.language
            }
        }

        try:
            response = self._requests.post(
                f"{self.BASE_URL}/create-phone-call",
                headers=self._headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return CallResult(
                call_id=data.get('call_id', ''),
                status='initiated',
                contact=contact
            )
        except Exception as e:
            return CallResult(status='failed', error=str(e), contact=contact)

    def get_call_status(self, call_id: str) -> CallResult:
        """Holt Anruf-Status."""
        try:
            response = self._requests.get(
                f"{self.BASE_URL}/get-call/{call_id}",
                headers=self._headers()
            )
            response.raise_for_status()
            data = response.json()

            return CallResult(
                call_id=call_id,
                status=data.get('call_status', 'unknown'),
                duration_seconds=data.get('duration_ms', 0) // 1000,
                transcript=data.get('transcript', ''),
                summary=data.get('call_analysis', {}).get('call_summary', ''),
                sentiment=data.get('call_analysis', {}).get('user_sentiment', 'neutral'),
                recording_url=data.get('recording_url', '')
            )
        except Exception as e:
            return CallResult(call_id=call_id, status='error', error=str(e))


class BlandClient(BaseProviderClient):
    """Bland.ai Client."""

    BASE_URL = "https://api.bland.ai/v1"

    def _headers(self):
        return {
            "authorization": self.config.api_key,
            "Content-Type": "application/json"
        }

    def start_call(self, contact: Contact) -> CallResult:
        """Startet Anruf über Bland."""
        payload = {
            "phone_number": contact.phone,
            "task": self.config.system_prompt,
            "voice": self.config.voice.voice_id or "matt",
            "language": contact.language,
            "model": "enhanced",
            "first_sentence": self._get_greeting(contact),
            "wait_for_greeting": True,
            "record": self.config.record_calls,
            "from": self.config.telephony.phone_number,
            "webhook": self.config.webhook_url,
            "metadata": {
                "contact_name": contact.name,
                "contact_id": contact.id
            }
        }

        try:
            response = self._requests.post(
                f"{self.BASE_URL}/calls",
                headers=self._headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return CallResult(
                call_id=data.get('call_id', ''),
                status='initiated',
                contact=contact
            )
        except Exception as e:
            return CallResult(status='failed', error=str(e), contact=contact)

    def get_call_status(self, call_id: str) -> CallResult:
        """Holt Anruf-Status."""
        try:
            response = self._requests.get(
                f"{self.BASE_URL}/calls/{call_id}",
                headers=self._headers()
            )
            response.raise_for_status()
            data = response.json()

            return CallResult(
                call_id=call_id,
                status=data.get('status', 'unknown'),
                duration_seconds=data.get('call_length', 0),
                transcript=data.get('concatenated_transcript', ''),
                summary=data.get('summary', ''),
                recording_url=data.get('recording_url', ''),
                cost=data.get('price', 0)
            )
        except Exception as e:
            return CallResult(call_id=call_id, status='error', error=str(e))

    def _get_greeting(self, contact: Contact) -> str:
        greetings = {
            'de': f"Hallo {contact.name}, guten Tag!",
            'bs': f"Zdravo {contact.name}, dobar dan!",
            'sr': f"Здраво {contact.name}, добар дан!"
        }
        return greetings.get(contact.language, greetings['de'])
