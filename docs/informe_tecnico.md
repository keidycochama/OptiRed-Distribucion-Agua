# Informe Técnico Breve — OptiRed
## Red de Distribución de Agua

*(Plantilla de apoyo — completar con datos reales del grupo antes de entregar.
Extensión sugerida por el enunciado: 8 a 12 páginas.)*

## 1. Carátula
- Universidad, curso, docentes, integrantes del grupo, fecha.

## 2. Descripción del problema
El sistema modela una red de distribución de agua compuesta por un
reservorio principal, estaciones de bombeo, tanques de almacenamiento y
zonas de consumo (barrios), conectados por tuberías con distancia, costo o
capacidad asociada.

## 3. Objetivos
- Modelar la red como un grafo.
- Aplicar recorridos, árboles de expansión mínima, rutas más cortas,
  caminos entre todos los pares y flujo máximo sobre dicha red.

## 4. Modelo del grafo
- Representación: lista de adyacencia (`src/graph.py`).
- Nodos: reservorio (R), estaciones de bombeo (EB1, EB2...), tanques
  (T1, T2...), zonas de consumo (Z1, Z2...).
- Aristas: tuberías, con peso según el módulo (distancia, costo o capacidad).

## 5. Algoritmos implementados
Describir brevemente, para cada uno, la idea principal y su rol en la red
de agua (ver también los comentarios dentro de cada archivo de `src/`):
- BFS / DFS
- Prim / Kruskal (Union-Find)
- Dijkstra / Bellman-Ford
- Floyd-Warshall / Johnson
- Ford-Fulkerson

## 6. Estructuras de datos utilizadas
- Diccionario de listas (lista de adyacencia).
- Cola (`collections.deque`) para BFS.
- Pila para DFS iterativo.
- Cola de prioridad (`heapq`) para Prim, Dijkstra y Johnson.
- Union-Find (Disjoint Set Union) para Kruskal.

## 7. Casos de prueba
Resumir los 7 escenarios de la carpeta `data/` y los resultados obtenidos
(ver `tests/test_algoritmos.py`).

## 8. Resultados obtenidos
Incluir capturas de pantalla de la interfaz gráfica ejecutando cada módulo.

## 9. Análisis de complejidad
| Algoritmo        | Complejidad temporal |
|-------------------|----------------------|
| BFS / DFS         | O(N + A)             |
| Prim (con heap)   | O(A log N)           |
| Kruskal           | O(A log A)           |
| Dijkstra (heap)   | O(A log N)           |
| Bellman-Ford      | O(N · A)             |
| Floyd-Warshall    | O(N³)                |
| Johnson           | O(N · A log N)       |
| Ford-Fulkerson (Edmonds-Karp) | O(N · A²) |

## 10. Dificultades encontradas
(completar según la experiencia real del grupo)

## 11. Conclusiones
(completar)
