# Reporte — Análisis por publisher, consolidado v10 a v14 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v14.csv` (607,878 filas, 396,370,107,200 requests; métricas de v14).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v14-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~90% del tráfico). Porcentajes sobre las filas de cada publisher.

**Movimientos en el top vs el corte anterior:** Equativ superó a TV Azteca en volumen (Azteca cayó de 4.1% a 3.1% de los requests) y **Vidaa siguió creciendo** (2.0% → 2.9%) con cambios visibles en su metadata.

## Tabla comparativa

| Publisher | % filas | % requests | % filas eCPM=0 | eCPM pond. | Fill category | Fill language | Fill title | Fill length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 24.1% | 24.6% | **99.9%** | 7.25 | 39.1% | 99.8% | 99.8% | 1.0% |
| Roku - oRTB | 1.5% | 14.3% | 95.8% | 5.81 | **98.1%** | 94.9% | **24.9%** | **77.2%** |
| TCL ADS - Springserve | 12.4% | 11.0% | 60.4% | 4.91 | 0.8% | 90.5% | 99.6% | 1.2% |
| iion Pty Ltd | 15.4% | 9.5% | 85.5% | 4.47 | 0.5% | **4.8%** | 99.8% | 3.0% |
| TCL ADs (APAC) | 12.5% | 6.3% | **54.8%** | 5.57 | 0.9% | 93.8% | 99.8% | 1.7% |
| Coocaa (SKYWORTH) | 1.1% | 4.5% | **42.1%** | 3.22 | **100%** | **100%** | **100%** | **100%** |
| Televisa Univision via SpringServe | 1.4% | 4.3% | 58.9% | 2.66 | 0.0% | 60.5% | 85.6% | 50.5% |
| Equativ - oRTB CTV | 2.7% | 4.2% | 82.9% | 2.66 | 27.7% | 85.0% | 83.2% | 23.0% |
| TV Azteca - Springserve | 0.3% | 3.1% | 97.7% | 5.67 | 0.2% | 100% | **0.1%** | 0.1% |
| Vidaa | 2.1% | 2.9% | 70.4% | **1.38** | 85.2% | 100% | 79.3% | 2.1% |
| Select Plus PTE LTD (CTV) | 7.8% | 2.7% | **99.9%** | **10.35** | 0.0% | 78.9% | 99.9% | 1.1% |
| Televisa Univision via OB | 0.7% | 2.5% | 48.0% | **1.50** | 0.0% | 100% | **0.0%** | 0.0% |

## Perfiles (con los datos del corte v14)

**1. OTTera.tv** (24.1% / 24.6% · pond. 7.25). Sin cambios: revende las 4 apps TCL, metadata descriptiva casi perfecta, **monetiza el 0.12% de sus filas** — el catálogo muerto sigue siendo un cuarto del dataset. Origen del `[IAB1-22]` inválido (14.9%) y del bundle `+com.tcl.livetv`.

**2. Roku - oRTB** (1.5% / **14.3%** · pond. 5.81). El de siempre: estructura perfecta (categoría 98.1%, duración 77.2%), identidad oculta (5 títulos distintos, series en hashes MD5 — 50.6% el hash del vacío). México 65.6% + Puerto Rico 33.1%. Ratings sin guion (`tv14`, `tvpg`) y el `b` mexicano.

**3. TCL ADS - Springserve** (12.4% / 11.0% · 60.4% en cero · pond. 4.91). La ruta TCL sana en lo descriptivo (título 99.6%) y nula en lo estructural (`[-7]` 99.2%). Sigue #2 del tráfico monetizado (17.9%) prácticamente empatado con Roku (18.0%).

**4. iion Pty Ltd** (15.4% / 9.5% · pond. 4.47). Tercera ruta TCL, dos cuentas, y **el agujero del idioma: fill 4.8%** cuando sus rutas hermanas superan el 90%. Su precio sigue mejorando entre cortes (3.63 → 4.21 → 4.47) — le iría aún mejor con el campo activado.

