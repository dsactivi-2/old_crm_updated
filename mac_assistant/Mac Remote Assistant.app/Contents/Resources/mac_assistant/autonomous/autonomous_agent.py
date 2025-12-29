"""
Autonomous Agent
Runs in background, makes proactive suggestions, executes automatic tasks
"""

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable


class AutonomousAgent:
    """Autonomous agent that proactively helps the user"""

    def __init__(self, core, analytics_engine, notification_callback=None):
        self.core = core
        self.analytics = analytics_engine
        self.notification_callback = notification_callback

        self.running = False
        self.thread = None

        # Rules for autonomous behavior
        self.rules = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default autonomous rules"""

        # Rule 1: Check for unread emails every 15 minutes
        self.add_rule(
            name="email_check",
            interval_minutes=15,
            action=self._check_unread_emails,
            enabled=True
        )

        # Rule 2: Analyze daily patterns every hour
        self.add_rule(
            name="pattern_analysis",
            interval_minutes=60,
            action=self._analyze_patterns,
            enabled=True
        )

        # Rule 3: Photo cleanup suggestions daily
        self.add_rule(
            name="photo_cleanup",
            interval_minutes=1440,  # Once per day
            action=self._suggest_photo_cleanup,
            enabled=True
        )

        # Rule 4: Activity summary at end of day
        self.add_rule(
            name="daily_summary",
            interval_minutes=1440,
            action=self._create_daily_summary,
            enabled=True,
            specific_time="18:00"  # 6 PM
        )

    def add_rule(self, name: str, interval_minutes: int, action: Callable,
                  enabled: bool = True, specific_time: str = None):
        """Add an autonomous rule"""
        rule = {
            'name': name,
            'interval_minutes': interval_minutes,
            'action': action,
            'enabled': enabled,
            'specific_time': specific_time,
            'last_run': None
        }
        self.rules.append(rule)

    def start(self):
        """Start the autonomous agent"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("🤖 Autonomous Agent started")

    def stop(self):
        """Stop the autonomous agent"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🤖 Autonomous Agent stopped")

    def _run_loop(self):
        """Main loop for autonomous agent"""
        while self.running:
            try:
                self._check_and_execute_rules()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in autonomous agent loop: {e}")

    def _check_and_execute_rules(self):
        """Check all rules and execute if needed"""
        now = datetime.now()

        for rule in self.rules:
            if not rule['enabled']:
                continue

            should_run = False

            # Check if specific time is set
            if rule['specific_time']:
                target_time = datetime.strptime(rule['specific_time'], "%H:%M").time()
                if now.time().hour == target_time.hour and now.time().minute == target_time.minute:
                    if rule['last_run'] is None or rule['last_run'].date() < now.date():
                        should_run = True
            else:
                # Check interval
                if rule['last_run'] is None:
                    should_run = True
                else:
                    elapsed = (now - rule['last_run']).total_seconds() / 60
                    if elapsed >= rule['interval_minutes']:
                        should_run = True

            if should_run:
                try:
                    print(f"🤖 Executing rule: {rule['name']}")
                    rule['action']()
                    rule['last_run'] = now
                except Exception as e:
                    print(f"Error executing rule {rule['name']}: {e}")

    # ===== Autonomous Actions =====

    def _check_unread_emails(self):
        """Check for unread emails and notify"""
        try:
            mail_plugin = self.core.get_plugin('Mail')
            if not mail_plugin or not mail_plugin.is_available():
                return

            # Get unread count
            emails = mail_plugin.get_unread_emails(5)

            if emails:
                # Analyze with AI if available
                if self.core.ai_enabled:
                    important = self._categorize_emails(emails)
                    if important:
                        self._notify(
                            f"📧 Du hast {len(important)} wichtige ungelesene E-Mails!",
                            action="show_emails"
                        )
                else:
                    self._notify(
                        f"📧 {len(emails)} neue E-Mails",
                        action="show_emails"
                    )
        except Exception as e:
            print(f"Error checking emails: {e}")

    def _analyze_patterns(self):
        """Analyze user patterns and make suggestions"""
        try:
            insights = self.analytics.get_insights()

            if insights.get('unusual_activity'):
                self._notify(
                    "🔍 Ungewöhnliche Aktivität erkannt",
                    details=insights['unusual_activity']
                )

            if insights.get('suggestions'):
                for suggestion in insights['suggestions'][:1]:  # Top suggestion
                    self._notify(
                        f"💡 Vorschlag: {suggestion}",
                        action="view_insights"
                    )
        except Exception as e:
            print(f"Error analyzing patterns: {e}")

    def _suggest_photo_cleanup(self):
        """Suggest photo cleanup"""
        try:
            photos_plugin = self.core.get_plugin('Photos')
            if not photos_plugin or not photos_plugin.is_available():
                return

            # Check for old/duplicate photos
            analysis = self.analytics.analyze_photos()

            if analysis.get('duplicates'):
                self._notify(
                    f"📸 {len(analysis['duplicates'])} mögliche Duplikate gefunden",
                    action="show_photo_cleanup"
                )

            if analysis.get('old_photos'):
                self._notify(
                    f"📸 {len(analysis['old_photos'])} alte Fotos zum Aufräumen",
                    action="show_photo_cleanup"
                )
        except Exception as e:
            print(f"Error suggesting photo cleanup: {e}")

    def _create_daily_summary(self):
        """Create end-of-day summary"""
        try:
            summary = self.analytics.get_daily_summary()

            summary_text = f"""
