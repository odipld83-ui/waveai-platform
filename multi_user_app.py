from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urlparse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')

# Fix pour PostgreSQL sur Render
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# === MODÈLES DE BASE DE DONNÉES ===

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(50), default='email')  # gmail, outlook, yahoo, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    login_count = db.Column(db.Integer, default=0)

class AppVersion(db.Model):
    __tablename__ = 'app_versions'
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False, unique=True)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    is_current = db.Column(db.Boolean, default=False)
    features = db.Column(db.Text)  # JSON string des nouvelles features

class MagicLink(db.Model):
    __tablename__ = 'magic_links'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))

# === UTILITAIRES D'AUTHENTIFICATION ===

def validate_email(email):
    """Validation universelle d'email pour tous providers"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def detect_email_provider(email):
    """Détection automatique du provider email"""
    domain = email.lower().split('@')[1]
    providers = {
        'gmail.com': 'Gmail',
        'googlemail.com': 'Gmail',
        'outlook.com': 'Outlook',
        'hotmail.com': 'Outlook',
        'live.com': 'Outlook',
        'yahoo.com': 'Yahoo',
        'yahoo.fr': 'Yahoo',
        'orange.fr': 'Orange',
        'free.fr': 'Free',
        'sfr.fr': 'SFR',
        'wanadoo.fr': 'Wanadoo',
        'laposte.net': 'LaPoste'
    }
    return providers.get(domain, 'Autre')

def create_magic_link(email, ip_address=None):
    """Création de lien magique universel"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    magic_link = MagicLink(
        email=email,
        token=token,
        expires_at=expires_at,
        ip_address=ip_address
    )

    db.session.add(magic_link)
    db.session.commit()

    return token

# === ROUTES PRINCIPALES ===

@app.route('/')
def landing():
    """Page d'accueil WaveAI"""
    return render_template('landing.html')

@app.route('/login')
def login():
    """Page de connexion universelle"""
    return render_template('login_universal.html')

@app.route('/dashboard')
def dashboard():
    """Tableau de bord principal après connexion"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Récupération de la version actuelle
    current_version = AppVersion.query.filter_by(is_current=True).first()

    # Statistiques utilisateur
    stats = {
        'login_count': user.login_count,
        'member_since': user.created_at.strftime('%B %Y'),
        'last_login': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Première connexion'
    }

    return render_template('dashboard.html', 
                         user=user, 
                         stats=stats, 
                         version=current_version)

# === ROUTES D'AUTHENTIFICATION ===

@app.route('/api/auth/magic-link', methods=['POST'])
def send_magic_link():
    """Envoi de lien magique universel"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({'success': False, 'message': 'Email requis'})

        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Format d\'email invalide'})

        # Détection du provider
        provider = detect_email_provider(email)

        # Récupération ou création de l'utilisateur
        user = User.query.filter_by(email=email).first()
        if not user:
            name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            user = User(
                email=email,
                name=name,
                provider=provider.lower()
            )
            db.session.add(user)
            db.session.commit()

        # Création du lien magique
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        token = create_magic_link(email, ip_address)

        # En mode démo/développement, connexion automatique
        if os.environ.get('FLASK_ENV') == 'development' or not os.environ.get('SENDGRID_API_KEY'):
            # Connexion directe en mode démo
            session['user_id'] = user.id
            session['user_email'] = user.email
            user.last_login = datetime.utcnow()
            user.login_count += 1
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Connexion réussie avec {provider} !',
                'redirect': '/dashboard',
                'demo_mode': True
            })

        # TODO: Intégrer SendGrid pour envoi réel d'emails
        # send_email_with_sendgrid(email, token)

        return jsonify({
            'success': True,
            'message': f'Lien magique envoyé à votre adresse {provider} !',
            'provider': provider
        })

    except Exception as e:
        return jsonify({'success': False, 'message': 'Erreur lors de l\'envoi'})

@app.route('/auth/verify/<token>')
def verify_magic_link(token):
    """Vérification et activation du lien magique"""
    magic_link = MagicLink.query.filter_by(token=token, used=False).first()

    if not magic_link:
        return render_template('auth_error.html', 
                             message='Lien invalide ou expiré')

    if magic_link.expires_at < datetime.utcnow():
        return render_template('auth_error.html', 
                             message='Lien expiré, veuillez en demander un nouveau')

    # Marquer le lien comme utilisé
    magic_link.used = True

    # Connexion de l'utilisateur
    user = User.query.filter_by(email=magic_link.email).first()
    if user:
        session['user_id'] = user.id
        session['user_email'] = user.email
        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('auth_error.html', 
                         message='Utilisateur introuvable')

@app.route('/logout')
def logout():
    """Déconnexion utilisateur"""
    session.clear()
    return redirect(url_for('landing'))

# === ROUTES DES AGENTS WAVEAI ===

