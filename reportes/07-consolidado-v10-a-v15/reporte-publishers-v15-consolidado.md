# Reporte — Análisis por publisher, consolidado v10 a v15 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v15.csv` (648,589 filas, 385,830,361,280 requests; métricas de v15).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v15-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~90% del tráfico). Porcentajes sobre las filas de cada publisher.

**Movimientos en el top vs el corte anterior:** Roku siguió ganando peso (14.3% → 15.0% de los requests), **iion ya pisa los talones a TCL Springserve** (10.1% vs 10.6%), **TV Azteca rebotó** (3.1% → 3.6%, y de 2.9% a 5.2% del tráfico monetizado) y **Vidaa se enfrió** (2.9% → 2.5%) tras el salto del corte pasado.

## Tabla comparativa

| Publisher | % filas | % requests | % filas eCPM=0 | eCPM pond. | Fill category | Fill language | Fill title | Fill length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 23.3% | 23.0% | **99.9%** | 6.97 | 39.0% | 99.7% | 99.8% | 1.1% |
| Roku - oRTB | 1.5% | 15.0% | 96.6% | 5.44 | **98.2%** | 94.8% | **24.6%** | **77.5%** |
| TCL ADS - Springserve | 12.2% | 10.6% | 59.1% | 5.06 | 0.8% | 87.7% | 99.6% | 1.4% |
| iion Pty Ltd | 15.6% | 10.1% | 87.3% | 4.99 | 0.7% | **5.0%** | 99.8% | 3.4% |
| TCL ADs (APAC) | 12.3% | 5.9% | **53.0%** | 5.51 | 0.9% | 91.5% | 99.8% | 2.4% |
| Equativ - oRTB CTV | 2.8% | 4.8% | 82.9% | 2.58 | 25.9% | 86.3% | 84.3% | 21.7% |
| Coocaa (SKYWORTH) | 1.0% | 4.6% | **48.0%** | 3.01 | **100%** | **100%** | **100%** | **100%** |
| Televisa Univision via SpringServe | 1.4% | 4.6% | 59.7% | 2.44 | 0.0% | 60.9% | 85.3% | 50.5% |
| TV Azteca - Springserve | 0.3% | 3.6% | 93.1% | 5.46 | 0.3% | 100% | **0.2%** | 0.2% |
| Televisa Univision via OB | 0.7% | 2.6% | 47.6% | **1.44** | 0.0% | 100% | **0.0%** | 0.0% |
| Vidaa | 2.0% | 2.5% | 71.3% | **1.40** | 84.5% | 100% | 79.7% | 2.2% |
| Select Plus PTE LTD (CTV) | 7.5% | 2.1% | **99.9%** | **9.54** | 0.0% | 77.0% | 99.9% | 1.1% |

## Perfiles (con los datos del corte v15)

**1. OTTera.tv** (23.3% / 23.0% · pond. 6.97). Sin cambios: revende las 4 apps TCL, metadata descriptiva casi perfecta, **monetiza el 0.13% de sus filas** — el catálogo muerto sigue siendo casi un cuarto del dataset. Origen del `[IAB1-22]` inválido y del bundle `+com.tcl.livetv`.

**2. Roku - oRTB** (1.5% / **15.0%** · pond. 5.44). Sigue creciendo en peso (14.3% → 15.0%). El de siempre: estructura perfecta (categoría 98.2%, duración 77.5%), identidad oculta (**5 títulos distintos**: `roku` 10.9%, `epg` 8.8%; series en hashes MD5 — 50.4% el hash del vacío). México 65.2% + Puerto Rico 33.5%.

**3. TCL ADS - Springserve** (12.2% / 10.6% · 59.1% en cero · pond. 5.06). La ruta TCL sana en lo descriptivo (título 99.6%) y nula en lo estructural (`[-7]` 99.2%). Sigue #2 del tráfico monetizado (16.9%), ya casi empatado con Roku (17.1%).

**4. iion Pty Ltd** (15.6% / 10.1% · pond. 4.99). Tercera ruta TCL, dos cuentas, y **el agujero del idioma intacto: fill 5.0%** cuando sus rutas hermanas superan el 87%. Su precio mejora por tercer corte (4.21 → 4.47 → 4.99) — le iría aún mejor con el campo activado.

