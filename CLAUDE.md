# Old CRM Updated - Regeln

## Sprache

- Antworte auf **Deutsch**
- Code-Kommentare auf **Englisch**

---

## Projekt-Typ

- **Flask** Web-Applikation
- **Python 3.10+**
- **SQLAlchemy** für Datenbank

---

## Coding Standards

### Python

- PEP 8 befolgen
- Type Hints verwenden
- Docstrings für alle Funktionen

### Namenskonventionen

| Element              | Convention           | Beispiel         |
| -------------------- | -------------------- | ---------------- |
| Variablen/Funktionen | snake_case           | `get_user_by_id` |
| Klassen              | PascalCase           | `UserModel`      |
| Konstanten           | SCREAMING_SNAKE_CASE | `MAX_RETRIES`    |

---

## 🧪 TEST-AUTOMATISIERUNG (PFLICHT)

### UI Test-IDs (PFLICHT für alle Templates)

```html
<!-- Jinja2 Templates -->
<button id="login_button_submit">Login</button>
<input id="login_input_email" name="email" />
<div id="dashboard_card_stats"></div>
```

**Naming Convention:** `screenName_elementType_beschreibung`

### Test-Typen

| Typ              | Wann                  | Beispiel             |
| ---------------- | --------------------- | -------------------- |
| Unit Test        | Jede Utility-Funktion | `test_models.py`     |
| Integration Test | Jede Route            | `test_routes.py`     |
| E2E Test         | Kritische Flows       | `test_login_flow.py` |

### Vor jedem Commit - Checkliste

- [ ] Alle neuen UI-Elemente haben IDs
- [ ] Alle neuen Funktionen haben Tests
- [ ] Alle Tests laufen durch (`pytest tests/`)
- [ ] Keine Syntax-Fehler

### Test-Befehle

```bash
# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Einzelnen Test
pytest tests/test_models.py -v
```

### CI/CD Integration

- Tests laufen automatisch bei Push auf `main/develop`
- Tests laufen bei Pull Requests
- Tägliche Tests um 6:00 UTC
- CI muss grün sein vor Merge

---

## Sicherheit

- [ ] Input-Validierung für alle Formulare
- [ ] CSRF-Protection aktiviert (Flask-WTF)
- [ ] SQL-Injection Prevention (SQLAlchemy)
- [ ] Secrets niemals im Code

### Verbotene Dateien

```
.env
.env.local
secrets/
*.pem
*.key
```

---

## Git-Workflow

### ❌ VERBOTEN

1. Direkt auf `main` pushen
2. Force push
3. Hooks überspringen

### ✅ PFLICHT

1. Feature-Branch erstellen
2. Tests bestehen
3. Pull Request erstellen
4. Review abwarten
