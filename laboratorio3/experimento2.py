#  variar M (número de búsquedas) con N fijo
# N = 10.000 estudiantes con ids aleatorios. Cada estructura hace M búsquedas,
# con M duplicándose (x1, x2, x4, x8), y se mide el tiempo TOTAL de esas búsquedas.
#
# Para qué sirve: si el tiempo crece en proporción a M (el doble de búsquedas,
# el doble de tiempo), entonces dividir entre M para obtener "el tiempo de una
# búsqueda" es válido, y se pueden comparar estructuras que hicieron distinto M.
#
# Mientras corre el cronómetro, el recolector de basura de Python (gc) está apagado.


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
N = 10000
NOMBRES = ["Ana", "Carlos", "María", "Luis", "Sofía", "Pedro"]

# Valores de M: cada uno es el doble del anterior. Son distintos por estructura para que
# cada prueba dure más de 1 segundo sin volverse eterna.
VALORES_M = {"Lista": [5000, 10000, 20000, 40000],
             "ABB":   [500000, 1000000, 2000000, 4000000],
             "B+":    [500000, 1000000, 2000000, 4000000]}
M_MAXIMO = 4000000


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


os.makedirs("resultados", exist_ok=True)
archivo = open("resultados/experimento2.csv", "w", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
escritor.writerow(["repeticion", "N", "estructura", "M", "t_buscar_s", "t_una_busqueda_us"])

resultados = {}     # (estructura, M) -> lista con el tiempo total de cada repetición
inicio_total = time.perf_counter()

for rep in range(1, REPETICIONES + 1):
    random.seed(rep)        # semilla = número de repetición -> los datos se pueden repetir
    estudiantes = crear_estudiantes(N)

    # Ids a buscar: se sortean una vez por repetición (todas las estructuras buscan los mismos)
    ids_a_buscar = []
    for k in range(M_MAXIMO):
        ids_a_buscar.append(random.randint(1, N))

    for nombre in ["Lista", "ABB", "B+"]:
        # Crear la estructura y meter los N estudiantes (una vez por repetición)
        if nombre == "Lista":
            estructura = Lista()
        elif nombre == "ABB":
            estructura = ArbolABB()
        else:
            estructura = ArbolBPlus()
        for estudiante in estudiantes:
            estructura.insertar(estudiante)

        for M in VALORES_M[nombre]:
            # Cronómetro: hacer las M búsquedas
            # Antes se limpia la memoria (gc.collect) y se apaga el recolector de
            # basura (gc.disable), para que sus pausas no se sumen al tiempo.
            busquedas = ids_a_buscar[:M]          # se prepara ANTES de prender el cronómetro
            gc.collect()
            gc.disable()
            inicio = time.perf_counter()
            for id_buscado in busquedas:
                estructura.buscar(id_buscado)
            t_buscar = time.perf_counter() - inicio
            gc.enable()

            t_una = t_buscar / M * 1000000        # tiempo de UNA búsqueda, en microsegundos

            escritor.writerow([rep, N, nombre, M, round(t_buscar, 6), round(t_una, 4)])
            archivo.flush()
            clave = (nombre, M)
            if clave not in resultados:
                resultados[clave] = []
            resultados[clave].append(t_buscar)

            print(f"rep {rep:2} | {nombre:5} | M={M:7} | {t_buscar:6.2f} s | "
                  f"una búsqueda: {t_una:7.2f} µs")
            if t_buscar < 1:
                print("      ¡Ojo! esta prueba duró menos de 1 segundo")

    minutos = (time.perf_counter() - inicio_total) / 60
    print(f"--- Repetición {rep} de {REPETICIONES} terminada ({minutos:.1f} min) ---\n")

archivo.close()

# Promedios finales: tiempo total de las M búsquedas, y tiempo de una búsqueda
print(f"PROMEDIOS DE {REPETICIONES} REPETICIONES (N = {N})")
for clave in resultados:
    nombre, M = clave
    valores = resultados[clave]
    promedio = statistics.mean(valores)
    if len(valores) > 1:
        desviacion = statistics.stdev(valores)
    else:
        desviacion = 0
    print(f"{nombre:5} | M={M:7} | tiempo total {promedio:6.2f} ± {desviacion:5.2f} s | "
          f"una búsqueda: {promedio / M * 1000000:7.2f} µs")

print("\nDatos guardados en resultados/experimento2.csv")
