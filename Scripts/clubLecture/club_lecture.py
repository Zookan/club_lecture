import sqlite3
from datetime import date
import tkinter as tk
from tkinter import messagebox, simpledialog

try:
    from textblob import TextBlob
except ModuleNotFoundError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "textblob"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    from textblob import TextBlob
    import nltk

    nltk.download('brown')
    nltk.download('punkt')


def initialiser_db():
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS membres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        email TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS livres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT,
        auteur TEXT,
        annee_publication INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emprunts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        livre_id INTEGER,
        date_emprunt TEXT,
        date_retour TEXT,
        FOREIGN KEY (membre_id) REFERENCES membres(id),
        FOREIGN KEY (livre_id) REFERENCES livres(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commentaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        livre_id INTEGER,
        commentaire TEXT,
        sentiment REAL,
        FOREIGN KEY (membre_id) REFERENCES membres(id),
        FOREIGN KEY (livre_id) REFERENCES livres(id)
    )
    ''')

    conn.commit()
    conn.close()


def ajouter_membre(nom, email):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO membres (nom, email)
    VALUES (?, ?)
    ''', (nom, email))
    conn.commit()
    conn.close()
    messagebox.showinfo("Succès", f"Membre '{nom}' ajouté avec succès.")


def afficher_tous_les_membres():
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM membres')
    membres = cursor.fetchall()
    conn.close()
    membres_str = "\n".join([f"ID: {membre[0]}, Nom: {membre[1]}, Email: {membre[2]}" for membre in membres])
    messagebox.showinfo("Liste des membres", membres_str)


def trouver_membre_par_nom(nom):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM membres WHERE nom = ?', (nom,))
    membres = cursor.fetchall()
    conn.close()
    if membres:
        membres_str = "\n".join([f"ID: {membre[0]}, Nom: {membre[1]}, Email: {membre[2]}" for membre in membres])
        messagebox.showinfo("Membre trouvé", membres_str)
    else:
        messagebox.showinfo("Aucun membre trouvé", f"Aucun membre trouvé avec le nom: {nom}")


def ajouter_livre(titre, auteur, annee_publication):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO livres (titre, auteur, annee_publication)
    VALUES (?, ?, ?)
    ''', (titre, auteur, annee_publication))
    conn.commit()
    conn.close()
    messagebox.showinfo("Succès", f"Livre '{titre}' ajouté avec succès.")


def afficher_tous_les_livres():
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres')
    livres = cursor.fetchall()
    conn.close()
    livres_str = "\n".join([f"ID: {livre[0]}, Titre: {livre[1]}, Auteur: {livre[2]}, Année de publication: {livre[3]}" for livre in livres])
    messagebox.showinfo("Liste des livres", livres_str)


def trouver_livre_par_titre(titre):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres WHERE titre = ?', (titre,))
    livres = cursor.fetchall()
    conn.close()
    if livres:
        livres_str = "\n".join([f"ID: {livre[0]}, Titre: {livre[1]}, Auteur: {livre[2]}, Année de publication: {livre[3]}" for livre in livres])
        messagebox.showinfo("Livre trouvé", livres_str)
    else:
        messagebox.showinfo("Aucun livre trouvé", f"Aucun livre trouvé avec le titre: {titre}")


def emprunter_livre(membre_id, livre_id):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM emprunts WHERE livre_id = ? AND date_retour IS NULL', (livre_id,))
    emprunt_existant = cursor.fetchone()

    if emprunt_existant:
        messagebox.showwarning("Erreur", f"Le livre ID {livre_id} est déjà emprunté.")
    else:
        date_emprunt = date.today()
        cursor.execute('''
        INSERT INTO emprunts (membre_id, livre_id, date_emprunt)
        VALUES (?, ?, ?)
        ''', (membre_id, livre_id, date_emprunt))
        conn.commit()
        messagebox.showinfo("Succès", f"Livre ID {livre_id} emprunté par le membre ID {membre_id} avec succès.")

    conn.close()


def retourner_livre(membre_id, livre_id):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()

    date_retour = date.today()
    cursor.execute('''
    UPDATE emprunts
    SET date_retour = ?
    WHERE membre_id = ? AND livre_id = ? AND date_retour IS NULL
    ''', (date_retour, membre_id, livre_id))

    if cursor.rowcount == 0:
        messagebox.showwarning("Erreur", f"Aucun emprunt en cours trouvé pour le membre ID {membre_id} et le livre ID {livre_id}.")
    else:
        conn.commit()
        messagebox.showinfo("Succès", f"Livre ID {livre_id} retourné par le membre ID {membre_id} avec succès.")

    conn.close()


def ajouter_commentaire(membre_id, livre_id, commentaire_texte):
    conn = sqlite3.connect('club_lecture.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO commentaires (membre_id, livre_id, commentaire)
    VALUES (?, ?, ?)
    ''', (membre_id, livre_id, commentaire_texte))
    conn.commit()
    conn.close()
    messagebox.showinfo("Succès", f"Commentaire ajouté avec succès pour le livre ID {livre_id} par le membre ID {membre_id}.")


