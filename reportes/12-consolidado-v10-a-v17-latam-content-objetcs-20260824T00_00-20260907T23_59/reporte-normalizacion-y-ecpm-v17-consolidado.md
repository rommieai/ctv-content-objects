# Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, 380,355,807,040 requests; métricas de v17).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v17-consolidado.json` e `inventory-consolidado-v10-a-v17-enriquecido.csv` (no versionado).

eCPM ponderado global: 4.04 (v17 solo: 4.05). Tráfico monetizado (eCPM > 0): 50.7% de los requests.

*Nota: el 10.6% de los requests del consolidado viene de llaves de cortes anteriores que ya no existen en v17. Los precios de este reporte son los del consolidado.*

---

# PARTE A — Género normalizado

86.8% de filas con al menos un género canónico; 261,228 filas multi-género. Distribución multi-etiqueta, % sobre las filas con género útil:

| Género | % filas no vacías | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|
| drama | 29.3% | 3.56 | 45.5% |
| terror | 11.7% | 3.95 | 32.3% |
| comedia | 10.9% | 3.74 | 51.7% |
| documental | 10.8% | 5.88 | 40.3% |
| accion | 9.2% | 4.97 | 37.6% |
| thriller | 9.2% | 3.86 | 30.1% |
| romance | 6.3% | 4.25 | 42.0% |
| infantil-familia | 5.2% | 5.82 | 40.6% |
| otros/desconocido | 4.8% | 5.15 | 26.5% |
| crimen | 4.2% | 4.68 | 33.7% |
| aventura | 4.1% | 5.79 | 33.5% |
| entretenimiento | 4.1% | 4.74 | 64.3% |
| deportes | 3.8% | 2.28 | 70.6% |
| musica | 3.2% | 4.11 | 47.4% |
| misterio | 3.0% | 4.57 | 30.3% |
| sci-fi | 2.9% | 4.30 | 28.0% |
| fantasia | 2.7% | 4.14 | 25.3% |
| anime | 1.9% | 7.35 | 47.4% |
| noticias | 1.7% | 4.61 | 57.4% |
| reality | 1.4% | 5.29 | 50.7% |

# PARTE B — Rating en franjas de edad

| Franja | % filas | % filas no vacías | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 6.8% | 9.2% | 4.64 | 63.7% |
| 7+ | 0.5% | 0.6% | 7.01 | 44.3% |
| 10+ | 9.6% | 12.9% | 4.66 | 50.5% |
| 13-15 | 22.0% | 29.7% | 3.72 | 50.7% |
| 16-17 | 8.2% | 11.0% | 5.24 | 32.0% |
| 18+ / adulto | 16.7% | 22.5% | 4.35 | 34.9% |
| sin clasificar | 8.7% | 11.7% | 3.73 | 44.7% |
| sin dato | 25.7% | — | 3.64 | 56.4% |
| no mapeado | 1.9% | 2.5% | 3.16 | 61.9% |

*"% filas" incluye la fila vacía ("sin dato"); "% filas no vacías" renormaliza sobre el 74.3% restante. "sin clasificar" (`nr`, `Unrated`) y "no mapeado" (`dv-t`, `dv-g`, `dv-ma`, `mpaa_r`, `movie-pg-13`) sí son dato presente. Equivalencias de la escala nueva: `All Ages` = todos, `Teen` = 10+, `Teen Plus` = 13-15, `Adults` = 18+.*

# PARTE C — El inventario que monetiza (eCPM > 0)

167,986 filas (17.5%) concentran el 50.7% del tráfico.

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 57.5% | 20.5% | 3.11 |
| Guatemala | 56.7% | 29.1% | 5.92 |
| Argentina | 55.3% | 19.0% | 6.25 |
| Costa Rica | 42.2% | 32.0% | 6.20 |
| Chile | 35.9% | 22.9% | 6.10 |
| Perú | 31.5% | 15.0% | 4.88 |
| Colombia | 28.8% | 14.3% | 5.85 |
| Panamá | 24.8% | 7.5% | 2.12 |
| Ecuador | 15.1% | 5.3% | 6.15 |

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | 15.7% | 48.9% | 5.32 |
| TCL ADS - Springserve | 14.2% | 77.4% | 5.04 |
| iion Pty Ltd | 10.5% | 38.3% | 5.66 |
| Televisa Univision via SpringServe | 8.4% | 82.9% | 2.24 |
| Equativ | 8.2% | 80.7% | 2.57 |
| TCL ADs (APAC) | 7.7% | 72.5% | 5.62 |
| Coocaa (SKYWORTH) | 6.7% | 78.5% | 2.89 |
| Televisa Univision via OB | 6.2% | 97.1% | 1.10 |
| Zeasn (WhaleLive) | 4.7% | 96.6% | 2.81 |
| TV Azteca - Springserve | 4.4% | 51.6% | 5.92 |
| Vidaa | 4.3% | 81.9% | 1.42 |
| PML Digital | 1.9% | 68.8% | 2.33 |

## Señales sobre el tráfico monetizado

| Dimensión | Segmento | % del tráfico vendido | eCPM pond. |
|---|---|---:|---:|
| Idioma | español (`es` + `Spanish`) | 43.7% | 4.37 |
| Idioma | inglés (`en` + `English`) | 20.3% | 3.14 |
| Idioma | sin dato | 33.1% | 4.23 |
| Livestream | live (`1`) | 49.6% | 3.96 |
| Livestream | sin dato | — | 4.12 |
| Título | con título | — | 4.08 |
| Título | sin título | — | 3.98 |

*Outliers: los eCPM de 194.3, 135.3 y 102.9 (TCL APAC / MovieArk Perú) están solo en el consolidado por llaves viejas; en v17 el máximo es 95.9 (iion, Perú).*
