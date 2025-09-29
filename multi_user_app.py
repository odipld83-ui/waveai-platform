# Ajoutez cet import en haut du fichier
from ai_agents import wave_ai

# Remplacez la fonction chat_api existante par celle-ci :
@app.route('/api/chat/<agent_name>', methods=['POST'])  
def chat_api(agent_name):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non authentifié'})
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'message': 'Message vide'})
    
    if len(message) > 1000:
        return jsonify({'success': False, 'message': 'Message trop long (max 1000 caractères)'})
    
    # Récupérer l'utilisateur
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur non trouvé'})
    
    # Récupérer l'historique récent pour le contexte
    recent_history = ChatMessage.query.filter_by(
        user_id=user.id, 
        agent_name=agent_name
    ).order_by(ChatMessage.created_at.desc()).limit(3).all()
    
    conversation_context = wave_ai.format_conversation_history(reversed(recent_history))
    
    try:
        # Génération de la réponse IA
        ai_response = wave_ai.get_ai_response(
            agent_name=agent_name,
            user_message=message,
            user_name=user.name,
            conversation_history=conversation_context
        )
        
        # Sauvegarder la conversation
        chat_msg = ChatMessage(
            user_id=user.id,
            agent_name=agent_name, 
            message=message,
            response=ai_response
        )
        db.session.add(chat_msg)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'agent_name': agent_name,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        # Log l'erreur pour debug (en production, utilisez un logger)
        print(f"Erreur chat IA: {e}")
        
        # Fallback sur une réponse d'erreur gracieuse
        fallback_response = wave_ai.get_intelligent_fallback(agent_name, message)
        
        # Sauvegarder même en cas d'erreur IA
        try:
            chat_msg = ChatMessage(
                user_id=user.id,
                agent_name=agent_name, 
                message=message,
                response=fallback_response
            )
            db.session.add(chat_msg)
            db.session.commit()
        except:
            pass
        
        return jsonify({
            'success': True,
            'response': fallback_response,
            'agent_name': agent_name,
            'timestamp': datetime.now().strftime('%H:%M'),
            'fallback': True
        })

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import hashlib
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'waveai-super-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    avatar_color = db.Column(db.String(7), default='#667eea')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_name = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes principales
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)

