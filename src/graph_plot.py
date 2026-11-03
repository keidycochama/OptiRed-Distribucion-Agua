# -*- coding: utf-8 -*-
"""
graph_plot.py
-------------
Visualizacion grafica de la red (nodos y tuberias) dentro de la interfaz.

Este archivo NO implementa un algoritmo del curso; es un componente de
apoyo visual para la GUI. Dibuja el grafo como un diagrama de nodos
(circulos) unidos por aristas (lineas), calculando la posicion de cada
nodo mediante un layout de fuerzas tipo "resorte" (una version simple
del algoritmo de Fruchterman-Reingold), para que la red no dependa de
coordenadas fijas y se acomode sola sin importar el archivo cargado.

Se usa matplotlib embebido en Tkinter (FigureCanvasTkAgg). Si matplotlib
no esta instalado, la clase PanelGrafo se degrada de forma segura y
muestra un mensaje en vez de romper toda la aplicacion.
"""

import math
import random

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

import tkinter as tk
from tkinter import ttk


# Paleta de colores "profesional" (tonos apagados, no muy llamativos)
PALETA = {
    "fondo": "#FFFFFF",
    "nodo": "#3A6EA5",          # azul acero
    "nodo_borde": "#20344E",
    "nodo_resaltado": "#D9822B",  # naranja tostado (nodo de interes: origen/fuente/etc.)
    "arista": "#B9C0CB",        # gris azulado suave
    "arista_texto": "#5B6472",
    "resaltado_mst": "#3B8256",    # verde bosque (arboles de expansion minima)
    "resaltado_camino": "#C0483C",  # rojo teja (rutas mas cortas)
    "resaltado_flujo": "#3A6EA5",   # azul acero (aristas con flujo enviado)
    "titulo": "#1F2937",
}


def layout_resortes(nodos, aristas, iteraciones=150, ancho=10.0, alto=10.0, semilla=7):
    """
    Calcula una posicion (x, y) para cada nodo usando un algoritmo simple
    de fuerzas dirigidas (spring layout): los nodos se repelen entre si,
    pero las aristas los "jalan" para acercarlos. Tras varias iteraciones,
    el dibujo se acomoda solo, similar a como lo hacen librerias como
    networkx, sin necesitar esa dependencia extra.
    """
    random.seed(semilla)
    if not nodos:
        return {}

    pos = {n: [random.uniform(1, ancho - 1), random.uniform(1, alto - 1)] for n in nodos}
    area = ancho * alto
    k = math.sqrt(area / len(nodos))  # distancia "ideal" entre nodos

    for it in range(iteraciones):
        disp = {n: [0.0, 0.0] for n in nodos}

        # Fuerza de repulsion entre todos los pares de nodos
        for i, u in enumerate(nodos):
            for v in nodos[i + 1:]:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy) or 0.01
                fuerza = (k * k) / dist
                fx, fy = dx / dist * fuerza, dy / dist * fuerza
                disp[u][0] += fx
                disp[u][1] += fy
                disp[v][0] -= fx
                disp[v][1] -= fy

        # Fuerza de atraccion a lo largo de cada arista
        for u, v in aristas:
            if u not in pos or v not in pos:
                continue
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.hypot(dx, dy) or 0.01
            fuerza = (dist * dist) / k
            fx, fy = dx / dist * fuerza, dy / dist * fuerza
            disp[u][0] -= fx
            disp[u][1] -= fy
            disp[v][0] += fx
            disp[v][1] += fy

        # La "temperatura" baja con el tiempo para que el sistema se estabilice
        temp = (ancho / 10) * (1 - it / iteraciones)
        for n in nodos:
            dx, dy = disp[n]
            dist = math.hypot(dx, dy) or 0.01
            limitado = min(dist, max(temp, 0.01))
            pos[n][0] += dx / dist * limitado
            pos[n][1] += dy / dist * limitado
            pos[n][0] = min(ancho, max(0.0, pos[n][0]))
            pos[n][1] = min(alto, max(0.0, pos[n][1]))

    return pos


