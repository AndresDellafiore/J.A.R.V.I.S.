import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import queue
import threading

class JARVISGUI:
    def __init__(self, jarvis, gui_queue):
        self.jarvis = jarvis
        self.gui_queue = gui_queue
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S - Sistema Inteligente")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        
        # Configuración de estilo
        self.configure_styles()
        
        # Cargar assets
        self.load_assets()
        
        # Crear interfaz
        self.create_interface()
        
        # Procesar actualizaciones de la cola
        self.root.after(100, self.process_updates)

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#0a0a1a')
        self.style.configure('TLabel', background='#0a0a1a', foreground='#00ffcc', 
                           font=('Courier New', 12))
        self.style.configure('TButton', background='#003333', foreground='#00ffcc', 
                           font=('Courier New', 10))

    def load_assets(self):
        try:
            self.logo_img = ImageTk.PhotoImage(Image.open("assets/jarvis_logo.png").resize((200, 200)))
            self.bg_img = ImageTk.PhotoImage(Image.open("assets/iron_man_bg.jpg").resize((900, 600)))
        except:
            self.logo_img = None
            self.bg_img = None

    def create_interface(self):
        # Fondo
        bg_color = '#0a0a1a'
        if self.bg_img:
            self.bg_label = tk.Label(self.root, image=self.bg_img)
        else:
            self.bg_label = tk.Label(self.root, bg=bg_color)
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
            command=self.start_listening_thread
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
        
        # Configurar grid
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def process_updates(self):
        """Procesa las actualizaciones de la cola en el hilo principal"""
        try:
            while True:
                method, args, kwargs = self.gui_queue.get_nowait()
                if hasattr(self, method):
                    getattr(self, method)(*args, **kwargs)
        except queue.Empty:
            pass
        self.root.after(100, self.process_updates)

    def display_message(self, sender, message, is_user=False):
        self.display_text.configure(state='normal')
        tag = 'user' if is_user else 'jarvis'
        self.display_text.insert(tk.END, f"{sender}: {message}\n", tag)
        self.display_text.configure(state='disabled')
        self.display_text.see(tk.END)

    def update_status(self, text):
        self.status_label.config(text=f"Estado: {text}")

    def animate_speech(self, speaking):
        if speaking:
            self.current_color = 0
            self.speech_animation()
        else:
            if hasattr(self, 'anim_id'):
                self.root.after_cancel(self.anim_id)
            self.logo_label.config(bg='black')

    def speech_animation(self):
        colors = ['#ff0000', '#ff6600', '#ffcc00', '#00ff00', '#0066ff', '#6600ff']
        self.logo_label.config(bg=colors[self.current_color])
        self.current_color = (self.current_color + 1) % len(colors)
        self.anim_id = self.root.after(100, self.speech_animation)

    def start_listening_thread(self):
        """Inicia el reconocimiento de voz en un hilo separado"""
        if self.jarvis:
            threading.Thread(target=self.jarvis.listen, daemon=True).start()

    def show_settings(self):
        # Implementar ventana de configuración
        pass

    def exit_program(self):
        if self.jarvis:
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
    gui_queue = queue.Queue()
    gui = JARVISGUI(None, gui_queue)
    gui.run()