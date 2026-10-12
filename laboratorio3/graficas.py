# graficas.py  -  PASO 5: gráficas y tablas
# Lee los resultados de los experimentos y genera:
#   graficas/grafica1_busqueda_vs_N.png   -> experimento 1 (variar N)
#   graficas/grafica2_tiempo_vs_M.png     -> experimento 2 (variar M)
#   graficas/grafica3_N_pequenos.png      -> experimento 3 (N pequeños), si ya se corrió
#   resultados/tablas.md                  -> tablas con promedio ± desviación estándar
# No mide nada: solo lee los CSV, así que se puede correr cuantas veces se quiera.
#
# Uso:  python graficas.py

import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")                     # guarda las imágenes sin abrir ventanas
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter

ESTRUCTURAS = ["Lista", "ABB", "B+"]
TAMANOS = [5000, 10000, 20000, 50000, 100000]
COLOR = {"Lista": "#2a78d6", "ABB": "#eb6834", "B+": "#1baf7a"}   # un color fijo por estructura
MARCA = {"Lista": "o", "ABB": "s", "B+": "^"}
GRIS = "#8a8985"

plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#b5b4ae", "axes.grid": True, "grid.color": "#e6e5e0",
    "xtick.color": "#52514e", "ytick.color": "#52514e", "legend.frameon": False,
    "savefig.dpi": 160,
})


def es(x, decimales=2):
    """Número en formato colombiano: 1.234,56"""
    texto = f"{x:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def agrupar(filas, campos_clave, campo_valor):
    """Junta los valores de las 10 repeticiones de cada caso: clave -> lista de valores."""
    grupos = {}
    for fila in filas:
        clave = tuple(fila[c] for c in campos_clave)
        if clave not in grupos:
            grupos[clave] = []
        if fila[campo_valor] != "":
            grupos[clave].append(float(fila[campo_valor]))
    return grupos


def prom(valores):
    return statistics.mean(valores)


def desv(valores):
    return statistics.stdev(valores) if len(valores) > 1 else 0


os.makedirs("graficas", exist_ok=True)
exp1 = leer("resultados/experimento1.csv")
exp2 = leer("resultados/experimento2.csv")
reps1 = len({f["repeticion"] for f in exp1})
reps2 = len({f["repeticion"] for f in exp2})

busqueda = agrupar(exp1, ["orden", "estructura", "N"], "t_una_busqueda_us")
construir = agrupar(exp1, ["orden", "estructura", "N"], "t_construir_s")
altura = agrupar(exp1, ["orden", "estructura", "N"], "altura")
M_usado = agrupar(exp1, ["orden", "estructura", "N"], "M")
total_M = agrupar(exp2, ["estructura", "M"], "t_buscar_s")

# El experimento 3 es opcional: si todavía no se ha corrido, no se hace la gráfica 3
hay_exp3 = os.path.exists("resultados/experimento3.csv")
if hay_exp3:
    exp3 = leer("resultados/experimento3.csv")
    reps3 = len({f["repeticion"] for f in exp3})
    pequenos = agrupar(exp3, ["estructura", "N"], "t_una_busqueda_us")
    M_pequenos = agrupar(exp3, ["estructura", "N"], "M")


