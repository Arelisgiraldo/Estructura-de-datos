# Laboratorio 1 - Matriz de 100.000 x 100.000 en disco

Estudiante: Arelis Giraldo 

## De qué se trata

El ejercicio consiste en crear una matriz de 100.000 x 100.000 (osea 10.000
millones de datos) y guardarla en el disco duro, sin que el computador se
quede sin memoria RAM ni se demore una eternidad escribiendo. Al final hay
que poder mostrar que la matriz sí quedó bien creada.

## Qué hay en este repositorio

- **crear_matriz.py**: es el script que arma la matriz y la guarda en disco.
  Se corre una sola vez.
- **mostrar_matriz.py**: sirve para revisar una fila específica de la matriz
  ya creada (por ejemplo si piden "muéstrame la fila 10000"). Además
  comprueba que esa fila sea la correcta y guarda el resultado en un .txt.
- **matriz_100k.dat**: es el archivo que se genera al correr crear_matriz.py.
  No está subido al repo porque pesa como 10 GB, pero se genera solo
  al correr el script.
- Los archivos **verificacion_fila_X.txt** son evidencia de las pruebas que
  hice, mostrando el contenido de distintas filas.

## Cómo correrlo

Necesitas tener Python y numpy instalado (`pip install numpy`).

Primero se corre:
```
python crear_matriz.py
```
Esto tarda un rato (varios minutos) porque va escribiendo la matriz de a
poquitos, mostrando el progreso en la consola.

Después, para ver una fila:
```
python mostrar_matriz.py
```
Te pregunta qué fila quieres ver y te muestra la info en pantalla, además
de guardarla en un archivo de texto.

## Cómo se resolvió cada problema

**Que no se llene la RAM:** en vez de crear la matriz completa de una, el
código la va armando en bloques de 1000 filas. Cada bloque se escribe al
disco y se bota de la memoria antes de seguir con el siguiente, entonces
en ningún momento está toda la matriz cargada en RAM.

**Que la escritura no sea lenta:** en vez de escribir dato por dato (lo
cual sería carísimo en tiempo, porque son 10.000 millones de operaciones),
se escribe de a bloques de 1000 filas, así hay muchas menos operaciones
de escritura al disco.

**Que esté organizado:** cada fila queda guardada con un tamaño fijo: los
100.000 datos más un byte extra que uso como "separador" (el número 2,
que nunca se confunde con los datos porque estos son solo 0 o 1). Así sé
exactamente dónde empieza y termina cada fila.

**Que la lectura sea rápida:** para mostrar una fila no hay que leer todo
el archivo desde el principio. Como todas las filas pesan lo mismo, calculo
matemáticamente en qué byte empieza la fila que me piden (fila x 100.001) y
salto directo ahí con `seek()`. Por eso da lo mismo pedir la fila 0 o la
fila 99.999, se demora prácticamente lo mismo en leerla.

## Cómo compruebo que la fila es la correcta

Cuando leo una fila, después de sus 100.000 datos leo un byte más. Si ese
byte es el separador (2), significa que el corte cayó exactamente donde
debía y que esos datos sí son de la fila que pedí y no de otra. Esto queda
mostrado en consola y guardado en el .txt de verificación.