from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'waveai-super-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///waveai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèles
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

# Routes
@app.route('/')
def landing():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WaveAI Platform</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px; }
            .agent { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px; border-radius: 10px; cursor: pointer; }
            .btn { background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; border: none; border-radius: 25px; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>🌊 WaveAI Platform</h1>
        <p>Vos Agents IA Personnalisés</p>
        
        <div class="agent" onclick="location.href='/login'">
            <h3>🏄‍♂️ Alex Wave - Gmail & Productivité</h3>
        </div>
        
        <div class="agent" onclick="location.href='/login'">
            <h3>🌊 Lina Wave - LinkedIn & Networking</h3>
        </div>
        
        <div class="agent" onclick="location.href='/login'">
            <h3>🏄‍♀️ Marco Wave - Réseaux Sociaux</h3>
        </div>
        
        <div class="agent" onclick="location.href='/login'">
            <h3>🌊 Sofia Wave - Calendrier & Planning</h3>
        </div>
        
        <br<span class="cursor">█</span>
