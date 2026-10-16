// ============================================
// LISTES.JS - Pages de listes
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Animation des items
    const items = document.querySelectorAll('.item-card');
    items.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(10px)';
        item.style.transition = `all 0.25s ease ${index * 0.06}s`;
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 150);
    });
    
    // Filtrer les items (si barre de recherche)
    const searchInput = document.getElementById('searchList');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            const items = document.querySelectorAll('.item-card');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (query === '' || text.includes(query)) {
                    item.style.display = 'block';
                    item.style.opacity = '1';
                } else {
                    item.style.display = 'none';
                    item.style.opacity = '0';
                }
            });
        });
    }
});

// Fonction pour trier les listes
function sortList(sortBy) {
    const container = document.querySelector('.list-items');
    if (!container) return;
    
    const items = Array.from(container.querySelectorAll('.item-card'));
    
    items.sort((a, b) => {
        // Logique de tri selon sortBy
        if (sortBy === 'nom') {
            const nameA = a.querySelector('.name')?.textContent || '';
            const nameB = b.querySelector('.name')?.textContent || '';
            return nameA.localeCompare(nameB);
        } else if (sortBy === 'montant') {
            const amountA = parseFloat(a.querySelector('.amount')?.textContent || '0');
            const amountB = parseFloat(b.querySelector('.amount')?.textContent || '0');
            return amountB - amountA;
        } else if (sortBy === 'date') {
            const dateA = a.querySelector('.date')?.textContent || '';
            const dateB = b.querySelector('.date')?.textContent || '';
            return dateA.localeCompare(dateB);
        }
        return 0;
    });
    
    // Réorganiser
    items.forEach(item => container.appendChild(item));
    showToast('📊 Liste triée', 'success');
}