from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from universal_ai_system import universal_ai
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
    
    # AGENTS WAVEAI COMPLETS (5 agents)
    agents = {
        'alex': {'name': 'Alex Wave', 'speciality': 'Gmail & Productivité', 'icon': '🏄‍♂️', 'color': '#667eea'},
        'lina': {'name': 'Lina Wave', 'speciality': 'LinkedIn & Networking', 'icon': '🌊', 'color': '#764ba2'},
        'marco': {'name': 'Marco Wave', 'speciality': 'Réseaux Sociaux', 'icon': '🏄‍♀️', 'color': '#8b5cf6'},
        'sofia': {'name': 'Sofia Wave', 'speciality': 'Planning & Organisation', 'icon': '🌊', 'color': '#06b6d4'},
        'kai': {'name': 'Kai Wave', 'speciality': 'Assistant Conversationnel', 'icon': '🤖', 'color': '#10b981'}
    }
    
    if agent_name not in agents:
        return redirect(url_for('dashboard'))
    
    user = User.query.get(session['user_id'])
    agent = agents[agent_name]
    
    # Suggestions personnalisées par agent
    if agent_name == 'kai':
        suggestions_html = '''
                <div class="suggestion" onclick="sendSuggestion('Comment ça va aujourd\\'hui ?')">
                    Comment ça va aujourd'hui ?
                </div>
                <div class="suggestion" onclick="sendSuggestion('J\\'ai une question random...')">
                    J'ai une question random...
                </div>
                <div class="suggestion" onclick="sendSuggestion('Aide-moi à réfléchir')">
                    Aide-moi à réfléchir
                </div>
                <div class="suggestion" onclick="sendSuggestion('Explique-moi quelque chose')">
                    Explique-moi quelque chose
                </div>
                <div class="suggestion" onclick="sendSuggestion('Discutons de philosophie')">
                    Discutons de philosophie
                </div>
                <div class="suggestion" onclick="sendSuggestion('Raconte-moi quelque chose d\\'intéressant')">
                    Raconte-moi quelque chose d'intéressant
                </div>'''
        
        welcome_message = f"Salut {user.name} ! 👋 Je suis Kai Wave, ton compagnon IA pour discuter de tout et n'importe quoi ! Questions, réflexions, brainstorming, conseils... De quoi as-tu envie de parler aujourd'hui ? 🤖✨"
        
    else:
        suggestions_html = '''
                <div class="suggestion" onclick="sendSuggestion('Aide-moi à organiser ma journée')">
                    Aide-moi à organiser ma journée
                </div>
                <div class="suggestion" onclick="sendSuggestion('Quelles sont tes fonctionnalités ?')">
                    Quelles sont tes fonctionnalités ?
                </div>
                <div class="suggestion" onclick="sendSuggestion('Comment optimiser ma productivité ?')">
                    Comment optimiser ma productivité ?
                </div>'''
        
        welcome_message = f"Salut {user.name} ! Je suis {agent['name']}, votre assistant spécialisé en {agent['speciality']}. Comment puis-je vous aider aujourd'hui ? 🌊"
    
    # Interface chat avec suggestions personnalisées
    return f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent["name"]} - WaveAI</title>
        <style>
            :root {{
                --wave-blue: #667eea;
                --wave-purple: #764ba2;
                --agent-color: {agent["color"]};
            }}
            
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, var(--wave-blue) 0%, var(--wave-purple) 100%);
                color: white; margin: 0; padding: 20px; min-height: 100vh;
            }}
            
            .header {{ 
                background: rgba(0,0,0,0.2); padding: 15px 25px; border-radius: 15px;
                display: flex; justify-content: space-between; align-items: center; 
                margin-bottom: 30px; backdrop-filter: blur(10px);
            }}
            
            .agent-header {{
                text-align: center; margin-bottom: 30px; padding: 20px;
                background: rgba(255,255,255,0.1); border-radius: 20px;
                backdrop-filter: blur(15px);
            }}
            
            .chat-container {{ 
                background: rgba(255,255,255,0.15); border-radius: 20px; padding: 30px;
                max-width: 900px; margin: 0 auto; min-height: 500px;
                backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }}
            
            .message {{ 
                background: rgba(255,255,255,0.1); padding: 15px 20px; 
                border-radius: 15px; margin-bottom: 15px;
                border-left: 4px solid var(--agent-color);
                animation: fadeIn 0.3s ease;
            }}
            
            .message.user {{ 
                background: rgba(255,255,255,0.2); text-align: right; 
                border-left: none; border-right: 4px solid #4ade80;
            }}
            
            .chat-input {{ 
                display: flex; gap: 15px; margin-top: 25px; 
                background: rgba(255,255,255,0.1); padding: 20px;
                border-radius: 25px; backdrop-filter: blur(10px);
            }}
            
            .chat-input input {{ 
                flex: 1; padding: 15px 20px; border: none; border-radius: 25px; 
                font-size: 16px; background: rgba(255,255,255,0.9); color: #333;
                outline: none; transition: all 0.3s ease;
            }}
            
            .chat-input input:focus {{
                background: white; transform: scale(1.02);
            }}
            
            .chat-input button {{ 
                background: var(--agent-color); color: white; padding: 15px 25px;
                border: none; border-radius: 25px; cursor: pointer; font-weight: bold;
                transition: all 0.3s ease; min-width: 120px;
            }}
            
            .chat-input button:hover {{
                transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            }}
            
            .suggestions {{ 
                margin-top: 25px; display: flex; flex-wrap: wrap; gap: 10px;
                justify-content: center;
            }}
            
            .suggestion {{ 
                background: rgba(255,255,255,0.1); padding: 12px 18px; 
                border-radius: 25px; cursor: pointer; font-size: 0.9em;
                transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .suggestion:hover {{ 
                background: rgba(255,255,255,0.25); transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            
            .btn {{ 
                background: rgba(255,255,255,0.2); color: white; padding: 10px 20px;
                border: none; border-radius: 15px; text-decoration: none;
                transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.3);
            }}
            
            .btn:hover {{
                background: rgba(255,255,255,0.3); transform: translateY(-2px);
            }}
            
            .typing-indicator {{
                display: none; opacity: 0.7; font-style: italic; margin: 10px 0;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @media (max-width: 768px) {{
                .chat-container {{ margin: 0 10px; padding: 20px; }}
                .suggestions {{ justify-content: center; }}
                .suggestion {{ font-size: 0.8em; padding: 10px 15px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{agent["icon"]} {agent["name"]}</h1>
            <a href="/dashboard" class="btn">← Dashboard</a>
        </div>
        
        <div class="agent-header">
            <div style="font-size: 4em; margin-bottom: 15px;">{agent["icon"]}</div>
            <h2 style="margin-bottom: 10px; color: var(--agent-color);">{agent["name"]}</h2>
            <p style="font-size: 1.1em; opacity: 0.9;">{agent["speciality"]}</p>
            {"<p style='font-size: 0.9em; opacity: 0.7; margin-top: 10px;'>💬 Votre compagnon IA pour toutes discussions</p>" if agent_name == 'kai' else ""}
        </div>
        
        <div class="chat-container">
            <div id="chatMessages">
                <div class="message">
                    <strong>{agent["name"]} :</strong><br>
                    {welcome_message}
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                {agent["name"]} est en train d'écrire...
            </div>
            
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Tapez votre message..." maxlength="500">
                <button onclick="sendMessage()">✨ Envoyer</button>
            </div>
            
            <div class="suggestions">
                {suggestions_html}
            </div>
        </div>
        
        <script>
        let isTyping = false;
        
        async function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message || isTyping) return;
            
            // Ajouter message utilisateur
            addMessage(message, true);
            input.value = '';
            
            // Indicateur de frappe
            showTyping(true);
            isTyping = true;
            
            try {{
                const response = await fetch('/api/chat/{agent_name}', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: message }})
                }});
                
                const data = await response.json();
                
                // Délai réaliste pour simulation IA
                setTimeout(() => {{
                    showTyping(false);
                    
                    if (data.success) {{
                        addMessage(data.response, false);
                    }} else {{
                        addMessage('❌ ' + data.message, false);
                    }}
                    
                    isTyping = false;
                }}, Math.random() * 2000 + 1000); // 1-3 secondes
                
            }} catch (error) {{
                showTyping(false);
                addMessage('🚫 Erreur de connexion. Réessayez dans un moment.', false);
                isTyping = false;
            }}
        }}
        
        function sendSuggestion(text) {{
            if (isTyping) return;
            document.getElementById('messageInput').value = text;
            sendMessage();
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
        
        function showTyping(show) {{
            const indicator = document.getElementById('typingIndicator');
            indicator.style.display = show ? 'block' : 'none';
            if (show) {{
                document.getElementById('chatMessages').scrollTop = 
                document.getElementById('chatMessages').scrollHeight;
            }}
        }}
        
        // Envoyer avec Entrée
        document.getElementById('messageInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter' && !isTyping) sendMessage();
        }});
        
        // Animation d'entrée
        document.addEventListener('DOMContentLoaded', function() {{
            const suggestions = document.querySelectorAll('.suggestion');
            suggestions.forEach((suggestion, index) => {{
                suggestion.style.opacity = '0';
                suggestion.style.transform = 'translateY(20px)';
                
                setTimeout(() => {{
                    suggestion.style.transition = 'all 0.6s ease';
                    suggestion.style.opacity = '1';
                    suggestion.style.transform = 'translateY(0)';
                }}, index * 100 + 500);
            }});
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
    
    if len(message) > 500:
        return jsonify({'success': False, 'message': 'Message trop long (max 500 caractères)'})
    
    # Réponses intelligentes par agent (INCLUANT KAI)
    agent_responses = {
        'alex': {
            'email': "📧 Gmail optimisé : filtres automatiques + libellés colorés + règle des 2min. Configurons votre système ! Quel est votre plus gros souci email ?",
            'productivité': "⚡ Ma méthode triple : planification matinale (15min) + blocs focus (90min) + révision (10min). Votre défi principal ?",
            'organisation': "🎯 Système GTD : capturer → clarifier → organiser → réviser. Par où commencer ?",
            'gmail': "📬 Gmail pro : raccourcis clavier + réponses types + programmation d'envoi. Quel aspect vous intéresse ?",
            'workflow': "🔄 Workflow optimisé : automatisation + templates + processus répétables. Quelle tâche répétez-vous le plus ?",
            'default': "👋 Alex Wave ! Expert productivité Gmail. Je transforme le chaos en efficacité. Votre plus grand défi de productivité ?"
        },
        'lina': {
            'linkedin': "🔗 LinkedIn stratégique : profil magnétique + contenu régulier + networking authentique. Sur quoi commencer ?",
            'networking': "🌟 Networking = donner avant recevoir ! Identifions vos 5 contacts cibles. Votre secteur d'activité ?",
            'professionnel': "💼 Personal branding : expertise + réputation + réseau. Lequel développer en priorité ?",
            'contenu': "✨ Contenu LinkedIn qui marche : expertise + histoire + valeur + CTA. Votre message unique ?",
            'réseau': "🤝 Développement réseau : veille + commentaires + messages personnalisés. Combien de contacts par semaine ?",
            'default': "💫 Lina Wave ! Je transforme votre potentiel pro en opportunités concrètes. Votre objectif LinkedIn ?"
        },
        'marco': {
            'social': "📱 Social media gagnant : 1 plateforme maîtrisée + contenu pilier + engagement. Votre priorité ?",
            'contenu': "🎨 Contenu viral : storytelling + émotion + valeur + timing. Quel message porter ?",
            'instagram': "📸 Instagram 2024 : Reels créatifs + Stories interactives + posts carrousel. Votre niche ?",
            'tiktok': "🎵 TikTok : tendances + authenticité + régularité. Montrons votre expertise !",
            'viral': "🚀 Viralité : timing + émotion + partageabilité. Mais l'engagement authentique prime !",
            'créativité': "💡 Créativité digitale : inspiration + expérimentation + analyse. Quel format tester ?",
            'default': "🎬 Marco Wave ! Expert contenu qui cartonne. Transformons vos idées en publications engageantes !"
        },
        'sofia': {
            'planning': "📅 Planning parfait : vision → objectifs → actions. Vos 3 priorités du mois ?",
            'organisation': "📋 Organisation zen : capture → clarification → action → révision. Votre outil actuel ?",
            'calendrier': "⏰ Calendrier optimisé : priorités d'abord + 25% buffer + groupage. Votre défi ?",
            'temps': "🕐 Gestion temps : matrice Eisenhower + time-blocking + Pomodoro. Quelle méthode ?",
            'agenda': "🗓️ Agenda parfait : synchronisation + couleurs + rappels. Combien de calendriers ?",
            'méthodes': "🎯 Méthodes éprouvées : GTD + PARA + Zettelkasten. Laquelle vous attire ?",
            'default': "🗓️ Sofia Wave ! Je transforme le chaos en sérénité organisée. Quelle zone organiser en premier ?"
        },
        'kai': {
            'question': "🤔 Excellente question ! J'adore creuser les sujets. Donne-moi plus de contexte et explorons ça ensemble ! Qu'est-ce qui t'amène à te poser ça ?",
            'philosophie': "🧠 Ah, la philosophie ! Questions existentielles, éthique, sens de la vie... Quel aspect t'intrigue ? J'aime ces discussions qui font réfléchir !",
            'aide': "🤝 Je suis là pour t'aider ! Que ce soit réfléchir, résoudre un problème, ou juste discuter. Raconte-moi ce qui te préoccupe.",
            'conseil': "💭 Les conseils, c'est personnel... Chaque situation est unique ! Partage ton contexte et tes enjeux, qu'on réfléchisse ensemble.",
            'comment': "🛠️ Les 'comment', j'adore ! Que veux-tu apprendre ? Je peux expliquer, ou te diriger vers Alex, Lina, Marco ou Sofia si c'est leur domaine !",
            'pourquoi': "🧐 Les grands 'pourquoi' ! Questions fascinantes. De quoi parles-tu ? Science, société, psychologie, existence ?",
            'intéressant': "✨ Quelque chose d'intéressant ? Alors... savais-tu que les pieuvres ont 3 cœurs et du sang bleu ? Ou préfères-tu science, techno, culture ?",
            'réfléchir': "💡 Brainstorming time ! J'adore réfléchir ensemble. Quel sujet te trotte dans la tête ? Projet, dilemme, idée créative ?",
            'expliquer': "🎓 J'adore expliquer ! Quel concept t'intrigue ? Sciences, techno, société, psychologie... Je rends ça clair et intéressant !",
            'chat': "😊 Salut ! Content de discuter ! Comment ça va ? Qu'est-ce qui t'occupe l'esprit ces temps-ci ? Projets, réflexions, découvertes ?",
            'random': "🎲 Question random ? Perfect ! Voici : si tu pouvais dîner avec 3 personnes (vivantes ou mortes), qui choisirais-tu et pourquoi ?",
            'default': "👋 Salut ! Kai Wave, ton compagnon IA ! Questions, réflexions, conseils, discussions... De quoi as-tu envie de parler ? 🤖✨"
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
    
    # AJOUT DE KAI dans les stats
    agents_stats = {}
    for agent in ['alex', 'lina', 'marco', 'sofia', 'kai']:
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
        'message': 'WaveAI Platform V2.1 - 5 Agents Opérationnels !', 
        'version': '2.1',
        'features': ['Design Moderne', 'Auth Multi-users', 'IA Conversationnelle', 'Chat Temps Réel'],
        'agents': ['Alex Wave', 'Lina Wave', 'Marco Wave', 'Sofia Wave', 'Kai Wave'],
        'new_features': ['Kai Wave - Assistant Conversationnel', 'Suggestions Personnalisées', 'Interface Améliorée']
    })

# Initialisation
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
