# WaveAI - Application Multi-Utilisateurs TOUTES FONCTIONNALITÉS
# CORRECTIONS PRÉCISES des erreurs de déploiement

import os
import logging
import json
import secrets
import smtplib
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration de base
app = Flask(__name__)

# CORRECTION 1: Configuration sécurisée avec fallbacks
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')

# CORRECTION 2: Fix URL PostgreSQL pour Render
database_url = app.config['SQLALCHEMY_DATABASE_URI']
if database_url and database_url.startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialisation des extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORRECTION 3: Modèles avec gestion d'erreurs
class User(db.Model):
    """Modèle utilisateur WaveAI"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations avec cascade proper
    ai_settings = db.relationship('AISettings', backref='user', uselist=False, cascade='all, delete-orphan', lazy='select')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    magic_links = db.relationship('MagicLink', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash or not password:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class AISettings(db.Model):
    """Paramètres IA par utilisateur"""
    __tablename__ = 'ai_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # APIs IA
    openai_api_key = db.Column(db.String(200))
    anthropic_api_key = db.Column(db.String(200))
    huggingface_token = db.Column(db.String(200))
    
    # Préférences
    default_model = db.Column(db.String(100), default='huggingface')
    use_ollama = db.Column(db.Boolean, default=True)
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=1000)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(db.Model):
    """Historique des conversations"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200))
    messages = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MagicLink(db.Model):
    """Links magiques pour connexion"""
    __tablename__ = 'magic_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AppVersion(db.Model):
    """Gestion des versions"""
    __tablename__ = 'app_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_current = db.Column(db.Boolean, default=False)
    changelog = db.Column(db.Text)

