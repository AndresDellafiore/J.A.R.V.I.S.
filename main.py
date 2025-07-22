import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os
import threading

class JARVISGUI:
    def __init__(self, jarvis):
        self.jarvis = jarvis
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S - Sistema Inteligente")
        self.root.geometry("900x600")
        self.root.configure(bg='#0a0a1a')
        
        # Configuración de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#0a0a1a')
        self.style.configure('TLabel', background='#0a0a1a', foreground='#00ffcc', font=('Courier New', 12))
        self.style.configure('TButton', background='#003333', foreground='#00ffcc', font=('Courier New', 10))
        
        # Cargar assets
        self.load_assets()
        
        # Crear interfaz
        self.create_interface()
        
        # Variables de animación
        self.animating = False
        self.animation_frames = []
        self.current_animation_frame = 0
        self.load_animation_frames()
        
    def load_assets(self):
        # Cargar imágenes (debes tener estas imágenes en una carpeta assets/)
        try:
            self.logo_img = ImageTk.PhotoImage(Image.open("assets/jarvis_logo.png").resize((200, 200)))
            self.bg_img = ImageTk.PhotoImage(Image.open("assets/iron_man_bg.jpg").resize((900, 600)))
        except:
            # Imágenes por defecto si no se encuentran los archivos
            self.logo_img = None
            self.bg_img = None
    
    def load_animation_frames(self):
        # Cargar frames de animación (simulado)
        self.animation_frames = ["frame1", "frame2", "frame3", "frame4"]
    
    def create_interface(self):
        # Fondo
        self.bg_label = tk.Label(self.root, image=self.bg_img)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Marco principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center', width=800, height=500)
        
        # Logo
        self.logo_label = tk.Label(self.main_frame, image=self.logo_img, bg='black')
        self.logo_label.grid(row=0, column=0, padx=20, pady=10, sticky='nw')
        
        # Panel de visualización
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=10, sticky='nsew')
        
        self.display_text = scrolledtext.ScrolledText(
            self.display_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            bg='black',
            fg='#00ffcc',
            font=('Courier New', 12),
            insertbackground='#00ffcc'
        )
        self.display_text.pack(fill='both', expand=True)
        self.display_text.configure(state='disabled')
        
        # Panel de estado
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky='sw')
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Estado: Inicializando...",
            font=('Courier New', 10)
        )
        self.status_label.pack()
        
        # Panel de controles
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.listen_btn = ttk.Button(
            self.control_frame,
            text="Escuchar",
            command=self.start_listening
        )
        self.listen_btn.pack(side='left', padx=10)
        
        self.settings_btn = ttk.Button(
            self.control_frame,
            text="Configuración",
            command=self.show_settings
        )
        self.settings_btn.pack(side='left', padx=10)
        
        self.exit_btn = ttk.Button(
            self.control_frame,
            text="Salir",
            command=self.exit_program
        )
        self.exit_btn.pack(side='left', padx=10)
        
        # Configurar grid weights
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def display_message(self, sender, message, is_user=False):
        self.display_text.configure(state='normal')
        
        if is_user:
            self.display_text.insert(tk.END, f"Usuario: {message}\n", 'user')
        else:
            self.display_text.insert(tk.END, f"JARVIS: {message}\n", 'jarvis')
        
        self.display_text.configure(state='disabled')
        self.display_text.see(tk.END)
    
    def update_status(self, message):
        self.status_label.config(text=f"Estado: {message}")
    
    def animate_speech(self, speaking):
        if speaking:
            self.animating = True
            threading.Thread(target=self._speech_animation, daemon=True).start()
        else:
            self.animating = False
    
    def _speech_animation(self):
        while self.animating:
            # Simular animación cambiando el color del logo
            colors = ['#ff0000', '#ff6600', '#ffcc00', '#00ff00', '#0066ff', '#6600ff']
            for color in colors:
                if not self.animating:
                    break
                self.logo_label.config(bg=color)
                self.root.update()
                self.root.after(100)
        
        # Restaurar color original
        self.logo_label.config(bg='black')
    
    def start_listening(self):
        threading.Thread(target=self.jarvis.listen, daemon=True).start()
    
    def show_settings(self):
        # Implementar ventana de configuración
        pass
    
    def exit_program(self):
        self.jarvis.running = False
        self.root.destroy()
    
    def show_interface(self):
        self.root.deiconify()
    
    def hide_interface(self):
        self.root.withdraw()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Para pruebas
    gui = JARVISGUI(None)
    gui.run()