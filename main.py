# ============================================================
# APHPM — Serveur Web Flask avec panneau Admin
# ============================================================

import os
import json
import uuid
from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for)
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='Templates', static_folder='Static')
app.secret_key = "aphpm_secret_key_changez_moi_2025"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "aphpm2025"

UPLOAD_FOLDER  = os.path.join("Static", "uploads")
ALLOWED_IMAGES = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_VIDEOS = {"mp4", "webm", "ogg", "mov"}
DATA_FILE      = os.path.join("data", "content.json")
MAX_FILE_MB    = 50

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# ============================================================
# DONNÉES PAR DÉFAUT
# ============================================================

SITE_DEFAUT = {
    "nom_site": "APHPM",
    "slogan": "Association des Personnes Handicapées Physique et Mentale",
    "hero_badge": "Association loi 1901 · Dakar, Sénégal",
    "hero_titre_1": "Pour l'inclusion",
    "hero_titre_2": "et la dignité des",
    "hero_titre_3": "personnes handicapées",
    "hero_sous_titre": "L'APHPM accompagne, défend et valorise les personnes handicapées physiques et mentales au Sénégal depuis plus de 10 ans.",
    "hero_btn_1": "Découvrir nos services",
    "hero_btn_2": "Nous contacter",
    "stat_1_num": "500+",
    "stat_1_label": "Membres",
    "stat_2_num": "10+",
    "stat_2_label": "Années",
    "stat_3_num": "3",
    "stat_3_label": "Régions",
    "about_p1": "L'Association des Personnes Handicapées Physique et Mentale (APHPM) a été fondée pour défendre les droits et améliorer les conditions de vie des personnes handicapées au Sénégal.",
    "about_p2": "Nous travaillons à l'inclusion sociale, économique et culturelle de nos membres, en leur fournissant un accompagnement personnalisé, des formations professionnelles et un accès aux soins de santé.",
    "vision_titre": "Notre vision",
    "vision_texte": "Un Sénégal où chaque personne handicapée vit dans la dignité, bénéficie de l'égalité des droits et participe pleinement à la vie de la société.",
    "contact_adresse": "Dakar, Sénégal",
    "contact_telephone": "+221 XX XXX XX XX",
    "contact_email": "contact@aphpm.org",
    "footer_desc": "Association des Personnes Handicapées Physique et Mentale\nDakar, Sénégal — Fondée pour l'inclusion et la dignité",
    "footer_copy": "© 2025 APHPM. Tous droits réservés.",
    "couleur_navy": "#0d1f3c",
    "couleur_gold": "#c8922a",
}

# ============================================================
# HELPERS
# ============================================================

def lire_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"photos": [], "videos": [], "temoignages": [],
                "actualites": [], "services": [], "site": {}}

def sauvegarder_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_site_config():
    data = lire_data()
    config = SITE_DEFAUT.copy()
    config.update(data.get("site", {}))
    return config

def extension_ok(filename, extensions):
    return ("." in filename and
            filename.rsplit(".", 1)[1].lower() in extensions)

