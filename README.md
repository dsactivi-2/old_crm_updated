# CRM System

A simple Customer Relationship Management system built with Flask.

## Features

- Customer management (CRUD)
- Interaction logging (calls, emails, meetings, notes)
- Search and filtering
- REST API endpoints
- Responsive design

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## API Endpoints

- `GET /api/customers` - List all customers
- `GET /api/customers/<id>` - Get customer details
- `POST /api/customers` - Create customer

## Configuration

Set environment variables:
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string (default: SQLite)
