"""
LABORATORIO 1 - Creación de una matriz de 100.000 x 100.000 en disco duro
Estudiante: Xiomara Echavarria
Este script construye la matriz directamente en el disco duro, evitando
los problemas de:
  1. Consumo excesivo de RAM
  2. Escritura lenta a disco
  3. Falta de optimización en la creación y almacenamiento de datos

La matriz nunca se arma completa en memoria. Se genera y escribe por
bloques (chunks) de filas, y cada fila queda delimitada en el archivo
por un byte separador, para poder identificar claramente dónde empieza
y dónde termina cada una.
"""

import numpy as np
import time
import os

# CONFIGURACIÓN GENERAL


# Nombre del archivo binario donde se va a guardar la matriz en disco
filename = "matriz_100k.dat"

# Dimensiones de la matriz pedida por el laboratorio
n_filas, n_cols = 100_000, 100_000

# Cantidad de filas que se generan y escriben juntas en cada pasada.
# En vez de escribir fila por fila (o peor, celda por celda), se agrupan
# 1000 filas por bloque. Esto reduce muchísimo la cantidad de operaciones
# de entrada/salida (I/O) contra el disco, que es lo que hace que la
# escritura sea lenta si se hace de a poquitos.
chunk = 1000

# Valor que se usa como separador entre una fila y la siguiente.
# Los datos de la matriz son únicamente 0 o 1, así que cualquier otro
# número (en este caso 2) nunca puede confundirse con un dato real.
# Al encontrar un 2 en el archivo, se tiene la certeza de que ahí
# terminó una fila y empieza la siguiente.
SEPARADOR = 2

# Cada fila ocupa en el archivo: sus 100.000 datos + 1 byte de separador.
# Este valor se usa después (en mostrar_matriz.py) para saber en qué
# byte exacto empieza cada fila, sin tener que leer el archivo desde
# el inicio.
ancho_fila_total = n_cols + 1  # 100.001 bytes por fila


def crear_matriz():
    """
    Genera la matriz y la escribe en disco, bloque por bloque.

    SOLUCIÓN AL CONSUMO EXCESIVO DE RAM:
    En vez de crear un arreglo con las 100.000 x 100.000 = 10.000 millones
    de celdas de una sola vez (lo que ocuparía varios GB de RAM y podría
    congelar el computador), se genera solo un bloque de 'chunk' filas
    a la vez. Ese bloque se escribe inmediatamente a disco y se descarta
    de la memoria antes de generar el siguiente. Así, en cualquier
    momento del proceso, solo hay en RAM una pequeña fracción de la
    matriz completa (unos pocos MB), nunca los 10 GB totales.

    SOLUCIÓN A LA ESCRITURA LENTA A DISCO:
    Escribir cada bloque de 1000 filas es UNA operación grande de
    escritura, en vez de 1000 (o peor, 100.000.000) operaciones
    pequeñas. Cada operación de escritura en disco tiene un costo fijo
    ("overhead"); agrupar los datos en bloques grandes reduce
    drásticamente ese costo acumulado y acelera todo el proceso.
    """
    print("Creando matriz en disco...")
    inicio = time.time()

    # "wb" = write binary -> abrimos el archivo para escritura binaria
    with open(filename, "wb") as f:

        # Recorremos la matriz de a "chunk" filas (0, 1000, 2000, ...)
        for i in range(0, n_filas, chunk):

            # Por si la última tanda tiene menos de 1000 filas restantes
            filas_generadas = min(chunk, n_filas - i)

            # Generamos de golpe un bloque de filas con valores 0 o 1.
            # np.random.randint es vectorizado (rápido), muy distinto
            # a generar cada celda con un bucle de Python puro.
            bloque = np.random.randint(
                0, 2, size=(filas_generadas, n_cols), dtype=np.uint8
            )

            # Escribimos cada fila del bloque, seguida de su separador
            for fila in bloque:
                f.write(fila.tobytes())        # los 100.000 datos de la fila
                f.write(bytes([SEPARADOR]))    # el separador -> fin de fila

            # Progreso: mostramos cada 10.000 filas cuánto llevamos y
            # cuánto pesa el archivo hasta el momento (evidencia de que
            # se está escribiendo en disco, no acumulando en RAM)
            if i % 10000 == 0:
                tam_mb = os.path.getsize(filename) / 1e6 if os.path.exists(filename) else 0
                print(f"Filas {i}/{n_filas} | Tiempo: {time.time()-inicio:.1f}s | Disco: {tam_mb:.1f} MB")

    tiempo_total = time.time() - inicio
    tamano_final_gb = os.path.getsize(filename) / 1e9

    print(f"\n¡Matriz creada en {tiempo_total:.1f} segundos!")
    print(f"Archivo: {filename}")
    print(f"Tamaño final en disco: {tamano_final_gb:.2f} GB")
    print(f"Total de datos: {n_filas * n_cols:,}")


# PUNTO DE ENTRADA

if __name__ == "__main__":
    crear_matriz()