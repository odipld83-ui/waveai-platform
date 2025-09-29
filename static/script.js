/* ==============================================
   🌊 WaveAI - JavaScript Global
   Fonctionnalités interactives et animations
   ============================================== */

// Configuration globale
const WaveAI = {
    version: '1.0.0',
    apiBase: '/api',
    socketConnected: false,
    currentUser: null,

    // Initialisation globale
    init() {
        this.setupGlobalEvents();
        this.initAnimations();
        this.setupNotifications();
        console.log('🌊 WaveAI JavaScript initialized v' + this.version);
    },

    // Configuration des événements globaux
    setupGlobalEvents() {
        // Gestion des formulaires
        document.addEventListener('submit', this.handleFormSubmit.bind(this));

        // Gestion responsive
        window.addEventListener('resize', this.handleResize.bind(this));

        // Gestion du scroll
        window.addEventListener('scroll', this.handleScroll.bind(this));

        // Prévention double-click sur boutons
        document.addEventListener('click', this.preventDoubleClick.bind(this));
    },

    // Animations d'entrée
    initAnimations() {
        // Observer pour animations au scroll
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            // Éléments à animer
            document.querySelectorAll('.agent-showcase, .stat-card, .quick-action-card').forEach(el => {
                observer.observe(el);
            });
        }

        // Animation des compteurs
        this.animateCounters();
    },

    // Animation des compteurs de statistiques
    animateCounters() {
        const counters = document.querySelectorAll('.stat-value');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            if (isNaN(target)) return;

            const increment = target / 50;
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 20);
        });
    },

    // Gestion des soumissions de formulaires
    handleFormSubmit(e) {
        const form = e.target;
        if (!form.matches('form')) return;

        // Ajouter un loader au bouton de soumission
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            this.addButtonLoader(submitBtn);
        }
    },

    // Ajouter un loader à un bouton
    addButtonLoader(button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Chargement...';

        // Restaurer après 3 secondes maximum
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        }, 3000);
    },

    // Prévenir les double-clics
    preventDoubleClick(e) {
        const button = e.target.closest('button, .btn');
        if (!button) return;

        if (button.classList.contains('clicking')) {
            e.preventDefault();
            return false;
        }

        button.classList.add('clicking');
        setTimeout(() => {
            button.classList.remove('clicking');
        }, 1000);
    },

    // Gestion responsive
    handleResize() {
        // Ajuster la hauteur des éléments chat sur mobile
        if (window.innerWidth <= 768) {
            const chatArea = document.querySelector('.chat-main-area');
            if (chatArea) {
                chatArea.style.height = `${window.innerHeight - 120}px`;
            }
        }
    },

    // Gestion du scroll
    handleScroll() {
        const navbar = document.querySelector('.wave-navbar');
        if (!navbar) return;

        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    },

    // Système de notifications
    setupNotifications() {
        // Créer le container de notifications s'il n'existe pas
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
    },

    // Afficher une notification
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.role = 'alert';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(notification);

        // Auto-suppression
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        }
    },

    // Appel API avec gestion d'erreurs
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(this.apiBase + endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return { success: true, data };

        } catch (error) {
            console.error('API Error:', error);
            this.showNotification(`Erreur: ${error.message}`, 'danger');
            return { success: false, error: error.message };
        }
    },

    // Utilitaires diverses
    utils: {
        // Formater une date
        formatDate(date) {
            return new Intl.DateTimeFormat('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }).format(new Date(date));
        },

        // Débounce pour les événements répétitifs
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Copier du texte dans le presse-papiers
        async copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                WaveAI.showNotification('Copié dans le presse-papiers !', 'success', 2000);
                return true;
            } catch (error) {
                console.error('Erreur copie:', error);
                return false;
            }
        },

        // Valider un email
        validateEmail(email) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(email);
        },

        // Échapper HTML
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        // Générer un ID unique
        generateId() {
            return Math.random().toString(36).substring(2) + Date.now().toString(36);
        }
    }
};

// Fonctions globales spécialisées

// Animation de la vague sur la page d'accueil
function initWaveAnimation() {
    const hero = document.querySelector('.hero-section');
    if (!hero) return;

    // Créer des particules flottantes
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'wave-particles';
    particlesContainer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
    `;

    // Ajouter des particules
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: float ${3 + Math.random() * 4}s ease-in-out infinite;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation-delay: ${Math.random() * 2}s;
        `;
        particlesContainer.appendChild(particle);
    }

    hero.appendChild(particlesContainer);
}

// Effet de frappe pour les textes
function typewriterEffect(element, text, speed = 50) {
    if (!element) return;

    element.textContent = '';
    let i = 0;

    const timer = setInterval(() => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
        } else {
            clearInterval(timer);
        }
    }, speed);
}

// Animation des cartes au survol
function initCardHoverEffects() {
    document.querySelectorAll('.agent-dashboard-card, .quick-action-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Gestion du mode sombre (pour futures versions)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser WaveAI
    WaveAI.init();

    // Animations spécifiques selon la page
    if (document.body.classList.contains('landing-page')) {
        initWaveAnimation();

        // Animation du titre principal
        const heroTitle = document.querySelector('.hero-section h1');
        if (heroTitle) {
            heroTitle.style.opacity = '0';
            heroTitle.style.transform = 'translateY(30px)';

            setTimeout(() => {
                heroTitle.style.transition = 'all 0.8s ease-out';
                heroTitle.style.opacity = '1';
                heroTitle.style.transform = 'translateY(0)';
            }, 300);
        }
    }

    if (document.body.classList.contains('dashboard-page')) {
        initCardHoverEffects();
    }

    // Effet de focus amélioré pour les inputs
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    // Smooth scroll pour les liens internes
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.timing;
            const loadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`🌊 WaveAI loaded in ${loadTime}ms`);

            if (loadTime > 3000) {
                console.warn('⚠️ Page load time is slow');
            }
        }, 100);
    });
}

// Gestion des erreurs JavaScript globales
window.addEventListener('error', function(e) {
    console.error('🚨 JavaScript Error:', e.error);

    // Éviter d'afficher trop de notifications d'erreur
    if (!window.errorNotificationShown) {
        WaveAI.showNotification(
            'Une erreur technique s'est produite. L'équipe a été notifiée.',
            'warning',
            5000
        );
        window.errorNotificationShown = true;

        // Réinitialiser après 10 secondes
        setTimeout(() => {
            window.errorNotificationShown = false;
        }, 10000);
    }
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveAI;
} else {
    window.WaveAI = WaveAI;
}