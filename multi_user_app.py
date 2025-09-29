from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'waveai-super-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix pour PostgreSQL sur Render
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class AppVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(10), nullable=False)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    is_current = db.Column(db.Boolean, default=False)

# Routes principales
@app.route('/')
def landing():
    return '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌊 WaveAI Platform</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 50px; }
            .header h1 { font-size: 3em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-bottom: 40px; }
            .agent { 
                background: rgba(255,255,255,0.15); 
                padding: 30px; border-radius: 15px; 
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .agent:hover { 
                transform: translateY(-5px); 
                background: rgba(255,255,255,0.25);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }
            .agent h3 { font-size: 1.4em; margin-bottom: 15px; }
            .agent p { opacity: 0.9; line-height: 1.6; }
            .cta-section { text-align: center; margin-top: 50px; }
            .btn-primary { 
                background: rgba(255,255,255,0.2); 
                color: white; padding: 15px 30px; 
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 50px; text-decoration: none;
                font-size: 1.1em; font-weight: bold;
                transition: all 0.3s ease;
                display: inline-block;
            }
            .btn-primary:hover { 
                background: rgba(255,255,255,0.3);
                transform: scale(1.05);
            }
            .status { text-align: center; margin-top: 30px; opacity: 0.8; }
            @media (max-width: 768px) {
                .header h1 { font-size: 2em; }
                .agents-grid { grid-template-columns: 1fr; }
                .container { padding: 15px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌊 WaveAI Platform</h1>
                <p>Vos Agents IA Personnalisés - Surfez sur la Vague de l'Innovation</p>
            </div>
            
            <div class="agents-grid">
                <div class="agent" onclick="location.href='/login'">
                    <h3>🏄‍♂️ Alex Wave</h3>
                    <h4>Gmail & Productivité</h4>
                    <p>Gestion intelligente de vos emails, organisation des tâches, et optimisation de votre productivité quotidienne avec l'IA.</p>
                </div>
                
                <div class="agent" onclick="location.href='/login'">
                    <h3>🌊 Lina Wave</h3>
                    <h4>LinkedIn & Networking</h4>
                    <p>Optimisation de votre présence professionnelle, génération de contenu LinkedIn, et stratégies de networking personnalisées.</p>
                </div>
                
                <div class="agent" onclick="location.href='/login'">
                    <h3>🏄‍♀️ Marco Wave</h3>
                    <h4>Réseaux Sociaux</h4>
                    <p>Création de contenu viral, planification de publications, et analyse des performances sur tous vos réseaux sociaux.</p>
                </div>
                
                <div class="agent" onclick="location.href='/login'">
                    <h3>🌊 Sofia Wave</h3>
                    <h4>Calendrier & Planning</h4>
                    <p>Organisation parfaite de votre temps, planification intelligente, et synchronisation de tous vos agendas.</p>
                </div>
            </div>
            
            <div class="cta-section">
                <a href="/login" class="btn-primary">🚀 Commencer avec WaveAI</a>
            </div>
            
            <div class="status">
                <p>✅ <strong>Plateforme Déployée avec Succès</strong></p>
                <p>Version 1.0 - Multi-utilisateurs - Authentification Universelle</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/login')
def login():
    return '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Connexion - WaveAI</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; min-height: 100vh;
                display: flex; align-items: center; justify-content: center;
            }
            .login-container { 
                background: rgba(255,255,255,0.15); 
                padding: 40px; border-radius: 20px; 
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255,255,255,0.2);
                max-width: 400px; width: 90%;
                text-align: center;
            }
            .login-container h1 { margin-bottom: 30px; font-size: 2em; }
            .form-group { margin-bottom: 20px; text-align: left; }
            .form-group label { display: block; margin-bottom: 8px; font-weight: bold; }
            .form-group input { 
                width: 100%; padding: 12px; border: none; 
                border-radius: 8px; font-size: 1em;
                background: rgba(255,255,255,0.9);
                color: #333;
            }
            .btn-login { 
                width: 100%; padding: 15px; 
                background: rgba(255,255,255,0.2); 
                color: white; border: 2px solid rgba(255,255,255,0.3);
                border-radius: 8px; font-size: 1.1em; font-weight: bold;
                cursor: pointer; transition: all 0.3s ease;
            }
            .btn-login:hover { background: rgba(255,255,255,0.3); }
            .back-link { margin-top: 20px; }
            .back-link a { color: rgba(255,255,255,0.8); text-decoration: none; }
            .back-link a:hover { color: white; }
            .message { margin-top: 15px; padding: 10px; border-radius: 5px; }
            .success { background: rgba(0,255,0,0.2); border: 1px solid rgba(0,255,0,0.3); }
            .error { background: rgba(255,0,0,0.2); border: 1px solid rgba(255,0,0,0.3); }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>🌊 Connexion WaveAI</h1>
            <form id="loginForm">
                <div class="form-group">
                    <label for="email">Email :</label>
                    <input type="email" id="email" name="email" required 
                           placeholder="votre@email.com">
                </div>
                <button type="submit" class="btn-<span class="cursor">█</span>
