import pytesseract
from PIL import ImageGrab, Image
import openai
import tkinter as tk
from tkinter import messagebox

# Configuration de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'xxxx'

# Clé API OpenAI
openai.api_key = 'xxxx'

# Variables globales pour stocker la zone sélectionnée
selected_area = None

# Pré-prompt pour aider l'IA à comprendre la demande
pre_prompt = "je passe un test technique sur symfony 7, voici une question il faut que tu me donne la réponse sans explication et la plus courte possible, parle moi en francais :\n\n"

def capture_screen_area(x1, y1, x2, y2):
    # Capture de la zone spécifiée de l'écran
    screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screen.save("screenshot.png")
    return "screenshot.png"

def ocr_image(image_path):
    # Extraction du texte de l'image
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

def get_gpt_response(question):
    # Inclure le pré-prompt avant la question capturée
    full_prompt = pre_prompt + question
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=full_prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

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
        self.top = tk.Toplevel(master)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-alpha", 0.3)  # Rendre la fenêtre semi-transparente
        self.canvas = tk.Canvas(self.top, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect = None
        self.callback = callback
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