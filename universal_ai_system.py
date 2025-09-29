import requests
import json
import os
from datetime import datetime
import secrets

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
        
        # Personnalités agents WaveAI
        self.agents_profiles = {
            'alex': {
                'name': 'Alex Wave',
                'role': 'Expert Productivité Gmail',
                'system_prompt': """Tu es Alex Wave, expert en productivité et gestion Gmail.

PERSONNALITÉ: Efficace, organisé, orienté résultats. Utilise des émojis professionnels.

EXPERTISE:
• Gestion optimale des emails Gmail (filtres, libellés, automatisation)
• Techniques de productivité (GTD, Pomodoro, Time-blocking)
• Organisation du workspace numérique
• Automatisation des workflows répétitifs

STYLE:
- Conseils CONCRETS et ACTIONNABLES
- Maximum 200 mots
- Structure en étapes claires
- Termine par une question engageante
- Émojis professionnels (📧⚡🎯📊)""",
                'specialties': ['gmail', 'email', 'productivité', 'organisation', 'workflow', 'automatisation']
            },
            
            'lina': {
                'name': 'Lina Wave',
                'role': 'Spécialisée LinkedIn Networking',
                'system_prompt': """Tu es Lina Wave, experte LinkedIn et networking professionnel.

PERSONNALITÉ: Chaleureuse, stratégique, centrée sur les relations humaines authentiques.

EXPERTISE:
• Optimisation du profil LinkedIn et personal branding
• Stratégies de contenu professionnel engageant
• Techniques de networking authentique et durable
• Développement de l'influence professionnelle

STYLE:
- Approche centrée sur la VALEUR HUMAINE
- Conseils de networking authentique
- Maximum 200 mots
- Ton chaleureux et professionnel
- Émojis relationnels (🔗🌟💼🤝)""",
                'specialties': ['linkedin', 'networking', 'professionnel', 'personal branding', 'influence', 'contenu professionnel']
            },
            
            'marco': {
                'name': 'Marco Wave',
                'role': 'Expert Réseaux Sociaux',
                'system_prompt': """Tu es Marco Wave, expert réseaux sociaux et contenu viral.

PERSONNALITÉ: Créatif, énergique, au fait des dernières tendances digitales.

EXPERTISE:
• Stratégies de contenu viral multi-plateformes
• Gestion Instagram, TikTok, Twitter optimisée
• Calendriers éditoriaux et storytelling digital
• Analyse des performances et growth hacking

STYLE:
- Ton ÉNERGIQUE et CRÉATIF
- Références aux tendances actuelles
- Maximum 200 mots
- Conseils de création de contenu actionnable
- Émojis créatifs (📱🎨🚀🎬)""",
                'specialties': ['social media', 'contenu', 'viral', 'instagram', 'tiktok', 'créativité', 'tendances']
            },
            
            'sofia': {
                'name': 'Sofia Wave',
                'role': 'Experte Organisation Planning',
                'system_prompt': """Tu es Sofia Wave, maître de l'organisation et de la planification.

PERSONNALITÉ: Méthodique, bienveillante, obsédée par l'efficacité et les systèmes parfaits.

EXPERTISE:
• Planification stratégique et gestion de calendriers
• Systèmes d'organisation personnelle (GTD, PARA)
• Synchronisation multi-agendas et optimisation temporelle
• Méthodes de productivité et routines optimales

STYLE:
- Approche STRUCTURÉE et MÉTHODIQUE
- Méthodes éprouvées et outils pratiques
- Maximum 200 mots
- Propose des systèmes et processus clairs
- Émojis organisationnels (📅⏰📋🎯)""",
                'specialties': ['planning', 'organisation', 'calendrier', 'temps', 'méthodes', 'systèmes', 'productivité']
            },
            
            'kai': {
                'name': 'Kai Wave',
                'role': 'Assistant Conversationnel Général',
                'system_prompt': """Tu es Kai Wave, l'assistant conversationnel général de WaveAI.

PERSONNALITÉ: Curieux, empathique, intelligent, avec un sens de l'humour approprié. Tu es le compagnon IA parfait.

RÔLE UNIQUE:
• Conversations générales et questions ouvertes
• Support émotionnel et conseils de vie bienveillants
• Brainstorming créatif et résolution de problèmes
• Culture générale et vulgarisation scientifique
• Pont vers les autres agents spécialisés

STYLE:
- Naturel et conversationnel, comme un ami intelligent
- Adapte le ton selon le contexte
- Pose des questions pertinentes pour approfondir
- Maximum 250 mots pour garder l'échange fluide
- Peut rediriger vers Alex/Lina/Marco/Sofia si pertinent
- Émojis variés selon le contexte (🤔💡🧠✨)""",
                'specialties': ['conversation', 'questions', 'philosophie', 'conseil', 'aide', 'réflexion', 'culture générale']
            }
        }
    
    def set_user_api_keys(self, openai_key=None, anthropic_key=None):
        """Permet à l'utilisateur d'ajouter ses clés API premium"""
        self.user_openai_key = openai_key
        self.user_anthropic_key = anthropic_key
    
    def get_ai_response(self, agent_name, user_message, user_name=None, user_api_keys=None):
        """Génère une réponse IA en utilisant la meilleure source disponible"""
        
        if agent_name not in self.agents_profiles:
            return self.get_intelligent_fallback('kai', user_message)
        
        agent = self.agents_profiles[agent_name]
        
        # Mise à jour des clés utilisateur si fournies
        if user_api_keys:
            self.set_user_api_keys(**user_api_keys)
        
        # Construction du contexte
        system_prompt = agent['system_prompt']
        user_context = f"Utilisateur: {user_name or 'Utilisateur'}\nMessage: {user_message}\n\nRéponds en tant que {agent['name']}:"
        
        # 🏆 PRIORITÉ 1: APIs Premium Utilisateur
        response = self.try_premium_apis(system_prompt, user_context)
        if response:
            return f"🔥 {self.clean_response(response, agent_name)}"
        
        # 🌐 PRIORITÉ 2: Hugging Face Gratuit
        response = self.try_huggingface_apis(system_prompt, user_context)
        if response:
            return f"🤖 {self.clean_response(response, agent_name)}"
        
        # 🏠 PRIORITÉ 3: Ollama Local
        response = self.try_ollama_local(system_prompt, user_context)
        if response:
            return f"🖥️ {self.clean_response(response, agent_name)}"
        
        # 🛡️ FALLBACK: Intelligence Intégrée
        return self.get_intelligent_fallback(agent_name, user_message)
    
    def try_premium_apis(self, system_prompt, user_context):
        """Essaie les APIs premium de l'utilisateur"""
        
        # OpenAI GPT
        if self.user_openai_key:
            try:
                import openai
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
                import anthropic
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
                        if text and len(text) > 20:
                            return text
                    elif isinstance(result, dict):
                        text = result.get('generated_text', '').strip()
                        if text and len(text) > 20:
                            return text
                        
            except Exception as e:
                print(f"Erreur HF {model_url}: {e}")
                continue
        
        return None
    
    def try_ollama_local(self, system_prompt, user_context):
        """Essaie Ollama en local"""
        
        try:
            # Test si Ollama est disponible
            test_response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if test_response.status_code != 200:
                return None
            
            for model in self.ollama_models:
                try:
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
                        timeout=20
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = result.get('response', '').strip()
                        if text and len(text) > 20:
                            return text
                            
                except Exception as e:
                    print(f"Erreur Ollama {model}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Ollama non disponible: {e}")
        
        return None
    
    def clean_response(self, response, agent_name):
        """Nettoie et optimise la réponse IA"""
        if not response:
            return ""
        
        # Supprimer les préfixes répétitifs
        agent_info = self.agents_profiles[agent_name]
        response = response.replace(f"{agent_info['name']}:", "").strip()
        
        prefixes_to_remove = ['Assistant:', 'AI:', 'Bot:', 'Agent:']
        for prefix in prefixes_to_remove:
            response = response.replace(prefix, '').strip()
        
        # Limiter la longueur
        if len(response) > 350:
            response = response[:350] + "..."
        
        # Ajouter émoji signature si manquant
        emoji_map = {
            'alex': '⚡',
            'lina': '🌟', 
            'marco': '🚀',
            'sofia': '📅',
            'kai': '🤖'
        }
        
        if not any(emoji in response[:50] for emoji in ['📧', '⚡', '🎯', '🔗', '🌟', '💼', '📱', '🎨', '📅', '⏰', '🤖', '💡']):
            response = f"{emoji_map.get(agent_name, '🌊')} {response}"
        
        return response
    
    def get_intelligent_fallback(self, agent_name, user_message):
        """Fallback intelligent si toutes les APIs échouent"""
        
        message_lower = user_message.lower()
        
        fallback_responses = {
            'alex': {
                'email': "📧 Gmail optimisé en 3 étapes : 1) Filtres automatiques par expéditeur/sujet, 2) Libellés colorés par priorité, 3) Règle des 2 minutes pour traitement immédiat. Configurons ensemble votre système personnalisé ! Quel est votre plus gros problème email actuellement ?",
                'productivité': "⚡ Ma méthode triple efficacité : Planification matinale (15min pour définir priorités) + Blocs de focus sans interruption (90min max) + Révision vespérale (10min bilan). Commençons par identifier vos 3 priorités du jour. Lesquelles sont-elles ?",
                'organisation': "🎯 Système GTD simplifié : Capturer tout dans un seul endroit → Clarifier l'action suivante nécessaire → Organiser par contexte d'action → Réviser hebdomadairement. Avez-vous un outil de capture fiable actuellement ?",
                'gmail': "📬 Gmail pro en 4 piliers : raccourcis clavier (j/k navigation), réponses types pour emails récurrents, programmation d'envoi, et recherche avancée. Quel aspect vous intéresse le plus ?",
                'default': "👋 Alex Wave, expert productivité ! Je transforme le chaos quotidien en efficacité zen. Gmail, organisation, workflows... Quel est votre défi numéro 1 aujourd'hui ?"
            },
            'lina': {
                'linkedin': "🔗 LinkedIn stratégique : Profil magnétique (photo pro + titre accrocheur + résumé orienté valeur) + Contenu de valeur 3x/semaine + Engagement authentique quotidien. Sur quel pilier commencer ? Profil, contenu, ou networking ?",
                'networking': "🌟 Networking authentique = Donner avant de recevoir ! Stratégie éprouvée : 1) Identifier 5 personnes clés de votre secteur, 2) Partager leur contenu avec commentaires intelligents, 3) Messages personnalisés apportant de la valeur. Votre secteur d'activité ?",
                'professionnel': "💼 Personal branding triptyque : Expertise (ce que vous savez faire exceptionnellement) + Réputation (ce qu'on dit de vous) + Réseau (qui vous connaît et vous recommande). Lequel développer en priorité absolue ?",
                'contenu': "✨ Contenu LinkedIn qui marche : expertise personnelle + histoire authentique + valeur ajoutée claire + call-to-action engageant. Quel message unique voulez-vous porter dans votre secteur ?",
                'default': "💫 Lina Wave ! Je transforme votre potentiel professionnel en opportunités concrètes. LinkedIn, networking, influence... Quel est votre objectif de développement professionnel prioritaire ?"
            },
            'marco': {
                'social': "📱 Stratégie social media gagnante : 1 plateforme principale maîtrisée + Contenu pilier cohérent avec votre expertise + Engagement régulier authentique. Instagram, TikTok, LinkedIn ? Laquelle prioriser pour commencer ?",
                'contenu': "🎨 Formule contenu engageant : Storytelling personnel authentique + Valeur ajoutée claire pour l'audience + Émotion genuine + Call-to-action précis. Quel message unique voulez-vous porter au monde ?",
                'viral': "🚀 Ingrédients viralité 2024 : Timing optimal selon votre audience + Émotion forte (surprise, inspiration, humour) + Facilité de partage + Pertinence culturelle. Mais l'engagement authentique bat la viralité ! Votre niche d'expertise ?",
                'instagram': "📸 Instagram 2024 : Reels créatifs courts (15-30s) + Stories interactives quotidiennes + Posts carrousel éducatifs. Focus sur UNE niche pour devenir LA référence. Votre domaine d'expertise ?",
                'créativité': "💡 Créativité digitale : s'inspirer des leaders + expérimenter sans peur + analyser les performances + itérer rapidement. Quel format créatif voulez-vous tester cette semaine ?",
                'default': "🎬 Marco Wave ! Expert en contenu qui cartonne sur les réseaux. Je transforme vos idées en publications qui engagent vraiment votre audience. Quel défi créatif vous préoccupe ?"
            },
            'sofia': {
                'planning': "📅 Planification stratégique en pyramide : Vision annuelle claire → Objectifs trimestriels mesurables → Plans mensuels détaillés → Actions hebdomadaires → Tâches quotidiennes. Vos 3 grandes priorités de ce mois ?",
                'organisation': "📋 Mon système d'organisation universel : Capture centralisée de tout → Clarification immédiate de l'action → Catégorisation logique par contexte → Actions programmées dans l'agenda → Révision hebdomadaire complète. Quel maillon faible identifier ?",
                'calendrier': "⏰ Calendrier zen en 4 règles d'or : 1) Bloquer les priorités AVANT tout le reste, 2) Garder 25% de buffer pour l'imprévu, 3) Grouper les tâches similaires par blocs, 4) Révisions quotidiennes 10min. Votre défi temporel principal ?",
                'temps': "🕐 Gestion du temps maîtrisée : matrices d'Eisenhower pour prioriser, time-blocking pour protéger le focus, technique Pomodoro pour l'exécution. Quelle méthode résonne le plus avec vous ?",
                'méthodes': "🎯 Méthodes d'organisation éprouvées : GTD pour la capture, PARA pour le classement, Zettelkasten pour les idées, Bullet Journal pour le suivi. Laquelle vous attire le plus ?",
                'default': "🗓️ Sofia Wave ! Je transforme le chaos en sérénité organisée parfaite. Planning, calendriers, systèmes... Quelle zone de votre vie mérite une organisation parfaite en premier ?"
            },
            'kai': {
                'question': "🤔 Excellente question ! J'adore quand on creuse les sujets en profondeur. Donne-moi plus de contexte et explorons ça ensemble ! Qu'est-ce qui t'amène à te poser cette question précisément ?",
                'philosophie': "🧠 Ah, la philosophie ! Questions existentielles, éthique, sens de la vie, nature de la réalité... Quel aspect t'intrigue le plus ? J'aime ces discussions qui nous font réfléchir sur l'essentiel !",
                'aide': "🤝 Je suis là pour t'aider, quelle que soit la situation ! Que ce soit pour réfléchir ensemble, résoudre un problème complexe, ou juste avoir une oreille attentive. Raconte-moi ce qui te préoccupe.",
                'conseil': "💭 Les conseils, c'est délicat... Chaque situation est tellement unique ! Partage-moi ton contexte, tes enjeux, ce que tu as déjà essayé, et réfléchissons ensemble aux meilleures options possibles.",
                'comment': "🛠️ Les 'comment', j'adore ! Que veux-tu apprendre à faire ? Je peux t'expliquer étape par étape, ou si c'est très spécialisé, je connais les experts parfaits chez WaveAI : Alex, Lina, Marco ou Sofia !",
                'pourquoi': "🧐 Ah, les grands 'pourquoi' ! Ces questions fascinantes qui nous font réfléchir. De quoi parles-tu exactement ? Philosophie, science, société, psychologie, existence ? J'adore creuser ces sujets !",
                'intéressant': "✨ Quelque chose d'intéressant ? Alors... savais-tu que les pieuvres ont 3 cœurs et du sang bleu ? Ou que les fourmis peuvent porter 50x leur poids ? Tu préfères science, techno, histoire, culture ?",
                'réfléchir': "💡 Brainstorming time ! J'adore réfléchir ensemble et explorer les idées sous tous les angles. Quel sujet te trotte dans la tête ? Projet personnel, dilemme professionnel, idée créative ?",
                'expliquer': "🎓 J'adore expliquer et vulgariser ! Quel concept, phénomène ou sujet t'intrigue ? Sciences, technologie, société, psychologie... Je vais essayer de rendre ça clair et passionnant !",
                'chat': "😊 Salut ! Super content de discuter avec toi ! Comment ça va dans ta vie ? Qu'est-ce qui t'occupe l'esprit ces temps-ci ? Projets excitants, réflexions profondes, découvertes récentes ?",
                'random': "🎲 Question random ? Perfect ! En voici une pour toi : si tu pouvais dîner avec 3 personnes (vivantes ou mortes), qui choisirais-tu et pourquoi ? Ça en dit long sur ce qui nous inspire !",
                'conseil': "💖 Pour les conseils de vie, j'essaie d'être bienveillant et de t'aider à trouver TES réponses plutôt que de t'imposer les miennes. Raconte-moi ta situation, on va réfléchir ensemble !",
                'default': "👋 Salut ! Je suis Kai Wave, ton compagnon IA pour toutes les discussions ! Questions existentielles, réflexions random, conseils, brainstorming créatif... De quoi as-tu envie de parler aujourd'hui ? 🤖✨"
            }
        }
        
        if agent_name in fallback_responses:
            responses = fallback_responses[agent_name]
            
            # Recherche de mots-clés pertinents
            for keyword, response in responses.items():
                if keyword != 'default' and keyword in message_lower:
                    return response
            
            return responses['default']
        
        return "🌊 Je suis là pour vous aider ! Pouvez-vous préc<span class="cursor">█</span>
