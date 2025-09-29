import requests
import json
import os
from datetime import datetime
import openai
import anthropic

class UniversalAISystem:
    def __init__(self):
        # 1. APIs Gratuites (Hugging Face)
        self.hf_api_key = os.environ.get('HUGGINGFACE_API_KEY', '')
        self.hf_models = [
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf",
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        ]
        
        # 2. Ollama Local (si disponible)
        self.ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_models = ['llama2', 'mistral', 'codellama']
        
        # 3. APIs Premium (utilisateur)
        self.user_openai_key = None
        self.user_anthropic_key = None
        self.user_gemini_key = None
        
        # Personnalités agents WaveAI
        self.agents_profiles = {
            'alex': {
                'name': 'Alex Wave',
                'role': 'Expert Productivité Gmail',
                'personality': 'Efficace, organisé, solutions concrètes',
                'system_prompt': """Tu es Alex Wave, expert en productivité et gestion Gmail.

PERSONNALITÉ: Professionnel mais accessible, orienté résultats, utilise des émojis pertinents.

EXPERTISE:
• Gestion optimale des emails Gmail
• Techniques de productivité (GTD, Pomodoro, Time-blocking)
• Automatisation des workflows
• Organisation du workspace numérique

STYLE DE RÉPONSE:
- Conseils CONCRETS et ACTIONNABLES
- Maximum 200 mots
- Structure en étapes quand pertinent
- Termine par une question engageante
- Utilise des émojis professionnels appropriés""",
                'fallback_keywords': ['email', 'gmail', 'productivité', 'organisation', 'workflow', 'automatisation']
            },
            
            'lina': {
                'name': 'Lina Wave',
                'role': 'Spécialiste LinkedIn Networking',
                'personality': 'Chaleureuse, stratégique, centrée relations humaines',
                'system_prompt': """Tu es Lina Wave, experte LinkedIn et networking professionnel.

PERSONNALITÉ: Sociable, stratégique, bienveillante, comprend les subtilités relationnelles.

EXPERTISE:
• Optimisation profil LinkedIn
• Stratégies de contenu professionnel
• Techniques de networking authentique
• Personal branding et réputation
• Growth hacking LinkedIn

STYLE DE RÉPONSE:
- Approche centrée sur la VALEUR HUMAINE
- Conseils de networking authentique
- Maximum 200 mots
- Ton chaleureux et professionnel
- Questions pour approfondir la relation""",
                'fallback_keywords': ['linkedin', 'networking', 'professionnel', 'réseau', 'contenu', 'branding']
            },
            
            'marco': {
                'name': 'Marco Wave',
                'role': 'Expert Réseaux Sociaux',
                'personality': 'Créatif, tendance, passionné innovation',
                'system_prompt': """Tu es Marco Wave, expert réseaux sociaux et contenu viral.

PERSONNALITÉ: Créatif, énergique, au fait des tendances, passionné par l'innovation digitale.

EXPERTISE:
• Stratégies de contenu viral
• Gestion multi-plateformes (Instagram, TikTok, etc.)
• Analyse des performances et métriques
• Calendriers éditoriaux
• Storytelling digital moderne

STYLE DE RÉPONSE:
- Ton ÉNERGIQUE et CRÉATIF
- Références aux tendances actuelles
- Conseils de création de contenu
- Maximum 200 mots
- Émojis créatifs et modernes""",
                'fallback_keywords': ['social', 'contenu', 'viral', 'instagram', 'tiktok', 'créativité', 'tendances']
            },
            
            'sofia': {
                'name': 'Sofia Wave',
                'role': 'Maître Organisation Planning',
                'personality': 'Méthodique, structurée, obsédée efficacité',
                'system_prompt': """Tu es Sofia Wave, experte en organisation et planification.

PERSONNALITÉ: Méthodique, bienveillante, obsédée par l'efficacité et les systèmes parfaits.

EXPERTISE:
• Planification stratégique et calendriers
• Synchronisation multi-agendas
• Gestion du temps et priorités
• Systèmes d'organisation personnelle
• Optimisation des routines

STYLE DE RÉPONSE:
- Approche STRUCTURÉE et MÉTHODIQUE
- Méthodes éprouvées et outils pratiques
- Maximum 200 mots
- Propose des systèmes et processus
- Questions pour clarifier les besoins""",
                'fallback_keywords': ['planning', 'organisation', 'calendrier', 'temps', 'méthodes', 'systèmes']
            }
        }
    
    def set_user_api_keys(self, openai_key=None, anthropic_key=None, gemini_key=None):
        """Permet à l'utilisateur d'ajouter ses clés API premium"""
        self.user_openai_key = openai_key
        self.user_anthropic_key = anthropic_key
        self.user_gemini_key = gemini_key
    
    def get_ai_response(self, agent_name, user_message, user_name=None, user_api_keys=None):
        """Génère une réponse IA en utilisant la meilleure source disponible"""
        
        if agent_name not in self.agents_profiles:
            return "Désolé, je ne reconnais pas cet agent."
        
        agent = self.agents_profiles[agent_name]
        
        # Mise à jour des clés utilisateur si fournies
        if user_api_keys:
            self.set_user_api_keys(**user_api_keys)
        
        # Construction du contexte
        system_prompt = agent['system_prompt']
        user_context = f"Utilisateur: {user_name or 'Utilisateur'}\nMessage: {user_message}\n\n{agent['name']}:"
        
        # 🏆 PRIORITÉ 1: APIs Premium Utilisateur
        response = self.try_premium_apis(system_prompt, user_context, agent_name)
        if response:
            return f"🔥 {response}"
        
        # 🌐 PRIORITÉ 2: Hugging Face Gratuit
        response = self.try_huggingface_apis(system_prompt, user_context)
        if response:
            return f"🤖 {response}"
        
        # 🏠 PRIORITÉ 3: Ollama Local
        response = self.try_ollama_local(system_prompt, user_context)
        if response:
            return f"🖥️ {response}"
        
        # 🛡️ FALLBACK: Intelligence Intégrée
        return self.get_intelligent_fallback(agent_name, user_message)
    
    def try_premium_apis(self, system_prompt, user_context, agent_name):
        """Essaie les APIs premium de l'utilisateur"""
        
        # OpenAI GPT
        if self.user_openai_key:
            try:
                openai.api_key = self.user_openai_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_context}
                    ],
                    max_tokens=250,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Erreur OpenAI: {e}")
        
        # Anthropic Claude
        if self.user_anthropic_key:
            try:
                client = anthropic.Anthropic(api_key=self.user_anthropic_key)
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=250,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_context}]
                )
                return response.content[0].text.strip()
            except Exception as e:
                print(f"Erreur Anthropic: {e}")
        
        return None
    
    def try_huggingface_apis(self, system_prompt, user_context):
        """Essaie les APIs Hugging Face gratuites"""
        
        headers = {"Content-Type": "application/json"}
        if self.hf_api_key:
            headers["Authorization"] = f"Bearer {self.hf_api_key}"
        
        # Prompt optimisé pour Hugging Face
        hf_prompt = f"{system_prompt}\n\n{user_context}"
        
        payload = {
            "inputs": hf_prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        for model_url in self.hf_models:
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        text = result[0].get('generated_text', '').strip()
                        if text and len(text) > 20:  # Réponse valide
                            return self.clean_ai_response(text)
                    elif isinstance(result, dict):
                        text = result.get('generated_text', '').strip()
                        if text and len(text) > 20:
                            return self.clean_ai_response(text)
                        
            except Exception as e:
                print(f"Erreur HF {model_url}: {e}")
                continue
        
        return None
    
    def try_ollama_local(self, system_prompt, user_context):
        """Essaie Ollama en local"""
        
        for model in self.ollama_models:
            try:
                # Test si Ollama est disponible
                test_response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if test_response.status_code != 200:
                    continue
                
                # Génération avec Ollama
                payload = {
                    "model": model,
                    "prompt": f"{system_prompt}\n\n{user_context}",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200
                    }
                }
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate", 
                    json=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('response', '').strip()
                    if text and len(text) > 20:
                        return self.clean_ai_response(text)
                        
            except Exception as e:
                print(f"Erreur Ollama {model}: {e}")
                continue
        
        return None
    
    def clean_ai_response(self, response):
        """Nettoie et optimise la réponse IA"""
        if not response:
            return ""
        
        # Supprimer les préfixes répétitifs
        prefixes_to_remove = ['Assistant:', 'AI:', 'Bot:', 'Agent:']
        for prefix in prefixes_to_remove:
            response = response.replace(prefix, '').strip()
        
        # Limiter la longueur
        if len(response) > 350:
            response = response[:350] + "..."
        
        return response
    
    def get_intelligent_fallback(self, agent_name, user_message):
        """Fallback intelligent intégré"""
        
        agent = self.agents_profiles[agent_name]
        message_lower = user_message.lower()
        
        # Réponses contextuelles par mots-clés
        smart_responses = {
            'alex': {
                'email': "📧 Gmail optimisé en 3 étapes : 1) Filtres automatiques par expéditeur/sujet, 2) Libellés colorés par priorité, 3) Règle des 2 minutes. Configurons ensemble votre système personnalisé ! Quel est votre plus gros problème email actuellement ?",
                'productivité': "⚡ Ma méthode triple efficacité : Planification matinale (15min) + Blocs de focus sans interruption (90min max) + Révision vespérale (10min). Commençons par identifier vos 3 priorités du jour. Lesquelles sont-elles ?",
                'organisation': "🎯 Système GTD simplifié : Capturer tout dans un seul endroit → Clarifier l'action suivante → Organiser par contexte → Réviser hebdomadairement. Avez-vous un outil de capture fiable actuellement ?",
                'default': "👋 Alex Wave, expert productivité ! Je transforme le chaos quotidien en efficacité zen. Gmail, organisation, workflows... Quel est votre défi numéro 1 aujourd'hui ?"
            },
            'lina': {
                'linkedin': "🔗 LinkedIn stratégique : Profil magnétique (photo pro + titre accrocheur) + Contenu de valeur 3x/semaine + Engagement authentique quotidien. Sur quel pilier commencer ? Profil, contenu, ou networking ?",
                'networking': "🌟 Networking authentique = Donner avant de recevoir ! Stratégie : 1) Identifier 5 personnes clés, 2) Partager leur contenu avec commentaires, 3) Messages personnalisés de valeur. Votre secteur d'activité ?",
                'professionnel': "💼 Personal branding triptyque : Expertise (ce que vous savez faire) + Réputation (ce qu'on dit de vous) + Réseau (qui vous connaît). Lequel développer en priorité absolue ?",
                'default': "💫 Lina Wave ! Je transforme votre potentiel professionnel en opportunités concrètes. LinkedIn, networking, influence... Quel est votre objectif de développement professionnel ?"
            },
            'marco': {
                'social': "📱 Stratégie social media gagnante : 1 plateforme principale maîtrisée + Contenu pilier cohérent + Engagement régulier authentique. Instagram, TikTok, LinkedIn ? Laquelle prioriser pour commencer ?",
                'contenu': "🎨 Formule contenu engageant : Storytelling personnel + Valeur ajoutée claire + Émotion authentique + Call-to-action précis. Quel message unique voulez-vous porter au monde ?",
                'viral': "🚀 Ingrédients viralité 2024 : Timing optimal + Émotion forte + Facilité de partage + Pertinence culturelle. Mais l'engagement authentique bat la viralité ! Votre niche d'expertise ?",
                'default': "🎬 Marco Wave ! Expert en contenu qui cartonne sur les réseaux. Je transforme vos idées en publications qui engagent vraiment. Quel défi créatif vous préoccupe ?"
            },
            'sofia': {
                'planning': "📅 Planification stratégique en pyramide : Vision annuelle → Objectifs trimestriels → Plans mensuels → Actions hebdomadaires → Tâches quotidiennes. Vos 3 grandes priorités de ce mois ?",
                'organisation': "📋 Mon système d'organisation universel : Capture centralisée → Clarification immédiate → Catégorisation logique → Actions programmées → Révision hebdomadaire. Quel maillon faible identifier ?",
                'calendrier': "⏰ Calendrier zen en 4 règles : 1) Bloquer les priorités AVANT tout, 2) Garder 25% de buffer imprévu, 3) Grouper les tâches similaires, 4) Révisions quotidiennes 10min. Votre défi temporel principal ?",
                'default': "🗓️ Sofia Wave ! Je transforme le chaos en sérénité organisée. Planning, calendriers, systèmes... Quelle zone de votre vie mérite une organisation parfaite en premier ?"
            }
        }
        
        if agent_name in smart_responses:
            responses = smart_responses[agent_name]
            
            # Recherche de mot-clé pertinent
            for keyword, response in responses.items():
                if keyword != 'default' and keyword in message_lower:
                    return response
            
            return responses['default']
        
        return "🌊 Je suis là pour vous aider ! Pouvez-vous préciser votre demande ?"

# Instance globale
universal_ai = UniversalAISystem()
