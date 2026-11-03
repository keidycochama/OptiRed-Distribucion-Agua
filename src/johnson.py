# -*- coding: utf-8 -*-
"""
johnson.py
----------
Modulo 5: Caminos mas cortos entre TODOS los pares - ALGORITMO DE JOHNSON.

Johnson combina Bellman-Ford y Dijkstra para resolver el problema de
caminos minimos entre todos los pares de forma mas eficiente que
Floyd-Warshall en grafos DISPERSOS (pocas aristas), incluso con pesos
negativos, siempre que no existan ciclos negativos.

Pasos del algoritmo:
    1. Agregar un nodo auxiliar q conectado a todos los demas con peso 0.
    2. Ejecutar Bellman-Ford desde q para obtener valores h(v).
    3. Si hay ciclo negativo, detener el algoritmo.
    4. Reponderar cada arista: w'(u,v) = w(u,v) + h(u) - h(v)  (>= 0)
    5. Ejecutar Dijkstra desde cada nodo con los pesos reponderados.
    6. Convertir de vuelta: dist(u,v) = dist'(u,v) - h(u) + h(v)
"""

import heapq
from bellman_ford import bellman_ford
from graph import Grafo

INFINITO = float("inf")


def johnson(grafo):
    """
    Ejecuta el algoritmo de Johnson sobre 'grafo'.

    Retorna un diccionario con:
        nodos -> lista de nodos
        matriz -> dict de dict: matriz[i][j] = distancia minima de i a j
        ciclo_negativo -> True si se detecto un ciclo negativo
    """
    nodos_originales = grafo.obtener_nodos()

    # 1. Construir un grafo auxiliar identico pero DIRIGIDO, agregando
    #    el nodo auxiliar "q" conectado con peso 0 a todos los nodos.
    aux = Grafo(dirigido=True, ponderado=True)
    for origen in grafo.adyacencia:
        aux.agregar_nodo(origen)
        for destino, peso in grafo.adyacencia[origen]:
            aux.agregar_arista(origen, destino, peso)

    NODO_AUX = "__q__"
    aux.agregar_nodo(NODO_AUX)
    for n in nodos_originales:
        aux.agregar_arista(NODO_AUX, n, 0)

    # 2 y 3. Bellman-Ford desde el nodo auxiliar para obtener h(v)
    resultado_bf = bellman_ford(aux, NODO_AUX)
    if resultado_bf["ciclo_negativo"]:
        return {"nodos": nodos_originales, "matriz": None, "ciclo_negativo": True}

    h = resultado_bf["distancias"]

    # 4. Reponderar las aristas del grafo original: w' = w + h(u) - h(v)
    reponderado = Grafo(dirigido=True, ponderado=True)
    for n in nodos_originales:
        reponderado.agregar_nodo(n)
    for origen in nodos_originales:
        for destino, peso in grafo.vecinos(origen):
            nuevo_peso = peso + h[origen] - h[destino]
            reponderado.agregar_arista(origen, destino, nuevo_peso)

    # 5 y 6. Dijkstra desde cada nodo (con pesos reponderados, ya no negativos)
    #        y luego se revierte la transformacion para obtener las
    #        distancias reales.
    matriz = {i: {j: INFINITO for j in nodos_originales} for i in nodos_originales}
    for n in nodos_originales:
        matriz[n][n] = 0

    for origen in nodos_originales:
        distancias_reponderadas = _dijkstra_simple(reponderado, origen)
        for destino in nodos_originales:
            if distancias_reponderadas[destino] != INFINITO:
                dist_real = distancias_reponderadas[destino] - h[origen] + h[destino]
                matriz[origen][destino] = dist_real

    return {"nodos": nodos_originales, "matriz": matriz, "ciclo_negativo": False}


def _dijkstra_simple(grafo, origen):
    """Version minima de Dijkstra que solo retorna el dict de distancias."""
    distancias = {n: INFINITO for n in grafo.obtener_nodos()}
    distancias[origen] = 0
    heap = [(0, origen)]
    visitados = set()

    while heap:
        dist_actual, actual = heapq.heappop(heap)
        if actual in visitados:
            continue
        visitados.add(actual)
        for vecino, peso in grafo.vecinos(actual):
            nueva_dist = dist_actual + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                heapq.heappush(heap, (nueva_dist, vecino))

    return distancias
