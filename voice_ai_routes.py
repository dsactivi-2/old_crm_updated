"""
Voice AI Sales Agent - API Routes für CRM Integration
Webhooks für Vapi.ai, Retell.ai, Bland.ai
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, Length
from datetime import datetime, timezone
from functools import wraps
import hmac
import hashlib
import os

from models import db, Customer
from voice_ai_models import VoiceAgent, CallSession, CallQueue, LeadScore
from voice_ai_service import VoiceAIService, SYSTEM_PROMPTS


# Blueprint erstellen
voice_ai_bp = Blueprint('voice_ai', __name__, url_prefix='/voice-ai')
voice_api_bp = Blueprint('voice_api', __name__, url_prefix='/api/voice')


# =============================================================================
# FORMS
# =============================================================================

class VoiceAgentForm(FlaskForm):
    """Form für Voice Agent Konfiguration."""

    name = StringField('Agent Name', validators=[DataRequired(), Length(max=100)])
    provider = SelectField('Provider', choices=[
        ('vapi', 'Vapi.ai (Empfohlen)'),
        ('retell', 'Retell.ai (Schnellste Latenz)'),
        ('bland', 'Bland.ai (Sales-fokussiert)')
    ])
    api_key = StringField('API Key', validators=[Optional(), Length(max=500)])

    primary_language = SelectField('Hauptsprache', choices=[
        ('de', 'Deutsch'),
        ('bs', 'Bosnisch'),
        ('sr', 'Serbisch')
    ])

    tts_provider = SelectField('Text-to-Speech', choices=[
        ('elevenlabs', 'ElevenLabs (Beste Qualität)'),
        ('azure', 'Azure Neural (Alle Sprachen)'),
        ('playht', 'PlayHT'),
        ('openai', 'OpenAI TTS')
    ])
    tts_voice_id = StringField('Voice ID', validators=[Optional()])

    stt_provider = SelectField('Speech-to-Text', choices=[
        ('deepgram', 'Deepgram (Schnellste)'),
        ('azure', 'Azure Speech'),
        ('google', 'Google STT'),
        ('whisper', 'OpenAI Whisper')
    ])

    llm_provider = SelectField('LLM Provider', choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('groq', 'Groq (Llama)')
    ])
    llm_model = SelectField('LLM Model', choices=[
        ('gpt-4o-mini', 'GPT-4o-mini (Schnell & Günstig)'),
        ('gpt-4o', 'GPT-4o (Beste Qualität)'),
        ('claude-3-haiku-20240307', 'Claude 3 Haiku'),
        ('llama-3.1-70b-versatile', 'Llama 3.1 70B')
    ])

    phone_number = StringField('Telefonnummer', validators=[Optional(), Length(max=20)])
    telephony_provider = SelectField('Telefonie', choices=[
        ('twilio', 'Twilio'),
        ('vonage', 'Vonage'),
        ('plivo', 'Plivo')
    ])

    system_prompt = TextAreaField('System Prompt (Sales Script)', validators=[Optional()])
    is_active = BooleanField('Aktiv', default=True)


# =============================================================================
# API KEY AUTHENTICATION
# =============================================================================

def require_api_key(f):
    """Decorator für API-Key Authentifizierung."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('VOICE_AI_API_KEY')

        if expected_key and api_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated


def verify_webhook_signature(provider: str, payload: bytes, signature: str) -> bool:
    """Verifiziert Webhook-Signatur."""
    secret = os.environ.get(f'{provider.upper()}_WEBHOOK_SECRET', '')
    if not secret:
        return True  # Keine Signatur-Verifizierung konfiguriert

    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


# =============================================================================
# WEB UI ROUTES
# =============================================================================

@voice_ai_bp.route('/')
def dashboard():
    """Voice AI Dashboard."""
    agents = VoiceAgent.query.filter_by(is_active=True).all()

    # Statistiken
    stats = {
        'total_agents': VoiceAgent.query.count(),
        'active_agents': VoiceAgent.query.filter_by(is_active=True).count(),
        'total_calls': CallSession.query.count(),
        'calls_today': CallSession.query.filter(
            CallSession.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        ).count(),
        'avg_duration': db.session.query(db.func.avg(CallSession.duration_seconds)).scalar() or 0,
        'queue_pending': CallQueue.query.filter_by(status='pending').count()
    }

    recent_calls = CallSession.query.order_by(
        CallSession.created_at.desc()
    ).limit(10).all()

    return render_template('voice_ai/dashboard.html',
                          agents=agents,
                          stats=stats,
                          recent_calls=recent_calls)


@voice_ai_bp.route('/agents')
def agent_list():
    """Liste aller Voice Agents."""
    agents = VoiceAgent.query.order_by(VoiceAgent.created_at.desc()).all()
    return render_template('voice_ai/agents.html', agents=agents)


