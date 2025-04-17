import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time
import threading
import random

# Liste de messages motivants
motivational_messages = [
    "Hey, Concentre-toi!",
    "Allez, tu peux le faire!",
    "Ne perds pas ta concentration!",
    "Reste focus, c'est important!",
    "Tu es presque à la fin, continue!",
    "Concentration maximale, tu es capable!",
    "Rappelle-toi pourquoi tu as commencé!",
    "Garde les yeux sur ton objectif!"
]

# Initialiser la webcam
cap = cv2.VideoCapture(0)

# Vérifier si la webcam est bien ouverte
if not cap.isOpened():
    print("Erreur : Webcam non trouvée ou non accessible")
    exit()  # Quitter si la webcam n'est pas accessible

# Initialiser MediaPipe Hands et Face Detection
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
hands = mp_hands.Hands()
face = mp_face.FaceDetection(min_detection_confidence=0.5)

# Variables de suivi de la distraction
distraction_count = 0
session_start_time = None
session_duration = 0  # Durée de la session en secondes
user_duration = 0  # Durée déterminée par l'utilisateur en secondes

# Fonction pour afficher l'alerte Tkinter avec un message aléatoire
def show_alert():
    alert = tk.Tk()
    alert.title("Distraction Alert")
    
    # Choisir un message aléatoire parmi ceux de la liste
    message = random.choice(motivational_messages)
    
    tk.Label(alert, text=message, font=("Arial", 18, "bold"), fg="#FF6347", bg="#f0f8ff", pady=20).pack(padx=20, pady=20)
    alert.after(2000, lambda: alert.destroy())  # Fermeture après 2 secondes
    alert.mainloop()

# Fonction pour démarrer la session
def start_session():
    global session_start_time, user_duration
    if user_duration <= 0:
        messagebox.showerror("Erreur", "Veuillez définir une durée de session valide.")
        return
    session_start_time = time.time()
    start_button.config(state="disabled")  # Désactive le bouton après démarrage
    stop_button.config(state="normal")  # Active le bouton pour arrêter la session
    session_label.config(text=f"Session en cours ({user_duration // 60} minutes)...")
    # Lancer la boucle de détection dans un thread séparé
    threading.Thread(target=webcam_loop, daemon=True).start()

# Fonction pour arrêter la session et calculer la durée
def stop_session():
    global session_start_time, session_duration
    session_duration = time.time() - session_start_time  # Temps écoulé en secondes
    session_duration_min = session_duration / 60  # Convertir en minutes
    session_label.config(text=f"Session terminée : {session_duration_min:.2f} minutes")
    start_button.config(state="normal")  # Réactive le bouton "Commencer"
    stop_button.config(state="disabled")  # Désactive le bouton "Arrêter"
    generate_report()  # Générer le rapport à la fin de la session

# Fonction pour générer le rapport
def generate_report():
    session_duration_min = session_duration / 60
    report_text = f"Tu t'es distrait {distraction_count} fois en {session_duration_min:.2f} minutes."
    with open("rapport_concentration.txt", "w") as f:
        f.write(report_text)
    print(report_text)

# Fonction pour définir la durée de la session
def set_session_duration():
    global user_duration
    try:
        user_duration = int(duration_entry.get()) * 60  # Convertir en secondes
        session_label.config(text=f"Durée de la session : {user_duration // 60} minutes")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la durée.")

# Créer la fenêtre principale Tkinter
root = tk.Tk()
root.title("Distraction Blocker")
root.geometry("450x500")  # Définir la taille de la fenêtre
root.config(bg="#f5f5f5")  # Couleur de fond de la fenêtre

# Ajouter un titre
title_label = tk.Label(root, text="Distraction Blocker", font=("Arial", 24, "bold"), fg="#FF6347", bg="#f5f5f5")
title_label.pack(pady=20)

# Label pour afficher la durée de la session
session_label = tk.Label(root, text="Clique sur 'Commencer' pour démarrer la session", font=("Arial", 14), bg="#f5f5f5")
session_label.pack(pady=10)

# Entrée pour définir la durée de la session
duration_label = tk.Label(root, text="Durée de la session (minutes):", font=("Arial", 12), bg="#f5f5f5")
duration_label.pack(pady=5)
duration_entry = tk.Entry(root, font=("Arial", 14))
duration_entry.pack(pady=10)

# Bouton pour définir la durée de la session
set_button = tk.Button(root, text="Définir la durée", font=("Arial", 14), command=set_session_duration, bg="#4CAF50", fg="white", relief="flat", width=20)
set_button.pack(pady=10)

# Boutons pour démarrer et arrêter la session
start_button = tk.Button(root, text="Commencer", font=("Arial", 14), command=start_session, bg="#4CAF50", fg="white", relief="flat", width=20)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Arrêter", font=("Arial", 14), command=stop_session, state="disabled", bg="#FF6347", fg="white", relief="flat", width=20)
stop_button.pack(pady=10)

# Style pour les boutons (au survol)
def on_enter(event):
    event.widget.config(bg="#45a049")

def on_leave(event):
    event.widget.config(bg="#4CAF50")

set_button.bind("<Enter>", on_enter)
set_button.bind("<Leave>", on_leave)

start_button.bind("<Enter>", on_enter)
start_button.bind("<Leave>", on_leave)

stop_button.bind("<Enter>", on_enter)
stop_button.bind("<Leave>", on_leave)

# Boucle principale pour la détection de distractions
def webcam_loop():
    global distraction_count
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de capturer l'image de la webcam")
            break

        # Convertir l'image en RGB pour MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_hands = hands.process(rgb_frame)
        results_face = face.process(rgb_frame)

        # Détection des mains
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                # Vérifier si la main est trop proche du bas de l'image (proche du téléphone)
                if hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y > 0.8:  # Ajuste cette condition selon le placement de la main
                    distraction_count += 1
                    show_alert()

        # Détection du visage
        if not results_face.detections:
            # Si le visage est absent, l'étudiant regarde ailleurs
            distraction_count += 1
            show_alert()

        # Affichage de l'image
        cv2.imshow("Webcam - Distraction Blocker", frame)

        # Vérification de la durée et arrêter la session automatiquement
        elapsed_time = time.time() - session_start_time
        if elapsed_time >= user_duration:
            stop_session()
            break

        # Vérification de la touche 'q' pour quitter
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_session()
            break

    cap.release()
    cv2.destroyAllWindows()

# Démarrer la boucle Tkinter
root.mainloop()
