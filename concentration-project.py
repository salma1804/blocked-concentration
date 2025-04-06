import cv2
import mediapipe as mp
import tkinter as tk
from datetime import datetime
import time

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

# Fonction pour afficher l'alerte Tkinter
def show_alert():
    alert = tk.Tk()
    alert.title("Distraction Alert")
    tk.Label(alert, text="Hey, Concentre-toi!", font=("Arial", 18)).pack(padx=20, pady=20)
    alert.after(2000, lambda: alert.destroy())  # Fermeture après 2 secondes
    alert.mainloop()

# Fonction pour démarrer la session
def start_session():
    global session_start_time
    session_start_time = time.time()
    start_button.config(state="disabled")  # Désactive le bouton après démarrage
    stop_button.config(state="normal")  # Active le bouton pour arrêter la session
    session_label.config(text="Session en cours...")

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

# Créer la fenêtre principale Tkinter
root = tk.Tk()
root.title("Distraction Blocker")

# Label pour afficher la durée de la session
session_label = tk.Label(root, text="Clique sur 'Commencer' pour démarrer la session", font=("Arial", 14))
session_label.pack(pady=20)

# Boutons pour démarrer et arrêter la session
start_button = tk.Button(root, text="Commencer", font=("Arial", 14), command=start_session)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Arrêter", font=("Arial", 14), command=stop_session, state="disabled")
stop_button.pack(pady=10)

# Boucle principale pour la détection de distractions
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

    # Vérification de la touche 'q' pour quitter
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fermer la webcam et la fenêtre
cap.release()
cv2.destroyAllWindows()

# Démarrer la boucle Tkinter
root.mainloop()
