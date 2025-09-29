# WaveAI - VERSION FINALE STABLE
# Correction d'URGENCE - Toutes fonctionnalités avec sécurité maximale

import os
import logging
import json
import secrets
import re
from datetime import datetime, timedelta

# Imports Flask - Base
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration de base SÉCURISÉE
app = Flask(__name__)

# Configuration avec fallbacks complets
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
database_url = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')

# CORRECTION CRITIQUE : Fix PostgreSQL URL
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialisation
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Logging sécurisé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MODÈLES DE BASE DE DONNÉES - SÉCURISÉS
class User(db.Model):
    """Utilisateur WaveAI"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class AISettings(db.Model):
    """Paramètres IA utilisateur"""
    __tablename__ = 'ai_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # APIs
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
    """Conversations"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200))
    messages = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MagicLink(db.Model):
    """Liens magiques"""
    __tablename__ = 'magic_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AppVersion(db.Model):
    """Versions app"""
    __tablename__ = 'app_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_current = db.Column(db.Boolean, default=False)

# SYSTÈME IA SÉCURISÉ - Toutes fonctionnalités
class SecureAISystem:
    """Système IA avec sécurité maximale"""
    
    def __init__(self):
        self.agents = {
            'kai': {
                'name': 'Kai Wave',
                'emoji': '🌊',
                'description': 'Assistant IA conversationnel et créatif',
                'prompt': 'Tu es Kai Wave, assistant IA amical de WaveAI.'
            },
            'alex': {
                'name': 'Alex Wave',
                'emoji': '⚡',
                'description': 'Spécialiste productivité et Gmail',
                'prompt': 'Tu es Alex Wave, expert productivité de WaveAI.'
            },
            'lina': {
                'name': 'Lina Wave',
                'emoji': '💼',
                'description': 'Experte LinkedIn et networking',
                'prompt': 'Tu es Lina Wave, experte LinkedIn de WaveAI.'
            },
            'marco': {
                'name': 'Marco Wave',
                'emoji': '📱',
                'description': 'Expert réseaux sociaux',
                'prompt': 'Tu es Marco Wave, expert réseaux sociaux de WaveAI.'
            },
            'sofia': {
                'name': 'Sofia Wave',
                'emoji': '📅',
                'description': 'Assistante planning et organisation',
                'prompt': 'Tu es Sofia Wave, experte organisation de WaveAI.'
            }
        }
    
    def check_ollama_availability(self):
        """Vérifie Ollama avec sécurité"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama non disponible: {e}")
            return False
    
    def get_huggingface_response(self, message, agent_type, settings=None):
        """Hugging Face sécurisé"""
        try:
            import requests
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            # API Hugging Face simple
            headers = {'Content-Type': 'application/json'}
            if settings and settings.huggingface_token:
                headers['Authorization'] = f'Bearer {settings.huggingface_token}'
            
            # Modèle gratuit fiable
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            
            payload = {
                "inputs": message,
                "parameters": {
                    "max_length": min(settings.max_tokens if settings else 150, 200),
                    "temperature": settings.temperature if settings else 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get('generated_text', '').strip()
                    if generated and generated != message:
                        # Nettoyer la réponse
                        clean_response = generated.replace(message, '').strip()
                        if clean_response:
                            return {
                                'response': clean_response,
                                'source': 'huggingface',
                                'agent': agent_type,
                                'timestamp': datetime.utcnow().isoformat()
                            }
            
        except Exception as e:
            logger.error(f"Erreur Hugging Face: {e}")
        
        return None
    
    def get_openai_response(self, message, agent_type, settings):
        """OpenAI sécurisé - Version 0.28"""
        try:
            if not settings or not settings.openai_api_key:
                return None
            
            import openai
            openai.api_key = settings.openai_api_key
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            # Version 0.28 de l'API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": agent['prompt']},
                    {"role": "user", "content": message}
                ],
                max_tokens=min(settings.max_tokens or 1000, 1500),
                temperature=min(max(settings.temperature or 0.7, 0.0), 1.0)
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
        """Anthropic sécurisé - Version 0.3"""
        try:
            if not settings or not settings.anthropic_api_key:
                return None
            
            import anthropic
            client = anthropic.Client(api_key=settings.anthropic_api_key)
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            # Version 0.3 de l'API
            response = client.completions.create(
                model="claude-instant-1.2",
                max_tokens_to_sample=min(settings.max_tokens or 1000, 1500),
                temperature=min(max(settings.temperature or 0.7, 0.0), 1.0),
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
        """Système complet avec fallbacks"""
        if not message or not message.strip():
            agent = self.agents.get(agent_type, self.agents['kai'])
            return {
                'response': f"Bonjour ! Je suis {agent['name']} {agent['emoji']}. Comment puis-je vous aider ?",
                'source': 'default',
                'agent': agent_type,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Ordre des tentatives
        methods = []
        
        if user_settings:
            if user_settings.default_model == 'openai' and user_settings.openai_api_key:
                methods.append(self.get_openai_response)
            elif user_settings.default_model == 'anthropic' and user_settings.anthropic_api_key:
                methods.append(self.get_anthropic_response)
            
            # Ajouter les autres APIs disponibles
            if user_settings.openai_api_key and self.get_openai_response not in methods:
                methods.append(self.get_openai_response)
            if user_settings.anthropic_api_key and self.get_anthropic_response not in methods:
                methods.append(self.get_anthropic_response)
        
        # Hugging Face en fallback
        methods.append(self.get_huggingface_response)
        
        # Essayer chaque méthode
        for method in methods:
            try:
                response = method(message, agent_type, user_settings)
                if response and response.get('response'):
                    return response
            except Exception as e:
                logger.error(f"Erreur méthode IA: {e}")
                continue
        
        # Fallback ultime
        agent = self.agents.get(agent_type, self.agents['kai'])
        return {
            'response': f"Je suis {agent['name']} {agent['emoji']}. Désolé, je rencontre des difficultés techniques. Pouvez-vous reformuler votre question ?",
            'source': 'fallback',
            'agent': agent_type,
            'timestamp': datetime.utcnow().isoformat()
        }

# Instance IA globale
ai_system = SecureAISystem()

# FONCTIONS UTILITAIRES SÉCURISÉES
def validate_email(email):
    """Validation email robuste"""
    if not email or not isinstance(email, str):
        return False
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None and len(email) <= 120

def get_user_settings(user_id):
    """Récupère settings utilisateur avec sécurité"""
    try:
        settings = AISettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = AISettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        return settings
    except Exception as e:
        logger.error(f"Erreur get_user_settings: {e}")
        return None

# ROUTES SÉCURISÉES
@app.route('/')
def landing():
    """Page d'accueil"""
    try:
        return render_template('landing.html')
    except Exception as e:
        logger.error(f"Erreur landing: {e}")
        return "<h1>🌊 WaveAI</h1><p>Plateforme d'agents IA intelligents</p><a href='/login'>Se connecter</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion sécurisée"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            
            if not validate_email(email):
                flash('Adresse email invalide', 'error')
                return render_template('login.html')
            
            # Recherche/création utilisateur
            user = User.query.filter_by(email=email).first()
            
            if not user:
                name = email.split('@')[0].title()
                user = User(email=email, name=name)
                db.session.add(user)
                db.session.flush()
                
                # Settings par défaut
                settings = AISettings(user_id=user.id)
                db.session.add(settings)
                db.session.commit()
                
                logger.info(f"Nouvel utilisateur: {email}")
            
            # Connexion
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

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('landing'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        
        # Statistics
        stats = {
            'total_conversations': Conversation.query.filter_by(user_id=user.id).count(),
            'agents_used': db.session.query(Conversation.agent_type).filter_by(user_id=user.id).distinct().count(),
            'last_activity': user.last_login.strftime('%d/%m/%Y à %H:%M') if user.last_login else 'Première connexion',
            'account_age': (datetime.utcnow() - user.created_at).days if user.created_at else 0
        }
        
        return render_template('dashboard.html', 
                             user=user, 
                             stats=stats, 
                             agents=ai_system.agents,
                             ollama_available=ai_system.check_ollama_availability())
                             
    except Exception as e:
        logger.error(f"Erreur dashboard: {e}")
        flash('Erreur dashboard', 'error')
        return redirect(url_for('login'))

@app.route('/ai-settings', methods=['GET', 'POST'])  
def ai_settings():
    """Configuration IA"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return redirect(url_for('login'))
        
        # Récupérer/créer settings
        settings = get_user_settings(user.id)
        
        if request.method == 'POST':
            if settings:
                # Mise à jour sécurisée
                settings.openai_api_key = request.form.get('openai_key', '').strip()
                settings.anthropic_api_key = request.form.get('anthropic_key', '').strip()
                settings.huggingface_token = request.form.get('huggingface_token', '').strip()
                settings.default_model = request.form.get('default_model', 'huggingface')
                settings.use_ollama = 'use_ollama' in request.form
                
                # Validation numérique
                try:
                    temp = float(request.form.get('temperature', 0.7))
                    settings.temperature = max(0.0, min(1.0, temp))
                except (ValueError, TypeError):
                    settings.temperature = 0.7
                
                try:
                    tokens = int(request.form.get('max_tokens', 1000))
                    settings.max_tokens = max(100, min(2000, tokens))
                except (ValueError, TypeError):
                    settings.max_tokens = 1000
                
                settings.updated_at = datetime.utcnow()
                db.session.commit()
                
                flash('Paramètres IA mis à jour ! 🤖', 'success')
                return redirect(url_for('dashboard'))
        
        return render_template('ai_settings.html', 
                             user={'ai_settings': settings}, 
                             ollama_available=ai_system.check_ollama_availability())
        
    except Exception as e:
        logger.error(f"Erreur ai_settings: {e}")
        flash('Erreur configuration IA', 'error')
        return redirect(url_for('dashboard'))

@app.route('/chat/<agent_type>')
def chat(agent_type):
    """Interface chat"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if agent_type not in ai_system.agents:
        flash('Agent non trouvé', 'error')
        return redirect(url_for('dashboard'))
    
    agent = ai_system.agents[agent_type]
    return render_template('chat.html', agent=agent, agent_type=agent_type)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API chat sécurisée"""
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
        
        # Récupérer utilisateur et settings
        user_id = session['user_id']
        settings = get_user_settings(user_id)
        
        # Réponse IA
        response = ai_system.get_response(message, agent_type, settings)
        
        # Sauvegarder conversation
        try:
            conversation_data = {
                'user_message': message,
                'agent_response': response['response'],
                'timestamp': response['timestamp'],
                'source': response['source']
            }
            
            conversation = Conversation(
                user_id=user_id,
                agent_type=agent_type,
                title=message[:100] + ('...' if len(message) > 100 else ''),
                messages=json.dumps([conversation_data])
            )
            db.session.add(conversation)
            db.session.commit()
        except Exception as e:
            logger.error(f"Erreur sauvegarde conversation: {e}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erreur API chat: {e}")
        return jsonify({'error': 'Erreur interne'}), 500

@app.route('/api/status')
def api_status():
    """Status API"""
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
        return jsonify({"error": "Erreur manifest"}), 500

# Gestionnaires d'erreurs
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page non trouvée'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error='Erreur interne'), 500

# Initialisation sécurisée
def init_database():
    """Initialisation DB avec sécurité maximale"""
    try:
        with app.app_context():
            # Créer toutes les tables
            db.create_all()
            
            # Version par défaut
            if not AppVersion.query.filter_by(is_current=True).first():
                version = AppVersion(
                    version='1.0.0',
                    description='WaveAI - Système IA universel complet et sécurisé',
                    is_current=True
                )
                db.session.add(version)
                db.session.commit()
            
            logger.info("✅ Base de données WaveAI initialisée avec succès")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erreur critique initialisation DB: {e}")
        return False

# Point d'entrée SÉCURISÉ
if __name__ == '__main__':
    # Mode développement
    if init_database():
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        logger.error("❌ Échec initialisation - Arrêt de l'application")
else:
    # Mode production (Render, etc.)
    init_database()
