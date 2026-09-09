# Reporte — Análisis por publisher, consolidado v10 a v16 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v16.csv` (810,933 filas, 365,377,125,360 requests; métricas de v16).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v16-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~88% del tráfico). Porcentajes sobre las filas de cada publisher.

**Antes de leer los movimientos:** el corte v16 trae un cambio de formato en el reporte (ver el detallado por país): el 28% de sus filas llega con género en mayúscula, rating en escala nueva (`Teen`, `Adults`…) e idioma como nombre (`English`), y en esas filas rating e idioma vienen mayormente vacíos. **Afecta a los 12 publishers por igual** (entre el 20% y el 51% de las filas de cada uno en v16), así que las caídas de rating/idioma de este reporte no son mérito ni culpa de ningún partner. Cambia también el top 12: **Zeasn (WhaleLive) entra** y **Select Plus sale** (2.0% de los requests).

**Movimientos en el top vs el corte anterior:** Roku sigue creciendo (15.0% → **16.6%** de los requests) y ya casi empata con OTTera (17.4%, venía de 23.0% — su catálogo muerto pierde peso relativo); iion subió (10.1% → 11.2%) y **desplazó a TCL Springserve (9.5%) del tercer puesto**; Equativ (4.8% → 5.7%), TV Azteca (3.6% → 4.5%) y Televisa OB (2.6% → 3.4%) ganan cuota en el tráfico mexicano; TCL APAC se enfrió (5.9% → 5.4%).

## Tabla comparativa

| Publisher | % filas no vacías | % filas eCPM=0 | eCPM pond. | % no vacías: category | % no vacías: language | % no vacías: title | % no vacías: length |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 21.9% | **99.9%** | 6.88 | 38.3% | 89.8% | 99.7% | 1.1% |
| Roku - oRTB | 1.5% | 97.7% | 5.40 | **98.2%** | 84.2% | **26.6%** | **78.9%** |
| iion Pty Ltd | 17.8% | 89.5% | 5.49 | 0.7% | **3.7%** | 99.8% | 3.3% |
| TCL ADS - Springserve | 12.5% | 62.2% | 5.13 | 0.7% | 75.6% | 99.6% | 1.4% |
| Equativ - oRTB CTV | 2.7% | 80.3% | 2.59 | 24.5% | 77.0% | 85.7% | 22.9% |
| TCL ADs (APAC) | 11.6% | **54.3%** | 5.58 | 0.9% | 82.1% | 99.8% | 2.5% |
| Televisa Univision via SpringServe | 1.5% | 61.3% | 2.26 | 0.0% | 50.3% | 85.9% | 53.2% |
| Coocaa (SKYWORTH) | 1.7% | 59.3% | 2.79 | **100%** | 74.9% | **100%** | **100%** |
| TV Azteca - Springserve | 0.3% | 93.1% | 5.83 | 0.3% | 98.6% | **0.2%** | 0.2% |
| Televisa Univision via OB | 0.6% | **45.9%** | **1.27** | 0.0% | 93.5% | **0.0%** | 0.0% |
| Vidaa | 1.9% | 70.4% | **1.35** | 85.8% | 89.3% | 80.5% | 2.4% |
| Zeasn Europe B.V. (WhaleLive) | 0.1% | 59.0% | 3.06 | 0.0% | 97.2% | **0.0%** | 0.0% |

*"% filas no vacías" equivale aquí al % de filas del dataset (Publisher viene en el 100% de las filas). El orden de la tabla — y la numeración de los perfiles — sigue el peso en requests de cada publisher (data completa en el JSON).*

## Perfiles (con los datos del corte v16)

**1. OTTera.tv** (21.9% / 17.4% · pond. 6.88). Pierde peso en requests (23.0% → 17.4%) sin cambiar de naturaleza: revende las 4 apps TCL, metadata descriptiva casi perfecta y **monetiza el 0.1% de sus filas**. El formato nuevo le vació parte del idioma (99.7% → 89.8%) y del rating (→ 90.0%). Sigue siendo el origen del `[IAB1-22]` inválido (13.0% de sus filas).

**2. Roku - oRTB** (1.5% / **16.6%** · pond. 5.40). Segundo corte seguido creciendo (14.3% → 15.0% → 16.6%), ya a un punto de OTTera. Estructura intacta (categoría 98.2%, duración 78.9%), identidad oculta (**5 títulos distintos**: `roku` 11.9%, `epg` 10.3%, `vod` 3.9%; series en hashes MD5 — 52.2% el hash del vacío). Su tasa de monetización cayó (96.6% → 97.7% en cero) y, con el formato nuevo, hasta Roku perdió idioma (94.8% → 84.2%) y rating (→ 86.7%).

**3. iion Pty Ltd** (17.8% / 11.2% · pond. 5.49). **Sube al tercer puesto** y es el publisher con más filas duplicadas por el formato nuevo (34% de las suyas en v16). Su agujero de siempre se agrava: **3.7% de idioma** (venía de 5.0%) cuando sus rutas hermanas TCL superan el 75%. El precio mejora por cuarto corte (4.21 → 4.47 → 4.99 → **5.49**), ya por encima de TCL Springserve.

