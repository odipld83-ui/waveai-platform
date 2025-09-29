# 🌊 WaveAI - Plateforme d'Agents IA Multi-utilisateurs

> **Surfez sur la Vague de l'Intelligence Artificielle**

WaveAI est une plateforme moderne d'agents IA spécialisés qui révolutionne votre productivité. Avec 4 agents experts (Gmail, LinkedIn, Réseaux Sociaux, Calendrier), une authentification universelle et une interface temps réel, WaveAI transforme votre workflow quotidien.

## 🚀 Fonctionnalités Principales

### ✨ **4 Agents IA Spécialisés**
- **📧 Alex Wave** - Expert Gmail & Productivité
- **💼 Lina Wave** - Spécialiste LinkedIn & Networking  
- **📱 Marco Wave** - Gestionnaire Réseaux Sociaux
- **📅 Sofia Wave** - Organisatrice Calendrier & Planning

### 🔐 **Authentification Universelle**
- Support de **tous les providers email** (Gmail, Outlook, Yahoo, etc.)
- Liens magiques sécurisés
- Connexion rapide en 30 secondes
- Mode démo inclus pour tests

### 🎨 **Interface Moderne**
- Design **thème océan** responsive
- Chat temps réel avec SocketIO
- Animations fluides et intuitives
- Support mobile et desktop

### ⚙️ **Architecture Robuste**
- **Multi-utilisateurs** avec sessions isolées
- Base de données PostgreSQL
- Système de versions automatique
- Gestion d'erreurs complète

## 📋 Prérequis

- **Python 3.8+**
- **Compte GitHub** (gratuit)
- **Compte Render** (gratuit)
- Navigateur web moderne

## 🛠️ Installation Rapide

### Option 1 : Déploiement Direct sur Render

1. **Téléchargez le ZIP** complet WaveAI
2. **Créez un repository GitHub** et uploadez les fichiers
3. **Connectez à Render** pour déploiement automatique
4. **Configurez les variables** d'environnement
5. **Accédez à votre plateforme** en ligne !

### Option 2 : Installation Locale

```bash
# Cloner le repository
git clone https://github.com/votre-username/waveai-platform.git
cd waveai-platform

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditez .env avec vos configurations

# Initialiser la base de données
python multi_user_app.py
```

## 🌐 Déploiement sur Render

### Étape 1 : Préparation GitHub

1. **Créez un nouveau repository** sur GitHub
2. **Uploadez tous les fichiers** WaveAI dans le repository
3. **Vérifiez la structure** :
   ```
   votre-repo/
   ├── multi_user_app.py
   ├── requirements.txt
   ├── render.yaml
   ├── .env.example
   ├── templates/
   │   ├── base.html
   │   ├── landing.html
   │   ├── login_universal.html
   │   ├── dashboard.html
   │   └── agent.html
   └── static/
       ├── style.css
       └── script.js
   ```

### Étape 2 : Configuration Render

1. **Connectez-vous à Render** : https://render.com
2. **Créez un nouveau Web Service**
3. **Connectez votre repository GitHub**
4. **Configuration automatique** détectée via `render.yaml`

### Étape 3 : Variables d'Environnement

Dans Render, configurez ces variables :

```env
FLASK_ENV=production
SECRET_KEY=votre-cle-super-secrete-longue-et-aleatoire
DATABASE_URL=postgresql://... (automatique avec Render)
```

**Optionnel (pour production avancée) :**
```env
SENDGRID_API_KEY=SG.votre-cle-sendgrid
SENDGRID_FROM_EMAIL=noreply@votredomaine.com
```

### Étape 4 : Déploiement

1. **Build automatique** démarré par Render
2. **Base de données PostgreSQL** créée automatiquement
3. **Lien HTTPS** généré : `https://waveai-[nom].onrender.com`
4. **Certificat SSL** automatique

## 🔧 Configuration

### Base de Données

WaveAI utilise **PostgreSQL** en production (automatique sur Render) et **SQLite** en local.

Les tables sont créées automatiquement au premier démarrage :
- `users` - Informations utilisateurs
- `app_versions` - Système de versions
- `magic_links` - Liens d'authentification

### Email (Production)

Pour l'envoi réel d'emails en production :

1. **Créez un compte SendGrid** (gratuit)
2. **Obtenez votre API Key**
3. **Configurez les variables** :
   ```env
   SENDGRID_API_KEY=SG.votre-cle
   SENDGRID_FROM_EMAIL=noreply@votredomaine.com
   ```

### Domaine Personnalisé

