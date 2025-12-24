"""
Contact Import/Export Module
Unterstützt CSV, JSON, Excel und API-Import
"""

import csv
import json
from datetime import datetime
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, asdict
from pathlib import Path
import io


@dataclass
class Contact:
    """Kontakt-Datenstruktur."""
    id: Optional[str] = None
    name: str = ''
    phone: str = ''
    email: str = ''
    company: str = ''
    language: str = 'de'  # de, bs, sr
    notes: str = ''
    tags: List[str] = None
    priority: int = 5  # 1-10, 1 = höchste
    status: str = 'pending'  # pending, called, completed, failed
    last_called: Optional[str] = None
    call_count: int = 0
    custom_data: Dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_data is None:
            self.custom_data = {}

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Contact':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ContactImporter:
    """
    Importiert Kontakte aus verschiedenen Quellen.

    Unterstützte Formate:
    - CSV
    - JSON
    - Excel (XLSX)
    - Dict/List
    """

    # Standard-Spalten-Mapping
    DEFAULT_MAPPING = {
        'name': ['name', 'Name', 'NAME', 'full_name', 'fullname', 'Kunde', 'kunde'],
        'phone': ['phone', 'Phone', 'PHONE', 'telefon', 'Telefon', 'tel', 'mobile', 'Handy'],
        'email': ['email', 'Email', 'EMAIL', 'e-mail', 'E-Mail', 'mail'],
        'company': ['company', 'Company', 'COMPANY', 'firma', 'Firma', 'unternehmen'],
        'language': ['language', 'Language', 'sprache', 'Sprache', 'lang'],
        'notes': ['notes', 'Notes', 'notizen', 'Notizen', 'bemerkung', 'Bemerkung'],
        'priority': ['priority', 'Priority', 'priorität', 'Priorität', 'prio'],
    }

    def __init__(self, column_mapping: Dict[str, List[str]] = None):
        self.mapping = column_mapping or self.DEFAULT_MAPPING
        self.errors = []
        self.imported_count = 0
        self.skipped_count = 0

    def import_csv(self, filepath: str, delimiter: str = ',',
                  encoding: str = 'utf-8') -> List[Contact]:
        """Importiert Kontakte aus CSV-Datei."""
        contacts = []

        with open(filepath, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            for row_num, row in enumerate(reader, start=2):
                try:
                    contact = self._row_to_contact(row)
                    if contact:
                        contacts.append(contact)
                        self.imported_count += 1
                    else:
                        self.skipped_count += 1
                except Exception as e:
                    self.errors.append(f"Zeile {row_num}: {str(e)}")
                    self.skipped_count += 1

        return contacts

    def import_csv_string(self, csv_content: str, delimiter: str = ',') -> List[Contact]:
        """Importiert Kontakte aus CSV-String."""
        contacts = []
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)

        for row_num, row in enumerate(reader, start=2):
            try:
                contact = self._row_to_contact(row)
                if contact:
                    contacts.append(contact)
                    self.imported_count += 1
            except Exception as e:
                self.errors.append(f"Zeile {row_num}: {str(e)}")
                self.skipped_count += 1

        return contacts

    def import_json(self, filepath: str) -> List[Contact]:
        """Importiert Kontakte aus JSON-Datei."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return [Contact.from_dict(item) for item in data]
        elif isinstance(data, dict) and 'contacts' in data:
            return [Contact.from_dict(item) for item in data['contacts']]
        else:
            raise ValueError("Ungültiges JSON-Format")

    def import_json_string(self, json_content: str) -> List[Contact]:
        """Importiert Kontakte aus JSON-String."""
        data = json.loads(json_content)
        if isinstance(data, list):
            return [Contact.from_dict(item) for item in data]
        return []

    def import_dict_list(self, data: List[Dict]) -> List[Contact]:
        """Importiert Kontakte aus Liste von Dictionaries."""
        contacts = []
        for item in data:
            contact = self._row_to_contact(item)
            if contact:
                contacts.append(contact)
        return contacts

    def import_from_api(self, api_url: str, headers: Dict = None,
                       contacts_key: str = 'data') -> List[Contact]:
        """Importiert Kontakte von einer API."""
        import requests

        response = requests.get(api_url, headers=headers or {})
        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get(contacts_key, [])
        else:
            raise ValueError("Ungültige API-Antwort")

        return self.import_dict_list(items)

    def _row_to_contact(self, row: Dict) -> Optional[Contact]:
        """Konvertiert eine Zeile zu einem Contact-Objekt."""
        # Finde Telefonnummer (Pflichtfeld)
        phone = self._find_value(row, 'phone')
        if not phone:
            return None

        # Bereinige Telefonnummer
        phone = self._clean_phone(phone)
        if not phone:
            return None

        # Extrahiere andere Felder
        name = self._find_value(row, 'name') or 'Unbekannt'
        email = self._find_value(row, 'email') or ''
        company = self._find_value(row, 'company') or ''
        language = self._find_value(row, 'language') or 'de'
        notes = self._find_value(row, 'notes') or ''
        priority = self._find_value(row, 'priority')

        # Konvertiere Priorität
        try:
            priority = int(priority) if priority else 5
            priority = max(1, min(10, priority))
        except (ValueError, TypeError):
            priority = 5

        # Validiere Sprache
        if language not in ['de', 'bs', 'sr', 'en']:
            language = 'de'

        return Contact(
            name=name,
            phone=phone,
            email=email,
            company=company,
            language=language,
            notes=notes,
            priority=priority
        )

    def _find_value(self, row: Dict, field: str) -> Optional[str]:
        """Findet Wert basierend auf Spalten-Mapping."""
        possible_names = self.mapping.get(field, [field])
        for name in possible_names:
            if name in row and row[name]:
                return str(row[name]).strip()
        return None

    def _clean_phone(self, phone: str) -> Optional[str]:
        """Bereinigt und validiert Telefonnummer."""
        # Entferne Leerzeichen und Sonderzeichen (außer +)
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Mindestlänge prüfen
        if len(cleaned) < 8:
            return None

        # Füge + hinzu wenn mit 00 beginnend
        if cleaned.startswith('00'):
            cleaned = '+' + cleaned[2:]
        elif not cleaned.startswith('+'):
            # Annahme: Deutsche Nummer
            if cleaned.startswith('0'):
                cleaned = '+49' + cleaned[1:]
            else:
                cleaned = '+49' + cleaned

        return cleaned

    def get_stats(self) -> Dict:
        """Gibt Import-Statistiken zurück."""
        return {
            'imported': self.imported_count,
            'skipped': self.skipped_count,
            'errors': len(self.errors),
            'error_details': self.errors[:10]  # Nur erste 10 Fehler
        }


class ContactExporter:
    """
    Exportiert Kontakte in verschiedene Formate.

    Unterstützte Formate:
    - CSV
    - JSON
    - Excel (XLSX) - benötigt openpyxl
    """

    def __init__(self, contacts: List[Contact]):
        self.contacts = contacts

    def to_csv(self, filepath: str = None, include_stats: bool = False) -> str:
        """Exportiert zu CSV."""
        output = io.StringIO()
        fieldnames = ['name', 'phone', 'email', 'company', 'language',
                     'priority', 'status', 'notes', 'call_count', 'last_called']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for contact in self.contacts:
            row = {k: getattr(contact, k, '') for k in fieldnames}
            writer.writerow(row)

        csv_content = output.getvalue()

        if filepath:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_content)

        return csv_content

    def to_json(self, filepath: str = None, pretty: bool = True) -> str:
        """Exportiert zu JSON."""
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_contacts': len(self.contacts),
            'contacts': [c.to_dict() for c in self.contacts]
        }

        json_content = json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_content)

        return json_content

    def to_dict_list(self) -> List[Dict]:
        """Exportiert zu Liste von Dictionaries."""
        return [c.to_dict() for c in self.contacts]

    def filter_by_status(self, status: str) -> 'ContactExporter':
        """Filtert Kontakte nach Status."""
        filtered = [c for c in self.contacts if c.status == status]
        return ContactExporter(filtered)

    def filter_by_language(self, language: str) -> 'ContactExporter':
        """Filtert Kontakte nach Sprache."""
        filtered = [c for c in self.contacts if c.language == language]
        return ContactExporter(filtered)

    def sort_by_priority(self, ascending: bool = True) -> 'ContactExporter':
        """Sortiert Kontakte nach Priorität."""
        sorted_contacts = sorted(self.contacts, key=lambda c: c.priority,
                                reverse=not ascending)
        return ContactExporter(sorted_contacts)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def import_contacts(source: str, format: str = 'auto') -> List[Contact]:
    """
    Einfache Funktion zum Importieren von Kontakten.

    Args:
        source: Dateipfad, URL oder String-Inhalt
        format: 'csv', 'json', 'api' oder 'auto' (automatische Erkennung)

    Returns:
        Liste von Contact-Objekten
    """
    importer = ContactImporter()

    if format == 'auto':
        if source.startswith('http'):
            format = 'api'
        elif source.endswith('.csv'):
            format = 'csv'
        elif source.endswith('.json'):
            format = 'json'
        else:
            # Versuche als String zu parsen
            if source.strip().startswith('[') or source.strip().startswith('{'):
                format = 'json_string'
            else:
                format = 'csv_string'

    if format == 'csv':
        return importer.import_csv(source)
    elif format == 'json':
        return importer.import_json(source)
    elif format == 'api':
        return importer.import_from_api(source)
    elif format == 'csv_string':
        return importer.import_csv_string(source)
    elif format == 'json_string':
        return importer.import_json_string(source)
    else:
        raise ValueError(f"Unbekanntes Format: {format}")


def export_contacts(contacts: List[Contact], filepath: str,
                   format: str = 'auto') -> str:
    """
    Einfache Funktion zum Exportieren von Kontakten.

    Args:
        contacts: Liste von Contact-Objekten
        filepath: Zieldateipfad
        format: 'csv', 'json' oder 'auto'

    Returns:
        Exportierter Inhalt als String
    """
    exporter = ContactExporter(contacts)

    if format == 'auto':
        if filepath.endswith('.json'):
            format = 'json'
        else:
            format = 'csv'

    if format == 'csv':
        return exporter.to_csv(filepath)
    elif format == 'json':
        return exporter.to_json(filepath)
    else:
        raise ValueError(f"Unbekanntes Format: {format}")
