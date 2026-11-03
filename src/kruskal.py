# -*- coding: utf-8 -*-
"""
kruskal.py
----------
Modulo 3: Arbol de Expansion Minima (MST) - Algoritmo de KRUSKAL.

Kruskal ordena TODAS las aristas del grafo por peso ascendente y las
va seleccionando siempre que no formen un ciclo. Para detectar ciclos
de manera eficiente se usa la estructura Union-Find (union_find.py).

Solo debe aplicarse sobre grafos NO dirigidos, ponderados y CONEXOS.
"""

from union_find import UnionFind


def kruskal(grafo):
    """
    Ejecuta el algoritmo de Kruskal sobre 'grafo'.

    Retorna un diccionario con:
        aristas -> lista de (origen, destino, peso) seleccionadas
        costo_total -> suma de los pesos del arbol
    Lanza ValueError si el grafo no es apto para MST.
    """
    if grafo.dirigido:
        raise ValueError("Kruskal solo puede aplicarse sobre grafos NO dirigidos.")
    if not grafo.es_conexo():
        raise ValueError(
            "El grafo no es conexo. No existe un arbol de expansion minima "
            "que cubra todos los nodos (podria calcularse un bosque por componentes)."
        )

    nodos = grafo.obtener_nodos()
    todas_las_aristas = sorted(grafo.obtener_aristas(), key=lambda a: a[2])  # ordenar por peso

    uf = UnionFind(nodos)
    aristas_resultado = []
    costo_total = 0

    for origen, destino, peso in todas_las_aristas:
        # union() devuelve True si origen y destino NO estaban conectados
        # (es decir, agregarla no genera un ciclo)
        if uf.union(origen, destino):
            aristas_resultado.append((origen, destino, peso))
            costo_total += peso

    return {"aristas": aristas_resultado, "costo_total": costo_total}
