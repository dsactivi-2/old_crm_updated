"""
Voice AI Sales Agent - Service Layer
Multi-Provider Unterstützung: Vapi.ai, Retell.ai, Bland.ai
Sprachen: Deutsch, Bosnisch, Serbisch
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


# =============================================================================
# SYSTEM PROMPTS FÜR SALES AGENT (Multilingual)
# =============================================================================

SYSTEM_PROMPTS = {
    'de': """Du bist ein freundlicher Verkaufsberater. Sprich natürlich wie ein Mensch.

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

DEIN ZIEL:
1. Begrüße freundlich und persönlich
2. Finde heraus, was der Kunde braucht
3. Präsentiere die passende Lösung
4. Bearbeite Einwände einfühlsam
5. Schließe mit klarem nächsten Schritt ab

Bei Interesse: Termin vereinbaren oder Angebot zusenden.
Bei Desinteresse: Freundlich verabschieden, Tür offen halten.""",

    'bs': """Ti si prijateljski prodajni savjetnik. Govori prirodno kao čovjek.

VAŽNO - Zvuči ljudski:
- Koristi poštapalice: "znači", "ovaj", "eto", "ma da"
- Pravi kratke pauze dok razmišljaš
- Reaguj empatično na prigovore
- Postavljaj potpitanja
- Govori kratkim, prirodnim rečenicama

IZBJEGAVAJ:
- Robot fraze kao "Sada ću..."
- Previše formalnog jezika
- Duge monologe

TVOJ CILJ:
1. Pozdravi prijateljski i lično
2. Otkrij šta klijentu treba
3. Predstavi odgovarajuće rješenje
4. Obradi prigovore s razumijevanjem
5. Završi s jasnim sljedećim korakom""",

    'sr': """Ти си пријатељски продајни саветник. Говори природно као човек.

ВАЖНО - Звучи људски:
- Користи поштапалице: "значи", "овај", "ето", "ма да"
- Прави кратке паузе док размишљаш
- Реагуј емпатично на приговоре
- Постављај потпитања
- Говори кратким, природним реченицама

ИЗБЕГАВАЈ:
- Робот фразе као "Сада ћу..."
- Превише формалног језика
- Дуге монологе

