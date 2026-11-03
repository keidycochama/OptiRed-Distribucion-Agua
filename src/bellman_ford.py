# -*- coding: utf-8 -*-
"""
bellman_ford.py
---------------
Modulo 4: Rutas mas cortas desde un origen - Algoritmo de BELLMAN-FORD.

A diferencia de Dijkstra, Bellman-Ford SI puede trabajar con pesos
negativos (por ejemplo, para modelar descuentos o compensaciones de
presion en la red de agua). Ademas, es capaz de DETECTAR ciclos
negativos alcanzables desde el origen; si existen, no es posible
definir distancias minimas bien definidas (el costo podria disminuir
indefinidamente dando vueltas en el ciclo).

Complejidad: O(N * A), donde N = numero de nodos y A = numero de aristas.
"""

INFINITO = float("inf")


def bellman_ford(grafo, origen):
    """
    Ejecuta Bellman-Ford desde 'origen'.

    Retorna un diccionario con:
        distancias -> {nodo: distancia_minima}
        previos    -> {nodo: nodo_anterior}
        ciclo_negativo -> True/False
        no_alcanzables -> lista de nodos sin camino desde el origen
    """
    if origen not in grafo.adyacencia:
        raise ValueError("El nodo origen '{}' no existe en el grafo".format(origen))

    nodos = grafo.obtener_nodos()
    aristas = _aristas_dirigidas(grafo)

    distancias = {n: INFINITO for n in nodos}
    previos = {n: None for n in nodos}
    distancias[origen] = 0

    # Relajar todas las aristas (N - 1) veces
    for _ in range(len(nodos) - 1):
        hubo_cambio = False
        for origen_a, destino_a, peso in aristas:
            if distancias[origen_a] != INFINITO and distancias[origen_a] + peso < distancias[destino_a]:
                distancias[destino_a] = distancias[origen_a] + peso
                previos[destino_a] = origen_a
                hubo_cambio = True
        if not hubo_cambio:
            break  # ya convergio, no hace falta seguir iterando

    # Una iteracion mas: si algo todavia mejora, hay un ciclo negativo
    ciclo_negativo = False
    for origen_a, destino_a, peso in aristas:
        if distancias[origen_a] != INFINITO and distancias[origen_a] + peso < distancias[destino_a]:
            ciclo_negativo = True
            break

    no_alcanzables = [n for n in nodos if distancias[n] == INFINITO]

    return {
        "distancias": distancias,
        "previos": previos,
        "ciclo_negativo": ciclo_negativo,
        "no_alcanzables": no_alcanzables,
    }


def _aristas_dirigidas(grafo):
    """
    Devuelve todas las aristas como (origen, destino, peso) tratandolas
    siempre como dirigidas (si el grafo es no dirigido, cada arista ya
    aparece en ambos sentidos dentro de la lista de adyacencia).
    """
    aristas = []
    for origen in grafo.adyacencia:
        for destino, peso in grafo.adyacencia[origen]:
            aristas.append((origen, destino, peso))
    return aristas


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
        return []
    return camino