def admin_requis(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_connecte"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def logo_existe():
    for ext in ALLOWED_IMAGES:
        if os.path.exists(os.path.join("Static", f"logo.{ext}")):
            return f"/static/logo.{ext}"   # ✅ minuscule
    return None

messages_recus = []

# ============================================================
# ROUTES PUBLIQUES
# ============================================================

@app.route("/")
def accueil():
    data = lire_data()
    logo = logo_existe()
    site = get_site_config()
    return render_template("index.html", data=data, logo=logo, site=site)

@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    if not data.get("prenom") or not data.get("email") or not data.get("message"):
        return jsonify({"success": False,
                        "message": "Veuillez remplir tous les champs obligatoires."}), 400
    msg = {
        "prenom":  data.get("prenom"),
        "nom":     data.get("nom", ""),
        "email":   data.get("email"),
        "objet":   data.get("objet", "Non précisé"),
        "message": data.get("message")
    }
    messages_recus.append(msg)
    return jsonify({"success": True,
                    "message": "✅ Merci ! Votre message a bien été envoyé. Nous vous répondrons sous 48h."})

# ============================================================
# AUTHENTIFICATION ADMIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    erreur = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_connecte"] = True
            return redirect(url_for("admin"))
        else:
            erreur = "Identifiants incorrects. Réessayez."
    return render_template("login.html", erreur=erreur)

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ============================================================
# PANNEAU ADMIN
# ============================================================

@app.route("/admin")
@admin_requis
def admin():
    data = lire_data()
    logo = logo_existe()
    site = get_site_config()
    return render_template("admin.html", data=data,
                           messages=messages_recus, logo=logo, site=site)

# ============================================================
# ADMIN — LOGO
# ============================================================

@app.route("/admin/logo/changer", methods=["POST"])
@admin_requis
def changer_logo():
    fichier = request.files.get("logo")
    if not fichier or fichier.filename == "":
        return jsonify({"success": False, "message": "Aucun fichier sélectionné."})
    if not extension_ok(fichier.filename, ALLOWED_IMAGES):
        return jsonify({"success": False, "message": "Format non supporté."})
    for ext in ALLOWED_IMAGES:
        ancien = os.path.join("Static", f"logo.{ext}")
        if os.path.exists(ancien):
            os.remove(ancien)
    ext = fichier.filename.rsplit(".", 1)[1].lower()
    chemin = os.path.join("Static", f"logo.{ext}")
    fichier.save(chemin)
    return jsonify({"success": True, "message": "✅ Logo mis à jour !", "url": f"/static/logo.{ext}"})  # ✅ minuscule

@app.route("/admin/logo/supprimer", methods=["DELETE"])
@admin_requis
def supprimer_logo():
    supprime = False
    for ext in ALLOWED_IMAGES:
        chemin = os.path.join("Static", f"logo.{ext}")
        if os.path.exists(chemin):
            os.remove(chemin)
            supprime = True
    if supprime:
        return jsonify({"success": True, "message": "Logo supprimé."})
    return jsonify({"success": False, "message": "Aucun logo trouvé."})

# ============================================================
# ADMIN — PERSONNALISATION DU SITE
# ============================================================

@app.route("/admin/site/sauvegarder", methods=["POST"])
@admin_requis
def sauvegarder_site():
    d = request.get_json()
    data = lire_data()
    if "site" not in data:
        data["site"] = {}
    for key in SITE_DEFAUT.keys():
        if key in d:
            data["site"][key] = d[key]
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "✅ Modifications sauvegardées !"})

# ============================================================
# ADMIN — PHOTOS
# ============================================================

@app.route("/admin/photos/ajouter", methods=["POST"])
@admin_requis
def ajouter_photo():
    fichier = request.files.get("photo")
    legende = request.form.get("legende", "").strip()
    if not fichier or fichier.filename == "":
        return jsonify({"success": False, "message": "Aucun fichier sélectionné."})
    if not extension_ok(fichier.filename, ALLOWED_IMAGES):
        return jsonify({"success": False, "message": "Format non supporté."})
    nom = str(uuid.uuid4()) + "_" + secure_filename(fichier.filename)
    fichier.save(os.path.join(UPLOAD_FOLDER, nom))
    data = lire_data()
    data["photos"].append({"id": str(uuid.uuid4()), "fichier": nom, "legende": legende})
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Photo ajoutée !"})

@app.route("/admin/photos/supprimer/<photo_id>", methods=["DELETE"])
@admin_requis
def supprimer_photo(photo_id):
    data = lire_data()
    photo = next((p for p in data["photos"] if p["id"] == photo_id), None)
    if not photo:
        return jsonify({"success": False, "message": "Photo introuvable."})
    chemin = os.path.join(UPLOAD_FOLDER, photo["fichier"])
    if os.path.exists(chemin):
        os.remove(chemin)
    data["photos"] = [p for p in data["photos"] if p["id"] != photo_id]
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Photo supprimée."})

# ============================================================
# ADMIN — VIDÉOS
# ============================================================

@app.route("/admin/videos/ajouter", methods=["POST"])
@admin_requis
def ajouter_video():
    titre   = request.form.get("titre", "").strip()
    url_yt  = request.form.get("url_youtube", "").strip()
    fichier = request.files.get("video")
    data    = lire_data()
    if url_yt:
        data["videos"].append({"id": str(uuid.uuid4()), "type": "youtube", "url": url_yt, "titre": titre})
        sauvegarder_data(data)
        return jsonify({"success": True, "message": "Vidéo YouTube ajoutée !"})
    if fichier and fichier.filename:
        if not extension_ok(fichier.filename, ALLOWED_VIDEOS):
            return jsonify({"success": False, "message": "Format non supporté."})
        nom = str(uuid.uuid4()) + "_" + secure_filename(fichier.filename)
        fichier.save(os.path.join(UPLOAD_FOLDER, nom))
        data["videos"].append({"id": str(uuid.uuid4()), "type": "fichier", "fichier": nom, "titre": titre})
        sauvegarder_data(data)
        return jsonify({"success": True, "message": "Vidéo uploadée !"})
    return jsonify({"success": False, "message": "Aucune vidéo fournie."})

