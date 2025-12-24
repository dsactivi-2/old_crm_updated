from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional

from config import Config
from models import db, Customer, Interaction


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


class CustomerForm(FlaskForm):
    """Form for customer creation/editing."""

    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    status = SelectField(
        'Status',
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('lead', 'Lead')],
        default='active'
    )
    notes = TextAreaField('Notes', validators=[Optional()])


class InteractionForm(FlaskForm):
    """Form for interaction logging."""

    type = SelectField(
        'Type',
        choices=[
            ('call', 'Phone Call'),
            ('email', 'Email'),
            ('meeting', 'Meeting'),
            ('note', 'Note')
        ]
    )
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])


def register_routes(app):
    """Register application routes."""

    @app.route('/')
    def index():
        """Dashboard with customer overview."""
        stats = {
            'total': Customer.query.count(),
            'active': Customer.query.filter_by(status='active').count(),
            'leads': Customer.query.filter_by(status='lead').count(),
            'recent_interactions': Interaction.query.order_by(
                Interaction.created_at.desc()
            ).limit(5).all()
        }
        return render_template('index.html', stats=stats)

    @app.route('/customers')
    def customer_list():
        """List all customers with search and filter."""
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '')
        page = request.args.get('page', 1, type=int)
        per_page = 10

        query = Customer.query

        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Customer.name.ilike(search_filter),
                    Customer.email.ilike(search_filter),
                    Customer.company.ilike(search_filter)
                )
            )

        if status:
            query = query.filter_by(status=status)

        pagination = query.order_by(Customer.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return render_template(
            'customers/list.html',
            customers=pagination.items,
            pagination=pagination,
            search=search,
            status=status
        )

    @app.route('/customers/new', methods=['GET', 'POST'])
    def customer_create():
        """Create new customer."""
        form = CustomerForm()

        if form.validate_on_submit():
            existing = Customer.query.filter_by(email=form.email.data).first()
            if existing:
                flash('A customer with this email already exists.', 'error')
                return render_template('customers/form.html', form=form, title='New Customer')

            customer = Customer(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                company=form.company.data,
                status=form.status.data,
                notes=form.notes.data
            )
            db.session.add(customer)
            db.session.commit()
            flash('Customer created successfully.', 'success')
            return redirect(url_for('customer_detail', id=customer.id))

        return render_template('customers/form.html', form=form, title='New Customer')

    @app.route('/customers/<int:id>')
    def customer_detail(id):
        """View customer details."""
        customer = Customer.query.get_or_404(id)
        interactions = customer.interactions.order_by(
            Interaction.created_at.desc()
        ).limit(10).all()
        return render_template(
            'customers/detail.html',
            customer=customer,
            interactions=interactions
        )

    @app.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
    def customer_edit(id):
        """Edit customer."""
        customer = Customer.query.get_or_404(id)
        form = CustomerForm(obj=customer)

        if form.validate_on_submit():
            existing = Customer.query.filter(
                Customer.email == form.email.data,
                Customer.id != id
            ).first()
            if existing:
                flash('A customer with this email already exists.', 'error')
                return render_template(
                    'customers/form.html',
                    form=form,
                    title='Edit Customer',
                    customer=customer
                )

            form.populate_obj(customer)
            db.session.commit()
            flash('Customer updated successfully.', 'success')
            return redirect(url_for('customer_detail', id=customer.id))

        return render_template(
            'customers/form.html',
            form=form,
            title='Edit Customer',
            customer=customer
        )

    @app.route('/customers/<int:id>/delete', methods=['POST'])
    def customer_delete(id):
        """Delete customer."""
        customer = Customer.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully.', 'success')
        return redirect(url_for('customer_list'))

    @app.route('/customers/<int:id>/interactions', methods=['POST'])
    def add_interaction(id):
        """Add interaction to customer."""
        customer = Customer.query.get_or_404(id)
        form = InteractionForm()

        if form.validate_on_submit():
            interaction = Interaction(
                customer_id=customer.id,
                type=form.type.data,
                subject=form.subject.data,
                description=form.description.data
            )
            db.session.add(interaction)
            db.session.commit()
            flash('Interaction logged successfully.', 'success')

        return redirect(url_for('customer_detail', id=customer.id))

    # API endpoints
    @app.route('/api/customers')
    def api_customers():
        """API: Get all customers."""
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        return jsonify([c.to_dict() for c in customers])

    @app.route('/api/customers/<int:id>')
    def api_customer_detail(id):
        """API: Get customer details."""
        customer = Customer.query.get_or_404(id)
        data = customer.to_dict()
        data['interactions'] = [i.to_dict() for i in customer.interactions.all()]
        return jsonify(data)

    @app.route('/api/customers', methods=['POST'])
    def api_customer_create():
        """API: Create customer."""
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required = ['name', 'email']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

        existing = Customer.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Email already exists'}), 409

        customer = Customer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            company=data.get('company'),
            status=data.get('status', 'active'),
            notes=data.get('notes')
        )
        db.session.add(customer)
        db.session.commit()

        return jsonify(customer.to_dict()), 201

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
