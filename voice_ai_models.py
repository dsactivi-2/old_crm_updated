"""
Voice AI Sales Agent - Database Models
Für CRM Integration mit Vapi.ai, Retell.ai, Bland.ai
Unterstützt: Deutsch, Bosnisch, Serbisch
"""

from datetime import datetime, timezone
from models import db
import json


class VoiceAgent(db.Model):
    """Voice AI Agent Konfiguration."""

    __tablename__ = 'voice_agents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # vapi, retell, bland
    agent_id = db.Column(db.String(100))  # Provider's agent ID

    # API Keys (verschlüsselt speichern in Production!)
    api_key = db.Column(db.String(500))

    # Sprach-Konfiguration
    primary_language = db.Column(db.String(10), default='de')  # de, bs, sr
    supported_languages = db.Column(db.Text, default='["de", "bs", "sr"]')

    # TTS Konfiguration
    tts_provider = db.Column(db.String(50), default='elevenlabs')  # elevenlabs, azure, playht
    tts_voice_id = db.Column(db.String(100))
    tts_voice_name = db.Column(db.String(100))

    # STT Konfiguration
    stt_provider = db.Column(db.String(50), default='deepgram')  # deepgram, azure, google

    # LLM Konfiguration
    llm_provider = db.Column(db.String(50), default='openai')  # openai, anthropic, groq
    llm_model = db.Column(db.String(50), default='gpt-4o-mini')

    # System Prompt (Sales Script)
    system_prompt = db.Column(db.Text)

    # Telefonie
    phone_number = db.Column(db.String(20))
    telephony_provider = db.Column(db.String(50), default='twilio')  # twilio, vonage, plivo

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    call_sessions = db.relationship('CallSession', backref='agent', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def get_supported_languages(self):
        return json.loads(self.supported_languages or '[]')

    def set_supported_languages(self, languages):
        self.supported_languages = json.dumps(languages)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'agent_id': self.agent_id,
            'primary_language': self.primary_language,
            'supported_languages': self.get_supported_languages(),
            'tts_provider': self.tts_provider,
            'tts_voice_name': self.tts_voice_name,
            'stt_provider': self.stt_provider,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'phone_number': self.phone_number,
            'telephony_provider': self.telephony_provider,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CallSession(db.Model):
    """Anruf-Session mit Transkript und Analyse."""

    __tablename__ = 'call_sessions'

    id = db.Column(db.Integer, primary_key=True)

    # Referenzen
    agent_id = db.Column(db.Integer, db.ForeignKey('voice_agents.id', ondelete='SET NULL'),
                        index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL'),
                           index=True)

    # Provider IDs
    provider_call_id = db.Column(db.String(100), unique=True, index=True)
    provider_session_id = db.Column(db.String(100))

    # Call Details
    direction = db.Column(db.String(20), default='outbound')  # inbound, outbound
    phone_from = db.Column(db.String(20))
    phone_to = db.Column(db.String(20))

    # Timing
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)

    # Status
    status = db.Column(db.String(50), default='initiated')
    # initiated, ringing, in_progress, completed, failed, no_answer, busy

    # Sprache
    detected_language = db.Column(db.String(10))  # de, bs, sr

    # Transkript
    transcript = db.Column(db.Text)
    transcript_segments = db.Column(db.Text)  # JSON mit Zeitstempeln

    # AI Analyse
    summary = db.Column(db.Text)
    sentiment = db.Column(db.String(20))  # positive, neutral, negative
    sentiment_score = db.Column(db.Float)  # -1.0 bis 1.0

    # Sales Outcome
    outcome = db.Column(db.String(50))
    # interested, not_interested, callback, appointment, sale, no_decision
    next_action = db.Column(db.String(200))
    appointment_date = db.Column(db.DateTime)

    # Lead Scoring
    lead_score_before = db.Column(db.Integer)
    lead_score_after = db.Column(db.Integer)

    # Recording
    recording_url = db.Column(db.String(500))

    # Kosten
    cost_amount = db.Column(db.Float, default=0.0)
    cost_currency = db.Column(db.String(3), default='EUR')

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    customer = db.relationship('Customer', backref='call_sessions')

    def get_transcript_segments(self):
        return json.loads(self.transcript_segments or '[]')

    def set_transcript_segments(self, segments):
        self.transcript_segments = json.dumps(segments, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'customer_id': self.customer_id,
            'provider_call_id': self.provider_call_id,
            'direction': self.direction,
            'phone_from': self.phone_from,
            'phone_to': self.phone_to,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'detected_language': self.detected_language,
            'transcript': self.transcript,
            'summary': self.summary,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'outcome': self.outcome,
            'next_action': self.next_action,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'lead_score_after': self.lead_score_after,
            'recording_url': self.recording_url,
            'cost_amount': self.cost_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CallQueue(db.Model):
    """Warteschlange für ausgehende Anrufe."""

    __tablename__ = 'call_queue'

    id = db.Column(db.Integer, primary_key=True)

    # Referenzen
    agent_id = db.Column(db.Integer, db.ForeignKey('voice_agents.id', ondelete='CASCADE'),
                        index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'),
                           index=True)

    # Queue Details
    priority = db.Column(db.Integer, default=5)  # 1 = höchste, 10 = niedrigste
    scheduled_for = db.Column(db.DateTime)

    # Status
    status = db.Column(db.String(20), default='pending')
    # pending, scheduled, calling, completed, failed, cancelled

    # Retry Logic
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=3)
    last_attempt_at = db.Column(db.DateTime)

    # Result
    call_session_id = db.Column(db.Integer, db.ForeignKey('call_sessions.id'))

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    agent = db.relationship('VoiceAgent', backref='queue_items')
    customer = db.relationship('Customer', backref='queue_items')
    call_session = db.relationship('CallSession', backref='queue_item')

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'priority': self.priority,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'status': self.status,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LeadScore(db.Model):
    """Lead Scoring basierend auf AI-Analyse."""

    __tablename__ = 'lead_scores'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'),
                           unique=True, index=True)

    # Scores (0-100)
    overall_score = db.Column(db.Integer, default=50)
    engagement_score = db.Column(db.Integer, default=50)
    interest_score = db.Column(db.Integer, default=50)
    urgency_score = db.Column(db.Integer, default=50)

    # Predictions
    predicted_outcome = db.Column(db.String(50))
    conversion_probability = db.Column(db.Float)

    # Best Time
    best_call_time = db.Column(db.String(50))  # morning, afternoon, evening
    preferred_language = db.Column(db.String(10))

    # Timestamps
    last_calculated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    customer = db.relationship('Customer', backref='lead_score', uselist=False)

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'overall_score': self.overall_score,
            'engagement_score': self.engagement_score,
            'interest_score': self.interest_score,
            'urgency_score': self.urgency_score,
            'predicted_outcome': self.predicted_outcome,
            'conversion_probability': self.conversion_probability,
            'best_call_time': self.best_call_time,
            'preferred_language': self.preferred_language,
            'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None,
        }
