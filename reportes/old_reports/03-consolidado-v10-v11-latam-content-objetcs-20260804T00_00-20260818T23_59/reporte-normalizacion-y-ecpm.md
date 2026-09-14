# Reporte — Normalización de género/rating y análisis del inventario monetizado

**Fuente:** `inventory-consolidado-v10-v11.csv` (525,178 filas, 428,140,540,640 requests).
**Entregables:**
- `inventory-consolidado-enriquecido.csv` — el consolidado + 2 columnas nuevas: `genero_normalizado` (géneros canónicos separados por `;`) y `rating_franja` (franja de edad)
- `reporte-normalizacion-y-ecpm.json` — toda la data de este reporte (distribuciones completas, mapeos fallidos, tops)

---

# PARTE A — Género normalizado

## Método

Cada valor de `contentGenre` se partió por comas (y `/`, `&`, `;`), se pasó a minúsculas y cada token se mapeó a un catálogo de **34 géneros canónicos** vía diccionario de sinónimos (inglés + español: `horror`→terror, `suspense/suspenso`→thriller, `kids/children/family`→infantil-familia, `biography/history/nature/science`→documental, etc.). Una fila puede quedar con varios géneros (multi-etiqueta), así que los porcentajes suman más de 100.

**Cobertura del mapeo:** 91.9% de las filas quedó con al menos un género canónico (482,421). El resto: 6,720 sin dato y 36,037 (6.9%) con género que no se pudo mapear. 222,778 filas (42%) son multi-género.

**Nuevos formatos sucios que destapó la normalización** (en los tokens no mapeados):
- La familia **`genre_*`** (`genre_drama`, `genre_action`, `genre_comedy`... ~15K filas): un publisher manda el nombre de la variable con prefijo en vez del valor.
- Géneros que no son géneros: `short`, `relaxing`, `culture`, `opinion`, `en español` (¡el idioma metido como género!), `live` (livestream metido como género), `classic tv`, `review`.
- Compuestos que el split no resuelve (`western drama`, `romance movies`, `crime and mystery movies`) — mapeables con una segunda pasada si hiciera falta.

## Distribución (ordenada por % de requests; multi-etiqueta)

| Género | % filas | % requests | eCPM pond. (>0) | % del tráfico del género que monetiza |
|---|---:|---:|---:|---:|
| drama | 30.1% | 29.8% | 4.51 | 42.8% |
| thriller | 12.1% | 11.8% | 4.77 | 38.2% |
| comedia | 13.2% | 11.8% | 4.43 | 45.8% |
| terror | 11.5% | 11.5% | 4.80 | 35.9% |
| accion | 10.1% | 8.7% | 5.21 | 41.5% |
| romance | 8.2% | 8.3% | 5.38 | 42.9% |
| documental | 12.0% | 7.7% | 5.38 | 38.3% |
| entretenimiento | 4.1% | 7.6% | 5.61 | **74.1%** |
| infantil-familia | 6.7% | 5.3% | 4.99 | 46.2% |
| deportes | 3.9% | 4.7% | **2.84** | **69.3%** |
| crimen | 5.5% | 4.4% | 5.17 | 40.6% |
| otros/desconocido | 7.0% | 4.1% | 4.98 | 31.1% |
| aventura | 5.2% | 3.8% | **5.67** | 38.5% |
| misterio | 4.4% | 3.5% | 5.08 | 37.3% |
| musica | 4.6% | 3.1% | 4.19 | 49.6% |
| noticias | 1.7% | 3.0% | 5.12 | **66.3%** |
| sci-fi | 3.2% | 2.4% | 4.49 | 33.0% |
| fantasia | 3.6% | 2.3% | 4.96 | 33.4% |
| anime | 2.3% | 2.1% | **6.16** | 44.2% |
| película (genérico) | 2.4% | 1.4% | 5.90 | 51.7% |
| reality | 1.6% | 1.1% | 4.80 | 48.0% |
| western | 1.7% | 1.0% | 4.45 | **26.4%** |
| animacion | 1.1% | 0.9% | 3.38 | **78.3%** |
| gastronomia | 0.6% | 0.7% | 5.14 | 66.1% |
| videojuegos | 0.6% | 0.6% | 5.54 | 64.9% |
| concursos | 0.2% | 0.5% | 5.94 | 74.9% |
| telenovela | 0.3% | 0.6% | 4.36 | 42.7% |
| (resto: bélico, lifestyle, viajes, talk, religión, educación...) | <1% c/u | <0.9% c/u | 3.7–5.0 | 29–54% |

