# Reporte — Análisis por publisher, consolidado v10 a v17 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, 380,355,807,040 requests; métricas de v17).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v17-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~88% del tráfico). Porcentajes sobre las filas de cada publisher.

**Antes de leer los movimientos:** la escritura nueva del reporte (ver el detallado por país) ya es el 54% de las filas de v17 y está repartida entre todos los publishers del top (del 44% de Roku al 73% de Select Plus), así que las diferencias de rating/idioma entre partners siguen sin ser atribuibles a ellos. El top 12 vuelve a cambiar: **Select Plus regresa (3.2% de los requests) y Zeasn sale**.

**Movimientos en el top vs el corte anterior:** **Roku ya es el #1 en requests (16.3%)** — OTTera cayó de 17.4% a 15.4% y cedió el primer puesto que tuvo desde v10; iion sigue subiendo (11.2% → 13.8%) y se afianza como #3; TV Azteca se apagó de nuevo (4.5% → 4.3% de los requests, pero de 6.3% a 4.4% del tráfico monetizado); Select Plus creció (2.0% → 3.2%) con su precio de vitrina disparado a 12.6.

## Tabla comparativa

| Publisher | % filas no vacías | % filas eCPM=0 | eCPM pond. | % no vacías: category | % no vacías: language | % no vacías: title | % no vacías: length |
|---|---:|---:|---:|---:|---:|---:|---:|
| Roku - oRTB | 1.4% | 98.0% | 5.32 | **98.1%** | 85.2% | **27.4%** | **80.0%** |
| OTTera.tv | 20.9% | **99.9%** | 6.25 | 37.1% | 90.4% | 99.7% | 1.1% |
| iion Pty Ltd | 19.1% | 89.0% | 5.66 | 0.6% | **3.4%** | 99.8% | 3.0% |
| TCL ADS - Springserve | 12.5% | 61.3% | 5.04 | 0.7% | 76.8% | 99.6% | 1.3% |
| TCL ADs (APAC) | 11.8% | **52.5%** | 5.62 | 0.9% | 82.3% | 99.8% | 2.4% |
| Equativ - oRTB CTV | 2.5% | 80.0% | 2.57 | 24.0% | 77.3% | 86.1% | 23.2% |
| Televisa Univision via SpringServe | 1.5% | 61.4% | 2.24 | 0.0% | 52.1% | 85.4% | 53.0% |
| TV Azteca - Springserve | 0.2% | 93.2% | 5.92 | 0.3% | 98.7% | **0.2%** | 0.2% |
| Coocaa (SKYWORTH) | 1.6% | 56.3% | 2.89 | **100%** | 77.3% | **100%** | **100%** |
| Televisa Univision via OB | 0.6% | **46.9%** | **1.10** | 0.0% | 93.9% | **0.0%** | 0.0% |
| Select Plus PTE LTD (CTV) | 8.7% | **99.9%** | **12.61** | 0.0% | 71.4% | 99.9% | 1.4% |
| Vidaa | 1.8% | 70.7% | **1.42** | 86.1% | 90.3% | 79.7% | 2.4% |

*"% filas no vacías" equivale aquí al % de filas del dataset (Publisher viene en el 100% de las filas). El orden de la tabla — y la numeración de los perfiles — sigue el peso en requests de cada publisher (data completa en el JSON).*

## Perfiles (con los datos del corte v17)

**1. Roku - oRTB** (1.4% / **16.3%** · pond. 5.32). **Nuevo #1 del dataset en requests** tras tres cortes creciendo (14.3 → 15.0 → 16.6 → 16.3%, y OTTera cayendo). Estructura intacta (categoría 98.1%, duración 80.0%), identidad oculta (**5 títulos distintos**: `roku` 12.5%, `epg` 10.8%, `vod` 3.6%; series en hashes MD5 — 53.2% el hash del vacío). Sigue #1 del tráfico monetizado (15.7%) pero su sell-through propio cae por segundo corte (60.4% → 50.0% → 48.9%). México 64.3% + Puerto Rico 34.6%.

**2. OTTera.tv** (20.9% / 15.4% · pond. 6.25). Pierde el liderato de siempre (23.0% → 17.4% → 15.4% de los requests) sin cambiar de naturaleza: revende las 4 apps TCL, metadata descriptiva casi perfecta y **monetiza el 0.06% de sus filas**. Su precio de vitrina también se erosiona (6.97 → 6.88 → 6.25). Origen del `[IAB1-22]` inválido (12.8% de sus filas).

**3. iion Pty Ltd** (19.1% / 13.8% · pond. 5.66). Sigue subiendo en volumen (10.1 → 11.2 → 13.8%) y en precio por quinto corte (4.21 → 4.47 → 4.99 → 5.49 → **5.66**), ya #3 del tráfico monetizado (10.5%). Y sigue con **3.4% de idioma** cuando sus rutas hermanas TCL están en 77–82%: el fix con mejor relación esfuerzo/impacto del dataset, un corte más sin resolverse. Es además el publisher con más filas en la escritura nueva (56% de las suyas en v17).

