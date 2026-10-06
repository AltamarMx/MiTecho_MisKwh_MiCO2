# PLAN — Taller "Mi techo, mis kWh, mi CO₂"

> Borrador para revisión. Nada de esto se ha ejecutado aún.

Taller práctico de **3 sesiones (6 h)** para estudiantes de ingeniería sin experiencia
previa en Python. Cada participante construye una app web en marimo que estima, para
cualquier ciudad de México, los kWh de un sistema fotovoltaico, el ahorro con tarifa
CFE y los kg de CO₂ evitados según la hora del día.

**Material base**: `tmp/6toColoquioEnergia-main/` — presentación Quarto/reveal.js con
geometría solar ya desarrollada, app de marimo celda por celda (`app_sitios.py` +
versión con 4 TODOs), catálogo de 18 ciudades y scripts de verificación. Se migra y
adapta, no se parte de cero.

---

## 1. Decisiones de arquitectura

### 1.1 Todo desde Quarto, publicado con gh-pages

- Proyecto Quarto tipo **website**: una página índice (`index.qmd`) + una presentación
  reveal.js por sesión (`sesion1.qmd`, `sesion2.qmd`, `sesion3.qmd`).
- Publicación con `uv run quarto publish gh-pages` (rama `gh-pages`, salida `_site/`
  ignorada en git). Ya no se versiona `docs/` en `main` como en el repo anterior.
- Se migran `custom.scss`, configuración de reveal.js (chalkboard, code-copy, etc.) y
  el patrón de QR generado con `qrcode` en una celda oculta.

### 1.2 Libretas marimo abiertas desde la presentación (equivalente al badge de Colab)

Mecanismo verificado en la documentación de marimo:

- **URL**: reemplazar `github.com` por `molab.marimo.io/github` en la URL del archivo:
  `https://molab.marimo.io/github/AltamarMx/MiTecho_MisKwh_MiCO2/blob/main/notebooks/s1_fundamentos.py`
- **Badge**: `[![Open in molab](https://marimo.io/molab-shield.svg)](<url molab>)`
  (generador oficial en <https://marimo.io/github>).
- molab **monta el repositorio completo** en el sistema de archivos de la libreta →
  las libretas leen `data/…` con rutas relativas, sin descargar nada.
- Las dependencias se declaran en el encabezado inline `# /// script` de cada libreta
  (patrón que ya usan las libretas del repo base).
- Cada diapositiva de arranque de sesión lleva **badge + QR** apuntando a su libreta,
  igual que la diapositiva de Colab actual.
- Requisito: **el repo debe ser público en GitHub** para que los enlaces funcionen.

### 1.3 Meteorología: pvlib la jala solo (PVGIS); el repo solo lleva la lista

En lugar de empacar un EPW por ciudad, las libretas usan
`pvlib.iotools.get_pvgis_tmy(lat, lon)`: el año meteorológico típico de **cualquier
localidad** de México (PVGIS cubre América vía NSRDB), sin API key. El repo solo
necesita `sitios_mexico.csv`, y la app cumple literalmente el "para cualquier ciudad
de México" — incluidos los sitios propios que agregue el estudiante. (El repo base ya
apuntaba ahí: es el "reto" al final de `app_sitios.py`.)

- **Alfabetización de formato**: se conserva **un** EPW de muestra en `data/epw/`
  para el bloque "leer archivos meteorológicos estándar" de la sesión 1 (`read_epw`);
  el resto del taller usa PVGIS.
- **Detalle didáctico**: PVGIS regresa timestamps en **UTC** → convertir a hora local
  con la `zona_horaria` del catálogo. Imprescindible para cruzar con demanda, tarifa
  y factor de emisión horarios en la sesión 3.
- **Plan B sin red**: `scripts/precargar_tmy.py` guarda en `data/tmy/` el TMY de las
  18 ciudades (parquet). Las libretas intentan la caché local primero (molab monta el
  repo) y solo llaman a PVGIS para sitios fuera del catálogo — el WiFi del aula deja
  de ser punto único de falla.

### 1.4 Datos de CENACE precalculados, no descargas en vivo

Para PML y factor de emisión los estudiantes **solo leen CSV** del repo. Descargar y
limpiar CENACE en vivo se comería la sesión. Los scripts de descarga/limpieza viven
en `scripts/` y los corre solo el autor antes del taller.

### 1.5 Factor de emisión: aproximación nacional v1, con los límites dichos en voz alta

