# -*- coding: utf-8 -*-
"""
prim.py
-------
Modulo 3: Arbol de Expansion Minima (MST) - Algoritmo de PRIM.

Prim construye el arbol empezando desde un nodo inicial y agregando,
en cada paso, la arista de MENOR PESO que conecta un nodo ya visitado
con un nodo todavia no visitado.

Se implementa usando una cola de prioridad (heapq), lo cual da una
complejidad de O(A log N), donde A es el numero de aristas y N el
numero de nodos.

Solo debe aplicarse sobre grafos NO dirigidos, ponderados y CONEXOS.
"""

import heapq


def prim(grafo, nodo_inicial=None):
    """
    Ejecuta el algoritmo de Prim sobre 'grafo'.

    Retorna un diccionario con:
        aristas -> lista de (origen, destino, peso) seleccionadas
        costo_total -> suma de los pesos del arbol
    Lanza ValueError si el grafo no es apto para MST (dirigido o no conexo).
    """
    if grafo.dirigido:
        raise ValueError("Prim solo puede aplicarse sobre grafos NO dirigidos.")
    if not grafo.es_conexo():
        raise ValueError(
            "El grafo no es conexo. No existe un arbol de expansion minima "
            "que cubra todos los nodos (podria calcularse un bosque por componentes)."
        )

    nodos = grafo.obtener_nodos()
    if not nodos:
        return {"aristas": [], "costo_total": 0}

    inicio = nodo_inicial if nodo_inicial in nodos else nodos[0]

    visitados = {inicio}
    aristas_resultado = []
    costo_total = 0

    # heap de (peso, origen, destino)
    heap = []
    for vecino, peso in grafo.vecinos(inicio):
        heapq.heappush(heap, (peso, inicio, vecino))

    while heap and len(visitados) < len(nodos):
        peso, origen, destino = heapq.heappop(heap)
        if destino in visitados:
            continue
        visitados.add(destino)
        aristas_resultado.append((origen, destino, peso))
        costo_total += peso

        for vecino, p in grafo.vecinos(destino):
            if vecino not in visitados:
                heapq.heappush(heap, (p, destino, vecino))

    return {"aristas": aristas_resultado, "costo_total": costo_total}
