// ============================================
// HOME.JS - Page d'accueil
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Animation d'entrée des cartes
    const cards = document.querySelectorAll('.menu-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `all 0.3s ease ${index * 0.05}s`;
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });
});

// Statistiques rapides (si affichées)
function updateStats() {
    // Cette fonction peut être appelée pour mettre à jour des statistiques
    // Exemple : nombre de clients, dettes en cours, etc.
    console.log('Stats mises à jour');
}