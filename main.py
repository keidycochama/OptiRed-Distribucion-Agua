# -*- coding: utf-8 -*-
"""
main.py
-------
OptiRed: Sistema de Analisis y Optimizacion de Redes
Aplicado a una RED DE DISTRIBUCION DE AGUA (reservorios, estaciones de
bombeo, tanques y zonas de consumo).

Este archivo es el PUNTO DE ENTRADA del sistema. Aqui NO se implementan
los algoritmos: unicamente se construye la interfaz grafica (Tkinter,
con un estilo plano y moderno) y se llama a las funciones definidas en
la carpeta src/, donde cada tecnica tiene su propio archivo (graph.py,
bfs_dfs.py, prim.py, kruskal.py, dijkstra.py, bellman_ford.py,
floyd_warshall.py, johnson.py, ford_fulkerson.py, union_find.py). La
visualizacion grafica de la red (diagrama de nodos y aristas) vive en
graph_plot.py.

Ejecucion:
    python main.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Permite importar los modulos ubicados en la carpeta src/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from graph import Grafo
from bfs_dfs import bfs, dfs
from prim import prim
from kruskal import kruskal
from dijkstra import dijkstra, reconstruir_camino as camino_dijkstra
from bellman_ford import bellman_ford, reconstruir_camino as camino_bellman
from floyd_warshall import floyd_warshall
from johnson import johnson
from ford_fulkerson import ford_fulkerson
from graph_plot import PanelGrafo, PALETA


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Colores adicionales para recorridos (no forman parte de graph_plot.PALETA
# porque ese resaltado es propio de la GUI, no del dibujo del grafo en si).
COLOR_RECORRIDO = "#8E5DB0"   # morado suave, usado para BFS/DFS

# ---------------------------------------------------------------------
# Paleta general de la interfaz (tonos serios, no llamativos)
# ---------------------------------------------------------------------
COLOR_FONDO = "#F4F6F9"        # gris muy claro, fondo general
COLOR_HEADER = "#1F3A5C"       # azul marino oscuro, barra superior
COLOR_HEADER_SUB = "#B9C7DA"   # texto secundario sobre el header
COLOR_ACCENTO = "#2E6E9E"      # azul acero, botones principales
COLOR_ACCENTO_HOVER = "#255880"
COLOR_SECUNDARIO = "#5C6B7A"   # gris pizarra, botones secundarios
COLOR_SECUNDARIO_HOVER = "#4A5766"
COLOR_PELIGRO = "#B0483F"      # rojo teja apagado, acciones de eliminar
COLOR_PELIGRO_HOVER = "#8F3A32"
COLOR_TEXTO = "#20344E"
COLOR_BORDE = "#D3DAE3"
COLOR_TARJETA = "#FFFFFF"


class OptiRedApp:
    """Clase principal de la aplicacion: arma la ventana y todas las pestanas."""

    def __init__(self, root):
        self.root = root
        self.root.title("OptiRed - Red de Distribucion de Agua")
        self.root.geometry("1280x760")
        self.root.minsize(1040, 620)
        self.root.configure(bg=COLOR_FONDO)

        # El grafo actual del sistema (se comparte entre todas las pestanas).
        self.grafo = Grafo(dirigido=False, ponderado=True)

        self._construir_estilo()
        self._construir_layout()

    # ------------------------------------------------------------------
    # Estilo visual: tema plano y moderno basado en ttk "clam"
    # ------------------------------------------------------------------
    def _construir_estilo(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(".", background=COLOR_FONDO, foreground=COLOR_TEXTO,
                          font=("Segoe UI", 9))
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#5C6B7A")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 13, "bold"), foreground=COLOR_TEXTO)

        # --- Encabezado superior ---
        estilo.configure("Header.TFrame", background=COLOR_HEADER)
        estilo.configure("HeaderTitulo.TLabel", background=COLOR_HEADER, foreground="white",
                          font=("Segoe UI", 14, "bold"))
        estilo.configure("HeaderSub.TLabel", background=COLOR_HEADER, foreground=COLOR_HEADER_SUB,
                          font=("Segoe UI", 9))

        # --- Barra de estado inferior ---
        estilo.configure("Status.TFrame", background="#E7ECF2")
        estilo.configure("Status.TLabel", background="#E7ECF2", foreground="#41546B",
                          font=("Segoe UI", 9))

        # --- Pestanas (Notebook) ---
        estilo.configure("TNotebook", background=COLOR_FONDO, borderwidth=0, tabmargins=(4, 6, 4, 0))
        estilo.configure("TNotebook.Tab", background="#E4E9F0", foreground=COLOR_TEXTO,
                          padding=(14, 8), font=("Segoe UI", 9, "bold"), borderwidth=0)
        estilo.map("TNotebook.Tab",
                   background=[("selected", COLOR_ACCENTO)],
                   foreground=[("selected", "white")])

        # --- Cuadros con borde (LabelFrame) ---
        estilo.configure("TLabelframe", background=COLOR_FONDO, bordercolor=COLOR_BORDE,
                          relief="solid", borderwidth=1)
        estilo.configure("TLabelframe.Label", background=COLOR_FONDO, foreground=COLOR_ACCENTO,
                          font=("Segoe UI", 9, "bold"))

        # --- Botones (con variantes primario / secundario / peligro) ---
        estilo.configure("TButton", background=COLOR_ACCENTO, foreground="white",
                          padding=(10, 6), borderwidth=0, font=("Segoe UI", 9, "bold"))
        estilo.map("TButton",
                   background=[("active", COLOR_ACCENTO_HOVER), ("disabled", "#AEB8C4")])

        estilo.configure("Secundario.TButton", background=COLOR_SECUNDARIO, foreground="white",
                          padding=(10, 6), borderwidth=0, font=("Segoe UI", 9))
        estilo.map("Secundario.TButton", background=[("active", COLOR_SECUNDARIO_HOVER)])

        estilo.configure("Peligro.TButton", background=COLOR_PELIGRO, foreground="white",
                          padding=(10, 6), borderwidth=0, font=("Segoe UI", 9))
        estilo.map("Peligro.TButton", background=[("active", COLOR_PELIGRO_HOVER)])

        # --- Checkbuttons y campos de texto ---
        estilo.configure("TCheckbutton", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TEntry", fieldbackground="white", padding=5, bordercolor=COLOR_BORDE)
        estilo.configure("TPanedwindow", background=COLOR_FONDO)

    def _construir_layout(self):
        # --- Encabezado ---
        encabezado = ttk.Frame(self.root, style="Header.TFrame", padding=(18, 14))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="OptiRed  -  Analisis y Optimizacion de la Red de Agua",
                   style="HeaderTitulo.TLabel").pack(anchor="w")
        ttk.Label(encabezado,
                   text="Reservorios, estaciones de bombeo, tanques y zonas de consumo, modelados como un grafo.",
                   style="HeaderSub.TLabel").pack(anchor="w", pady=(2, 0))

        # --- Cuerpo: panel izquierdo (pestanas) + panel derecho (diagrama de la red) ---
        cuerpo = ttk.Panedwindow(self.root, orient="horizontal")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=10)

        panel_izquierdo = ttk.Frame(cuerpo)
        panel_derecho = ttk.Frame(cuerpo, padding=(8, 0, 0, 0))
        cuerpo.add(panel_izquierdo, weight=3)
        cuerpo.add(panel_derecho, weight=2)

        # --- Panel derecho: diagrama grafico de la red ---
        # Se crea ANTES que las pestanas, porque la pestana 1 ya intenta
        # dibujar el grafo (vacio) al construirse.
        marco_grafico = ttk.LabelFrame(panel_derecho, text="Visualizacion de la red", padding=8)
        marco_grafico.pack(fill="both", expand=True)
        self.panel_grafo = PanelGrafo(marco_grafico)

        self.notebook = ttk.Notebook(panel_izquierdo)
        self.notebook.pack(fill="both", expand=True)

        self._tab_grafo()
        self._tab_bfs_dfs()
        self._tab_mst()
        self._tab_rutas()
        self._tab_todos_pares()
        self._tab_flujo()

        # --- Barra de estado ---
        self.estado_var = tk.StringVar(value="Grafo vacio. Cargue una red desde la pestana 'Gestion del grafo'.")
        barra = ttk.Frame(self.root, style="Status.TFrame", padding=(14, 6))
        barra.pack(fill="x")
        ttk.Label(barra, textvariable=self.estado_var, style="Status.TLabel").pack(anchor="w")

        self._actualizar_grafico(titulo="Red de distribucion de agua")

    def _fijar_estado(self, texto):
        self.estado_var.set(texto)

    def _actualizar_grafico(self, **kwargs):
        """Atajo para redibujar el panel grafico de la derecha con el grafo actual."""
        self.panel_grafo.dibujar(self.grafo, **kwargs)

    # ==================================================================
    # PESTANA 1: Gestion del grafo (Modulo 1)
    # ==================================================================
    def _tab_grafo(self):
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text="1. Gestion del grafo")

        # --- Configuracion del tipo de grafo ---
        config = ttk.LabelFrame(frame, text="Configuracion de la red", padding=10)
        config.pack(fill="x", pady=(0, 10))

        self.var_dirigido = tk.BooleanVar(value=False)
        self.var_ponderado = tk.BooleanVar(value=True)
        ttk.Checkbutton(config, text="Grafo dirigido (tuberias de un solo sentido)",
                         variable=self.var_dirigido).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Checkbutton(config, text="Grafo ponderado (con distancia/costo/capacidad)",
                         variable=self.var_ponderado).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(config, text="Crear grafo nuevo", command=self._crear_grafo_nuevo).grid(
            row=0, column=2, padx=10)

        # --- Cargar / guardar archivo ---
        archivo = ttk.LabelFrame(frame, text="Cargar o guardar red desde archivo (.csv)", padding=10)
        archivo.pack(fill="x", pady=(0, 10))
        ttk.Button(archivo, text="Cargar CSV...", command=self._cargar_csv).pack(side="left", padx=5)
        ttk.Button(archivo, text="Guardar CSV...", style="Secundario.TButton",
                   command=self._guardar_csv).pack(side="left", padx=5)
       

        # --- Edicion manual ---
        edicion = ttk.LabelFrame(frame, text="Edicion manual de nodos y aristas", padding=10)
        edicion.pack(fill="x", pady=(0, 10))

        ttk.Label(edicion, text="Nodo:").grid(row=0, column=0, sticky="e")
        self.entry_nodo = ttk.Entry(edicion, width=10)
        self.entry_nodo.grid(row=0, column=1, padx=4)
        ttk.Button(edicion, text="Agregar nodo", command=self._agregar_nodo).grid(row=0, column=2, padx=4)
        ttk.Button(edicion, text="Eliminar nodo", style="Peligro.TButton",
                   command=self._eliminar_nodo).grid(row=0, column=3, padx=4)

        ttk.Label(edicion, text="Origen:").grid(row=1, column=0, sticky="e", pady=(6, 0))
        self.entry_origen = ttk.Entry(edicion, width=10)
        self.entry_origen.grid(row=1, column=1, padx=4, pady=(6, 0))
        ttk.Label(edicion, text="Destino:").grid(row=1, column=2, sticky="e", pady=(6, 0))
        self.entry_destino = ttk.Entry(edicion, width=10)
        self.entry_destino.grid(row=1, column=3, padx=4, pady=(6, 0))
        ttk.Label(edicion, text="Peso:").grid(row=1, column=4, sticky="e", pady=(6, 0))
        self.entry_peso = ttk.Entry(edicion, width=8)
        self.entry_peso.grid(row=1, column=5, padx=4, pady=(6, 0))
        ttk.Button(edicion, text="Agregar arista", command=self._agregar_arista).grid(
            row=1, column=6, padx=4, pady=(6, 0))
        ttk.Button(edicion, text="Eliminar arista", style="Peligro.TButton",
                   command=self._eliminar_arista).grid(row=1, column=7, padx=4, pady=(6, 0))

        # --- Visualizacion en texto ---
        vista = ttk.LabelFrame(frame, text="Nodos y aristas actuales", padding=10)
        vista.pack(fill="both", expand=True)
        self.texto_grafo = scrolledtext.ScrolledText(vista, height=12, font=("Consolas", 10),
                                                       bg="white", fg=COLOR_TEXTO,
                                                       relief="flat", borderwidth=0)
        self.texto_grafo.pack(fill="both", expand=True)

        self._refrescar_vista_grafo()

    def _crear_grafo_nuevo(self):
        self.grafo = Grafo(dirigido=self.var_dirigido.get(), ponderado=self.var_ponderado.get())
        self._refrescar_vista_grafo()
        self._fijar_estado("Se creo un grafo nuevo y vacio.")

    def _cargar_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de red",
            initialdir=DATA_DIR,
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            self.grafo = Grafo(dirigido=self.var_dirigido.get(), ponderado=self.var_ponderado.get())
            self.grafo.cargar_desde_csv(ruta)
            self._refrescar_vista_grafo()
            self._fijar_estado("Grafo cargado correctamente desde: {}".format(os.path.basename(ruta)))
        except Exception as e:
            messagebox.showerror("Error al cargar archivo", str(e))

    def _guardar_csv(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar red como...", defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
        )
        if not ruta:
            return
        try:
            self.grafo.guardar_en_csv(ruta)
            self._fijar_estado("Grafo guardado en: {}".format(ruta))
        except Exception as e:
            messagebox.showerror("Error al guardar archivo", str(e))

    def _agregar_nodo(self):
        nodo = self.entry_nodo.get().strip()
        if not nodo:
            messagebox.showwarning("Falta informacion", "Escriba el nombre del nodo.")
            return
        self.grafo.agregar_nodo(nodo)
        self._refrescar_vista_grafo()
        self._fijar_estado("Nodo '{}' agregado.".format(nodo))

    def _eliminar_nodo(self):
        nodo = self.entry_nodo.get().strip()
        if not nodo:
            messagebox.showwarning("Falta informacion", "Escriba el nombre del nodo a eliminar.")
            return
        self.grafo.eliminar_nodo(nodo)
        self._refrescar_vista_grafo()
        self._fijar_estado("Nodo '{}' eliminado .".format(nodo))

    def _agregar_arista(self):
        origen = self.entry_origen.get().strip()
        destino = self.entry_destino.get().strip()
        peso_txt = self.entry_peso.get().strip()
        if not origen or not destino:
            messagebox.showwarning("Falta informacion", "Escriba el nodo origen y el nodo destino.")
            return
        try:
            peso = float(peso_txt) if peso_txt else 1
        except ValueError:
            messagebox.showerror("Peso invalido", "El peso debe ser un valor numerico.")
            return
        self.grafo.agregar_arista(origen, destino, peso)
        self._refrescar_vista_grafo()
        self._fijar_estado("Arista {} -> {} agregada.".format(origen, destino))

    def _eliminar_arista(self):
        origen = self.entry_origen.get().strip()
        destino = self.entry_destino.get().strip()
        if not origen or not destino:
            messagebox.showwarning("Falta informacion", "Escriba el nodo origen y el nodo destino.")
            return
        self.grafo.eliminar_arista(origen, destino)
        self._refrescar_vista_grafo()
        self._fijar_estado("Arista {} -> {} eliminada (si existia).".format(origen, destino))

    def _refrescar_vista_grafo(self):
        self.texto_grafo.delete("1.0", tk.END)
        tipo = "Dirigido" if self.grafo.dirigido else "No dirigido"
        peso = "Ponderado" if self.grafo.ponderado else "No ponderado"
        self.texto_grafo.insert(tk.END, "Tipo de grafo: {} y {}\n".format(tipo, peso))
        self.texto_grafo.insert(tk.END, "Es conexo: {}\n\n".format(self.grafo.es_conexo()))

        nodos = self.grafo.obtener_nodos()
        self.texto_grafo.insert(tk.END, "NODOS ({}):\n  {}\n\n".format(len(nodos), ", ".join(nodos) if nodos else "(vacio)"))

        aristas = self.grafo.obtener_aristas()
        self.texto_grafo.insert(tk.END, "ARISTAS ({}):\n".format(len(aristas)))
        if not aristas:
            self.texto_grafo.insert(tk.END, "  (sin aristas)\n")
        for origen, destino, w in aristas:
            self.texto_grafo.insert(tk.END, "  {} -> {} : {}\n".format(origen, destino, w))

        # Cada vez que el grafo cambia, se refresca tambien el diagrama grafico
        self._actualizar_grafico(titulo="Red de distribucion de agua actual")

    # ==================================================================
    # PESTANA 2: BFS y DFS (Modulo 2)
    # ==================================================================
    def _tab_bfs_dfs(self):
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text="2. BFS / DFS")

        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 10))
        ttk.Label(controles, text="Nodo origen:").pack(side="left")
        self.entry_origen_recorrido = ttk.Entry(controles, width=10)
        self.entry_origen_recorrido.pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar BFS", command=lambda: self._ejecutar_recorrido("BFS")).pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar DFS", style="Secundario.TButton",
                   command=lambda: self._ejecutar_recorrido("DFS")).pack(side="left", padx=6)

        self.texto_recorrido = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 10),
                                                          bg="white", fg=COLOR_TEXTO, relief="flat", borderwidth=0)
        self.texto_recorrido.pack(fill="both", expand=True)

    def _ejecutar_recorrido(self, tipo):
        origen = self.entry_origen_recorrido.get().strip()
        if not origen:
            messagebox.showwarning("Falta informacion", "Escriba el nodo origen.")
            return
        try:
            resultado = bfs(self.grafo, origen) if tipo == "BFS" else dfs(self.grafo, origen)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.texto_recorrido.delete("1.0", tk.END)
        self.texto_recorrido.insert(tk.END, "Recorrido {} desde {}:\n\n".format(tipo, origen))
        self.texto_recorrido.insert(tk.END, "Orden de visita:\n  {}\n\n".format(" -> ".join(resultado["orden"])))
        self.texto_recorrido.insert(tk.END, "Arbol de recorrido:\n")
        if resultado["arbol"]:
            for padre, hijo in resultado["arbol"]:
                self.texto_recorrido.insert(tk.END, "  {} -> {}\n".format(padre, hijo))
        else:
            self.texto_recorrido.insert(tk.END, "  (sin aristas de recorrido)\n")
        self.texto_recorrido.insert(tk.END, "\nNodos no alcanzables:\n  {}\n".format(
            ", ".join(resultado["no_alcanzables"]) if resultado["no_alcanzables"] else "(ninguno)"))
        self._fijar_estado("{} ejecutado desde '{}'.".format(tipo, origen))

        self._actualizar_grafico(
            titulo="Recorrido {} desde {}".format(tipo, origen),
            aristas_resaltadas=resultado["arbol"],
            color_resaltado=COLOR_RECORRIDO,
            nodos_resaltados=[origen],
        )

    # ==================================================================
    # PESTANA 3: Arbol de expansion minima (Modulo 3)
    # ==================================================================
    def _tab_mst(self):
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text="3. MST (Prim / Kruskal)")

        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 10))
        ttk.Label(controles, text="Nodo inicial para Prim (opcional):").pack(side="left")
        self.entry_inicio_prim = ttk.Entry(controles, width=10)
        self.entry_inicio_prim.pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar Prim", command=self._ejecutar_prim).pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar Kruskal", style="Secundario.TButton",
                   command=self._ejecutar_kruskal).pack(side="left", padx=6)

        self.texto_mst = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 10),
                                                    bg="white", fg=COLOR_TEXTO, relief="flat", borderwidth=0)
        self.texto_mst.pack(fill="both", expand=True)

    def _mostrar_resultado_mst(self, nombre, resultado):
        self.texto_mst.delete("1.0", tk.END)
        self.texto_mst.insert(tk.END, "Arbol de expansion minima usando {}:\n\n".format(nombre))
        self.texto_mst.insert(tk.END, "Aristas seleccionadas:\n")
        for origen, destino, peso in resultado["aristas"]:
            self.texto_mst.insert(tk.END, "  {} - {} : {}\n".format(origen, destino, peso))
        self.texto_mst.insert(tk.END, "\nCosto total: {}\n".format(resultado["costo_total"]))

        self._actualizar_grafico(
            titulo="Arbol de expansion minima ({})".format(nombre),
            aristas_resaltadas=[(o, d) for o, d, _ in resultado["aristas"]],
            color_resaltado=PALETA["resaltado_mst"],
        )

    def _ejecutar_prim(self):
        try:
            inicio = self.entry_inicio_prim.get().strip() or None
            resultado = prim(self.grafo, inicio)
            self._mostrar_resultado_mst("Prim", resultado)
            self._fijar_estado("Prim ejecutado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _ejecutar_kruskal(self):
        try:
            resultado = kruskal(self.grafo)
            self._mostrar_resultado_mst("Kruskal", resultado)
            self._fijar_estado("Kruskal ejecutado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==================================================================
    # PESTANA 4: Rutas mas cortas desde un origen (Modulo 4)
    # ==================================================================
    def _tab_rutas(self):
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text="4. Rutas mas cortas")

        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 10))
        ttk.Label(controles, text="Origen:").pack(side="left")
        self.entry_origen_ruta = ttk.Entry(controles, width=10)
        self.entry_origen_ruta.pack(side="left", padx=6)
        ttk.Label(controles, text="Destino (opcional):").pack(side="left")
        self.entry_destino_ruta = ttk.Entry(controles, width=10)
        self.entry_destino_ruta.pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar Dijkstra", command=self._ejecutar_dijkstra).pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar Bellman-Ford", style="Secundario.TButton",
                   command=self._ejecutar_bellman).pack(side="left", padx=6)

        self.texto_rutas = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 10),
                                                      bg="white", fg=COLOR_TEXTO, relief="flat", borderwidth=0)
        self.texto_rutas.pack(fill="both", expand=True)

    def _ejecutar_dijkstra(self):
        origen = self.entry_origen_ruta.get().strip()
        destino = self.entry_destino_ruta.get().strip()
        if not origen:
            messagebox.showwarning("Falta informacion", "Escriba el nodo origen.")
            return
        try:
            resultado = dijkstra(self.grafo, origen)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.texto_rutas.delete("1.0", tk.END)
        self.texto_rutas.insert(tk.END, "Dijkstra desde {}:\n\n".format(origen))
        self.texto_rutas.insert(tk.END, "Distancias minimas:\n")
        for nodo, dist in resultado["distancias"].items():
            self.texto_rutas.insert(tk.END, "  {} : {}\n".format(nodo, "INF" if dist == float("inf") else dist))
        self.texto_rutas.insert(tk.END, "\nNodos no alcanzables:\n  {}\n".format(
            ", ".join(resultado["no_alcanzables"]) if resultado["no_alcanzables"] else "(ninguno)"))

        camino = []
        if destino:
            camino = camino_dijkstra(resultado["previos"], origen, destino)
            self.texto_rutas.insert(tk.END, "\nCamino de {} a {}:\n  {}\n".format(
                origen, destino, " -> ".join(camino) if camino else "No existe camino"))
        self._fijar_estado("Dijkstra ejecutado desde '{}'.".format(origen))

        self._actualizar_grafico(
            titulo="Dijkstra desde {}".format(origen),
            nodos_resaltados=[n for n in [origen, destino] if n],
            camino=camino if camino else None,
        )

    def _ejecutar_bellman(self):
        origen = self.entry_origen_ruta.get().strip()
        destino = self.entry_destino_ruta.get().strip()
        if not origen:
            messagebox.showwarning("Falta informacion", "Escriba el nodo origen.")
            return
        try:
            resultado = bellman_ford(self.grafo, origen)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.texto_rutas.delete("1.0", tk.END)
        self.texto_rutas.insert(tk.END, "Bellman-Ford desde {}:\n\n".format(origen))

        if resultado["ciclo_negativo"]:
            self.texto_rutas.insert(tk.END, "Se detecto un ciclo negativo alcanzable desde el origen.\n")
            self.texto_rutas.insert(tk.END, "No es posible calcular rutas minimas bien definidas.\n")
            self._fijar_estado("Bellman-Ford: se detecto un ciclo negativo.")
            self._actualizar_grafico(titulo="Bellman-Ford: ciclo negativo detectado",
                                       nodos_resaltados=[origen])
            return

        self.texto_rutas.insert(tk.END, "Distancias minimas:\n")
        for nodo, dist in resultado["distancias"].items():
            self.texto_rutas.insert(tk.END, "  {} : {}\n".format(nodo, "INF" if dist == float("inf") else dist))
        self.texto_rutas.insert(tk.END, "\nNo se detectaron ciclos negativos.\n")
        self.texto_rutas.insert(tk.END, "\nNodos no alcanzables:\n  {}\n".format(
            ", ".join(resultado["no_alcanzables"]) if resultado["no_alcanzables"] else "(ninguno)"))

        camino = []
        if destino:
            camino = camino_bellman(resultado["previos"], origen, destino)
            self.texto_rutas.insert(tk.END, "\nCamino de {} a {}:\n  {}\n".format(
                origen, destino, " -> ".join(camino) if camino else "No existe camino"))
        self._fijar_estado("Bellman-Ford ejecutado desde '{}'.".format(origen))

        self._actualizar_grafico(
            titulo="Bellman-Ford desde {}".format(origen),
            nodos_resaltados=[n for n in [origen, destino] if n],
            camino=camino if camino else None,
        )

    # ==================================================================
    # PESTANA 5: Caminos entre todos los pares (Modulo 5)
    # ==================================================================
    def _tab_todos_pares(self):
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text="5. Todos los pares")

        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 10))
        ttk.Button(controles, text="Ejecutar Floyd-Warshall", command=self._ejecutar_floyd).pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar Johnson", style="Secundario.TButton",
                   command=self._ejecutar_johnson).pack(side="left", padx=6)

        self.texto_pares = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 10),
                                                      bg="white", fg=COLOR_TEXTO, relief="flat", borderwidth=0)
        self.texto_pares.pack(fill="both", expand=True)

    def _mostrar_matriz(self, nombre, nodos, matriz):
        self.texto_pares.delete("1.0", tk.END)
        self.texto_pares.insert(tk.END, "Matriz de distancias minimas usando {}:\n\n".format(nombre))

        ancho = max(6, max((len(n) for n in nodos), default=1) + 2)
        encabezado = " " * ancho + "".join(n.rjust(ancho) for n in nodos)
        self.texto_pares.insert(tk.END, encabezado + "\n")
        for i in nodos:
            fila = i.rjust(ancho)
            for j in nodos:
                valor = matriz[i][j]
                texto_valor = "INF" if valor == float("inf") else str(valor)
                fila += texto_valor.rjust(ancho)
            self.texto_pares.insert(tk.END, fila + "\n")

        self._actualizar_grafico(titulo="Caminos entre todos los pares ({})".format(nombre))

    def _ejecutar_floyd(self):
        try:
            resultado = floyd_warshall(self.grafo)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        if resultado["ciclo_negativo"]:
            self.texto_pares.delete("1.0", tk.END)
            self.texto_pares.insert(tk.END, "Se detecto un ciclo negativo en el grafo.\nNo es posible calcular una matriz de distancias valida.\n")
            self._fijar_estado("Floyd-Warshall: se detecto un ciclo negativo.")
            return
        self._mostrar_matriz("Floyd-Warshall", resultado["nodos"], resultado["matriz"])
        self._fijar_estado("Floyd-Warshall ejecutado correctamente.")

    def _ejecutar_johnson(self):
        try:
            resultado = johnson(self.grafo)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        if resultado["ciclo_negativo"]:
            self.texto_pares.delete("1.0", tk.END)
            self.texto_pares.insert(tk.END, "Se detecto un ciclo negativo en el grafo.\nJohnson no puede continuar (Bellman-Ford lo detecto en el paso de reponderacion).\n")
            self._fijar_estado("Johnson: se detecto un ciclo negativo.")
            return
        self._mostrar_matriz("Johnson", resultado["nodos"], resultado["matriz"])
        self._fijar_estado("Johnson ejecutado correctamente.")

    # ==================================================================
    # PESTANA 6: Flujo maximo (Modulo 6)
    # ==================================================================
    def _tab_flujo(self):
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text="6. Flujo maximo")

        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 10))
        ttk.Label(controles, text="Fuente (reservorio):").pack(side="left")
        self.entry_fuente = ttk.Entry(controles, width=10)
        self.entry_fuente.pack(side="left", padx=6)
        ttk.Label(controles, text="Sumidero (zona destino):").pack(side="left")
        self.entry_sumidero = ttk.Entry(controles, width=10)
        self.entry_sumidero.pack(side="left", padx=6)
        ttk.Button(controles, text="Ejecutar Ford-Fulkerson", command=self._ejecutar_flujo).pack(side="left", padx=6)

        self.texto_flujo = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 10),
                                                      bg="white", fg=COLOR_TEXTO, relief="flat", borderwidth=0)
        self.texto_flujo.pack(fill="both", expand=True)

    def _ejecutar_flujo(self):
        fuente = self.entry_fuente.get().strip()
        sumidero = self.entry_sumidero.get().strip()
        if not fuente or not sumidero:
            messagebox.showwarning("Falta informacion", "Escriba el nodo fuente y el nodo sumidero.")
            return
        try:
            resultado = ford_fulkerson(self.grafo, fuente, sumidero)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.texto_flujo.delete("1.0", tk.END)
        self.texto_flujo.insert(tk.END, "Fuente: {}\n".format(fuente))
        self.texto_flujo.insert(tk.END, "Sumidero: {}\n".format(sumidero))
        self.texto_flujo.insert(tk.END, "Flujo maximo encontrado: {}\n\n".format(resultado["flujo_maximo"]))
        self.texto_flujo.insert(tk.END, "Flujo por arista (enviado/capacidad):\n")

        aristas_con_flujo = []
        etiquetas = {}
        for origen, destino, enviado, capacidad in resultado["flujo_por_arista"]:
            self.texto_flujo.insert(tk.END, "  {} -> {} : {}/{}\n".format(origen, destino, enviado, capacidad))
            etiquetas[(origen, destino)] = "{}/{}".format(enviado, capacidad)
            if enviado > 0:
                aristas_con_flujo.append((origen, destino))

        self._fijar_estado("Ford-Fulkerson ejecutado: flujo maximo = {}.".format(resultado["flujo_maximo"]))

        self._actualizar_grafico(
            titulo="Flujo maximo: {} (fuente {} -> sumidero {})".format(
                resultado["flujo_maximo"], fuente, sumidero),
            aristas_resaltadas=aristas_con_flujo,
            color_resaltado=PALETA["resaltado_flujo"],
            nodos_resaltados=[fuente, sumidero],
            etiquetas_aristas=etiquetas,
        )


def main():
    root = tk.Tk()
    OptiRedApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