**4. TCL ADS - Springserve** (12.5% / 9.3% · 61.3% en cero · pond. 5.04). Estable en volumen (9.5% → 9.3%) y con el precio cediendo (5.13 → 5.04). La ruta TCL sana en lo descriptivo (título 99.6%) y nula en lo estructural (`[-7]` 99.3%). #2 del tráfico monetizado (14.2%).

**5. TCL ADs (APAC)** (11.8% / 5.4% · **52.5% en cero** · pond. 5.62). Sigue siendo la ruta TCL que mejor convierte (47.5% de filas monetizadas). Sus outliers peruanos de tres dígitos **desaparecieron del corte v17** (siguen en el consolidado por llaves viejas); el máximo real de v17 es 95.9 y es de iion. El nuevo outlier propio es "chicken stew season 1" a 82.8 en México.

**6. Equativ - oRTB CTV** (2.5% / 5.1% · pond. 2.57). El exchange se estabiliza (5.7% → 5.1%) tras tres cortes creciendo. México 84.8%, App Name perdido en el 25.9%, categoría 24.0% (con [IAB12] 11.6% — contagiado del inventario Vidaa/ViX que revende). Precio bajo estable (2.59 → 2.57); #5 del tráfico monetizado (8.2%).

**7. Televisa Univision via SpringServe** (1.5% / 5.1% · 61.4% en cero · pond. 2.24). ViX multi-plataforma con el modelo broadcaster de siempre: metadata casi siempre llena, precio bajo y bajando (2.66 → 2.44 → 2.26 → **2.24**). `Teen Plus` ya es el 16.9% de sus filas (segundo rating tras `tv-14`), y su rating total recuperó (84.2% → 86.4%) porque el formato nuevo ya lo trae.

**8. TV Azteca - Springserve** (0.2% / 4.3% · 93.2% en cero · pond. 5.92). El rebote de v15–v16 no aguantó: **su sell-through propio se desplomó de 73.4% a 51.6%** y pasa del 6.3% al 4.4% del tráfico monetizado. Sigue siendo el más sucio (géneros `genre_*`, la macro `[{{CONTENT_CATEGORIES}}]`, título 0.2%) y el mejor precio con volumen del top (5.92) — cuando vende.

**9. Coocaa, a SKYWORTH company** (1.6% / 4.3% · 56.3% en cero · pond. 2.89). El content object perfecto en lo estructural (categoría, título, duración y livestream al 100%, series 90.4%). Su rating se recupera un poco con el formato nuevo (66.3% → 69.1%; `All Ages` 12.3%, `Teen` 11.6%). Precio estable (2.79 → 2.89); pierde peso en el tráfico vendido (7.5% → 6.7%).

**10. Televisa Univision via OB** (0.6% / 3.3% · **46.9% en cero** · pond. **1.10**). El despojo de metadata de siempre (título/serie/duración/categoría en 0%, ratings `dv-*`) al peor precio del top, que sigue bajando (1.44 → 1.27 → **1.10**). Es la ruta que más monetiza en proporción (97.1% de sus requests). El contraste con su ruta hermana (2.24 con metadata) sigue siendo el caso de estudio de supply path.

**11. Select Plus PTE LTD (CTV)** (8.7% / 3.2% · **99.9% en cero** · pond. **12.61**). Vuelve al top 12 con más volumen (2.0% → 3.2%) y un precio de vitrina que se disparó (9.54 → 12.61) sobre el 0.05% de sus filas que monetizan: el premium fantasma de siempre, ahora más fantasma. Catálogo TCL (MovieArk 70%), livestream=1 al 100%, rating al 23.1% (el peor del top). Es el publisher con más filas en escritura nueva (73% de las suyas en v17).

**12. Vidaa** (1.8% / 2.6% · 70.7% en cero · pond. **1.42**). Baja al último puesto del top (2.8% → 2.6%) con el mismo perfil: **el default [IAB12] "News" marca el 66.1% de sus filas** (cine y novelas etiquetados como noticias), App Name a medias (38.7%) y el segundo precio más bajo del top. Su rating sigue en 47.6%, el segundo peor tras Select Plus.

---

## Síntesis

1. **Cambio de líder por primera vez en ocho cortes: Roku supera a OTTera en requests** (16.3% vs 15.4%). No es que Roku venda más — su sell-through propio baja —, es que el catálogo muerto de OTTera pierde peso. El dataset se vuelve un poco más "tráfico real" y un poco menos "inventario de vitrina".
2. **El mapa de responsables sigue igual** — iion sin idioma, Roku sin título, OTTera y Select Plus sin monetizar, Televisa OB sin metadata, Vidaa con su default de noticias — y el cambio de formato del reporte sigue sin poder atribuirse a ningún partner. Con la escritura nueva ya mayoritaria, rating e idioma por publisher empiezan a estabilizarse en su nuevo nivel.
3. **TV Azteca vuelve a apagarse** (51.6% de sell-through propio, venía de 73.4%): el rebote de dos cortes fue un episodio, no una tendencia.
4. Los premium aparentes siguen siendo ruido, y más: Select Plus a 12.61 monetiza el 0.05% de sus filas. El precio real con volumen sigue en la banda 5.0–5.9 (Roku, TCL x2, iion, Azteca); el bloque Televisa/Vidaa/Equativ, en 1.1–2.6 y bajando.
