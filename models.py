from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Customer(db.Model):
    """Customer model for CRM."""

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100), index=True)
    status = db.Column(db.String(20), default='active', index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    interactions = db.relationship(
        'Interaction',
        backref='customer',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        """Convert customer to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Interaction(db.Model):
    """Interaction/activity log for customers."""

    __tablename__ = 'interactions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    type = db.Column(db.String(50), nullable=False)  # call, email, meeting, note
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert interaction to dictionary."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'type': self.type,
            'subject': self.subject,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
