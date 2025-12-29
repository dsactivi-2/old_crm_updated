"""
AI Assistant powered by Claude API
Handles intelligent responses and automation decisions
"""

import os
from typing import Dict, List, Optional
import anthropic
from datetime import datetime


class AIAssistant:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI Assistant with Claude API"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.conversation_history = []

    def process_query(self, query: str, context: Optional[Dict] = None) -> str:
        """Process a user query and return AI response"""

        # Build context message
        system_message = """Du bist ein intelligenter Mac-Assistent. Du hilfst dem Nutzer:
- E-Mails und Nachrichten zu verwalten und zu beantworten
- Fotos zu durchsuchen und zu organisieren
- Aktivitäten zu verfolgen und zu finden
- Automatisierungen durchzuführen

Du hast Zugriff auf:
- Mail.app (E-Mails lesen, senden, beantworten)
- Messages/WhatsApp (Nachrichten senden und lesen)
- Photos.app (Fotos suchen, anzeigen, löschen)
- Aktivitätsverlauf (was der Nutzer wann gemacht hat)

Antworte präzise, freundlich und auf Deutsch."""

        if context:
            context_str = "\n\nAktueller Kontext:\n"
            for key, value in context.items():
                context_str += f"{key}: {value}\n"
            system_message += context_str

        # Add message to history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                system=system_message,
                messages=self.conversation_history[-10:]  # Keep last 10 messages for context
            )

            assistant_message = response.content[0].text

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"Fehler bei der KI-Verarbeitung: {str(e)}"

    def compose_email_reply(self, original_email: Dict, context: str = "") -> str:
        """Generate an email reply based on original email and context"""

        prompt = f"""Schreibe eine professionelle E-Mail-Antwort auf folgende E-Mail:

Von: {original_email.get('sender', 'Unbekannt')}
Betreff: {original_email.get('subject', 'Kein Betreff')}
Inhalt: {original_email.get('body', '')}

{f'Zusätzlicher Kontext: {context}' if context else ''}

Schreibe eine angemessene, freundliche Antwort."""

        return self.process_query(prompt)

    def compose_message_reply(self, original_message: str, contact: str, context: str = "") -> str:
        """Generate a message reply"""

        prompt = f"""Schreibe eine passende Antwort auf folgende Nachricht:

Von: {contact}
Nachricht: {original_message}

{f'Kontext: {context}' if context else ''}

Schreibe eine freundliche, kurze Antwort."""

        return self.process_query(prompt)

    def analyze_photos_for_deletion(self, photo_list: List[str]) -> Dict:
        """Analyze photos and suggest which ones to delete"""

        prompt = f"""Analysiere folgende Fotoliste und schlage vor, welche eventuell gelöscht werden könnten (z.B. Duplikate, Screenshots, temporäre Bilder):

{chr(10).join(photo_list)}

Gib eine strukturierte Empfehlung zurück."""

        response = self.process_query(prompt)

        return {
            "analysis": response,
            "timestamp": datetime.now().isoformat()
        }

    def search_activities_natural_language(self, query: str, activities: List) -> str:
        """Search through activities using natural language"""

        activities_str = "\n".join([str(a) for a in activities])

        prompt = f"""Der Nutzer fragt: "{query}"

Hier sind die relevanten Aktivitäten:
{activities_str}

Beantworte die Frage des Nutzers basierend auf diesen Aktivitäten."""

        return self.process_query(prompt)

    def get_task_suggestions(self, current_context: Dict) -> str:
        """Get AI suggestions for tasks based on current context"""

        prompt = f"""Basierend auf folgendem Kontext, was sollte der Nutzer als nächstes tun?

Aktueller Kontext:
{chr(10).join([f'{k}: {v}' for k, v in current_context.items()])}

Gib 3-5 konkrete Vorschläge."""

        return self.process_query(prompt)

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


class AutomationEngine:
    """Engine to execute automated tasks based on AI decisions"""

    def __init__(self, ai_assistant: AIAssistant):
        self.ai = ai_assistant

    def should_auto_reply(self, message: Dict) -> bool:
        """Determine if a message should be auto-replied"""

        prompt = f"""Sollte auf folgende Nachricht automatisch geantwortet werden?

Absender: {message.get('sender', 'Unbekannt')}
Inhalt: {message.get('content', '')}

Antworte nur mit 'JA' oder 'NEIN' und einer kurzen Begründung."""

        response = self.ai.process_query(prompt)
        return response.upper().startswith('JA')

    def categorize_email(self, email: Dict) -> str:
        """Categorize an email into: important, spam, newsletter, personal, work"""

        prompt = f"""Kategorisiere folgende E-Mail in eine dieser Kategorien:
- wichtig (important)
- spam
- newsletter
- persönlich (personal)
- arbeit (work)

E-Mail:
Von: {email.get('sender', '')}
Betreff: {email.get('subject', '')}
Inhalt (Auszug): {email.get('body', '')[:200]}

Antworte nur mit der Kategorie."""

        return self.ai.process_query(prompt).strip().lower()
