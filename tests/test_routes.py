"""Tests for Flask routes."""
import pytest
from models import db, Customer


class TestIndexRoutes:
    """Tests for index/home routes."""

    def test_index_page(self, client):
        """Test index page loads."""
        response = client.get('/')
        assert response.status_code == 200

    def test_customers_list_page(self, client):
        """Test customers list page."""
        response = client.get('/customers')
        assert response.status_code == 200


class TestCustomerAPI:
    """Tests for Customer API endpoints."""

    def test_get_customers_empty(self, client):
        """Test getting customers when empty."""
        response = client.get('/api/customers')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_customers_with_data(self, client, sample_customer):
        """Test getting customers with data."""
        response = client.get('/api/customers')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Test Customer'

    def test_get_single_customer(self, client, sample_customer):
        """Test getting a single customer."""
        response = client.get(f'/api/customers/{sample_customer}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Test Customer'
        assert data['email'] == 'test@example.com'

    def test_get_nonexistent_customer(self, client):
        """Test getting a customer that doesn't exist."""
        response = client.get('/api/customers/9999')
        assert response.status_code == 404

    def test_create_customer(self, client, app):
        """Test creating a new customer."""
        response = client.post('/api/customers', json={
            'name': 'New Customer',
            'email': 'new@example.com',
            'phone': '555-0000',
            'company': 'New Corp',
            'status': 'lead'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Customer'

        # Verify in database
        with app.app_context():
            customer = Customer.query.filter_by(email='new@example.com').first()
            assert customer is not None

    def test_create_customer_missing_fields(self, client):
        """Test creating customer with missing required fields."""
        response = client.post('/api/customers', json={
            'name': 'No Email Customer'
        })
        assert response.status_code == 400

    def test_update_customer(self, client, sample_customer, app):
        """Test updating a customer."""
        response = client.put(f'/api/customers/{sample_customer}', json={
            'name': 'Updated Name',
            'email': 'updated@example.com'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Name'

    def test_delete_customer(self, client, sample_customer, app):
        """Test deleting a customer."""
        response = client.delete(f'/api/customers/{sample_customer}')
        assert response.status_code == 200

        # Verify deleted
        with app.app_context():
            customer = db.session.get(Customer, sample_customer)
            assert customer is None
