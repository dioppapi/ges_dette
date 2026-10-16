// ============================================
// TOAST.JS - Notifications
// ============================================

let toastTimeout = null;

function initToast() {
    // Créer le toast s'il n'existe pas
    if (!document.getElementById('toast')) {
        const toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        toast.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span id="toastMessage">Message</span>
        `;
        document.body.appendChild(toast);
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toastMessage');
    const icon = toast ? toast.querySelector('i') : null;
    
    if (!toast || !msg) return;
    
    // Clear previous timeout
    if (toastTimeout) {
        clearTimeout(toastTimeout);
        toastTimeout = null;
    }
    
    // Reset classes
    toast.className = 'toast';
    if (type === 'success') toast.classList.add('success');
    if (type === 'error') toast.classList.add('error');
    if (type === 'warning') toast.classList.add('warning');
    
    msg.textContent = message;
    
    if (icon) {
        if (type === 'success') icon.className = 'fas fa-check-circle';
        else if (type === 'error') icon.className = 'fas fa-exclamation-circle';
        else if (type === 'warning') icon.className = 'fas fa-exclamation-triangle';
        else icon.className = 'fas fa-info-circle';
    }
    
    toast.classList.add('show');
    
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
        toastTimeout = null;
    }, 3000);
}

// Toast avec timeout personnalisé
function showToastWithDuration(message, type = 'success', duration = 3000) {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toastMessage');
    const icon = toast ? toast.querySelector('i') : null;
    
    if (!toast || !msg) return;
    
    if (toastTimeout) {
        clearTimeout(toastTimeout);
        toastTimeout = null;
    }
    
    toast.className = 'toast';
    if (type === 'success') toast.classList.add('success');
    if (type === 'error') toast.classList.add('error');
    
    msg.textContent = message;
    
    if (icon) {
        if (type === 'success') icon.className = 'fas fa-check-circle';
        else if (type === 'error') icon.className = 'fas fa-exclamation-circle';
        else icon.className = 'fas fa-info-circle';
    }
    
    toast.classList.add('show');
    
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
        toastTimeout = null;
    }, duration);
}