Sur Render, vous pouvez configurer votre propre domaine :

1. **Ajoutez votre domaine** dans Render
2. **Configurez les DNS** selon les instructions
3. **Certificat SSL automatique**

## 🎯 Utilisation

### Page d'Accueil

```url
https://votre-waveai.onrender.com/
```

- Présentation des 4 agents Wave
- Démonstration des fonctionnalités
- Bouton de connexion universelle

### Connexion

```url
https://votre-waveai.onrender.com/login
```

- Entrez **n'importe quel email** valide
- Détection automatique du provider
- **Mode démo** : connexion instantanée
- **Production** : lien magique envoyé par email

### Tableau de Bord

```url
https://votre-waveai.onrender.com/dashboard
```

- Vue d'ensemble des 4 agents
- Statistiques personnalisées
- Actions rapides
- Informations système

### Chat avec Agents

```url
https://votre-waveai.onrender.com/agents/alex
https://votre-waveai.onrender.com/agents/lina
https://votre-waveai.onrender.com/agents/marco
https://votre-waveai.onrender.com/agents/sofia
```

- Interface de chat temps réel
- Suggestions personnalisées par agent
- Sidebar avec conseils et spécialités

## 🤖 Agents IA Disponibles

### 📧 **Alex Wave - Gmail & Productivité**

**Spécialités :**
- Organisation automatique des emails
- Réponses intelligentes et templates
- Rappels contextuels
- Workflows de productivité

**Utilisation :**
```
"Aide-moi à organiser ma boîte email"
"Crée des réponses automatiques pour mes emails fréquents"
"Rappelle-moi de répondre à cet email important demain"
```

### 💼 **Lina Wave - LinkedIn & Networking**

**Spécialités :**
- Messages LinkedIn personnalisés
- Analyse de réseau professionnel
- Stratégie de contenu
- Lead generation

**Utilisation :**
```
"Analyse mon réseau LinkedIn"
"Écris un message personnalisé pour ce prospect"
"Suggère une stratégie de contenu pour ma niche"
```

### 📱 **Marco Wave - Réseaux Sociaux**

**Spécialités :**
- Planification de posts multi-plateformes
- Analyse d'engagement
- Veille des tendances
- Optimisation de contenu

**Utilisation :**
```
"Planifie mes posts sur les réseaux sociaux cette semaine"
"Analyse les tendances actuelles dans mon secteur"
"Optimise ce post pour Instagram et Twitter"
```

### 📅 **Sofia Wave - Calendrier & Planning**

**Spécialités :**
- Planification intelligente
- Synchronisation multi-calendriers
- Rappels contextuels
- Optimisation du temps

**Utilisation :**
```
"Optimise mon planning de la semaine"
"Synchronise mes calendriers Google et Outlook"
"Trouve le meilleur créneau pour cette réunion"
```

## 🔒 Sécurité

### Authentification

- **Liens magiques** avec expiration (15 minutes)
- **Tokens sécurisés** générés automatiquement
- **Sessions chiffrées** avec clés rotatives
- **Validation IP** pour sécurité renforcée

### Données

- **Chiffrement HTTPS** obligatoire (Render)
- **Séparation utilisateurs** en base de données
- **Pas de stockage** de mots de passe
- **Logs sécurisés** sans données sensibles

### Infrastructure

- **Render Cloud** : infrastructure sécurisée
- **PostgreSQL** : base de données robuste
- **Auto-scaling** selon la charge
- **Monitoring** et alertes automatiques

## 📊 API Endpoints

### Authentification

```http
POST /api/auth/magic-link
Content-Type: application/json

{
    "email": "utilisateur@exemple.com"
}
```

### Informations Système

```http
GET /api/version
GET /api/stats
```

### Chat Agents (WebSocket)

```javascript
socket.emit('agent_message', {
    agent_id: 'alex',
    message: 'Votre message'
});

socket.on('agent_response', function(data) {
    console.log(data.message);
});
```

## 🛠️ Développement

### Structure du Projet

```
waveai-platform/
├── 📱 multi_user_app.py      # Application Flask principale
├── 🔐 universal_auth.py      # Système d'authentification (optionnel)
├── ⚙️ requirements.txt       # Dépendances Python
├── 🚀 render.yaml           # Configuration Render
├── 📝 .env.example          # Variables d'environnement
├── 📚 README.md             # Cette documentation
├── templates/                # Templates Jinja2
│   ├── 🏠 base.html         # Template de base
│   ├── 🌊 landing.html      # Page d'accueil
│   ├── 🔑 login_universal.html # Connexion
│   ├── 📊 dashboard.html    # Tableau de bord
│   └── 🤖 agent.html        # Interface chat
└── static/                   # Assets statiques
    ├── 🎨 style.css         # Styles CSS
    └── ⚡ script.js         # JavaScript
```