@app.route("/admin/videos/supprimer/<video_id>", methods=["DELETE"])
@admin_requis
def supprimer_video(video_id):
    data = lire_data()
    video = next((v for v in data["videos"] if v["id"] == video_id), None)
    if not video:
        return jsonify({"success": False, "message": "Vidéo introuvable."})
    if video.get("type") == "fichier":
        chemin = os.path.join(UPLOAD_FOLDER, video["fichier"])
        if os.path.exists(chemin):
            os.remove(chemin)
    data["videos"] = [v for v in data["videos"] if v["id"] != video_id]
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Vidéo supprimée."})

# ============================================================
# ADMIN — TÉMOIGNAGES
# ============================================================

@app.route("/admin/temoignages/ajouter", methods=["POST"])
@admin_requis
def ajouter_temoignage():
    d = request.get_json()
    if not d.get("nom") or not d.get("texte"):
        return jsonify({"success": False, "message": "Nom et texte obligatoires."})
    data = lire_data()
    initiales = "".join(w[0].upper() for w in d["nom"].split()[:2])
    data["temoignages"].append({
        "id": str(uuid.uuid4()), "initiales": initiales,
        "nom": d["nom"], "lieu": d.get("lieu", ""), "texte": d["texte"]
    })
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Témoignage ajouté !"})

@app.route("/admin/temoignages/supprimer/<tem_id>", methods=["DELETE"])
@admin_requis
def supprimer_temoignage(tem_id):
    data = lire_data()
    data["temoignages"] = [t for t in data["temoignages"] if t["id"] != tem_id]
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Témoignage supprimé."})

# ============================================================
# ADMIN — ACTUALITÉS
# ============================================================

@app.route("/admin/actualites/ajouter", methods=["POST"])
@admin_requis
def ajouter_actualite():
    d = request.get_json()
    if not d.get("titre") or not d.get("contenu"):
        return jsonify({"success": False, "message": "Titre et contenu obligatoires."})
    data = lire_data()
    data["actualites"].append({
        "id": str(uuid.uuid4()), "titre": d["titre"],
        "contenu": d["contenu"], "date": d.get("date", ""), "emoji": d.get("emoji", "📰")
    })
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Actualité ajoutée !"})

@app.route("/admin/actualites/supprimer/<actu_id>", methods=["DELETE"])
@admin_requis
def supprimer_actualite(actu_id):
    data = lire_data()
    data["actualites"] = [a for a in data["actualites"] if a["id"] != actu_id]
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Actualité supprimée."})

# ============================================================
# ADMIN — SERVICES
# ============================================================

@app.route("/admin/services/ajouter", methods=["POST"])
@admin_requis
def ajouter_service():
    d = request.get_json()
    if not d.get("titre") or not d.get("description"):
        return jsonify({"success": False, "message": "Titre et description obligatoires."})
    data = lire_data()
    data["services"].append({
        "id": str(uuid.uuid4()), "emoji": d.get("emoji", "⭐"),
        "titre": d["titre"], "description": d["description"]
    })
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Service ajouté !"})

@app.route("/admin/services/supprimer/<service_id>", methods=["DELETE"])
@admin_requis
def supprimer_service(service_id):
    data = lire_data()
    data["services"] = [s for s in data["services"] if s["id"] != service_id]
    sauvegarder_data(data)
    return jsonify({"success": True, "message": "Service supprimé."})

# ============================================================
# ADMIN — MESSAGES
# ============================================================

@app.route("/admin/messages")
@admin_requis
def voir_messages():
    return jsonify({"total": len(messages_recus), "messages": messages_recus})

# ============================================================
# DÉMARRAGE
# ============================================================

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000
    print("🚀 Serveur APHPM démarré !")
    print(f"🌐 Local          : http://127.0.0.1:{port}")
    print(f"🌐 Réseau         : http://192.168.1.11:{port}")
    print(f"🔐 Panneau admin  : http://192.168.1.11:{port}/admin")
    print("⛔ Pour arrêter   : CTRL+C\n")
    app.run(debug=True, host=host, port=port)