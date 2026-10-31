import os
import random
import unittest
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from Quadtreetree import (generar_puntos, distancia, fuerza_bruta_rango,
                          fuerza_bruta_vecino, Caja, crear_arbol)

DATOS = generar_puntos(10000)
ARBOL = crear_arbol(DATOS)


# Pruebas unitarias: el árbol debe dar lo mismo que la fuerza bruta
class PruebasQuadtree(unittest.TestCase):

    def test_distancia(self):
        self.assertEqual(distancia((0, 0), (3, 4)), 5.0)

    def test_caja(self):
        caja = Caja(0, 0, 10, 4)
        self.assertTrue(caja.contiene((3, 3)))
        self.assertFalse(caja.contiene((11, 1)))
        self.assertEqual(caja.distancia_minima((13, 8)), 5.0)
        self.assertEqual(caja.distancia_minima((3, 3)), 0.0)

    def test_no_se_pierden_puntos(self):
        self.assertEqual(ARBOL.contar_puntos(), 10000)

    def test_punto_fuera_del_mapa(self):
        self.assertFalse(ARBOL.insertar((-50, -50)))

    def test_puntos_repetidos(self):
        arbol = crear_arbol([(3, 3)] * 50, tamano=10)
        self.assertEqual(arbol.contar_puntos(), 50)

    def test_radio_igual_a_fuerza_bruta(self):
        random.seed(7)
        for _ in range(100):
            centro = (random.uniform(0, 10000), random.uniform(0, 10000))
            self.assertCountEqual(ARBOL.buscar_en_radio(centro, 500),
                                  fuerza_bruta_rango(DATOS, centro, 500))

    def test_vecino_igual_a_fuerza_bruta(self):
        random.seed(11)
        for _ in range(100):
            objetivo = (random.uniform(0, 10000), random.uniform(0, 10000))
            self.assertAlmostEqual(ARBOL.vecino_mas_cercano(objetivo)[1],
                                   fuerza_bruta_vecino(DATOS, objetivo)[1])

    def test_vecinos_ordenados(self):
        vecinos = ARBOL.vecinos_ordenados((5000, 5000), 500)
        distancias = [distancia(p, (5000, 5000)) for p in vecinos]
        self.assertEqual(distancias, sorted(distancias))


# Verificación visual: dibuja los puntos, el punto consultado y los encontrados
def graficar(nombre, titulo, centro, encontrados, zoom, radio=None, lineas=False):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter([p[0] for p in DATOS], [p[1] for p in DATOS], s=4, color="lightgray", label="Otros puntos")
    ax.scatter([p[0] for p in encontrados], [p[1] for p in encontrados], s=25, color="blue", label="Encontrados")
    ax.plot(centro[0], centro[1], marker="*", markersize=18, color="red", label="Punto consultado")
    if radio:
        ax.add_patch(Circle(centro, radio, fill=False, edgecolor="red", linewidth=2))
    if lineas:
        for p in encontrados:
            ax.plot([centro[0], p[0]], [centro[1], p[1]], color="blue")
    ax.set_xlim(centro[0] - zoom, centro[0] + zoom)
    ax.set_ylim(centro[1] - zoom, centro[1] + zoom)
    ax.set_aspect("equal")
    ax.set_title(titulo)
    ax.set_xlabel("x (metros)")
    ax.set_ylabel("y (metros)")
    ax.legend(loc="upper right")
    fig.savefig("graficas/" + nombre, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generar_graficas():
    os.makedirs("graficas", exist_ok=True)

    centro = (5000, 5000)
    en_radio = ARBOL.buscar_en_radio(centro, 500)
    graficar("radio.png", "Puntos a 500 m o menos: " + str(len(en_radio)),
             centro, en_radio, 800, radio=500)

    objetivo = (3200, 6800)
    cinco_cercanos = ARBOL.vecinos_ordenados(objetivo, 500)[:5]
    graficar("vecinos.png", "Los 5 vecinos más cercanos", objetivo, cinco_cercanos, 150, lineas=True)

    print("Gráficas guardadas: graficas/radio.png y graficas/vecinos.png")


if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
    generar_graficas()