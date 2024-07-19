import os
import pytesseract
from PIL import Image, ImageGrab
import openai
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API et le chemin de Tesseract depuis les variables d'environnement
openai.api_key = os.getenv('OPENAI_API_KEY')
tesseract_cmd_path = os.getenv('TESSERACT_CMD_PATH')

# Configuration de Tesseract
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

# Variables globales pour stocker la zone sélectionnée
selected_area = None

# Pré-prompt pour aider l'IA à comprendre la demande
pre_prompt = "Voici une question type qcm sur symfony 7, il peut y avoir plusieurs réponse possible, donne moi uniquement la ou les bonnes réponses, je ne veux pas d'explication, soit bref:\n\n"

def capture_screen_area(x1, y1, x2, y2):
    # Vérification et ajustement des coordonnées
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # Capture de la zone spécifiée de l'écran avec Pillow
    print(f"Capture d'écran: ({x1}, {y1}) - ({x2}, {y2})")  # Debugging line
    bbox = (x1, y1, x2, y2)
    screen = ImageGrab.grab(bbox)

    # Générer un nom de fichier unique basé sur la date et l'heure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"

    screen.save(filename)
    return filename

def ocr_image(image_path):
    # Extraction du texte de l'image
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

def get_gpt_response(question):
    # Inclure le pré-prompt avant la question capturée
    full_prompt = pre_prompt + question
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": pre_prompt},
            {"role": "user", "content": question}
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

def select_area():
    # Fonction de sélection de la zone à capturer
    root.attributes("-alpha", 0.3)
    area_selector = AreaSelector(root, on_area_selected)
    root.wait_window(area_selector.top)
    root.attributes("-alpha", 1.0)  # Assure le retour à la normale après la sélection

def on_area_selected(x1, y1, x2, y2):
    global selected_area
    selected_area = (x1, y1, x2, y2)
    messagebox.showinfo("Zone sélectionnée", f"Zone sélectionnée : ({x1}, {y1}) - ({x2}, {y2})")

def capture_and_process():
    if selected_area:
        image_path = capture_screen_area(*selected_area)
        text = ocr_image(image_path)

        if text.strip():  # Vérifie s'il y a du texte capturé
            response = get_gpt_response(text)
            messagebox.showinfo("Réponse GPT", response)
        else:
            messagebox.showwarning("Attention", "Aucun texte détecté dans la capture d'écran.")
    else:
        messagebox.showwarning("Attention", "Aucune zone sélectionnée. Veuillez sélectionner une zone d'abord.")

class AreaSelector:
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback

        # Obtenir les dimensions de l'écran
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        print(f"Dimensions de l'écran: {screen_width}x{screen_height}")  # Debugging line

        # Créer une fenêtre sans décoration couvrant l'écran
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)  # Supprimer les décorations de la fenêtre
        self.top.geometry(f"{screen_width}x{screen_height}+0+0")
        self.top.attributes("-alpha", 0.3)  # Rendre la fenêtre semi-transparente
        self.top.configure(bg='gray')  # Set background to gray

        self.canvas = tk.Canvas(self.top, cursor="cross", bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        self.top.destroy()
        self.callback(int(self.start_x), int(self.start_y), int(self.end_x), int(self.end_y))

# Configuration de l'interface graphique
root = tk.Tk()
root.title("Capture et GPT Assistant")

# Bouton pour sélectionner la zone
select_button = tk.Button(root, text="Sélectionner la zone", command=select_area, cursor="hand2")
select_button.pack(pady=10)

# Bouton pour capturer la zone et obtenir une réponse
capture_button = tk.Button(root, text="Capturer et obtenir une réponse", command=capture_and_process, cursor="hand2")
capture_button.pack(pady=10)

root.mainloop()
