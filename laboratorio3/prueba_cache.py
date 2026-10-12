#  PRUEBA APARTE (no es uno de los tres experimentos)
# Pregunta: con N grande, ¿por qué la Lista con ids aleatorios tarda más que con ids
# ordenados, si en los dos casos revisa en promedio la misma cantidad de nodos, (N + 1) / 2?
#
# Hipótesis: la memoria caché. En Python cada id es un objeto guardado en la memoria.
# Los ids se crean en orden (1, 2, 3, ...) y después se mezclan: al recorrer la lista,
# el procesador encuentra esos objetos en desorden y tiene que traerlos de la memoria
# principal, que es mucho más lenta que la caché.
# Si la hipótesis es cierta, al crear un id NUEVO junto a cada estudiante la diferencia
# debe desaparecer, aunque los ids sigan en orden aleatorio.
#
# Mide el tiempo por nodo visitado en tres casos, con N = 100.000.


import csv
import gc
import os
import random
import statistics
import time

from lista_enlazada import Lista

N = 100000
M = 1000                 # búsquedas por medición (cada medición dura más de 1 segundo)
REPETICIONES = 5


def crear_lista(ids, id_nuevo):
    """Mete N estudiantes en una Lista. Si id_nuevo es True, cada id se crea de nuevo
    justo antes de su estudiante, así queda a su lado en la memoria."""
    lista = Lista()
    for i in ids:
        if id_nuevo:
            i = int(str(i))      # mismo número, pero en un objeto nuevo
        lista.insertar({"id": i, "nombre": "Ana", "edad": 20, "promedio": 4.0})
    return lista


ordenados = list(range(1, N + 1))
random.seed(1)
mezclados = list(range(1, N + 1))
random.shuffle(mezclados)

casos = [("ids ordenados", ordenados, False),
         ("ids aleatorios", mezclados, False),
         ("ids aleatorios, cada id creado junto a su estudiante", mezclados, True)]

os.makedirs("resultados", exist_ok=True)
archivo = open("resultados/prueba_cache.csv", "w", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
escritor.writerow(["caso", "repeticion", "M", "t_buscar_s", "ns_por_nodo"])

for titulo, ids, id_nuevo in casos:
    lista = crear_lista(ids, id_nuevo)
    valores = []
    for rep in range(1, REPETICIONES + 1):
        random.seed(100 + rep)               # los tres casos buscan los mismos ids
        busquedas = []
        for k in range(M):
            busquedas.append(random.randint(1, N))

        gc.collect()
        gc.disable()
        inicio = time.perf_counter()
        for id_buscado in busquedas:
            lista.buscar(id_buscado)
        t_buscar = time.perf_counter() - inicio
        gc.enable()

        # En promedio cada búsqueda revisa (N + 1) / 2 nodos
        ns_por_nodo = t_buscar / M / ((N + 1) / 2) * 1000000000
        escritor.writerow([titulo, rep, M, round(t_buscar, 6), round(ns_por_nodo, 2)])
        archivo.flush()
        valores.append(ns_por_nodo)
        if t_buscar < 1:
            print("      ¡Ojo! esta prueba duró menos de 1 segundo")

    print(f"{titulo:53}: {statistics.mean(valores):5.1f} ± "
          f"{statistics.stdev(valores):4.1f} ns por nodo")

archivo.close()
print("\nDatos guardados en resultados/prueba_cache.csv")
