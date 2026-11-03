# -*- coding: utf-8 -*-
"""
ford_fulkerson.py
-----------------
Modulo 6: Flujo maximo - ALGORITMO DE FORD-FULKERSON.

Calcula la maxima cantidad de agua que puede enviarse desde una FUENTE
(por ejemplo, el reservorio principal) hasta un SUMIDERO (por ejemplo,
una zona de consumo final), respetando la capacidad maxima de cada
tuberia (arista).

Se implementa la variante EDMONDS-KARP: en cada iteracion se busca un
camino aumentante usando BFS (esto garantiza mejor complejidad que
buscar con DFS). El proceso es:
    1. Iniciar el flujo en cero.
    2. Buscar un camino aumentante desde la fuente hasta el sumidero
       usando el GRAFO RESIDUAL (capacidad restante).
    3. Calcular la minima capacidad residual del camino (cuello de botella).
    4. Aumentar el flujo en ese valor y actualizar el grafo residual.
    5. Repetir hasta que no existan mas caminos aumentantes.
"""

from collections import deque, defaultdict


def ford_fulkerson(grafo, fuente, sumidero):
    """
    Ejecuta Ford-Fulkerson (variante Edmonds-Karp) sobre 'grafo'.

    El peso de cada arista se interpreta como CAPACIDAD MAXIMA.

    Retorna un diccionario con:
        flujo_maximo -> valor numerico del flujo maximo encontrado
        flujo_por_arista -> lista de (origen, destino, flujo_enviado, capacidad)
    Lanza ValueError si no existe ningun camino entre fuente y sumidero.
    """
    if fuente not in grafo.adyacencia:
        raise ValueError("El nodo fuente '{}' no existe en el grafo".format(fuente))
    if sumidero not in grafo.adyacencia:
        raise ValueError("El nodo sumidero '{}' no existe en el grafo".format(sumidero))

    # Capacidad residual: capacidad[u][v] = capacidad restante disponible.
    # Se inicializa con las capacidades originales; la arista inversa
    # (v -> u) empieza en 0 y permite "deshacer" flujo enviado (grafo residual).
    capacidad = defaultdict(lambda: defaultdict(int))
    capacidad_original = {}  # guarda la capacidad original de cada arista real

    for origen in grafo.adyacencia:
        for destino, peso in grafo.adyacencia[origen]:
            capacidad[origen][destino] += int(peso)
            capacidad_original[(origen, destino)] = capacidad_original.get((origen, destino), 0) + int(peso)

    # Antes de empezar, verificamos si existe al menos un camino en el
    # grafo original (con las capacidades completas, sin usar nada aun).
    camino_inicial, _ = _bfs_camino_aumentante(capacidad, fuente, sumidero)
    if camino_inicial is None:
        raise ValueError(
            "No existe ningun camino desde la fuente '{}' hasta el sumidero '{}'.".format(fuente, sumidero)
        )

    flujo_maximo = 0

    while True:
        camino, capacidad_minima = _bfs_camino_aumentante(capacidad, fuente, sumidero)
        if camino is None:
            break  # ya no hay mas caminos aumentantes

        # Actualizar capacidades residuales a lo largo del camino
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            capacidad[u][v] -= capacidad_minima
            capacidad[v][u] += capacidad_minima  # arista inversa (permite deshacer flujo)

        flujo_maximo += capacidad_minima

    # Calcular el flujo final enviado por cada arista real:
    # flujo enviado = capacidad_original - capacidad_residual_restante
    flujo_por_arista = []
    for (origen, destino), cap_original in capacidad_original.items():
        cap_restante = capacidad[origen][destino]
        flujo_enviado = cap_original - cap_restante
        flujo_por_arista.append((origen, destino, max(flujo_enviado, 0), cap_original))

    return {"flujo_maximo": flujo_maximo, "flujo_por_arista": flujo_por_arista}


def _bfs_camino_aumentante(capacidad, fuente, sumidero):
    """
    Busca, mediante BFS, un camino desde fuente hasta sumidero donde
    todas las aristas tengan capacidad residual > 0.
    Retorna (camino, capacidad_minima_del_camino) o (None, 0) si no existe.
    """
    padres = {fuente: None}
    cola = deque([fuente])

    while cola:
        actual = cola.popleft()
        if actual == sumidero:
            break
        for vecino, cap_residual in capacidad[actual].items():
            if cap_residual > 0 and vecino not in padres:
                padres[vecino] = actual
                cola.append(vecino)

    if sumidero not in padres:
        return None, 0

    # Reconstruir el camino y calcular el cuello de botella (capacidad minima)
    camino = []
    actual = sumidero
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]
    camino.reverse()

    capacidad_minima = min(
        capacidad[camino[i]][camino[i + 1]] for i in range(len(camino) - 1)
    )
    return camino, capacidad_minima
