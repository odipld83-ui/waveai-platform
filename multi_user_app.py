# WaveAI - Application Multi-Utilisateurs Complète RÉPARÉE
# Toutes les fonctionnalités avancées conservées avec corrections des bugs

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

# Configuration sécurisée
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')

# Correction URL PostgreSQL pour Render
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialisation des extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèles de base de données
class User(db.Model):
    """Modèle utilisateur WaveAI"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    ai_settings = db.relationship('AISettings', backref='user', uselist=False, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    magic_links = db.relationship('MagicLink', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Définit le mot de passe hashé"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Conversion en dictionnaire"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class AISettings(db.Model):
    """Paramètres IA par utilisateur"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_type = db.Column(db.String(50), nullable=False)  # kai, alex, lina, marco, sofia
    title = db.Column(db.String(200))
    messages = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MagicLink(db.Model):
    """Links magiques pour connexion sans mot de passe"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AppVersion(db.Model):
    """Gestion des versions de l'application"""
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_current = db.Column(db.Boolean, default=False)
    changelog = db.Column(db.Text)

# Système IA Universal - Version complète corrigée
class UniversalAISystem:
    """Système IA universel avec triple fallback"""
    
    def __init__(self):
        self.agents = {
            'kai': {
                'name': 'Kai Wave',
                'emoji': '🌊',
                'description': 'Assistant IA conversationnel et créatif',
                'color': '#3282b8',
                'prompt': """Tu es Kai Wave, un assistant IA amical, créatif et intelligent. 
                Tu fais partie de l'équipe WaveAI et tu aides les utilisateurs avec leurs questions générales, 
                la créativité, les idées et les conversations. Tu es moderne, décontracté mais professionnel."""
            },
            'alex': {
                'name': 'Alex Wave',
                'emoji': '⚡',
                'description': 'Spécialiste productivité et gestion Gmail',
                'color': '#ff6b35',
                'prompt': """Tu es Alex Wave, expert en productivité et gestion d'emails. 
                Tu aides avec l'organisation, la gestion du temps, l'optimisation des workflows, 
                la rédaction d'emails professionnels et l'automatisation des tâches."""
            },
            'lina': {
                'name': 'Lina Wave',
                'emoji': '💼',
                'description': 'Experte LinkedIn et networking professionnel',
                'color': '#0077b5',
                'prompt': """Tu es Lina Wave, spécialiste LinkedIn et réseautage professionnel. 
                Tu aides avec l'optimisation de profils LinkedIn, la rédaction de posts engageants, 
                les stratégies de networking et le développement de carrière."""
            },
            'marco': {
                'name': 'Marco Wave',
                'emoji': '📱',
                'description': 'Expert réseaux sociaux et marketing digital',
                'color': '#e1306c',
                'prompt': """Tu es Marco Wave, expert en réseaux sociaux et marketing digital. 
                Tu aides avec les stratégies social media, la création de contenu viral, 
                l'engagement communautaire et les campagnes marketing digitales."""
            },
            'sofia': {
                'name': 'Sofia Wave',
                'emoji': '📅',
                'description': 'Assistante planning et gestion du temps',
                'color': '#9c27b0',
                'prompt': """Tu es Sofia Wave, experte en organisation et gestion du temps. 
                Tu aides avec la planification, la gestion de calendriers, l'organisation 
                d'événements et l'optimisation de l'emploi du temps."""
            }
        }
    
    def check_ollama_availability(self):
        """Vérifie si Ollama est disponible localement"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_huggingface_response(self, message, agent_type, settings=None):
        """Utilise Hugging Face Inference API (gratuit)"""
        try:
            import requests
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            prompt = f"{agent['prompt']}\n\nUtilisateur: {message}\n{agent['name']}:"
            
            # Token Hugging Face utilisateur ou token par défaut
            token = None
            if settings and settings.huggingface_token:
                token = settings.huggingface_token
            
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            # Modèle gratuit Hugging Face
            model_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": settings.max_tokens if settings else 1000,
                    "temperature": settings.temperature if settings else 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(model_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Extraire seulement la réponse de l'agent
                    if f"{agent['name']}:" in generated_text:
                        response_text = generated_text.split(f"{agent['name']}:")[-1].strip()
                    else:
                        response_text = generated_text.replace(prompt, '').strip()
                    
                    return {
                        'response': response_text or f"Bonjour ! Je suis {agent['name']} {agent['emoji']}. Comment puis-je vous aider ?",
                        'source': 'huggingface',
                        'agent': agent_type,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Erreur Hugging Face: {e}")
        
        return None
    
    def get_ollama_response(self, message, agent_type, settings=None):
        """Utilise Ollama local"""
        try:
            import requests
            
            agent = self.agents.get(agent_type, self.agents['kai'])
            prompt = f"{agent['prompt']}\n\nUtilisateur: {message}\n\nRéponds en tant que {agent['name']}:"
            
            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": settings.temperature if settings else 0.7,
                    "num_predict": settings.max_tokens if settings else 1000
                }
            }
            
            response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'response': result.get('response', '').strip(),
                    'source': 'ollama_local',
                    'agent': agent_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erreur Ollama: {e}")
        
        return None
    
    def get_openai_response(self, message, agent_type, settings):
        """Utilise OpenAI API avec clé utilisateur"""
        try:
            import openai
            
            if not settings or not settings.openai_api_key:
                return None
            
            client = openai.OpenAI(api_key=settings.openai_api_key)
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": agent['prompt']},
                    {"role": "user", "content": message}
                ],
                max_tokens=settings.max_tokens or 1000,
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
        """Utilise Anthropic Claude avec clé utilisateur"""
        try:
            import anthropic
            
            if not settings or not settings.anthropic_api_key:
                return None
            
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            agent = self.agents.get(agent_type, self.agents['kai'])
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=settings.max_tokens or 1000,
                temperature=settings.temperature or 0.7,
                system=agent['prompt'],
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            
            return {
                'response': response.content[0].text.strip(),
                'source': 'anthropic',
                'agent': agent_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur Anthropic: {e}")
        
        return None
    
    def get_response(self, message, agent_type='kai', user_settings=None):
        """Système de fallback intelligent pour réponse IA"""
        agent = self.agents.get(agent_type, self.agents['kai'])
        
        # Définir l'ordre de priorité selon les préférences utilisateur
        fallback_order = []
        
        if user_settings:
            if user_settings.default_model == 'openai' and user_settings.openai_api_key:
                fallback_order.append('openai')
            elif user_settings.default_model == 'anthropic' and user_settings.anthropic_api_key:
                fallback_order.append('anthropic')
            elif user_settings.default_model == 'ollama' and user_settings.use_ollama:
                fallback_order.append('ollama')
        
        # Ajouter les autres options dans l'ordre de fallback
        if 'openai' not in fallback_order and user_settings and user_settings.openai_api_key:
            fallback_order.append('openai')
        if 'anthropic' not in fallback_order and user_settings and user_settings.anthropic_api_key:
            fallback_order.append('anthropic')
        if 'ollama' not in fallback_order and user_settings and user_settings.use_ollama:
            fallback_order.append('ollama')
        
        # Toujours ajouter Hugging Face comme fallback final (gratuit)
        fallback_order.append('huggingface')
        
        # Essayer chaque méthode dans l'ordre
        for method in fallback_order:
            try:
                if method == 'openai':
                    response = self.get_openai_response(message, agent_type, user_settings)
                elif method == 'anthropic':
                    response = self.get_anthropic_response(message, agent_type, user_settings)
                elif method == 'ollama':
                    response = self.get_ollama_response(message, agent_type, user_settings)
                elif method == 'huggingface':
                    response = self.get_huggingface_response(message, agent_type, user_settings)
                
                if response and response.get('response'):
                    return response
                    
            except Exception as e:
                logger.error(f"Erreur méthode {method}: {e}")
                continue
        
        # Fallback ultime si tout échoue
        return {
            'response': f"Bonjour ! Je suis {agent['name']} {agent['emoji']}. Désolé, je rencontre des difficultés techniques temporaires. Pouvez-vous réessayer ?",
            'source': 'fallback',
            'agent': agent_type,
            'timestamp': datetime.utcnow().isoformat()
        }

# Instance IA globale
ai_system = UniversalAISystem()

# Fonctions utilitaires
def send_magic_link_email(email, magic_link):
    """Envoie un lien magique par email"""
    try:
        # Configuration SMTP - utiliser variables d'environnement
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not smtp_username or not smtp_password:
            # Mode démo - log au lieu d'envoyer
            logger.info(f"Mode démo - Magic link pour {email}: {magic_link}")
            return True
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = "🌊 Votre lien de connexion WaveAI"
        
        body = f"""
        Bonjour,
        
        Cliquez sur le lien ci-dessous pour vous connecter à WaveAI :
        
        {magic_link}
        
        Ce lien est valide pendant 10 minutes.
        
        Bonne navigation ! 🌊
        L'équipe WaveAI
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Envoyer l'email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        
        logger.info(f"Magic link envoyé à {email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoi email: {e}")
        return False