📊 Deine Tages-Zusammenfassung:

📧 E-Mails: {summary.get('emails_sent', 0)} gesendet, {summary.get('emails_received', 0)} empfangen
💬 Nachrichten: {summary.get('messages_sent', 0)} gesendet
📸 Fotos: {summary.get('photos_taken', 0)} neu
🎯 Tasks: {summary.get('tasks_completed', 0)} erledigt

🏆 Produktivste Zeit: {summary.get('most_productive_time', 'N/A')}
"""

            self._notify(
                "📊 Deine Tages-Zusammenfassung ist fertig",
                details=summary_text
            )
        except Exception as e:
            print(f"Error creating daily summary: {e}")

    def _categorize_emails(self, emails):
        """Categorize emails by importance"""
        if not self.core.ai_enabled:
            return emails

        important = []
        for email in emails:
            # Use AI to determine importance
            category = self.core.automation.categorize_email(email)
            if category in ['important', 'work']:
                important.append(email)

        return important

    def _notify(self, message: str, action: str = None, details: str = None):
        """Send notification to user"""
        notification = {
            'timestamp': datetime.now(),
            'message': message,
            'action': action,
            'details': details
        }

        print(f"🔔 Notification: {message}")

        if self.notification_callback:
            self.notification_callback(notification)

    # ===== Proactive Intelligence =====

    def suggest_next_action(self) -> str:
        """Proactively suggest what to do next"""
        insights = self.analytics.get_insights()

        suggestions = []

        # Check pending items
        if insights.get('unread_emails', 0) > 0:
            suggestions.append(f"Du hast {insights['unread_emails']} ungelesene E-Mails")

        if insights.get('unanswered_messages', 0) > 0:
            suggestions.append(f"{insights['unanswered_messages']} unbeantwortete Nachrichten")

        # Pattern-based suggestions
        current_hour = datetime.now().hour

        if 9 <= current_hour <= 11:
            suggestions.append("Guter Zeitpunkt um E-Mails zu beantworten")
        elif 14 <= current_hour <= 16:
            suggestions.append("Vielleicht Zeit für kreative Arbeit?")

        return "\n".join(suggestions) if suggestions else "Alles erledigt! 🎉"

    def auto_organize(self):
        """Automatically organize data"""
        print("🤖 Auto-organizing data...")

        # Organize photos by date
        # Categorize emails
        # Archive old messages
        # etc.

        return {
            'photos_organized': 0,
            'emails_categorized': 0,
            'messages_archived': 0
        }

    def learn_from_behavior(self):
        """Learn from user behavior patterns"""
        patterns = self.analytics.detect_patterns()

        # Update rules based on patterns
        if patterns.get('preferred_email_time'):
            # Adjust email check time
            pass

        if patterns.get('frequent_contacts'):
            # Prioritize these contacts
            pass

        return patterns