El factor de emisión horario se construye **a nivel nacional**: la *forma* horaria
(24 h × 12 meses) sale de la generación por tecnología de CENACE, y el *nivel* se
ancla al **factor de emisión oficial anual del SEN** (SEMARNAT/CRE), que es el número
citable. Eso reduce mucho la ingeniería de datos y basta para el insight central
(la red está más limpia a mediodía).

A cambio, la sesión 3 incluye una diapositiva explícita de **"los límites de nuestra
aproximación"**: un análisis serio usaría (a) factores por sistema — BCA y BCS tienen
mezclas distintas al SIN —, (b) el factor **marginal**, no el promedio — el kWh solar
desplaza a la planta marginal, no a la mezcla —, y (c) el año real, no un TMY.
Decir qué simplificamos y por qué es parte del entrenamiento.

### 1.6 México no es una sola red

El catálogo de sitios gana columnas `sistema` (SIN / BCA / BCS), `zona_carga` y
`tarifa_cfe`. La dimensión regional se muestra con el **PML por zona de carga**
(Tijuana → BCA, La Paz → BCS, el resto → SIN); para emisiones aplica la aproximación
nacional de 1.5 y su diapositiva de límites.

---

## 2. Estructura propuesta del repositorio

```
MiTecho_MisKwh_MiCO2/
├── _quarto.yml                  # website; render: index + 3 sesiones; publish gh-pages
├── index.qmd                    # landing: objetivo, agenda, badges molab, QRs
├── sesion1.qmd                  # revealjs · fundamentos + geometría solar + EPW + pvlib
├── sesion2.qmd                  # revealjs · de libreta a app con controles marimo
├── sesion3.qmd                  # revealjs · demanda, tarifa CFE, CO₂ horario (+ PML)
├── custom.scss                  # migrado del repo base
├── notebooks/
│   ├── s1_fundamentos.py        # Python mínimo + reglas de marimo (nuevo)
│   ├── s1_geometria_solar.py    # demo reactiva β/γ/ρ (adapta demo_irradiancia.py)
│   ├── s1_meteo_pvlib.py        # EPW de muestra + TMY de PVGIS + primer modelo FV (nuevo)
│   ├── s2_app_taller.py         # punto de control con TODOs (adapta app_sitios_taller.py)
│   ├── s2_app_completa.py       # referencia (adapta app_sitios.py)
│   └── s3_mi_techo.py           # app final: generación × demanda × tarifa × CO₂ (+ PML)
├── data/
│   ├── sitios_mexico.csv            # 18 ciudades + sistema, zona_carga, tarifa_cfe
│   ├── epw/                         # 1 EPW de muestra (alfabetización de formato)
│   ├── tmy/                         # caché parquet del TMY de PVGIS (18 ciudades, plan B)
│   ├── factor_emision_horario.csv   # gCO₂/kWh · 24 h × 12 meses · nacional, anclado al factor oficial anual
│   ├── pml_promedio_horario.csv     # $/MWh · 24 h × 12 meses × zona de carga
│   ├── tarifas_cfe.csv              # escalones 1, 1A–1F, DAC · temporada
│   └── perfil_demanda_residencial.csv  # perfil horario normalizado (+ variante con A/C)
├── scripts/                     # solo para el autor, nunca en sesión
│   ├── descargar_pml_cenace.py  # API SW-PND/SW-PML, tramos de 7 días, por sistema
│   ├── factor_emision.py        # generación horaria por tecnología → gCO₂/kWh
│   ├── precargar_tmy.py         # caché local del TMY de PVGIS (plan B sin red)
│   └── verificar_celdas.py      # código de diapositivas == libretas (adaptado)
├── PLAN.md                      # este archivo
├── README.md
└── pyproject.toml / uv.lock     # ya existen; agregar qrcode, nbformat si hace falta
```

`tmp/` se agrega a `.gitignore` (es material de consulta, no parte del repo).

---

## 3. Sesión 1 · Fundamentos, geometría solar y primer modelo (2 h)

Trabajo en **marimo molab** desde el minuto uno: el estudiante abre la libreta con el
badge/QR, sin instalar nada.