### Technologies Utilisées

- **Backend** : Flask, SQLAlchemy, SocketIO
- **Frontend** : HTML5, CSS3, JavaScript ES6+
- **UI Framework** : Bootstrap 5
- **Base de données** : PostgreSQL / SQLite
- **Déploiement** : Render Cloud
- **Real-time** : WebSocket (SocketIO)

### Personnalisation

#### Ajout d'un Nouvel Agent

1. **Modifiez** `multi_user_app.py` :
```python
agents = {
    'nouveau': {
        'name': 'Nouveau Agent',
        'title': 'Spécialité Agent',
        'description': 'Description...',
        'color': '#FF5722',
        'icon': '🤖',
        'features': ['Feature 1', 'Feature 2']
    }
}
```

2. **Ajoutez la route** :
```python
@app.route('/agents/nouveau')
def nouveau_agent():
    # Logique spécifique
```

3. **Intégrez dans les templates** dashboard et navigation

#### Modification du Thème

Variables CSS dans `static/style.css` :
```css
:root {
    --wave-primary: #VOTRE_COULEUR;
    --wave-secondary: #VOTRE_COULEUR;
    /* ... */
}
```

## 🧪 Tests

### Tests Locaux

```bash
# Lancer l'application en mode debug
python multi_user_app.py

# Accéder à http://localhost:5000
```

### Tests de Charge

```bash
# Installer siege
sudo apt-get install siege

# Test de charge
siege -c 10 -r 10 http://localhost:5000/
```

## 📈 Monitoring

### Render Dashboard

- **Metrics** : CPU, RAM, trafic
- **Logs** : Erreurs et performances
- **Auto-scaling** : Ajustement automatique

### Logs Application

```python
# Logs intégrés dans multi_user_app.py
import logging
logging.basicConfig(level=logging.INFO)
```

## 🚨 Dépannage

### Erreurs Communes

**❌ "Module not found"**
```bash
pip install -r requirements.txt
```

**❌ "Database connection error"**
- Vérifiez `DATABASE_URL` dans les variables d'environnement
- Render : attendez la création automatique de PostgreSQL

**❌ "Port already in use"**
```bash
# Trouvez le processus
lsof -i :5000
# Tuez le processus
kill -9 PID
```

### Problèmes Render

**❌ Build échoue**
- Vérifiez `requirements.txt`
- Consultez les logs de build dans Render

**❌ Application ne démarre pas**
- Vérifiez les variables d'environnement
- Consultez les logs d'application

## 🆕 Mises à Jour

### Système de Versions Automatique

WaveAI inclut un système de versions intégré :

```python
# Version actuelle stockée en base
version = AppVersion.query.filter_by(is_current=True).first()
```

### Déploiement des Mises à Jour

1. **Modifiez votre code** localement
2. **Commitez sur GitHub**
3. **Render redéploie automatiquement**
4. **Version mise à jour** dans l'interface

## 🤝 Contribution

### Signaler un Bug

Créez une issue GitHub avec :
- Description du problème
- Étapes de reproduction
- Logs d'erreur
- Environnement (local/Render)

### Proposer une Fonctionnalité

1. **Fork** le repository
2. **Créez une branche** : `feature/nouvelle-fonctionnalite`
3. **Développez** avec tests
4. **Créez une Pull Request**

## 📞 Support

- **Documentation** : Ce README.md
- **Issues GitHub** : Pour bugs et questions
- **Render Support** : https://render.com/docs
- **Community** : Discord/Slack (liens à venir)

## 📜 Licence

```
MIT License

Copyright (c) 2024 WaveAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🎉 Félicitations !

Vous avez maintenant une plateforme WaveAI complète et opérationnelle ! 

**Prochaines étapes suggérées :**

1. 🚀 **Déployez sur Render** et obtenez votre lien public
2. 🎨 **Personnalisez le design** selon vos besoins
3. 🤖 **Intégrez de vraies APIs IA** (OpenAI, Anthropic, etc.)
4. 📧 **Configurez SendGrid** pour l'envoi d'emails réels
5. 📊 **Ajoutez Google Analytics** pour le suivi
6. 🌍 **Configurez un domaine personnalisé**

---

**🌊 Surfez sur la Vague de l'IA avec WaveAI !**

*Développé avec ❤️ par l'équipe WaveAI*
