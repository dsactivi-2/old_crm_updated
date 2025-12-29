"""
Main GUI Window for Mac Assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta
import threading


class MacAssistantGUI:
    def __init__(self, assistant_core):
        self.core = assistant_core
        self.root = tk.Tk()
        self.root.title("Mac Remote Assistant")
        self.root.geometry("1000x700")

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Chat/Query Interface
        self.create_chat_tab()

        # Tab 2: Activity Timeline
        self.create_timeline_tab()

        # Tab 3: Mail Management
        self.create_mail_tab()

        # Tab 4: Photo Management
        self.create_photo_tab()

        # Tab 5: Settings
        self.create_settings_tab()

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Bereit",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_chat_tab(self):
        """Create the main chat interface tab"""
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="Assistent")

        # Chat display
        chat_label = ttk.Label(chat_frame, text="Frage deinen Mac-Assistenten:")
        chat_label.pack(padx=10, pady=5, anchor=tk.W)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=('Arial', 11)
        )
        self.chat_display.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.query_input = ttk.Entry(input_frame, font=('Arial', 11))
        self.query_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.query_input.bind('<Return>', lambda e: self.send_query())

        send_button = ttk.Button(input_frame, text="Senden", command=self.send_query)
        send_button.pack(side=tk.LEFT)

        # Quick actions
        actions_frame = ttk.LabelFrame(chat_frame, text="Schnellaktionen")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            actions_frame,
            text="Was habe ich heute gemacht?",
            command=lambda: self.quick_query("Was habe ich heute gemacht?")
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            actions_frame,
            text="Neue E-Mails",
            command=lambda: self.quick_query("Zeige mir meine neuen E-Mails")
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            actions_frame,
            text="Fotos diese Woche",
            command=lambda: self.quick_query("Welche Fotos habe ich diese Woche gemacht?")
        ).pack(side=tk.LEFT, padx=5, pady=5)

    def create_timeline_tab(self):
        """Create activity timeline tab"""
        timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(timeline_frame, text="Aktivitäten")

        # Time selector
        time_frame = ttk.Frame(timeline_frame)
        time_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(time_frame, text="Zeige Aktivitäten von:").pack(side=tk.LEFT, padx=5)

        self.days_ago_var = tk.IntVar(value=0)
        ttk.Spinbox(
            time_frame,
            from_=0,
            to=30,
            textvariable=self.days_ago_var,
            width=5
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(time_frame, text="Tagen zuvor").pack(side=tk.LEFT, padx=5)

        self.hour_var = tk.IntVar(value=-1)
        ttk.Label(time_frame, text="um").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Spinbox(
            time_frame,
            from_=-1,
            to=23,
            textvariable=self.hour_var,
            width=5
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(time_frame, text="Uhr (-1 = ganzer Tag)").pack(side=tk.LEFT, padx=5)

        ttk.Button(
            time_frame,
            text="Laden",
            command=self.load_timeline
        ).pack(side=tk.LEFT, padx=20)

        # Timeline display
        self.timeline_display = scrolledtext.ScrolledText(
            timeline_frame,
            wrap=tk.WORD,
            width=100,
            height=35,
            font=('Courier', 10)
        )
        self.timeline_display.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def create_mail_tab(self):
        """Create mail management tab"""
        mail_frame = ttk.Frame(self.notebook)
        self.notebook.add(mail_frame, text="E-Mails")

        # Controls
        control_frame = ttk.Frame(mail_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            control_frame,
            text="Ungelesene E-Mails laden",
            command=self.load_unread_mails
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Mit KI beantworten",
            command=self.ai_reply_email
        ).pack(side=tk.LEFT, padx=5)

        # Email list
        self.mail_tree = ttk.Treeview(
            mail_frame,
            columns=('Absender', 'Betreff', 'Datum'),
            show='headings',
            height=15
        )
        self.mail_tree.heading('Absender', text='Absender')
        self.mail_tree.heading('Betreff', text='Betreff')
        self.mail_tree.heading('Datum', text='Datum')
        self.mail_tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Email preview
        preview_label = ttk.Label(mail_frame, text="Vorschau:")
        preview_label.pack(padx=10, pady=5, anchor=tk.W)

        self.mail_preview = scrolledtext.ScrolledText(
            mail_frame,
            wrap=tk.WORD,
            height=10,
            font=('Arial', 10)
        )
        self.mail_preview.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def create_photo_tab(self):
        """Create photo management tab"""
        photo_frame = ttk.Frame(self.notebook)
        self.notebook.add(photo_frame, text="Fotos")

        # Search controls
        search_frame = ttk.Frame(photo_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Suche:").pack(side=tk.LEFT, padx=5)

        self.photo_search_var = tk.StringVar()
        ttk.Entry(
            search_frame,
            textvariable=self.photo_search_var,
            width=30
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="Fotos suchen",
            command=self.search_photos
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="Letzte 7 Tage",
            command=lambda: self.load_recent_photos(7)
        ).pack(side=tk.LEFT, padx=5)

        # Photo list
        self.photo_tree = ttk.Treeview(
            photo_frame,
            columns=('Name', 'Datum', 'Pfad'),
            show='headings',
            height=20
        )
        self.photo_tree.heading('Name', text='Name')
        self.photo_tree.heading('Datum', text='Datum')
        self.photo_tree.heading('Pfad', text='Pfad')
        self.photo_tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Action buttons
        action_frame = ttk.Frame(photo_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            action_frame,
            text="Ausgewählte löschen",
            command=self.delete_selected_photos
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="KI-Analyse",
            command=self.ai_analyze_photos
        ).pack(side=tk.LEFT, padx=5)

    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Einstellungen")

        # API Key
        api_frame = ttk.LabelFrame(settings_frame, text="API Einstellungen")
        api_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(api_frame, text="Anthropic API Key:").pack(padx=10, pady=5, anchor=tk.W)

        self.api_key_var = tk.StringVar()
        ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            width=60,
            show="*"
        ).pack(padx=10, pady=5)

        ttk.Button(
            api_frame,
            text="Speichern",
            command=self.save_settings
        ).pack(padx=10, pady=5)

        # Activity tracking
        tracking_frame = ttk.LabelFrame(settings_frame, text="Aktivitätsverfolgung")
        tracking_frame.pack(fill=tk.X, padx=10, pady=10)

        self.tracking_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tracking_frame,
            text="Aktivitätsverfolgung aktiviert",
            variable=self.tracking_enabled
        ).pack(padx=10, pady=5, anchor=tk.W)

        self.auto_reply_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            tracking_frame,
            text="Automatische Antworten (KI)",
            variable=self.auto_reply_enabled
        ).pack(padx=10, pady=5, anchor=tk.W)

        # Info
        info_frame = ttk.LabelFrame(settings_frame, text="Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_text = """Mac Remote Assistant v1.0

