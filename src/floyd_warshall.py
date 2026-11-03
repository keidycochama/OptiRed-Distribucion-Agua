# -*- coding: utf-8 -*-
"""
floyd_warshall.py
-----------------
Modulo 5: Caminos mas cortos entre TODOS los pares - FLOYD-WARSHALL.

Algoritmo de programacion dinamica que calcula la distancia minima
entre cada par de nodos, actualizando progresivamente una matriz de
distancias considerando nodos intermedios k:

    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

Complejidad: O(N^3). Conveniente para redes pequenas o medianas, ya
que entrega directamente la matriz completa de distancias.
"""

INFINITO = float("inf")


def floyd_warshall(grafo):
    """
    Ejecuta Floyd-Warshall sobre 'grafo'.

    Retorna un diccionario con:
        nodos -> lista de nodos (define el orden de filas/columnas)
        matriz -> dict de dict: matriz[i][j] = distancia minima de i a j
        ciclo_negativo -> True si se detecta un ciclo negativo (distancia
                          negativa en la diagonal principal)
    """
    nodos = grafo.obtener_nodos()
    matriz = {i: {j: INFINITO for j in nodos} for i in nodos}

    # Distancia de cada nodo a si mismo es 0
    for n in nodos:
        matriz[n][n] = 0

    # Peso directo cuando existe arista
    for origen in nodos:
        for destino, peso in grafo.vecinos(origen):
            if peso < matriz[origen][destino]:
                matriz[origen][destino] = peso

    # Recurrencia principal: probar cada nodo k como intermediario
    for k in nodos:
        for i in nodos:
            if matriz[i][k] == INFINITO:
                continue
            for j in nodos:
                if matriz[k][j] == INFINITO:
                    continue
                nueva = matriz[i][k] + matriz[k][j]
                if nueva < matriz[i][j]:
                    matriz[i][j] = nueva

    ciclo_negativo = any(matriz[n][n] < 0 for n in nodos)

    return {"nodos": nodos, "matriz": matriz, "ciclo_negativo": ciclo_negativo}
