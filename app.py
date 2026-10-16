from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)
app.secret_key = 'jgnjtgklgkeir45u-0212544IF5'


def connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='btq'
    )


# ============================================
# ACCUEIL
# ============================================
@app.route("/")
def index():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    # Dettes en attente (actives)
    curs.execute("""
        SELECT COUNT(*) AS total FROM dette 
        WHERE status = 'Ouvert' AND montant_rest > 0
    """)
    row = curs.fetchone()
    dettes_attente = row['total'] if row else 0
    
    # Dettes soldées
    curs.execute("""
        SELECT COUNT(*) AS total FROM dette 
        WHERE status = 'Soldée'
    """)
    row = curs.fetchone()
    dettes_soldees = row['total'] if row else 0
    
    # Nombre de clients
    curs.execute("SELECT COUNT(*) AS total FROM client")
    row = curs.fetchone()
    clients = row['total'] if row else 0
    
    conn.close()
    
    return render_template('index.html',
        dettes_attente=dettes_attente,
        dettes_soldees=dettes_soldees, 
        clients=clients
    )


# ============================================
# AJOUTER CLIENT
# ============================================
@app.route('/ajouter_client', methods=['GET', 'POST'])
def ajouter():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        nom = request.form.get('nom')
        tel = request.form.get('tel')
        
        if not nom:
            return render_template("ajouter.html", 
                erreur="Le nom est obligatoire.")
        
        conn = connection()
        with conn.cursor() as curs:
            curs.execute("INSERT INTO client (nom, tel) VALUES (%s, %s)", (nom, tel))
            conn.commit()
        conn.close()
        return redirect(url_for('liste'))
    
    return render_template("ajouter.html")


# ============================================
# LISTE DES CLIENTS
# ============================================
@app.route("/liste")
def liste():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("""
            SELECT 
                c.id_client,
                c.nom,
                c.tel,
                COALESCE(
                    (SELECT SUM(d.montant_rest)
                     FROM dette d
                     WHERE d.id_client = c.id_client
                     AND d.status = 'Ouvert'
                     AND d.montant_rest > 0),
                    0
                ) AS total_dettes,
                COALESCE(
                    (SELECT SUM(a.montant)
                     FROM avoir_client a
                     WHERE a.id_client = c.id_client),
                    0
                ) AS total_avoir
            FROM client c
            ORDER BY c.nom
        """)
        clients = curs.fetchall()
    conn.close()
    
    return render_template("liste.html", clients=clients)


# ============================================
# MODIFIER CLIENT
# ============================================
@app.route('/modifier_client/<int:id_client>', methods=['GET', 'POST'])
def modifier_client(id_client):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("SELECT * FROM client WHERE id_client = %s", (id_client,))
    client = curs.fetchone()
    
    if not client:
        conn.close()
        return redirect(url_for('liste'))
    
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        tel = request.form.get('tel', '').strip()
        
        if not nom:
            conn.close()
            return render_template('modifier_client.html',
                client=client,
                erreur="Le nom est obligatoire.")
        
        try:
            curs.execute("""
                UPDATE client SET nom = %s, tel = %s 
                WHERE id_client = %s
            """, (nom, tel, id_client))
            conn.commit()
            conn.close()
            return redirect(url_for('liste'))
        except Exception as e:
            conn.rollback()
            conn.close()
            return render_template('modifier_client.html',
                client=client,
                erreur=f"Erreur : {str(e)}")
    
    conn.close()
    return render_template('modifier_client.html', client=client)


# ============================================
# SUPPRIMER CLIENT
# ============================================
@app.route('/supprimer_client/<int:id_client>')
def supprimer_client(id_client):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    with conn.cursor() as curs:
        curs.execute("DELETE FROM client WHERE id_client = %s", (id_client,))
        conn.commit()
    conn.close()
    return redirect(url_for('liste'))