@app.route('/agents/<agent_name>')
def agent_interface(agent_name):
    """Interface des agents IA spécialisés"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    agents = {
        'alex': {
            'name': 'Alex Wave',
            'title': 'Expert Gmail & Productivité',
            'description': 'Votre assistant pour organiser emails, automatiser workflows et booster votre productivité',
            'color': '#4285F4',
            'icon': '📧',
            'features': ['Tri automatique emails', 'Réponses intelligentes', 'Rappels contextuels']
        },
        'lina': {
            'name': 'Lina Wave',
            'title': 'Spécialiste LinkedIn & Networking',
            'description': 'Développez votre réseau professionnel et optimisez votre présence LinkedIn',
            'color': '#0077B5',
            'icon': '💼',
            'features': ['Messages personnalisés', 'Analyse de réseau', 'Stratégie de contenu']
        },
        'marco': {
            'name': 'Marco Wave',
            'title': 'Gestionnaire Réseaux Sociaux',
            'description': 'Planifiez, créez et optimisez votre présence sur tous les réseaux sociaux',
            'color': '#E4405F',
            'icon': '📱',
            'features': ['Planification posts', 'Analyse engagement', 'Tendances temps réel']
        },
        'sofia': {
            'name': 'Sofia Wave',
            'title': 'Organisatrice Calendrier & Planning',
            'description': 'Optimisez votre temps et synchronisez tous vos calendriers intelligemment',
            'color': '#34A853',
            'icon': '📅',
            'features': ['Planification smart', 'Synchronisation calendriers', 'Rappels contextuels']
        }
    }

    if agent_name not in agents:
        return redirect(url_for('dashboard'))

    user = User.query.get(session['user_id'])
    return render_template('agent.html', 
                         agent=agents[agent_name], 
                         agent_id=agent_name,
                         user=user)

# === API DES AGENTS ===

@socketio.on('agent_message')
def handle_agent_message(data):
    """Gestion des messages vers les agents IA"""
    if 'user_id' not in session:
        emit('error', {'message': 'Session expirée'})
        return

    agent_id = data.get('agent_id')
    message = data.get('message')

    if not agent_id or not message:
        emit('error', {'message': 'Données manquantes'})
        return

    # Simulation de réponse d'agent (à remplacer par IA réelle)
    responses = {
        'alex': f"📧 Alex Wave : J'analyse votre demande '{message}'. Je peux vous aider avec Gmail et la productivité !",
        'lina': f"💼 Lina Wave : Excellente question sur '{message}' ! Je vais optimiser votre stratégie LinkedIn.",
        'marco': f"📱 Marco Wave : Pour '{message}', je recommande une approche multi-réseaux intégrée.",
        'sofia': f"📅 Sofia Wave : Concernant '{message}', je vais organiser cela dans votre planning optimal."
    }

    response = responses.get(agent_id, "Agent non trouvé")

    # Simulation d'un délai de traitement
    import time
    time.sleep(1)

    emit('agent_response', {
        'agent_id': agent_id,
        'message': response,
        'timestamp': datetime.utcnow().isoformat()
    })

# === ROUTES ADMIN ET API ===

@app.route('/api/version')
def get_version():
    """API pour récupérer la version actuelle"""
    version = AppVersion.query.filter_by(is_current=True).first()
    if version:
        return jsonify({
            'version': version.version,
            'release_date': version.release_date.isoformat(),
            'description': version.description
        })
    return jsonify({'version': '1.0.0', 'description': 'Version initiale'})

@app.route('/api/stats')
def get_stats():
    """Statistiques générales de la plateforme"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401

    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'platform': 'WaveAI v1.0'
    })

# === GESTION DES ERREURS ===

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# === INITIALISATION ===

def init_database():
    """Initialisation de la base de données"""
    db.create_all()

    # Création de la version initiale si inexistante
    if not AppVersion.query.first():
        version = AppVersion(
            version='1.0.0',
            description='Lancement officiel de WaveAI - Plateforme d\'agents IA multi-utilisateurs',
            is_current=True,
            features=json.dumps([
                'Authentification universelle (Gmail, Outlook, Yahoo...)',
                '4 agents IA spécialisés (Alex, Lina, Marco, Sofia)',
                'Interface moderne responsive',
                'Chat temps réel avec agents',
                'Système de versions automatique'
            ])
        )
        db.session.add(version)
        db.session.commit()
        print("✅ Base de données initialisée avec version 1.0.0")

# === POINT D'ENTRÉE ===

i# Initialisation base de données au démarrage
@app.before_first_request
def create_tables():
    db.create_all()
    # Créer version initiale
    if not AppVersion.query.first():
        version = AppVersion(version='1.0.0', description='Version initiale WaveAI', is_current=True)
        db.session.add(version)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=False)

    debug = os.environ.get('FLASK_ENV') == 'development'

    socketio.run(app, 
                debug=debug, 
                host='0.0.0.0', 
                port=port,
                allow_unsafe_werkzeug=True)
