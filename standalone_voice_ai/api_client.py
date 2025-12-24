"""
Voice AI API Client
Für externe Anbindung an CRM-Systeme
"""

import json
import time
import hashlib
import hmac
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger('VoiceAI.API')


@dataclass
class APIResponse:
    """Standard API Response."""
    success: bool
    data: Dict = None
    error: str = ''
    status_code: int = 200


class VoiceAIAPIClient:
    """
    REST API Client für Voice AI System.

    Ermöglicht Anbindung an externes CRM oder andere Systeme.

    Beispiel:
        client = VoiceAIAPIClient(
            base_url='https://your-server.com/api/voice',
            api_key='your-api-key'
        )

        # Anruf starten
        result = client.start_call(
            agent_id=1,
            phone='+49123456789',
            name='Max Mustermann'
        )

        # Status abfragen
        status = client.get_call_status(result['call_id'])
    """

    def __init__(self, base_url: str, api_key: str = '',
                 webhook_secret: str = '', timeout: int = 30):
        """
        Initialisiert API Client.

        Args:
            base_url: Basis-URL der API (z.B. 'https://crm.example.com/api/voice')
            api_key: API-Key für Authentifizierung
            webhook_secret: Secret für Webhook-Signatur-Verifizierung
            timeout: Request-Timeout in Sekunden
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.timeout = timeout

        try:
            import requests
            self._requests = requests
        except ImportError:
            raise ImportError("requests library required: pip install requests")

    def _headers(self) -> Dict:
        """Erzeugt Request-Header."""
        return {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self, method: str, endpoint: str,
                data: Dict = None, params: Dict = None) -> APIResponse:
        """Führt API-Request aus."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self._requests.request(
                method=method,
                url=url,
                headers=self._headers(),
                json=data,
                params=params,
                timeout=self.timeout
            )

            if response.status_code >= 400:
                return APIResponse(
                    success=False,
                    error=response.json().get('error', 'Unknown error'),
                    status_code=response.status_code
                )

            return APIResponse(
                success=True,
                data=response.json(),
                status_code=response.status_code
            )

        except self._requests.exceptions.Timeout:
            return APIResponse(success=False, error='Request timeout', status_code=408)
        except self._requests.exceptions.ConnectionError:
            return APIResponse(success=False, error='Connection error', status_code=503)
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    # =========================================================================
    # AGENTS
    # =========================================================================

    def get_agents(self) -> APIResponse:
        """Holt alle verfügbaren Agents."""
        return self._request('GET', '/agents')

    def get_agent(self, agent_id: int) -> APIResponse:
        """Holt Agent-Details."""
        return self._request('GET', f'/agents/{agent_id}')

    def create_agent(self, name: str, provider: str = 'vapi',
                    language: str = 'de', **kwargs) -> APIResponse:
        """
        Erstellt neuen Agent.

        Args:
            name: Agent-Name
            provider: 'vapi', 'retell' oder 'bland'
            language: 'de', 'bs' oder 'sr'
            **kwargs: Weitere Optionen (tts_provider, llm_model, etc.)
        """
        data = {
            'name': name,
            'provider': provider,
            'primary_language': language,
            **kwargs
        }
        return self._request('POST', '/agents', data=data)

    # =========================================================================
    # CALLS
    # =========================================================================

    def start_call(self, agent_id: int, phone: str = None,
                  customer_id: int = None, name: str = '',
                  **kwargs) -> APIResponse:
        """
        Startet einen Anruf.

        Args:
            agent_id: ID des Agents
            phone: Telefonnummer (wenn kein customer_id)
            customer_id: CRM Customer-ID (wenn vorhanden)
            name: Kundenname
            **kwargs: Weitere Optionen
        """
        data = {
            'agent_id': agent_id,
            'phone': phone,
            'customer_id': customer_id,
            'name': name,
            **kwargs
        }
        return self._request('POST', '/calls/start', data=data)

    def get_call_status(self, call_id: int) -> APIResponse:
        """Holt Anruf-Status."""
        return self._request('GET', f'/calls/{call_id}')

    def get_calls(self, limit: int = 50, status: str = None,
                 agent_id: int = None) -> APIResponse:
        """Holt Anruf-Liste."""
        params = {'limit': limit}
        if status:
            params['status'] = status
        if agent_id:
            params['agent_id'] = agent_id

        return self._request('GET', '/calls', params=params)

    # =========================================================================
    # QUEUE
    # =========================================================================

    def add_to_queue(self, agent_id: int, customer_id: int,
                    priority: int = 5, scheduled_for: str = None) -> APIResponse:
        """
        Fügt Kunden zur Anruf-Queue hinzu.

        Args:
            agent_id: ID des Agents
            customer_id: CRM Customer-ID
            priority: 1-10 (1 = höchste Priorität)
            scheduled_for: ISO-Timestamp für geplanten Anruf
        """
        data = {
            'agent_id': agent_id,
            'customer_id': customer_id,
            'priority': priority,
            'scheduled_for': scheduled_for
        }
        return self._request('POST', '/queue', data=data)

    def get_queue(self, agent_id: int = None) -> APIResponse:
        """Holt Queue-Einträge."""
        params = {}
        if agent_id:
            params['agent_id'] = agent_id
        return self._request('GET', '/queue', params=params)

    # =========================================================================
    # CUSTOMERS (CRM Integration)
    # =========================================================================

    def get_customers(self, status: str = None, search: str = None) -> APIResponse:
        """Holt Kunden aus CRM."""
        params = {}
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        return self._request('GET', '/customers', params=params)

    def get_customer(self, customer_id: int) -> APIResponse:
        """Holt Kunden-Details."""
        return self._request('GET', f'/customers/{customer_id}')

    def get_lead_score(self, customer_id: int) -> APIResponse:
        """Holt Lead-Score für Kunden."""
        return self._request('GET', f'/customers/{customer_id}/lead-score')

    # =========================================================================
    # WEBHOOK HANDLING
    # =========================================================================

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verifiziert Webhook-Signatur.

        Args:
            payload: Request-Body als Bytes
            signature: X-Signature Header-Wert

        Returns:
            True wenn Signatur gültig
        """
        if not self.webhook_secret:
            return True  # Keine Verifizierung konfiguriert

        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def parse_webhook(self, payload: Dict, provider: str = 'vapi') -> Dict:
        """
        Parsed Webhook-Payload zu einheitlichem Format.

        Args:
            payload: Webhook JSON-Daten
            provider: 'vapi', 'retell' oder 'bland'

        Returns:
            Normalisierte Webhook-Daten
        """
        if provider == 'vapi':
            return self._parse_vapi_webhook(payload)
        elif provider == 'retell':
            return self._parse_retell_webhook(payload)
        elif provider == 'bland':
            return self._parse_bland_webhook(payload)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _parse_vapi_webhook(self, payload: Dict) -> Dict:
        """Parsed Vapi Webhook."""
        message = payload.get('message', {})
        call = message.get('call', {})

        return {
            'event_type': message.get('type', ''),
            'call_id': call.get('id'),
            'status': call.get('status'),
            'phone': call.get('customer', {}).get('number'),
            'duration': None,
            'transcript': message.get('transcript', ''),
            'summary': message.get('summary', ''),
            'recording_url': message.get('recordingUrl'),
            'cost': message.get('cost'),
            'timestamp': datetime.now().isoformat()
        }

    def _parse_retell_webhook(self, payload: Dict) -> Dict:
        """Parsed Retell Webhook."""
        call = payload.get('call', {})
        analysis = call.get('call_analysis', {})

        return {
            'event_type': payload.get('event', ''),
            'call_id': call.get('call_id'),
            'status': call.get('call_status'),
            'phone': call.get('to_number'),
            'duration': call.get('duration_ms', 0) // 1000,
            'transcript': call.get('transcript', ''),
            'summary': analysis.get('call_summary', ''),
            'sentiment': analysis.get('user_sentiment'),
            'recording_url': call.get('recording_url'),
            'timestamp': datetime.now().isoformat()
        }

    def _parse_bland_webhook(self, payload: Dict) -> Dict:
        """Parsed Bland Webhook."""
        return {
            'event_type': payload.get('status', ''),
            'call_id': payload.get('call_id'),
            'status': payload.get('status'),
            'phone': payload.get('to'),
            'duration': payload.get('call_length'),
            'transcript': payload.get('concatenated_transcript', ''),
            'summary': payload.get('summary', ''),
            'recording_url': payload.get('recording_url'),
            'cost': payload.get('price'),
            'timestamp': datetime.now().isoformat()
        }


# =============================================================================
# WEBHOOK SERVER (für eigenständigen Betrieb)
# =============================================================================

def create_webhook_server(host: str = '0.0.0.0', port: int = 8080,
                         callback: callable = None):
    """
    Erstellt einfachen Webhook-Server.

    Args:
        host: Server-Host
        port: Server-Port
        callback: Funktion die bei Webhook aufgerufen wird

    Beispiel:
        def on_webhook(data):
            print(f"Anruf beendet: {data['call_id']}")

        server = create_webhook_server(callback=on_webhook)
        server.run()
    """
    from flask import Flask, request, jsonify

    app = Flask('VoiceAI-Webhook')
    client = VoiceAIAPIClient('')

    @app.route('/webhook/<provider>', methods=['POST'])
    def handle_webhook(provider):
        payload = request.get_json()

        try:
            data = client.parse_webhook(payload, provider)

            if callback:
                callback(data)

            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'}), 200

    return app


# =============================================================================
# CONVENIENCE CLASS für schnelle Integration
# =============================================================================

class QuickConnect:
    """
    Schnelle Integration für bestehende Systeme.

    Beispiel:
        from standalone_voice_ai import QuickConnect

        # Mit CRM verbinden
        qc = QuickConnect(
            crm_api_url='https://your-crm.com/api',
            crm_api_key='your-key',
            voice_provider='vapi',
            voice_api_key='vapi-key'
        )

        # Leads abrufen und anrufen
        leads = qc.get_leads(status='new')
        for lead in leads:
            result = qc.call_lead(lead['id'])
            print(f"Called {lead['name']}: {result['status']}")
    """

    def __init__(self, crm_api_url: str, crm_api_key: str,
                 voice_provider: str, voice_api_key: str,
                 agent_id: int = None):
        """
        Initialisiert QuickConnect.

        Args:
            crm_api_url: URL der CRM API
            crm_api_key: CRM API Key
            voice_provider: 'vapi', 'retell' oder 'bland'
            voice_api_key: Voice Provider API Key
            agent_id: Standard-Agent ID
        """
        self.crm_client = VoiceAIAPIClient(crm_api_url, crm_api_key)
        self.voice_provider = voice_provider
        self.voice_api_key = voice_api_key
        self.agent_id = agent_id

        # Import Voice Agent
        from .agent import VoiceAISalesAgent
        self.agent = VoiceAISalesAgent(
            provider=voice_provider,
            api_key=voice_api_key
        )

    def get_leads(self, status: str = 'lead', limit: int = 50) -> List[Dict]:
        """Holt Leads aus CRM."""
        response = self.crm_client.get_customers(status=status)
        if response.success:
            return response.data[:limit] if isinstance(response.data, list) else []
        return []

    def call_lead(self, customer_id: int = None, phone: str = None,
                 name: str = '', wait: bool = True) -> Dict:
        """Ruft Lead an."""
        if customer_id:
            # Lade Kundendaten aus CRM
            response = self.crm_client.get_customer(customer_id)
            if response.success:
                customer = response.data
                phone = customer.get('phone')
                name = customer.get('name', '')

        if not phone:
            return {'error': 'No phone number'}

        result = self.agent.call(phone=phone, name=name,
                                wait_for_completion=wait)
        return result.to_dict()

    def call_all_leads(self, status: str = 'lead', max_calls: int = 10,
                      delay: int = 30) -> List[Dict]:
        """Ruft alle Leads an."""
        leads = self.get_leads(status=status, limit=max_calls)
        results = []

        for lead in leads:
            result = self.call_lead(
                phone=lead.get('phone'),
                name=lead.get('name', '')
            )
            results.append(result)

            if lead != leads[-1]:
                time.sleep(delay)

        return results
