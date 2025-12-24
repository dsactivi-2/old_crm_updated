"""
Core Application Logic
Connects all components together
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from database.activity_tracker import ActivityTracker
from scripts.applescript_bridge import AppleScriptBridge
from utils.ai_assistant import AIAssistant, AutomationEngine


class MacAssistantCore:
    """Core logic for Mac Assistant"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the assistant core"""
        self.tracker = ActivityTracker()
        self.bridge = AppleScriptBridge()

        # Initialize AI (will raise error if no API key)
        try:
            self.ai = AIAssistant(api_key)
            self.automation = AutomationEngine(self.ai)
            self.ai_enabled = True
        except ValueError:
            print("Warning: ANTHROPIC_API_KEY not set. AI features disabled.")
            self.ai = None
            self.automation = None
            self.ai_enabled = False

        # Start activity monitoring
        self.monitoring_active = False

    def process_user_query(self, query: str) -> str:
        """Process a user query and return response"""

        # Parse query for special commands
        query_lower = query.lower()

        # Time-based queries
        if "vor" in query_lower and ("tagen" in query_lower or "tag" in query_lower):
            return self._handle_time_query(query)

        # Email queries
        if any(word in query_lower for word in ["email", "e-mail", "mail"]):
            return self._handle_email_query(query)

        # Photo queries
        if any(word in query_lower for word in ["foto", "fotos", "bild", "bilder"]):
            return self._handle_photo_query(query)

        # Message queries
        if any(word in query_lower for word in ["nachricht", "nachrichten", "whatsapp", "message"]):
            return self._handle_message_query(query)

        # General activity search
        if any(word in query_lower for word in ["was habe ich", "was hab ich", "was machte ich"]):
            return self._handle_activity_search(query)

        # If AI is enabled, use it for general queries
        if self.ai_enabled:
            context = self._gather_context()
            return self.ai.process_query(query, context)
        else:
            return "Bitte stelle eine spezifischere Frage (z.B. über E-Mails, Fotos, oder Aktivitäten)"

    def _handle_time_query(self, query: str) -> str:
        """Handle time-based queries like 'was habe ich vor 3 tagen um 2 uhr gemacht'"""

        # Extract days
        days_match = re.search(r'vor (\d+) tag', query.lower())
        days_ago = int(days_match.group(1)) if days_match else 0

        # Extract hour
        hour_match = re.search(r'um (\d+)\s*uhr', query.lower())
        hour = int(hour_match.group(1)) if hour_match else None

        # Get activities
        activities = self.tracker.get_activities_at_time(days_ago=days_ago, hour=hour)

        if not activities:
            time_desc = f"vor {days_ago} Tagen" if days_ago > 0 else "heute"
            if hour is not None:
                time_desc += f" um {hour} Uhr"
            return f"Ich habe keine Aktivitäten {time_desc} gefunden."

        # Format response
        if self.ai_enabled:
            return self.ai.search_activities_natural_language(query, activities)
        else:
            response = f"Aktivitäten gefunden ({len(activities)}):\n\n"
            for activity in activities[:10]:  # Limit to 10
                response += f"- {activity[1]} | {activity[2]} | {activity[3]}: {activity[4]}\n"
            return response

    def _handle_email_query(self, query: str) -> str:
        """Handle email-related queries"""

        query_lower = query.lower()

        if "neu" in query_lower or "ungelesen" in query_lower:
            # Get unread emails
            emails = self.bridge.get_unread_emails(limit=10)
            self.tracker.log_activity('Mail', 'check_unread', 'Checked unread emails')
            return f"Ungelesene E-Mails:\n{emails}"

        elif "letzte" in query_lower or "recent" in query_lower:
            # Get recent emails
            hours = 24
            hour_match = re.search(r'(\d+)\s*stunden', query_lower)
            if hour_match:
                hours = int(hour_match.group(1))

            emails = self.bridge.get_recent_emails(hours=hours)
            self.tracker.log_activity('Mail', 'check_recent', f'Checked emails from last {hours}h')
            return f"E-Mails der letzten {hours} Stunden:\n{emails}"

        elif "antworte" in query_lower or "beantworte" in query_lower:
            if not self.ai_enabled:
                return "KI-Funktionen sind nicht verfügbar (API Key fehlt)"

            # Extract reply context
            reply_text = self.ai.compose_email_reply({'sender': 'Latest', 'subject': '', 'body': ''})
            return f"Vorgeschlagene Antwort:\n\n{reply_text}\n\nMöchtest du diese senden?"

        return "Was möchtest du mit E-Mails tun? (z.B. 'zeige neue E-Mails')"

    def _handle_photo_query(self, query: str) -> str:
        """Handle photo-related queries"""

        query_lower = query.lower()

        if "suche" in query_lower or "finde" in query_lower:
            # Extract search term
            search_term = query_lower.replace("suche", "").replace("finde", "").replace("foto", "").replace("fotos", "").strip()
            if search_term:
                results = self.bridge.search_photos(search_term, limit=20)
                self.tracker.log_photo('search', tags=[search_term])
                return f"Suchergebnisse für '{search_term}':\n{results}"

        elif "letzte" in query_lower or "diese woche" in query_lower:
            days = 7
            if "monat" in query_lower:
                days = 30
            elif "heute" in query_lower:
                days = 1

            photos = self.bridge.get_recent_photos(days=days)
            self.tracker.log_photo('browse_recent', tags=[f'last_{days}_days'])
            return f"Fotos der letzten {days} Tage:\n{photos}"

        elif "lösche" in query_lower or "löschen" in query_lower:
            return "Welche Fotos möchtest du löschen? Bitte gib die Namen an."

        return "Was möchtest du mit Fotos tun? (z.B. 'zeige Fotos dieser Woche')"

    def _handle_message_query(self, query: str) -> str:
        """Handle message-related queries"""

        query_lower = query.lower()

        if "neu" in query_lower or "letzte" in query_lower:
            messages = self.bridge.get_recent_messages(limit=10)
            self.tracker.log_whatsapp('check_messages', chat_name='Recent')
            return f"Letzte Nachrichten:\n{messages}"

        elif "sende" in query_lower or "schreibe" in query_lower:
            return "An wen möchtest du eine Nachricht senden?"

        return "Was möchtest du mit Nachrichten tun?"

    def _handle_activity_search(self, query: str) -> str:
        """Handle general activity searches"""

        # Default to today
        days_match = re.search(r'vor (\d+) tag', query.lower())
        days_ago = int(days_match.group(1)) if days_match else 0

        if "heute" in query.lower():
            days_ago = 0
        elif "gestern" in query.lower():
            days_ago = 1

        activities = self.tracker.get_activities_at_time(days_ago=days_ago)

        if not activities:
            return f"Keine Aktivitäten gefunden."

        if self.ai_enabled:
            return self.ai.search_activities_natural_language(query, activities)
        else:
            response = f"Deine Aktivitäten:\n\n"
            for activity in activities[:20]:
                response += f"• {activity[1]} | {activity[2]}: {activity[4]}\n"
            return response

    def _gather_context(self) -> Dict:
        """Gather current context for AI"""
        context = {
            'current_time': datetime.now().isoformat(),
            'active_app': self.bridge.get_active_app(),
        }

        try:
            context['active_window'] = self.bridge.get_active_window_title()
        except:
            pass

        return context

    # ===== Direct Actions =====

    def get_unread_emails(self, limit: int = 10) -> List[Dict]:
        """Get unread emails"""
        result = self.bridge.get_unread_emails(limit)
        self.tracker.log_mail('check_unread', subject=f'Checked {limit} unread')
        return result

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email"""
        success = self.bridge.send_email(to, subject, body)
        if success:
            self.tracker.log_mail('sent', recipient=to, subject=subject, body=body)
        return success

    def reply_to_email_with_ai(self, email_data: Dict, context: str = "") -> str:
        """Generate and optionally send AI reply to email"""
        if not self.ai_enabled:
            return "KI nicht verfügbar"

        reply = self.ai.compose_email_reply(email_data, context)
        return reply

    def search_photos(self, query: str, limit: int = 20) -> str:
        """Search for photos"""
        results = self.bridge.search_photos(query, limit)
        self.tracker.log_photo('search', tags=[query])
        return results

    def get_recent_photos(self, days: int = 7) -> str:
        """Get recent photos"""
        photos = self.bridge.get_recent_photos(days)
        self.tracker.log_photo('browse_recent', tags=[f'last_{days}_days'])
        return photos

    def delete_photos(self, photo_names: List[str]) -> bool:
        """Delete photos by name"""
        success = self.bridge.delete_photos_by_name(photo_names)
        if success:
            for name in photo_names:
                self.tracker.log_photo('delete', file_name=name)
        return success

    def send_message(self, contact: str, message: str) -> bool:
        """Send a message"""
        success = self.bridge.send_message(contact, message)
        if success:
            self.tracker.log_whatsapp('sent', contact=contact, message=message)
        return success

    def get_activities_at_time(self, days_ago: int = 0, hour: Optional[int] = None) -> List:
        """Get activities from a specific time"""
        return self.tracker.get_activities_at_time(days_ago, hour)

    def search_activities(self, query: str, days_back: int = 30) -> List:
        """Search through activities"""
        return self.tracker.search_activities(query, days_back=days_back)

    # ===== Monitoring =====

    def start_monitoring(self):
        """Start monitoring user activities"""
        self.monitoring_active = True
        print("Activity monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        print("Activity monitoring stopped")

    def log_current_activity(self):
        """Log current activity"""
        if not self.monitoring_active:
            return

        try:
            app = self.bridge.get_active_app()
            window = self.bridge.get_active_window_title()

            self.tracker.log_activity(
                app_name=app,
                activity_type='app_usage',
                title=window,
                metadata={'timestamp': datetime.now().isoformat()}
            )
        except Exception as e:
            print(f"Error logging activity: {e}")