# CORRECTION 4: Système IA avec imports sécurisés
class UniversalAISystem:
    """Système IA universel avec gestion d'erreurs robuste"""
    
    def __init__(self):
        self.agents = {
            'kai': {
                'name': 'Kai Wave',
                'emoji': '🌊',
                'description': 'Assistant IA conversationnel et créatif',
                'color': '#3282b8',
                'prompt': 'Tu es Kai Wave, un assistant IA amical, créatif et intelligent de l\'équipe WaveAI.'
            },
            'alex': {
                'name': 'Alex Wave',
                'emoji': '⚡',
                'description': 'Spécialiste productivité et gestion Gmail',
                'color': '#ff6b35',
                'prompt': 'Tu es Alex Wave, expert en productivité et gestion d\'emails.'
            },
            'lina': {
                'name': 'Lina Wave',
                'emoji': '💼',
                'description': 'Experte LinkedIn et networking professionnel',
                'color': '#0077b5',
                'prompt': 'Tu es Lina Wave, spécialiste LinkedIn et réseautage professionnel.'
            },
            'marco': {
                'name': 'Marco Wave',
                'emoji': '📱',
                'description': 'Expert réseaux sociaux et marketing digital',
                'color': '#e1306c',
                'prompt': 'Tu es Marco Wave, expert en réseaux sociaux et marketing digital.'
            },
            'sofia': {
                'name': 'Sofia Wave',
                'emoji': '📅',
                'description': 'Assistante planning et gestion du temps',
                'color': '#9c27b0',
                'prompt': 'Tu es Sofia Wave, experte en organisation et gestion du temps.'
            }
        }
    
    def check_ollama_availability(self):
        """Vérifie Ollama avec gestion d'erreurs"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_huggingface_response(self, message, agent_type, settings=None):
        """Hugging Face avec gestion d'erreurs"""
        try:
            import requests
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            # URL API Hugging Face
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            
            headers = {}
            if settings and settings.huggingface_token:
                headers['Authorization'] = f'Bearer {settings.huggingface_token}'
            
            payload = {
                "inputs": message,
                "parameters": {
                    "max_length": min(settings.max_tokens if settings else 150, 150),
                    "temperature": settings.temperature if settings else 0.7
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '').strip()
                    if text and text != message:
                        return {
                            'response': text.replace(message, '').strip() or f"Bonjour ! Je suis {agent['name']} {agent['emoji']}.",
                            'source': 'huggingface',
                            'agent': agent_type,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
        except Exception as e:
            logger.error(f"Erreur Hugging Face: {e}")
        
        return None
    
    def get_openai_response(self, message, agent_type, settings):
        """OpenAI avec version compatible"""
        try:
            if not settings or not settings.openai_api_key:
                return None
            
            import openai
            openai.api_key = settings.openai_api_key
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": agent['prompt']},
                    {"role": "user", "content": message}
                ],
                max_tokens=min(settings.max_tokens or 1000, 1500),
                temperature=settings.temperature or 0.7
            )
            
            return {
                'response': response.choices[0].message.content.strip(),
                'source': 'openai',
                'agent': agent_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            return None
    
    def get_anthropic_response(self, message, agent_type, settings):
        """Anthropic avec version compatible"""
        try:
            if not settings or not settings.anthropic_api_key:
                return None
            
            import anthropic
            client = anthropic.Client(api_key=settings.anthropic_api_key)
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            response = client.completions.create(
                model="claude-instant-1.2",
                max_tokens_to_sample=min(settings.max_tokens or 1000, 1500),
                temperature=settings.temperature or 0.7,
                prompt=f"Human: {agent['prompt']}\n\n{message}\n\nAssistant:"
            )
            
            return {
                'response': response.completion.strip(),
                'source': 'anthropic',
                'agent': agent_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur Anthropic: {e}")
            return None
    
    def get_response(self, message, agent_type='kai', user_settings=None):
        """Système de fallback intelligent"""
        agent = self.agents.get(agent_type, self.agents['kai'])
        
        # Ordre des tentatives
        methods = []
        
        if user_settings:
            if user_settings.default_model == 'openai' and user_settings.openai_api_key:
                methods.append('openai')
            elif user_settings.default_model == 'anthropic' and user_settings.anthropic_api_key:
                methods.append('anthropic')
            
            if user_settings.openai_api_key and 'openai' not in methods:
                methods.append('openai')
            if user_settings.anthropic_api_key and 'anthropic' not in methods:
                methods.append('anthropic')
        
        # Toujours essayer Hugging Face en fallback
        methods.append('huggingface')
        
        # Tentatives
        for method in methods:
            try:
                if method == 'openai':
                    response = self.get_openai_response(message, agent_type, user_settings)
                elif method == 'anthropic':
                    response = self.get_anthropic_response(message, agent_type, user_settings)
                elif method == 'huggingface':
                    response = self.get_huggingface_response(message, agent_type, user_settings)
                
                if response and response.get('response'):
                    return response
                    
            except Exception as e:
                logger.error(f"Erreur méthode {method}: {e}")
                continue
        
        # Fallback ultime
        return {
            'response': f"Bonjour ! Je suis {agent['name']} {agent['emoji']}. Comment puis-je vous aider aujourd'hui ?",
            'source': 'fallback',
            'agent': agent_type,
            'timestamp': datetime.utcnow().isoformat()
        }

# Instance IA globale
ai_system = UniversalAISystem()

# CORRECTION 5: Fonctions utilitaires sécurisées
def send_magic_link_email(email, magic_link):
    """Envoi email avec gestion d'erreurs"""
    try:
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not all([smtp_server, smtp_username, smtp_password]):
            logger.info(f"Mode démo - Magic link pour {email}: {magic_link}")
            return True
        
        # Configuration SMTP
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = "🌊 Votre lien de connexion WaveAI"
        
        body = f"""
        Bonjour,
        
        Cliquez sur le lien ci-dessous pour vous connecter à WaveAI :
        {magic_link}
        
        Ce lien est valide pendant 10 minutes.
        
        L'équipe WaveAI 🌊
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Envoi
        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, email, msg.as_string())
        
        logger.info(f"Magic link envoyé à {email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoi email: {e}")
        return False

def validate_email(email):
    """Validation email sécurisée"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_magic_link(user):
    """Génération lien magique sécurisé"""
    try:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Invalider anciens liens
        MagicLink.query.filter_by(user_id=user.id, used=False).update({'used': True})
        db.session.commit()
        
        # Nouveau lien
        magic_link = MagicLink(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(magic_link)
        db.session.commit()
        
        return url_for('magic_login', token=token, _external=True)
        
    except Exception as e:
        logger.error(f"Erreur génération magic link: {e}")
        return None

# CORRECTION 6: Routes avec gestion d'erreurs complète
@app.route('/')
def landing():
    """Page d'accueil"""
    try:
        return render_template('landing.html')
    except Exception as e:
        logger.error(f"Erreur landing: {e}")
        return f"<h1>🌊 WaveAI</h1><p>Bienvenue ! <a href='{url_for('login')}'>Se connecter</a></p>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion utilisateur avec toutes les fonctionnalités"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            use_magic_link = 'magic_link' in request.form
            
            if not validate_email(email):
                flash('Adresse email invalide', 'error')
                return render_template('login.html')
            
            # Recherche ou création utilisateur
            user = User.query.filter_by(email=email).first()
            
            if not user:
                name = email.split('@')[0].title()
                user = User(email=email, name=name)
                db.session.add(user)
                db.session.flush()
                
                # Paramètres IA par défaut
                ai_settings = AISettings(user_id=user.id)
                db.session.add(ai_settings)
                
                db.session.commit()
                logger.info(f"Nouvel utilisateur: {email}")
            
            if use_magic_link:
                # Lien magique
                magic_link = generate_magic_link(user)
                if magic_link and send_magic_link_email(email, magic_link):
                    flash(f'Lien magique envoyé à {email} ! 📧', 'success')
                else:
                    flash('Erreur lors de l\'envoi du lien magique', 'error')
                return render_template('login.html')
            else:
                # Connexion directe
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_name'] = user.name
                session.permanent = True
                
                flash(f'Bienvenue {user.name} ! 🌊', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            logger.error(f"Erreur login: {e}")
            flash('Erreur de connexion', 'error')
            db.session.rollback()
    
    return render_template('login.html')

@app.route('/magic/<token>')
def magic_login(token):
    """Connexion via lien magique"""
    try:
        magic_link = MagicLink.query.filter_by(token=token, used=False).first()
        
        if not magic_link:
            flash('Lien magique invalide ou expiré', 'error')
            return redirect(url_for('login'))
        
        if magic_link.expires_at < datetime.utcnow():
            flash('Lien magique expiré', 'error')
            return redirect(url_for('login'))
        
        # Utilisation du lien
        magic_link.used = True
        magic_link.user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Connexion
        session['user_id'] = magic_link.user.id
        session['user_email'] = magic_link.user.email
        session['user_name'] = magic_link.user.name
        session.permanent = True
        
        flash(f'Connexion réussie ! Bienvenue {magic_link.user.name} 🌊', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Erreur magic login: {e}")
        flash('Erreur de connexion', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('landing'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal avec toutes les fonctionnalités"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        
        # Stats
        stats = {
            'total_conversations': Conversation.query.filter_by(user_id=user.id).count(),
            'agents_used': db.session.query(Conversation.agent_type).filter_by(user_id=user.id).distinct().count(),
            'last_activity': user.last_login.strftime('%d/%m/%Y à %H:%M') if user.last_login else 'Première connexion',
            'account_age': (datetime.utcnow() - user.created_at).days if user.created_at else 0
        }
        
        # Vérifier Ollama
        ollama_available = ai_system.check_ollama_availability()
        
        return render_template('dashboard.html', 
                             user=user, 
                             stats=stats, 
                             agents=ai_system.agents,
                             ollama_available=ollama_available)
                             
    except Exception as e:
        logger.error(f"Erreur dashboard: {e}")
        flash('Erreur lors du chargement du dashboard', 'error')
        return redirect(url_for('login'))

@app.route('/ai-settings', methods=['GET', 'POST'])
def ai_settings():
    """Configuration IA complète"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return redirect(url_for('login'))
        
        # Créer settings si nécessaire
        if not user.ai_settings:
            ai_settings = AISettings(user_id=user.id)
            db.session.add(ai_settings)
            db.session.commit()
            user.ai_settings = ai_settings
        
        if request.method == 'POST':
            settings = user.ai_settings
            
            # Mise à jour
            settings.openai_api_key = request.form.get('openai_key', '').strip()
            settings.anthropic_api_key = request.form.get('anthropic_key', '').strip()
            settings.huggingface_token = request.form.get('huggingface_token', '').strip()
            settings.default_model = request.form.get('default_model', 'huggingface')
            settings.use_ollama = 'use_ollama' in request.form
            
            # Paramètres avancés avec validation
            try:
                settings.temperature = float(request.form.get('temperature', 0.7))
                settings.temperature = max(0.0, min(1.0, settings.temperature))
            except (ValueError, TypeError):
                settings.temperature = 0.7
            
            try:
                settings.max_tokens = int(request.form.get('max_tokens', 1000))
                settings.max_tokens = max(100, min(2000, settings.max_tokens))
            except (ValueError, TypeError):
                settings.max_tokens = 1000
            
            settings.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Paramètres IA mis à jour ! 🤖', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('ai_settings.html', user=user, ollama_available=ai_system.check_ollama_availability())
        
    except Exception as e:
        logger.error(f"Erreur ai_settings: {e}")
        flash('Erreur lors de la configuration IA', 'error')
        return redirect(url_for('dashboard'))

@app.route('/chat/<agent_type>')
def chat(agent_type):
    """Interface de chat"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if agent_type not in ai_system.agents:
        flash('Agent non trouvé', 'error')
        return redirect(url_for('dashboard'))
    
    agent = ai_system.agents[agent_type]
    return render_template('chat.html', agent=agent, agent_type=agent_type)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API chat avec IA complète"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        message = data.get('message', '').strip()
        agent_type = data.get('agent', 'kai')
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        if len(message) > 5000:
            return jsonify({'error': 'Message trop long'}), 400
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401
        
        # Obtenir réponse IA
        response = ai_system.get_response(message, agent_type, user.ai_settings)
        
        # Sauvegarder conversation
        conversation_data = {
            'user_message': message,
            'agent_response': response['response'],
            'timestamp': response['timestamp'],
            'source': response['source']
        }
        
        conversation = Conversation(
            user_id=user.id,
            agent_type=agent_type,
            title=message[:100] + ('...' if len(message) > 100 else ''),
            messages=json.dumps([conversation_data])
        )
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erreur API chat: {e}")
        return jsonify({'error': 'Erreur interne'}), 500

@app.route('/api/status')
def api_status():
    """Status complet"""
    try:
        return jsonify({
            'status': 'ok',
            'app': 'WaveAI',
            'version': '1.0.0',
            'agents': list(ai_system.agents.keys()),
            'services': {
                'ollama_local': ai_system.check_ollama_availability(),
                'database': True
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Erreur status: {e}")
        return jsonify({'error': 'Erreur status'}), 500

# PWA Routes
@app.route('/manifest.json')
def manifest():
    """Manifest PWA"""
    try:
        manifest_data = {
            "name": "WaveAI - Agents IA Intelligents",
            "short_name": "WaveAI",
            "description": "Plateforme d'agents IA spécialisés",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0f4c75",
            "theme_color": "#3282b8",
            "icons": [
                {
                    "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🌊%3C/text%3E%3C/svg%3E",
                    "sizes": "any",
                    "type": "image/svg+xml"
                }
            ]
        }
        
        response = make_response(jsonify(manifest_data))
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        logger.error(f"Erreur manifest: {e}")
        return jsonify({"error": "Manifest error"}), 500

# Gestionnaires d'erreurs
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page non trouvée'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error='Erreur interne'), 500

# CORRECTION 7: Initialisation DB sécurisée
def init_database():
    """Initialisation sécurisée de la base de données"""
    try:
        with app.app_context():
            db.create_all()
            
            # Version par défaut
            if not AppVersion.query.filter_by(is_current=True).first():
                version = AppVersion(
                    version='1.0.0',
                    description='WaveAI avec système IA universel complet',
                    is_current=True,
                    changelog='- 5 agents IA spécialisés\n- Système IA universel\n- Multi-utilisateurs\n- PWA'
                )
                db.session.add(version)
                db.session.commit()
            
            logger.info("Base de données WaveAI initialisée avec succès")
            
    except Exception as e:
        logger.error(f"Erreur initialisation base de données: {e}")

# Point d'entrée
if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # Pour déploiement (Render, etc.)
    init_database()