## Conclusiones del género normalizado

1. **El inventario es 2/3 ficción de catálogo**: drama+thriller+terror+comedia+acción+romance suman ~80% del tráfico (con solape multi-género). La "larga cola de 7,700 géneros" se reduce a ~15 géneros que importan.
2. **El precio por género se mueve poco (4.2–6.2), pero la facilidad de venta se mueve muchísimo (26%–78%)**. Los géneros "de canal lineal/FAST" — animación 78%, concursos 75%, entretenimiento 74%, deportes 69%, noticias/gastronomía 66% — se venden al doble de tasa que el catálogo de películas (terror 36%, sci-fi 33%, western 26%). La demanda compra canales, no películas B.
3. **Deportes es la anomalía**: el género que más fácil se vende (69%) pero al peor precio del dataset (2.84). Parece inventario deportivo vendido por volumen/deals baratos, no premium. Al revés, **anime es el género mejor pagado (6.16)** con volumen decente (2% del tráfico) — nicho con demanda que puja.
4. **Aventura, romance y documental pagan por encima de la media** (5.4–5.7) — junto con anime, son los géneros donde priorizar paquetes si el objetivo es yield.

---

# PARTE B — Rating normalizado a franjas de edad

## Método

Los 182 valores de `contentRating` se mapearon a 7 franjas: **todos** (g, tv-g, tv-y, atp, l...), **7+** (tv-y7, 6, 7), **10+** (pg, tv-pg, 10), **13-15** (pg-13, tv-14, 12–15, b, b15...), **16-17** (r, 16, m), **18+/adulto** (tv-ma, nc-17, 18, c, d, x), **sin clasificar** (nr, not rated, banned) — más "sin dato" (centinelas) y "no mapeado".

**Cobertura: 97.1% de las filas mapeadas.** En el 2.9% no mapeado aparecieron más familias sucias: `dv-t`/`dv-g`/`dv-ma` (prefijo "dv-"), `mpaa_r`/`mpaa_pg` (otro prefijo de sistema), `tv-14.tv-pg` (dos ratings pegados), **`{{content_rating` (otra macro sin reemplazar, 330 filas)**, `-10`/`-12` (sistema francés), `12a` (UK), `tp`/`su` (España "todos los públicos" / "sin restricción"), `18 anos` (portugués). Con ~15 sinónimos más, la cobertura pasaría del 99%.

## Distribución

| Franja | % filas | % requests | eCPM pond. (>0) | % del tráfico de la franja que monetiza |
|---|---:|---:|---:|---:|
| todos | 7.9% | 10.3% | 5.20 | **71.3%** |
| 7+ | 0.7% | 0.7% | 5.32 | 44.5% |
| 10+ | 10.3% | 10.6% | **5.46** | 55.3% |
| 13-15 | 24.5% | **32.4%** | 4.87 | 54.8% |
| 16-17 | 12.5% | 9.2% | 5.25 | **36.4%** |
| 18+ / adulto | 15.9% | 14.4% | 5.41 | **37.3%** |
| sin clasificar | 10.1% | 7.5% | **3.98** | 44.0% |
| sin dato | 15.3% | 11.8% | 4.87 | 49.3% |
| no mapeado | 2.9% | 3.2% | 3.95 | 63.0% |

## Conclusiones del rating normalizado

