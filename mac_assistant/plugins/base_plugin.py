"""
Base Plugin Class
All app integrations should inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BasePlugin(ABC):
    """Base class for all app plugins"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this plugin supports.

        Common capabilities:
        - read_messages
        - send_messages
        - read_emails
        - send_emails
        - search
        - delete
        - upload
        - download
        - execute_commands
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this app is installed and accessible"""
        pass

    # Optional methods - override if supported

    def read_messages(self, limit: int = 10) -> List[Dict]:
        """Read recent messages/chats"""
        raise NotImplementedError(f"{self.name} does not support reading messages")

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """Send a message"""
        raise NotImplementedError(f"{self.name} does not support sending messages")

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search within the app"""
        raise NotImplementedError(f"{self.name} does not support search")

    def get_status(self) -> Dict:
        """Get current status/state of the app"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'available': self.is_available(),
            'capabilities': self.get_capabilities()
        }

    def execute_action(self, action: str, **params) -> Any:
        """
        Execute a custom action with parameters

        Args:
            action: Action name (e.g., 'create_channel', 'set_status', etc.)
            **params: Action-specific parameters

        Returns:
            Action result
        """
        raise NotImplementedError(f"{self.name} does not support action: {action}")

    def enable(self):
        """Enable this plugin"""
        self.enabled = True

    def disable(self):
        """Disable this plugin"""
        self.enabled = False


class MessagingPlugin(BasePlugin):
    """Base class for messaging apps (WhatsApp, Slack, Viber, etc.)"""

    def get_capabilities(self) -> List[str]:
        return ['read_messages', 'send_messages', 'search']

    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages"""
        return self.read_messages(limit)

    def send(self, recipient: str, message: str) -> bool:
        """Send a message"""
        return self.send_message(recipient, message)


class EmailPlugin(BasePlugin):
    """Base class for email apps"""

    def get_capabilities(self) -> List[str]:
        return ['read_emails', 'send_emails', 'search', 'reply']

    def get_unread_emails(self, limit: int = 10) -> List[Dict]:
        """Get unread emails"""
        raise NotImplementedError()

    def send_email(self, to: str, subject: str, body: str, **kwargs) -> bool:
        """Send an email"""
        raise NotImplementedError()

    def reply_to_email(self, email_id: str, reply_body: str) -> bool:
        """Reply to an email"""
        raise NotImplementedError()


class MediaPlugin(BasePlugin):
    """Base class for media apps (Photos, etc.)"""

    def get_capabilities(self) -> List[str]:
        return ['search', 'delete', 'upload', 'download']

    def get_recent_media(self, days: int = 7) -> List[Dict]:
        """Get recent media files"""
        raise NotImplementedError()

    def delete_media(self, media_ids: List[str]) -> bool:
        """Delete media files"""
        raise NotImplementedError()


class ProductivityPlugin(BasePlugin):
    """Base class for productivity apps (Calendar, Notes, Reminders, etc.)"""

    def get_capabilities(self) -> List[str]:
        return ['create', 'read', 'update', 'delete', 'search']

    def create_item(self, **kwargs) -> Dict:
        """Create a new item (note, reminder, event, etc.)"""
        raise NotImplementedError()

    def get_items(self, **filters) -> List[Dict]:
        """Get items with optional filters"""
        raise NotImplementedError()
