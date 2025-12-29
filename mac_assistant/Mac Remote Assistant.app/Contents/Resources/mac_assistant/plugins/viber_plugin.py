"""
Viber Plugin
"""

from typing import Dict, List
from .base_plugin import MessagingPlugin
import subprocess
import os


class ViberPlugin(MessagingPlugin):
    """Plugin for Viber"""

    def __init__(self):
        super().__init__('Viber')

    def is_available(self) -> bool:
        """Check if Viber is installed"""
        return os.path.exists('/Applications/Viber.app')

    def _execute_applescript(self, script: str) -> str:
        """Execute AppleScript"""
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def read_messages(self, limit: int = 10) -> List[Dict]:
        """Read recent Viber messages"""
        script = '''
        tell application "Viber"
            activate
        end tell

        tell application "System Events"
            tell process "Viber"
                return "Viber is running"
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'status': result, 'note': 'Viber requires UI scripting for full access'}]

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """Send a Viber message"""
        script = f'''
        tell application "Viber"
            activate
        end tell

        delay 0.5

        tell application "System Events"
            tell process "Viber"
                -- Press Cmd+F to search for contact
                keystroke "f" using command down
                delay 0.3

                -- Type contact name
                keystroke "{recipient}"
                delay 0.5

                -- Press Return to select
                keystroke return
                delay 0.3

                -- Type message
                keystroke "{message}"
                delay 0.2

                -- Send message (Return)
                keystroke return
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return "Error" not in result

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search Viber messages"""
        script = f'''
        tell application "Viber"
            activate
        end tell

        tell application "System Events"
            tell process "Viber"
                keystroke "f" using command down
                delay 0.3
                keystroke "{query}"
            end tell
        end tell
        '''
        self._execute_applescript(script)
        return [{'status': 'Search initiated in Viber'}]
