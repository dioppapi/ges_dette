// ============================================
// APP.JS - FICHIER PRINCIPAL
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation
    initPopups();
    initToast();
});

// ============================================
// POPUPS
// ============================================

function initPopups() {
    const overlay = document.getElementById('popupOverlay');
    const copyOverlay = document.getElementById('popupCopy');
    
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) closePopup();
        });
    }
    
    if (copyOverlay) {
        copyOverlay.addEventListener('click', function(e) {
            if (e.target === this) closePopupCopy();
        });
    }
}

function openPopup(title, body, actionText, actionCallback) {
    const overlay = document.getElementById('popupOverlay');
    const titleEl = document.getElementById('popupTitle');
    const bodyEl = document.getElementById('popupBody');
    const actionBtn = document.getElementById('popupAction');
    
    if (!overlay || !titleEl || !bodyEl || !actionBtn) return;
    
    titleEl.textContent = title;
    bodyEl.innerHTML = body;
    actionBtn.textContent = actionText || 'Confirmer';
    
    // Remove old listeners
    const newBtn = actionBtn.cloneNode(true);
    actionBtn.parentNode.replaceChild(newBtn, actionBtn);
    
    newBtn.addEventListener('click', function() {
        if (actionCallback) actionCallback();
        closePopup();
    });
    
    overlay.classList.add('active');
}

function closePopup() {
    const overlay = document.getElementById('popupOverlay');
    if (overlay) overlay.classList.remove('active');
}

// ============================================
// POPUP COPIER
// ============================================

let currentCopyText = '';

function openPopupCopy(nom, description, montant, reste, status, date) {
    const text = `🧾 DETTE\n━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 Client : ${nom}\n📝 Description : ${description}\n💰 Montant : ${montant} UM\n💵 Reste : ${reste} UM\n📌 Statut : ${status}\n📅 Date : ${date}\n━━━━━━━━━━━━━━━━━━━━━━━━━`;
    
    currentCopyText = text;
    
    const copyContent = document.getElementById('copyContent');
    const overlay = document.getElementById('popupCopy');
    
    if (!copyContent || !overlay) return;
    
    copyContent.innerHTML = `
        <pre>${text}</pre>
    `;
    
    overlay.classList.add('active');
}

function closePopupCopy() {
    const overlay = document.getElementById('popupCopy');
    if (overlay) overlay.classList.remove('active');
}

function copyToClipboard() {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(currentCopyText).then(() => {
            showToast('✅ Texte copié !');
            closePopupCopy();
        }).catch(() => {
            fallbackCopy(currentCopyText);
        });
    } else {
        fallbackCopy(currentCopyText);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showToast('✅ Texte copié !');
        closePopupCopy();
    } catch (err) {
        showToast('❌ Erreur lors de la copie');
    }
    document.body.removeChild(textarea);
}

// ============================================
// TOAST
// ============================================

let toastTimeout = null;

function initToast() {
    // Pas besoin d'initialisation spéciale
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
    }, 3000);
}

// ============================================
// FONCTIONS RAPIDES POUR LES ACTIONS
// ============================================

function showConfirmDelete(clientName, deleteUrl) {
    openPopup(
        '⚠️ Confirmer la suppression',
        `<p>Voulez-vous vraiment supprimer <strong>${clientName}</strong> ?</p>
         <p style="color:#f87171;font-size:13px;margin-top:8px;">
             <i class="fas fa-exclamation-triangle"></i> Cette action est irréversible.
         </p>`,
        'Supprimer',
        function() {
            window.location.href = deleteUrl;
        }
    );
}

function showConfirmPayment(clientName, amount, paymentUrl) {
    openPopup(
        '💸 Confirmer le paiement',
        `<p>Voulez-vous confirmer le paiement de <strong>${amount} UM</strong> pour <strong>${clientName}</strong> ?</p>
         <p style="color:#22c55e;font-size:13px;margin-top:8px;">
             <i class="fas fa-check-circle"></i> Le solde sera mis à jour automatiquement.
         </p>`,
        'Confirmer',
        function() {
            window.location.href = paymentUrl;
        }
    );
}

function showUseAvoir(clientName, amount, useUrl) {
    openPopup(
        '🔄 Utiliser un reste',
        `<p>Voulez-vous utiliser <strong>${amount} UM</strong> du reste de <strong>${clientName}</strong> ?</p>
         <p style="color:var(--cyan);font-size:13px;margin-top:8px;">
             <i class="fas fa-info-circle"></i> Ce montant sera déduit de sa dette.
         </p>`,
        'Utiliser',
        function() {
            window.location.href = useUrl;
        }
    );
}

function showConfirmArchive(clientName, amount, archiveUrl) {
    openPopup(
        '📦 Archiver la dette',
        `<p>Voulez-vous archiver la dette de <strong>${clientName}</strong> (${amount} UM) ?</p>
         <p style="color:var(--text-secondary);font-size:13px;margin-top:8px;">
             <i class="fas fa-info-circle"></i> La dette sera déplacée dans les archives.
         </p>`,
        'Archiver',
        function() {
            window.location.href = archiveUrl;
        }
    );
}