# ============================================
# AJOUTER DETTE
# ============================================
@app.route('/ajouter_dettes', methods=['GET', 'POST'])
def ajouter_dette():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("SELECT * FROM client ORDER BY nom")
        clients = curs.fetchall()
        
        if request.method == 'POST':
            id_client = request.form.get('id_client')
            description = request.form.get('description')
            montant_str = request.form.get('montant')
            
            if not id_client:
                conn.close()
                return render_template("dette.html", clients=clients,
                    erreur="Veuillez sélectionner un client.")
            
            try:
                montant = int(montant_str)
                if montant <= 0:
                    raise ValueError
            except:
                conn.close()
                return render_template("dette.html", clients=clients,
                    erreur="Montant invalide.")
            
            curs.execute("""
                INSERT INTO dette 
                (id_client, description, montant_tot, montant_paye, montant_rest, date_dette, status)
                VALUES (%s, %s, %s, 0, %s, NOW(), 'Ouvert')
            """, (id_client, description, montant, montant))
            
            conn.commit()
            conn.close()
            return redirect(url_for('liste_dette'))
    
    conn.close()
    return render_template("dette.html", clients=clients)


# ============================================
# LISTE DES DETTES
# ============================================
@app.route('/liste_des_dettes')
def liste_dette():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("""
            SELECT 
                dette.id_dette,
                client.nom,
                dette.description,
                dette.montant_tot,
                dette.montant_paye,
                dette.montant_rest,
                dette.date_dette,
                dette.status
            FROM dette 
            JOIN client ON dette.id_client = client.id_client 
            WHERE dette.status = 'Ouvert'
            ORDER BY dette.date_dette DESC
        """)
        dettes = curs.fetchall()
    conn.close()
    
    return render_template("liste_dette.html", dettes=dettes)


# ============================================
# PAYER (espèces)
# ============================================
@app.route('/payer/<int:id_dette>', methods=['GET', 'POST'])
def payer(id_dette):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("SELECT * FROM dette WHERE id_dette = %s", (id_dette,))
    dette = curs.fetchone()
    
    if not dette:
        conn.close()
        return redirect(url_for('liste_dette'))
    
    if request.method == 'POST':
        try:
            paiement = int(request.form.get('paiement'))
            if paiement <= 0:
                raise ValueError
        except:
            conn.close()
            return render_template("payer.html", dette=dette,
                erreur="Montant invalide.")
        
        montant_tot = int(dette['montant_tot'])
        montant_paye_actuel = int(dette['montant_paye'] or 0)
        
        nouveau_paye = montant_paye_actuel + paiement
        nouveau_rest = montant_tot - nouveau_paye
        
        # Surplus
        if nouveau_rest < 0:
            surplus = nouveau_paye - montant_tot
            nouveau_paye = montant_tot
            nouveau_rest = 0
            
            curs.execute("""
                INSERT INTO avoir_client (id_client, montant, description, date_avoir)
                VALUES (%s, %s, %s, NOW())
            """, (dette['id_client'], surplus, "Surplus après paiement"))
        
        if nouveau_rest == 0:
            curs.execute("""
                UPDATE dette 
                SET montant_paye = %s, montant_rest = 0,
                    status = 'Soldée', date_reg = NOW()
                WHERE id_dette = %s
            """, (nouveau_paye, id_dette))
        else:
            curs.execute("""
                UPDATE dette 
                SET montant_paye = %s, montant_rest = %s
                WHERE id_dette = %s
            """, (nouveau_paye, nouveau_rest, id_dette))
        
        conn.commit()
        conn.close()
        return redirect(url_for('liste_dette'))
    
    conn.close()
    return render_template("payer.html", dette=dette)


