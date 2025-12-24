"""
Background Monitor
Continuously monitors system and provides real-time updates
"""

import threading
import time
from datetime import datetime
from typing import Callable, Dict


class BackgroundMonitor:
    """Monitors system activities in background"""

    def __init__(self, core, update_callback: Callable = None):
        self.core = core
        self.update_callback = update_callback

        self.running = False
        self.thread = None

        # Monitoring configuration
        self.monitors = {
            'emails': {'enabled': True, 'interval': 300},  # 5 min
            'messages': {'enabled': True, 'interval': 180},  # 3 min
            'photos': {'enabled': False, 'interval': 600},  # 10 min
            'system': {'enabled': True, 'interval': 60},   # 1 min
        }

        self.last_checks = {}
        self.stats = {
            'emails_checked': 0,
            'messages_checked': 0,
            'notifications_sent': 0,
            'uptime': 0
        }

    def start(self):
        """Start background monitoring"""
        if self.running:
            return

        self.running = True
        self.start_time = datetime.now()

        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        print("👁️  Background Monitor started")

    def stop(self):
        """Stop background monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("👁️  Background Monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                current_time = time.time()

                # Check each monitor
                for monitor_name, config in self.monitors.items():
                    if not config['enabled']:
                        continue

                    last_check = self.last_checks.get(monitor_name, 0)
                    if current_time - last_check >= config['interval']:
                        self._run_monitor(monitor_name)
                        self.last_checks[monitor_name] = current_time

                # Update uptime
                self.stats['uptime'] = (datetime.now() - self.start_time).total_seconds()

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"Error in monitor loop: {e}")

    def _run_monitor(self, monitor_name: str):
        """Run a specific monitor"""
        try:
            if monitor_name == 'emails':
                self._monitor_emails()
            elif monitor_name == 'messages':
                self._monitor_messages()
            elif monitor_name == 'photos':
                self._monitor_photos()
            elif monitor_name == 'system':
                self._monitor_system()
        except Exception as e:
            print(f"Error in {monitor_name} monitor: {e}")

    def _monitor_emails(self):
        """Monitor for new emails"""
        try:
            mail_plugin = self.core.get_plugin('Mail')
            if not mail_plugin or not mail_plugin.is_available():
                return

            # Check for new emails
            emails = mail_plugin.get_unread_emails(5)
            count = len(str(emails).split('\n'))

            self.stats['emails_checked'] += 1

            if count > 0:
                self._send_update({
                    'type': 'emails',
                    'count': count,
                    'message': f"📧 {count} ungelesene E-Mails",
                    'timestamp': datetime.now()
                })

        except Exception as e:
            print(f"Email monitor error: {e}")

    def _monitor_messages(self):
        """Monitor for new messages"""
        try:
            # Check all messaging plugins
            messaging_plugins = self.core.plugin_manager.get_plugins_by_capability('read_messages')

            new_messages = []
            for plugin in messaging_plugins:
                try:
                    messages = plugin.read_messages(5)
                    if messages:
                        new_messages.extend(messages)
                except:
                    pass

            self.stats['messages_checked'] += 1

            if new_messages:
                self._send_update({
                    'type': 'messages',
                    'count': len(new_messages),
                    'message': f"💬 {len(new_messages)} neue Nachrichten",
                    'timestamp': datetime.now()
                })

        except Exception as e:
            print(f"Messages monitor error: {e}")

    def _monitor_photos(self):
        """Monitor for new photos"""
        try:
            photos_plugin = self.core.get_plugin('Photos')
            if not photos_plugin or not photos_plugin.is_available():
                return

            # Check for today's photos
            photos = photos_plugin.get_recent_media(days=0)
            # Parse count
            count = len(str(photos).split('\n'))

            if count > 0:
                self._send_update({
                    'type': 'photos',
                    'count': count,
                    'message': f"📸 {count} neue Fotos heute",
                    'timestamp': datetime.now()
                })

        except Exception as e:
            print(f"Photos monitor error: {e}")

    def _monitor_system(self):
        """Monitor system status"""
        try:
            # Check plugin status
            available_plugins = len(self.core.plugin_manager.get_available_plugins())
            enabled_plugins = len(self.core.plugin_manager.get_enabled_plugins())

            status = {
                'type': 'system',
                'plugins_available': available_plugins,
                'plugins_enabled': enabled_plugins,
                'ai_enabled': self.core.ai_enabled,
                'timestamp': datetime.now()
            }

            self._send_update(status)

        except Exception as e:
            print(f"System monitor error: {e}")

    def _send_update(self, update: Dict):
        """Send update to callback"""
        self.stats['notifications_sent'] += 1

        if self.update_callback:
            self.update_callback(update)
        else:
            print(f"📊 Update: {update.get('message', update)}")

    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        return {
            **self.stats,
            'uptime_formatted': self._format_uptime(self.stats['uptime'])
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

    def enable_monitor(self, monitor_name: str):
        """Enable a specific monitor"""
        if monitor_name in self.monitors:
            self.monitors[monitor_name]['enabled'] = True

    def disable_monitor(self, monitor_name: str):
        """Disable a specific monitor"""
        if monitor_name in self.monitors:
            self.monitors[monitor_name]['enabled'] = False

    def set_interval(self, monitor_name: str, seconds: int):
        """Set monitoring interval"""
        if monitor_name in self.monitors:
            self.monitors[monitor_name]['interval'] = seconds
