# Reporte — Normalización de género/rating y análisis del inventario monetizado (consolidado v10+v11+v12)

**Fuente:** `inventory-consolidado-v10-v11-v12.csv` (539,190 filas, 429,176,186,240 requests; métricas del corte v12 cuando la llave existe en varios).
**Generado con:** `scripts/normalizar_monetizar.py`
**Entregables:**
- `inventory-consolidado-v10-v11-v12-enriquecido.csv` — el consolidado + `genero_normalizado` (géneros canónicos separados por `;`) y `rating_franja` (no versionado en el repo, se regenera con el script)
- `reporte-normalizacion-y-ecpm-v12-consolidado.json` — toda la data de este reporte

**Contexto importante:** respecto a la versión anterior de este análisis (sobre v10+v11), los patrones estructurales se mantienen casi idénticos, pero **v12 recalculó los eCPM a la baja en varias filas gigantes** (desapareció el outlier de 200.0, WhaleLive pasó de 10.7 a 4.8 de ponderado, TV Azteca de 8.55 a 5.34). Donde ese recálculo cambia una conclusión, lo señalo explícitamente.

---

# PARTE A — Género normalizado

## Método y cobertura

Split por comas (`/`, `&`, `;`), minúsculas, y mapeo por diccionario de sinónimos a ~34 géneros canónicos. **92% de las filas quedó con al menos un género canónico** (6,816 sin dato; 38,827 con género no mapeable — la familia `genre_*`, "short", "culture", "en español" y demás basura ya documentada). 227,749 filas (42%) son multi-género, así que los porcentajes suman más de 100.

## Distribución (ordenada por % de requests)

| Género | % filas | % requests | eCPM pond. (>0) | % del tráfico del género que monetiza |
|---|---:|---:|---:|---:|
| drama | 29.9% | 30.0% | 4.48 | 42.8% |
| comedia | 13.1% | 11.9% | 4.38 | 45.8% |
| thriller | 12.0% | 11.9% | 4.72 | 37.7% |
| terror | 11.6% | 11.5% | 4.74 | 35.8% |
| accion | 10.1% | 8.7% | 5.16 | 41.6% |
| romance | 8.1% | 8.4% | 5.38 | 43.0% |
| documental | 11.9% | 7.8% | 5.34 | 38.1% |
| entretenimiento | 4.1% | 7.6% | 5.61 | **73.8%** |
| infantil-familia | 6.6% | 5.5% | 5.23 | 46.3% |
| deportes | 3.9% | 4.6% | **2.86** | **68.7%** |
| crimen | 5.4% | 4.5% | 5.15 | 40.0% |
| otros/desconocido | 7.0% | 4.1% | 4.92 | 30.8% |
| aventura | 5.1% | 3.9% | **5.83** | 38.8% |
| misterio | 4.3% | 3.5% | 5.05 | 36.3% |
| musica | 4.6% | 3.1% | 4.17 | 49.3% |
| noticias | 1.7% | 3.0% | 5.22 | **65.5%** |
| sci-fi | 3.2% | 2.4% | 4.46 | 32.6% |
| fantasia | 3.6% | 2.3% | 5.01 | 33.1% |
| anime | 2.2% | 2.2% | **6.54** | 44.4% |
| película (genérico) | 2.4% | 1.4% | 5.93 | 51.6% |
| reality | 1.6% | 1.1% | 4.77 | 47.6% |
| (cola: western, animación, gastronomía, videojuegos, concursos, telenovela...) | <1.5% c/u | <1% c/u | 2.9–6.0 | 24–78% |

## Conclusiones — género

1. Se confirma con el universo completo: **el precio por género varía poco (4.2–6.5) pero la facilidad de venta varía 3x**. Los géneros de canal FAST (entretenimiento 74%, deportes 69%, noticias 66%) doblan el sell-through del catálogo de películas (terror 36%, sci-fi 33%).
2. **Deportes sigue siendo la anomalía** (el más fácil de vender, el peor pagado: 2.86) y **anime consolida su lugar como el género mejor pagado (6.54)**, ahora seguido de aventura (5.83) y película genérica (5.93).
3. La estabilidad de esta tabla a través de tres cortes del reporte le da confianza: estos patrones no son ruido de una exportación.

