"""Precarga el TMY de PVGIS para las ciudades del catálogo.

Guarda un CSV por ciudad en data/tmy/ con el índice ya en hora local fija
(roll_utc_offset) y el año forzado a 2026, listo para leerse con:

    pd.read_csv("data/tmy/temixco.csv", index_col=0, parse_dates=True)

Es el "plan B sin red" del taller: molab (nube) monta el repo, y la versión
WASM (la libreta corriendo en el navegador, sin sesión) no puede llamar a
PVGIS porque el navegador bloquea la petición (CORS), así que las libretas
leen esta caché primero.

Uso:
    uv run python scripts/precargar_tmy.py              # las 18 ciudades
    uv run python scripts/precargar_tmy.py Temixco Mérida   # solo algunas
"""
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from pvlib import iotools

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "data" / "sitios_mexico.csv"
SALIDA = RAIZ / "data" / "tmy"
COLUMNAS = ["ghi", "dni", "dhi", "temp_air", "wind_speed"]
ANIO = 2026


def slug(nombre):
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return s.lower().replace(" ", "_")


def offset_estandar(tz):
    """Offset UTC en horas el 1 de enero (sin horario de verano)."""
    return int(datetime(ANIO, 1, 1, tzinfo=ZoneInfo(tz)).utcoffset().total_seconds() // 3600)


def main():
    pedidos = {slug(n) for n in sys.argv[1:]}
    catalogo = pd.read_csv(CATALOGO)
    SALIDA.mkdir(parents=True, exist_ok=True)
    for _, sitio in catalogo.iterrows():
        s = slug(sitio["nombre"])
        if pedidos and s not in pedidos:
            continue
        offset = offset_estandar(sitio["zona_horaria"])
        tmy, _ = iotools.get_pvgis_tmy(
            sitio["latitud"], sitio["longitud"], map_variables=True,
            roll_utc_offset=offset, coerce_year=ANIO,
        )
        destino = SALIDA / f"{s}.csv"
        tmy[COLUMNAS].round(2).to_csv(destino, index_label="tiempo")
        print(f"{destino.relative_to(RAIZ)}: {len(tmy)} horas, UTC{offset:+d}")


if __name__ == "__main__":
    main()