**5. TCL ADs (APAC)** (12.5% / 6.3% · **54.8% en cero** · pond. 5.57). La ruta TCL que mejor convierte (45% de filas monetizadas). Nota: es el publisher detrás de los outliers peruanos (el 135.3 y tres más del top 5 son suyos).

**6. Coocaa, a SKYWORTH company** (1.1% / 4.5% · **42.1% en cero** · pond. 3.22). El content object perfecto (100% en todo, series 90.9%) y la parrilla clonada en 16 países (~9.8% de filas cada uno). Metadata perfecta ≠ precio: 3.22.

**7. Televisa Univision via SpringServe** (1.4% / 4.3% · 58.9% en cero · pond. 2.66). ViX multi-plataforma, rating 99.2% (tv-14 63.3%), duración 50.5% (bucket 8), y el modelo broadcaster: fill alto, precio bajo.

**8. Equativ - oRTB CTV** (2.7% / 4.2% · pond. 2.66). El exchange creció y **superó a TV Azteca en volumen**. México 84.4%, App Name perdido en el 30.2%, categoría 27.7% (ahora con [IAB12] 14.8% — contagiado del inventario Vidaa/ViX que revende). Precio bajo estable.

**9. TV Azteca - Springserve** (0.3% / 3.1% · **97.7% en cero** · pond. 5.67). Sigue vendiendo Tubi México y sigue siendo el más sucio (géneros `genre_*`, ratings `tvpg_tv_*`/`mpaa_*`, la macro `[{{CONTENT_CATEGORIES}}]`). Su volumen y su sell-through vienen cayendo corte a corte (4.9% → 2.9% del tráfico monetizado).

**10. Vidaa** (2.1% / 2.9% · 70.4% en cero · pond. **1.38**). El que más cambió: creció 50% en filas, **ViX ya es el 66.3% de su inventario**, y su App Name "revivió" a medias (33.6% de fill, pero con el valor genérico "Vidaa", no el nombre real de la app). **Se confirma la sospecha del default: [IAB12] "News" subió a 68.6% de sus filas** — cine y novelas etiquetados como noticias. Su categoría NO es usable pese al 85.2% de fill, y es la fuente del [IAB12] que ahora aparece en el top de México. Sigue siendo el más barato del top (1.38).

**11. Select Plus PTE LTD (CTV)** (7.8% / 2.7% · **99.92% en cero** · pond. 10.35). El premium fantasma: catálogo TCL que no se vende, con livestream=1 falso al 100% y rating al 22.3%. Uno de los outliers peruanos del top 5 es suyo.

**12. Televisa Univision via OB** (0.7% / 2.5% · pond. **1.50**). El despojo de metadata de siempre (título/serie/duración/categoría en 0%, ratings `dv-*`) al peor precio útil del top. El contraste con su ruta hermana (2.66 con metadata) sigue siendo el caso de estudio de supply path.

---

## Síntesis

1. **El mapa de responsables cumple cinco cortes sin cambios** — los fixes por partner siguen siendo los mismos y siguen pendientes. Nadie ha arreglado nada entre v10 y v14.
2. **Vidaa es el hallazgo del corte**: crece rápido, concentra ViX, y su categoría [IAB12] al 68.6% confirma el patrón "campo poblado con default" — la tercera variante de vacío disfrazado del dataset (tras `[-7]` y el MD5 vacío). De paso contamina el top de categorías de México vía Equativ.
3. Los cuatro vendedores premium aparentes del dataset (Select Plus 10.35, OTTera 7.25) monetizan <0.2% de su tráfico: **el precio alto sobre volumen despreciable no es premium, es ruido**. El precio real con volumen sigue en la banda 4.9–5.8 (Roku, TCL, Azteca).
4. TV Azteca se está apagando (volumen y sell-through cayendo por tercer corte consecutivo) — si la tendencia sigue, el principal emisor de formatos sucios de México dejará de importar por sí solo.
