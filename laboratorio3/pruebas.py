# pruebas.py
# Comprueba que las 3 estructuras funcionan bien ANTES de medir tiempos.
#
# "assert" revisa que algo sea cierto; si no lo es, el programa se detiene con error.

import random

from lista_enlazada import Lista
from arbol_abb import ArbolABB
from arbol_bplus import ArbolBPlus

ESTRUCTURAS = [("Lista", Lista), ("ABB", ArbolABB), ("B+", ArbolBPlus)]

for N in [1, 10, 1000, 5000]:
    for orden in ["aleatorio", "ordenado"]:
        ids = list(range(1, N + 1))
        if orden == "aleatorio":
            random.shuffle(ids)

        for nombre, Clase in ESTRUCTURAS:
            estructura = Clase()
            for i in ids:
                estructura.insertar({"id": i, "nombre": "Prueba"})

            # 1) Buscar: encuentra a todos los estudiantes
            for i in ids:
                assert estructura.buscar(i)["id"] == i

            # 2) Buscar un id que no existe devuelve None
            assert estructura.buscar(N + 1) is None

            # 3) Listar: salen todos, en orden 1, 2, 3, ..., N
            listado = estructura.listar_en_orden()
            assert [e["id"] for e in listado] == list(range(1, N + 1))

            if nombre == "Lista":
                print(f"OK  {nombre:5} N={N:5} {orden}")
            else:
                print(f"OK  {nombre:5} N={N:5} {orden:9}  altura = {estructura.altura()}")

print("\nTodas las pruebas pasaron.")
