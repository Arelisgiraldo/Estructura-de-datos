import random
import math


# 1. Generar los puntos de entrega (en metros, ciudad de 10 km x 10 km)
def generar_puntos(n, tamano=10000, semilla=42):
    random.seed(semilla)
    puntos = []
    for _ in range(n):
        puntos.append((random.uniform(0, tamano), random.uniform(0, tamano)))
    return puntos


# 2. Distancia en línea recta (Pitágoras)
def distancia(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# 3. Fuerza bruta: revisa TODOS los puntos
def fuerza_bruta_rango(puntos, centro, radio):
    encontrados = []
    for punto in puntos:
        if distancia(punto, centro) <= radio:
            encontrados.append(punto)
    return encontrados


def fuerza_bruta_vecino(puntos, objetivo):
    mejor_punto = None
    mejor_distancia = float("inf")
    for punto in puntos:
        d = distancia(punto, objetivo)
        if d < mejor_distancia:
            mejor_punto = punto
            mejor_distancia = d
    return mejor_punto, mejor_distancia


# 4. Caja: un rectángulo del mapa
class Caja:

    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def contiene(self, punto):
        x, y = punto
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

    def distancia_minima(self, punto):
        # El punto de la caja más cercano: se "aprieta" x e y dentro de la caja
        x = max(self.x_min, min(punto[0], self.x_max))
        y = max(self.y_min, min(punto[1], self.y_max))
        return distancia(punto, (x, y))

    def partir(self):
        # Devuelve las 4 cajas hijas: suroeste, sureste, noroeste, noreste
        x_medio = (self.x_min + self.x_max) / 2
        y_medio = (self.y_min + self.y_max) / 2
        return [
            Caja(self.x_min, self.y_min, x_medio, y_medio),
            Caja(x_medio, self.y_min, self.x_max, y_medio),
            Caja(self.x_min, y_medio, x_medio, self.y_max),
            Caja(x_medio, y_medio, self.x_max, self.y_max),
        ]


# 5. Nodo del Quadtree
class Nodo:

    def __init__(self, caja, capacidad=4, profundidad=0):
        self.caja = caja
        self.capacidad = capacidad
        self.profundidad = profundidad
        self.puntos = []
        self.hijos = None

    def es_hoja(self):
        return self.hijos is None

    def subdividir(self):
        self.hijos = []
        for pedazo in self.caja.partir():
            self.hijos.append(Nodo(pedazo, self.capacidad, self.profundidad + 1))
        # Los puntos que tenía pasan a sus hijos
        for punto in self.puntos:
            self.insertar_en_hijos(punto)
        self.puntos = []

    def insertar_en_hijos(self, punto):
        # Se guarda en el primer hijo que lo acepte (así nunca queda duplicado)
        for hijo in self.hijos:
            if hijo.insertar(punto):
                return True
        return False

    def insertar(self, punto):
        if not self.caja.contiene(punto):
            return False
        if self.es_hoja():
            # Si hay espacio, o ya se está muy profundo (puntos repetidos), se guarda aquí
            if len(self.puntos) < self.capacidad or self.profundidad >= 20:
                self.puntos.append(punto)
                return True
            self.subdividir()
        return self.insertar_en_hijos(punto)

    def contar_puntos(self):
        if self.es_hoja():
            return len(self.puntos)
        total = 0
        for hijo in self.hijos:
            total += hijo.contar_puntos()
        return total

    # Búsqueda por radio (Range Search)
    def buscar_en_radio(self, centro, radio, resultado=None):
        if resultado is None:
            resultado = []
        # Poda: si la caja no toca el círculo, no se revisa nada de ella
        if self.caja.distancia_minima(centro) > radio:
            return resultado
        if self.es_hoja():
            for punto in self.puntos:
                if distancia(punto, centro) <= radio:
                    resultado.append(punto)
        else:
            for hijo in self.hijos:
                hijo.buscar_en_radio(centro, radio, resultado)
        return resultado

    # Vecinos dentro del radio, ordenados del más cercano al más lejano
    def vecinos_ordenados(self, centro, radio):
        vecinos = self.buscar_en_radio(centro, radio)
        return sorted(vecinos, key=lambda punto: distancia(punto, centro))

    # Vecino más cercano
    def vecino_mas_cercano(self, objetivo, mejor=None):
        if mejor is None:
            mejor = [None, float("inf")]  # [mejor punto, mejor distancia]
        # Poda: si la caja está más lejos que el récord, no puede mejorarlo
        if self.caja.distancia_minima(objetivo) >= mejor[1]:
            return mejor
        if self.es_hoja():
            for punto in self.puntos:
                d = distancia(punto, objetivo)
                if d < mejor[1]:
                    mejor[0] = punto
                    mejor[1] = d
        else:
            # Primero los hijos más cercanos: así el récord baja rápido
            hijos = sorted(self.hijos, key=lambda h: h.caja.distancia_minima(objetivo))
            for hijo in hijos:
                hijo.vecino_mas_cercano(objetivo, mejor)
        return mejor


# 6. Crear el árbol con todos los puntos
def crear_arbol(puntos, tamano=10000, capacidad=4):
    arbol = Nodo(Caja(0, 0, tamano, tamano), capacidad)
    for punto in puntos:
        arbol.insertar(punto)
    return arbol


if __name__ == "__main__":
    datos = generar_puntos(10000)
    arbol = crear_arbol(datos)
    print("Puntos en el árbol:", arbol.contar_puntos())
    print("A 500 m de (5000, 5000):", len(arbol.buscar_en_radio((5000, 5000), 500)))
    print("Más cercano a (5000, 5000):", arbol.vecino_mas_cercano((5000, 5000)))