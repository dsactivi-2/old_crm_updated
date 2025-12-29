"""
Analytics Engine
Analyzes all data and provides intelligent insights
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json


class AnalyticsEngine:
    """Intelligent analytics and insights engine"""

    def __init__(self, core):
        self.core = core
        self.tracker = core.tracker

    def get_insights(self) -> Dict:
        """Get current insights about user behavior"""
        insights = {}

        # Email insights
        insights['unread_emails'] = self._count_unread_emails()
        insights['email_trends'] = self._analyze_email_trends()

        # Activity insights
        insights['top_apps'] = self._get_top_apps()
        insights['productivity_score'] = self._calculate_productivity()

        # Pattern insights
        insights['unusual_activity'] = self._detect_unusual_activity()
        insights['suggestions'] = self._generate_suggestions()

        return insights

    def get_daily_summary(self) -> Dict:
        """Get summary of today's activities"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        summary = {
            'date': today.isoformat(),
            'emails_sent': 0,
            'emails_received': 0,
            'messages_sent': 0,
            'photos_taken': 0,
            'tasks_completed': 0,
            'most_productive_time': None,
            'top_contacts': []
        }

        # Get today's activities
        activities = self.tracker.get_activities_at_time(days_ago=0)

        # Analyze activities
        for activity in activities:
            # Count by type
            if 'mail' in str(activity).lower():
                if 'sent' in str(activity).lower():
                    summary['emails_sent'] += 1
                else:
                    summary['emails_received'] += 1

            if 'message' in str(activity).lower() or 'slack' in str(activity).lower():
                summary['messages_sent'] += 1

            if 'photo' in str(activity).lower():
                summary['photos_taken'] += 1

            if 'task' in str(activity).lower() and 'completed' in str(activity).lower():
                summary['tasks_completed'] += 1

        # Find most productive time
        summary['most_productive_time'] = self._find_productive_hours(activities)

        return summary

    def analyze_photos(self) -> Dict:
        """Analyze photos for cleanup suggestions"""
        analysis = {
            'total': 0,
            'duplicates': [],
            'old_photos': [],
            'large_files': [],
            'suggestions': []
        }

        # This would analyze actual photos
        # For now, return structure
        analysis['suggestions'].append("Regelmäßig Duplikate entfernen")
        analysis['suggestions'].append("Alte Screenshots aufräumen")

        return analysis

    def detect_patterns(self) -> Dict:
        """Detect user behavior patterns"""
        patterns = {}

        # Analyze last 30 days
        activities = self.tracker.search_activities("", days_back=30)

        # Find patterns
        patterns['preferred_email_time'] = self._find_preferred_time(activities, 'mail')
        patterns['frequent_contacts'] = self._find_frequent_contacts(activities)
        patterns['app_usage_patterns'] = self._analyze_app_usage(activities)
        patterns['work_hours'] = self._detect_work_hours(activities)

        return patterns

    def _count_unread_emails(self) -> int:
        """Count unread emails"""
        try:
            mail_plugin = self.core.get_plugin('Mail')
            if mail_plugin and mail_plugin.is_available():
                emails = mail_plugin.get_unread_emails(100)
                # Parse count from result
                return len(str(emails).split('\n'))
        except:
            pass
        return 0

    def _analyze_email_trends(self) -> Dict:
        """Analyze email trends"""
        trends = {
            'increasing': False,
            'average_per_day': 0,
            'busiest_day': None
        }

        # Would analyze actual email data
        return trends

    def _get_top_apps(self, limit: int = 5) -> List[str]:
        """Get most used apps"""
        activities = self.tracker.search_activities("", days_back=7)

        app_counts = {}
        for activity in activities:
            app_name = activity[2] if len(activity) > 2 else 'Unknown'
            app_counts[app_name] = app_counts.get(app_name, 0) + 1

        # Sort by count
        sorted_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)
        return [app for app, count in sorted_apps[:limit]]

    def _calculate_productivity(self) -> int:
        """Calculate productivity score (0-100)"""
        score = 50  # Base score

        # Factors that increase score
        activities_today = len(self.tracker.get_activities_at_time(days_ago=0))
        score += min(activities_today, 30)  # Max +30

        # Tasks completed
        tasks = self.core.get_task_history(limit=10)
        completed = len([t for t in tasks if t.get('status') == 'completed'])
        score += completed * 2  # +2 per task

        return min(score, 100)

    def _detect_unusual_activity(self) -> str:
        """Detect unusual activity patterns"""
        current_hour = datetime.now().hour

        # Check if working at unusual time
        if current_hour < 6 or current_hour > 22:
            return "Du arbeitest zu ungewöhnlicher Zeit"

        # Check activity spike
        today_count = len(self.tracker.get_activities_at_time(days_ago=0))
        yesterday_count = len(self.tracker.get_activities_at_time(days_ago=1))

        if today_count > yesterday_count * 2:
            return "Deutlich mehr Aktivität als gestern"

        return None

    def _generate_suggestions(self) -> List[str]:
        """Generate intelligent suggestions"""
        suggestions = []

        # Time-based suggestions
        hour = datetime.now().hour

        if 9 <= hour <= 11:
            suggestions.append("Gute Zeit für E-Mails beantworten")

        if 14 <= hour <= 16:
            suggestions.append("Nachmittag - Zeit für kreative Arbeit")

        # Activity-based suggestions
        unread = self._count_unread_emails()
        if unread > 10:
            suggestions.append(f"{unread} ungelesene E-Mails - Zeit zum Aufräumen?")

        # Weekly cleanup
        if datetime.now().weekday() == 4:  # Friday
            suggestions.append("Freitag - Guter Tag für Foto-Aufräumen")

        return suggestions

    def _find_productive_hours(self, activities) -> str:
        """Find most productive hours"""
        hour_counts = {}

        for activity in activities:
            # Extract hour from timestamp
            try:
                timestamp = activity[1]
                if isinstance(timestamp, str):
                    hour = int(timestamp.split(':')[0][-2:])
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                pass

        if not hour_counts:
            return "N/A"

        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        return f"{peak_hour}:00 - {peak_hour+1}:00 Uhr"

    def _find_preferred_time(self, activities, activity_type: str):
        """Find preferred time for activity type"""
        # Analyze when user typically does this activity
        return "10:00 - 12:00"  # Placeholder

    def _find_frequent_contacts(self, activities) -> List[str]:
        """Find most frequent contacts"""
        contacts = {}

        for activity in activities:
            # Extract contacts from activities
            content = str(activity[4]) if len(activity) > 4 else ''
            # Parse contacts (simplified)

        return list(contacts.keys())[:5]

    def _analyze_app_usage(self, activities) -> Dict:
        """Analyze app usage patterns"""
        return {
            'morning': ['Mail', 'Slack'],
            'afternoon': ['Slack', 'Photos'],
            'evening': ['Messages']
        }

    def _detect_work_hours(self, activities) -> Dict:
        """Detect typical work hours"""
        return {
            'start': '09:00',
            'end': '18:00',
            'peak': '14:00-16:00'
        }

    # ===== Advanced Analytics =====

    def get_weekly_report(self) -> Dict:
        """Get weekly activity report"""
        report = {
            'total_activities': 0,
            'emails': {'sent': 0, 'received': 0},
            'messages': {'sent': 0, 'received': 0},
            'photos': {'taken': 0, 'deleted': 0},
            'productivity_trend': 'stable',
            'top_apps': [],
            'insights': []
        }

        # Analyze last 7 days
        for days_ago in range(7):
            activities = self.tracker.get_activities_at_time(days_ago=days_ago)
            report['total_activities'] += len(activities)

        report['top_apps'] = self._get_top_apps()

        # Generate insights
        report['insights'].append(f"Du warst {report['total_activities']} mal aktiv diese Woche")

        return report

    def predict_next_action(self) -> str:
        """Predict what user will likely do next"""
        patterns = self.detect_patterns()
        hour = datetime.now().hour

        # Based on time and patterns
        if hour in [9, 10, 11]:
            return "Wahrscheinlich E-Mails checken"
        elif hour in [14, 15]:
            return "Wahrscheinlich Meetings oder Calls"
        else:
            return "Unbestimmt"

    def sentiment_analysis(self, text: str) -> str:
        """Analyze sentiment of text"""
        # Would use AI for real sentiment analysis
        positive_words = ['gut', 'super', 'toll', 'danke', 'perfekt']
        negative_words = ['problem', 'fehler', 'schlecht', 'nicht']

        text_lower = text.lower()

        if any(word in text_lower for word in positive_words):
            return 'positive'
        elif any(word in text_lower for word in negative_words):
            return 'negative'
        else:
            return 'neutral'
