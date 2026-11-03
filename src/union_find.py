# -*- coding: utf-8 -*-
"""
union_find.py
-------------
Estructura dinamica: Union-Find (tambien llamada Disjoint Set Union, DSU).

Se utiliza dentro del algoritmo de Kruskal para detectar de forma
eficiente si dos nodos ya pertenecen al mismo conjunto (y por lo tanto
agregar la arista entre ellos formaria un ciclo).

Implementa las dos optimizaciones clasicas:
    - Compresion de caminos (path compression) en find().
    - Union por rango (union by rank) en union().

Con estas optimizaciones, cada operacion es practicamente O(1) en la
practica (mas precisamente O(alfa(n)), la funcion inversa de Ackermann).
"""


class UnionFind:
    def __init__(self, elementos):
        # Cada elemento comienza siendo su propio representante (su propio conjunto)
        self.padre = {e: e for e in elementos}
        self.rango = {e: 0 for e in elementos}

    def find(self, x):
        """Devuelve el representante del conjunto de x, comprimiendo el camino."""
        if self.padre[x] != x:
            self.padre[x] = self.find(self.padre[x])  # compresion de caminos
        return self.padre[x]

    def union(self, x, y):
        """
        Une los conjuntos de x e y.
        Retorna True si se unieron (antes estaban separados),
        o False si ya pertenecian al mismo conjunto (indicaria un ciclo).
        """
        raiz_x = self.find(x)
        raiz_y = self.find(y)

        if raiz_x == raiz_y:
            return False  # ya estan conectados -> formaria un ciclo

        # Union por rango: el arbol mas pequeno cuelga del mas grande
        if self.rango[raiz_x] < self.rango[raiz_y]:
            raiz_x, raiz_y = raiz_y, raiz_x
        self.padre[raiz_y] = raiz_x
        if self.rango[raiz_x] == self.rango[raiz_y]:
            self.rango[raiz_x] += 1
        return True

    def conectados(self, x, y):
        return self.find(x) == self.find(y)