1. **El grueso del inventario es "teen" (13-15): un tercio del tráfico.** Sumando de "todos" hasta 13-15, el **54% del tráfico es apto para audiencias generales** — más de lo que aparentaban los 182 valores crudos.
2. **El contenido 16+/adulto (23.6% del tráfico) se vende a la mitad de tasa** que el familiar: 36-37% de sell-through vs 71% de "todos". Los compradores están filtrando madurez activamente. Y ojo: NO pagan menos por él (5.25-5.41) — simplemente lo compran menos anunciantes.
3. **El inventario "sin clasificar" (nr/banned) sufre castigo de precio real: 3.98 vs ~5.2 del clasificado (-24%)**. Es el argumento con números para exigirles rating a los publishers: clasificar sube el precio una cuarta parte.
4. La franja "todos" tiene el mejor sell-through del dataset (71%) — el inventario family-safe es el más líquido. Kids/familia + rating "todos" es probablemente el paquete más fácil de vender de todo el archivo.

---

# PARTE C — El inventario que monetiza (eCPM > 0)

## El universo monetizado

**90,146 filas (17.2%) concentran 218,698 millones de requests = el 51.1% de todo el tráfico.** La mitad del inventario (en volumen) se vende; lo que no se vende es sobre todo catálogo de cola.

## Sell-through por país (% del tráfico del país que corre por combinaciones con revenue)

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| Paraguay | **63.9%** | 12.2% | 5.94 |
| México | 58.5% | 18.4% | 4.44 |
| Costa Rica | 56.8% | **37.5%** | 5.94 |
| Puerto Rico | 55.1% | 11.2% | 8.14 |
| Argentina | 53.6% | 19.6% | 6.25 |
| Chile | 35.0% | 19.5% | **8.33** |
| Perú | 31.4% | 18.4% | 6.09 |
| Guatemala | 26.8% | 22.8% | 4.62 |
| Honduras | 24.6% | 21.2% | 4.00 |
| Ecuador | 22.1% | 6.0% | 7.54 |
| Colombia | 21.5% | 12.3% | 3.00 |
| Rep. Dominicana | 16.3% | 8.2% | 5.45 |
| Panamá | 12.6% | 10.8% | 4.26 |
| Uruguay | 12.4% | 2.6% | 5.45 |
| El Salvador | **8.9%** | 14.3% | 6.43 |
| Nicaragua | 44.8% | 30.8% | 7.79 |
| Bolivia | 28.5% | 0.2% | 1.99 |
| Venezuela | **0%** | 0% | — |

Lectura: México monetiza mucho volumen a precio medio; Chile monetiza poco pero carísimo; Colombia falla en ambas (21% y 3.00 — el mercado enfermo del dataset); Bolivia es un espejismo (2 filas concentran el 28.5%).

## Quién se lleva el tráfico monetizado (por publisher)

| Publisher | Share del tráfico monetizado | % de su propio tráfico que monetiza | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | **17.5%** | 63.3% | 5.94 |
| TCL ADS - Springserve | 17.1% | 78.9% | 5.04 |
| TCL ADs (APAC) | 13.4% | 76.4% | 6.21 |
| Televisa Univision via SpringServe | 8.3% | **92.8%** | **2.24** |
| TV Azteca - Springserve | 8.1% | 75.2% | **8.55** |
| Coocaa (SKYWORTH) | 7.9% | 95.1% | 3.50 |
| Televisa Univision via OB | 5.5% | **97.6%** | **1.30** |
| iion Pty Ltd | 5.3% | 36.5% | 3.61 |
| Equativ | 4.8% | 76.7% | 2.77 |
| Zeasn (WhaleLive) | 3.1% | 91.5% | **10.72** |
| ...OTTera.tv | 0.7% | **1.45%** | 7.11 |
| ...Select Plus | 0.2% | **2.2%** | 7.29 |
| ...Pluto LATAM | 0.1% | 24.7% | 10.05 |

