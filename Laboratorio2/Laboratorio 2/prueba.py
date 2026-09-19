"""
LABORATORIO 2 - Prueba del Arbol de Merkle
Estudiante: Arelis Giraldo
Este script usa la implementacion de merkle_tree.py para construir un
arbol con transacciones de ejemplo, generar la prueba de inclusion de
una de ellas y verificar que dicha prueba funciona tanto con el dato
verdadero como con un dato alterado.
"""

from merkle_tree import MerkleTree, verificar_prueba, hash_hoja, hash_padre


def recalcular_raiz(dato, prueba):
    """Sube por el arbol paso a paso, mostrando el hash que se obtiene en cada paso."""
    actual = hash_hoja(dato)
    print("  hash del dato       :", actual.hex()[:16] + "...")
    numero = 1
    for hermano, lado in prueba:
        if lado == "izq":
            actual = hash_padre(hermano, actual)
        else:
            actual = hash_padre(actual, hermano)
        print(f"  paso {numero} (hermano {lado}):", actual.hex()[:16] + "...")
        numero = numero + 1
    return actual


def main():
    transacciones = [
        "Tx1: Ana -> Bruno : 10 monedas",
        "Tx2: Bruno -> Carla : 4 monedas",
        "Tx3: Carla -> Diego : 2 monedas",
        "Tx4: Diego -> Ana : 7 monedas",
        "Tx5: Ana -> Elena : 1 moneda",
    ]

    print("1. Transacciones")
    for t in transacciones:
        print("  ", t)

    print("\n2. Arbol de Merkle")
    arbol = MerkleTree(transacciones)
    print(arbol.a_ascii())
    print("\nMerkle Root:", arbol.raiz.hex())

    print("\n3. Modificar una transaccion")
    modificadas = list(transacciones)
    modificadas[1] = "Tx2: Bruno -> Carla : 400 monedas"  # dato alterado
    arbol_mod = MerkleTree(modificadas)
    print("Raiz original  :", arbol.raiz.hex())
    print("Raiz modificada:", arbol_mod.raiz.hex())
    print("¿La raiz cambio? ->", arbol.raiz != arbol_mod.raiz)

    # Prueba de inclusion de la transaccion 3 (indice 2, porque se cuenta desde 0)
    indice = 2
    prueba = arbol.prueba_de_inclusion(indice)
    raiz_esperada = arbol.raiz

    print("\n4. Prueba de inclusion de la transaccion 3")
    print("Hashes hermanos que forman la prueba:")
    for i, (h, lado) in enumerate(prueba, 1):
        print(f"  hermano {i} (a la {lado}): {h.hex()[:16]}...")
    print("Raiz esperada:", raiz_esperada.hex())

    print("\n4.1 Verificacion con el DATO VERDADERO")
    dato_verdadero = transacciones[indice]
    print("Dato a verificar:", dato_verdadero)
    raiz_calculada = recalcular_raiz(dato_verdadero, prueba)
    print("  raiz calculada      :", raiz_calculada.hex())
    print("  raiz esperada       :", raiz_esperada.hex())
    print("  ¿Son iguales?       :", raiz_calculada == raiz_esperada)
    if verificar_prueba(dato_verdadero, prueba, raiz_esperada):
        print("RESULTADO: VALIDA (la Tx3 si pertenece al arbol)")
    else:
        print("RESULTADO: INVALIDA")

    print("\n5. Verificacion con un dato incorrecto")
    print("Se usa la MISMA prueba y la MISMA raiz esperada, pero con otro dato.")
    dato_falso = "Tx3: Carla -> Diego : 2000 monedas"
    print("Dato verdadero:", dato_verdadero)
    print("Dato falso    :", dato_falso)
    raiz_calculada_falsa = recalcular_raiz(dato_falso, prueba)
    print("  raiz calculada      :", raiz_calculada_falsa.hex())
    print("  raiz esperada       :", raiz_esperada.hex())
    print("  ¿Son iguales?       :", raiz_calculada_falsa == raiz_esperada)
    if verificar_prueba(dato_falso, prueba, raiz_esperada):
        print("RESULTADO: VALIDA")
    else:
        print("RESULTADO: INVALIDA (el dato falso no pertenece al arbol, como se esperaba)")


if __name__ == "__main__":
    main()