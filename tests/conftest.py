"""Pytest configuration and fixtures."""
import pytest
from app import create_app
from models import db, Customer, Interaction


class TestConfig:
    """Test configuration."""
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    TESTING = True


@pytest.fixture
def app():
    """Create application for testing."""
    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_customer(app):
    """Create a sample customer for testing."""
    with app.app_context():
        customer = Customer(
            name='Test Customer',
            email='test@example.com',
            phone='123-456-7890',
            company='Test Company',
            status='active',
            notes='Test notes'
        )
        db.session.add(customer)
        db.session.commit()

        # Return customer id to fetch fresh instance
        customer_id = customer.id

    return customer_id


@pytest.fixture
def sample_interaction(app, sample_customer):
    """Create a sample interaction for testing."""
    with app.app_context():
        interaction = Interaction(
            customer_id=sample_customer,
            type='call',
            subject='Test Call',
            description='Test call description'
        )
        db.session.add(interaction)
        db.session.commit()

        interaction_id = interaction.id

    return interaction_id