ТВОЈ ЦИЉ:
1. Поздрави пријатељски и лично
2. Открij шта клијенту треба
3. Представи одговарајуће решење
4. Обради приговоре с разумевањем
5. Заврши са јасним следећим кораком"""
}


# =============================================================================
# BASE PROVIDER CLASS
# =============================================================================

class VoiceAIProvider(ABC):
    """Abstract Base Class für Voice AI Provider."""

    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}

    @abstractmethod
    def create_agent(self, name: str, system_prompt: str, voice_config: Dict) -> Dict:
        """Erstellt einen Voice Agent beim Provider."""
        pass

    @abstractmethod
    def start_outbound_call(self, agent_id: str, phone_number: str,
                           customer_data: Dict) -> Dict:
        """Startet einen ausgehenden Anruf."""
        pass

    @abstractmethod
    def get_call_status(self, call_id: str) -> Dict:
        """Holt den Status eines Anrufs."""
        pass

    @abstractmethod
    def parse_webhook(self, payload: Dict) -> Dict:
        """Parsed Webhook-Daten vom Provider."""
        pass


# =============================================================================
# VAPI.AI PROVIDER
# =============================================================================

class VapiProvider(VoiceAIProvider):
    """Vapi.ai Integration."""

    BASE_URL = "https://api.vapi.ai"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_agent(self, name: str, system_prompt: str, voice_config: Dict) -> Dict:
        """Erstellt Vapi Assistant."""
        payload = {
            "name": name,
            "model": {
                "provider": voice_config.get('llm_provider', 'openai'),
                "model": voice_config.get('llm_model', 'gpt-4o-mini'),
                "messages": [{"role": "system", "content": system_prompt}],
                "temperature": 0.7
            },
            "voice": {
                "provider": voice_config.get('tts_provider', 'elevenlabs'),
                "voiceId": voice_config.get('tts_voice_id', 'pNInz6obpgDQGcFmaJgB')  # Adam
            },
            "transcriber": {
                "provider": voice_config.get('stt_provider', 'deepgram'),
                "language": voice_config.get('language', 'de')
            },
            "firstMessage": voice_config.get('first_message', "Hallo, guten Tag!"),
            "endCallMessage": voice_config.get('end_message', "Auf Wiederhören!"),
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 600,  # 10 Minuten max
            "backgroundSound": "office",  # Büro-Ambiente
            "backchannelingEnabled": True,  # "Mhm", "Ja" während Kunde spricht
            "hipaaEnabled": False
        }

        response = requests.post(
            f"{self.BASE_URL}/assistant",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def start_outbound_call(self, agent_id: str, phone_number: str,
                           customer_data: Dict) -> Dict:
        """Startet Outbound Call über Vapi."""
        payload = {
            "assistantId": agent_id,
            "customer": {
                "number": phone_number,
                "name": customer_data.get('name', 'Kunde')
            },
            "phoneNumberId": self.config.get('phone_number_id'),
            "assistantOverrides": {
                "variableValues": {
                    "customer_name": customer_data.get('name', ''),
                    "customer_company": customer_data.get('company', ''),
                    "customer_notes": customer_data.get('notes', '')
                }
            }
        }

        response = requests.post(
            f"{self.BASE_URL}/call/phone",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_call_status(self, call_id: str) -> Dict:
        """Holt Call-Details von Vapi."""
        response = requests.get(
            f"{self.BASE_URL}/call/{call_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def parse_webhook(self, payload: Dict) -> Dict:
        """Parsed Vapi Webhook."""
        message = payload.get('message', {})
        call = message.get('call', {})

        event_type = message.get('type', '')

        result = {
            'provider': 'vapi',
            'event_type': event_type,
            'call_id': call.get('id'),
            'status': call.get('status'),
            'phone_from': call.get('customer', {}).get('number'),
            'phone_to': call.get('phoneNumber', {}).get('number'),
            'started_at': call.get('startedAt'),
            'ended_at': call.get('endedAt'),
            'duration_seconds': None,
            'transcript': None,
            'recording_url': None,
            'cost': None
        }

        # End of call
        if event_type == 'end-of-call-report':
            result['transcript'] = message.get('transcript', '')
            result['summary'] = message.get('summary', '')
            result['recording_url'] = message.get('recordingUrl')
            result['cost'] = message.get('cost')

            # Berechne Dauer
            if call.get('startedAt') and call.get('endedAt'):
                start = datetime.fromisoformat(call['startedAt'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(call['endedAt'].replace('Z', '+00:00'))
                result['duration_seconds'] = int((end - start).total_seconds())

        return result


# =============================================================================
# RETELL.AI PROVIDER
# =============================================================================

class RetellProvider(VoiceAIProvider):
    """Retell.ai Integration."""

    BASE_URL = "https://api.retellai.com"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_agent(self, name: str, system_prompt: str, voice_config: Dict) -> Dict:
        """Erstellt Retell Agent."""
        # Erst LLM erstellen
        llm_payload = {
            "model": voice_config.get('llm_model', 'gpt-4o-mini'),
            "general_prompt": system_prompt,
            "begin_message": voice_config.get('first_message', "Hallo, guten Tag!"),
            "general_tools": []
        }

        llm_response = requests.post(
            f"{self.BASE_URL}/create-retell-llm",
            headers=self._headers(),
            json=llm_payload
        )
        llm_response.raise_for_status()
        llm_id = llm_response.json().get('llm_id')

        # Dann Agent erstellen
        agent_payload = {
            "llm_websocket_url": f"wss://api.retellai.com/llm-websocket/{llm_id}",
            "agent_name": name,
            "voice_id": voice_config.get('tts_voice_id', 'eleven_multilingual_v2'),
            "language": voice_config.get('language', 'de-DE'),
            "ambient_sound": "coffee-shop",
            "backchannel_frequency": 0.8,
            "enable_backchannel": True,
            "interruption_sensitivity": 0.8,
            "responsiveness": 0.8
        }

        response = requests.post(
            f"{self.BASE_URL}/create-agent",
            headers=self._headers(),
            json=agent_payload
        )
        response.raise_for_status()
        return response.json()

    def start_outbound_call(self, agent_id: str, phone_number: str,
                           customer_data: Dict) -> Dict:
        """Startet Outbound Call über Retell."""
        payload = {
            "agent_id": agent_id,
            "to_number": phone_number,
            "from_number": self.config.get('from_number'),
            "retell_llm_dynamic_variables": {
                "customer_name": customer_data.get('name', ''),
                "customer_company": customer_data.get('company', ''),
            }
        }

        response = requests.post(
            f"{self.BASE_URL}/create-phone-call",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_call_status(self, call_id: str) -> Dict:
        """Holt Call-Details von Retell."""
        response = requests.get(
            f"{self.BASE_URL}/get-call/{call_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def parse_webhook(self, payload: Dict) -> Dict:
        """Parsed Retell Webhook."""
        event = payload.get('event', '')
        call = payload.get('call', {})

        result = {
            'provider': 'retell',
            'event_type': event,
            'call_id': call.get('call_id'),
            'status': call.get('call_status'),
            'phone_from': call.get('from_number'),
            'phone_to': call.get('to_number'),
            'started_at': call.get('start_timestamp'),
            'ended_at': call.get('end_timestamp'),
            'duration_seconds': None,
            'transcript': None,
            'recording_url': None,
            'cost': None
        }

        if event == 'call_ended':
            result['transcript'] = call.get('transcript', '')
            result['recording_url'] = call.get('recording_url')
            result['duration_seconds'] = call.get('duration_ms', 0) // 1000

            # Analyse
            result['sentiment'] = call.get('call_analysis', {}).get('user_sentiment')
            result['summary'] = call.get('call_analysis', {}).get('call_summary')

        return result


# =============================================================================
# BLAND.AI PROVIDER
# =============================================================================

class BlandProvider(VoiceAIProvider):
    """Bland.ai Integration."""

    BASE_URL = "https://api.bland.ai/v1"

    def _headers(self):
        return {
            "authorization": self.api_key,
            "Content-Type": "application/json"
        }

    def create_agent(self, name: str, system_prompt: str, voice_config: Dict) -> Dict:
        """Bland hat keine persistenten Agents - gibt Config zurück."""
        return {
            "name": name,
            "prompt": system_prompt,
            "voice": voice_config.get('tts_voice_id', 'matt'),
            "language": voice_config.get('language', 'de'),
            "model": voice_config.get('llm_model', 'enhanced')
        }

    def start_outbound_call(self, agent_id: str, phone_number: str,
                           customer_data: Dict) -> Dict:
        """Startet Outbound Call über Bland."""
        # agent_id ist hier die gespeicherte Config
        agent_config = json.loads(agent_id) if isinstance(agent_id, str) else agent_id

        payload = {
            "phone_number": phone_number,
            "task": agent_config.get('prompt', ''),
            "voice": agent_config.get('voice', 'matt'),
            "language": agent_config.get('language', 'de'),
            "model": agent_config.get('model', 'enhanced'),
            "first_sentence": f"Hallo {customer_data.get('name', '')}, hier ist...",
            "wait_for_greeting": True,
            "record": True,
            "from": self.config.get('from_number'),
            "webhook": self.config.get('webhook_url'),
            "metadata": {
                "customer_id": customer_data.get('id'),
                "customer_name": customer_data.get('name')
            }
        }

        response = requests.post(
            f"{self.BASE_URL}/calls",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_call_status(self, call_id: str) -> Dict:
        """Holt Call-Details von Bland."""
        response = requests.get(
            f"{self.BASE_URL}/calls/{call_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def parse_webhook(self, payload: Dict) -> Dict:
        """Parsed Bland Webhook."""
        result = {
            'provider': 'bland',
            'event_type': payload.get('status', 'unknown'),
            'call_id': payload.get('call_id'),
            'status': payload.get('status'),
            'phone_from': payload.get('from'),
            'phone_to': payload.get('to'),
            'started_at': payload.get('started_at'),
            'ended_at': payload.get('ended_at'),
            'duration_seconds': payload.get('call_length'),
            'transcript': None,
            'recording_url': None,
            'cost': payload.get('price')
        }

        if payload.get('status') == 'completed':
            # Hole volles Transkript
            result['transcript'] = payload.get('concatenated_transcript', '')
            result['recording_url'] = payload.get('recording_url')
            result['summary'] = payload.get('summary')
            result['sentiment'] = payload.get('analysis', {}).get('sentiment')

        return result


# =============================================================================
# PROVIDER FACTORY
# =============================================================================

def get_provider(provider_name: str, api_key: str, config: Dict = None) -> VoiceAIProvider:
    """Factory-Funktion um den richtigen Provider zu erstellen."""
    providers = {
        'vapi': VapiProvider,
        'retell': RetellProvider,
        'bland': BlandProvider
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    return provider_class(api_key, config)


# =============================================================================
# VOICE AI SERVICE
# =============================================================================

class VoiceAIService:
    """
    Hauptservice für Voice AI Integration.
    Verwaltet Agents, Calls und Webhooks.
    """

    def __init__(self, db_session):
        self.db = db_session

    def create_agent(self, agent_data: Dict) -> 'VoiceAgent':
        """Erstellt einen neuen Voice Agent."""
        from voice_ai_models import VoiceAgent

        # System Prompt basierend auf Sprache
        language = agent_data.get('primary_language', 'de')
        system_prompt = agent_data.get('system_prompt') or SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS['de'])

        # Agent in DB erstellen
        agent = VoiceAgent(
            name=agent_data['name'],
            provider=agent_data['provider'],
            api_key=agent_data.get('api_key'),
            primary_language=language,
            system_prompt=system_prompt,
            tts_provider=agent_data.get('tts_provider', 'elevenlabs'),
            tts_voice_id=agent_data.get('tts_voice_id'),
            tts_voice_name=agent_data.get('tts_voice_name'),
            stt_provider=agent_data.get('stt_provider', 'deepgram'),
            llm_provider=agent_data.get('llm_provider', 'openai'),
            llm_model=agent_data.get('llm_model', 'gpt-4o-mini'),
            phone_number=agent_data.get('phone_number'),
            telephony_provider=agent_data.get('telephony_provider', 'twilio')
        )

        if agent_data.get('supported_languages'):
            agent.set_supported_languages(agent_data['supported_languages'])

        self.db.add(agent)
        self.db.commit()

        # Bei Provider registrieren (wenn API-Key vorhanden)
        if agent.api_key:
            try:
                provider = get_provider(agent.provider, agent.api_key)
                voice_config = {
                    'llm_provider': agent.llm_provider,
                    'llm_model': agent.llm_model,
                    'tts_provider': agent.tts_provider,
                    'tts_voice_id': agent.tts_voice_id,
                    'stt_provider': agent.stt_provider,
                    'language': agent.primary_language,
                    'first_message': self._get_greeting(language)
                }
                result = provider.create_agent(agent.name, system_prompt, voice_config)
                agent.agent_id = result.get('id') or result.get('agent_id')
                self.db.commit()
            except Exception as e:
                print(f"Warning: Could not create agent at provider: {e}")

        return agent

    def _get_greeting(self, language: str) -> str:
        """Gibt Begrüßung in der richtigen Sprache zurück."""
        greetings = {
            'de': "Hallo, guten Tag! Wie kann ich Ihnen helfen?",
            'bs': "Zdravo, dobar dan! Kako vam mogu pomoći?",
            'sr': "Здраво, добар дан! Како вам могу помоћи?"
        }
        return greetings.get(language, greetings['de'])

    def start_call(self, agent_id: int, customer_id: int) -> 'CallSession':
        """Startet einen ausgehenden Anruf."""
        from voice_ai_models import VoiceAgent, CallSession
        from models import Customer

        agent = VoiceAgent.query.get(agent_id)
        customer = Customer.query.get(customer_id)

        if not agent or not customer:
            raise ValueError("Agent or Customer not found")

        if not customer.phone:
            raise ValueError("Customer has no phone number")

        # Call Session erstellen
        session = CallSession(
            agent_id=agent.id,
            customer_id=customer.id,
            direction='outbound',
            phone_from=agent.phone_number,
            phone_to=customer.phone,
            status='initiated',
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(session)
        self.db.commit()

        # Anruf beim Provider starten
        try:
            provider = get_provider(agent.provider, agent.api_key, {
                'phone_number_id': agent.phone_number,
                'from_number': agent.phone_number
            })

            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'company': customer.company,
                'notes': customer.notes
            }

            result = provider.start_outbound_call(
                agent.agent_id,
                customer.phone,
                customer_data
            )

            session.provider_call_id = result.get('id') or result.get('call_id')
            session.status = 'ringing'
            self.db.commit()

        except Exception as e:
            session.status = 'failed'
            self.db.commit()
            raise e

        return session

    def handle_webhook(self, provider_name: str, payload: Dict) -> 'CallSession':
        """Verarbeitet eingehende Webhooks."""
        from voice_ai_models import CallSession, LeadScore
        from models import Customer, Interaction

        provider = get_provider(provider_name, "")  # API key not needed for parsing
        data = provider.parse_webhook(payload)

        # Session finden
        session = CallSession.query.filter_by(
            provider_call_id=data['call_id']
        ).first()

        if not session:
            # Neuer Inbound Call?
            session = CallSession(
                provider_call_id=data['call_id'],
                direction='inbound',
                status=data['status']
            )
            self.db.add(session)

        # Update Session
        if data.get('status'):
            session.status = data['status']

        if data.get('ended_at'):
            session.ended_at = datetime.fromisoformat(
                data['ended_at'].replace('Z', '+00:00')
            ) if isinstance(data['ended_at'], str) else data['ended_at']

        if data.get('duration_seconds'):
            session.duration_seconds = data['duration_seconds']

        if data.get('transcript'):
            session.transcript = data['transcript']

        if data.get('summary'):
            session.summary = data['summary']

        if data.get('recording_url'):
            session.recording_url = data['recording_url']

        if data.get('cost'):
            session.cost_amount = float(data['cost'])

        if data.get('sentiment'):
            session.sentiment = data['sentiment']

        self.db.commit()

        # Bei Call-Ende: Interaction erstellen und Lead Score updaten
        if data.get('event_type') in ['end-of-call-report', 'call_ended', 'completed']:
            if session.customer_id:
                # Interaction loggen
                interaction = Interaction(
                    customer_id=session.customer_id,
                    type='call',
                    subject=f"AI Sales Call ({session.duration_seconds}s)",
                    description=session.summary or session.transcript[:500] if session.transcript else None
                )
                self.db.add(interaction)

                # Lead Score updaten
                self._update_lead_score(session)

            self.db.commit()

        return session

    def _update_lead_score(self, session: 'CallSession'):
        """Aktualisiert Lead Score basierend auf Call."""
        from voice_ai_models import LeadScore

        if not session.customer_id:
            return

        score = LeadScore.query.filter_by(customer_id=session.customer_id).first()
        if not score:
            score = LeadScore(customer_id=session.customer_id)
            self.db.add(score)

        # Einfache Scoring-Logik
        sentiment_scores = {'positive': 20, 'neutral': 0, 'negative': -20}
        delta = sentiment_scores.get(session.sentiment, 0)

        # Längere Calls = mehr Interesse
        if session.duration_seconds:
            if session.duration_seconds > 180:  # > 3 Minuten
                delta += 15
            elif session.duration_seconds > 60:  # > 1 Minute
                delta += 5

        score.overall_score = max(0, min(100, score.overall_score + delta))

        if session.sentiment == 'positive':
            score.interest_score = min(100, score.interest_score + 15)

        score.last_calculated = datetime.now(timezone.utc)

    def get_queue_next(self, agent_id: int = None) -> Optional['CallQueue']:
        """Holt den nächsten Anruf aus der Queue."""
        from voice_ai_models import CallQueue

        query = CallQueue.query.filter_by(status='pending')

        if agent_id:
            query = query.filter_by(agent_id=agent_id)

        return query.order_by(
            CallQueue.priority.asc(),
            CallQueue.created_at.asc()
        ).first()

    def add_to_queue(self, agent_id: int, customer_id: int, priority: int = 5,
                    scheduled_for: datetime = None) -> 'CallQueue':
        """Fügt Kunden zur Call-Queue hinzu."""
        from voice_ai_models import CallQueue

        queue_item = CallQueue(
            agent_id=agent_id,
            customer_id=customer_id,
            priority=priority,
            scheduled_for=scheduled_for,
            status='scheduled' if scheduled_for else 'pending'
        )
        self.db.add(queue_item)
        self.db.commit()
        return queue_item