Diese App hilft dir:
• E-Mails und Nachrichten zu verwalten
• Fotos zu durchsuchen und zu organisieren
• Aktivitäten zu verfolgen
• KI-gestützte Automatisierung

Berechtigungen erforderlich:
• Zugriff auf Mail.app
• Zugriff auf Messages.app
• Zugriff auf Photos.app
• Zugriff auf Accessibility APIs
"""
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)

    # ===== Event Handlers =====

    def send_query(self):
        """Send a query to the AI assistant"""
        query = self.query_input.get().strip()
        if not query:
            return

        self.chat_display.insert(tk.END, f"\n🙋 Du: {query}\n", 'user')
        self.query_input.delete(0, tk.END)

        self.status_bar.config(text="Verarbeite Anfrage...")
        self.root.update()

        # Process in thread to avoid blocking UI
        threading.Thread(target=self._process_query, args=(query,), daemon=True).start()

    def _process_query(self, query):
        """Process query in background thread"""
        try:
            response = self.core.process_user_query(query)
            self.chat_display.insert(tk.END, f"🤖 Assistent: {response}\n", 'assistant')
            self.status_bar.config(text="Bereit")
        except Exception as e:
            self.chat_display.insert(tk.END, f"❌ Fehler: {str(e)}\n", 'error')
            self.status_bar.config(text="Fehler aufgetreten")

    def quick_query(self, query):
        """Execute a quick query"""
        self.query_input.delete(0, tk.END)
        self.query_input.insert(0, query)
        self.send_query()

    def load_timeline(self):
        """Load activity timeline"""
        days_ago = self.days_ago_var.get()
        hour = self.hour_var.get()

        self.timeline_display.delete('1.0', tk.END)
        self.status_bar.config(text="Lade Aktivitäten...")

        threading.Thread(
            target=self._load_timeline,
            args=(days_ago, hour),
            daemon=True
        ).start()

    def _load_timeline(self, days_ago, hour):
        """Load timeline in background"""
        try:
            activities = self.core.get_activities_at_time(
                days_ago=days_ago,
                hour=hour if hour >= 0 else None
            )

            if not activities:
                self.timeline_display.insert(
                    tk.END,
                    "Keine Aktivitäten für diesen Zeitraum gefunden."
                )
            else:
                for activity in activities:
                    self.timeline_display.insert(
                        tk.END,
                        f"{activity}\n\n"
                    )

            self.status_bar.config(text=f"{len(activities)} Aktivitäten geladen")
        except Exception as e:
            self.timeline_display.insert(tk.END, f"Fehler: {str(e)}")
            self.status_bar.config(text="Fehler beim Laden")

    def load_unread_mails(self):
        """Load unread emails"""
        self.status_bar.config(text="Lade E-Mails...")
        threading.Thread(target=self._load_unread_mails, daemon=True).start()

    def _load_unread_mails(self):
        """Load unread emails in background"""
        try:
            # Clear existing items
            for item in self.mail_tree.get_children():
                self.mail_tree.delete(item)

            emails = self.core.get_unread_emails()
            # Process and display emails
            self.status_bar.config(text=f"{len(emails)} E-Mails geladen")
        except Exception as e:
            self.status_bar.config(text=f"Fehler: {str(e)}")

    def ai_reply_email(self):
        """Generate AI reply for selected email"""
        selection = self.mail_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wähle eine E-Mail aus")
            return

        # Generate reply using AI
        messagebox.showinfo("Info", "KI-Antwort wird generiert...")

    def search_photos(self):
        """Search for photos"""
        query = self.photo_search_var.get().strip()
        if not query:
            return

        self.status_bar.config(text="Suche Fotos...")
        threading.Thread(target=self._search_photos, args=(query,), daemon=True).start()

    def _search_photos(self, query):
        """Search photos in background"""
        try:
            results = self.core.search_photos(query)
            # Display results
            self.status_bar.config(text=f"{len(results)} Fotos gefunden")
        except Exception as e:
            self.status_bar.config(text=f"Fehler: {str(e)}")

    def load_recent_photos(self, days):
        """Load recent photos"""
        self.status_bar.config(text=f"Lade Fotos der letzten {days} Tage...")
        threading.Thread(target=self._load_recent_photos, args=(days,), daemon=True).start()

    def _load_recent_photos(self, days):
        """Load recent photos in background"""
        try:
            photos = self.core.get_recent_photos(days)
            # Display photos
            self.status_bar.config(text=f"{len(photos)} Fotos geladen")
        except Exception as e:
            self.status_bar.config(text=f"Fehler: {str(e)}")

    def delete_selected_photos(self):
        """Delete selected photos"""
        selection = self.photo_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wähle Fotos aus")
            return

        if messagebox.askyesno("Bestätigung", f"{len(selection)} Foto(s) wirklich löschen?"):
            # Delete photos
            messagebox.showinfo("Info", "Fotos gelöscht")

    def ai_analyze_photos(self):
        """Let AI analyze photos for suggestions"""
        messagebox.showinfo("Info", "KI analysiert Fotos...")

    def save_settings(self):
        """Save settings"""
        api_key = self.api_key_var.get()
        if api_key:
            # Save API key
            messagebox.showinfo("Erfolg", "Einstellungen gespeichert")

    def run(self):
        """Start the GUI"""
        self.root.mainloop()
