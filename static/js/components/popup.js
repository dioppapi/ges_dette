// ============================================
// POPUP.JS - Gestion des popups
// ============================================

// Variable globale pour stocker le callback
let popupCallback = null;

function initPopups() {
    // Fermer en cliquant sur l'overlay
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('popup-overlay')) {
            closePopup();
        }
    });

    // Fermer avec ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopup();
            closePopupCopy();
        }
    });
}

function openPopup(title, body, actionText, callback) {
    const overlay = document.getElementById('popupOverlay');
    const titleEl = document.getElementById('popupTitle');
    const bodyEl = document.getElementById('popupBody');
    const actionBtn = document.getElementById('popupAction');
    
    if (!overlay || !titleEl || !bodyEl || !actionBtn) return;
    
    titleEl.textContent = title;
    bodyEl.innerHTML = body;
    actionBtn.textContent = actionText || 'Confirmer';
    
    // Sauvegarder le callback
    popupCallback = callback || null;
    
    // Supprimer les anciens écouteurs
    const newBtn = actionBtn.cloneNode(true);
    actionBtn.parentNode.replaceChild(newBtn, actionBtn);
    
    newBtn.addEventListener('click', function() {
        if (typeof popupCallback === 'function') {
            popupCallback();
        }
        closePopup();
    });
    
    overlay.classList.add('active');
}

function closePopup() {
    const overlay = document.getElementById('popupOverlay');
    if (overlay) overlay.classList.remove('active');
    popupCallback = null;
}

// ============================================
// FONCTIONS RAPIDES
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