"""
Plugin Manager
Manages all app plugins and provides unified interface
"""

from typing import Dict, List, Optional, Type
from .base_plugin import BasePlugin


class PluginManager:
    """Manages all registered plugins"""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        print(f"✓ Plugin registered: {plugin.name}")

    def unregister(self, plugin_name: str):
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            print(f"✓ Plugin unregistered: {plugin_name}")

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)

    def get_all_plugins(self) -> List[BasePlugin]:
        """Get all registered plugins"""
        return list(self.plugins.values())

    def get_available_plugins(self) -> List[BasePlugin]:
        """Get all available (installed) plugins"""
        return [p for p in self.plugins.values() if p.is_available()]

    def get_enabled_plugins(self) -> List[BasePlugin]:
        """Get all enabled plugins"""
        return [p for p in self.plugins.values() if p.enabled and p.is_available()]

    def get_plugins_by_capability(self, capability: str) -> List[BasePlugin]:
        """Get all plugins that support a specific capability"""
        return [
            p for p in self.get_enabled_plugins()
            if capability in p.get_capabilities()
        ]

    def send_message_to_any(self, recipient: str, message: str, app_preference: Optional[str] = None) -> bool:
        """
        Send a message using any available messaging plugin

        Args:
            recipient: Recipient name/number
            message: Message text
            app_preference: Preferred app (e.g., 'WhatsApp', 'Slack')

        Returns:
            True if message was sent successfully
        """
        # Try preferred app first
        if app_preference:
            plugin = self.get_plugin(app_preference)
            if plugin and plugin.enabled and 'send_messages' in plugin.get_capabilities():
                try:
                    return plugin.send_message(recipient, message)
                except Exception as e:
                    print(f"Error with {app_preference}: {e}")

        # Try all messaging plugins
        messaging_plugins = self.get_plugins_by_capability('send_messages')
        for plugin in messaging_plugins:
            try:
                return plugin.send_message(recipient, message)
            except Exception as e:
                print(f"Error with {plugin.name}: {e}")
                continue

        return False

    def search_everywhere(self, query: str) -> Dict[str, List]:
        """
        Search across all plugins that support search

        Returns:
            Dict mapping plugin name to search results
        """
        results = {}
        search_plugins = self.get_plugins_by_capability('search')

        for plugin in search_plugins:
            try:
                plugin_results = plugin.search(query)
                if plugin_results:
                    results[plugin.name] = plugin_results
            except Exception as e:
                print(f"Search error in {plugin.name}: {e}")

        return results

    def get_all_messages(self, limit: int = 10) -> Dict[str, List]:
        """
        Get messages from all messaging plugins

        Returns:
            Dict mapping plugin name to messages
        """
        all_messages = {}
        messaging_plugins = self.get_plugins_by_capability('read_messages')

        for plugin in messaging_plugins:
            try:
                messages = plugin.read_messages(limit)
                if messages:
                    all_messages[plugin.name] = messages
            except Exception as e:
                print(f"Error reading from {plugin.name}: {e}")

        return all_messages

    def execute_task(self, task_description: str, ai_assistant=None) -> Dict:
        """
        Execute a task using the appropriate plugin

        Args:
            task_description: Natural language task description
            ai_assistant: Optional AI assistant to parse task

        Returns:
            Task execution result
        """
        # If AI is available, use it to determine which plugin and action to use
        if ai_assistant:
            # AI will analyze the task and determine the action
            task_plan = ai_assistant.parse_task(task_description, self.get_all_plugins())

            plugin_name = task_plan.get('plugin')
            action = task_plan.get('action')
            params = task_plan.get('params', {})

            plugin = self.get_plugin(plugin_name)
            if plugin and plugin.enabled:
                return plugin.execute_action(action, **params)

        # Fallback: simple keyword matching
        return self._execute_task_simple(task_description)

    def _execute_task_simple(self, task_description: str) -> Dict:
        """Simple task execution based on keywords"""
        task_lower = task_description.lower()

        # Messaging tasks
        if 'nachricht' in task_lower or 'message' in task_lower:
            # Extract recipient and message
            # This is simplified - in reality, AI would parse this better
            return {'status': 'Please specify recipient and message'}

        # Email tasks
        if 'email' in task_lower or 'mail' in task_lower:
            return {'status': 'Please specify email details'}

        return {'status': 'Task not recognized', 'description': task_description}

    def get_status_summary(self) -> Dict:
        """Get summary of all plugins"""
        summary = {
            'total': len(self.plugins),
            'available': len(self.get_available_plugins()),
            'enabled': len(self.get_enabled_plugins()),
            'plugins': {}
        }

        for plugin in self.plugins.values():
            summary['plugins'][plugin.name] = plugin.get_status()

        return summary