@voice_ai_bp.route('/agents/new', methods=['GET', 'POST'])
def agent_create():
    """Neuen Voice Agent erstellen."""
    form = VoiceAgentForm()

    if form.validate_on_submit():
        service = VoiceAIService(db.session)

        agent_data = {
            'name': form.name.data,
            'provider': form.provider.data,
            'api_key': form.api_key.data,
            'primary_language': form.primary_language.data,
            'tts_provider': form.tts_provider.data,
            'tts_voice_id': form.tts_voice_id.data,
            'stt_provider': form.stt_provider.data,
            'llm_provider': form.llm_provider.data,
            'llm_model': form.llm_model.data,
            'phone_number': form.phone_number.data,
            'telephony_provider': form.telephony_provider.data,
            'system_prompt': form.system_prompt.data,
            'supported_languages': ['de', 'bs', 'sr']
        }

        try:
            agent = service.create_agent(agent_data)
            flash(f'Agent "{agent.name}" erfolgreich erstellt!', 'success')
            return redirect(url_for('voice_ai.agent_detail', id=agent.id))
        except Exception as e:
            flash(f'Fehler beim Erstellen: {str(e)}', 'error')

    # Default System Prompt setzen
    if not form.system_prompt.data:
        form.system_prompt.data = SYSTEM_PROMPTS['de']

    return render_template('voice_ai/agent_form.html', form=form, title='Neuer Agent')


@voice_ai_bp.route('/agents/<int:id>')
def agent_detail(id):
    """Agent Details und Statistiken."""
    agent = VoiceAgent.query.get_or_404(id)

    stats = {
        'total_calls': agent.call_sessions.count(),
        'avg_duration': db.session.query(
            db.func.avg(CallSession.duration_seconds)
        ).filter(CallSession.agent_id == id).scalar() or 0,
        'positive_calls': agent.call_sessions.filter_by(sentiment='positive').count(),
        'appointments': agent.call_sessions.filter(
            CallSession.outcome == 'appointment'
        ).count()
    }

    recent_calls = agent.call_sessions.order_by(
        CallSession.created_at.desc()
    ).limit(20).all()

    return render_template('voice_ai/agent_detail.html',
                          agent=agent,
                          stats=stats,
                          recent_calls=recent_calls)


@voice_ai_bp.route('/agents/<int:id>/edit', methods=['GET', 'POST'])
def agent_edit(id):
    """Agent bearbeiten."""
    agent = VoiceAgent.query.get_or_404(id)
    form = VoiceAgentForm(obj=agent)

    if form.validate_on_submit():
        form.populate_obj(agent)
        db.session.commit()
        flash('Agent erfolgreich aktualisiert!', 'success')
        return redirect(url_for('voice_ai.agent_detail', id=agent.id))

    return render_template('voice_ai/agent_form.html',
                          form=form,
                          agent=agent,
                          title='Agent bearbeiten')


