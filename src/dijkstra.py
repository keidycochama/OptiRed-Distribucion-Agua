# -*- coding: utf-8 -*-
"""
dijkstra.py
-----------
Modulo 4: Rutas mas cortas desde un origen - Algoritmo de DIJKSTRA.

Dijkstra calcula la distancia minima desde un nodo origen hacia todos
los demas nodos, usando una cola de prioridad (heapq). SOLO funciona
correctamente si TODOS los pesos son NO NEGATIVOS (por ejemplo,
distancias o costos de tuberias, que nunca son negativos en la
realidad).
"""

import heapq

INFINITO = float("inf")


def _tiene_pesos_negativos(grafo):
    for _, _, peso in grafo.obtener_aristas():
        if peso < 0:
            return True
    return False


def dijkstra(grafo, origen):
    """
    Ejecuta Dijkstra desde 'origen'.

    Retorna un diccionario con:
        distancias -> {nodo: distancia_minima}
        previos    -> {nodo: nodo_anterior_en_el_camino_mas_corto}
        no_alcanzables -> lista de nodos sin camino desde el origen
    Lanza ValueError si el grafo tiene pesos negativos (Dijkstra no es
    valido en ese caso: se debe usar Bellman-Ford).
    """
    if origen not in grafo.adyacencia:
        raise ValueError("El nodo origen '{}' no existe en el grafo".format(origen))

    if _tiene_pesos_negativos(grafo):
        raise ValueError(
            "El grafo contiene pesos negativos. Dijkstra no puede aplicarse "
            "(los resultados serian incorrectos). Use Bellman-Ford."
        )

    nodos = grafo.obtener_nodos()
    distancias = {n: INFINITO for n in nodos}
    previos = {n: None for n in nodos}
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
                previos[vecino] = actual
                heapq.heappush(heap, (nueva_dist, vecino))

    no_alcanzables = [n for n in nodos if distancias[n] == INFINITO]

    return {"distancias": distancias, "previos": previos, "no_alcanzables": no_alcanzables}


def reconstruir_camino(previos, origen, destino):
    """Reconstruye el camino origen->destino a partir del diccionario 'previos'."""
    if destino not in previos:
        return []
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        if actual == origen:
            break
        actual = previos[actual]
    camino.reverse()
    if not camino or camino[0] != origen:
        return []  # no hay camino valido
    return camino
