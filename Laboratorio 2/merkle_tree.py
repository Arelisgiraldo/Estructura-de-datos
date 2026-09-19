"""
LABORATORIO 2 - Arbol de Merkle
Estudiante: Arelis Giraldo
Este script construye un arbol de Merkle a partir de una lista de
transacciones y permite verificar si una transaccion especifica
pertenece al arbol, sin necesidad de recorrerlo completo cada vez.

Un arbol de Merkle resuelve el problema de:
  1. Verificar la integridad de muchas transacciones con un solo hash (la raiz)
  2. Detectar si una sola transaccion fue alterada, sin comparar todo el conjunto
  3. Generar, para una transaccion puntual, una prueba corta de que
     pertenece al conjunto, sin necesitar todas las demas transacciones
"""

import hashlib

# CONFIGURACION GENERAL

# Etiquetas usadas para marcar de que lado queda el hash "hermano" al
# combinarse con el hash actual durante la verificacion. Se definen aqui
# para no repetir los strings sueltos por todo el codigo.
LADO_IZQUIERDA = "izq"
LADO_DERECHA = "der"


def hash_hoja(dato):
    """
    Calcula el hash de una transaccion individual (una "hoja" del arbol).

    SOLUCION PARA TRABAJAR CON TRANSACCIONES DE TAMANO VARIABLE:
    En vez de comparar las transacciones como texto plano (lento y con
    tamanos distintos), se convierte cada una a un hash SHA-256 de
    tamano fijo (32 bytes). Asi, sin importar que tan larga sea la
    transaccion original, todo el arbol trabaja con bloques uniformes.
    """
    return hashlib.sha256(dato.encode("utf-8")).digest()


def hash_padre(izquierda, derecha):
    """
    Combina el hash de dos nodos hijos para obtener el hash del padre.

    El orden importa: concatenar (izquierda + derecha) da un resultado
    distinto a (derecha + izquierda). Por eso la prueba de inclusion
    siempre debe guardar cual hash iba a cada lado.
    """
    return hashlib.sha256(izquierda + derecha).digest()


class MerkleTree:
    """
    Representa el arbol de Merkle completo, construido a partir de una
    lista de transacciones.

    SOLUCION PARA VERIFICAR UNA TRANSACCION SIN GUARDAR TODO EL ARBOL:
    En vez de quedarse solo con la raiz y descartar el resto, se
    almacenan tambien los niveles intermedios (self.niveles). Esto
    permite despues generar, para cualquier transaccion, la lista
    minima de hashes "hermanos" necesarios para reconstruir la raiz
    (la prueba de inclusion), en lugar de tener que recorrer todas
    las transacciones cada vez que se quiera verificar una sola.
    """

    def __init__(self, transacciones):
        if len(transacciones) == 0:
            raise ValueError("Se necesita al menos una transaccion")

        self.transacciones = transacciones
        self.niveles = []  # niveles[0] = hojas, niveles[-1] = [raiz]

        # Nivel 0: se hashea cada transaccion por separado
        nivel = []
        for tx in transacciones:
            nivel.append(hash_hoja(tx))
        self.niveles.append(nivel)

        # SOLUCION PARA NUMERO IMPAR DE ELEMENTOS:
        # El arbol necesita combinar los hashes de dos en dos. Si un
        # nivel queda con una cantidad impar de nodos, se duplica el
        # ultimo para completar el par, sin inventar una transaccion
        # nueva (el duplicado no representa un dato distinto).
        while len(nivel) > 1:
            if len(nivel) % 2 == 1:
                nivel = nivel + [nivel[-1]]
                self.niveles[-1] = nivel

            nivel_siguiente = []
            for i in range(0, len(nivel), 2):
                nivel_siguiente.append(hash_padre(nivel[i], nivel[i + 1]))

            self.niveles.append(nivel_siguiente)
            nivel = nivel_siguiente

        self.raiz = nivel[0]

    def prueba_de_inclusion(self, indice):
        """
        Genera la prueba de inclusion de la transaccion ubicada en
        `indice`: la lista minima de hashes "hermanos" necesarios para
        reconstruir la raiz partiendo unicamente de esa transaccion.

        Devuelve una lista de tuplas (hash_hermano, lado), donde "lado"
        indica si ese hermano debe ir a la izquierda o a la derecha del
        hash actual al combinarse en cada nivel.
        """
        if indice < 0 or indice >= len(self.transacciones):
            raise IndexError("Indice de transaccion fuera de rango")

        prueba = []
        i = indice

        # Se recorre cada nivel menos el ultimo (la raiz), porque la
        # raiz ya no tiene un hermano con el que combinarse.
        for nivel_num in range(len(self.niveles) - 1):
            nivel = self.niveles[nivel_num]

            if i % 2 == 0:
                indice_hermano = i + 1
                lado = LADO_DERECHA
            else:
                indice_hermano = i - 1
                lado = LADO_IZQUIERDA

            prueba.append((nivel[indice_hermano], lado))
            i = i // 2

        return prueba

    def a_ascii(self):
        """
        Devuelve una representacion en texto del arbol, nivel por nivel,
        mostrando solo los primeros caracteres de cada hash para que sea
        legible en consola.
        """
        texto = ""
        for nivel_num in range(len(self.niveles) - 1, -1, -1):
            texto = texto + f"Nivel {nivel_num}: "
            for h in self.niveles[nivel_num]:
                texto = texto + h.hex()[:8] + "...  "
            texto = texto + "\n"
        return texto


def verificar_prueba(dato, prueba, raiz_esperada):
    """
    Verifica si una transaccion pertenece al arbol, usando solo su
    prueba de inclusion y la raiz esperada.

    SOLUCION PARA NO NECESITAR EL ARBOL COMPLETO:
    En vez de reconstruir todo el arbol para comprobar una sola
    transaccion, se parte del hash de esa transaccion y se sube nivel
    por nivel combinandolo con cada hermano de la prueba, hasta llegar
    a un unico hash final. Si ese hash coincide con la raiz esperada,
    la transaccion pertenece al arbol; si el dato fue alterado o la
    prueba no corresponde, el resultado final sera distinto.
    """
    actual = hash_hoja(dato)

    for hermano, lado in prueba:
        if lado == LADO_IZQUIERDA:
            actual = hash_padre(hermano, actual)
        else:
            actual = hash_padre(actual, hermano)

    return actual == raiz_esperada


# PUNTO DE ENTRADA

if __name__ == "__main__":
    transacciones = [f"tx{i}" for i in range(7)]

    arbol = MerkleTree(transacciones)
    print(arbol.a_ascii())
    print("Merkle Root:", arbol.raiz.hex())

    indice = 3
    prueba = arbol.prueba_de_inclusion(indice)
    print(f"\nPrueba de inclusion para '{transacciones[indice]}':")
    for h, lado in prueba:
        print(f"  ({lado}) {h.hex()[:16]}...")

    es_valida = verificar_prueba(transacciones[indice], prueba, arbol.raiz)
    print(f"\n¿La transaccion '{transacciones[indice]}' pertenece al arbol? {es_valida}")

    es_valida_falsa = verificar_prueba("tx_falsa", prueba, arbol.raiz)
    print(f"¿Una transaccion falsa pasa la verificacion? {es_valida_falsa}")