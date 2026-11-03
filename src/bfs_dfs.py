# -*- coding: utf-8 -*-
"""
bfs_dfs.py
----------
Modulo 2: Recorridos BFS (busqueda en anchura) y DFS (busqueda en
profundidad) sobre la red de distribucion de agua.

BFS -> usa una COLA. Visita primero el origen, luego sus vecinos
       directos, despues los vecinos de esos vecinos, etc.
DFS -> usa recursion (o una PILA explicita). Avanza lo mas profundo
       posible por una rama antes de retroceder.

Los vecinos de cada nodo se procesan en el mismo orden en que fueron
agregados al grafo (orden de insercion en la lista de adyacencia), por
lo que el orden de visita depende directamente del archivo de datos
cargado.
"""

from collections import deque


def bfs(grafo, origen):
    """
    Ejecuta BFS desde 'origen'.

    Retorna un diccionario con:
        orden        -> lista con el orden de visita
        arbol        -> lista de aristas (padre, hijo) del arbol de recorrido
        alcanzables  -> conjunto de nodos alcanzados
        no_alcanzables -> lista de nodos del grafo que NO fueron visitados
    """
    if origen not in grafo.adyacencia:
        raise ValueError("El nodo origen '{}' no existe en el grafo".format(origen))

    visitados = {origen}
    orden = [origen]
    arbol = []
    cola = deque([origen])

    while cola:
        actual = cola.popleft()
        for vecino, _ in grafo.vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                orden.append(vecino)
                arbol.append((actual, vecino))
                cola.append(vecino)

    no_alcanzables = [n for n in grafo.obtener_nodos() if n not in visitados]

    return {
        "orden": orden,
        "arbol": arbol,
        "alcanzables": visitados,
        "no_alcanzables": no_alcanzables,
    }


def dfs(grafo, origen):
    """
    Ejecuta DFS desde 'origen' de forma iterativa usando una pila
    explicita (para evitar problemas de limite de recursion en grafos
    grandes, aunque conceptualmente equivale a la version recursiva).

    Retorna el mismo formato de diccionario que bfs().
    """
    if origen not in grafo.adyacencia:
        raise ValueError("El nodo origen '{}' no existe en el grafo".format(origen))

    visitados = set()
    orden = []
    arbol = []
    # Cada elemento de la pila es (nodo, padre)
    pila = [(origen, None)]

    while pila:
        actual, padre = pila.pop()
        if actual in visitados:
            continue
        visitados.add(actual)
        orden.append(actual)
        if padre is not None:
            arbol.append((padre, actual))

        # Se insertan los vecinos en orden inverso para que, al usar la
        # pila (LIFO), se visiten en el mismo orden en que aparecen en
        # la lista de adyacencia.
        for vecino, _ in reversed(grafo.vecinos(actual)):
            if vecino not in visitados:
                pila.append((vecino, actual))

    no_alcanzables = [n for n in grafo.obtener_nodos() if n not in visitados]

    return {
        "orden": orden,
        "arbol": arbol,
        "alcanzables": visitados,
        "no_alcanzables": no_alcanzables,
    }
