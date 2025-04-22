import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time
import threading
from tkinter.ttk import Progressbar

# Initialiser la webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erreur : Webcam non trouvée ou non accessible")
    exit()

# Initialiser MediaPipe
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
hands = mp_hands.Hands()
face = mp_face.FaceDetection(min_detection_confidence=0.5)

# Variables
distraction_count = 0
session_start_time = None
session_duration = 0
user_duration = 0

# Flags pour les messages motivants
halfway_message_shown = False
end_message_shown = False

# Affichage alerte Tkinter
def show_alert(message, bg_color):
    alert = tk.Tk()
    alert.title("Distraction Alert")
    tk.Label(alert, text=message, font=("Arial", 18, "bold"), fg="#FFFFFF", bg=bg_color, pady=20).pack(padx=20, pady=20)
    alert.after(5000, lambda: alert.destroy())  # Message reste pendant 5 secondes
    alert.mainloop()

# Lancer la session
def start_session():
    global session_start_time, user_duration
    if user_duration <= 0:
        messagebox.showerror("Erreur", "Veuillez définir une durée de session valide.")
        return
    session_start_time = time.time()
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    session_label.config(text=f"🧠 Prépare-toi pour {user_duration // 60} minutes de pure concentration ! 💪")
    threading.Thread(target=webcam_loop, daemon=True).start()

# Arrêter la session
def stop_session():
    global session_start_time, session_duration
    session_duration = time.time() - session_start_time
    session_duration_min = session_duration / 60
    session_label.config(text=f"Session terminée : {session_duration_min:.2f} minutes")
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    generate_report()

# Rapport de session
def generate_report():
    session_duration_min = session_duration / 60
    report_text = f"Tu t'es distrait {distraction_count} fois en {session_duration_min:.2f} minutes."
    with open("rapport_concentration.txt", "w") as f:
        f.write(report_text)
    print(report_text)

# Définir la durée
def set_session_duration():
    global user_duration
    try:
        user_duration = int(duration_entry.get()) * 60
        session_label.config(text=f"🧠 Prépare-toi pour {user_duration // 60} minutes de pure concentration ! 💪")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la durée.")

# Interface Tkinter
root = tk.Tk()
root.title("Distraction Blocker")
root.geometry("450x500")
root.config(bg="#f5f5f5")

title_label = tk.Label(root, text="Distraction Blocker", font=("Arial", 24, "bold"), fg="#FF6347", bg="#f5f5f5")
title_label.pack(pady=20)

session_label = tk.Label(root, text="Clique sur 'Commencer' pour démarrer la session", font=("Arial", 14), bg="#f5f5f5")
session_label.pack(pady=10)

duration_label = tk.Label(root, text="Durée de la session (minutes):", font=("Arial", 12), bg="#f5f5f5")
duration_label.pack(pady=5)
duration_entry = tk.Entry(root, font=("Arial", 14))
duration_entry.pack(pady=10)

set_button = tk.Button(root, text="Définir la durée", font=("Arial", 14), command=set_session_duration, bg="#4CAF50", fg="white", relief="flat", width=20)
set_button.pack(pady=10)

start_button = tk.Button(root, text="Commencer", font=("Arial", 14), command=start_session, bg="#4CAF50", fg="white", relief="flat", width=20)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Arrêter", font=("Arial", 14), command=stop_session, state="disabled", bg="#FF6347", fg="white", relief="flat", width=20)
stop_button.pack(pady=10)

# Ajouter la barre de progression
progress_label = tk.Label(root, text="Progression de la session:", font=("Arial", 12), bg="#f5f5f5")
progress_label.pack(pady=5)

progress = Progressbar(root, length=400, orient="horizontal", mode="determinate", maximum=100)
progress.pack(pady=20)

def on_enter(event): event.widget.config(bg="#45a049")
def on_leave(event): event.widget.config(bg="#4CAF50")

set_button.bind("<Enter>", on_enter)
set_button.bind("<Leave>", on_leave)
start_button.bind("<Enter>", on_enter)
start_button.bind("<Leave>", on_leave)
stop_button.bind("<Enter>", lambda e: e.widget.config(bg="#e55347"))
stop_button.bind("<Leave>", lambda e: e.widget.config(bg="#FF6347"))

# Boucle de détection
def webcam_loop():
    global distraction_count, halfway_message_shown, end_message_shown
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de capturer l'image")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_hands = hands.process(rgb_frame)
        results_face = face.process(rgb_frame)

        elapsed_time = time.time() - session_start_time
        progress_value = (elapsed_time / user_duration) * 100
        progress["value"] = progress_value  # Mise à jour de la barre de progression

        # Message à mi-parcours (50% du temps)
        if elapsed_time >= user_duration * 0.5 and not halfway_message_shown:
            show_alert("Bravo ! Tu as déjà atteint la moitié du parcours. Continue, tu es sur la bonne voie ! 🚀", "#4682B4")  # Bleu
            halfway_message_shown = True

        # Message à la fin de la session
        if elapsed_time >= user_duration and not end_message_shown:
            show_alert("Mission accomplie ! Félicitations, tu as terminé la session ! À la prochaine session ! 👏", "#32CD32")  # Vert
            end_message_shown = True
            stop_session()
            break

        # Détection des mains
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                if hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y > 0.8:
                    distraction_count += 1
                    show_alert("Tu t'es distrait, concentre-toi !", "#FF6347")  # Rouge

        # Détection du visage
        if not results_face.detections:
            distraction_count += 1
            show_alert("Pas de visage détecté, concentre-toi !", "#FF6347")  # Rouge

        cv2.imshow("Webcam - Distraction Blocker", frame)

        # Touche 'q' pour quitter
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_session()
            break

    cap.release()
    cv2.destroyAllWindows()

# Lancer l'interface
root.mainloop()