@app.route('/agents/<agent_name>')
def agent_interface(agent_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    agents = {
        'alex': {'name': 'Alex Wave', 'speciality': 'Gmail & Productivité', 'icon': '🏄‍♂️', 'color': '#667eea'},
        'lina': {'name': 'Lina Wave', 'speciality': 'LinkedIn & Networking', 'icon': '🌊', 'color': '#764ba2'},
        'marco': {'name': 'Marco Wave', 'speciality': 'Réseaux Sociaux', 'icon': '🏄‍♀️', 'color': '#8b5cf6'},
        'sofia': {'name': 'Sofia Wave', 'speciality': 'Calendrier & Planning', 'icon': '🌊', 'color': '#06b6d4'}
    }
    
    if agent_name not in agents:
        return redirect(url_for('dashboard'))
    
    user = User.query.get(session['user_id'])
    agent = agents[agent_name]
    
    # Récupérer l'historique des conversations
    chat_history = ChatMessage.query.filter_by(
        user_id=user.id, 
        agent_name=agent_name
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    return render_template('agent.html', user=user, agent=agent, agent_name=agent_name, chat_history=reversed(chat_history))

# API Routes
@app.route('/api/auth/login', methods=['POST'])
def login_api():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': 'Email requis'})
    
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'success': False, 'message': 'Format email invalide'})
    
    # Créer ou récupérer utilisateur
    user = User.query.filter_by(email=email).first()
    if not user:
        # Nouveau utilisateur
        name = email.split('@')[0].title()
        # Générer une couleur d'avatar aléatoire
        colors = ['#667eea', '#764ba2', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
        avatar_color = secrets.choice(colors)
        
        user = User(email=email, name=name, avatar_color=avatar_color)
        db.session.add(user)
        try:
            db.session.commit()
            message = f'Bienvenue {name} ! Compte créé avec succès.'
        except:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Erreur lors de la création du compte'})
    else:
        message = f'Content de vous revoir, {user.name} !'
    
    # Connecter l'utilisateur
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.name
    
    # Mettre à jour la dernière connexion
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': message,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'avatar_color': user.avatar_color
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout_api():
    session.clear()
    return jsonify({'success': True, 'message': 'Déconnexion réussie'})

@app.route('/api/chat/<agent_name>', methods=['POST'])  
def chat_api(agent_name):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non authentifié'})
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'message': 'Message vide'})
    
    # Simulation IA pour le moment (nous intégrerons une vraie IA ensuite)
    agent_responses = {
        'alex': [
            "📧 Excellente question ! Pour optimiser votre productivité Gmail, je recommande d'utiliser des filtres automatiques et des libellés organisés.",
            "⚡ Basé sur votre demande, voici 3 stratégies de productivité : 1) Time-blocking, 2) Technique Pomodoro, 3) Inbox Zero.",
            "🎯 Je vais analyser votre workflow. Commencez par définir 3 priorités quotidiennes maximum et utilisez la matrice d'Eisenhower.",
            "📊 Pour une meilleure organisation, créez des templates d'emails récurrents et configurez des réponses automatiques."
        ],
        'lina': [
            "🔗 Parfait pour LinkedIn ! Je suggère de publier du contenu de valeur 3x par semaine et d'engager authentiquement avec votre réseau.",
            "🌟 Pour optimiser votre profil LinkedIn : photo professionnelle, titre accrocheur, résumé orienté valeur, et recommandations.",
            "💼 Stratégie networking : identifiez 10 personnes clés par semaine, envoyez des messages personnalisés, proposez de la valeur.",
            "📈 Analysons votre présence LinkedIn : cohérence du message, fréquence de publication, et engagement avec les commentaires."
        ],
        'marco': [
            "📱 Stratégie réseaux sociaux : définissons votre ligne éditoriale et créons un calendrier de contenu adapté à chaque plateforme.",
            "🎨 Pour du contenu viral : storytelling authentique, visuels impactants, et timing optimal selon votre audience.",
            "📊 Analysons vos performances : taux d'engagement, meilleur horaire de publication, et types de contenu les plus performants.",
            "🚀 Plan d'action : 1) Audit de vos comptes, 2) Stratégie de contenu, 3) Planification, 4) Analyse des résultats."
        ],
        'sofia': [
            "📅 Organisation parfaite ! Créons votre système de planification : agenda principal, tâches par priorité, et blocs de temps dédiés.",
            "⏰ Optimisation du temps : identifions vos pics de productivité et alignons vos tâches importantes sur ces créneaux.",
            "🎯 Planification stratégique : objectifs mensuels découpés en actions hebdomadaires et tâches quotidiennes mesurables.",
            "📋 Système complet : calendrier partagé, rappels automatiques, révisions hebdomadaires, et ajustements proactifs."
        ]
    }
    
    # Réponse simulée intelligente
    if agent_name in agent_responses:
        response = secrets.choice(agent_responses[agent_name])
    else:
        response = "Je suis là pour vous aider ! Pouvez-vous préciser votre demande ?"
    
    # Sauvegarder la conversation
    try:
        chat_msg = ChatMessage(
            user_id=session['user_id'],
            agent_name=agent_name, 
            message=message,
            response=response
        )
        db.session.add(chat_msg)
        db.session.commit()
    except:
        pass  # Continue même si la sauvegarde échoue
    
    return jsonify({
        'success': True,
        'response': response,
        'agent_name': agent_name
    })

@app.route('/api/user/stats')
def user_stats():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non authentifié'})
    
    # Statistiques utilisateur
    user = User.query.get(session['user_id'])
    total_messages = ChatMessage.query.filter_by(user_id=user.id).count()
    
    # Messages par agent
    agents_stats = {}
    for agent in ['alex', 'lina', 'marco', 'sofia']:
        count = ChatMessage.query.filter_by(user_id=user.id, agent_name=agent).count()
        agents_stats[agent] = count
    
    return jsonify({
        'success': True,
        'user': {
            'name': user.name,
            'email': user.email,
            'member_since': user.created_at.strftime('%d/%m/%Y'),
            'last_login': user.last_login.strftime('%d/%m/%Y à %H:%M') if user.last_login else 'Première connexion',
            'avatar_color': user.avatar_color
        },
        'stats': {
            'total_messages': total_messages,
            'agents_usage': agents_stats
        }
    })

@app.route('/test')
def test():
    return jsonify({
        'status': 'success', 
        'message': 'WaveAI Platform fonctionne parfaitement !', 
        'version': '2.0',
        'features': ['Templates HTML', 'Authentification', 'Chat IA', 'Multi-utilisateurs'],
        'agents': ['Alex Wave', 'Lina Wave', 'Marco Wave', 'Sofia Wave']
    })

# Initialisation base de données
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