| min | Bloque | Material |
|---|---|---|
| 10 | Bienvenida · abrir `s1_fundamentos.py` en molab (badge + QR) | diapositiva tipo "Antes de empezar" |
| 20 | Python mínimo en marimo: variables, listas, diccionarios, funciones, f-strings; reactividad (una variable = una celda, el grafo recalcula solo) | `s1_fundamentos.py`, incluye la "prueba del estado oculto" del demo actual |
| 10 | ¿Por qué Python para energía? | diapositivas existentes (se migran casi intactas) |
| 30 | **Geometría solar básica** (ya está en la presentación base, se reusa): GHI/DNI/DHI, posición del Sol (θz, γs), trayectoria aparente, ecuación POA con sus 3 caminos (directa, difusa de cielo, reflejada) y albedo | diapositivas de `presentacion.qmd` + `s1_geometria_solar.py` con sliders β/γ/ρ |
| 25 | **Datos meteorológicos**: qué es un TMY; leer el EPW de muestra con `read_epw`; cualquier localidad con `get_pvgis_tmy` (UTC → hora local); cielo despejado vs TMY | `s1_meteo_pvlib.py` + `data/epw/` |
| 15 | **Primer modelo FV**: TMY → POA (`get_total_irradiance`) → kWh con área × eficiencia | `s1_meteo_pvlib.py` |
| 10 | Cierre: uv y reproducibilidad (el encabezado `# /// script`), reto para casa | diapositivas |

Cambio respecto al repo base: la física pasa de cielo despejado (Ineichen) a **datos
de TMY (PVGIS, con un EPW de muestra)**, que es lo que pide el temario. El cielo
despejado se queda como comparación ("¿cuánto pierde tu ciudad por nubes?").

## 4. Sesión 2 · De libreta a app interactiva (2 h)

Se adapta casi directo la "Sesión 2" del repo base (bloques 1–4), cambiando el motor
de cielo despejado por EPW:

| min | Bloque |
|---|---|
| 10 | Reglas del juego en molab; cómo se guarda y comparte una libreta |
| 25 | Bloque 1 · Catálogo de sitios: `mo.ui.table` con selección múltiple + sitios propios |
| 25 | Bloque 2 · Parámetros: sliders (β, γ, ρ, área, eficiencia), dropdowns (modelo de difusa, periodo) |
| 30 | Bloque 3 · La física y el ciclo: función `calcular_sitio` + ciclo sobre sitios seleccionados |
| 20 | Bloque 4 · Resultados: tabla formateada, gráficas, botón de descarga CSV |
| 20 | **Modo app**: ejecutar sin código visible; los 4 TODOs de `s2_app_taller.py` como ejercicio; export a HTML-WASM autocontenido (el entregable de portafolio) |

## 5. Sesión 3 · Demanda, tarifa CFE y CO₂ horario (2 h)

| min | Bloque |
|---|---|
| 15 | Perfil de demanda residencial horario: leer `perfil_demanda_residencial.csv`, escalar a kWh/bimestre del recibo del estudiante |
| 15 | Cruce generación–demanda hora por hora: autoconsumo vs inyección a la red |
| 25 | **CO₂ horario** (aproximación nacional): leer `factor_emision_horario.csv`; kg CO₂ evitados con factor horario vs el factor oficial anual — primera mitad del insight |
| 25 | **Tarifa CFE**: escalones (1, 1A–1F, DAC), temporada de verano, asignación por ciudad; net metering **compensa kWh, no pesos** → el ahorro se calcula en energía, no por hora |
| 15 | Los 3 KPIs en la app: kWh generados, $ ahorrados, kg CO₂ evitados |
| 10 | Lente 4 (opcional): **valor de mercado** con el perfil de PML promedio por zona de carga — un kWh vale distinto según la hora *para el sistema* |
| 15 | **Límites de la aproximación + insight central**: promedio ≠ marginal, nacional ≠ BCA/BCS, TMY ≠ año real; el panel genera cuando nadie está en casa y cuando la red ya está limpia → baterías, net metering, redes inteligentes |

Puntos conceptuales que las diapositivas dicen explícitamente:

- **El usuario doméstico no paga el PML.** Las tarifas residenciales son por escalones
  de consumo, no por hora. El PML es la lente del "valor del kWh para el sistema",
  no del ahorro en el recibo.
- **México no es una sola red**: el PML por zona de carga lo muestra; el factor de
  emisión usa la aproximación nacional y lo decimos (diapositiva de límites).
- **Nuestro factor de emisión es promedio y nacional**: un análisis riguroso usaría
  el factor marginal y por sistema. Qué haríamos distinto queda escrito en la app.

---

## 6. Preparación de datos (autor, antes del taller)

1. **Meteorología** — `scripts/precargar_tmy.py`: TMY de PVGIS para las 18 ciudades a
   `data/tmy/` (caché / plan B sin red) + **un** EPW de muestra en `data/epw/` para la
   alfabetización de formato de la sesión 1.
