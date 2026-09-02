"""
LABORATORIO 1 - Mostrar / verificar la matriz creada en disco
Estudiante: Arelis Giraldo
Este script lee y muestra una fila específica de la matriz generada por
crear_matriz.py, sin necesidad de cargar la matriz completa en memoria
ni recorrer el archivo desde el principio.

También verifica que la fila leída es efectivamente la que se pidió,
comprobando que justo después de sus 100.000 datos aparece el byte
separador esperado.
"""

import os
import time

# CONFIGURACIÓN (debe coincidir exactamente con crear_matriz.py)

filename = "matriz_100k.dat"
n_cols = 100_000
SEPARADOR = 2
ancho_fila_total = n_cols + 1  # 100.000 datos + 1 byte separador


def mostrar_fila(fila_pedida):
    """
    Lee y muestra una fila específica de la matriz, y guarda el
    resultado completo en un archivo .txt.

    SOLUCIÓN A LA OPTIMIZACIÓN DE LECTURA (y por qué no consume RAM):
    En vez de abrir el archivo y leerlo desde el principio hasta llegar
    a la fila pedida (lo que sería lento y además obligaría a "pasar
    por" -y cargar en memoria en algún momento- todas las filas
    anteriores), se calcula matemáticamente el byte exacto donde
    empieza esa fila:

        offset = fila_pedida * ancho_fila_total

    Como todas las filas tienen el mismo ancho fijo (100.001 bytes:
    100.000 datos + 1 separador), no hace falta ningún tipo de
    "búsqueda": basta con multiplicar el número de fila por el ancho
    fijo para saber su posición exacta.

    Con f.seek(offset) saltamos directo a esa posición del archivo en
    disco (como ir a una página específica de un libro sabiendo el
    número de página), y con f.read() leemos ÚNICAMENTE los bytes de
    esa fila. Nunca se leen ni se cargan en memoria las demás filas,
    sin importar si la fila pedida es la 0 o la 99.999 -el tiempo de
    acceso es prácticamente el mismo en ambos casos, lo cual se puede
    comprobar cronometrando la lectura (ver el tiempo impreso al final).

    VERIFICACIÓN DE QUE ES LA FILA CORRECTA:
    Justo después de leer los 100.000 datos, se lee 1 byte más. Como
    cada fila fue escrita seguida de un separador (el número 2, que
    nunca es un dato real porque los datos son solo 0 o 1), si ese
    byte leído es efectivamente un 2, se confirma que el corte cayó
    exactamente donde debía: al final de la fila pedida, y no en medio
    de otra fila por un error de cálculo del offset.
    """

    if not os.path.exists(filename):
        print("No se encontró el archivo. Primero corre crear_matriz.py")
        return

    # Calculamos el byte exacto donde empieza la fila pedida
    offset = fila_pedida * ancho_fila_total

    inicio = time.time()

    # "rb" = read binary -> abrimos el archivo para lectura binaria
    with open(filename, "rb") as f:
        f.seek(offset)                 # saltamos directo a la posición exacta
        datos = f.read(n_cols)         # leemos SOLO los 100.000 datos de esta fila
        separador_leido = f.read(1)    # leemos el byte siguiente (debe ser el separador)

    tiempo_lectura = (time.time() - inicio) * 1000  # en milisegundos

    es_correcto = (len(separador_leido) == 1 and separador_leido[0] == SEPARADOR)

    # ---------- Mostramos un resumen en consola ----------
    print(f"\nFila verificada: {fila_pedida}")
    print(f"Byte de inicio (offset): {offset}")
    print(f"Cantidad de datos leídos: {len(datos)}")
    print(f"Byte separador encontrado: {separador_leido[0] if separador_leido else 'N/A'}")
    print(f"¿Es el separador correcto? (¿la fila está bien delimitada?): {es_correcto}")
    print(f"Tiempo de lectura: {tiempo_lectura:.3f} ms")
    print("(Nota: este tiempo es prácticamente el mismo sin importar si se pide")
    print(" la fila 0 o la fila 99999, porque no se recorre el archivo, se salta directo)")

    # ---------- Guardamos el resultado completo en un .txt ----------
    # Cada valor de la fila queda en su propia línea, para poder ver
    # claramente los 100.000 datos, uno debajo del otro.
    nombre_txt = f"verificacion_fila_{fila_pedida}.txt"
    with open(nombre_txt, "w") as f_txt:
        f_txt.write(f"Fila verificada: {fila_pedida}\n")
        f_txt.write(f"Byte de inicio (offset): {offset}\n")
        f_txt.write(f"Cantidad de datos en la fila: {len(datos)}\n")
        f_txt.write(f"Byte separador encontrado: {separador_leido[0] if separador_leido else 'N/A'}\n")
        f_txt.write(f"¿Es el separador correcto?: {es_correcto}\n")
        f_txt.write(f"Tiempo de lectura: {tiempo_lectura:.3f} ms\n")
        f_txt.write("\n--- Datos de la fila (uno por línea) ---\n")
        for valor in datos:
            f_txt.write(f"{valor}\n")

    print(f"\n Resultado completo guardado en: {nombre_txt}")


# PUNTO DE ENTRADA

if __name__ == "__main__":
    fila = int(input("¿Qué fila quieres ver/verificar? (0 a 99999): "))
    mostrar_fila(fila)