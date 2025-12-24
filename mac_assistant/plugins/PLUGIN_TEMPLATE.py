"""
Plugin Template
Copy this file and customize it for your app

INSTRUCTIONS:
1. Copy this file to a new file (e.g., whatsapp_plugin.py)
2. Replace YOUR_APP_NAME with your app name
3. Implement the required methods
4. Register the plugin in core_v2.py
"""

from typing import Dict, List
from .base_plugin import MessagingPlugin, EmailPlugin, MediaPlugin, ProductivityPlugin
import subprocess
import os


# Choose the appropriate base class:
# - MessagingPlugin for chat apps (WhatsApp, Discord, etc.)
# - EmailPlugin for email clients
# - MediaPlugin for photo/video apps
# - ProductivityPlugin for notes, calendars, reminders
# - BasePlugin for anything else

class YourAppPlugin(MessagingPlugin):  # Change base class as needed
    """Plugin for YOUR_APP_NAME"""

    def __init__(self):
        super().__init__('YOUR_APP_NAME')  # Replace with your app name

    def is_available(self) -> bool:
        """
        Check if the app is installed and available

        Returns:
            True if app is installed, False otherwise
        """
        # Check if app exists in /Applications/
        return os.path.exists('/Applications/YOUR_APP_NAME.app')

    def _execute_applescript(self, script: str) -> str:
        """
        Execute AppleScript and return result

        Args:
            script: AppleScript code to execute

        Returns:
            Script output
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    # ===== REQUIRED METHODS (implement based on your base class) =====

    def read_messages(self, limit: int = 10) -> List[Dict]:
        """
        Read recent messages from the app

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries
        """
        script = f'''
        tell application "YOUR_APP_NAME"
            -- Your AppleScript code here
            -- Example: get recent messages
        end tell
        '''

        result = self._execute_applescript(script)

        # Parse result and return as list of dicts
        return [{'raw': result}]

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """
        Send a message via the app

        Args:
            recipient: Recipient name/number
            message: Message text
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise
        """
        script = f'''
        tell application "YOUR_APP_NAME"
            -- Your AppleScript code to send message
            -- Use recipient: {recipient}
            -- Use message: {message}
        end tell
        '''

        result = self._execute_applescript(script)
        return "Error" not in result

    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        Search within the app

        Args:
            query: Search query
            **kwargs: Additional search parameters

        Returns:
            List of search results
        """
        script = f'''
        tell application "YOUR_APP_NAME"
            -- Your AppleScript code to search
            -- Use query: {query}
        end tell
        '''

        result = self._execute_applescript(script)
        return [{'query': query, 'results': result}]

    # ===== OPTIONAL: Custom Actions =====

    def execute_action(self, action: str, **params) -> Dict:
        """
        Execute custom app-specific actions

        Args:
            action: Action name
            **params: Action parameters

        Returns:
            Action result

        Examples:
            - action='create_group', params={'name': 'My Group', 'members': [...]}
            - action='set_status', params={'status': 'Away'}
        """

        if action == 'your_custom_action':
            # Implement your custom action
            return {'status': 'success', 'message': 'Action executed'}

        # If action not recognized, call parent
        return super().execute_action(action, **params)


# ===== REGISTRATION =====
# After creating your plugin, register it in core_v2.py:
#
# 1. Import your plugin:
#    from mac_assistant.plugins.your_app_plugin import YourAppPlugin
#
# 2. Register in _register_plugins() method:
#    self.plugin_manager.register(YourAppPlugin())
#

# ===== EXAMPLE USAGE =====
# Once registered, users can use your plugin via:
#
# - Natural language:
#   "Sende eine Nachricht über YOUR_APP_NAME an Max"
#
# - Direct API:
#   core.execute_task("send message via YOUR_APP_NAME to Max: Hello!")
#
# - Plugin Manager:
#   plugin = core.get_plugin('YOUR_APP_NAME')
#   plugin.send_message('Max', 'Hello!')
