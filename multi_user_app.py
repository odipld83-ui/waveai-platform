from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

# Routes de base
@app.route('/')
def landing():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌊 WaveAI Platform</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px; }
            .container { max-width: 800px; margin: 0 auto; }
            .agent { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌊 WaveAI Platform</h1>
            <p>Votre plateforme d'agents IA multi-utilisateurs</p>
            
            <div class="agent">
                <h3>🏄‍♂️ Alex Wave - Gmail & Productivité</h3>
                <p>Gestion intelligente de vos emails et tâches</p>
            </div>
            
            <div class="agent">
                <h3>🌊 Lina Wave - LinkedIn & Networking</h3>
                <p>Optimisation de votre présence professionnelle</p>
            </div>
            
            <div class="agent">
                <h3>🏄‍♀️ Marco Wave - Réseaux Sociaux</h3>
                <p>Stratégie et contenu pour vos réseaux</p>
            </div>
            
            <div class="agent">
                <h3>🌊 Sofia Wave - Calendrier & Planning</h3>
                <p>Organisation parfaite de votre temps</p>
            </div>
            
            <p><strong>✅ Déploiement Render réussi !</strong></p>
            <p>Version de test - Fonctionnalités complètes bientôt disponibles</p>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'WaveAI Platform fonctionne !',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=False)
