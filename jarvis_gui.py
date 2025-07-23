import tkinter as tk
from tkinter import scrolledtext, font as tkfont
from PIL import Image, ImageTk

class JARVISGUI:
    def __init__(self, jarvis):
        self.jarvis = jarvis
        self.root = tk.Tk()
        self.setup_window()
        self.setup_style()
        self.setup_ui()
        self.schedule_updates()

    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title("J.A.R.V.I.S. - Just A Rather Very Intelligent System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0a0a0a")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_style(self):
        """Configura los estilos visuales"""
        self.title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.text_font = tkfont.Font(family="Consolas", size=12)
        self.status_font = tkfont.Font(family="Helvetica", size=10)
        
        # Colores estilo Iron Man
        self.primary_color = "#52B2E0"
        self.secondary_color = "#FF4C4C"
        self.bg_color = "#0a0a0a"
        self.text_bg = "#1a1a1a"
        self.text_fg = "#ffffff"

    def setup_ui(self):
        """Configura los elementos de la interfaz"""
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_header()
        self.setup_conversation_area()
        self.setup_status_bar()

    def setup_header(self):
        """Configura la cabecera con logo"""
        self.header_frame = tk.Frame(self.main_frame, bg="#121212")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.logo_image = None
        self.setup_logo()
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="J.A.R.V.I.S. - Just A Rather Very Intelligent System",
            font=self.title_font,
            fg=self.primary_color,
            bg="#121212"
        )
        self.title_label.pack(side=tk.LEFT, padx=10)

    def setup_logo(self):
        """Configura el logo con manejo de errores"""
        try:
            img = Image.open("assets/logo.png")
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self.header_frame, image=self.logo_image, bg="#121212")
            logo_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error cargando logo: {e}")

    def setup_conversation_area(self):
        """Configura el área de conversación"""
        self.text_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=self.text_font,
            bg=self.text_bg,
            fg=self.text_fg,
            insertbackground="white",
            padx=10,
            pady=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Configurar tags para diferentes tipos de mensajes
        self.text_area.tag_config("jarvis", foreground=self.primary_color)
        self.text_area.tag_config("user", foreground="#ffffff")
        self.text_area.tag_config("system", foreground="#888888")

    def setup_status_bar(self):
        """Configura la barra de estado"""
        self.status_var = tk.StringVar()
        self.status_var.set("Sistema iniciado - Esperando comandos")
        
        self.status_bar = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=self.status_font,
            fg=self.text_fg,
            bg="#121212",
            padx=10
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def update_display(self, text):
        """Actualiza el área de texto con manejo seguro"""
        try:
            self.text_area.config(state=tk.NORMAL)
            
            if text.startswith("JARVIS:"):
                self.text_area.insert(tk.END, text + "\n", "jarvis")
            elif text.startswith("Usuario:"):
                self.text_area.insert(tk.END, text + "\n", "user")
            else:
                self.text_area.insert(tk.END, text + "\n", "system")
                
            self.text_area.config(state=tk.DISABLED)
            self.text_area.see(tk.END)
        except Exception as e:
            print(f"Error en update_display: {e}")

    def update_status(self, text):
        """Actualiza la barra de estado de manera segura"""
        try:
            self.status_var.set(text)
            self.root.update()
        except Exception as e:
            print(f"Error en update_status: {e}")

    def schedule_updates(self):
        """Programa actualizaciones periódicas con manejo seguro"""
        try:
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(100, self.schedule_updates)
        except Exception as e:
            print(f"Error en schedule_updates: {e}")

    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.jarvis.shutdown()

    def run(self):
        """Inicia la interfaz gráfica"""
        self.root.mainloop()