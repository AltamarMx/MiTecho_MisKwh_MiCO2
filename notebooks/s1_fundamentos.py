# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.0",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="S1 · Python mínimo y marimo")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Sesión 1 · Python mínimo y las reglas de marimo

    Bienvenida/o al taller **Mi techo, mis kWh, mi CO₂**. Esta libreta corre en
    [molab](https://molab.marimo.io): marimo en la nube, con el repositorio del
    taller completo montado (datos incluidos). No instalaste nada.

    **Las tres reglas de marimo:**

    1. Cada celda es una función de Python; el cuaderno es un **grafo de dependencias**.
    2. Una variable se define en **una sola** celda.
    3. Cambias algo → se recalcula **todo lo que depende de ello**. No hay estado oculto.

    Y un secreto: este archivo es Python puro (`notebooks/s1_fundamentos.py`).
    Ábrelo en un editor de texto y compruébalo.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Variables y tipos

    Una variable es un nombre pegado a un valor. El tipo (`int`, `float`, `str`) se lo
    da el valor, no tú. Los comentarios con `#` documentan **las unidades**: en
    energía, la mitad de los errores son de unidades.
    """)
    return


@app.cell
def _():
    potencia_panel = 550   # W, un panel típico
    eficiencia = 0.20      # fracción, sin unidades
    ciudad = "Temixco"
    type(potencia_panel), type(eficiencia), type(ciudad)
    return ciudad, eficiencia, potencia_panel


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · Listas

    Una lista es una colección ordenada. Se indexa desde **cero**, y `-1` es el
    último elemento. En la sesión 2, tu app recorrerá una lista de ciudades
    exactamente así.
    """)
    return


@app.cell
def _():
    ciudades = ["Temixco", "Mérida", "Tijuana", "La Paz"]
    ciudades[0], ciudades[-1], len(ciudades)
    return (ciudades,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Diccionarios

    Un diccionario guarda pares **clave → valor**. Es la forma natural de describir
    *un* sitio; una tabla de pandas será la forma natural de describir *muchos*.
    """)
    return


@app.cell
def _():
    sitio = {"nombre": "Temixco", "lat": 18.84,
             "lon": -99.24, "altitud": 1220}
    sitio["lat"]
    return (sitio,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · Funciones

    Una función empaca un cálculo con nombre y valores por defecto. Esta es la regla
    de tres de los instaladores solares: área × *horas solares pico* × eficiencia ×
    30 días.

    Ese `hsp=5.5` es un **número mágico** por ahora. En la libreta de meteorología lo
    vamos a calcular de verdad, para tu techo y tu clima.
    """)
    return


@app.cell
def _():
    def kwh_mensuales(area_m2, hsp=5.5, eficiencia=0.20):
        return area_m2 * hsp * eficiencia * 30

    f"{kwh_mensuales(10):.0f} kWh al mes con 10 m²"
    return (kwh_mensuales,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · La reactividad en acción

    Mueve el slider. No hay botón de "ejecutar": la celda de abajo **depende** del
    slider, así que marimo la recalcula sola. Este es el superpoder que en la
    sesión 2 convierte tu libreta en una app.
    """)
    return


@app.cell
def _(mo):
    area_arreglo = mo.ui.slider(1, 50, step=1, value=10,
                                label="Área del arreglo (m²)")
    area_arreglo
    return (area_arreglo,)


@app.cell
def _(area_arreglo, kwh_mensuales, mo):
    mo.md(
        f"**{kwh_mensuales(area_arreglo.value):.0f} kWh al mes** "
        f"con {area_arreglo.value} m² (hsp = 5.5, eficiencia = 20 %)"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6 · La prueba del estado oculto

    La celda de abajo define `borrar_me`. La que le sigue la usa.
    **Borra la celda de abajo** y observa qué pasa con la que la usa.
    En Jupyter, la variable seguiría viva en el kernel, mintiendo en silencio.
    """)
    return


@app.cell
def _():
    borrar_me = 42
    return (borrar_me,)


@app.cell
def _(borrar_me, mo):
    mo.md(f"`borrar_me` vale **{borrar_me}**")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## Siguiente parada

    - [**s1_geometria_solar.py**](https://molab.marimo.io/github/AltamarMx/MiTecho_MisKwh_MiCO2/blob/main/notebooks/s1_geometria_solar.py):
      la física del recurso solar, con sliders.
    - [**s1_meteo_pvlib.py**](https://molab.marimo.io/github/AltamarMx/MiTecho_MisKwh_MiCO2/blob/main/notebooks/s1_meteo_pvlib.py):
      clima real (EPW y PVGIS) y tu primer modelo fotovoltaico.
    """)
    return


if __name__ == "__main__":
    app.run()