# affichage de l'ui
def initialiser_ui():
    root = tk.Tk()
    root.title("Club de Lecture")

    # Section Membres
    tk.Label(root, text="Gérer les Membres").grid(row=0, column=0, padx=10, pady=10)
    tk.Button(root, text="Ajouter Membre", command=ajouter_membre_ui).grid(row=1, column=0, padx=10, pady=5)
    tk.Button(root, text="Afficher Tous les Membres", command=afficher_tous_les_membres).grid(row=2, column=0, padx=10, pady=5)
    tk.Button(root, text="Trouver Membre par Nom", command=trouver_membre_par_nom_ui).grid(row=3, column=0, padx=10, pady=5)

    # Section Livres
    tk.Label(root, text="Gérer les Livres").grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Ajouter Livre", command=ajouter_livre_ui).grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="Afficher Tous les Livres", command=afficher_tous_les_livres).grid(row=2, column=1, padx=10, pady=5)
    tk.Button(root, text="Trouver Livre par Titre", command=trouver_livre_par_titre_ui).grid(row=3, column=1, padx=10, pady=5)

    # Section Emprunts
    tk.Label(root, text="Gérer les Emprunts").grid(row=0, column=2, padx=10, pady=10)
    tk.Button(root, text="Emprunter Livre", command=emprunter_livre_ui).grid(row=1, column=2, padx=10, pady=5)
    tk.Button(root, text="Retourner Livre", command=retourner_livre_ui).grid(row=2, column=2, padx=10, pady=5)

    # Section Commentaires
    tk.Label(root, text="Gérer les Commentaires").grid(row=0, column=3, padx=10, pady=10)
    tk.Button(root, text="Ajouter Commentaire", command=ajouter_commentaire_ui).grid(row=1, column=3, padx=10, pady=5)

    root.mainloop()


def ajouter_membre_ui():
    nom = simpledialog.askstring("Ajouter Membre", "Nom du membre:")
    email = simpledialog.askstring("Ajouter Membre", "Email du membre:")
    if nom and email:
        ajouter_membre(nom, email)


def trouver_membre_par_nom_ui():
    nom = simpledialog.askstring("Trouver Membre par Nom", "Nom du membre:")
    if nom:
        trouver_membre_par_nom(nom)


def ajouter_livre_ui():
    titre = simpledialog.askstring("Ajouter Livre", "Titre du livre:")
    auteur = simpledialog.askstring("Ajouter Livre", "Auteur du livre:")
    annee_publication = simpledialog.askinteger("Ajouter Livre", "Année de publication du livre:")
    if titre and auteur and annee_publication:
        ajouter_livre(titre, auteur, annee_publication)


def trouver_livre_par_titre_ui():
    titre = simpledialog.askstring("Trouver Livre par Titre", "Titre du livre:")
    if titre:
        trouver_livre_par_titre(titre)


def emprunter_livre_ui():
    membre_id = simpledialog.askinteger("Emprunter Livre", "ID du membre:")
    livre_id = simpledialog.askinteger("Emprunter Livre", "ID du livre:")
    if membre_id and livre_id:
        emprunter_livre(membre_id, livre_id)


def retourner_livre_ui():
    membre_id = simpledialog.askinteger("Retourner Livre", "ID du membre:")
    livre_id = simpledialog.askinteger("Retourner Livre", "ID du livre:")
    if membre_id and livre_id:
        retourner_livre(membre_id, livre_id)


def ajouter_commentaire_ui():
    membre_id = simpledialog.askinteger("Ajouter Commentaire", "ID du membre:")
    livre_id = simpledialog.askinteger("Ajouter Commentaire", "ID du livre:")
    commentaire_texte = simpledialog.askstring("Ajouter Commentaire", "Texte du commentaire:")
    if membre_id and livre_id and commentaire_texte:
        ajouter_commentaire(membre_id, livre_id, commentaire_texte)


# Initialiser la base de données et lancer l'interface utilisateur
initialiser_db()
initialiser_ui()