class PanelGrafo:
    """
    Envuelve una figura de matplotlib embebida en un Frame de Tkinter, y
    expone un metodo dibujar(...) que las distintas pestanas de main.py
    llaman para mostrar la red, resaltando aristas/nodos segun el
    algoritmo que se acaba de ejecutar (MST, ruta mas corta, flujo, etc.).
    """

    def __init__(self, parent):
        self.disponible = MATPLOTLIB_DISPONIBLE
        self._pos_cache = {}
        self._clave_cache = None

        if not self.disponible:
            ttk.Label(
                parent,
                text="No se pudo cargar matplotlib.\nInstale con:  pip install matplotlib",
                justify="center",
            ).pack(expand=True, fill="both", padx=10, pady=10)
            return

        self.figure = Figure(figsize=(5.2, 5), dpi=100, facecolor=PALETA["fondo"])
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._mostrar_vacio()

    def _mostrar_vacio(self):
        if not self.disponible:
            return
        self.ax.clear()
        self.ax.axis("off")
        self.ax.set_facecolor(PALETA["fondo"])
        self.ax.text(0.5, 0.5, "Cargue una red para\nver el diagrama aqui",
                     ha="center", va="center", fontsize=10, color="#8A93A3")
        self.canvas.draw()

    def dibujar(self, grafo, titulo="Red de distribucion de agua",
                aristas_resaltadas=None, color_resaltado=None,
                nodos_resaltados=None, camino=None,
                etiquetas_aristas=None):
        """
        Dibuja el grafo actual.

        aristas_resaltadas: lista de (origen, destino) a pintar de otro color
                             (por ejemplo, las aristas del MST o del flujo).
        color_resaltado: color a usar para esas aristas resaltadas.
        nodos_resaltados: lista de nodos a pintar distinto (ej. fuente/sumidero,
                           u origen de un recorrido).
        camino: lista ordenada de nodos [n1, n2, n3, ...] a dibujar como una
                ruta con flechas (para Dijkstra/Bellman-Ford).
        etiquetas_aristas: dict {(origen,destino): "texto"} para reemplazar el
                            peso mostrado (por ejemplo "12/16" en flujo maximo).
        """
        if not self.disponible:
            return

        nodos = grafo.obtener_nodos()
        if not nodos:
            self._mostrar_vacio()
            return

        aristas = grafo.obtener_aristas()
        pares = [(o, d) for o, d, _ in aristas]

        clave = tuple(sorted(nodos))
        if clave != self._clave_cache:
            self._pos_cache = layout_resortes(nodos, pares)
            self._clave_cache = clave
        pos = self._pos_cache

        self.ax.clear()
        self.ax.axis("off")
        self.ax.set_facecolor(PALETA["fondo"])
        self.ax.set_title(titulo, fontsize=10.5, color=PALETA["titulo"], fontweight="bold", pad=10)

        resaltadas = set(aristas_resaltadas or [])
        etiquetas_aristas = etiquetas_aristas or {}

        # --- Dibujar aristas (lineas o flechas si el grafo es dirigido) ---
        for origen, destino, peso in aristas:
            if origen not in pos or destino not in pos:
                continue
            x0, y0 = pos[origen]
            x1, y1 = pos[destino]
            es_resaltada = (origen, destino) in resaltadas or (destino, origen) in resaltadas
            color = color_resaltado if (es_resaltada and color_resaltado) else PALETA["arista"]
            grosor = 2.8 if es_resaltada else 1.3
            alpha = 0.95 if es_resaltada else 0.75

            if grafo.dirigido:
                self.ax.annotate(
                    "", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=grosor, alpha=alpha,
                                     shrinkA=14, shrinkB=14),
                    zorder=1,
                )
            else:
                self.ax.plot([x0, x1], [y0, y1], color=color, linewidth=grosor,
                             alpha=alpha, solid_capstyle="round", zorder=1)

            texto = etiquetas_aristas.get((origen, destino), etiquetas_aristas.get((destino, origen)))
            if texto is None:
                texto = str(peso)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            self.ax.text(mx, my, texto, fontsize=7.3, color=PALETA["arista_texto"],
                         ha="center", va="center", zorder=2,
                         bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

        # --- Dibujar un camino especifico con flechas mas gruesas (rutas mas cortas) ---
        if camino:
            for i in range(len(camino) - 1):
                o, d = camino[i], camino[i + 1]
                if o in pos and d in pos:
                    self.ax.annotate(
                        "", xy=pos[d], xytext=pos[o],
                        arrowprops=dict(arrowstyle="-|>", color=PALETA["resaltado_camino"],
                                        lw=3.0, shrinkA=14, shrinkB=14),
                        zorder=3,
                    )

        # --- Dibujar nodos ---
        resaltados_set = set(nodos_resaltados or [])
        for nodo in nodos:
            if nodo not in pos:
                continue
            x, y = pos[nodo]
            color_nodo = PALETA["nodo_resaltado"] if nodo in resaltados_set else PALETA["nodo"]
            self.ax.scatter([x], [y], s=680, color=color_nodo, edgecolor=PALETA["nodo_borde"],
                             linewidth=1.3, zorder=4)
            self.ax.text(x, y, nodo, fontsize=8.3, color="white", ha="center", va="center",
                         fontweight="bold", zorder=5)

        margen = 0.9
        self.ax.set_xlim(-margen, 10 + margen)
        self.ax.set_ylim(-margen, 10 + margen)
        self.figure.tight_layout()
        self.canvas.draw()
