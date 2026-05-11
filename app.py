from flask import Flask,request,render_template,redirect,url_for,session
import mysql.connector
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os
app=Flask(__name__)
app.secret_key=os.getenv("MYSQLPASSWORD")
def connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )
@app.route("/")
def index():
    if 'nom' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')
@app.route('/ajouter_client',methods=['GET','POST'])
def ajouter():
    if 'nom' not in session:
        return redirect(url_for('login'))
    if request.method=="POST":
        nom=request.form.get('nom')
        tel=request.form.get('tel')

        conn=connection()
        with conn.cursor() as curs:
            curs.execute("insert into client (nom,tel) values(%s,%s)",(nom,tel))
            conn.commit()
        conn.close()
        return redirect(url_for('liste'))
    return render_template("ajouter.html")
@app.route("/liste des client",methods=['GET','POST'])
def liste():
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("select * from client")
        liste=curs.fetchall()
    conn.close()
    return render_template("liste.html",liste=liste)
@app.route('/ajouter_dettes',methods=['GET','POST'])
def ajouter_dette():
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("select * from client")
        clients=curs.fetchall()
    
        if request.method=='POST':
            id_client=request.form.get('id_client')
            description=request.form.get('description')
            montant=request.form.get('montant')
            if float(montant)<0:
                return render_template("dette.html",erreur="Montant Invalide")
            curs.execute("insert into dette (id_client,description,montant_tot,montant_rest,date_dette,status) values(%s,%s,%s,%s,now(),%s)",(id_client,description,montant,montant,'Ouvert'))
            conn.commit()
            conn.close()
            return redirect(url_for('liste_dette'))
    conn.close()
    return render_template("dette.html",clients=clients) 
@app.route('/liste_des_dettes')
def liste_dette():
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("select dette.id_dette,client.nom,dette.description,dette.montant_tot,dette.montant_rest,dette.date_dette,dette.status from dette join client on dette.id_client=client.id_client where dette.status='Ouvert' ")
        dettes=curs.fetchall()
        conn.close()
    return render_template("liste_dette.html",dettes=dettes)
@app.route('/payer/<int:id_dette>',methods=['GET','POST'])
def payer(id_dette):
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("select * from dette where id_dette=%s",(id_dette,))
        dette=curs.fetchone()
        if request.method=='POST':
            paiement=int(request.form.get('paiement'))
            nouveau_rest= dette['montant_rest']-paiement
            if nouveau_rest<=0:
                nouveau_rest=0
                status='Soldée'
                curs.execute("update dette set montant_rest=%s,status=%s,date_reg=now() where id_dette=%s",(nouveau_rest,status,id_dette))
            else:
                status='Ouvert'
                curs.execute("update dette set montant_rest=%s,status=%s where id_dette=%s",(nouveau_rest,status,id_dette))
            conn.commit()
            conn.close()
            return redirect(url_for('liste_dette'))
        conn.close()
    return render_template("payer.html",dette=dette)
@app.route("/demande_payement/<int:id_dette>",methods=['GET','POST'])
def demande_payement(id_dette):
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("select * from dette where id_dette=%s",(id_dette,))
        dette=curs.fetchone()
        if request.method=='POST':
            montant=int(request.form.get('montant'))
            if montant > dette['montant_rest']:
                conn.close()
                return render_template("demande.html",dette=dette,erreur="Le montant dépasse la dette")
            description=request.form.get('description')
            if montant <=0:
                conn.close()
                return render_template("demande.html",dette=dette,erreur="Montant Invalide")
            curs.execute("insert into demande_paiement(id_dette,montant,description) values(%s,%s,%s)",(id_dette,montant,description))
            conn.commit()
            conn.close()
            return redirect(url_for('paiement_en_attente'))
        conn.close()
        return render_template("demande.html",dette=dette)
@app.route('/paiement_en_attente')
def paiement_en_attente():
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    curs=conn.cursor(dictionary=True)
    curs.execute(" select demande_paiement.id_demande,client.nom,dette.description as achat ,demande_paiement.description as method,demande_paiement.montant,demande_paiement.date_demande from demande_paiement join dette on demande_paiement.id_dette=dette.id_dette join client on dette.id_client=client.id_client where demande_paiement.status='en_attente' ")
    demandes=curs.fetchall()
    conn.close()
    return render_template("paiement_en_attente.html",demandes=demandes)
@app.route("/confirmer/<int:id_demande>")
def confirmer(id_demande):
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    curs=conn.cursor(dictionary=True)
    curs.execute("select * from demande_paiement where id_demande=%s",(id_demande,))
    demande=curs.fetchone()
    id_dette=demande['id_dette']
    curs.execute("select * from dette where id_dette=%s",(id_dette,))
    dette=curs.fetchone()
    nouveau_rest=(dette['montant_rest']-demande['montant'])
    if nouveau_rest<=0:
        nouveau_rest=0
        status='Soldée'
    else:
        status='Ouvert'
    curs.execute("update dette set montant_rest=%s,status=%s where id_dette=%s",(nouveau_rest,status,id_dette))
    if status=='Soldée':
        curs.execute("update dette set date_reg=now() where id_dette=%s",(id_dette,))
    curs.execute("update demande_paiement set status='confirmé' where id_demande=%s ",(id_demande,))
    conn.commit()
    conn.close()
    return redirect(url_for('liste_dette'))
