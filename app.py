from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🌊 WaveAI Platform</h1>
    <p>Votre plateforme d'agents IA est en cours de configuration...</p>
    <p>Bravo ! Le déploiement fonctionne !</p>
    '''

if __name__ == '__main__':
    app.run(debug=False)