---

# PARTE B — Rating normalizado a franjas de edad

## Cobertura

97.2% de filas mapeadas a las 7 franjas (todos / 7+ / 10+ / 13-15 / 16-17 / 18+ / sin clasificar); el "no mapeado" (2.8%) sigue siendo la colección de formatos exóticos ya catalogada (`dv-t`, `mpaa_r`, `-12`, `12a`, `18 anos`, `{{content_rating`).

## Distribución

| Franja | % filas | % requests | eCPM pond. (>0) | % del tráfico de la franja que monetiza |
|---|---:|---:|---:|---:|
| todos | 7.8% | 10.3% | **5.28** | **71.8%** |
| 7+ | 0.7% | 0.7% | 5.28 | 43.9% |
| 10+ | 10.3% | 10.7% | 4.96 | 54.1% |
| 13-15 | 24.7% | **32.3%** | 4.37 | 53.9% |
| 16-17 | 12.5% | 9.3% | 5.21 | **36.0%** |
| 18+ / adulto | 16.1% | 14.5% | 5.16 | **36.5%** |
| sin clasificar | 10.0% | 7.6% | 4.06 | 43.5% |
| sin dato | 15.2% | 11.5% | **3.34** | 51.2% |
| no mapeado | 2.8% | 3.1% | 3.60 | 61.2% |

## Conclusiones — rating

1. Sin cambios estructurales: un tercio del tráfico es "teen" (13-15) y el 54% es apto para audiencias generales. **El contenido 16+/adulto (24% del tráfico) se sigue vendiendo a la mitad de tasa que el familiar** (36% vs 72%) sin pagar menos.
2. El castigo por no clasificar se mantiene y ahora se ve doble: "sin clasificar" paga 4.06 y **"sin dato" cayó a 3.34** — el inventario sin rating (explícito o ausente) transa un 20–35% por debajo del clasificado (~4.4–5.3). Con el recálculo de v12 el descuento del "sin dato" se profundizó (era 4.87): las filas caras sin rating (WhaleLive) eran justamente las que se corrigieron a la baja.
3. Matiz nuevo del recálculo: la franja 13-15, la más grande, quedó como la más barata de las clasificadas (4.37) — ahí vive el volumen de Televisa (tv-14 masivo a precio bajo).

---

# PARTE C — El inventario que monetiza (eCPM > 0)

## El universo monetizado

**92,088 filas (17.1%) concentran el 50.7% de todo el tráfico.** La mitad del inventario en volumen se vende; el resto es catálogo de cola de los agregadores.

## Por país (los que pediste priorizar, más el resto de grandes)

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 57.6% | 17.9% | 3.78 |
| Argentina | 54.0% | 20.0% | 6.34 |
| Chile | 35.1% | 19.4% | **8.17** |
| Colombia | 21.9% | 12.2% | **3.01** |
| Perú | 32.0% | 18.6% | 6.05 |
| Costa Rica | 56.8% | **37.7%** | 5.82 |
| Puerto Rico | 53.5% | 11.2% | 8.11 |
| Ecuador | 22.1% | 6.2% | 7.32 |

México mantiene su patrón (mucho volumen vendido a precio medio, ahora 3.78 tras el recálculo de WhaleLive); Chile sigue siendo el precio premium de los grandes; Colombia sigue enferma en ambas dimensiones (21.9% y 3.01).

## Por publisher