# ------------------------------------------------------------ GRÁFICA 1
# Eje X (N) en escala logarítmica y eje Y normal:
#   - lo que crece exactamente como log N se vería como una línea RECTA
#   - lo que crece como N se CURVA hacia arriba (la "parábola")
# Los árboles balanceados van en otro panel porque son ~1.000 veces más rápidos
# (si estuvieran junto a la Lista, quedarían pegados al cero).
# Ojo: en la práctica los árboles se curvan un poco hacia arriba. Los niveles sí crecen
# como log N, pero cada nivel cuesta más cuando el árbol ya no cabe en la memoria caché.
paneles_g1 = [
    ("Crecen con N, O(N): se curvan hacia arriba",
     [("aleatorio", "Lista", "-"), ("ordenado", "Lista", "--"), ("ordenado", "ABB", "--")]),
    ("Árboles balanceados, O(log N): crecen poco",
     [("aleatorio", "ABB", "-"), ("aleatorio", "B+", "-"), ("ordenado", "B+", "--")]),
]
fig, paneles = plt.subplots(1, 2, figsize=(12, 5.4))
maximos = []        # el promedio más alto de cada panel (para la nota sobre la escala)
for ax, (titulo, series) in zip(paneles, paneles_g1):
    maximo = 0
    for orden, nombre, linea in series:
        Ns = [N for N in TAMANOS if (orden, nombre, str(N)) in busqueda]
        promedios = [prom(busqueda[(orden, nombre, str(N))]) for N in Ns]
        desviaciones = [desv(busqueda[(orden, nombre, str(N))]) for N in Ns]
        maximo = max(maximo, max(promedios))
        ax.errorbar(Ns, promedios, yerr=desviaciones, label=f"{nombre} – IDs {orden}s",
                    color=COLOR[nombre], marker=MARCA[nombre], linestyle=linea, markersize=7,
                    linewidth=2, capsize=4, markeredgecolor="white")
    maximos.append(maximo)
    ax.set_xscale("log")
    ax.set_xticks(TAMANOS)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: es(x, 0)))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda y, _: "0" if y == 0 else (es(y, 0) if y >= 100 else es(y, 1))))
    ax.set_ylim(bottom=0)
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.set_xlabel("Número de estudiantes N (escala logarítmica)")
    ax.legend(loc="upper left", fontsize=9)
paneles[0].set_ylabel("Tiempo de una búsqueda (µs, escala normal)")
paneles[0].annotate("El ABB con IDs ordenados solo se midió hasta N = 20.000:\n"
                    "construirlo con más datos tardaría varios minutos.",
                    xy=(0.03, 0.62), xycoords="axes fraction", fontsize=8.5, color="#52514e")
fig.suptitle("Experimento 1: tiempo de buscar UN estudiante según el número de estudiantes N",
             x=0.01, ha="left", fontsize=13, fontweight="bold", y=0.99)
fig.text(0.01, 0.885, "Eje X logarítmico y eje Y normal: lo que crece como log N se vería como una recta, "
         "y lo que crece como N se curva hacia arriba.\n"
         f"Cada punto es el promedio de {reps1} repeticiones; barras: ± 1 desviación estándar. "
         f"Ojo con la escala: el panel izquierdo llega a unos {es(maximos[0], 0)} µs "
         f"y el derecho a unos {es(maximos[1], 1)} µs.",
         fontsize=9, color="#52514e")
fig.text(0.01, 0.01, "Datos: resultados/experimento1.csv", fontsize=8, color=GRIS)
fig.tight_layout(rect=(0, 0.03, 1, 0.86))
fig.savefig("graficas/grafica1_busqueda_vs_N.png")
plt.close(fig)


# ------------------------------------------------------------ GRÁFICA 2
fig, paneles = plt.subplots(1, 3, figsize=(13, 4.8))
for ax, nombre in zip(paneles, ESTRUCTURAS):
    Ms = sorted(int(M) for (e, M) in total_M if e == nombre)
    promedios = [prom(total_M[(nombre, str(M))]) for M in Ms]
    desviaciones = [desv(total_M[(nombre, str(M))]) for M in Ms]
    if nombre == "Lista":
        escala, unidad = 1000, "miles"
    else:
        escala, unidad = 1000000, "millones"
    x = [M / escala for M in Ms]
    # Recta "proporcional a M" que pasa por el cero (pendiente = tiempo promedio de una búsqueda)
    pendiente = sum(promedios) / sum(x)
    ax.plot([0, x[-1] * 1.05], [0, pendiente * x[-1] * 1.05], color=GRIS, linestyle="--",
            linewidth=1.2, label="proporcional a M")
    ax.errorbar(x, promedios, yerr=desviaciones, color=COLOR[nombre], marker=MARCA[nombre],
                markersize=7, linewidth=0, elinewidth=2, capsize=4, markeredgecolor="white",
                label="promedio medido")
    ax.set_xlim(0, x[-1] * 1.1)
    ax.set_ylim(0, max(promedios) * 1.2)
    ax.set_xticks(x)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: es(v, 1).replace(",0", "")))
    ax.set_title(nombre, fontsize=11, fontweight="bold")
    ax.set_xlabel(f"M (número de búsquedas, en {unidad})")
    ax.legend(loc="upper left", fontsize=8.5)
