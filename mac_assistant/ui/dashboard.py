"""
Modern Dashboard GUI for Mac Assistant
Native macOS look & feel with all controls
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime
import os


class DashboardGUI:
    def __init__(self, core):
        self.core = core
        self.root = tk.Tk()
        self.root.title("Mac Remote Assistant")
        self.root.geometry("1400x900")

        # Colors - macOS style
        self.bg_color = "#f5f5f7"
        self.card_color = "#ffffff"
        self.accent_color = "#007AFF"
        self.text_color = "#1d1d1f"
        self.success_color = "#34C759"
        self.warning_color = "#FF9500"
        self.error_color = "#FF3B30"

        self.root.configure(bg=self.bg_color)

        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Setup the complete dashboard UI"""

        # Top Bar
        self.create_top_bar()

        # Main Container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left Sidebar (Plugins & Quick Actions)
        self.create_sidebar(main_container)

        # Center Panel (Main Dashboard)
        self.create_center_panel(main_container)

        # Right Panel (Activity Feed)
        self.create_right_panel(main_container)

        # Bottom Status Bar
        self.create_status_bar()

    def create_top_bar(self):
        """Create top navigation bar"""
        top_bar = tk.Frame(self.root, bg=self.accent_color, height=60)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        # Logo/Title
        title = tk.Label(
            top_bar,
            text="🤖 Mac Remote Assistant",
            font=("SF Pro Display", 24, "bold"),
            bg=self.accent_color,
            fg="white"
        )
        title.pack(side=tk.LEFT, padx=20, pady=10)

        # API Status Indicator
        self.api_status = tk.Label(
            top_bar,
            text="● KI Aktiv" if self.core.ai_enabled else "○ KI Inaktiv",
            font=("SF Pro Text", 12),
            bg=self.accent_color,
            fg="white"
        )
        self.api_status.pack(side=tk.RIGHT, padx=20, pady=10)

        # Settings Button
        settings_btn = tk.Button(
            top_bar,
            text="⚙️ Einstellungen",
            font=("SF Pro Text", 12),
            bg="white",
            fg=self.accent_color,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.open_settings
        )
        settings_btn.pack(side=tk.RIGHT, padx=10, pady=15)

    def create_sidebar(self, parent):
        """Create left sidebar with plugins and quick actions"""
        sidebar = tk.Frame(parent, bg=self.card_color, width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)

        # Plugins Section
        plugins_label = tk.Label(
            sidebar,
            text="📱 Apps & Plugins",
            font=("SF Pro Display", 16, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        plugins_label.pack(pady=(20, 10), padx=15, anchor=tk.W)

        # Plugin List with Toggle Switches
        self.plugin_frame = tk.Frame(sidebar, bg=self.card_color)
        self.plugin_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.create_plugin_controls()

        # Quick Actions
        separator = tk.Frame(sidebar, bg="#e5e5ea", height=1)
        separator.pack(fill=tk.X, padx=15, pady=10)

        quick_label = tk.Label(
            sidebar,
            text="⚡ Schnellaktionen",
            font=("SF Pro Display", 16, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        quick_label.pack(pady=(10, 10), padx=15, anchor=tk.W)

        # Quick Action Buttons
        quick_actions = [
            ("📧 Neue E-Mails", self.check_emails),
            ("💬 Neue Nachrichten", self.check_messages),
            ("📸 Fotos heute", lambda: self.search_photos_date(0)),
            ("🔍 Überall suchen", self.universal_search),
            ("⏰ Was tat ich vor...", self.time_travel),
        ]

        for text, command in quick_actions:
            btn = tk.Button(
                sidebar,
                text=text,
                font=("SF Pro Text", 12),
                bg=self.bg_color,
                fg=self.text_color,
                relief=tk.FLAT,
                anchor=tk.W,
                padx=15,
                pady=10,
                command=command
            )
            btn.pack(fill=tk.X, padx=15, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.accent_color, fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.bg_color, fg=self.text_color))

    def create_plugin_controls(self):
        """Create toggle controls for each plugin"""
        for widget in self.plugin_frame.winfo_children():
            widget.destroy()

        plugins = self.core.plugin_manager.get_all_plugins()

        for plugin in plugins:
            plugin_card = tk.Frame(self.plugin_frame, bg="#f9f9f9", relief=tk.FLAT)
            plugin_card.pack(fill=tk.X, pady=3, padx=5)

            # Plugin Icon and Name
            status_icon = "✓" if plugin.is_available() else "✗"
            color = self.success_color if plugin.is_available() else "#999"

            name_label = tk.Label(
                plugin_card,
                text=f"{status_icon} {plugin.name}",
                font=("SF Pro Text", 11),
                bg="#f9f9f9",
                fg=color,
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT, padx=10, pady=8)

            # Toggle Switch
            if plugin.is_available():
                toggle_var = tk.BooleanVar(value=plugin.enabled)
                toggle = tk.Checkbutton(
                    plugin_card,
                    text="",
                    variable=toggle_var,
                    bg="#f9f9f9",
                    command=lambda p=plugin, v=toggle_var: self.toggle_plugin(p, v.get())
                )
                toggle.pack(side=tk.RIGHT, padx=10)

    def create_center_panel(self, parent):
        """Create main center dashboard panel"""
        center = tk.Frame(parent, bg=self.bg_color)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Command Input Card
        self.create_command_card(center)

        # Dashboard Cards
        cards_container = tk.Frame(center, bg=self.bg_color)
        cards_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # Top Row: Stats Cards
        stats_row = tk.Frame(cards_container, bg=self.bg_color)
        stats_row.pack(fill=tk.X, pady=(0, 10))

        self.create_stat_card(stats_row, "📧 E-Mails", "0", "Ungelesen").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.create_stat_card(stats_row, "💬 Nachrichten", "0", "Neu").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.create_stat_card(stats_row, "📸 Fotos", "0", "Heute").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.create_stat_card(stats_row, "🎯 Tasks", "0", "Ausgeführt").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Main Content Area - Tabbed Interface
        self.create_tabbed_content(cards_container)

    def create_command_card(self, parent):
        """Create AI command input card"""
        card = tk.Frame(parent, bg=self.card_color, relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 10))

        # Title
        title = tk.Label(
            card,
            text="🤖 KI-Assistent - Was soll ich tun?",
            font=("SF Pro Display", 18, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        title.pack(pady=(15, 10), padx=20, anchor=tk.W)

        # Input Frame
        input_frame = tk.Frame(card, bg=self.card_color)
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.command_input = tk.Entry(
            input_frame,
            font=("SF Pro Text", 14),
            relief=tk.FLAT,
            bg="#f9f9f9",
            fg=self.text_color
        )
        self.command_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=10, padx=(0, 10))
        self.command_input.bind('<Return>', lambda e: self.execute_command())

        execute_btn = tk.Button(
            input_frame,
            text="▶ Ausführen",
            font=("SF Pro Text", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=10,
            command=self.execute_command
        )
        execute_btn.pack(side=tk.LEFT)

        # Examples
        examples = tk.Label(
            card,
            text='💡 Beispiele: "Sende E-Mail an max@example.com" • "Was habe ich gestern gemacht?" • "Suche Fotos vom Strand"',
            font=("SF Pro Text", 10),
            bg=self.card_color,
            fg="#666"
        )
        examples.pack(pady=(0, 15), padx=20, anchor=tk.W)

    def create_stat_card(self, parent, title, value, subtitle):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=self.card_color, relief=tk.FLAT)

        title_label = tk.Label(
            card,
            text=title,
            font=("SF Pro Text", 12),
            bg=self.card_color,
            fg="#666"
        )
        title_label.pack(pady=(15, 5))

        value_label = tk.Label(
            card,
            text=value,
            font=("SF Pro Display", 32, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        value_label.pack()

        subtitle_label = tk.Label(
            card,
            text=subtitle,
            font=("SF Pro Text", 11),
            bg=self.card_color,
            fg="#999"
        )
        subtitle_label.pack(pady=(0, 15))

        # Store reference for updates
        if "E-Mail" in title:
            self.email_count = value_label
        elif "Nachrichten" in title:
            self.message_count = value_label
        elif "Fotos" in title:
            self.photo_count = value_label
        elif "Tasks" in title:
            self.task_count = value_label

        return card

    def create_tabbed_content(self, parent):
        """Create tabbed content area"""
        tab_frame = tk.Frame(parent, bg=self.card_color)
        tab_frame.pack(fill=tk.BOTH, expand=True)

        # Tab Buttons
        tab_bar = tk.Frame(tab_frame, bg=self.card_color)
        tab_bar.pack(fill=tk.X, padx=20, pady=(15, 0))

        tabs = ["📋 Ergebnisse", "📧 E-Mails", "💬 Nachrichten", "📸 Fotos", "🎯 Tasks"]
        self.tab_buttons = []

        for i, tab_name in enumerate(tabs):
            btn = tk.Button(
                tab_bar,
                text=tab_name,
                font=("SF Pro Text", 12),
                bg=self.card_color,
                fg=self.text_color,
                relief=tk.FLAT,
                padx=20,
                pady=10,
                command=lambda idx=i: self.switch_tab(idx)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons.append(btn)

        # Tab Content
        self.tab_content = tk.Frame(tab_frame, bg=self.card_color)
        self.tab_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Results Display
        self.results_display = scrolledtext.ScrolledText(
            self.tab_content,
            wrap=tk.WORD,
            font=("SF Mono", 11),
            bg="#f9f9f9",
            fg=self.text_color,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.results_display.pack(fill=tk.BOTH, expand=True)

        # Select first tab
        self.switch_tab(0)

    def create_right_panel(self, parent):
        """Create right activity feed panel"""
        right = tk.Frame(parent, bg=self.card_color, width=300)
        right.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        right.pack_propagate(False)

        # Title
        title = tk.Label(
            right,
            text="📊 Aktivitäts-Feed",
            font=("SF Pro Display", 16, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        title.pack(pady=(20, 15), padx=15, anchor=tk.W)

        # Activity List
        self.activity_list = tk.Frame(right, bg=self.card_color)
        self.activity_list.pack(fill=tk.BOTH, expand=True, padx=10)

        # Refresh Button
        refresh_btn = tk.Button(
            right,
            text="🔄 Aktualisieren",
            font=("SF Pro Text", 11),
            bg=self.bg_color,
            fg=self.text_color,
            relief=tk.FLAT,
            pady=8,
            command=self.refresh_activity_feed
        )
        refresh_btn.pack(fill=tk.X, padx=15, pady=15)

    def create_status_bar(self):
        """Create bottom status bar"""
        self.status_bar = tk.Frame(self.root, bg="#e5e5ea", height=30)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        self.status_text = tk.Label(
            self.status_bar,
            text="● Bereit",
            font=("SF Pro Text", 10),
            bg="#e5e5ea",
            fg=self.text_color,
            anchor=tk.W
        )
        self.status_text.pack(side=tk.LEFT, padx=15)

        # Plugin Count
        plugin_count = len(self.core.plugin_manager.get_available_plugins())
        plugin_label = tk.Label(
            self.status_bar,
            text=f"🔌 {plugin_count} Plugins aktiv",
            font=("SF Pro Text", 10),
            bg="#e5e5ea",
            fg=self.text_color
        )
        plugin_label.pack(side=tk.RIGHT, padx=15)

    # Event Handlers

    def switch_tab(self, index):
        """Switch between tabs"""
        for i, btn in enumerate(self.tab_buttons):
            if i == index:
                btn.configure(bg=self.accent_color, fg="white")
            else:
                btn.configure(bg=self.card_color, fg=self.text_color)

    def execute_command(self):
        """Execute AI command"""
        command = self.command_input.get().strip()
        if not command:
            return

        self.status_text.configure(text="⏳ Verarbeite...")
        self.results_display.delete('1.0', tk.END)
        self.results_display.insert(tk.END, f"🙋 Du: {command}\n\n")

        threading.Thread(target=self._execute_command_thread, args=(command,), daemon=True).start()

    def _execute_command_thread(self, command):
        """Execute command in background"""
        try:
            result = self.core.process_user_query(command)
            self.results_display.insert(tk.END, f"🤖 Assistent:\n{result}\n")
            self.status_text.configure(text="● Bereit")
            self.command_input.delete(0, tk.END)
        except Exception as e:
            self.results_display.insert(tk.END, f"❌ Fehler: {str(e)}\n")
            self.status_text.configure(text="● Fehler aufgetreten")

    def toggle_plugin(self, plugin, enabled):
        """Toggle plugin on/off"""
        if enabled:
            plugin.enable()
        else:
            plugin.disable()
        self.status_text.configure(text=f"● {plugin.name} {'aktiviert' if enabled else 'deaktiviert'}")

    def open_settings(self):
        """Open settings dialog"""
        SettingsDialog(self.root, self.core)

    def check_emails(self):
        """Check for new emails"""
        self.status_text.configure(text="⏳ Prüfe E-Mails...")
        threading.Thread(target=self._check_emails_thread, daemon=True).start()

    def _check_emails_thread(self):
        """Check emails in background"""
        try:
            mail_plugin = self.core.get_plugin('Mail')
            if mail_plugin:
                emails = mail_plugin.get_unread_emails(10)
                self.results_display.delete('1.0', tk.END)
                self.results_display.insert(tk.END, f"📧 Neue E-Mails:\n\n{emails}\n")
                self.status_text.configure(text="● E-Mails geladen")
        except Exception as e:
            self.status_text.configure(text=f"● Fehler: {str(e)}")

    def check_messages(self):
        """Check for new messages"""
        self.status_text.configure(text="⏳ Prüfe Nachrichten...")
        self.results_display.delete('1.0', tk.END)
        self.results_display.insert(tk.END, "💬 Nachrichten werden geladen...\n")

    def search_photos_date(self, days_ago):
        """Search photos by date"""
        self.status_text.configure(text=f"⏳ Suche Fotos von vor {days_ago} Tagen...")

    def universal_search(self):
        """Open universal search dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Überall suchen")
        dialog.geometry("600x400")
        # Add search UI here

    def time_travel(self):
        """Open time travel dialog"""
        TimeTravelDialog(self.root, self.core)

    def refresh_activity_feed(self):
        """Refresh the activity feed"""
        for widget in self.activity_list.winfo_children():
            widget.destroy()

        # Add sample activities
        activities = [
            ("📧", "E-Mail gesendet", "vor 5 Min"),
            ("💬", "Slack-Nachricht", "vor 12 Min"),
            ("📸", "Foto gelöscht", "vor 1 Std"),
        ]

        for icon, text, time in activities:
            item = tk.Frame(self.activity_list, bg="#f9f9f9")
            item.pack(fill=tk.X, pady=2, padx=5)

            tk.Label(item, text=icon, bg="#f9f9f9", font=("SF Pro Text", 14)).pack(side=tk.LEFT, padx=5, pady=8)
            tk.Label(item, text=text, bg="#f9f9f9", font=("SF Pro Text", 11), anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(item, text=time, bg="#f9f9f9", font=("SF Pro Text", 9), fg="#999").pack(side=tk.RIGHT, padx=5)

    def load_initial_data(self):
        """Load initial dashboard data"""
        self.refresh_activity_feed()

    def run(self):
        """Start the GUI"""
        self.root.mainloop()


class SettingsDialog:
    """Settings dialog window"""
    def __init__(self, parent, core):
        self.core = core
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg="#f5f5f7")

        # Title
        title = tk.Label(
            self.dialog,
            text="⚙️ Einstellungen",
            font=("SF Pro Display", 24, "bold"),
            bg="#f5f5f7"
        )
        title.pack(pady=20)

        # API Key Section
        api_frame = tk.LabelFrame(
            self.dialog,
            text="Anthropic API Key",
            font=("SF Pro Text", 14),
            bg="white",
            padx=20,
            pady=15
        )
        api_frame.pack(fill=tk.X, padx=20, pady=10)

        self.api_entry = tk.Entry(api_frame, font=("SF Mono", 11), show="*", width=50)
        self.api_entry.pack(pady=5)

        if self.core.ai and self.core.ai.api_key:
            self.api_entry.insert(0, self.core.ai.api_key)

        save_btn = tk.Button(
            api_frame,
            text="💾 API Key speichern",
            font=("SF Pro Text", 12),
            bg="#007AFF",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.save_api_key
        )
        save_btn.pack(pady=5)

        # Close Button
        close_btn = tk.Button(
            self.dialog,
            text="Schließen",
            font=("SF Pro Text", 12),
            bg="#f5f5f7",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.dialog.destroy
        )
        close_btn.pack(pady=20)

    def save_api_key(self):
        """Save API key"""
        key = self.api_entry.get()
        if key:
            os.environ['ANTHROPIC_API_KEY'] = key
            messagebox.showinfo("Erfolg", "API Key gespeichert! Bitte App neu starten.")


class TimeTravelDialog:
    """Time travel dialog window"""
    def __init__(self, parent, core):
        self.core = core
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Zeitreise - Was habe ich gemacht?")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg="#f5f5f7")

        # Title
        title = tk.Label(
            self.dialog,
            text="⏰ Zeitreise",
            font=("SF Pro Display", 24, "bold"),
            bg="#f5f5f7"
        )
        title.pack(pady=20)

        # Input Frame
        input_frame = tk.Frame(self.dialog, bg="white")
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(input_frame, text="Vor wie vielen Tagen?", font=("SF Pro Text", 12), bg="white").pack(pady=5)

        self.days_var = tk.IntVar(value=0)
        days_spin = tk.Spinbox(input_frame, from_=0, to=30, textvariable=self.days_var, font=("SF Pro Text", 14), width=10)
        days_spin.pack(pady=5)

        tk.Label(input_frame, text="Um welche Uhrzeit? (optional)", font=("SF Pro Text", 12), bg="white").pack(pady=5)

        self.hour_var = tk.IntVar(value=-1)
        hour_spin = tk.Spinbox(input_frame, from_=-1, to=23, textvariable=self.hour_var, font=("SF Pro Text", 14), width=10)
        hour_spin.pack(pady=5)

        search_btn = tk.Button(
            input_frame,
            text="🔍 Suchen",
            font=("SF Pro Text", 14, "bold"),
            bg="#007AFF",
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.search_activities
        )
        search_btn.pack(pady=15)

        # Results
        self.results = scrolledtext.ScrolledText(
            self.dialog,
            wrap=tk.WORD,
            font=("SF Mono", 11),
            bg="white"
        )
        self.results.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def search_activities(self):
        """Search for activities"""
        days = self.days_var.get()
        hour = self.hour_var.get() if self.hour_var.get() >= 0 else None

        activities = self.core.get_activities_at_time(days_ago=days, hour=hour)

        self.results.delete('1.0', tk.END)

        if activities:
            self.results.insert(tk.END, f"✓ {len(activities)} Aktivitäten gefunden:\n\n")
            for act in activities[:20]:
                self.results.insert(tk.END, f"{act}\n")
        else:
            self.results.insert(tk.END, "Keine Aktivitäten gefunden.")
