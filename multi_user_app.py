from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'waveai-super-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

@app.route('/')
def landing():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WaveAI Platform</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                text-align: center; 
                padding: 50px; 
                margin: 0;
            }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { font-size: 3em; margin-bottom: 20px; }
            .agent { 
                background: rgba(255,255,255,0.1); 
                padding: 20px; 
                margin: 15px; 
                border-radius: 10px; 
                cursor: pointer; 
                transition: all 0.3s ease;
            }
            .agent:hover { background: rgba(255,255,255,0.2); }
            .btn { 
                background: rgba(255,255,255,0.2); 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 25px; 
                text-decoration: none; 
                display: inline-block; 
                margin: 20px;
            }
            .btn:hover { background: rgba(255,255,255,0.3); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌊 WaveAI Platform</h1>
            <p>Vos Agents IA Personnalisés - Multi-utilisateurs</p>
            
            <div class="agent" onclick="location.href='/login'">
                <h3>🏄‍♂️ Alex Wave</h3>
                <p>Gmail & Productivité</p>
            </div>
            
            <div class="agent" onclick="location.href='/login'">
                <h3>🌊 Lina Wave</h3>
                <p>LinkedIn & Networking</p>
            </div>
            
            <div class="agent" onclick="location.href='/login'">
                <h3>🏄‍♀️ Marco Wave</h3>
                <p>Réseaux Sociaux</p>
            </div>
            
            <div class="agent" onclick="location.href='/login'">
                <h3>🌊 Sofia Wave</h3>
                <p>Calendrier & Planning</p>
            </div>
            
            <a href="/login" class="btn">🚀 Commencer avec WaveAI</a>
            
            <p><strong>✅ Plateforme Multi-Utilisateurs Déployée avec Succès !</strong></p>
        </div>
    </body>
    </html>
    '''

@app.route('/login')
def login():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connexion WaveAI</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                min-height: 100vh; 
                margin: 0;
            }
            .login-box { 
                background: rgba(255,255,255,0.15); 
                padding: 40px; 
                border-radius: 20px; 
                text-align: center; 
                max-width: 400px; 
                width: 90%;
            }
            input { 
                width: 100%; 
                padding: 12px; 
                border: none; 
                border-radius: 8px; 
                margin: 10px 0; 
                font-size: 16px;
            }
            button { 
                width: 100%; 
                padding: 15px; 
                background: rgba(255,255,255,0.2); 
                color: white; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px;
            }
            button:hover { background: rgba(255,255,255,0.3); }
            a { color: white; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🌊 Connexion WaveAI</h1>
            <form id="loginForm">
                <input type="email" id="email" placeholder="votre@email.com" required>
                <button type="submit">🚀 Se Connecter</button>
            </form>
            <div id="message"></div>
            <br><br>
            <a href="/">← Retour à l'accueil</a>
        </div>
        
        <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email })
                });
                
                const data = await response.json();
                if (data.success) {
                    document.getElementById('message').innerHTML = '<p style="color: lightgreen;">Connexion réussie !</p>';
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    document.getElementById('message').innerHTML = '<p style="color: pink;">' + data.message + '</p>';
                }
            } catch (error) {
                document.getElementById('message').innerHTML = '<p style="color: pink;">Erreur de connexion</p>';
            }
        });
        </script>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_name = user.name if user else 'Utilisateur'
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard WaveAI</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 20px; 
                margin: 0;
            }}
            .header {{ 
                background: rgba(0,0,0,0.2); 
                padding: 20px; 
                border-radius: 10px; 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 30px; 
            }}
            .agent-card {{ 
                background: rgba(255,255,255,0.15); 
                padding: 30px; 
                margin: 15px; 
                border-radius: 15px; 
                text-align: center; 
            }}
            .btn {{ 
                background: rgba(255,255,255,0.2); 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 25px; 
                text-decoration: none; 
                display: inline-block;
            }}
            .btn:hover {{ background: rgba(255,255,255,0.3); }}
            .logout {{ 
                background: rgba(255,255,255,0.2); 
                color: white; 
                padding: 8px 15px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌊 WaveAI Dashboard</h1>
            <div>
                <span>Bienvenue, {user_name}</span>
                <button class="logout" onclick="logout()">Déconnexion</button>
            </div>
        </div>
        
        <h2 style="text-align: center;">Choisissez Votre Agent WaveAI</h2>
        
        <div class="agent-card">
            <h3>🏄‍♂️ Alex Wave</h3>
            <p>Expert en productivité et gestion Gmail</p>
            <a href="/agents/alex" class="btn">Démarrer avec Alex</a>
        </div>
        
        <div class="agent-card">
            <h3>🌊 Lina Wave</h3>
            <p>Spécialiste LinkedIn et networking</p>
            <a href="/agents/lina" class="btn">Démarrer avec Lina</a>
        </div>
        
        <div class="agent-card">
            <h3>🏄‍♀️ Marco Wave</h3>
            <p>Expert réseaux sociaux et contenu</p>
            <a href="/agents/marco" class="btn">Démarrer avec Marco</a>
        </div>
        
        <div class="agent-card">
            <h3>🌊 Sofia Wave</h3>
            <p>Maître organisation et planification</p>
            <a href="/agents/sofia" class="btn">Démarrer avec Sofia</a>
        </div>
        
        <script>
        function logout() {{
            fetch('/api/auth/logout', {{ method: 'POST' }})
                .then(() => window.location.href = '/');
        }}
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/agents/<agent_name>')
def agent_interface(agent_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    agents = {
        'alex': {'name': 'Alex Wave', 'speciality': 'Gmail & Productivité', 'icon': '🏄‍♂️'},
        'lina': {'name': 'Lina Wave', 'speciality': 'LinkedIn & Networking', 'icon': '🌊'},
        'marco': {'name': 'Marco Wave', 'speciality': 'Réseaux Sociaux', 'icon': '🏄‍♀️'},<span class="cursor">█</span>