**5. TCL ADs (APAC)** (12.3% / 5.9% · **53.0% en cero** · pond. 5.51). La ruta TCL que mejor convierte (47% de filas monetizadas). Este corte el top 5 de outliers peruanos es **enteramente suyo** (135.3, 102.9, 100.6, 100.3, 99.2 — todos MovieArk Perú).

**6. Equativ - oRTB CTV** (2.8% / 4.8% · pond. 2.58). El exchange consolida el puesto ganado (4.2% → 4.8%). México 82.0%, App Name perdido en el 28.2%, categoría 25.9% (con [IAB12] 13.5% — contagiado del inventario Vidaa/ViX que revende). Precio bajo estable.

**7. Coocaa, a SKYWORTH company** (1.0% / 4.6% · **48.0% en cero** · pond. 3.01). El content object perfecto (100% en todo, series 91.0%) y la parrilla clonada multi-país. Metadata perfecta ≠ precio: 3.01, y su tasa de monetización cedió un poco (42.1% → 48.0% en cero).

**8. Televisa Univision via SpringServe** (1.4% / 4.6% · 59.7% en cero · pond. 2.44). ViX multi-plataforma, rating 99.0% (tv-14 62.8%), duración 50.5% (bucket 8), y el modelo broadcaster de siempre: fill alto, precio bajo (y bajando: 2.66 → 2.44).

**9. TV Azteca - Springserve** (0.3% / 3.6% · 93.1% en cero · pond. 5.46). **El rebote del corte**: tras tres cortes cayendo, sube en volumen (3.1% → 3.6%) y su sell-through salta (97.7% → 93.1% en cero; 2.9% → 5.2% del tráfico monetizado). Sigue siendo el más sucio (géneros `genre_*`, la macro `[{{CONTENT_CATEGORIES}}]`, título 0.2%) — vender más no lo hizo más limpio.

**10. Televisa Univision via OB** (0.7% / 2.6% · pond. **1.44**). El despojo de metadata de siempre (título/serie/duración/categoría en 0%, ratings `dv-*` — `dv-t` 46.5%) al peor precio útil del top. El contraste con su ruta hermana (2.44 con metadata) sigue siendo el caso de estudio de supply path.

**11. Vidaa** (2.0% / 2.5% · 71.3% en cero · pond. **1.40**). Se enfrió tras el salto del corte pasado (2.9% → 2.5% de los requests), pero su perfil se mantiene: **ViX es el 64.9% de su inventario** y **el default [IAB12] "News" marca el 67.2% de sus filas** — cine y novelas etiquetados como noticias. Su categoría sigue sin ser usable pese al 84.5% de fill, su App Name sigue a medias (33.0%, con el genérico "Vidaa") y sigue siendo el más barato del top (1.40).

**12. Select Plus PTE LTD (CTV)** (7.5% / 2.1% · **99.9% en cero** · pond. 9.54). El premium fantasma: catálogo TCL que no se vende, livestream=1 falso al 100%, rating al 21.9%. Su precio de vitrina también se eroda (10.35 → 9.54).

---

## Síntesis

1. **El mapa de responsables cumple seis cortes sin cambios de fondo** — los fixes por partner siguen siendo los mismos y siguen pendientes. Nadie ha arreglado nada entre v10 y v15.
2. **TV Azteca desmintió su propia despedida**: tras tres cortes apagándose, rebotó a 5.2% del tráfico monetizado con mejor sell-through. El principal emisor de formatos sucios de México vuelve a importar — y su metadata sigue igual de rota.
3. **Vidaa se enfrió pero su default no**: [IAB12] al 67.2% de sus filas confirma por segundo corte la tercera variante de vacío disfrazado (tras `[-7]` y el MD5 vacío), y sigue contaminando el top de categorías de México vía Equativ.
4. Los premium aparentes siguen siendo ruido: Select Plus (9.54) y OTTera (6.97) monetizan <0.2% de sus filas. El precio real con volumen sigue en la banda 5.0–5.5 (Roku, TCL x2, Azteca).
