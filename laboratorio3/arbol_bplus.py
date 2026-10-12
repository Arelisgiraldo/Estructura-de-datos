# Árbol B+
# Diferencia clave con el ABB: los datos SOLO viven en las hojas (nodos de
# abajo). Los nodos de arriba solo tienen "claves guía" para saber hacia
# dónde bajar, y las hojas están conectadas entre sí en fila (bueno para
# recorrer rangos). Cuando un nodo se llena (ORDEN claves), se divide en
# dos y avisa al padre -> el árbol crece parejo por todos lados, por eso
# NO se desbalancea sin importar el orden de inserción (a diferencia del ABB).

ORDEN = 4  # un nodo se divide al llegar a ORDEN claves: cada nodo queda con máximo 3

class NodoBPlus:
    def __init__(self, hoja=True):
        self.hoja = hoja
        self.claves = []       # ids guardados en este nodo (guía u hoja)
        self.datos = []        # estudiantes reales -> solo lo usan las hojas
        self.hijos = []        # nodos hijos -> solo lo usan los nodos internos
        self.siguiente = None  # hoja siguiente en la fila -> solo lo usan las hojas
        self.padre = None      # para poder "avisar" hacia arriba al dividir


class ArbolBPlus:
    def __init__(self):
        self.raiz = NodoBPlus(hoja=True)   # empieza siendo una sola hoja vacía

    def buscar(self, id):
        # 1) bajar hasta la hoja donde debería estar el id
        # 2) revisar esa hoja en busca del id exacto
        hoja = self._encontrar_hoja(id)
        for i, clave in enumerate(hoja.claves):
            if clave == id:
                return hoja.datos[i]
        return None

    def _encontrar_hoja(self, id):
        # Baja desde la raíz: en cada nodo interno, compara el id contra
        # las claves guía para decidir por cuál hijo seguir.
        nodo = self.raiz
        while not nodo.hoja:
            i = 0
            while i < len(nodo.claves) and id >= nodo.claves[i]:
                i += 1
            nodo = nodo.hijos[i]
        return nodo

    def insertar(self, dato):
        # Encuentra la hoja correcta (según el id) e inserta ahí, ordenado.
        # Si la hoja se pasa de ORDEN claves, se divide en dos.
        id = dato["id"]
        hoja = self._encontrar_hoja(id)

        i = 0
        while i < len(hoja.claves) and hoja.claves[i] < id:
            i += 1
        hoja.claves.insert(i, id)
        hoja.datos.insert(i, dato)

        if len(hoja.claves) >= ORDEN:
            self._dividir(hoja)

    def _dividir(self, nodo):
        # Corta el nodo a la mitad. Si es hoja, las hojas resultantes se
        # quedan conectadas por "siguiente". Si es nodo interno, una clave
        # "sube" al padre para que sepa que ahora hay un hijo nuevo.
        medio = len(nodo.claves) // 2

        if nodo.hoja:
            nueva = NodoBPlus(hoja=True)
            nueva.claves = nodo.claves[medio:]
            nueva.datos = nodo.datos[medio:]
            nodo.claves = nodo.claves[:medio]
            nodo.datos = nodo.datos[:medio]
            nueva.siguiente = nodo.siguiente
            nodo.siguiente = nueva
            clave_subida = nueva.claves[0]
        else:
            nueva = NodoBPlus(hoja=False)
            clave_subida = nodo.claves[medio]
            nueva.claves = nodo.claves[medio + 1:]
            nueva.hijos = nodo.hijos[medio + 1:]
            for h in nueva.hijos:
                h.padre = nueva
            nodo.claves = nodo.claves[:medio]
            nodo.hijos = nodo.hijos[:medio + 1]

        if nodo.padre is None:
            # el nodo dividido era la raíz -> se crea una raíz nueva arriba
            nueva_raiz = NodoBPlus(hoja=False)
            nueva_raiz.claves = [clave_subida]
            nueva_raiz.hijos = [nodo, nueva]
            nodo.padre = nueva_raiz
            nueva.padre = nueva_raiz
            self.raiz = nueva_raiz
        else:
            # avisarle al padre: nueva clave guía + nuevo hijo
            padre = nodo.padre
            nueva.padre = padre
            idx = padre.hijos.index(nodo)
            padre.claves.insert(idx, clave_subida)
            padre.hijos.insert(idx + 1, nueva)
            if len(padre.claves) >= ORDEN:
                self._dividir(padre)   # el padre también se puede llenar y dividir

    def _hoja_mas_izquierda(self):
        # Baja siempre por el primer hijo hasta llegar a una hoja.
        nodo = self.raiz
        while not nodo.hoja:
            nodo = nodo.hijos[0]
        return nodo

    def listar_en_orden(self):
        # Aquí se aprovecha la fila de hojas: se empieza en la hoja de más a
        # la izquierda y se sigue el puntero "siguiente". Las hojas ya están
        # ordenadas, así que el resultado sale ordenado por id -> O(n).
        resultado, hoja = [], self._hoja_mas_izquierda()
        while hoja:
            resultado.extend(hoja.datos)
            hoja = hoja.siguiente
        return resultado

    def altura(self):
        # En un B+ todas las hojas están a la misma profundidad, así que basta
        # contar los niveles bajando por un solo camino. Crece ~log(n) siempre,
        # sin importar el orden de inserción.
        h, nodo = 1, self.raiz
        while not nodo.hoja:
            nodo = nodo.hijos[0]
            h += 1
        return h