# ============================================
# MODIFIER DETTE
# ============================================
@app.route('/modifier_dette/<int:id_dette>', methods=['GET', 'POST'])
def modifier_dette(id_dette):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("SELECT * FROM dette WHERE id_dette = %s", (id_dette,))
    dette = curs.fetchone()
    
    if not dette:
        conn.close()
        return redirect(url_for('liste_dette'))
    
    curs.execute("SELECT id_client, nom FROM client ORDER BY nom")
    clients = curs.fetchall()
    
    if request.method == 'POST':
        id_client = request.form.get('id_client')
        description = request.form.get('description')
        
        if not id_client:
            conn.close()
            return render_template('modifier_dette.html',
                dette=dette, clients=clients,
                erreur="Veuillez sélectionner un client.")
        
        try:
            nouveau_total = int(request.form.get('montant_tot'))
            nouveau_paye = int(request.form.get('montant_paye') or 0)
            if nouveau_total <= 0 or nouveau_paye < 0:
                raise ValueError
        except:
            conn.close()
            return render_template('modifier_dette.html',
                dette=dette, clients=clients,
                erreur="Montants invalides.")
        
        surplus = 0
        if nouveau_paye > nouveau_total:
            surplus = nouveau_paye - nouveau_total
            nouveau_paye = nouveau_total
        
        nouveau_rest = nouveau_total - nouveau_paye
        
        try:
            if nouveau_rest == 0:
                curs.execute("""
                    UPDATE dette 
                    SET id_client=%s, description=%s,
                        montant_tot=%s, montant_paye=%s, montant_rest=0,
                        status='Soldée', date_reg=NOW()
                    WHERE id_dette=%s
                """, (id_client, description, nouveau_total, nouveau_paye, id_dette))
            else:
                curs.execute("""
                    UPDATE dette 
                    SET id_client=%s, description=%s,
                        montant_tot=%s, montant_paye=%s, montant_rest=%s,
                        status='Ouvert'
                    WHERE id_dette=%s
                """, (id_client, description, nouveau_total,
                      nouveau_paye, nouveau_rest, id_dette))
            
            if surplus > 0:
                curs.execute("""
                    INSERT INTO avoir_client (id_client, montant, description, date_avoir)
                    VALUES (%s, %s, %s, NOW())
                """, (id_client, surplus, "Surplus après modification de la dette"))
            
            conn.commit()
            conn.close()
            return redirect(url_for('liste_dette'))
        except Exception as e:
            conn.rollback()
            conn.close()
            return render_template('modifier_dette.html',
                dette=dette, clients=clients,
                erreur=f"Erreur : {str(e)}")
    
    conn.close()
    return render_template('modifier_dette.html', dette=dette, clients=clients)


# ============================================
# DEMANDE DE PAIEMENT MOBILE
# ============================================
@app.route("/demande_payement/<int:id_dette>", methods=['GET', 'POST'])
def demande_payement(id_dette):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("SELECT * FROM dette WHERE id_dette=%s", (id_dette,))
        dette = curs.fetchone()
        
        if not dette:
            conn.close()
            return redirect(url_for('liste_dette'))
        
        if request.method == 'POST':
            try:
                montant = int(request.form.get('montant'))
                if montant <= 0:
                    raise ValueError
            except:
                conn.close()
                return render_template("demande.html", dette=dette,
                    erreur="Montant invalide.")
            
            if montant > int(dette['montant_rest']):
                conn.close()
                return render_template("demande.html", dette=dette,
                    erreur="Le montant dépasse le reste à payer.")
            
            description = request.form.get('description')
            
            curs.execute("""
                INSERT INTO demande_paiement (id_dette, montant, description)
                VALUES (%s, %s, %s)
            """, (id_dette, montant, description))
            
            conn.commit()
            conn.close()
            return redirect(url_for('paiement_en_attente'))
    
    conn.close()
    return render_template("demande.html", dette=dette)


# ============================================
# PAIEMENT EN ATTENTE
# ============================================
@app.route('/paiement_en_attente')
def paiement_en_attente():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    curs.execute("""
        SELECT 
            demande_paiement.id_demande,
            client.nom,
            dette.description AS achat,
            demande_paiement.description AS method,
            demande_paiement.montant,
            demande_paiement.date_demande
        FROM demande_paiement 
        JOIN dette ON demande_paiement.id_dette = dette.id_dette 
        JOIN client ON dette.id_client = client.id_client 
        WHERE demande_paiement.status = 'en_attente'
        ORDER BY demande_paiement.date_demande DESC
    """)
    demandes = curs.fetchall()
    conn.close()
    
    return render_template("paiement_en_attente.html", demandes=demandes)


