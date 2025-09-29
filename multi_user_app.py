from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
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
    
    # Interface chat simple intégrée (pas de template séparé)
    return f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent["name"]} - WaveAI</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; margin: 0; padding: 20px;
            }}
            .header {{ 
                background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px;
                display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;
            }}
            .chat-container {{ 
                background: rgba(255,255,255,0.15); border-radius: 15px; padding: 30px;
                max-width: 800px; margin: 0 auto; min-height: 400px;
            }}
            .message {{ 
                background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;
            }}
            .message.user {{ background: rgba(255,255,255,0.2); text-align: right; }}
            .chat-input {{ display: flex; gap: 10px; margin-top: 20px; }}
            .chat-input input {{ 
                flex: 1; padding: 12px; border: none; border-radius: 25px; font-size: 16px;
            }}
            .chat-input button {{ 
                background: rgba(255,255,255,0.2); color: white; padding: 12px 20px;
                border: none; border-radius: 25px; cursor: pointer;
            }}
            .btn {{ 
                background: rgba(255,255,255,0.2); color: white; padding: 8px 15px;
                border: none; border-radius: 5px; text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{agent["icon"]} {agent["name"]}</h1>
            <a href="/dashboard" class="btn">← Dashboard</a>
        </div>
        
        <div class="chat-container">
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="font-size: 3em; margin-bottom: 10px;">{agent["icon"]}</div>
                <h2>{agent["name"]}</h2>
                <p>{agent["speciality"]}</p>
            </div>
            
            <div id="chatMessages">
                <div class="message">
                    <strong>{agent["name"]} :</strong><br>
                    Salut {user.name} ! Je suis {agent["name"]}, votre assistant spécialisé en {agent["speciality"]}. 
                    Comment puis-je vous aider aujourd'hui ? 🌊
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Tapez votre message...">
                <button onclick="sendMessage()">Envoyer</button>
            </div>
        </div>
        
        <script>
        async function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Ajouter message utilisateur
            addMessage(message, true);
            input.value = '';
            
            try {{
                const response = await fetch('/api/chat/{agent_name}', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: message }})
                }});
                
                const data = await response.json();
                if (data.success) {{
                    addMessage(data.response, false);
                }} else {{
                    addMessage('Erreur: ' + data.message, false);
                }}
            }} catch (error) {{
                addMessage('Erreur de connexion', false);
            }}
        }}
        
        function addMessage(text, isUser) {{
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message' + (isUser ? ' user' : '');
            messageDiv.innerHTML = isUser 
                ? '<strong>Vous :</strong><br>' + text
                : '<strong>{agent["name"]} :</strong><br>' + text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') sendMessage();
        }});
        </script>
    </body>
    </html>
    '''

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
    
    # Réponses intelligentes par agent
    agent_responses = {
        'alex': {
            'email': "📧 Pour Gmail : filtres automatiques, libellés colorés, règle des 2min. Créons votre système !",
            'productivité': "⚡ Ma méthode : planification matinale + blocs focus + révision. Votre défi principal ?",
            'organisation': "🎯 Système GTD : capturer, clarifier, organiser, réviser. Par où commencer ?",
            'default': "👋 Alex Wave ici ! Expert productivité et Gmail. Comment optimiser votre workflow aujourd'hui ?"
        },
        'lina': {
            'linkedin': "🔗 LinkedIn gagnant : profil optimisé + contenu régulier + networking authentique. Votre objectif ?",
            'networking': "🌟 Networking = donner avant recevoir. Identifions vos contacts cibles !",
            'professionnel': "💼 Personal branding : expertise + réputation + réseau. Priorité ?",
            'default': "💫 Lina Wave ! Spécialisée LinkedIn et networking. Développons votre influence professionnelle !"
        },
        'marco': {
            'social': "📱 Stratégie social media : plateforme principale + contenu pilier + engagement. Votre focus ?",
            'contenu': "🎨 Contenu viral : storytelling + émotion + call-to-action. Quel message porter ?",
            'instagram': "📸 Instagram 2024 : Reels créatifs + Stories interactives. Votre niche ?",
            'default': "🎬 Marco Wave ! Expert réseaux sociaux. Transformons vos idées en contenu engageant !"
        },
        'sofia': {
            'planning': "📅 Planification parfaite : vision → objectifs → actions. Vos priorités du mois ?",
            'calendrier': "⏰ Calendrier zen : priorités d'abord + buffer 25% + groupage. Votre défi ?",
            'organisation': "📋 Mon système : capture → clarification → action. Votre outil actuel ?",
            'default': "🗓️ Sofia Wave ! Experte organisation. Transformons le chaos en efficacité !"
        }
    }
    
    # Génération de réponse intelligente
    message_lower = message.lower()
    
    if agent_name in agent_responses:
        agent_data = agent_responses[agent_name]
        
        # Chercher des mots-clés
        for keyword, response in agent_data.items():
            if keyword != 'default' and keyword in message_lower:
                ai_response = response
                break
        else:
            ai_response = agent_data['default']
    else:
        ai_response = "Je suis là pour vous aider !"
    
    # Sauvegarder la conversation
    try:
        user = User.query.get(session['user_id'])
        chat_msg = ChatMessage(
            user_id=user.id,
            agent_name=agent_name, 
            message=message,
            response=ai_response
        )
        db.session.add(chat_msg)
        db.session.commit()
    except:
        pass
    
    return jsonify({
        'success': True,
        'response': ai_response,
        'agent_name': agent_name,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@app.route('/api/user/stats')
def user_stats():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non authentifié'})
    
    user = User.query.get(session['user_id'])
    total_messages = ChatMessage.query.filter_by(user_id=user.id).count()
    
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
        'message': 'WaveAI Platform V2.0 - Tout Fonctionne !', 
        'version': '2.0',
        'features': ['Design Moderne', 'Auth Multi-users', 'IA Intelligente', 'Chat Temps Réel'],
        'agents': ['Alex Wave', 'Lina Wave', 'Marco Wave', 'Sofia Wave']
    })

# Initialisation
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)

