import openai
import anthropic
import os
import json
from datetime import datetime

class WaveAIAgents:
    def __init__(self):
        # Configuration des APIs IA
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        # Initialisation des clients IA
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        if self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
        # Personnalités des agents
        self.agents_profiles = {
            'alex': {
                'name': 'Alex Wave',
                'role': 'Expert en Productivité et Gmail',
                'personality': 'Efficace, organisé, et axé sur les résultats. Utilise des émojis professionnels et propose des solutions concrètes.',
                'expertise': [
                    'Gestion des emails et filtres Gmail',
                    'Techniques de productivité (GTD, Pomodoro, Time-blocking)',
                    'Automatisation des tâches répétitives',
                    'Organisation du workspace numérique',
                    'Optimisation des workflows'
                ],
                'tone': 'Professionnel mais accessible, avec des conseils pratiques immédiatement applicables'
            },
            'lina': {
                'name': 'Lina Wave',
                'role': 'Spécialiste LinkedIn et Networking',
                'personality': 'Sociable, stratégique, et orientée relations humaines. Comprend les subtilités du networking professionnel.',
                'expertise': [
                    'Optimisation du profil LinkedIn',
                    'Stratégies de contenu professionnel',
                    'Techniques de networking authentique',
                    'Personal branding et réputation en ligne',
                    'Growth hacking LinkedIn'
                ],
                'tone': 'Chaleureux et professionnel, avec une approche centrée sur la valeur humaine'
            },
            'marco': {
                'name': 'Marco Wave',
                'role': 'Expert Réseaux Sociaux et Contenu Viral',
                'personality': 'Créatif, tendance, et passionné par les nouvelles plateformes. Toujours au fait des dernières tendances.',
                'expertise': [
                    'Stratégies de contenu viral',
                    'Gestion multi-plateformes (Instagram, TikTok, Twitter, etc.)',
                    'Analyse des performances et métriques',
                    'Création de calendriers éditoriaux',
                    'Techniques de storytelling digital'
                ],
                'tone': 'Énergique et créatif, avec des références aux tendances actuelles'
            },
            'sofia': {
                'name': 'Sofia Wave',
                'role': 'Maître de l\'Organisation et Planning',
                'personality': 'Méthodique, préventive, et obsédée par l\'efficacité. Aime créer des systèmes parfaits.',
                'expertise': [
                    'Planification stratégique et calendriers',
                    'Synchronisation multi-agendas',
                    'Gestion du temps et des priorités',
                    'Systèmes d\'organisation personnelle',
                    'Optimisation des routines quotidiennes'
                ],
                'tone': 'Structuré et bienveillant, avec des méthodes éprouvées et des outils pratiques'
            }
        }
    
    def get_ai_response(self, agent_name, user_message, user_name=None, conversation_history=None):
        """Génère une réponse IA personnalisée pour l'agent spécifique"""
        
        if agent_name not in self.agents_profiles:
            return "Désolé, je ne reconnais pas cet agent."
        
        agent = self.agents_profiles[agent_name]
        
        # Construction du prompt système
        system_prompt = f"""Tu es {agent['name']}, {agent['role']}.

PERSONNALITÉ: {agent['personality']}

EXPERTISE:
{chr(10).join(f'• {expertise}' for expertise in agent['expertise'])}

TON: {agent['tone']}

RÈGLES DE RÉPONSE:
1. Reste TOUJOURS dans ton rôle d'expert {agent['role']}
2. Utilise un ton {agent['tone']}
3. Propose des conseils CONCRETS et ACTIONNABLES
4. Utilise des émojis appropriés à ta personnalité
5. Structure tes réponses avec des listes ou étapes quand pertinent
6. Référence tes domaines d'expertise spécifiques
7. Limite-toi à 200-300 mots maximum
8. Termine par une question engageante ou une suggestion d'action

CONTEXTE:
- L'utilisateur s'appelle {user_name or 'utilisateur'}
- Tu fais partie de la plateforme WaveAI avec 3 autres agents experts
- Date actuelle: {datetime.now().strftime('%d/%m/%Y')}
"""

        # Ajouter l'historique si disponible
        if conversation_history:
            system_prompt += f"\n\nHISTORIQUE RÉCENT:\n{conversation_history}"
        
        # Tentative avec OpenAI GPT d'abord
        if self.openai_api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=400,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Erreur OpenAI: {e}")
        
        # Tentative avec Anthropic Claude en fallback
        if self.anthropic_api_key:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.content[0].text.strip()
            except Exception as e:
                print(f"Erreur Anthropic: {e}")
        
        # Fallback intelligent si aucune API n'est disponible
        return self.get_intelligent_fallback(agent_name, user_message)
    
    def get_intelligent_fallback(self, agent_name, user_message):
        """Fallback intelligent basé sur des mots-clés et templates"""
        
        agent = self.agents_profiles[agent_name]
        message_lower = user_message.lower()
        
        # Réponses contextuelles basées sur les mots-clés
        keyword_responses = {
            'alex': {
                'email': "📧 Pour optimiser votre gestion d'emails, je recommande la règle des 2 minutes : si ça prend moins de 2min, faites-le immédiatement. Sinon, planifiez un créneau dédié. Utilisez des filtres automatiques et la technique Inbox Zero. Voulez-vous que je vous aide à configurer un système spécifique ?",
                'productivité': "⚡ Voici ma méthode de productivité en 3 étapes : 1) Planification matinale (15min), 2) Blocs de temps focalisés (90min max), 3) Révision vespérale (10min). Commencez par identifier vos 3 priorités du jour. Quelle est votre plus grande difficulté actuelle ?",
                'organisation': "🎯 L'organisation efficace repose sur 4 piliers : Capture (tout noter), Clarification (que faire ?), Organisation (où le mettre ?), Révision (mise à jour régulière). Quel aspect vous pose le plus de difficultés ?",
                'default': f"👋 Salut ! Je suis {agent['name']}, votre expert en productivité. Je peux vous aider avec la gestion d'emails, l'organisation, et l'optimisation de votre workflow. Quelle est votre préoccupation principale aujourd'hui ?"
            },
            'lina': {
                'linkedin': "🔗 Pour booster votre LinkedIn : 1) Optimisez votre profil (photo pro + titre accrocheur), 2) Publiez du contenu de valeur 3x/semaine, 3) Commentez intelligemment sur les posts de votre secteur. Le secret ? L'authenticité et la régularité. Sur quoi voulez-vous vous concentrer en premier ?",
                'networking': "🌟 Le networking efficace commence par donner avant de recevoir. Identifiez 5 personnes de votre secteur, partagez leur contenu, ajoutez de la valeur par vos commentaires. Puis envoyez un message personnalisé. Avez-vous déjà une liste de contacts cibles ?",
                'professionnel': "💼 Votre marque professionnelle se construit sur 3 éléments : expertise (ce que vous savez), réputation (ce qu'on dit de vous), et réseau (qui vous connaît). Concentrons-nous sur l'un de ces axes. Lequel vous semble prioritaire ?",
                'default': f"💫 Bonjour ! Je suis {agent['name']}, spécialisée dans le développement professionnel et LinkedIn. Je peux vous aider à développer votre réseau, optimiser votre présence en ligne, et créer des opportunités. Par où souhaitez-vous commencer ?"
            },
            'marco': {
                'social': "📱 Stratégie réseaux sociaux gagnante : 1) Une plateforme principale (expertise), 2) Contenu pilier + variation, 3) Engagement authentique, 4) Analyse régulière. Quelle plateforme voulez-vous développer en priorité ?",
                'contenu': "🎨 Pour créer du contenu engageant : storytelling + valeur ajoutée + call-to-action clair. La règle 80/20 : 80% de valeur, 20% de promotion. Quel type de contenu résonne le mieux avec votre audience ?",
                'viral': "🚀 Les contenus viraux combinent : timing parfait, émotion forte, facilité de partage, et pertinence. Mais viser l'engagement authentique est plus profitable long-terme que la viralité. Quel message voulez-vous porter ?",
                'default': f"🎬 Hey ! Je suis {agent['name']}, expert en réseaux sociaux et création de contenu. Je transforme vos idées en contenus qui engagent et convertissent. Quel défi digital puis-je vous aider à relever ?"
            },
            'sofia': {
                'planning': "📅 La planification parfaite en 4 étapes : 1) Vision mensuelle, 2) Objectifs hebdomadaires, 3) Tâches quotidiennes, 4) Révision continue. Commençons par définir vos 3 priorités du mois. Quelles sont-elles ?",
                'calendrier': "⏰ Pour un calendrier optimisé : bloquez du temps pour les priorités AVANT les réunions, gardez 25% de buffer pour l'imprévu, groupez les tâches similaires. Quel est votre plus gros défi temporel actuellement ?",
                'organisation': "📋 Mon système d'organisation : Capture → Clarification → Catégorisation → Action → Révision. Tout commence par un outil de capture fiable. Utilisez-vous déjà un système ou partez-vous de zéro ?",
                'default': f"🗓️ Salut ! Je suis {agent['name']}, votre experte en organisation et gestion du temps. Je crée des systèmes qui transforment le chaos en efficacité sereine. Quelle zone de votre vie voulez-vous organiser ?"
            }
        }
        
        # Chercher des mots-clés pertinents
        if agent_name in keyword_responses:
            for keyword, response in keyword_responses[agent_name].items():
                if keyword != 'default' and keyword in message_lower:
                    return response
            
            # Réponse par défaut si aucun mot-clé trouvé
            return keyword_responses[agent_name]['default']
        
        return "Je suis là pour vous aider ! Pouvez-vous me dire plus précisément ce que vous recherchez ?"
    
    def format_conversation_history(self, chat_history, limit=3):
        """Formate l'historique de conversation pour le contexte IA"""
        if not chat_history:
            return ""
        
        history_text = ""
        for chat in list(chat_history)[-limit:]:  # Derniers messages
            history_text += f"Utilisateur: {chat.message}\nAgent: {chat.response}\n\n"
        
        return history_text.strip()

# Instance globale
wave_ai = WaveAIAgents()
