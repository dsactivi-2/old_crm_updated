"""
Mail.app Plugin
"""

from typing import Dict, List
from .base_plugin import EmailPlugin
import subprocess


class MailAppPlugin(EmailPlugin):
    """Plugin for macOS Mail.app"""

    def __init__(self):
        super().__init__('Mail')

    def is_available(self) -> bool:
        """Check if Mail.app is available"""
        try:
            script = 'tell application "System Events" to return exists application process "Mail"'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return True  # Mail.app is always available on macOS
        except:
            return False

    def _execute_applescript(self, script: str) -> str:
        """Execute AppleScript"""
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def get_unread_emails(self, limit: int = 10) -> List[Dict]:
        """Get unread emails"""
        script = f'''
        tell application "Mail"
            set unreadMessages to messages of inbox whose read status is false
            set emailList to {{}}
            repeat with msg in (items 1 thru (count of unreadMessages) of unreadMessages)
                set emailInfo to {{subject:(subject of msg), sender:(sender of msg), dateReceived:(date received of msg)}}
                set end of emailList to emailInfo
                if (count of emailList) >= {limit} then exit repeat
            end repeat
            return emailList
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'raw': result}]

    def send_email(self, to: str, subject: str, body: str, **kwargs) -> bool:
        """Send an email"""
        script = f'''
        tell application "Mail"
            set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
            tell newMessage
                make new to recipient with properties {{address:"{to}"}}
                send
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return "Error" not in result

    def reply_to_email(self, email_id: str, reply_body: str) -> bool:
        """Reply to latest email"""
        script = f'''
        tell application "Mail"
            set latestMessage to item 1 of (messages of inbox)
            set replyMessage to reply latestMessage with opening window yes
            set content of replyMessage to "{reply_body}"
            send replyMessage
        end tell
        '''
        result = self._execute_applescript(script)
        return "Error" not in result

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search emails"""
        script = f'''
        tell application "Mail"
            set foundMessages to (every message whose subject contains "{query}" or sender contains "{query}")
            return count of foundMessages
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'query': query, 'results': result}]
