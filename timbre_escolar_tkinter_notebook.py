# timbre_escolar_tkinter_notebook.py

import os                         # Para trabajar con rutas de archivos y comprobar si existen
import json                       # Para cargar y guardar la configuración en formato JSON
import datetime                   # Para obtener la hora actual y formatearla
import pygame                     # Para reproducir fragmentos de audio MP3/WAV
import tkinter as tk              # Interfaz gráfica básica con Tkinter
from tkinter import ttk,         # Widgets avanzados: Notebook, Scrollbar, Spinbox…
                   filedialog,    # Para abrir un diálogo de selección de archivos
                   messagebox     # Para mostrar cuadros de diálogo (info, error…)

CONFIG_FILE = "config_customizable.json"  # Nombre del fichero de configuración

class TimbreEscolarApp(tk.Tk):
    def __init__(self):
        super().__init__()                       # Inicializa la ventana principal
        self.title("Configuración Timbre Escolar")  # Título de la ventana
        self.geometry("1000x700")                 # Tamaño inicial de la ventana
        self.configure(bg="#87CEFA")              # Color de fondo azul pastel

        # Carga configuración si existe, o inicializa valores por defecto:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)        # Lee y parsea JSON
        else:
            # Estructura por defecto para mañana y tarde
            self.config = {
                "mañana": {
                    "hora1":   {"nombre": "Inicio clases", "hora": "08:00", "cancion": "", "inicio": 0, "duracion": 10},
                    "hora2":   {"nombre": "Hora 2",       "hora": "09:00", "cancion": "", "inicio": 0, "duracion": 10},
                    "hora3":   {"nombre": "Hora 3",       "hora": "10:00", "cancion": "", "inicio": 0, "duracion": 10},
                    "recreo":  {"nombre": "Recreo",       "hora_inicio": "11:00", "hora_fin": "11:30",
                                "cancion": "", "inicio": 0, "duracion": 10},
                    "hora4":   {"nombre": "Hora 4",       "hora": "11:30", "cancion": "", "inicio": 0, "duracion": 10},
                    "hora5":   {"nombre": "Hora 5",       "hora": "12:30", "cancion": "", "inicio": 0, "duracion": 10},
                    "fin_clase": {"nombre": "Fin de Clase", "hora": "13:30", "cancion": "", "inicio": 0, "duracion": 10}
                },
                "tarde": {
                    "hora1":   {"nombre": "Inicio clases", "hora": "15:00", "cancion": "", "inicio": 0, "duracion": 10},
                    "hora2":   {"nombre": "Hora 2",        "hora": "16:00", "cancion": "", "inicio": 0, "duracion": 10},
                    "hora3":   {"nombre": "Hora 3",        "hora": "17:00", "cancion": "", "inicio": 0, "duracion": 10},
                    "recreo":  {"nombre": "Recreo",        "hora_inicio": "18:00", "hora_fin": "18:30",
                                "cancion": "", "inicio": 0, "duracion": 10},
                    "hora4":   {"nombre": "Hora 4",        "hora": "18:30", "cancion": "", "inicio": 0, "duracion": 10},
                    "hora5":   {"nombre": "Hora 5",        "hora": "19:30", "cancion": "", "inicio": 0, "duracion": 10},
                    "fin_clase": {"nombre": "Fin de Clase", "hora": "20:30", "cancion": "", "inicio": 0, "duracion": 10}
                }
            }

        self.widgets = {"mañana": {}, "tarde": {}}  # Guardará los StringVar/IntVar de cada campo
        self.estado_activo = False                   # Indica si el temporizador está activo
        self.ultimo_evento = None                    # Para que cada timbre suene una sola vez

        self.build_ui()                              # Construye la interfaz
        pygame.mixer.init(frequency=44100, size=-16,
                          channels=2, buffer=512)  # Inicializa el mezclador de pygame

    def build_ui(self):
        # Crea un Notebook (pestañas) para mañana y tarde
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        for periodo in ("mañana", "tarde"):
            frame = ttk.Frame(notebook)             # Cada pestaña es un frame
            notebook.add(frame, text="Mañana" if periodo=="mañana" else "Tarde")

            # Canvas con Scrollbar para desplazamiento si sobra contenido
            canvas = tk.Canvas(frame, bg="#87CEFA", highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            inner = ttk.Frame(canvas)
            # Ajusta la zona de scroll al cambiar el contenido
            inner.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0,0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            self.build_group(inner, periodo)        # Añade los campos dentro del frame interno

        # Pie de página con botones y estado
        footer = ttk.Frame(self)
        footer.pack(fill="x", side="bottom", pady=10)
        # Botón Guardar
        ttk.Button(footer, text="Guardar Configuración", command=self.actualizar_config)\
            .pack(side="left", padx=20)
        # Botón Iniciar/Detener
        ttk.Button(footer, text="Iniciar Programa", command=self.toggle_programa)\
            .pack(side="left", padx=20)
        # Etiqueta que muestra "Estado: Activo/Inactivo"
        self.lbl_estado = ttk.Label(footer, text="Estado: Inactivo",
                                   background="#87CEFA", font=("Segoe UI",10,"bold"))
        self.lbl_estado.pack(side="right", padx=20)

    def build_group(self, parent, periodo):
        # Crea los campos para cada "momento": hora1, hora2, hora3, recreo, etc.
        for idx, key in enumerate(("hora1","hora2","hora3","recreo","hora4","hora5","fin_clase")):
            data = self.config[periodo][key]
            row = idx * 4

            # Campo "Nombre"
            ttk.Label(parent, text="Nombre:", background="#87CEFA")\
                .grid(row=row, column=0, sticky="e", pady=2)
            v_nom = tk.StringVar(value=data["nombre"])
            ttk.Entry(parent, textvariable=v_nom, width=20)\
                .grid(row=row, column=1, padx=5)

            if key != "recreo":
                # Campo "Hora"
                ttk.Label(parent, text="Hora:", background="#87CEFA")\
                    .grid(row=row, column=2, sticky="e")
                v_h = tk.StringVar(value=data["hora"])
                ttk.Entry(parent, textvariable=v_h, width=7)\
                    .grid(row=row, column=3, padx=5)
            else:
                # Recreo: "Hora inicio"
                ttk.Label(parent, text="Hora inicio:", background="#87CEFA")\
                    .grid(row=row, column=2, sticky="e")
                v_hi = tk.StringVar(value=data["hora_inicio"])
                ttk.Entry(parent, textvariable=v_hi, width=7)\
                    .grid(row=row, column=3, padx=5)
                # Recreo: "Hora fin"
                ttk.Label(parent, text="Hora fin:", background="#87CEFA")\
                    .grid(row=row, column=4, sticky="e")
                v_hf = tk.StringVar(value=data["hora_fin"])
                ttk.Entry(parent, textvariable=v_hf, width=7)\
                    .grid(row=row, column=5, padx=5)

            # Campo "Canción"
            ttk.Label(parent, text="Canción:", background="#87CEFA")\
                .grid(row=row+1, column=0, sticky="e")
            v_c = tk.StringVar(value=data["cancion"])
            ttk.Entry(parent, textvariable=v_c, width=25)\
                .grid(row=row+1, column=1, columnspan=4, padx=5)
            ttk.Button(parent, text="Elegir",
                       command=lambda p=periodo,k=key: self.seleccionar_archivo(p,k))\
                .grid(row=row+1, column=5)

            # Campos "Inicio (s)" y "Duración (s)"
            ttk.Label(parent, text="Inicio (s):", background="#87CEFA")\
                .grid(row=row+2, column=0, sticky="e")
            v_i = tk.IntVar(value=data["inicio"])
            ttk.Spinbox(parent, from_=0, to=600, textvariable=v_i, width=5)\
                .grid(row=row+2, column=1)

            ttk.Label(parent, text="Duración (s):", background="#87CEFA")\
                .grid(row=row+2, column=2, sticky="e")
            v_d = tk.IntVar(value=data["duracion"])
            ttk.Spinbox(parent, from_=1, to=600, textvariable=v_d, width=5)\
                .grid(row=row+2, column=3)

            # Guardamos las variables para luego leer sus valores
            if key != "recreo":
                self.widgets[periodo][key] = {
                    "nombre": v_nom, "hora": v_h, "cancion": v_c,
                    "inicio": v_i, "duracion": v_d
                }
            else:
                self.widgets[periodo][key] = {
                    "nombre": v_nom, "hora_inicio": v_hi, "hora_fin": v_hf,
                    "cancion": v_c, "inicio": v_i, "duracion": v_d
                }

    def seleccionar_archivo(self, periodo, momento):
        # Abre diálogo de archivos y actualiza el StringVar de "cancion"
        ruta = filedialog.askopenfilename(filetypes=[("Audio","*.mp3 *.wav")])
        if ruta:
            self.widgets[periodo][momento]["cancion"].set(ruta)

    def actualizar_config(self):
        # Recorre todos los widgets y vuelca sus valores en self.config
        for p in ("mañana","tarde"):
            for k,w in self.widgets[p].items():
                self.config[p][k]["nombre"] = w["nombre"].get()
                if k != "recreo":
                    self.config[p][k]["hora"] = w["hora"].get()
                else:
                    self.config[p][k]["hora_inicio"] = w["hora_inicio"].get()
                    self.config[p][k]["hora_fin"]    = w["hora_fin"].get()
                self.config[p][k]["cancion"]  = w["cancion"].get()
                self.config[p][k]["inicio"]   = int(w["inicio"].get())
                self.config[p][k]["duracion"] = int(w["duracion"].get())
        # Guarda el JSON
        with open(CONFIG_FILE,"w") as f:
            json.dump(self.config,f,indent=4)
        messagebox.showinfo("Guardado","Configuración guardada.")

    def reproducir_sonido(self, ruta, ini, dur):
        # Si existe el archivo, lo carga y reproduce desde 'ini', deteniéndolo tras 'dur'
        if os.path.exists(ruta):
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(start=ini)
            self.after(dur*1000, pygame.mixer.music.stop)

    def comprobar_y_reproducir(self):
        ahora = datetime.datetime.now().strftime("%H:%M")  # Hora actual
        # Evita repetir en el mismo minuto
        if ahora == self.ultimo_evento:
            if self.estado_activo:
                self.after(60000, self.comprobar_y_reproducir)
            return
        self.ultimo_evento = ahora

        for p in ("mañana","tarde"):
            s = self.config[p]
            # Hora1 (inicio clases)
            if ahora == s["hora1"]["hora"]:
                self.reproducir_sonido(s["hora1"]["cancion"], s["hora1"]["inicio"], s["hora1"]["duracion"])
                break
            # Recreo inicio
            if ahora == s["recreo"]["hora_inicio"]:
                self.reproducir_sonido(s["recreo"]["cancion"], s["recreo"]["inicio"], s["recreo"]["duracion"])
                break
            # Recreo fin
            if ahora == s["recreo"]["hora_fin"]:
                self.reproducir_sonido(s["recreo"]["cancion"], s["recreo"]["inicio"], s["recreo"]["duracion"])
                break
            # Horas 2,3,4,5
            for c in ("hora2","hora3","hora4","hora5"):
                if ahora == s[c]["hora"]:
                    self.reproducir_sonido(s[c]["cancion"], s[c]["inicio"], s[c]["duracion"])
                    break
            # Fin de clase
            if ahora == s["fin_clase"]["hora"]:
                self.reproducir_sonido(s["fin_clase"]["cancion"], s["fin_clase"]["inicio"], s["fin_clase"]["duracion"])
                break

        # Programa siguiente comprobación en 60s
        if self.estado_activo:
            self.after(60000, self.comprobar_y_reproducir)

    def toggle_programa(self):
        # Activa o detiene el timbre automático y actualiza la etiqueta de estado
        self.estado_activo = not self.estado_activo
        self.lbl_estado.config(text=f"Estado: {'Activo' if self.estado_activo else 'Inactivo'}")
        if self.estado_activo:
            self.comprobar_y_reproducir()


if __name__=="__main__":
    pygame.mixer.init()            # Inicializa mixer antes de usarlo
    app = TimbreEscolarApp()        # Crea la aplicación
    app.mainloop()                  # Arranca el bucle principal de Tkinter
