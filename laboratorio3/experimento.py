#  10 repeticiones, guardar en CSV y promedios
# Mide cuánto tarda BUSCAR en Lista, ABB y B+ para N = 5.000 ... 100.000,
# con ids insertados en orden aleatorio y en orden ordenado.
# Todo se repite 10 veces; cada medición queda guardada en resultados/experimento1.csv
# y al final se muestran los promedios en pantalla.
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
TAMANOS = [5000, 10000, 20000, 50000, 100000]
ORDENES = ["aleatorio", "ordenado"]
NOMBRES = ["Ana", "Carlos", "María", "Luis", "Sofía", "Pedro"]

# Tabla de M (número de búsquedas), escogida con la prueba piloto
M_LENTAS = {5000: 10000, 10000: 5000, 20000: 2500, 50000: 1000, 100000: 500}  # Lista y ABB ordenado
M_RAPIDAS = 1000000                                                          # ABB aleatorio y B+

# El ABB con ids ordenados solo se mide hasta este N (construirlo crece como N²)
N_MAX_ABB_ORDENADO = 20000


def crear_estudiantes(N, orden):
    """N estudiantes con ids del 1 al N; si el orden es "aleatorio", se mezclan."""
    ids = list(range(1, N + 1))
    if orden == "aleatorio":
        random.shuffle(ids)
    estudiantes = []
    for i in ids:
        estudiantes.append({"id": i,
                            "nombre": random.choice(NOMBRES),
                            "edad": random.randint(16, 30),
                            "promedio": round(random.uniform(0, 5), 1)})
    return estudiantes


# Archivo donde se guarda cada medición (una fila por prueba)
os.makedirs("resultados", exist_ok=True)
archivo = open("resultados/experimento1.csv", "w", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
escritor.writerow(["repeticion", "N", "orden", "estructura", "M",
                   "t_construir_s", "t_buscar_s", "t_una_busqueda_us", "altura"])

resultados = {}     # (orden, estructura, N) -> lista con el tiempo de una búsqueda de cada repetición
inicio_total = time.perf_counter()

for rep in range(1, REPETICIONES + 1):
    random.seed(rep)        # semilla = número de repetición -> los datos se pueden repetir

    for N in TAMANOS:
        # Los ids a buscar se sortean UNA vez por cada N:
        # así todas las estructuras y los dos órdenes buscan los mismos estudiantes.
        ids_a_buscar = []
        for k in range(M_RAPIDAS):
            ids_a_buscar.append(random.randint(1, N))

        for orden in ORDENES:
            estudiantes = crear_estudiantes(N, orden)

            for nombre in ["Lista", "ABB", "B+"]:
                if nombre == "ABB" and orden == "ordenado" and N > N_MAX_ABB_ORDENADO:
                    continue    # se salta: tardaría demasiado

                # Crear la estructura vacía y escoger M según la tabla
                if nombre == "Lista":
                    estructura = Lista()
                    M = M_LENTAS[N]
                elif nombre == "ABB":
                    estructura = ArbolABB()
                    if orden == "ordenado":
                        M = M_LENTAS[N]
                    else:
                        M = M_RAPIDAS
                else:
                    estructura = ArbolBPlus()
                    M = M_RAPIDAS

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

                # Guardar la medición en el CSV y en el diccionario de resultados
                escritor.writerow([rep, N, orden, nombre, M, round(t_construir, 6),
                                   round(t_buscar, 6), round(t_una, 4), altura])
                archivo.flush()                       # se guarda ya: si se corta, no se pierde
                clave = (orden, nombre, N)
                if clave not in resultados:
                    resultados[clave] = []
                resultados[clave].append(t_una)

                # (los números después de ":" solo sirven para alinear las columnas)
                print(f"rep {rep:2} | N={N:6} | {orden:9} | {nombre:5} | "
                      f"construir {t_construir:6.2f} s | M={M:7} en {t_buscar:5.2f} s | "
                      f"una búsqueda: {t_una:9.2f} µs | altura {altura}")
                if t_buscar < 1:
                    print("      ¡Ojo! esta prueba duró menos de 1 segundo")

    minutos = (time.perf_counter() - inicio_total) / 60
    print(f"--- Repetición {rep} de {REPETICIONES} terminada ({minutos:.1f} min) ---\n")

archivo.close()

# Promedios finales: promedio ± desviación estándar de las repeticiones
print(f"PROMEDIOS DE {REPETICIONES} REPETICIONES (tiempo de una búsqueda)")
for clave in resultados:
    orden, nombre, N = clave
    valores = resultados[clave]
    promedio = statistics.mean(valores)
    if len(valores) > 1:
        desviacion = statistics.stdev(valores)
    else:
        desviacion = 0
    print(f"N={N:6} | {orden:9} | {nombre:5} | {promedio:9.2f} ± {desviacion:7.2f} µs")

print("\nDatos guardados en resultados/experimento1.csv")