2. **PML/PND de CENACE** — `scripts/descargar_pml_cenace.py` contra la API REST
   (`https://ws01.cenace.gob.mx:8082/SWPML/SIM/…` y el servicio SW-PND de zonas de
   carga, que es el adecuado para una app residencial). Restricciones conocidas:
   puerto 8082, tope de 7 días por consulta (→ ~52 llamadas por zona-año), las claves
   dependen del sistema (SIN/BCA/BCS se consultan por separado). Producto: perfil
   promedio 24 h × 12 meses por zona de carga (`pml_promedio_horario.csv`).
3. **Factor de emisión horario (nacional)** — `scripts/factor_emision.py`: generación
   horaria **nacional** por tecnología de CENACE × intensidades típicas por tecnología
   → forma 24 × 12, con el promedio anual **anclado al factor oficial del SEN**
   (SEMARNAT/CRE). Supuestos documentados en el propio CSV. Versión por sistema y
   factor marginal: declarados como trabajo futuro, no se calculan.
4. **Tarifas CFE** — capturar escalones vigentes (básico/intermedio/excedente, verano
   y fuera de verano) de 1, 1A–1F y DAC en `tarifas_cfe.csv`, y asignar tarifa a cada
   ciudad del catálogo.
5. **Perfil de demanda residencial** — perfil horario normalizado de 24 h con variante
   de verano (A/C), fuente documentada.
6. **Catálogo** — agregar columnas `sistema`, `zona_carga`, `tarifa_cfe` a
   `sitios_mexico.csv`.

## 7. Verificación y publicación

- `uv run marimo check notebooks/` — grafo de dependencias sano en las 6 libretas.
- `scripts/verificar_celdas.py` adaptado: el código mostrado en cada `sesionN.qmd`
  existe línea por línea en su libreta correspondiente.
- Probar **cada enlace molab real** tras el primer push (requiere repo público).
- `uv run quarto render` sin errores → `uv run quarto publish gh-pages`.
- Activar GitHub Pages sobre la rama `gh-pages` en la configuración del repo.

## 8. Orden de ejecución propuesto

1. **Esqueleto**: `_quarto.yml` (website), `index.qmd`, migrar `custom.scss`,
   `.gitignore` (+`tmp/`, `_site/`, `.quarto/`), README, commit inicial.
2. **Sesión 1**: `sesion1.qmd` (migrando diapositivas de geometría solar) + las 3
   libretas de la sesión + caché TMY/EPW de muestra para poder probar.
3. **Datos**: scripts de CENACE/EPW/tarifas y generación de los CSV precalculados.
4. **Sesión 2**: `sesion2.qmd` + adaptación de las dos apps a EPW.
5. **Sesión 3**: `sesion3.qmd` + `s3_mi_techo.py`.
6. **QA y publicación**: verificaciones, push, badges molab, gh-pages.

Cada fase termina en un estado que renderiza y se puede revisar.

## 9. Decisiones abiertas (para confirmar antes de ejecutar)

1. **Nombre/visibilidad del repo**: asumo `github.com/AltamarMx/MiTecho_MisKwh_MiCO2`,
   público (sin remote configurado aún). ¿Correcto, o prefieres otro nombre sin
   guiones bajos (p. ej. `mi-techo-mis-kwh-mi-co2`)? Los badges molab dependen de esto.
2. **molab requiere iniciar sesión** (GitHub/Google) para ejecutar. ¿Les pedimos
   cuenta a los estudiantes como requisito previo, o agregamos el enlace `/wasm`
   (corre en el navegador sin cuenta) como respaldo? Habría que probar pvlib en WASM.
3. **Ciudad del ejemplo conductor y del EPW de muestra**: propongo Temixco (IER).
4. **¿Conservamos la vía Colab** (`generar_cuaderno.py` → ipynb) como respaldo, o
   el taller es 100 % marimo? Propongo 100 % marimo para no mantener dos vías.
5. **Zonas de carga para el PML**: una por ciudad del catálogo, ¿o solo las de las
   ciudades con EPW?
6. **Fechas y sede del taller** (para portada y pie de página).

## Referencias

- Abrir libretas de GitHub en molab: <https://docs.marimo.io/guides/publishing/github/>
- Generador de badges molab: <https://marimo.io/github>
- Anuncio de molab: <https://marimo.io/blog/announcing-molab>
- API de PML de CENACE (manual técnico SW-PML): `ws01.cenace.gob.mx:8082/SWPML/SIM/…`
- EPW de México: <https://climate.onebuilding.org>
