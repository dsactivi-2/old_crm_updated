"""
Task Parser
Uses AI to parse natural language tasks into executable actions
"""

from typing import Dict, List, Optional
import re


class TaskParser:
    """Parses natural language tasks into structured actions"""

    def __init__(self, ai_assistant=None):
        self.ai = ai_assistant

    def parse(self, task_description: str, available_plugins: List) -> Dict:
        """
        Parse a task description into an executable action plan

        Args:
            task_description: Natural language task
            available_plugins: List of available plugins

        Returns:
            Dict with structure:
            {
                'plugin': 'PluginName',
                'action': 'action_name',
                'params': {...},
                'confidence': 0.0-1.0
            }
        """

        if self.ai:
            return self._parse_with_ai(task_description, available_plugins)
        else:
            return self._parse_simple(task_description)

    def _parse_with_ai(self, task: str, plugins: List) -> Dict:
        """Use AI to parse the task"""

        plugin_info = "\n".join([
            f"- {p.name}: {', '.join(p.get_capabilities())}"
            for p in plugins
        ])

        prompt = f"""Analysiere folgende Aufgabe und bestimme welches Plugin und welche Aktion verwendet werden soll:

Aufgabe: "{task}"

Verfügbare Plugins und ihre Fähigkeiten:
{plugin_info}

Gib zurück (in diesem exakten Format):
Plugin: [Name]
Action: [action_name]
Params: [key1=value1, key2=value2]
Confidence: [0.0-1.0]

Beispiel:
Plugin: Slack
Action: send_message
Params: recipient=Max, message=Hallo wie geht's?
Confidence: 0.95
"""

        response = self.ai.process_query(prompt)

        # Parse AI response
        result = {
            'plugin': self._extract_field(response, 'Plugin'),
            'action': self._extract_field(response, 'Action'),
            'params': self._extract_params(response),
            'confidence': float(self._extract_field(response, 'Confidence') or '0.5')
        }

        return result

    def _parse_simple(self, task: str) -> Dict:
        """Simple keyword-based parsing"""

        task_lower = task.lower()
        result = {
            'plugin': None,
            'action': None,
            'params': {},
            'confidence': 0.5
        }

        # Detect plugin
        if any(word in task_lower for word in ['slack']):
            result['plugin'] = 'Slack'
        elif any(word in task_lower for word in ['viber']):
            result['plugin'] = 'Viber'
        elif any(word in task_lower for word in ['telegram']):
            result['plugin'] = 'Telegram'
        elif any(word in task_lower for word in ['mail', 'email', 'e-mail']):
            result['plugin'] = 'Mail'
        elif any(word in task_lower for word in ['foto', 'photo', 'bild']):
            result['plugin'] = 'Photos'

        # Detect action
        if any(word in task_lower for word in ['send', 'sende', 'schicke', 'schreibe']):
            result['action'] = 'send_message' if result['plugin'] != 'Mail' else 'send_email'
        elif any(word in task_lower for word in ['such', 'find', 'finde']):
            result['action'] = 'search'
        elif any(word in task_lower for word in ['lösche', 'delete', 'entferne']):
            result['action'] = 'delete'
        elif any(word in task_lower for word in ['lese', 'read', 'zeige', 'show']):
            result['action'] = 'read_messages' if result['plugin'] != 'Mail' else 'get_unread_emails'

        return result

    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field from AI response"""
        pattern = rf'{field_name}:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_params(self, text: str) -> Dict:
        """Extract parameters from AI response"""
        params_line = self._extract_field(text, 'Params')
        if not params_line:
            return {}

        params = {}
        # Parse key=value pairs
        pairs = re.findall(r'(\w+)=([^,\n]+)', params_line)
        for key, value in pairs:
            params[key.strip()] = value.strip()

        return params


class TaskValidator:
    """Validates task execution plans"""

    @staticmethod
    def validate(task_plan: Dict, plugin_manager) -> tuple[bool, Optional[str]]:
        """
        Validate a task plan

        Returns:
            (is_valid, error_message)
        """

        plugin_name = task_plan.get('plugin')
        action = task_plan.get('action')

        if not plugin_name:
            return False, "No plugin specified"

        if not action:
            return False, "No action specified"

        # Check if plugin exists
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return False, f"Plugin '{plugin_name}' not found"

        # Check if plugin is available
        if not plugin.is_available():
            return False, f"Plugin '{plugin_name}' is not available (app not installed)"

        # Check if plugin is enabled
        if not plugin.enabled:
            return False, f"Plugin '{plugin_name}' is disabled"

        # Check if action is supported
        # This is simplified - in reality, we'd check plugin's supported actions
        return True, None
