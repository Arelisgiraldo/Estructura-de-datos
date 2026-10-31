import os
import time
import random
import matplotlib.pyplot as plt

from Quadtreetree import (generar_puntos, crear_arbol,
                          fuerza_bruta_rango, fuerza_bruta_vecino)

TAMANOS = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
CONSULTAS = 300
RADIO = 500


# Mide el tiempo promedio de una búsqueda, en microsegundos
def medir(buscar, consultas):
    mejor = float("inf")
    for _ in range(5):  # Se repite 5 veces y se queda con la más rápida (menos ruido)
        inicio = time.perf_counter()
        for punto in consultas:
            buscar(punto)
        fin = time.perf_counter()
        mejor = min(mejor, fin - inicio)
    return mejor / len(consultas) * 1000000


# Primer tamaño en que el árbol fue más rápido que la fuerza bruta
def primer_cruce(tiempos_fuerza, tiempos_arbol):
    for i in range(len(TAMANOS)):
        if tiempos_arbol[i] < tiempos_fuerza[i]:
            return TAMANOS[i]
    return None


# 1. Medir los tiempos para cada tamaño
radio_fuerza, radio_arbol = [], []
vecino_fuerza, vecino_arbol = [], []
construccion = []

random.seed(1)
consultas = [(random.uniform(0, 10000), random.uniform(0, 10000)) for _ in range(CONSULTAS)]

for n in TAMANOS:
    puntos = generar_puntos(n)

    inicio = time.perf_counter()
    arbol = crear_arbol(puntos)
    construccion.append((time.perf_counter() - inicio) * 1000)  # milisegundos

    radio_fuerza.append(medir(lambda c: fuerza_bruta_rango(puntos, c, RADIO), consultas))
    radio_arbol.append(medir(lambda c: arbol.buscar_en_radio(c, RADIO), consultas))
    vecino_fuerza.append(medir(lambda c: fuerza_bruta_vecino(puntos, c), consultas))
    vecino_arbol.append(medir(lambda c: arbol.vecino_mas_cercano(c), consultas))


# 2. Tabla de resultados (FB = fuerza bruta, QT = Quadtree)
print("Tiempo promedio por consulta, en microsegundos")
print("Puntos | Radio FB | Radio QT | Vecino FB | Vecino QT | Construir QT (ms)")
for i in range(len(TAMANOS)):
    print(TAMANOS[i], "|", round(radio_fuerza[i], 1), "|", round(radio_arbol[i], 1), "|",
          round(vecino_fuerza[i], 1), "|", round(vecino_arbol[i], 1), "|", round(construccion[i], 1))


# 3. Respuesta a la pregunta del laboratorio
print()
print("¿Desde qué tamaño el Quadtree es más rápido que la fuerza bruta?")
print("Búsqueda por radio: desde", primer_cruce(radio_fuerza, radio_arbol), "puntos")
print("Vecino más cercano: desde", primer_cruce(vecino_fuerza, vecino_arbol), "puntos")

# Cuántas veces más rápido es el árbol con 10.000 puntos
i = TAMANOS.index(10000)
print()
print("Con 10.000 puntos, el Quadtree fue", round(radio_fuerza[i] / radio_arbol[i]),
      "veces más rápido en el radio y", round(vecino_fuerza[i] / vecino_arbol[i]),
      "veces más rápido en el vecino más cercano.")

# Cuántas búsquedas se necesitan para recuperar el tiempo de construir el árbol
ahorro = (radio_fuerza[i] - radio_arbol[i]) / 1000  # milisegundos ahorrados por búsqueda
print("Construir el árbol de 10.000 puntos tomó", round(construccion[i], 1), "ms.",
      "Ese tiempo se recupera después de unas", round(construccion[i] / ahorro), "búsquedas por radio.")


# 4. Gráfica de tiempos
os.makedirs("graficas", exist_ok=True)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(TAMANOS, radio_fuerza, marker="o", color="orange", label="Fuerza bruta")
ax1.plot(TAMANOS, radio_arbol, marker="o", color="blue", label="Quadtree")
ax1.set_title("Búsqueda en un radio de 500 m")

ax2.plot(TAMANOS, vecino_fuerza, marker="o", color="orange", label="Fuerza bruta")
ax2.plot(TAMANOS, vecino_arbol, marker="o", color="blue", label="Quadtree")
ax2.set_title("Vecino más cercano")

for ax in (ax1, ax2):
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cantidad de puntos (escala logarítmica)")
    ax.set_ylabel("Microsegundos por consulta (escala logarítmica)")
    ax.legend()

fig.savefig("graficas/tiempos.png", dpi=150, bbox_inches="tight")
print()
print("Gráfica guardada: graficas/tiempos.png")