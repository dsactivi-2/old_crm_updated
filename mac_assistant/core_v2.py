"""
Core Application Logic V2
With Plugin System and Task Execution
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from database.activity_tracker import ActivityTracker
from utils.ai_assistant import AIAssistant, AutomationEngine
from plugins.plugin_manager import PluginManager
from tasks.task_executor import TaskExecutor

# Import all plugins
from plugins.mail_plugin import MailAppPlugin
from plugins.slack_plugin import SlackPlugin
from plugins.viber_plugin import ViberPlugin
from plugins.telegram_plugin import TelegramPlugin
from plugins.photos_plugin import PhotosPlugin


class MacAssistantCore:
    """Core logic for Mac Assistant with Plugin System"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the assistant core"""

        # Initialize components
        self.tracker = ActivityTracker()

        # Initialize AI
        try:
            self.ai = AIAssistant(api_key)
            self.automation = AutomationEngine(self.ai)
            self.ai_enabled = True
        except ValueError:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. AI features disabled.")
            self.ai = None
            self.automation = None
            self.ai_enabled = False

        # Initialize Plugin Manager
        self.plugin_manager = PluginManager()
        self._register_plugins()

        # Initialize Task Executor
        self.task_executor = TaskExecutor(
            plugin_manager=self.plugin_manager,
            activity_tracker=self.tracker,
            ai_assistant=self.ai
        )

        # Activity monitoring
        self.monitoring_active = False

        print(f"✓ Core initialized with {len(self.plugin_manager.get_available_plugins())} available plugins")

    def _register_plugins(self):
        """Register all available plugins"""

        # Core plugins
        self.plugin_manager.register(MailAppPlugin())
        self.plugin_manager.register(PhotosPlugin())

        # Messaging plugins
        self.plugin_manager.register(SlackPlugin())
        self.plugin_manager.register(ViberPlugin())
        self.plugin_manager.register(TelegramPlugin())

        # More plugins can be added here...

    def process_user_query(self, query: str) -> str:
        """Process a user query and return response"""

        query_lower = query.lower()

        # Check if this is a task execution request
        if self._is_task_request(query_lower):
            return self._handle_task_execution(query)

        # Time-based queries
        if "vor" in query_lower and ("tagen" in query_lower or "tag" in query_lower):
            return self._handle_time_query(query)

        # Plugin management queries
        if "plugin" in query_lower or "app" in query_lower:
            if "liste" in query_lower or "zeige" in query_lower or "verfügbar" in query_lower:
                return self._list_plugins()
            elif "aktiviere" in query_lower or "enable" in query_lower:
                return self._enable_plugin(query)
            elif "deaktiviere" in query_lower or "disable" in query_lower:
                return self._disable_plugin(query)

        # Search everywhere
        if "suche überall" in query_lower or "search everywhere" in query_lower:
            search_term = query_lower.replace("suche überall", "").replace("search everywhere", "").strip()
            return self._search_everywhere(search_term)

        # General queries - use AI if available
        if self.ai_enabled:
            context = self._gather_context()
            return self.ai.process_query(query, context)
        else:
            return "Bitte stelle eine spezifischere Frage oder führe eine Aufgabe aus."

    def _is_task_request(self, query_lower: str) -> bool:
        """Check if query is a task execution request"""
        task_keywords = [
            'sende', 'send', 'schicke', 'schreibe', 'write',
            'lösche', 'delete', 'erstelle', 'create',
            'öffne', 'open', 'starte', 'start',
            'führe aus', 'execute', 'mach', 'do'
        ]
        return any(keyword in query_lower for keyword in task_keywords)

    def _handle_task_execution(self, task_description: str) -> str:
        """Execute a task based on natural language description"""

        if not self.ai_enabled:
            # Try simple execution
            result = self.task_executor.execute_from_natural_language(task_description)
        else:
            # Check if it's a multi-step task
            if "und dann" in task_description.lower() or "danach" in task_description.lower():
                result = self.task_executor.execute_multi_step_task(task_description)
            else:
                result = self.task_executor.execute_from_natural_language(task_description)

        if result['success']:
            return f"✓ Aufgabe ausgeführt!\n\nErgebnis: {result.get('result', 'OK')}"
        else:
            return f"✗ Fehler: {result.get('error', 'Unknown error')}"

    def _handle_time_query(self, query: str) -> str:
        """Handle time-based queries"""

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
            return f"Keine Aktivitäten {time_desc} gefunden."

        # Format response
        if self.ai_enabled:
            return self.ai.search_activities_natural_language(query, activities)
        else:
            response = f"Aktivitäten gefunden ({len(activities)}):\n\n"
            for activity in activities[:10]:
                response += f"- {activity[1]} | {activity[2]} | {activity[3]}: {activity[4]}\n"
            return response

    def _list_plugins(self) -> str:
        """List all available plugins"""

        response = "=== Verfügbare Plugins ===\n\n"

        all_plugins = self.plugin_manager.get_all_plugins()

        for plugin in all_plugins:
            status = "✓" if plugin.is_available() else "✗"
            enabled = "AN" if plugin.enabled else "AUS"

            response += f"{status} {plugin.name} [{enabled}]\n"
            response += f"   Funktionen: {', '.join(plugin.get_capabilities())}\n\n"

        return response

    def _enable_plugin(self, query: str) -> str:
        """Enable a plugin"""
        # Extract plugin name from query
        for plugin in self.plugin_manager.get_all_plugins():
            if plugin.name.lower() in query.lower():
                plugin.enable()
                return f"✓ Plugin '{plugin.name}' aktiviert"

        return "Plugin nicht gefunden"

    def _disable_plugin(self, query: str) -> str:
        """Disable a plugin"""
        for plugin in self.plugin_manager.get_all_plugins():
            if plugin.name.lower() in query.lower():
                plugin.disable()
                return f"✓ Plugin '{plugin.name}' deaktiviert"

        return "Plugin nicht gefunden"

    def _search_everywhere(self, query: str) -> str:
        """Search across all plugins"""

        if not query:
            return "Bitte gib einen Suchbegriff an"

        results = self.plugin_manager.search_everywhere(query)

        if not results:
            return f"Keine Ergebnisse für '{query}' gefunden"

        response = f"=== Suchergebnisse für '{query}' ===\n\n"

        for plugin_name, plugin_results in results.items():
            response += f"📱 {plugin_name}:\n"
            for result in plugin_results:
                response += f"   - {result}\n"
            response += "\n"

        return response

    def _gather_context(self) -> Dict:
        """Gather current context for AI"""

        context = {
            'current_time': datetime.now().isoformat(),
            'available_plugins': [p.name for p in self.plugin_manager.get_available_plugins()],
            'enabled_plugins': [p.name for p in self.plugin_manager.get_enabled_plugins()],
        }

        return context

    # ===== Direct Actions =====

    def execute_task(self, task_description: str) -> Dict:
        """
        Execute a task and return structured result

        Args:
            task_description: Natural language task description

        Returns:
            Task execution result
        """
        return self.task_executor.execute_from_natural_language(task_description)

    def execute_multi_step_task(self, task_description: str) -> Dict:
        """Execute a multi-step task"""
        return self.task_executor.execute_multi_step_task(task_description)

    def get_plugin(self, name: str):
        """Get a plugin by name"""
        return self.plugin_manager.get_plugin(name)

    def get_all_messages(self, limit: int = 10) -> Dict:
        """Get messages from all messaging apps"""
        return self.plugin_manager.get_all_messages(limit)

    def send_message_to_any(self, recipient: str, message: str, app_preference: str = None) -> bool:
        """Send a message using any available messaging app"""
        success = self.plugin_manager.send_message_to_any(recipient, message, app_preference)

        if success and self.tracker:
            self.tracker.log_activity(
                app_name=app_preference or 'Any',
                activity_type='message_sent',
                title=recipient,
                content=message
            )

        return success

    def get_activities_at_time(self, days_ago: int = 0, hour: Optional[int] = None) -> List:
        """Get activities from a specific time"""
        return self.tracker.get_activities_at_time(days_ago, hour)

    def search_activities(self, query: str, days_back: int = 30) -> List:
        """Search through activities"""
        return self.tracker.search_activities(query, days_back=days_back)

    def get_task_history(self, limit: int = 20) -> List:
        """Get task execution history"""
        return self.task_executor.get_task_history(limit)

    def get_plugin_status(self) -> Dict:
        """Get status of all plugins"""
        return self.plugin_manager.get_status_summary()

    # ===== Monitoring =====

    def start_monitoring(self):
        """Start monitoring user activities"""
        self.monitoring_active = True
        print("✓ Activity monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        print("✓ Activity monitoring stopped")
