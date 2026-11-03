# -*- coding: utf-8 -*-
"""
test_algoritmos.py
-------------------
Casos de prueba minimos para validar el funcionamiento de cada modulo
del sistema OptiRed, usando los archivos de la carpeta data/.

Para ejecutar todas las pruebas:
    python -m unittest tests/test_algoritmos.py -v

(ejecutar desde la carpeta raiz del proyecto: proyecto_optired/)
"""

import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
DATA = os.path.join(RAIZ, "data")

from graph import Grafo
from bfs_dfs import bfs, dfs
from prim import prim
from kruskal import kruskal
from dijkstra import dijkstra
from bellman_ford import bellman_ford
from floyd_warshall import floyd_warshall
from johnson import johnson
from ford_fulkerson import ford_fulkerson


def _cargar(nombre_archivo, dirigido, ponderado):
    g = Grafo(dirigido=dirigido, ponderado=ponderado)
    g.cargar_desde_csv(os.path.join(DATA, nombre_archivo))
    return g


class TestModulo1Grafo(unittest.TestCase):
    def test_cargar_y_contar(self):
        g = _cargar("grafo_mst.csv", dirigido=False, ponderado=True)
        self.assertIn("R", g.obtener_nodos())
        self.assertGreater(len(g.obtener_aristas()), 0)

    def test_no_dirigido_arista_en_ambos_sentidos(self):
        g = Grafo(dirigido=False, ponderado=True)
        g.agregar_arista("A", "B", 5)
        self.assertTrue(any(v == "B" for v, _ in g.vecinos("A")))
        self.assertTrue(any(v == "A" for v, _ in g.vecinos("B")))


class TestModulo2BFSDFS(unittest.TestCase):
    def setUp(self):
        self.g = _cargar("grafo_simple.csv", dirigido=False, ponderado=False)

    def test_bfs_alcanza_componente_principal(self):
        resultado = bfs(self.g, "R")
        # Z6 y Z7 forman un componente aparte: no deben ser alcanzables desde R
        self.assertIn("Z6", resultado["no_alcanzables"])
        self.assertIn("Z7", resultado["no_alcanzables"])
        self.assertIn("Z4", resultado["orden"])

    def test_dfs_visita_los_mismos_nodos_que_bfs(self):
        r_bfs = bfs(self.g, "R")
        r_dfs = dfs(self.g, "R")
        self.assertEqual(set(r_bfs["orden"]), set(r_dfs["orden"]))


class TestModulo3MST(unittest.TestCase):
    def setUp(self):
        self.g = _cargar("grafo_mst.csv", dirigido=False, ponderado=True)

    def test_prim_y_kruskal_dan_el_mismo_costo(self):
        r_prim = prim(self.g)
        r_kruskal = kruskal(self.g)
        # Ambos algoritmos deben encontrar un MST del mismo costo total
        self.assertEqual(r_prim["costo_total"], r_kruskal["costo_total"])
        # El MST siempre tiene (numero_de_nodos - 1) aristas
        self.assertEqual(len(r_prim["aristas"]), len(self.g.obtener_nodos()) - 1)


class TestModulo4Rutas(unittest.TestCase):
    def test_dijkstra_distancia_minima(self):
        g = _cargar("grafo_dijkstra.csv", dirigido=True, ponderado=True)
        resultado = dijkstra(g, "R")
        # Camino optimo: R->EB1->T1->Z1->Z2 = 4+5+2+3 = 14
        self.assertEqual(resultado["distancias"]["Z2"], 14)

    def test_bellman_ford_detecta_ciclo_negativo(self):
        g = _cargar("grafo_ciclo_negativo.csv", dirigido=True, ponderado=True)
        resultado = bellman_ford(g, "R")
        self.assertTrue(resultado["ciclo_negativo"])

    def test_bellman_ford_sin_ciclo_negativo(self):
        g = _cargar("grafo_negativo.csv", dirigido=True, ponderado=True)
        resultado = bellman_ford(g, "R")
        self.assertFalse(resultado["ciclo_negativo"])


class TestModulo5TodosLosPares(unittest.TestCase):
    def setUp(self):
        self.g = _cargar("grafo_todos_pares.csv", dirigido=True, ponderado=True)

    def test_floyd_warshall_diagonal_es_cero(self):
        resultado = floyd_warshall(self.g)
        for n in resultado["nodos"]:
            self.assertEqual(resultado["matriz"][n][n], 0)

    def test_johnson_coincide_con_floyd_warshall(self):
        r_floyd = floyd_warshall(self.g)
        r_johnson = johnson(self.g)
        for i in r_floyd["nodos"]:
            for j in r_floyd["nodos"]:
                self.assertAlmostEqual(r_floyd["matriz"][i][j], r_johnson["matriz"][i][j])


class TestModulo6Flujo(unittest.TestCase):
    def test_flujo_maximo_esperado(self):
        g = _cargar("grafo_flujo.csv", dirigido=True, ponderado=True)
        resultado = ford_fulkerson(g, "R", "Z1")
        self.assertEqual(resultado["flujo_maximo"], 23)

    def test_sin_camino_lanza_error(self):
        g = Grafo(dirigido=True, ponderado=True)
        g.agregar_nodo("R")
        g.agregar_nodo("Z1")  # nodo aislado, sin aristas
        with self.assertRaises(ValueError):
            ford_fulkerson(g, "R", "Z1")


if __name__ == "__main__":
    unittest.main()
