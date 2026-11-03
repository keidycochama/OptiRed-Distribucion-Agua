# OptiRed — Sistema de Análisis y Optimización de Redes
### Aplicado a una Red de Distribución de Agua

Proyecto Parcial II — Programación III

## Descripción

El sistema modela una **red de distribución de agua** (reservorio, estaciones
de bombeo, tanques y zonas de consumo) mediante un grafo, y permite ejecutar
sobre ella los algoritmos clásicos vistos en el curso: recorridos BFS/DFS,
árboles de expansión mínima (Prim/Kruskal), rutas más cortas (Dijkstra/
Bellman-Ford), caminos entre todos los pares (Floyd-Warshall/Johnson) y
flujo máximo (Ford-Fulkerson).

La interfaz es gráfica (Tkinter), organizada en pestañas — una por cada
módulo del sistema.

## Requisitos

- Python 3.8 o superior.
- La mayor parte del sistema usa solo la librería estándar (`tkinter`,
  `heapq`, `csv`, `json`, `collections`). La única dependencia externa es
  **matplotlib**, usada solo para dibujar el diagrama de la red (panel
  derecho de la interfaz):
  ```bash
  pip install -r requirements.txt
  ```
  Si no se instala matplotlib, el sistema sigue funcionando igual (todos
  los algoritmos y resultados en texto), solo que el panel derecho muestra
  un aviso en vez del diagrama.
- En Linux, si `tkinter` no está disponible, instalar con:
  `sudo apt-get install python3-tk`

## Interfaz gráfica

La ventana está dividida en dos partes:
- **Izquierda**: pestañas con los controles y resultados en texto de cada
  módulo (igual que antes).
- **Derecha**: un **diagrama de la red** (nodos y tuberías) que se redibuja
  automáticamente después de cada acción, resaltando lo relevante:
  - Gestión del grafo → la red completa tal como se cargó.
  - BFS/DFS → el árbol de recorrido (morado) y el nodo origen.
  - MST → las aristas del árbol de expansión mínima (verde).
  - Rutas más cortas → el camino encontrado, con flechas (rojo).
  - Flujo máximo → las tuberías con flujo enviado (azul), mostrando
    "enviado/capacidad" en vez del peso.

## Abrir el proyecto en Visual Studio 2022

Este proyecto incluye los archivos `proyecto_optired.sln` y
`proyecto_optired.pyproj`, por lo que se puede abrir directamente como un
**proyecto de Python en Visual Studio 2022** (como cualquier otro proyecto
de VS), en vez de solo tener sueltos los archivos `.py`.

Pasos:

1. Instalar en Visual Studio 2022 el workload **"Desarrollo de Python"**
   (Visual Studio Installer → Modificar → marcar "Python development").
2. Doble clic en `proyecto_optired.sln` para abrir la solución.
3. En el Explorador de soluciones aparecerán las carpetas `src/`, `data/`,
   `tests/` y `docs/`, y el archivo `main.py` marcado como **Startup File**
   (con negrita) — el que se ejecuta al presionar F5 o el boton "Start".
4. Si es la primera vez, Visual Studio pedira seleccionar el **interprete
   de Python** instalado en tu equipo (Python 3.8+). Se selecciona el que
   ya tengas instalado (no requiere librerias externas, solo la libreria
   estandar).
5. Presionar **F5** (o el boton verde "Start") para ejecutar la interfaz
   grafica (Tkinter).

También se puede seguir ejecutando desde consola sin Visual Studio, como se
explica a continuación.

## Ejecución por consola (alternativa)

```bash
cd proyecto_optired
python main.py
```

Se abrirá la ventana principal con 6 pestañas, una por cada módulo.

## Cómo usar cada pestaña

1. **Gestión del grafo**: elegir si el grafo es dirigido/ponderado, cargar
   una red desde un archivo `.csv` de la carpeta `data/` (o crear una
   manualmente agregando nodos y aristas), y ver la lista de nodos/aristas.
2. **BFS / DFS**: escribir un nodo origen y ejecutar el recorrido.
3. **MST (Prim / Kruskal)**: requiere un grafo NO dirigido y conexo.
4. **Rutas más cortas**: Dijkstra (sin pesos negativos) o Bellman-Ford
   (admite pesos negativos y detecta ciclos negativos). El destino es
   opcional; si se indica, se reconstruye el camino.
5. **Todos los pares**: Floyd-Warshall o Johnson, muestran la matriz
   completa de distancias mínimas.
6. **Flujo máximo**: indicar el nodo fuente y el nodo sumidero; se ejecuta
   Ford-Fulkerson (variante Edmonds-Karp) y se muestra el flujo por arista.

## Datos de prueba (carpeta `data/`)

| Archivo                       | Uso                                             |
|--------------------------------|--------------------------------------------------|
| `grafo_simple.csv`             | BFS / DFS (no ponderado, con componente separado) |
| `grafo_mst.csv`                | Prim / Kruskal (no dirigido, ponderado, conexo)   |
| `grafo_dijkstra.csv`           | Dijkstra (dirigido, sin pesos negativos)          |
| `grafo_negativo.csv`           | Bellman-Ford / Johnson (pesos negativos, sin ciclo)|
| `grafo_ciclo_negativo.csv`     | Detección de ciclo negativo                       |
| `grafo_todos_pares.csv`        | Floyd-Warshall / Johnson (comparación)            |
| `grafo_flujo.csv`              | Ford-Fulkerson (fuente `R`, sumidero `Z1`)        |

Formato de cada línea: `origen,destino,peso`. Las líneas que empiezan con
`#` son comentarios y se ignoran.

## Estructura del proyecto

```
proyecto_optired/
|-- main.py                 # Interfaz gráfica (Tkinter), integra todos los módulos
|-- requirements.txt        # Única dependencia externa: matplotlib (para el diagrama)
|-- README.md
|-- data/                   # Archivos .csv de prueba
|-- src/
|   |-- graph.py            # Módulo 1: representación del grafo (lista de adyacencia)
|   |-- bfs_dfs.py           # Módulo 2: BFS y DFS
|   |-- union_find.py        # Estructura dinámica usada por Kruskal
|   |-- prim.py              # Módulo 3: MST - Prim
|   |-- kruskal.py           # Módulo 3: MST - Kruskal
|   |-- dijkstra.py          # Módulo 4: rutas más cortas - Dijkstra
|   |-- bellman_ford.py      # Módulo 4: rutas más cortas - Bellman-Ford
|   |-- floyd_warshall.py    # Módulo 5: todos los pares - Floyd-Warshall
|   |-- johnson.py           # Módulo 5: todos los pares - Johnson
|   +-- ford_fulkerson.py    # Módulo 6: flujo máximo - Ford-Fulkerson
|   +-- graph_plot.py        # Panel grafico: dibuja la red (nodos y aristas) en la GUI
|-- tests/
|   +-- test_algoritmos.py   # Casos de prueba (unittest) para todos los módulos
+-- docs/
    +-- informe_tecnico.md   # Plantilla del informe técnico breve
```

Cada técnica algorítmica vive en su propio archivo dentro de `src/`; `main.py`
solo importa esas funciones y arma la interfaz gráfica.

## Pruebas

```bash
cd proyecto_optired
python -m unittest tests/test_algoritmos.py -v
```

## Autor

Samuel — UNSAAC — Programación III — Grupo 3 (Red de distribución de agua)