**Tres modelos de negocio saltan a la vista:**
- **Broadcasters con fill casi total a precio bajo**: TelevisaUnivision monetiza el 93-98% de su tráfico pero a 1.30-2.24 — parece inventario vendido por volumen/garantizado. TV Azteca es lo contrario: 75% de fill a 8.55, el premium real del dataset.
- **OEMs con fill alto y precio medio**: TCL (76-79% a 5-6.2), Coocaa (95% a 3.5), Vidaa (82% a 1.4).
- **Agregadores que casi no venden**: OTTera — el dueño del 23.8% de las filas del dataset — **solo monetiza el 1.45% de su tráfico**. Select Plus igual (2.2%). Todo ese catálogo de películas B replicado en 18 países prácticamente no genera revenue. Eso explica el 83% de filas en cero del dataset: es el catálogo muerto de los agregadores.
- Rarezas de precio alto: Zeasn/WhaleLive a 10.72 (con 91.5% fill — el publisher más valioso por request), Pluto a 10.05 (pero solo monetiza 25%).

## Por app (bundle), idioma y señales

- **Apps**: The Roku Channel 17.2% del tráfico monetizado (a 5.95), MovieArk 16.3% (5.41), Live TV 9.8% (2.85), ViX-Roku 8.4% (2.52), Coolita 8.3% (3.52), **Tubi 8.1% a 8.54** y **BrowseHere 4.3% a 7.83** (las dos apps "caras"), TCL Channel 7.7% (6.74), ViX-Android 6.4% (1.34 — ViX vende barato en todas sus variantes).
- **Idioma del tráfico monetizado**: español 50.4% a **5.63** vs inglés 30.4% a 5.03 — **el contenido en español no solo domina el tráfico vendido: paga ~12% más que el inglés**. El tráfico sin idioma se castiga fuerte (2.91). Curiosidad: el catalán paga 7.15 (el catálogo "catalunya über alles" tiene comprador).
- **Live vs no declarado**: mitad y mitad del tráfico monetizado, precio casi idéntico (5.02 vs 4.93) — el flag livestream no discrimina precio.
- **Título presente — matiz importante**: el tráfico monetizado SIN título es el 30% y paga MÁS (5.79 vs 4.62). No contradice la correlación por fila de los reportes anteriores; significa que el inventario premium de alto volumen (Roku EPG, WhaleLive) se vende caro *a pesar* de ocultar el título — su precio viene de la relación comercial, no de la metadata. La metadata correlaciona con precio en la cola, no en los gigantes.

## Outliers de precio (top eCPM)

**16 de las 20 filas más caras del dataset son de Perú**, encabezadas por el eCPM de 200.0 exacto (TelevisaUnivision/ViX, telenovela "La hija del mariachi", 57K requests) y seguidas de valores 45-107 en MovieArk/ViX/Pluto Perú, casi todos con volúmenes chicos (30-500K requests). Un país secundario concentrando todos los precios extremos, con un valor "redondo" de 200, huele a **problema de moneda o de deal puntual en la integración peruana** (¿PEN en vez de USD?). Recomendación: excluir eCPM > ~30 de cualquier promedio hasta aclararlo con la fuente — son 0.2% del tráfico pero distorsionan los promedios por fila de Perú (su 6.09 ponderado bajaría).

---

# Qué más valdría la pena hacer después

En orden de valor probable:

1. **Mapa bundle→servicio** (ViX = 4 bundles, Tubi = 3, Plex = 2...): permitiría responder "cuánto alcance y a qué precio tiene cada servicio" — hoy ViX aparece partido en 4 filas de cualquier ranking. Es una tabla de ~50 mapeos manuales.
2. **Análisis de supply path**: la misma app vendida por varios sellers (Tubi via OneFox vs via TV Azteca; Televisa via SpringServe vs via OB a precios 2.24 vs 1.30) — comparar precio del mismo inventario por ruta dice qué camino comprar.
3. **Auditoría de outliers de Perú** y del 200.0 con la fuente antes de usar promedios de ese país.
4. **Corte de brand safety por app**: cruzar franja adulto + sin clasificar por bundle/publisher para armar block/allow lists con números.
5. **Pedir exportaciones segmentadas** (por país o publisher) para superar el límite de 512K filas del reporte y recuperar la cola que hoy queda truncada.
