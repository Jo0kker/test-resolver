import os
import pytesseract
from PIL import Image, ImageGrab
from openai import OpenAI
import tkinter as tk
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, jsonify
import socket

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API et le chemin de Tesseract depuis les variables d'environnement
tesseract_cmd_path = os.getenv('TESSERACT_CMD_PATH')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
port = int(os.getenv('FLASK_PORT', 5000))  # Utiliser 5000 comme port par défaut

# Configuration de Tesseract
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

# Variables globales pour stocker la zone sélectionnée
selected_area = None

# Pré-prompt pour aider l'IA à comprendre la demande
pre_prompt = "Voici une question type qcm sur symfony, il peut y avoir plusieurs réponse possible, donne moi uniquement la ou les bonnes réponses, je ne veux pas d'explication, soit bref:\n\n"

app = Flask(__name__)

def get_ip_address():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

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
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": pre_prompt},
            {"role": "user", "content": question}
        ],
        max_tokens=150,
        temperature=0.5,
        top_p=1.0
    )
    return response.choices[0].message.content.strip()

@app.route('/select_area', methods=['POST'])
def api_select_area():
    global selected_area
    data = request.json
    x1, y1, x2, y2 = data['x1'], data['y1'], data['x2'], data['y2']
    selected_area = (x1, y1, x2, y2)
    return jsonify({"status": "zone selected", "area": selected_area})

@app.route('/capture_and_process', methods=['POST'])
def api_capture_and_process():
    if selected_area:
        image_path = capture_screen_area(*selected_area)
        text = ocr_image(image_path)

        if text.strip():  # Vérifie s'il y a du texte capturé
            response = get_gpt_response(text)
            return jsonify({"response": response})
        else:
            return jsonify({"error": "No text detected in the screenshot"})
    else:
        return jsonify({"error": "No area selected"})

def on_area_selected(x1, y1, x2, y2):
    global selected_area
    selected_area = (x1, y1, x2, y2)
    print(f"Zone sélectionnée : ({x1}, {y1}) - ({x2}, {y2})")

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
        root.config(cursor="")
        self.callback(int(self.start_x), int(self.start_y), int(self.end_x), int(self.end_y))

# Configuration de l'interface graphique
root = tk.Tk()
root.title("Capture et GPT Assistant")

# Bouton pour sélectionner la zone
select_button = tk.Button(root, text="Sélectionner la zone", command=lambda: AreaSelector(root, on_area_selected), cursor="hand2")
select_button.pack(pady=10)

# Afficher l'adresse IP
ip_address = get_ip_address()
tk.Label(root, text=f"API accessible à: http://{ip_address}:{port}").pack(pady=10)

# Lancer l'application Flask dans un thread séparé
import threading
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()

root.mainloop()