| Publisher | Share del tráfico monetizado | % de su propio tráfico que monetiza | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | **17.6%** | 63.8% | 5.96 |
| TCL ADS - Springserve | 17.5% | 78.6% | 5.19 |
| TCL ADs (APAC) | 13.3% | 76.1% | 6.20 |
| Televisa Univision via SpringServe | 8.0% | **92.3%** | 2.23 |
| Coocaa (SKYWORTH) | 7.9% | 94.9% | 3.47 |
| TV Azteca - Springserve | 7.4% | 70.8% | **5.34** |
| iion Pty Ltd | 5.6% | 37.6% | 3.63 |
| Televisa Univision via OB | 5.3% | **97.5%** | 1.31 |
| Equativ | 5.0% | 77.8% | 2.75 |
| Zeasn (WhaleLive) | 3.1% | 91.5% | **4.76** |
| ...OTTera.tv | ~0.7% | **~1.5%** | ~7 |

Los tres modelos se sostienen — broadcasters con fill casi total a precio bajo (Televisa 92–98% a 1.31–2.23), OEMs con fill alto a precio medio, y **agregadores que casi no venden (OTTera: dueño del 24% del catálogo, monetiza ~1.5% de su tráfico)** — pero el piso "premium" se comprimió con v12: **TV Azteca bajó de 8.55 a 5.34 y Zeasn/WhaleLive de 10.72 a 4.76**. El único premium que sobrevive al recálculo con volumen es la dupla Roku/TCL APAC (~6) y, en precio puro, los mercados Chile/Puerto Rico (~8).

## Por app, idioma y señales

- **Apps:** The Roku Channel 17.3% del tráfico monetizado (5.97), MovieArk 15.5% (5.31), Live TV 10.5% (2.90), ViX-Roku 8.6% (2.51), TCL Channel 8.4% (6.87), Coolita 8.3% (3.49), Tubi 7.4% (5.34), **BrowseHere 4.6% a 7.97 — la app más cara con volumen**. Las variantes de ViX venden barato en todas las plataformas (1.3–2.5).
- **Idioma:** el español es el **50.2% del tráfico monetizado a 5.18 vs inglés 30.2% a 4.37 — la prima del español subió a +19%** (era +12% antes del recálculo: los precios que cayeron eran mayormente de filas en inglés o sin idioma). El tráfico sin idioma paga 2.98.
- **Live:** 48.7% del tráfico monetizado es live confirmado, con leve prima (4.74 vs 4.37).
- **Título — conclusión corregida por v12:** en el análisis sobre v10+v11 el tráfico sin título pagaba *más* (5.79 vs 4.62) por las filas gigantes de Roku/WhaleLive; **con las métricas recalculadas se invierte: el tráfico con título paga 4.63 vs 4.35 sin título**. La supuesta prima del inventario opaco era en buena parte un artefacto de los precios que v12 corrigió. Queda la lectura sana: la metadata correlaciona con precio, y el inventario premium opaco ya no es la excepción que era.

## Outliers

El top de precios sigue concentrado en Perú (máximo 76.7, TCL/MovieArk "abandoned: trailer"; ViX con telenovelas a 45–68), pero ya sin el 200.0 — v12 corrigió esa fila. La recomendación se mantiene: **excluir eCPM > ~30 de cualquier promedio de Perú** hasta validar esa integración con la fuente; son volúmenes chicos que distorsionan.

---

## Síntesis

1. **Lo estructural es estable a través de los tres cortes** (sell-through por género y franja, los tres modelos de publisher, la paradoja español/inglés, el catálogo muerto de los agregadores): son conclusiones sobre las que se puede construir.
2. **Lo que no es estable es el nivel de precios**: v12 recortó los eCPM altos (TV Azteca −38%, WhaleLive −56%, el outlier 200 eliminado) y eso movió el ponderado global de ~4.98 a 4.55, invirtió la conclusión del "premium sin título" y profundizó el castigo del inventario sin rating. Cualquier cifra de precio que se comparta debe decir de qué versión del reporte sale.
3. Con el recálculo, los argumentos comerciales quedan así: el español paga +19%, clasificar el contenido vale +20–35% de precio, el inventario family-safe es el más líquido (72% de sell-through), y anime/aventura son los géneros a empaquetar por yield.
