"""
Activity Tracker Database
Tracks all user activities on the Mac
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json


class ActivityTracker:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path.home() / ".mac_assistant" / "activities.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                app_name TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                metadata TEXT
            )
        ''')

        # Mail activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mail_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                body TEXT,
                attachments TEXT
            )
        ''')

        # WhatsApp activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                contact TEXT,
                message TEXT,
                chat_name TEXT
            )
        ''')

        # Photo activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photo_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                file_path TEXT,
                file_name TEXT,
                tags TEXT,
                date_taken DATETIME
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON activities(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_name ON activities(app_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mail_timestamp ON mail_activities(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_whatsapp_timestamp ON whatsapp_activities(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_photo_timestamp ON photo_activities(timestamp)')

        conn.commit()
        conn.close()

    def log_activity(self, app_name, activity_type, title=None, content=None, metadata=None):
        """Log a general activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT INTO activities (app_name, activity_type, title, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (app_name, activity_type, title, content, metadata_json))

        conn.commit()
        conn.close()

    def log_mail(self, action, sender=None, recipient=None, subject=None, body=None, attachments=None):
        """Log mail activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        attachments_json = json.dumps(attachments) if attachments else None

        cursor.execute('''
            INSERT INTO mail_activities (action, sender, recipient, subject, body, attachments)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action, sender, recipient, subject, body, attachments_json))

        conn.commit()
        conn.close()

    def log_whatsapp(self, action, contact=None, message=None, chat_name=None):
        """Log WhatsApp activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO whatsapp_activities (action, contact, message, chat_name)
            VALUES (?, ?, ?, ?)
        ''', (action, contact, message, chat_name))

        conn.commit()
        conn.close()

    def log_photo(self, action, file_path=None, file_name=None, tags=None, date_taken=None):
        """Log photo activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        tags_json = json.dumps(tags) if tags else None

        cursor.execute('''
            INSERT INTO photo_activities (action, file_path, file_name, tags, date_taken)
            VALUES (?, ?, ?, ?, ?)
        ''', (action, file_path, file_name, tags_json, date_taken))

        conn.commit()
        conn.close()

    def get_activities_at_time(self, days_ago=0, hour=None):
        """Get activities from X days ago, optionally at a specific hour"""
        target_date = datetime.now() - timedelta(days=days_ago)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if hour is not None:
            start_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)

            cursor.execute('''
                SELECT * FROM activities
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
        else:
            start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            cursor.execute('''
                SELECT * FROM activities
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))

        activities = cursor.fetchall()
        conn.close()

        return activities

    def get_recent_mail(self, limit=10):
        """Get recent mail activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM mail_activities
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        mails = cursor.fetchall()
        conn.close()

        return mails

    def get_recent_whatsapp(self, limit=10):
        """Get recent WhatsApp activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM whatsapp_activities
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        messages = cursor.fetchall()
        conn.close()

        return messages

    def search_activities(self, query, app_name=None, days_back=30):
        """Search activities by query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_date = datetime.now() - timedelta(days=days_back)

        sql = '''
            SELECT * FROM activities
            WHERE timestamp >= ?
            AND (title LIKE ? OR content LIKE ?)
        '''
        params = [start_date, f'%{query}%', f'%{query}%']

        if app_name:
            sql += ' AND app_name = ?'
            params.append(app_name)

        sql += ' ORDER BY timestamp DESC LIMIT 100'

        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()

        return results
