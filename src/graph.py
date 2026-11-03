# -*- coding: utf-8 -*-
"""
graph.py
--------
Modulo 1: Gestion del grafo.

Este archivo define la clase Grafo, que representa la red de distribucion
de agua (reservorios, estaciones de bombeo y zonas de consumo) mediante
una LISTA DE ADYACENCIA, tal como recomienda el enunciado del proyecto.

La lista de adyacencia se guarda en un diccionario de Python:

    self.adyacencia = {
        "R":  [("E1", 4), ("E2", 2)],
        "E1": [("Z1", 5)],
        ...
    }

Cada clave es un nodo (por ejemplo un reservorio o una zona urbana) y
cada valor es una lista de tuplas (vecino, peso). El "peso" puede
representar distancia, costo o capacidad de tuberia, dependiendo del
modulo que use el grafo.

Todos los demas modulos (BFS/DFS, MST, rutas mas cortas, flujo maximo,
etc.) reciben un objeto Grafo y trabajan sobre su lista de adyacencia.
"""

import csv
import json
import os


class Grafo:
    def __init__(self, dirigido=False, ponderado=True, con_capacidad=False):
        """
        dirigido: True si las aristas tienen sentido unico (ej. tuberias
                  que solo permiten flujo en una direccion).
        ponderado: True si las aristas tienen un valor numerico asociado
                   (distancia, costo, capacidad).
        con_capacidad: True si el grafo se usara para el modulo de flujo
                       maximo (el peso se interpreta como capacidad).
        """
        self.dirigido = dirigido
        self.ponderado = ponderado
        self.con_capacidad = con_capacidad
        # Lista de adyacencia: nodo -> [(vecino, peso), ...]
        self.adyacencia = {}

    # ------------------------------------------------------------------
    # Operaciones basicas sobre nodos y aristas (funcionalidades minimas)
    # ------------------------------------------------------------------
    def agregar_nodo(self, nodo):
        """Agrega un nodo vacio si todavia no existe."""
        if nodo not in self.adyacencia:
            self.adyacencia[nodo] = []

    def agregar_arista(self, origen, destino, peso=1):
        """
        Agrega una arista origen->destino con el peso indicado.
        Si el grafo NO es dirigido, tambien se agrega destino->origen,
        tal como pide el enunciado.
        Evita duplicados: si la arista ya existe, actualiza el peso.
        """
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)

        if not self.ponderado:
            peso = 1
        else:
            peso = float(peso)
            # Si el peso es un numero entero, lo dejamos como entero
            # para que la interfaz se vea mas limpia (4 en vez de 4.0)
            if peso == int(peso):
                peso = int(peso)

        self._set_arista(origen, destino, peso)
        if not self.dirigido:
            self._set_arista(destino, origen, peso)

    def _set_arista(self, origen, destino, peso):
        """Inserta o actualiza (origen, destino, peso) evitando duplicados."""
        vecinos = self.adyacencia[origen]
        for i, (v, _) in enumerate(vecinos):
            if v == destino:
                vecinos[i] = (destino, peso)
                return
        vecinos.append((destino, peso))

    def eliminar_nodo(self, nodo):
        """Elimina un nodo y todas las aristas que lo mencionan."""
        if nodo in self.adyacencia:
            del self.adyacencia[nodo]
        for n in self.adyacencia:
            self.adyacencia[n] = [(v, p) for (v, p) in self.adyacencia[n] if v != nodo]

    def eliminar_arista(self, origen, destino):
        """Elimina la arista origen->destino (y destino->origen si no es dirigido)."""
        if origen in self.adyacencia:
            self.adyacencia[origen] = [(v, p) for (v, p) in self.adyacencia[origen] if v != destino]
        if not self.dirigido and destino in self.adyacencia:
            self.adyacencia[destino] = [(v, p) for (v, p) in self.adyacencia[destino] if v != origen]

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def obtener_nodos(self):
        return list(self.adyacencia.keys())

    def obtener_aristas(self):
        """
        Devuelve la lista de aristas como tuplas (origen, destino, peso).
        Si el grafo no es dirigido, cada arista se muestra una sola vez
        (evitando repetir A-B y B-A).
        """
        aristas = []
        vistas = set()
        for origen in self.adyacencia:
            for destino, peso in self.adyacencia[origen]:
                if self.dirigido:
                    aristas.append((origen, destino, peso))
                else:
                    clave = tuple(sorted([origen, destino]))
                    if clave not in vistas:
                        vistas.add(clave)
                        aristas.append((origen, destino, peso))
        return aristas

    def vecinos(self, nodo):
        return self.adyacencia.get(nodo, [])

    def es_conexo(self):
        """
        Verifica si el grafo (tratado como no dirigido) es conexo.
        Se usa un BFS simple desde un nodo cualquiera y se comprueba si
        se alcanzan todos los nodos. Necesario para validar el modulo
        de arbol de expansion minima (MST).
        """
        nodos = self.obtener_nodos()
        if not nodos:
            return True

        inicio = nodos[0]
        visitados = {inicio}
        cola = [inicio]
        while cola:
            actual = cola.pop(0)
            for vecino, _ in self.adyacencia.get(actual, []):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)
                # como puede ser dirigido, tambien revisamos en sentido inverso
            if self.dirigido:
                for otro in self.adyacencia:
                    for vecino, _ in self.adyacencia[otro]:
                        if vecino == actual and otro not in visitados:
                            visitados.add(otro)
                            cola.append(otro)
        return len(visitados) == len(nodos)

    # ------------------------------------------------------------------
    # Carga y guardado de archivos (.csv, .txt igual formato, .json)
    # ------------------------------------------------------------------
    def cargar_desde_csv(self, ruta):
        """
        Carga el grafo desde un archivo .csv con formato:
            origen,destino,peso
        Cada linea representa una arista. Si una linea trae menos de 3
        columnas o el peso no es numerico, se informa el error.
        """
        if not os.path.exists(ruta):
            raise FileNotFoundError("No se encontro el archivo: {}".format(ruta))

        with open(ruta, "r", encoding="utf-8") as f:
            lector = csv.reader(f)
            for num_linea, fila in enumerate(lector, start=1):
                if not fila or fila[0].strip().startswith("#"):
                    continue  # permite comentarios y lineas vacias
                fila = [c.strip() for c in fila]
                if len(fila) < 2:
                    raise ValueError(
                        "Formato incorrecto en la linea {}: se esperaba 'origen,destino,peso'".format(num_linea)
                    )
                origen, destino = fila[0], fila[1]
                peso = fila[2] if len(fila) >= 3 and fila[2] != "" else 1
                try:
                    peso = float(peso)
                except ValueError:
                    raise ValueError(
                        "El peso '{}' no es numerico (linea {})".format(peso, num_linea)
                    )
                self.agregar_arista(origen, destino, peso)

    def guardar_en_csv(self, ruta):
        """Guarda el grafo actual en un archivo .csv (origen,destino,peso)."""
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            for origen, destino, peso in self.obtener_aristas():
                escritor.writerow([origen, destino, peso])

    def cargar_desde_json(self, ruta):
        """Carga el grafo desde un archivo .json con la forma {nodo: [[vecino, peso], ...]}."""
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        for nodo, vecinos in data.items():
            self.agregar_nodo(nodo)
            for vecino, peso in vecinos:
                self.agregar_arista(nodo, vecino, peso)

    def guardar_en_json(self, ruta):
        data = {n: [[v, p] for v, p in vs] for n, vs in self.adyacencia.items()}
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    def __str__(self):
        tipo = "dirigido" if self.dirigido else "no dirigido"
        peso = "ponderado" if self.ponderado else "no ponderado"
        return "Grafo {} y {} | Nodos: {} | Aristas: {}".format(
            tipo, peso, len(self.obtener_nodos()), len(self.obtener_aristas())
        )
