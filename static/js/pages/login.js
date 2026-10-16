// ============================================
// LOGIN.JS - Page de connexion
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.login-form');
    const username = document.querySelector('input[name="nom"]');
    const password = document.querySelector('input[name="mdp"]');
    const submitBtn = form ? form.querySelector('.btn-primary') : null;
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validation côté client
            let hasError = false;
            
            if (username && !username.value.trim()) {
                username.classList.add('error');
                hasError = true;
            } else if (username) {
                username.classList.remove('error');
            }
            
            if (password && !password.value.trim()) {
                password.classList.add('error');
                hasError = true;
            } else if (password) {
                password.classList.remove('error');
            }
            
            if (hasError) {
                e.preventDefault();
                showToast('Veuillez remplir tous les champs', 'error');
            }
        });
        
        // Supprimer l'erreur sur focus
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.classList.remove('error');
            });
        });
    }
});

// Mot de passe visible (optionnel)
function togglePasswordVisibility() {
    const passwordInput = document.querySelector('input[name="mdp"]');
    if (passwordInput) {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    }
}