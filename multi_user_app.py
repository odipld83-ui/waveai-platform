from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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
    try:
        return render_template('landing.html')
    except:
        return '<h1>🌊 WaveAI Platform</h1><p>Templates en cours de création...</p><a href="/test">Test API</a>'

@app.route('/login')
def login():
    return '<h1>🌊 Connexion WaveAI</h1><p>Page de connexion en construction</p><a href="/">← Retour</a>'

@app.route('/dashboard')
def dashboard():
    return '<h1>🌊 Dashboard WaveAI</h1><p>Dashboard en construction</p><a href="/">← Retour</a>'

@app.route('/test')
def test():
    return jsonify({
        'status': 'success', 
        'message': 'WaveAI Platform fonctionne parfaitement !', 
        'version': '1.0',
        'agents': ['Alex Wave', 'Lina Wave', 'Marco Wave', 'Sofia Wave']
    })

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