paneles[0].set_ylabel("Tiempo total de las M búsquedas (s)")
fig.suptitle("Experimento 2: tiempo total según el número de búsquedas M (N = 10.000, IDs aleatorios)",
             x=0.01, ha="left", fontsize=13, fontweight="bold")
fig.text(0.01, 0.89, f"Promedio de {reps2} repeticiones (barras: ± 1 desviación estándar). "
         "Los puntos caen sobre una recta que pasa por el cero: si M se duplica, el tiempo se duplica.",
         fontsize=9, color="#52514e")
fig.text(0.01, 0.01, "Datos: resultados/experimento2.csv", fontsize=8, color=GRIS)
fig.tight_layout(rect=(0, 0.03, 1, 0.87))
fig.savefig("graficas/grafica2_tiempo_vs_M.png")
plt.close(fig)


# ------------------------------------------------------------ GRÁFICA 3
# Experimento 3 (N de 10 a 1.000) junto con el experimento 1 (N de 5.000 a 100.000),
# solo con IDs aleatorios. Los DOS ejes van en escala logarítmica, porque N va de 10 a
# 100.000 y los tiempos van de menos de 1 µs a miles de µs.
if hay_exp3:
    fig, ax = plt.subplots(figsize=(10, 6.2))
    for nombre in ESTRUCTURAS:
        Ns3 = sorted(int(N) for (e, N) in pequenos if e == nombre)
        Ns1 = [N for N in TAMANOS if ("aleatorio", nombre, str(N)) in busqueda]
        prom3 = [prom(pequenos[(nombre, str(N))]) for N in Ns3]
        desv3 = [desv(pequenos[(nombre, str(N))]) for N in Ns3]
        prom1 = [prom(busqueda[("aleatorio", nombre, str(N))]) for N in Ns1]
        desv1 = [desv(busqueda[("aleatorio", nombre, str(N))]) for N in Ns1]
        # Una sola línea por estructura, de N = 10 a N = 100.000
        ax.plot(Ns3 + Ns1, prom3 + prom1, color=COLOR[nombre], linewidth=2, label=nombre)
        # Marcadores huecos: experimento 3. Marcadores rellenos: experimento 1.
        ax.errorbar(Ns3, prom3, yerr=desv3, color=COLOR[nombre], marker=MARCA[nombre],
                    markersize=7, linestyle="", capsize=3, markerfacecolor="white")
        ax.errorbar(Ns1, prom1, yerr=desv1, color=COLOR[nombre], marker=MARCA[nombre],
                    markersize=7, linestyle="", capsize=3, markeredgecolor="white")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([10, 100, 1000, 10000, 100000])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: es(x, 0)))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: es(y, 1) if y < 1 else es(y, 0)))
    ax.set_xlabel("Número de estudiantes N (escala logarítmica)")
    ax.set_ylabel("Tiempo de una búsqueda (µs, escala logarítmica)")
    ax.legend(loc="upper left", fontsize=10)
    fig.suptitle("Experimento 3: ¿desde qué N se notan las diferencias? (IDs aleatorios)",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.875, "Los dos ejes son logarítmicos: una línea que sube inclinada es O(N) y una casi "
             "plana es O(log N).\n"
             f"Cada punto es el promedio de {reps3} repeticiones (barras: ± 1 desviación estándar). "
             "Marcadores huecos: experimento 3 (N de 10 a 1.000).\n"
             "Marcadores rellenos: experimento 1 (N de 5.000 a 100.000).",
             fontsize=9, color="#52514e")
    fig.text(0.01, 0.01, "Datos: resultados/experimento3.csv y resultados/experimento1.csv",
             fontsize=8, color=GRIS)
    fig.tight_layout(rect=(0, 0.03, 1, 0.85))
    fig.savefig("graficas/grafica3_N_pequenos.png")
    plt.close(fig)


# ------------------------------------------------------------ TABLAS
lineas = ["# Tablas de resultados", ""]

