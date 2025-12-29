"""Tests for database models."""
import pytest
from models import db, Customer, Interaction


class TestCustomerModel:
    """Tests for Customer model."""

    def test_create_customer(self, app):
        """Test customer creation."""
        with app.app_context():
            customer = Customer(
                name='John Doe',
                email='john@example.com',
                phone='555-1234',
                company='ACME Inc',
                status='active'
            )
            db.session.add(customer)
            db.session.commit()

            assert customer.id is not None
            assert customer.name == 'John Doe'
            assert customer.email == 'john@example.com'
            assert customer.created_at is not None

    def test_customer_to_dict(self, app, sample_customer):
        """Test customer to_dict method."""
        with app.app_context():
            customer = db.session.get(Customer, sample_customer)
            data = customer.to_dict()

            assert data['name'] == 'Test Customer'
            assert data['email'] == 'test@example.com'
            assert 'id' in data
            assert 'created_at' in data

    def test_customer_unique_email(self, app):
        """Test that email must be unique."""
        with app.app_context():
            customer1 = Customer(name='User 1', email='same@example.com')
            db.session.add(customer1)
            db.session.commit()

            customer2 = Customer(name='User 2', email='same@example.com')
            db.session.add(customer2)

            with pytest.raises(Exception):
                db.session.commit()

    def test_customer_status_default(self, app):
        """Test default status value."""
        with app.app_context():
            customer = Customer(name='Test', email='test2@example.com')
            db.session.add(customer)
            db.session.commit()

            assert customer.status == 'active'


class TestInteractionModel:
    """Tests for Interaction model."""

    def test_create_interaction(self, app, sample_customer):
        """Test interaction creation."""
        with app.app_context():
            interaction = Interaction(
                customer_id=sample_customer,
                type='email',
                subject='Follow up',
                description='Sent follow up email'
            )
            db.session.add(interaction)
            db.session.commit()

            assert interaction.id is not None
            assert interaction.type == 'email'
            assert interaction.created_at is not None

    def test_interaction_to_dict(self, app, sample_interaction):
        """Test interaction to_dict method."""
        with app.app_context():
            interaction = db.session.get(Interaction, sample_interaction)
            data = interaction.to_dict()

            assert data['type'] == 'call'
            assert data['subject'] == 'Test Call'
            assert 'id' in data

    def test_interaction_customer_relationship(self, app, sample_customer):
        """Test interaction-customer relationship."""
        with app.app_context():
            customer = db.session.get(Customer, sample_customer)
            interaction = Interaction(
                customer_id=sample_customer,
                type='meeting',
                subject='Meeting'
            )
            db.session.add(interaction)
            db.session.commit()

            assert interaction.customer == customer
            assert interaction in customer.interactions.all()

    def test_cascade_delete(self, app, sample_customer, sample_interaction):
        """Test that interactions are deleted when customer is deleted."""
        with app.app_context():
            customer = db.session.get(Customer, sample_customer)
            db.session.delete(customer)
            db.session.commit()

            interaction = db.session.get(Interaction, sample_interaction)
            assert interaction is None