def validate_email(email):
    """Valide le format email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_magic_link(user):
    """Génère un lien magique pour l'utilisateur"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Invalider les anciens liens
    MagicLink.query.filter_by(user_id=user.id, used=False).update({'used': True})
    
    # Créer nouveau lien
    magic_link = MagicLink(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.session.add(magic_link)
    db.session.commit()
    
    return url_for('magic_login', token=token, _external=True)

# Routes principales
@app.route('/')
def landing():
    """Page d'accueil WaveAI"""
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion utilisateur avec support lien magique"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        use_magic_link = 'magic_link' in request.form
        
        if not validate_email(email):
            flash('Adresse email invalide', 'error')
            return render_template('login.html')
        
        # Recherche ou création utilisateur
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Créer nouvel utilisateur
            name = email.split('@')[0].title()
            user = User(email=email, name=name)
            
            # Créer paramètres IA par défaut
            ai_settings = AISettings(user=user)
            
            db.session.add(user)
            db.session.add(ai_settings)
            db.session.commit()
            
            logger.info(f"Nouvel utilisateur créé: {email}")
        
        if use_magic_link:
            # Envoyer lien magique
            magic_link = generate_magic_link(user)
            if send_magic_link_email(email, magic_link):
                flash(f'Lien magique envoyé à {email} ! Vérifiez votre boîte mail. 📧', 'success')
            else:
                flash('Erreur lors de l\'envoi du lien magique', 'error')
            return render_template('login.html')
        else:
            # Connexion directe (mode démo)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session.permanent = True
            
            flash(f'Bienvenue {user.name} ! 🌊', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/magic/<token>')
def magic_login(token):
    """Connexion via lien magique"""
    magic_link = MagicLink.query.filter_by(token=token, used=False).first()
    
    if not magic_link:
        flash('Lien magique invalide ou expiré', 'error')
        return redirect(url_for('login'))
    
    if magic_link.expires_at < datetime.utcnow():
        flash('Lien magique expiré', 'error')
        return redirect(url_for('login'))
    
    # Marquer le lien comme utilisé
    magic_link.used = True
    magic_link.user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Connecter l'utilisateur
    session['user_id'] = magic_link.user.id
    session['user_email'] = magic_link.user.email
    session['user_name'] = magic_link.user.name
    session.permanent = True
    
    flash(f'Connexion réussie ! Bienvenue {magic_link.user.name} 🌊', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Déconnexion utilisateur"""
    session.clear()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('landing'))

@app.route('/dashboard')
def dashboard():
    """Tableau de bord principal"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # Statistiques utilisateur
    stats = {
        'total_conversations': Conversation.query.filter_by(user_id=user.id).count(),
        'agents_used': db.session.query(Conversation.agent_type).filter_by(user_id=user.id).distinct().count(),
        'last_activity': user.last_login.strftime('%d/%m/%Y à %H:%M') if user.last_login else 'Première connexion',
        'account_age': (datetime.utcnow() - user.created_at).days if user.created_at else 0
    }
    
    # Vérifier la disponibilité d'Ollama
    ollama_available = ai_system.check_ollama_availability()
    
    return render_template('dashboard.html', 
                         user=user, 
                         stats=stats, 
                         agents=ai_system.agents,
                         ollama_available=ollama_available)

@app.route('/ai-settings', methods=['GET', 'POST'])
def ai_settings():
    """Configuration IA utilisateur"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.ai_settings:
        user.ai_settings = AISettings(user_id=user.id)
        db.session.add(user.ai_settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings = user.ai_settings
        
        # Mise à jour des paramètres
        settings.openai_api_key = request.form.get('openai_key', '').strip()
        settings.anthropic_api_key = request.form.get('anthropic_key', '').strip()
        settings.huggingface_token = request.form.get('huggingface_token', '').strip()
        settings.default_model = request.form.get('default_model', 'huggingface')
        settings.use_ollama = 'use_ollama' in request.form
        
        # Paramètres avancés
        try:
            settings.temperature = float(request.form.get('temperature', 0.7))
            settings.max_tokens = int(request.form.get('max_tokens', 1000))
        except ValueError:
            settings.temperature = 0.7
            settings.max_tokens = 1000
        
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Paramètres IA mis à jour ! 🤖', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('ai_settings.html', user=user)

@app.route('/chat/<agent_type>')
def chat(agent_type):
    """Interface de chat avec un agent"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if agent_type not in ai_system.agents:
        flash('Agent non trouvé', 'error')
        return redirect(url_for('dashboard'))
    
    agent = ai_system.agents[agent_type]
    return render_template('chat.html', agent=agent, agent_type=agent_type)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API de chat avec les agents IA"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données manquantes'}), 400
    
    message = data.get('message', '').strip()
    agent_type = data.get('agent', 'kai')
    
    if not message:
        return jsonify({'error': 'Message vide'}), 400
    
    if len(message) > 5000:
        return jsonify({'error': 'Message trop long (max 5000 caractères)'}), 400
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401
        
        # Obtenir la réponse IA
        response = ai_system.get_response(message, agent_type, user.ai_settings)
        
        # Sauvegarder la conversation
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
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.route('/api/conversations')
def api_conversations():
    """API pour récupérer l'historique des conversations"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        conversations = Conversation.query.filter_by(user_id=session['user_id']).order_by(Conversation.updated_at.desc()).limit(50).all()
        
        result = []
        for conv in conversations:
            result.append({
                'id': conv.id,
                'agent_type': conv.agent_type,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur API conversations: {e}")
        return jsonify({'error': 'Erreur interne'}), 500

@app.route('/api/status')
def api_status():
    """Status de l'application et des services"""
    ollama_status = ai_system.check_ollama_availability()
    
    return jsonify({
        'status': 'ok',
        'app': 'WaveAI',
        'version': '1.0.0',
        'agents': list(ai_system.agents.keys()),
        'services': {
            'ollama_local': ollama_status,
            'huggingface': True,  # Toujours disponible
            'database': True
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# PWA Routes
@app.route('/manifest.json')
def manifest():
    """Manifest PWA"""
    manifest_data = {
        "name": "WaveAI - Agents IA Intelligents",
        "short_name": "WaveAI",
        "description": "Plateforme d'agents IA spécialisés - Alex, Lina, Marco, Sofia, Kai",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f4c75",
        "theme_color": "#3282b8",
        "orientation": "portrait-primary",
        "scope": "/",
        "lang": "fr",
        "icons": [
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🌊%3C/text%3E%3C/svg%3E",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ],
        "shortcuts": [
            {
                "name": "Chat avec Kai",
                "short_name": "Kai Wave",
                "description": "Assistant IA conversationnel",
                "url": "/chat/kai"
            },
            {
                "name": "Productivité Alex",
                "short_name": "Alex Wave", 
                "description": "Agent productivité et Gmail",
                "url": "/chat/alex"
            }
        ]
    }
    
    response = make_response(jsonify(manifest_data))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/sw.js')
def service_worker():
    """Service Worker pour PWA"""
    sw_content = """
// WaveAI Service Worker
const CACHE_NAME = 'waveai-v1.0';
const OFFLINE_URL = '/offline';

self.addEventListener('install', event => {
    console.log('WaveAI Service Worker: Installation');
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
    console.log('WaveAI Service Worker: Activation');
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(OFFLINE_URL);
            })
        );
    }
});
    """
    
    response = make_response(sw_content)
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/offline')
def offline():
    """Page hors ligne"""
    return render_template('offline.html')

# Gestionnaires d'erreurs
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page non trouvée'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error='Erreur interne du serveur'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error='Accès interdit'), 403

# Initialisation de la base de données
def create_tables():
    """Créer les tables si elles n'existent pas"""
    try:
        with app.app_context():
            db.create_all()
            
            # Version initiale
            if not AppVersion.query.filter_by(is_current=True).first():
                version = AppVersion(
                    version='1.0.0',
                    description='Version initiale WaveAI avec 5 agents IA et système universel',
                    is_current=True,
                    changelog='- 5 agents IA spécialisés\n- Système IA universel\n- Support PWA\n- Authentification universelle'
                )
                db.session.add(version)
                db.session.commit()
                
            logger.info("Base de données WaveAI initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur initialisation DB: {e}")

# Point d'entrée
if __name__ == '__main__':
    create_tables()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # Pour Render et autres déploiements
    create_tables()
