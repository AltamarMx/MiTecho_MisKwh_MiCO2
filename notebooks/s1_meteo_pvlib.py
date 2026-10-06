# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.0",
#     "pandas>=3.0",
#     "pvlib>=0.16",
#     "matplotlib>=3.11",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="S1 · Clima real y primer modelo FV")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    from pathlib import Path
    from pvlib import iotools, irradiance
    from pvlib.location import Location

    return Location, Path, iotools, irradiance, mo, pd, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Del clima real a tus kWh

    El cielo despejado es una ficción útil: perfecto para entender la geometría,
    malo para dimensionar un sistema. Aquí entra el **TMY** (*typical meteorological
    year*): 8760 horas armadas mes a mes con los meses más "típicos" de ~15–20 años
    de datos. Dos maneras de conseguirlo:

    1. Un archivo **EPW**, el formato estándar de la simulación de edificios.
    2. Pedírselo a **PVGIS** desde Python, para cualquier punto del mapa.
    """)
    return


@app.cell
def _(Location):
    temixco = Location(latitude=18.84, longitude=-99.24,
                       tz="America/Mexico_City", altitude=1220, name="Temixco")
    return (temixco,)


@app.cell
def _(Path, iotools):
    _candidatas = [Path("data/epw/temixco.epw"), Path("../data/epw/temixco.epw")]
    URL_EPW = ("https://raw.githubusercontent.com/AltamarMx/"
               "MiTecho_MisKwh_MiCO2/main/data/epw/temixco.epw")
    ruta_epw = next((str(_r) for _r in _candidatas if _r.exists()), URL_EPW)

    epw, meta_epw = iotools.read_epw(ruta_epw, coerce_year=2026)
    epw[["ghi", "dni", "dhi", "temp_air"]].head(3)
    return URL_EPW, epw, meta_epw, ruta_epw


@app.cell
def _(mo, ruta_epw):
    mo.md(rf"""
    Un EPW es texto plano: 8 renglones de encabezado y 8760 de datos. `read_epw` lo
    convierte en la tabla que ya conocemos —GHI, DNI, DHI— más temperatura y viento.
    `coerce_year` pone todas las horas en el mismo año.

    (Esta libreta lo leyó de: `{ruta_epw}`)
    """)
    return


@app.cell
def _(epw, plt):
    _diaria = epw["ghi"].resample("D").sum() / 1000
    _fig, _ax = plt.subplots(figsize=(9, 3))
    _ax.plot(_diaria.index, _diaria.values, lw=0.8, color="#5c677d")
    _ax.plot(_diaria.rolling(30, center=True).mean(), lw=2.5, color="#f4a300")
    _ax.set_title("GHI diaria en Temixco · año meteorológico típico")
    _ax.set_ylabel("kWh/m² al día"); _ax.grid(alpha=.3)
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Cualquier localidad, una línea: PVGIS

    PVGIS (Comisión Europea) entrega el TMY de **cualquier punto de América**,
    derivado de satélite, sin registrarse. Ojo: lo entrega en **UTC**;
    `roll_utc_offset=-6` lo recorre a la hora del centro de México. Si lo olvidas,
    tu sol sale a medianoche.

    **Prueba tu ciudad**: clic derecho en Google Maps → copiar coordenadas →
    pégalas aquí. (Tijuana es UTC−8; Hermosillo y La Paz, UTC−7.)

    ⚠️ La llamada en vivo necesita la **nube de molab** (inicia sesión y crea tu
    copia) o tu máquina. Si la libreta corre en el navegador (versión WASM), el
    navegador bloquea a PVGIS (CORS) y la celda cae sola a la **caché del
    repositorio**.
    """)
    return


@app.cell
def _(Path, iotools, pd):
    URL_TMY = ("https://raw.githubusercontent.com/AltamarMx/"
               "MiTecho_MisKwh_MiCO2/main/data/tmy/temixco.csv")
    try:
        tmy, meta = iotools.get_pvgis_tmy(18.84, -99.24,
                                          map_variables=True,
                                          roll_utc_offset=-6,
                                          coerce_year=2026)
        fuente_tmy = "PVGIS en vivo"
    except Exception:
        _cache = next((str(_r) for _r in [Path("data/tmy/temixco.csv"),
                                          Path("../data/tmy/temixco.csv")]
                       if _r.exists()), URL_TMY)
        tmy = pd.read_csv(_cache, index_col=0, parse_dates=True)
        meta = {"fuente": _cache}
        fuente_tmy = f"caché precalculada (`{_cache}`)"
    tmy[["ghi", "dni", "dhi", "temp_air"]].head(3)
    return URL_TMY, fuente_tmy, meta, tmy


