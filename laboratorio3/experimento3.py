# experimento3.py  -  EXPERIMENTO 3: N pequeños (de 10 a 1.000 estudiantes)
# El experimento 1 empieza en N = 5.000, donde la Lista ya es mucho más lenta.
# Este experimento mide N pequeños para responder dos preguntas del laboratorio:
#   - ¿A partir de qué N se empiezan a ver las diferencias entre las estructuras?
#   - ¿Hay costos constantes que hacen que la Lista (O(N)) tarde parecido a los
#     árboles (O(log N)) cuando hay pocos estudiantes?
# Mide igual que el experimento 1, pero solo con ids aleatorios.
# Todo se repite 10 veces; cada medición queda guardada en resultados/experimento3.csv
# Mientras corre cada cronómetro, el recolector de basura de Python (gc) está apagado.


import csv
import gc
import os
import random
import statistics
import time

from lista_enlazada import Lista
from arbol_abb import ArbolABB
from arbol_bplus import ArbolBPlus

REPETICIONES = 10
TAMANOS = [10, 20, 50, 100, 200, 500, 1000]
NOMBRES = ["Ana", "Carlos", "María", "Luis", "Sofía", "Pedro"]

# Tabla de M (número de búsquedas), escogida con una prueba para que cada medición
# dure más de 1 segundo. Con N pequeño cada búsqueda tarda menos de 1 µs, así que
# hacen falta millones de búsquedas.
M_LISTA = {10: 5000000, 20: 3000000, 50: 1500000, 100: 1000000,
           200: 500000, 500: 200000, 1000: 100000}
M_ARBOLES = 3000000                                  # ABB y B+


def crear_estudiantes(N):
    """N estudiantes con ids del 1 al N, mezclados al azar."""
    ids = list(range(1, N + 1))
    random.shuffle(ids)
    estudiantes = []
    for i in ids:
        estudiantes.append({"id": i,
                            "nombre": random.choice(NOMBRES),
                            "edad": random.randint(16, 30),
                            "promedio": round(random.uniform(0, 5), 1)})
    return estudiantes


# Archivo donde se guarda cada medición (mismas columnas que el experimento 1)
os.makedirs("resultados", exist_ok=True)
archivo = open("resultados/experimento3.csv", "w", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
escritor.writerow(["repeticion", "N", "orden", "estructura", "M",
                   "t_construir_s", "t_buscar_s", "t_una_busqueda_us", "altura"])

resultados = {}     # (estructura, N) -> lista con el tiempo de una búsqueda de cada repetición
inicio_total = time.perf_counter()

for rep in range(1, REPETICIONES + 1):
    random.seed(rep)        # semilla = número de repetición -> los datos se pueden repetir

    for N in TAMANOS:
        # Los ids a buscar se sortean UNA vez por cada N:
        # así las tres estructuras buscan los mismos estudiantes.
        # random.choices escoge M_maximo ids al azar entre 1 y N (se pueden repetir);
        # hace lo mismo que el ciclo con randint del experimento 1, pero más rápido.
        M_maximo = max(M_LISTA[N], M_ARBOLES)
        ids_a_buscar = random.choices(range(1, N + 1), k=M_maximo)

        estudiantes = crear_estudiantes(N)

        for nombre in ["Lista", "ABB", "B+"]:
            # Crear la estructura vacía y escoger M según la tabla
            if nombre == "Lista":
                estructura = Lista()
                M = M_LISTA[N]
            elif nombre == "ABB":
                estructura = ArbolABB()
                M = M_ARBOLES
            else:
                estructura = ArbolBPlus()
                M = M_ARBOLES

            # Cronómetro 1: construir (meter los N estudiantes)
            # Antes de cada cronómetro se limpia la memoria (gc.collect) y se apaga el
            # recolector de basura (gc.disable), para que sus pausas no se sumen al tiempo.
            gc.collect()
            gc.disable()
            inicio = time.perf_counter()
            for estudiante in estudiantes:
                estructura.insertar(estudiante)
            t_construir = time.perf_counter() - inicio
            gc.enable()

            # Cronómetro 2: hacer las M búsquedas
            busquedas = ids_a_buscar[:M]          # se prepara ANTES de prender el cronómetro
            gc.collect()
            gc.disable()
            inicio = time.perf_counter()
            for id_buscado in busquedas:
                estructura.buscar(id_buscado)
            t_buscar = time.perf_counter() - inicio
            gc.enable()

            t_una = t_buscar / M * 1000000        # tiempo de UNA búsqueda, en microsegundos

            if nombre == "Lista":
                altura = ""                       # la lista no tiene altura
            else:
                altura = estructura.altura()

            # Guardar la medición en el CSV (después de parar el cronómetro)
            escritor.writerow([rep, N, "aleatorio", nombre, M, round(t_construir, 6),
                               round(t_buscar, 6), round(t_una, 4), altura])
            archivo.flush()                       # se guarda ya: si se corta, no se pierde
            clave = (nombre, N)
            if clave not in resultados:
                resultados[clave] = []
            resultados[clave].append(t_una)

            print(f"rep {rep:2} | N={N:5} | {nombre:5} | M={M:7} en {t_buscar:5.2f} s | "
                  f"una búsqueda: {t_una:7.3f} µs | altura {altura}")
            if t_buscar < 1:
                print("      ¡Ojo! esta prueba duró menos de 1 segundo")

    minutos = (time.perf_counter() - inicio_total) / 60
    print(f"--- Repetición {rep} de {REPETICIONES} terminada ({minutos:.1f} min) ---\n")

archivo.close()

# Promedios finales, y cuántas veces más lenta es la Lista que cada árbol
print(f"PROMEDIOS DE {REPETICIONES} REPETICIONES (tiempo de una búsqueda, µs)")
for N in TAMANOS:
    promedios = {}
    texto = f"N={N:5}"
    for nombre in ["Lista", "ABB", "B+"]:
        valores = resultados[(nombre, N)]
        promedios[nombre] = statistics.mean(valores)
        if len(valores) > 1:
            desviacion = statistics.stdev(valores)
        else:
            desviacion = 0
        texto += f" | {nombre} {promedios[nombre]:6.3f} ± {desviacion:5.3f}"
    texto += (f" | la Lista tarda {promedios['Lista'] / promedios['ABB']:4.1f} veces el ABB"
              f" y {promedios['Lista'] / promedios['B+']:4.1f} veces el B+")
    print(texto)

print("\nDatos guardados en resultados/experimento3.csv")