@voice_ai_bp.route('/calls')
def call_list():
    """Liste aller Anrufe."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')

    query = CallSession.query

    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(
        CallSession.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    return render_template('voice_ai/calls.html',
                          calls=pagination.items,
                          pagination=pagination,
                          status=status)


@voice_ai_bp.route('/calls/<int:id>')
def call_detail(id):
    """Call Details mit Transkript."""
    call = CallSession.query.get_or_404(id)
    return render_template('voice_ai/call_detail.html', call=call)


@voice_ai_bp.route('/queue')
def queue_list():
    """Call Queue anzeigen."""
    pending = CallQueue.query.filter_by(status='pending').order_by(
        CallQueue.priority.asc(),
        CallQueue.created_at.asc()
    ).all()

    scheduled = CallQueue.query.filter_by(status='scheduled').order_by(
        CallQueue.scheduled_for.asc()
    ).all()

    return render_template('voice_ai/queue.html',
                          pending=pending,
                          scheduled=scheduled)


@voice_ai_bp.route('/customers/<int:id>/call', methods=['POST'])
def start_customer_call(id):
    """Startet Anruf zu einem Kunden."""
    customer = Customer.query.get_or_404(id)
    agent_id = request.form.get('agent_id', type=int)

    if not agent_id:
        flash('Bitte Agent auswählen!', 'error')
        return redirect(url_for('customer_detail', id=id))

    service = VoiceAIService(db.session)

    try:
        session = service.start_call(agent_id, customer.id)
        flash(f'Anruf zu {customer.name} gestartet!', 'success')
    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')

    return redirect(url_for('customer_detail', id=id))


# =============================================================================
# API ROUTES
# =============================================================================

@voice_api_bp.route('/agents', methods=['GET'])
@require_api_key
def api_agents():
    """API: Liste aller Agents."""
    agents = VoiceAgent.query.filter_by(is_active=True).all()
    return jsonify([a.to_dict() for a in agents])


@voice_api_bp.route('/agents', methods=['POST'])
@require_api_key
def api_create_agent():
    """API: Agent erstellen."""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    service = VoiceAIService(db.session)
    try:
        agent = service.create_agent(data)
        return jsonify(agent.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@voice_api_bp.route('/agents/<int:id>', methods=['GET'])
@require_api_key
def api_agent_detail(id):
    """API: Agent Details."""
    agent = VoiceAgent.query.get_or_404(id)
    return jsonify(agent.to_dict())


@voice_api_bp.route('/calls', methods=['GET'])
@require_api_key
def api_calls():
    """API: Liste der Anrufe."""
    limit = request.args.get('limit', 50, type=int)
    calls = CallSession.query.order_by(
        CallSession.created_at.desc()
    ).limit(limit).all()
    return jsonify([c.to_dict() for c in calls])


@voice_api_bp.route('/calls/<int:id>', methods=['GET'])
@require_api_key
def api_call_detail(id):
    """API: Call Details."""
    call = CallSession.query.get_or_404(id)
    return jsonify(call.to_dict())


@voice_api_bp.route('/calls/start', methods=['POST'])
@require_api_key
def api_start_call():
    """API: Anruf starten."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    agent_id = data.get('agent_id')
    customer_id = data.get('customer_id')

    if not agent_id or not customer_id:
        return jsonify({'error': 'agent_id and customer_id required'}), 400

    service = VoiceAIService(db.session)

    try:
        session = service.start_call(agent_id, customer_id)
        return jsonify(session.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@voice_api_bp.route('/queue', methods=['GET'])
@require_api_key
def api_queue():
    """API: Queue abrufen."""
    pending = CallQueue.query.filter_by(status='pending').order_by(
        CallQueue.priority.asc()
    ).all()
    return jsonify([q.to_dict() for q in pending])


@voice_api_bp.route('/queue', methods=['POST'])
@require_api_key
def api_add_to_queue():
    """API: Zur Queue hinzufügen."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    agent_id = data.get('agent_id')
    customer_id = data.get('customer_id')

    if not agent_id or not customer_id:
        return jsonify({'error': 'agent_id and customer_id required'}), 400

    service = VoiceAIService(db.session)

    try:
        queue_item = service.add_to_queue(
            agent_id,
            customer_id,
            priority=data.get('priority', 5),
            scheduled_for=data.get('scheduled_for')
        )
        return jsonify(queue_item.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@voice_api_bp.route('/customers/<int:id>/lead-score', methods=['GET'])
@require_api_key
def api_lead_score(id):
    """API: Lead Score abrufen."""
    score = LeadScore.query.filter_by(customer_id=id).first()
    if not score:
        return jsonify({'error': 'No score available'}), 404
    return jsonify(score.to_dict())


# =============================================================================
# WEBHOOK ROUTES
# =============================================================================

@voice_api_bp.route('/webhooks/vapi', methods=['POST'])
def webhook_vapi():
    """Webhook für Vapi.ai."""
    signature = request.headers.get('X-Vapi-Signature', '')

    if not verify_webhook_signature('vapi', request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    payload = request.get_json()
    service = VoiceAIService(db.session)

    try:
        session = service.handle_webhook('vapi', payload)
        return jsonify({'status': 'ok', 'call_id': session.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@voice_api_bp.route('/webhooks/retell', methods=['POST'])
def webhook_retell():
    """Webhook für Retell.ai."""
    signature = request.headers.get('X-Retell-Signature', '')

    if not verify_webhook_signature('retell', request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    payload = request.get_json()
    service = VoiceAIService(db.session)

    try:
        session = service.handle_webhook('retell', payload)
        return jsonify({'status': 'ok', 'call_id': session.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@voice_api_bp.route('/webhooks/bland', methods=['POST'])
def webhook_bland():
    """Webhook für Bland.ai."""
    signature = request.headers.get('X-Bland-Signature', '')

    if not verify_webhook_signature('bland', request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    payload = request.get_json()
    service = VoiceAIService(db.session)

    try:
        session = service.handle_webhook('bland', payload)
        return jsonify({'status': 'ok', 'call_id': session.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# REGISTER BLUEPRINTS HELPER
# =============================================================================

def register_voice_ai(app):
    """Registriert Voice AI Blueprints bei der Flask App."""
    app.register_blueprint(voice_ai_bp)
    app.register_blueprint(voice_api_bp)

    # Tabellen erstellen
    with app.app_context():
        db.create_all()