@app.cell
def _(fuente_tmy, mo):
    mo.md(f"**Fuente de este TMY**: {fuente_tmy}. Ambas vías dan el mismo año típico.")
    return


@app.cell
def _(pd, plt, temixco, tmy):
    cielo_anio = temixco.get_clearsky(tmy.index, model="ineichen",
                                      linke_turbidity=3.0)
    _mensual = pd.DataFrame({
        "cielo despejado": cielo_anio["ghi"].groupby(cielo_anio.index.month).sum() / 1000,
        "año típico (PVGIS)": tmy["ghi"].groupby(tmy.index.month).sum() / 1000,
    })
    _ax = _mensual.plot.bar(figsize=(9, 3.2), color=["#5c677d", "#f4a300"], width=0.75)
    _ax.set_title("Las nubes, mes a mes")
    _ax.set_xticklabels(list("EFMAMJJASOND"), rotation=0)
    _ax.set_ylabel("kWh/m² al mes"); _ax.grid(alpha=.3, axis="y")
    _ax.legend(frameon=False)
    plt.tight_layout()
    _ax.figure
    return (cielo_anio,)


@app.cell
def _(cielo_anio, mo, tmy):
    _perdida = 1 - tmy["ghi"].sum() / cielo_anio["ghi"].sum()
    mo.md(
        f"Las nubes le cuestan a Temixco **{_perdida:.0%}** del recurso anual — "
        f"casi todo concentrado en la temporada de lluvias."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Tu primer modelo fotovoltaico

    La misma ecuación de los tres caminos, pero con el **año típico** en lugar del
    cielo despejado: un techo a 20° mirando al sur, 8760 renglones.
    """)
    return


@app.cell
def _(irradiance, temixco, tmy):
    sol_tmy = temixco.get_solarposition(tmy.index)
    techo = irradiance.get_total_irradiance(
        surface_tilt=20, surface_azimuth=180,
        solar_zenith=sol_tmy["apparent_zenith"],
        solar_azimuth=sol_tmy["azimuth"],
        dni=tmy["dni"], ghi=tmy["ghi"], dhi=tmy["dhi"],
        albedo=0.20, model="isotropic")
    return sol_tmy, techo


@app.cell
def _(mo, techo):
    area = 10          # m² de paneles
    eficiencia = 0.20  # 20 %
    kwh_anio = techo["poa_global"].sum() / 1000 * area * eficiencia
    mo.md(
        f"**{kwh_anio:,.0f} kWh al año** con {area} m². Cada renglón del TMY dura "
        f"1 hora, así que la suma ya integra; entre 1000 → kWh/m², por área y "
        f"eficiencia → la energía del sistema."
    )
    return area, eficiencia, kwh_anio


@app.cell
def _(kwh_anio, mo, techo):
    hsp = techo["poa_global"].sum() / 1000 / 365
    mo.md(
        f"**El número mágico, revelado**: {hsp:.2f} horas solares pico promedio en "
        f"Temixco. La `hsp=5.5` de la primera libreta era esto: los kWh/m²-día que "
        f"recibe el plano del arreglo. Con el año completo: "
        f"**{kwh_anio / 12:,.0f} kWh/mes**."
    )
    return (hsp,)


@app.cell
def _(area, eficiencia, plt, techo):
    _kwh_mes = techo["poa_global"].groupby(techo.index.month).sum() / 1000 * area * eficiencia
    _fig, _ax = plt.subplots(figsize=(9, 3.2))
    _ax.bar(_kwh_mes.index, _kwh_mes.values, color="#f4a300")
    _ax.set_title("La cosecha, mes a mes · sistema de 10 m² en Temixco")
    _ax.set_xticks(range(1, 13)); _ax.set_xticklabels(list("EFMAMJJASOND"))
    _ax.set_ylabel("kWh del sistema"); _ax.grid(alpha=.3, axis="y")
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    **Supuestos del modelo mínimo**: sin efecto de temperatura ni pérdidas de
    sistema (cables, inversor, suciedad); difusa isotrópica; albedo fijo en 0.20.
    Todo eso se refina en la sesión 2.

    **Reto para casa:**

    1. **Tu ciudad**: cambia las coordenadas en la celda de PVGIS (y su
       `roll_utc_offset`). ¿Cuántas horas solares pico tiene? ¿Le gana a Temixco?
    2. **Tu techo real**: cambia `surface_tilt` y `surface_azimuth`.
       ¿Cuánto pierdes respecto a 20° al sur?
    3. 📄 **Consigue un recibo de CFE** para la sesión 3.
    """)
    return


if __name__ == "__main__":
    app.run()