# ============================================
# CONFIRMER PAIEMENT MOBILE
# ============================================
@app.route("/confirmer/<int:id_demande>")
def confirmer(id_demande):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("SELECT * FROM demande_paiement WHERE id_demande = %s", (id_demande,))
    demande = curs.fetchone()
    
    if not demande:
        conn.close()
        return redirect(url_for('liste_dette'))
    
    curs.execute("SELECT * FROM dette WHERE id_dette = %s", (demande['id_dette'],))
    dette = curs.fetchone()
    
    if not dette:
        conn.close()
        return redirect(url_for('liste_dette'))
    
    montant_demande = int(demande['montant'])
    montant_tot = int(dette['montant_tot'])
    montant_paye_actuel = int(dette['montant_paye'] or 0)
    
    nouveau_paye = montant_paye_actuel + montant_demande
    nouveau_rest = montant_tot - nouveau_paye
    
    try:
        if nouveau_rest < 0:
            surplus = nouveau_paye - montant_tot
            nouveau_paye = montant_tot
            nouveau_rest = 0
            
            curs.execute("""
                INSERT INTO avoir_client (id_client, montant, description, date_avoir)
                VALUES (%s, %s, %s, NOW())
            """, (dette['id_client'], surplus, "Surplus après paiement mobile"))
        
        if nouveau_rest == 0:
            curs.execute("""
                UPDATE dette 
                SET montant_paye = %s, montant_rest = 0,
                    status = 'Soldée', date_reg = NOW()
                WHERE id_dette = %s
            """, (nouveau_paye, dette['id_dette']))
        else:
            curs.execute("""
                UPDATE dette 
                SET montant_paye = %s, montant_rest = %s
                WHERE id_dette = %s
            """, (nouveau_paye, nouveau_rest, dette['id_dette']))
        
        curs.execute("""
            UPDATE demande_paiement SET status = 'confirmé' 
            WHERE id_demande = %s
        """, (id_demande,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erreur confirmation : {e}")
    
    conn.close()
    return redirect(url_for('liste_dette'))


# ============================================
# REFUSER PAIEMENT MOBILE
# ============================================
@app.route("/refuse/<int:id_demande>")
def refuser(id_demande):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("""
            UPDATE demande_paiement SET status = 'refusé' 
            WHERE id_demande = %s
        """, (id_demande,))
        conn.commit()
    conn.close()
    return redirect(url_for('liste_dette'))


# ============================================
# DEMANDES REFUSÉES
# ============================================
@app.route("/demandes_refuse")
def demandes_refuses():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    curs.execute("""
        SELECT 
            client.nom,
            demande_paiement.montant,
            dette.description,
            demande_paiement.date_demande
        FROM demande_paiement 
        JOIN dette ON demande_paiement.id_dette = dette.id_dette 
        JOIN client ON dette.id_client = client.id_client 
        WHERE demande_paiement.status = 'refusé'
        ORDER BY demande_paiement.date_demande DESC
    """)
    demandes = curs.fetchall()
    conn.close()
    
    return render_template("demandes_refuses.html", demandes=demandes)


# ============================================
# ARCHIVE
# ============================================
@app.route("/archive")
def archive():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    curs.execute("""
        SELECT 
            client.nom,
            dette.montant_tot,
            dette.description,
            dette.date_dette,
            dette.date_reg
        FROM dette 
        JOIN client ON dette.id_client = client.id_client 
        WHERE dette.status = 'Soldée'
        ORDER BY dette.date_reg DESC
    """)
    archives = curs.fetchall()
    conn.close()
    
    return render_template("archive.html", archives=archives)


# ============================================
# RECHERCHE
# ============================================
@app.route("/recherche")
def recherche():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    mot = request.args.get('recherche', '').strip()
    client_trouve = False
    client_info = None
    dettes_en_cours = []
    archives = []
    
    if mot:
        conn = connection()
        curs = conn.cursor(dictionary=True)
        
        curs.execute("""
            SELECT id_client, nom, tel FROM client 
            WHERE nom LIKE %s LIMIT 1
        """, (f'%{mot}%',))
        client_info = curs.fetchone()
        
        if client_info:
            client_trouve = True
            client_id = client_info['id_client']
            
            curs.execute("""
                SELECT id_dette, description, montant_tot, 
                       montant_paye, montant_rest, date_dette, status
                FROM dette 
                WHERE id_client = %s AND status = 'Ouvert'
                ORDER BY date_dette DESC
            """, (client_id,))
            dettes_en_cours = curs.fetchall()
            
            curs.execute("""
                SELECT id_dette, description, montant_tot, 
                       montant_paye, montant_rest, date_dette, 
                       date_reg, status
                FROM dette 
                WHERE id_client = %s AND status = 'Soldée'
                ORDER BY date_reg DESC
            """, (client_id,))
            archives = curs.fetchall()
        
        conn.close()
    
    return render_template("resultat_recherche.html",
        client_trouve=client_trouve,
        client_info=client_info,
        dettes_en_cours=dettes_en_cours,
        archives=archives,
        mot_recherche=mot
    )


# ============================================
# AJOUTER MONNAIE À RENDRE
# ============================================
@app.route('/ajouter_avoir', methods=['GET', 'POST'])
def ajouter_avoir():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("SELECT id_client, nom FROM client ORDER BY nom")
    clients = curs.fetchall()
    
    if request.method == 'POST':
        id_client = request.form.get('id_client')
        montant_str = request.form.get('montant')
        description = request.form.get('description')
        
        if not id_client:
            conn.close()
            return render_template('ajouter_avoir.html',
                clients=clients,
                erreur="Veuillez sélectionner un client.")
        
        try:
            montant = int(montant_str)
            if montant <= 0:
                raise ValueError
        except:
            conn.close()
            return render_template('ajouter_avoir.html',
                clients=clients,
                erreur="Montant invalide.")
        
        curs.execute("""
            INSERT INTO avoir_client (id_client, montant, description, date_avoir)
            VALUES (%s, %s, %s, NOW())
        """, (id_client, montant, description))
        
        conn.commit()
        conn.close()
        return redirect(url_for('liste_avoirs'))
    
    conn.close()
    return render_template('ajouter_avoir.html', clients=clients)


# ============================================
# LISTE MONNAIE À RENDRE
# ============================================
@app.route('/liste_avoirs')
def liste_avoirs():
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("""
        SELECT 
            a.id_avoir,
            a.id_client,
            a.montant,
            a.description,
            a.date_avoir,
            c.nom,
            c.tel,
            EXISTS(
                SELECT 1 FROM dette d 
                WHERE d.id_client = a.id_client 
                AND d.status = 'Ouvert'
                AND d.montant_rest > 0
            ) AS has_active_debt,
            COALESCE(
                (SELECT SUM(d.montant_rest) 
                 FROM dette d 
                 WHERE d.id_client = a.id_client 
                 AND d.status = 'Ouvert'),
                0
            ) AS total_dette_restante
        FROM avoir_client a
        JOIN client c ON a.id_client = c.id_client
        WHERE a.montant > 0
        ORDER BY a.date_avoir DESC
    """)
    
    avoirs = curs.fetchall()
    conn.close()
    
    return render_template('liste_avoirs.html', avoirs=avoirs)


# ============================================
# UTILISER AVOIR (Déduire d'une dette)
# ============================================
@app.route('/utiliser_avoir/<int:id_avoir>', methods=['GET', 'POST'])
def utiliser_avoir(id_avoir):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("""
        SELECT a.*, c.nom
        FROM avoir_client a
        JOIN client c ON a.id_client = c.id_client
        WHERE a.id_avoir = %s
    """, (id_avoir,))
    avoir = curs.fetchone()
    
    if not avoir:
        conn.close()
        return redirect(url_for('liste_avoirs'))
    
    curs.execute("""
        SELECT id_dette, montant_rest, montant_paye, description
        FROM dette
        WHERE id_client = %s 
        AND status = 'Ouvert'
        AND montant_rest > 0
        ORDER BY date_dette DESC
        LIMIT 1
    """, (avoir['id_client'],))
    dette = curs.fetchone()
    
    if request.method == 'POST':
        if not dette:
            conn.close()
            return render_template('utiliser_avoir.html',
                avoir=avoir, dette=None,
                erreur="Aucune dette active.")
        
        try:
            montant = int(request.form.get('montant'))
            if montant <= 0:
                raise ValueError
        except:
            conn.close()
            return render_template('utiliser_avoir.html',
                avoir=avoir, dette=dette,
                erreur="Montant invalide.")
        
        avoir_montant = int(avoir['montant'])
        dette_rest = int(dette['montant_rest'])
        dette_paye = int(dette['montant_paye'] or 0)
        
        max_autorise = min(avoir_montant, dette_rest)
        
        if montant > max_autorise:
            conn.close()
            return render_template('utiliser_avoir.html',
                avoir=avoir, dette=dette,
                erreur=f"Maximum autorisé : {max_autorise} UM")
        
        try:
            nouveau_rest = dette_rest - montant
            nouveau_paye = dette_paye + montant
            
            if nouveau_rest <= 0:
                curs.execute("""
                    UPDATE dette 
                    SET montant_rest = 0, montant_paye = %s,
                        status = 'Soldée', date_reg = NOW()
                    WHERE id_dette = %s
                """, (nouveau_paye, dette['id_dette']))
            else:
                curs.execute("""
                    UPDATE dette 
                    SET montant_rest = %s, montant_paye = %s
                    WHERE id_dette = %s
                """, (nouveau_rest, nouveau_paye, dette['id_dette']))
            
            nouveau_avoir = avoir_montant - montant
            if nouveau_avoir <= 0:
                curs.execute("DELETE FROM avoir_client WHERE id_avoir = %s", (id_avoir,))
            else:
                curs.execute("""
                    UPDATE avoir_client SET montant = %s 
                    WHERE id_avoir = %s
                """, (nouveau_avoir, id_avoir))
            
            conn.commit()
            conn.close()
            return redirect(url_for('liste_avoirs'))
        except Exception as e:
            conn.rollback()
            conn.close()
            return render_template('utiliser_avoir.html',
                avoir=avoir, dette=dette,
                erreur=f"Erreur : {str(e)}")
    
    conn.close()
    return render_template('utiliser_avoir.html', avoir=avoir, dette=dette)


# ============================================
# RENDRE MONNAIE AU CLIENT
# ============================================
@app.route('/rendre_monnaie/<int:id_avoir>', methods=['GET', 'POST'])
def rendre_monnaie(id_avoir):
    if 'nom' not in session:
        return redirect(url_for('login'))
    
    conn = connection()
    curs = conn.cursor(dictionary=True)
    
    curs.execute("""
        SELECT a.*, c.nom
        FROM avoir_client a
        JOIN client c ON a.id_client = c.id_client
        WHERE a.id_avoir = %s
    """, (id_avoir,))
    avoir = curs.fetchone()
    
    if not avoir:
        conn.close()
        return redirect(url_for('liste_avoirs'))
    
    if request.method == 'POST':
        try:
            montant = int(request.form.get('montant'))
            if montant <= 0:
                raise ValueError
        except:
            conn.close()
            return render_template('rendre_monnaie.html',
                avoir=avoir, erreur="Montant invalide.")
        
        avoir_montant = int(avoir['montant'])
        
        if montant > avoir_montant:
            conn.close()
            return render_template('rendre_monnaie.html',
                avoir=avoir,
                erreur="Montant supérieur à la monnaie disponible.")
        
        nouveau = avoir_montant - montant
        
        try:
            if nouveau <= 0:
                curs.execute("DELETE FROM avoir_client WHERE id_avoir = %s", (id_avoir,))
            else:
                curs.execute("""
                    UPDATE avoir_client SET montant = %s 
                    WHERE id_avoir = %s
                """, (nouveau, id_avoir))
            
            conn.commit()
            conn.close()
            return redirect(url_for('liste_avoirs'))
        except Exception as e:
            conn.rollback()
            conn.close()
            return render_template('rendre_monnaie.html',
                avoir=avoir, erreur=f"Erreur : {str(e)}")
    
    conn.close()
    return render_template('rendre_monnaie.html', avoir=avoir)


# ============================================
# LOGIN / LOGOUT
# ============================================
@app.route("/login", methods=['GET', 'POST'])
def login():
    erreur = ""
    if request.method == 'POST':
        nom = request.form.get('nom')
        mdp = request.form.get('mdp')
        
        conn = connection()
        curs = conn.cursor(dictionary=True)
        curs.execute("SELECT * FROM user WHERE nom = %s", (nom,))
        user = curs.fetchone()
        conn.close()
        
        if user and check_password_hash(user['mdp'], mdp):
            session['nom'] = user['nom']
            return redirect(url_for('index'))
        else:
            erreur = "Nom ou Mot de Passe Incorrect"
    
    return render_template("login.html", erreur=erreur)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)