@app.route("/refuse/<int:id_demande>")
def refuser(id_demande):
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    with conn.cursor(dictionary=True) as curs:
        curs.execute("update demande_paiement set status='refusé' where id_demande=%s ",(id_demande,))
        conn.commit()
        conn.close()
    return redirect(url_for('liste_dette'))
@app.route("/demandes_refuse")
def demandes_refuses():
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    curs=conn.cursor(dictionary=True)
    curs.execute("select client.nom,demande_paiement.montant,dette.description,demande_paiement.date_demande from demande_paiement join dette on demande_paiement.id_dette=dette.id_dette join client on dette.id_client=client.id_client where demande_paiement.status='refusé' ")
    demandes=curs.fetchall()
    conn.close()
    return render_template("demandes_refuses.html",demandes=demandes)
@app.route("/archive")
def archive():
    if 'nom' not in session:
        return redirect(url_for('login'))
    conn=connection()
    curs=conn.cursor(dictionary=True)
    curs.execute("select client.nom,dette.montant_tot,dette.description,dette.date_dette,dette.date_reg from dette join client on dette.id_client=client.id_client where dette.status='Soldée' ")
    archives=curs.fetchall()
    return render_template("archive.html",archives=archives)
@app.route("/recherche")
def recherche():
    if 'nom' not in session:
        return redirect(url_for('login'))
    mot=request.args.get('recherche','').strip()
    clients=[]
    if mot:
        conn=connection()
        curs=conn.cursor(dictionary=True)

        mot= "%" + mot + "%"
        curs.execute("select client.nom,dette.description,dette.montant_rest from dette join client on dette.id_client=client.id_client where client.nom like %s",(mot,))
        clients=curs.fetchall()
        conn.close()
    return render_template("resultat_recherche.html",clients=clients)
@app.route("/login",methods=['GET','POST'])
def login():
    erreur=""
    if request.method=='POST':
        nom=request.form.get('nom')
        mdp=request.form.get('mdp')
        conn=connection()
        curs=conn.cursor(dictionary=True)
        curs.execute("select * from user where nom=%s",(nom,))
        user=curs.fetchone()
        conn.close()
        if user and check_password_hash(user['mdp'],mdp):
            session['nom']=user['nom']
            return redirect(url_for('index'))
        else:
            erreur="Nom ou Mot de Passe Incorrect "
    return render_template("login.html",erreur=erreur)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/ajouter_avoir', methods=['GET', 'POST'])
def ajouter_avoir():
    conn = connection()
    curs = conn.cursor(dictionary=True)
    curs.execute("SELECT * FROM client")
    clients = curs.fetchall()
    if request.method == 'POST':
        id_client = request.form.get('id_client')
        montant = float(request.form.get('montant'))
        description = request.form.get('description')
        if montant <= 0:
            conn.close()
            return render_template('ajouter_avoir.html',clients=clients,erreur="Montant invalide")
        curs.execute("INSERT INTO avoir_client(id_client,montant,description)VALUES(%s,%s,%s)", (id_client,montant,description))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_avoirs'))
    conn.close()
    return render_template('ajouter_avoir.html',clients=clients)
@app.route('/liste_avoirs')
def liste_avoirs():
    conn = connection()
    curs = conn.cursor(dictionary=True)
    curs.execute(" SELECT avoir_client.id_avoir, client.nom, avoir_client.montant, avoir_client.description, avoir_client.date_avoir FROM avoir_client JOIN client ON avoir_client.id_client =client.id_client")
    avoirs = curs.fetchall()
    conn.close()
    return render_template('liste_avoirs.html',avoirs=avoirs)
@app.route('/utiliser_avoir/<int:id_avoir>',methods=['GET', 'POST'])
def utiliser_avoir(id_avoir):
    conn = connection()
    curs = conn.cursor(dictionary=True)
    curs.execute(" SELECT * FROM avoir_client WHERE id_avoir=%s", (id_avoir,))
    avoir = curs.fetchone()
    if request.method == 'POST':
        montant_achat = int(request.form.get('montant'))
        if montant_achat <= 0:
            conn.close()
            return render_template('utiliser_avoir.html',avoir=avoir,erreur="Montant invalide")
        if montant_achat > avoir['montant']:
            conn.close()
            return render_template('utiliser_avoir.html',avoir=avoir,erreur="Montant dépasse avoir")
        nouveau_montant = (avoir['montant']- montant_achat)
        if nouveau_montant == 0:
            curs.execute(" DELETE FROM avoir_client WHERE id_avoir=%s", (id_avoir,))
        curs.execute("UPDATE avoir_client SET montant=%s WHERE id_avoir=%s",(nouveau_montant,id_avoir))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_avoirs'))
    conn.close()
    return render_template('utiliser_avoir.html',avoir=avoir)
if __name__=="__main__":
   app.run()