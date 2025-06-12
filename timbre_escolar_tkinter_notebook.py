
# timbre_escolar_tkinter_notebook.py

import os                         # Permite gestionar rutas y comprobar existencia de archivos
import json                       # Proporciona funciones para leer y escribir archivos JSON
import datetime                   # Facilita la obtención y formateo de la fecha y hora actual
import pygame                     # Biblioteca para reproducir audio en formato MP3/WAV
import tkinter as tk              # Módulo principal de Tkinter para la interfaz gráfica
tk from tkinter import ttk, filedialog, messagebox  # Importa widgets avanzados, diálogos de archivos y mensajes

CONFIG_FILE = "config_customizable.json"  # Nombre del archivo JSON donde se guarda la configuración

class TimbreEscolarApp(tk.Tk):   # Define la clase principal que hereda de Tkinter.Tk
    def __init__(self):         # Constructor de la clase
        super().__init__()       # Llama al constructor de la ventana principal
        self.title("Configuración Timbre Escolar")  # Establece el título de la ventana
        self.geometry("1000x700")       # Define el tamaño inicial de la ventana (ancho x alto)
        self.configure(bg="#87CEFA")    # Asigna un color de fondo azul pastel

        # Si existe el archivo de configuración, se carga; en caso contrario, se define uno por defecto
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)  # Lee el JSON y lo convierte en un diccionario de Python
        else:
            # Configuración por defecto para turnos de mañana y tarde
            self.config = { ... }

        self.widgets = {"mañana": {}, "tarde": {}}  # Almacena referencias a los widgets (valores vinculados)
        self.estado_activo = False  # Indica si el temporizador está activo
        self.ultimo_evento = None   # Guardará la última hora procesada para evitar repeticiones

        self.build_ui()             # Llama al método que construye la interfaz completa
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)  # Inicializa el reproductor de audio

    def build_ui(self):          # Método para crear y organizar los widgets en la ventana
        notebook = ttk.Notebook(self)  # Crea un control de pestañas
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        for periodo in ("mañana", "tarde"):  # Itera sobre los dos turnos
            frame = ttk.Frame(notebook)  # Crea un frame por pestaña
            notebook.add(frame, text="Mañana" if periodo=="mañana" else "Tarde")  # Añade la pestaña

            canvas = tk.Canvas(frame, bg="#87CEFA", highlightthickness=0)  # Canvas para contener widgets con scroll
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)  # Barra de scroll vertical
            inner = ttk.Frame(canvas)  # Frame interior que irá dentro del canvas

            # Ajusta la zona de scroll automáticamente al cambiar el contenido
            inner.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0,0), window=inner, anchor="nw")  # Sitúa el frame interior
            canvas.configure(yscrollcommand=scrollbar.set)  # Conecta el canvas con la barra de scroll

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            self.build_group(inner, periodo)  # Llama a la función que añade los controles de cada horario

        footer = ttk.Frame(self)  # Crea el pie de página con botones y etiqueta de estado
        footer.pack(fill="x", side="bottom", pady=10)
        ttk.Button(footer, text="Guardar Configuración", command=self.actualizar_config).pack(side="left", padx=20)  # Botón guardar
        ttk.Button(footer, text="Iniciar Programa", command=self.toggle_programa).pack(side="left", padx=20)  # Botón iniciar/detener
        self.lbl_estado = ttk.Label(footer, text="Estado: Inactivo", background="#87CEFA", font=("Segoe UI",10,"bold"))  # Etiqueta de estado
        self.lbl_estado.pack(side="right", padx=20)

    def build_group(self, parent, periodo):  # Construye el formulario para un turno (mañana/tarde)
        for idx, key in enumerate(("hora1","hora2","hora3","recreo","hora4","hora5","fin_clase")):
            data = self.config[periodo][key]  # Obtiene los datos de configuración para este elemento
            row = idx * 4  # Calcula la fila base para situar widgets

            # Campo Nombre
            ttk.Label(parent, text="Nombre:", background="#87CEFA").grid(row=row, column=0, sticky="e", pady=2)
            v_nom = tk.StringVar(value=data["nombre"])  # Variable para el nombre
            ttk.Entry(parent, textvariable=v_nom, width=20).grid(row=row, column=1, padx=5)

            if key != "recreo":
                # Campo Hora (solo si no es recreo)
                ttk.Label(parent, text="Hora:", background="#87CEFA").grid(row=row, column=2, sticky="e")
                v_h = tk.StringVar(value=data["hora"])  # Variable para la hora
                ttk.Entry(parent, textvariable=v_h, width=7).grid(row=row, column=3, padx=5)
            else:
                # Recreo: Hora inicio
                ttk.Label(parent, text="Hora inicio:", background="#87CEFA").grid(row=row, column=2, sticky="e")
                v_hi = tk.StringVar(value=data["hora_inicio"])
                ttk.Entry(parent, textvariable=v_hi, width=7).grid(row=row, column=3, padx=5)

                # Recreo: Hora fin
                ttk.Label(parent, text="Hora fin:", background="#87CEFA").grid(row=row, column=4, sticky="e")
                v_hf = tk.StringVar(value=data["hora_fin"])
                ttk.Entry(parent, textvariable=v_hf, width=7).grid(row=row, column=5, padx=5)

            # Campo Canción
            ttk.Label(parent, text="Canción:", background="#87CEFA").grid(row=row+1, column=0, sticky="e")
            v_c = tk.StringVar(value=data["cancion"])  # Variable para la ruta de audio
            ttk.Entry(parent, textvariable=v_c, width=25).grid(row=row+1, column=1, columnspan=4, padx=5)
            ttk.Button(parent, text="Elegir", command=lambda p=periodo, k=key: self.seleccionar_archivo(p, k)).grid(row=row+1, column=5)

            # Campo Inicio (segundos)
            ttk.Label(parent, text="Inicio (s):", background="#87CEFA").grid(row=row+2, column=0, sticky="e")
            v_i = tk.IntVar(value=data["inicio"])  # Variable para segundos de inicio
            ttk.Spinbox(parent, from_=0, to=600, textvariable=v_i, width=5).grid(row=row+2, column=1)

            # Campo Duración (segundos)
            ttk.Label(parent, text="Duración (s):", background="#87CEFA").grid(row=row+2, column=2, sticky="e")
            v_d = tk.IntVar(value=data["duracion"])  # Variable para segundos de duración
            ttk.Spinbox(parent, from_=1, to=600, textvariable=v_d, width=5).grid(row=row+2, column=3)

            # Almacena referencias a las variables para actualización posterior
            if key != "recreo":
                self.widgets[periodo][key] = {"nombre": v_nom, "hora": v_h, "cancion": v_c, "inicio": v_i, "duracion": v_d}
            else:
                self.widgets[periodo][key] = {"nombre": v_nom, "hora_inicio": v_hi, "hora_fin": v_hf, "cancion": v_c, "inicio": v_i, "duracion": v_d}

    def seleccionar_archivo(self, periodo, momento):  # Maneja el diálogo para elegir archivo de audio
        ruta = filedialog.askopenfilename(filetypes=[("Audio","*.mp3 *.wav")])  # Muestra el explorador
        if ruta:
            self.widgets[periodo][momento]["cancion"].set(ruta)  # Actualiza la variable con la ruta

    def actualizar_config(self):  # Guarda en JSON los valores editados
        for p in ("mañana","tarde"):
            for k, w in self.widgets[p].items():
                self.config[p][k]["nombre"] = w["nombre"].get()
                if k != "recreo":
                    self.config[p][k]["hora"] = w["hora"].get()
                else:
                    self.config[p][k]["hora_inicio"] = w["hora_inicio"].get()
                    self.config[p][k]["hora_fin"] = w["hora_fin"].get()
                self.config[p][k]["cancion"] = w["cancion"].get()
                self.config[p][k]["inicio"] = int(w["inicio"].get())
                self.config[p][k]["duracion"] = int(w["duracion"].get())
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)  # Escribe el JSON en disco
        messagebox.showinfo("Guardado", "Configuración guardada.")  # Notifica al usuario

    def reproducir_sonido(self, ruta, ini, dur):  # Reproduce un fragmento de audio
        if os.path.exists(ruta):  # Solo si el archivo existe
            pygame.mixer.music.load(ruta)  # Carga la pista
            pygame.mixer.music.play(start=ini)  # Reproduce desde el segundo 'ini'
            self.after(dur*1000, pygame.mixer.music.stop)  # Detiene tras 'dur' segundos

    def comprobar_y_reproducir(self):  # Compara hora actual y dispara sonidos
        ahora = datetime.datetime.now().strftime("%H:%M")  # Obtiene 'HH:MM'
        if ahora == self.ultimo_evento:  # Si ya desencadenó este minuto, espera
            if self.estado_activo:
                self.after(60000, self.comprobar_y_reproducir)
            return
        self.ultimo_evento = ahora  # Marca el evento como procesado

        for p in ("mañana","tarde"):
            s = self.config[p]
            if ahora == s["hora1"]["hora"]:
                self.reproducir_sonido(s["hora1"]["cancion"], s["hora1"]["inicio"], s["hora1"]["duracion"])
                break
            if ahora == s["recreo"]["hora_inicio"]:
                self.reproducir_sonido(s["recreo"]["cancion"], s["recreo"]["inicio"], s["recreo"]["duracion"])
                break
            if ahora == s["recreo"]["hora_fin"]:
                self.reproducir_sonido(s["recreo"]["cancion"], s["recreo"]["inicio"], s["recreo"]["duracion"])
                break
            for c in ("hora2","hora3","hora4","hora5"):
                if ahora == s[c]["hora"]:
                    self.reproducir_sonido(s[c]["cancion"], s[c]["inicio"], s[c]["duracion"])
                    break
            if ahora == s["fin_clase"]["hora"]:
                self.reproducir_sonido(s["fin_clase"]["cancion"], s["fin_clase"]["inicio"], s["fin_clase"]["duracion"])
                break

        if self.estado_activo:
            self.after(60000, self.comprobar_y_reproducir)  # Programa la siguiente comprobación

    def toggle_programa(self):  # Inicia o detiene la comprobación periódica
        self.estado_activo = not self.estado_activo
        self.lbl_estado.config(text=f"Estado: {'Activo' if self.estado_activo else 'Inactivo'}")  # Actualiza etiqueta
        if self.estado_activo:
            self.comprobar_y_reproducir()  # Lanza la primera comprobación


if __name__ == "__main__":
    pygame.mixer.init()  # Inicializa el mezclador de audio
    app = TimbreEscolarApp()  # Crea la instancia de la aplicación
    app.mainloop()  # Inicia el bucle principal de la GUI


