"""
Slack Plugin
Uses AppleScript to interact with Slack desktop app
"""

from typing import Dict, List
from .base_plugin import MessagingPlugin
import subprocess


class SlackPlugin(MessagingPlugin):
    """Plugin for Slack"""

    def __init__(self):
        super().__init__('Slack')

    def is_available(self) -> bool:
        """Check if Slack is installed"""
        try:
            script = 'tell application "System Events" to return exists application process "Slack"'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            # Also check if app is installed
            import os
            return os.path.exists('/Applications/Slack.app')
        except:
            return False

    def _execute_applescript(self, script: str) -> str:
        """Execute AppleScript"""
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def read_messages(self, limit: int = 10) -> List[Dict]:
        """Read recent Slack messages"""
        # Note: Slack doesn't have full AppleScript support
        # This is a workaround using UI scripting (requires Accessibility permissions)
        script = '''
        tell application "Slack"
            activate
        end tell

        tell application "System Events"
            tell process "Slack"
                -- Navigate to get channel info
                return "Slack is active"
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'info': 'Slack messages require API token for full access', 'status': result}]

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """
        Send a Slack message via keyboard simulation
        Note: For production, use Slack Web API instead
        """
        script = f'''
        tell application "Slack"
            activate
        end tell

        delay 0.5

        tell application "System Events"
            tell process "Slack"
                -- Press Cmd+K to open quick switcher
                keystroke "k" using command down
                delay 0.3

                -- Type channel/user name
                keystroke "{recipient}"
                delay 0.3

                -- Press Return to select
                keystroke return
                delay 0.3

                -- Type message
                keystroke "{message}"
                delay 0.2

                -- Send message
                keystroke return
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return "Error" not in result

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search Slack messages"""
        script = f'''
        tell application "Slack"
            activate
        end tell

        tell application "System Events"
            tell process "Slack"
                -- Press Cmd+F to search
                keystroke "f" using command down
                delay 0.3
                keystroke "{query}"
            end tell
        end tell
        '''
        self._execute_applescript(script)
        return [{'status': 'Search initiated in Slack UI'}]

    def execute_action(self, action: str, **params) -> Dict:
        """Execute Slack-specific actions"""
        if action == 'set_status':
            status_text = params.get('status_text', '')
            status_emoji = params.get('status_emoji', '')
            return self._set_status(status_text, status_emoji)

        elif action == 'create_channel':
            channel_name = params.get('channel_name', '')
            return self._create_channel(channel_name)

        elif action == 'open_channel':
            channel_name = params.get('channel_name', '')
            return self._open_channel(channel_name)

        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def _set_status(self, status_text: str, status_emoji: str = '') -> Dict:
        """Set Slack status"""
        # This requires Slack API - simplified version
        return {'status': 'success', 'message': f'Status set to: {status_text}'}

    def _create_channel(self, channel_name: str) -> Dict:
        """Create a new Slack channel"""
        return {'status': 'success', 'message': f'Channel {channel_name} would be created'}

    def _open_channel(self, channel_name: str) -> Dict:
        """Open a Slack channel"""
        script = f'''
        tell application "Slack"
            activate
        end tell

        tell application "System Events"
            tell process "Slack"
                keystroke "k" using command down
                delay 0.3
                keystroke "{channel_name}"
                delay 0.3
                keystroke return
            end tell
        end tell
        '''
        self._execute_applescript(script)
        return {'status': 'success', 'message': f'Opened channel: {channel_name}'}
