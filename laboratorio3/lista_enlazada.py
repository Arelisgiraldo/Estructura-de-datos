# Lista enlazada
# Cada estudiante vive en un "nodo" que apunta al siguiente.
# Cada dato es un dict: {"id", "nombre", "edad", "promedio"}.
# Para buscar hay que recorrer nodo por nodo desde el inicio -> O(n)

class Nodo:
    def __init__(self, dato):
        self.dato = dato          # el estudiante (dict con id, nombre, edad y promedio)
        self.siguiente = None     # puntero al siguiente nodo (None = no hay más)


class Lista:
    def __init__(self):
        self.head = None          # primer nodo de la lista (vacía al inicio)

    def insertar(self, dato):
        # Inserta siempre al PRINCIPIO -> O(1), no hay que recorrer nada
        n = Nodo(dato)
        n.siguiente = self.head
        self.head = n

    def buscar(self, id):
        # Recorre desde head hasta encontrar el id o llegar al final -> O(n)
        actual = self.head
        while actual:
            if actual.dato["id"] == id:
                return actual.dato
            actual = actual.siguiente
        return None

    def listar_en_orden(self):
        # La lista NO queda ordenada por sí sola (se inserta al inicio),
        # así que hay que recolectar todo y ordenar al final.
        r, actual = [], self.head
        while actual:
            r.append(actual.dato)
            actual = actual.siguiente
        return sorted(r, key=lambda e: e["id"])