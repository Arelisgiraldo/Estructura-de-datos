# Árbol Binario de Búsqueda (ABB)
# Cada nodo tiene un hijo izquierdo (valores menores) y uno derecho (valores mayores).
# Eso permite descartar una parte del árbol en cada comparación: si los ids llegan
# en orden aleatorio, en promedio la búsqueda es O(log n).
#
# ADVERTENCIA: si insertas los ids ya ordenados (1, 2, 3...), el árbol se
# desbalancea y se vuelve una fila larga hacia un lado -> se comporta como
# una lista, O(n). Por eso el B+ existe: se auto-balancea sin importar el orden.

class NodoABB:
    def __init__(self, dato):
        self.dato = dato
        self.izquierda = None
        self.derecha = None


class ArbolABB:
    def __init__(self):
        self.raiz = None

    def insertar(self, dato):
        # Iterativo (con while), no recursivo: con 10,000 ids ordenados,
        # una versión recursiva revienta el límite de recursión de Python.
        if not self.raiz:
            self.raiz = NodoABB(dato)
            return
        actual = self.raiz
        while True:
            if dato["id"] < actual.dato["id"]:
                if not actual.izquierda:
                    actual.izquierda = NodoABB(dato); return
                actual = actual.izquierda
            else:
                if not actual.derecha:
                    actual.derecha = NodoABB(dato); return
                actual = actual.derecha

    def buscar(self, id):
        # Baja por el árbol comparando en cada nodo: menor -> izquierda,
        # mayor o igual -> derecha, hasta encontrarlo o llegar a None.
        actual = self.raiz
        while actual:
            if id == actual.dato["id"]:
                return actual.dato
            actual = actual.izquierda if id < actual.dato["id"] else actual.derecha
        return None

    def listar_en_orden(self):
        # Recorrido INORDEN (izquierda -> nodo -> derecha): en un ABB esto
        # devuelve los datos ya ordenados por id, sin necesidad de sort -> O(n).
        # Iterativo con una pila propia, por el mismo motivo que insertar:
        # con ids ordenados el árbol puede tener altura n y la recursión reventaría.
        resultado, pila, actual = [], [], self.raiz
        while pila or actual:
            while actual:                 # bajar todo a la izquierda
                pila.append(actual)
                actual = actual.izquierda
            actual = pila.pop()           # visitar el nodo
            resultado.append(actual.dato)
            actual = actual.derecha       # seguir por la derecha
        return resultado

    def altura(self):
        # Número de niveles del árbol (árbol vacío = 0, solo raíz = 1).
        # Balanceado: ~log2(n). Con ids ordenados: n (una fila larga).
        # Se recorre por niveles (BFS) para no usar recursión.
        if not self.raiz:
            return 0
        nivel, h = [self.raiz], 0
        while nivel:
            h += 1
            siguiente = []
            for nodo in nivel:
                if nodo.izquierda: siguiente.append(nodo.izquierda)
                if nodo.derecha:   siguiente.append(nodo.derecha)
            nivel = siguiente
        return h