lineas.append(f"## Experimento 1: tiempo de una búsqueda (µs), promedio ± desviación estándar de {reps1} repeticiones")
for orden in ["aleatorio", "ordenado"]:
    lineas += ["", f"**IDs {orden}s**", "",
               "| N | M Lista | Lista | M ABB | ABB | M B+ | B+ |",
               "|---:|---:|---:|---:|---:|---:|---:|"]
    for N in TAMANOS:
        celdas = [es(N, 0)]
        for nombre in ESTRUCTURAS:
            clave = (orden, nombre, str(N))
            if clave in busqueda:
                celdas.append(es(M_usado[clave][0], 0))
                celdas.append(f"{es(prom(busqueda[clave]))} ± {es(desv(busqueda[clave]))}")
            else:
                celdas += ["—", "no se midió"]
        lineas.append("| " + " | ".join(celdas) + " |")

lineas += ["", f"## Altura de los árboles (número de niveles, promedio de {reps1} repeticiones)", "",
           "| N | ABB aleatorio | ABB ordenado | B+ aleatorio | B+ ordenado |",
           "|---:|---:|---:|---:|---:|"]
for N in TAMANOS:
    celdas = [es(N, 0)]
    for orden, nombre in [("aleatorio", "ABB"), ("ordenado", "ABB"), ("aleatorio", "B+"), ("ordenado", "B+")]:
        clave = (orden, nombre, str(N))
        celdas.append(es(prom(altura[clave]), 1) if clave in altura else "—")
    lineas.append("| " + " | ".join(celdas) + " |")

lineas += ["", f"## Tiempo de construcción (s): meter los N estudiantes, promedio de {reps1} repeticiones", "",
           "| N | Lista aleatorio | ABB aleatorio | B+ aleatorio | ABB ordenado |",
           "|---:|---:|---:|---:|---:|"]
for N in TAMANOS:
    celdas = [es(N, 0)]
    for orden, nombre in [("aleatorio", "Lista"), ("aleatorio", "ABB"), ("aleatorio", "B+"), ("ordenado", "ABB")]:
        clave = (orden, nombre, str(N))
        celdas.append(es(prom(construir[clave]), 3) if clave in construir else "—")
    lineas.append("| " + " | ".join(celdas) + " |")

lineas += ["", f"## Experimento 2 (N = 10.000, IDs aleatorios): promedio ± desviación estándar de {reps2} repeticiones", "",
           "| Estructura | M | Tiempo total (s) | Tiempo de una búsqueda (µs) |",
           "|---|---:|---:|---:|"]
for nombre in ESTRUCTURAS:
    for M in sorted(int(M) for (e, M) in total_M if e == nombre):
        valores = total_M[(nombre, str(M))]
        lineas.append(f"| {nombre} | {es(M, 0)} | {es(prom(valores))} ± {es(desv(valores))} | "
                      f"{es(prom(valores) / M * 1000000)} |")

if hay_exp3:
    lineas += ["", f"## Experimento 3: N pequeños, IDs aleatorios (promedio ± desviación estándar "
               f"de {reps3} repeticiones)", "",
               "| N | M Lista | Lista (µs) | M ABB y B+ | ABB (µs) | B+ (µs) | Lista ÷ ABB | Lista ÷ B+ |",
               "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for N in sorted({int(N) for (e, N) in pequenos}):
        lista = pequenos[("Lista", str(N))]
        abb = pequenos[("ABB", str(N))]
        bmas = pequenos[("B+", str(N))]
        lineas.append(f"| {es(N, 0)} | {es(M_pequenos[('Lista', str(N))][0], 0)} | "
                      f"{es(prom(lista), 3)} ± {es(desv(lista), 3)} | "
                      f"{es(M_pequenos[('ABB', str(N))][0], 0)} | "
                      f"{es(prom(abb), 3)} ± {es(desv(abb), 3)} | {es(prom(bmas), 3)} ± {es(desv(bmas), 3)} | "
                      f"{es(prom(lista) / prom(abb), 1)} | {es(prom(lista) / prom(bmas), 1)} |")

with open("resultados/tablas.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lineas) + "\n")

print("Listo:")
print("  graficas/grafica1_busqueda_vs_N.png")
print("  graficas/grafica2_tiempo_vs_M.png")
if hay_exp3:
    print("  graficas/grafica3_N_pequenos.png")
else:
    print("  (la gráfica 3 se hace cuando exista resultados/experimento3.csv)")
print("  resultados/tablas.md")
