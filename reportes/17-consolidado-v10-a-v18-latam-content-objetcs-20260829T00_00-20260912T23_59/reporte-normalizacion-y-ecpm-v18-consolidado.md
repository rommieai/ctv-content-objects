# Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v18)

**Fuente:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, 426,223,575,360 requests; métricas de v18).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v18-consolidado.json` e `inventory-consolidado-v10-a-v18-enriquecido.csv` (no versionado).

eCPM ponderado global (>0): 4.04 (v18 solo: 4.02). Tráfico monetizado (eCPM > 0): 53.3% de los requests (v18 solo: 57.9%).

*Nota: el 13.0% de los requests del consolidado viene de llaves de cortes anteriores que ya no existen en v18. Los precios de este reporte son los del consolidado.*

---

# PARTE A — Género normalizado

86.2% de filas con al menos un género canónico; 261,228 filas multi-género. Distribución multi-etiqueta, % sobre las filas con género útil:

| Género | % filas llenas | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|
| drama | 31.0% | $3.51 | 48.2% |
| terror | 12.3% | $3.82 | 35.0% |
| documental | 11.8% | $5.70 | 43.1% |
| comedia | 11.2% | $3.43 | 53.7% |
| accion | 9.8% | $4.73 | 42.2% |
| thriller | 9.2% | $4.00 | 24.5% |
| romance | 6.4% | $3.87 | 44.9% |
| infantil-familia | 5.3% | $5.76 | 35.3% |
| otros/desconocido | 4.7% | $6.38 | 20.9% |
| entretenimiento | 4.7% | $4.75 | 69.8% |
| crimen | 4.3% | $4.51 | 30.6% |
| aventura | 4.2% | $5.34 | 34.1% |
| deportes | 3.9% | $2.23 | 75.0% |
| musica | 3.1% | $4.35 | 29.8% |
| sci-fi | 3.0% | $4.08 | 27.9% |
| misterio | 2.9% | $4.78 | 19.9% |
| fantasia | 2.7% | $4.58 | 24.0% |
| pelicula (generico) | 2.2% | $4.91 | 47.9% |
| anime | 2.1% | $6.18 | 54.9% |
| western | 1.9% | $3.67 | 25.9% |

# PARTE B — Rating en franjas de edad

| Franja | % filas | % filas llenas | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 7.0% | 9.3% | $4.63 | 70.5% |
| 7+ | 0.4% | 0.6% | $5.16 | 32.7% |
| 10+ | 10.1% | 13.5% | $4.92 | 55.2% |
| 13-15 | 22.0% | 29.4% | $3.71 | 53.8% |
| 16-17 | 7.3% | 9.7% | $5.78 | 22.9% |
| 18+ / adulto | 17.6% | 23.5% | $4.34 | 39.6% |
| sin clasificar | 8.9% | 11.8% | $3.55 | 52.3% |
| sin dato | 25.1% | — | $3.49 | 55.2% |
| no mapeado | 1.7% | 2.3% | $2.68 | 33.2% |

*"% filas" incluye la fila vacía ("sin dato"); "% filas llenas" renormaliza sobre el 74.9% restante. "sin clasificar" (`nr`, `Unrated`) y "no mapeado" (`dv-t`, `mpaa_r`, `movie-pg-13`, `pg 13`, `dv-g`) sí son dato presente. Equivalencias de la escala nueva: `All Ages` = todos, `Teen` = 10+, `Teen Plus` = 13-15, `Adults` = 18+.*

# PARTE C — El inventario que monetiza (eCPM > 0)

187,172 filas (17.5%) concentran el 53.3% del tráfico.

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 61.4% | 20.0% | $3.20 |
| Argentina | 57.1% | 19.8% | $6.10 |
| Guatemala | 55.7% | 29.4% | $6.67 |
| Costa Rica | 46.0% | 30.8% | $6.12 |
| Perú | 37.8% | 16.4% | $4.67 |
| Chile | 36.1% | 21.9% | $6.11 |
| Panamá | 32.5% | 6.8% | $1.91 |
| Colombia | 27.5% | 13.6% | $5.03 |
| Ecuador | 15.2% | 5.3% | $6.01 |

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | 16.3% | 58.5% | $5.67 |
| TCL ADS - Springserve | 13.9% | 78.9% | $4.95 |
| iion Pty Ltd | 13.0% | 43.5% | $4.72 |
| Televisa Univision via SpringServe | 8.1% | 84.0% | $2.26 |
| Equativ | 7.9% | 82.7% | $2.61 |
| TCL ADs (APAC) | 7.8% | 74.2% | $5.64 |
| Televisa Univision via OB | 5.8% | 97.6% | $0.97 |
| Coocaa (SKYWORTH) | 5.3% | 76.9% | $3.26 |
| Vidaa | 4.7% | 84.0% | $1.48 |
| Zeasn (WhaleLive) | 4.5% | 98.6% | $2.56 |
| TV Azteca - Springserve | 3.2% | 45.4% | $7.31 |
| Vidaa APAC Hisense Headquarter | 1.9% | 79.2% | $1.97 |

## Señales sobre el tráfico monetizado

| Dimensión | Segmento | % del tráfico vendido | eCPM pond. |
|---|---|---:|---:|
| Idioma | español (`es` + `Spanish`) | 43.4% | $4.48 |
| Idioma | inglés (`en` + `English`) | 19.3% | $3.21 |
| Idioma | sin dato | 34.8% | $3.99 |
| Livestream | live (`1`) | 49.5% | $4.00 |
| Livestream | sin dato | 50.5% | $4.07 |
| Título | con título | 64.8% | $4.07 |
| Título | sin título | 35.2% | $3.98 |

*Outliers: los eCPM de 194.3, 135.3, 102.9 (TCL APAC / MovieArk Perú) están solo en el consolidado por llaves viejas; en v18 el máximo es 80.0 (Pluto LATAM via SpringServe, México).*
