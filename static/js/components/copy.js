// ============================================
// COPY.JS - Gestion du copier/coller
// ============================================

let currentCopyText = '';

function initCopy() {
    // Fermer le popup copy avec ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopupCopy();
        }
    });
}

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
    textarea.style.pointerEvents = 'none';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showToast('✅ Texte copié !');
        closePopupCopy();
    } catch (err) {
        showToast('❌ Erreur lors de la copie', 'error');
    }
    document.body.removeChild(textarea);
}

function copySimpleText(text, message = '✅ Copié !') {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast(message);
        }).catch(() => {
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}