**4. TCL ADS - Springserve** (12.5% / 9.5% · 62.2% en cero · pond. 5.13). Baja al cuarto puesto (10.6% → 9.5%), sell-through algo peor (59.1% → 62.2% en cero) y precio levemente mejor (5.06 → 5.13). Sigue siendo la ruta TCL sana en lo descriptivo (título 99.6%) y nula en lo estructural (`[-7]` 99.3%). #2 del tráfico monetizado (14.5%).

**5. Equativ - oRTB CTV** (2.7% / 5.7% · pond. 2.59). El exchange sigue ganando cuota (4.2% → 4.8% → 5.7%) y sube al #3 del tráfico monetizado (8.9%). México 84.5%, App Name perdido en el 25.7%, categoría 24.5% (con [IAB12] 12.4% — contagiado del inventario Vidaa/ViX que revende). Precio bajo estable (2.58 → 2.59).

**6. TCL ADs (APAC)** (11.6% / 5.4% · **54.3% en cero** · pond. 5.58). Sigue siendo la ruta TCL que mejor convierte (46% de filas monetizadas), pero se enfría en volumen (5.9% → 5.4%). Y sigue siendo la fábrica de outliers: **los 6 eCPM más altos del dataset son suyos, todos MovieArk Perú**, encabezados por un nuevo récord de **194.3** ("blink and friends").

**7. Televisa Univision via SpringServe** (1.5% / 5.2% · 61.3% en cero · pond. 2.26). ViX multi-plataforma con el modelo broadcaster de siempre: metadata casi siempre llena, precio bajo y bajando (2.66 → 2.44 → **2.26**). Ojo: es el publisher del top donde el formato nuevo más pega en requests (32% de los suyos en v16), y su idioma cayó de 60.9% a 50.3%. El rating `Teen Plus` ya es el 7.8% de sus filas.

**8. Coocaa, a SKYWORTH company** (1.7% / 4.9% · 59.3% en cero · pond. 2.79). El content object perfecto en lo estructural (categoría, título, duración y livestream al 100%, series 90.6%) pero **el formato nuevo lo alcanzó de lleno: 51% de sus filas en v16 vienen en la escritura nueva**, y su rating cayó al 66.3% (`Teen` 9.6%, `All Ages` 9.0%). Precio a la baja (3.01 → 2.79) y sell-through peor (48.0% → 59.3% en cero).

**9. TV Azteca - Springserve** (0.3% / 4.5% · 93.1% en cero · pond. 5.83). Segundo corte de rebote (3.1% → 3.6% → 4.5% de los requests; 6.3% del tráfico monetizado) y el mejor precio con volumen del top (5.83). Sigue siendo el más sucio (géneros `genre_*`, la macro `[{{CONTENT_CATEGORIES}}]`, título 0.2%) — y como manda casi todo en `es`/`Spanish`, es el único al que el formato nuevo no le vació el idioma (98.6%).

**10. Televisa Univision via OB** (0.6% / 3.4% · **45.9% en cero** · pond. **1.27**). El despojo de metadata de siempre (título/serie/duración/categoría en 0%, ratings `dv-*`) al peor precio del top, que además baja (1.44 → 1.27). Gana cuota (2.6% → 3.4%) y es la ruta que más monetiza en proporción (92.3% de sus requests). El contraste con su ruta hermana (2.26 con metadata) sigue siendo el caso de estudio de supply path.

**11. Vidaa** (1.9% / 2.8% · 70.4% en cero · pond. **1.35**). Recupera un poco de volumen (2.5% → 2.8%) con el mismo perfil: **el default [IAB12] "News" marca el 66.8% de sus filas** (cine y novelas etiquetados como noticias), App Name a medias (37.2%) y el precio más bajo del top junto a Televisa OB. Su rating se desplomó (→ 46.0%): es el publisher donde más filas quedaron sin rating con el formato nuevo.

**12. Zeasn Europe B.V. (WhaleLive)** (0.1% / 2.2% · 59.0% en cero · pond. 3.06). Entra al top 12 por el retroceso de Select Plus. Perfil "app de TV lineal": 0.1% de las filas con 2.2% de los requests, título/serie/categoría/duración en 0%, idioma 97.2%, livestream 99.0%, ratings `dv-*`. Argentina 34.8% + Perú 30.9%. Precio medio (3.06) y buen sell-through (94.5% de sus requests monetizados).

---

## Síntesis

1. **El mapa de responsables cumple siete cortes sin cambios de fondo**, pero este corte añade un responsable nuevo que no es ningún partner: **la plataforma del reporte**, que cambió la escritura de género/rating/idioma y vació rating e idioma en la parte nueva de la ventana. Ninguna caída de rating o idioma de esta tabla se le puede reclamar a un vendedor hasta confirmar qué pasó en la fuente.
2. **Roku ya casi empata con OTTera en requests** (16.6% vs 17.4%) y sigue siendo el #1 del tráfico monetizado (15.8%). Con OTTera perdiendo peso relativo, el dataset se vuelve un poco menos "catálogo muerto".
3. **iion sube al #3 y a 5.49 de precio, pero con 3.7% de idioma** — el fix con mejor relación esfuerzo/impacto del dataset sigue siendo activar `contentLanguage` en esa ruta.
4. Los premium aparentes siguen siendo ruido: OTTera (6.88) monetiza el 0.1% de sus filas y Select Plus salió del top. El precio real con volumen sigue en la banda 5.1–5.8 (Roku, TCL x2, iion, Azteca); el bloque Televisa/Vidaa/Equativ, en 1.3–2.6.
