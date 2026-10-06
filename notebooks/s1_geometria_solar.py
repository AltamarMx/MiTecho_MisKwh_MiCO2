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
app = marimo.App(width="medium", app_title="S1 · Geometría solar en Temixco")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    from pvlib import irradiance
    from pvlib.location import Location

    return Location, irradiance, mo, pd, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Geometría solar en Temixco

    Es el mismo cálculo de la presentación, pero **reactivo**: cambia un valor en
    la celda de parámetros (β, γ, la fecha…) y todo lo que depende de él se
    recalcula solo. No hay botón de "ejecutar".

    La ecuación de los tres caminos:
    directa ($\mathrm{DNI}\cos\theta$), difusa del cielo
    ($\mathrm{DHI}\,\tfrac{1+\cos\beta}{2}$) y reflejada por el suelo
    ($\mathrm{GHI}\,\rho\,\tfrac{1-\cos\beta}{2}$).

    **Experimentos sugeridos:**

    - Arranca como está: una **pared al este** (β = 90°, γ = 90°). ¿A qué hora pica?
    - Cambia a la **pared sur** (γ = 180°). ¿Por qué en Temixco no gana?
    - Acuéstala: **techo a 20° al sur** (β = 20°, γ = 180°). Ahí está la mina.
    - Cambia la fecha a los solsticios (21 jun, 21 dic). ¿Qué pasa con la pared norte?
    """)
    return


@app.cell
def _():
    fecha = "2026-03-21"   # prueba "2026-06-21" y "2026-12-21"
    inclinacion = 90       # β (°): 0 = horizontal, 90 = pared
    azimut = 90            # γ (°): 0 = N, 90 = E, 180 = S, 270 = O
    albedo = 0.20          # ρ: pasto 0.20, concreto 0.30, techo blanco 0.70
    turbidez = 3.0         # turbidez de Linke: 2 = muy limpio, 7 = bruma
    return albedo, azimut, fecha, inclinacion, turbidez


@app.cell
def _(Location, fecha, pd, turbidez):
    temixco = Location(latitude=18.84, longitude=-99.24,
                       tz="America/Mexico_City", altitude=1220, name="Temixco")
    _inicio = pd.Timestamp(fecha)
    horas = pd.date_range(_inicio, _inicio + pd.Timedelta(days=1), freq="10min", tz=temixco.tz)
    sol = temixco.get_solarposition(horas)
    cielo = temixco.get_clearsky(horas, model="ineichen", linke_turbidity=turbidez)
    return cielo, sol


@app.cell
def _(albedo, azimut, cielo, inclinacion, irradiance, sol):
    poa = irradiance.get_total_irradiance(
        surface_tilt=inclinacion, surface_azimuth=azimut,
        solar_zenith=sol["apparent_zenith"], solar_azimuth=sol["azimuth"],
        dni=cielo["dni"], ghi=cielo["ghi"], dhi=cielo["dhi"],
        albedo=albedo, model="isotropic")
    return (poa,)


@app.cell
def _(cielo, plt, poa):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
    cielo[["ghi", "dni", "dhi"]].plot(ax=_ax1, lw=2)
    _ax1.set_title("Cielo despejado: GHI, DNI, DHI")
    _ax1.set_ylabel("W/m²"); _ax1.set_xlabel("Hora local"); _ax1.grid(alpha=.3)
    _ax1.legend(["GHI", "DNI", "DHI"], frameon=False)
    poa[["poa_global", "poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]].plot(ax=_ax2, lw=1.5)
    _ax2.lines[0].set_linewidth(2.8)
    _ax2.set_title("Sobre la superficie (β, γ)")
    _ax2.set_xlabel("Hora local"); _ax2.grid(alpha=.3)
    _ax2.legend(["Total", "Directa", "Difusa cielo", "Reflejada suelo"], frameon=False, fontsize=9)
    plt.tight_layout()
    _fig
    return


@app.cell
def _(cielo, mo, poa):
    _dt_h = 10 / 60
    _e_sup = poa["poa_global"].sum() * _dt_h / 1000
    _e_hor = cielo["ghi"].sum() * _dt_h / 1000
    mo.md(
        f"**Energía del día** · superficie: **{_e_sup:.2f} kWh/m²** · "
        f"horizontal: {_e_hor:.2f} kWh/m² · cociente: {_e_sup / _e_hor:.0%}"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    Este cálculo usa **cielo despejado**: la física sin clima. La siguiente libreta
    ([**s1_meteo_pvlib.py**](https://molab.marimo.io/github/AltamarMx/MiTecho_MisKwh_MiCO2/blob/main/notebooks/s1_meteo_pvlib.py))
    mete las nubes: el año meteorológico típico de tu ciudad.
    """)
    return


if __name__ == "__main__":
    app.run()
