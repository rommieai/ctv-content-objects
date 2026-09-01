# Reporte — Análisis por publisher, consolidado v10 a v13 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v13.csv` (579,679 filas, 403,522,711,360 requests; métricas de v13).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v13-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~90% del tráfico). Porcentajes de "top valores" sobre las filas de cada publisher.

**Cambio en el top 12 vs el corte anterior:** entra **Vidaa** (Hisense) y Zeasn/WhaleLive sale del top por volumen (sigue existiendo, con su eCPM recalculado a la baja: de 10.7 en v10-v11 a ~3.0 ahora — el "premium" de WhaleLive terminó de desinflarse con los recálculos).

## Tabla comparativa

| Publisher | % filas | % requests | % filas eCPM=0 | eCPM pond. | Fill category | Fill language | Fill title | Fill length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 24.0% | 24.3% | **99.9%** | 7.14 | 39.6% | 99.9% | 99.8% | 1.0% |
| Roku - oRTB | 1.6% | 14.4% | 95.5% | 5.95 | **98.1%** | 94.8% | **25.0%** | **77.2%** |
| TCL ADS - Springserve | 12.7% | 11.4% | 61.0% | 5.08 | 0.8% | 91.8% | 99.6% | 1.2% |
| iion Pty Ltd | 15.5% | 8.8% | 86.0% | 4.21 | 0.5% | **4.5%** | 99.8% | 2.7% |
| TCL ADs (APAC) | 12.9% | 7.2% | **55.3%** | 5.77 | 0.9% | 94.1% | 99.8% | 1.6% |
| Coocaa (SKYWORTH) | 1.1% | 4.5% | **42.1%** | 3.30 | **100%** | **100%** | **100%** | **100%** |
| Televisa Univision via SpringServe | 1.5% | 4.3% | 57.6% | 2.65 | 0.0% | 60.4% | 85.6% | 50.9% |
| TV Azteca - Springserve | 0.4% | 4.1% | 96.4% | 5.53 | 0.1% | 100% | **0.1%** | 0.1% |
| Equativ - oRTB CTV | 2.5% | 3.9% | 82.9% | 2.69 | 23.3% | 83.1% | 84.8% | 25.9% |
| Select Plus PTE LTD (CTV) | 7.9% | 2.7% | **99.9%** | **10.72** | 0.0% | 79.4% | 99.9% | 1.1% |
| Televisa Univision via OB | 0.7% | 2.6% | 47.3% | **1.46** | 0.0% | 100% | **0.0%** | 0.0% |
| Vidaa | 1.5% | 2.0% | 71.5% | **1.41** | 78.3% | 100% | 77.9% | 2.7% |

## Perfiles (lo que define a cada uno, con los datos del corte v13)

**1. OTTera.tv** (24.0% filas / 24.3% requests · 99.88% en cero · pond. 7.14). Sin cambios: revende las 4 apps TCL (incluido el bundle malformado `+com.tcl.livetv`, 100% suyo), metadata descriptiva casi perfecta (idioma/rating/título 99.8–99.9%) y **el catálogo muerto del dataset: monetiza el 0.12% de sus filas**. Sigue siendo el origen del código inválido `[IAB1-22]` (15.1% de sus filas).

**2. Roku - oRTB** (1.6% filas / **14.4% requests** · pond. 5.95). El espejo de OTTera: la mejor metadata estructural (categoría 98.1%, duración 77.2%, rating 98.4%) y la peor identidad de contenido — **5 valores de título en 8,980 filas** (`roku`, `epg`, `vod`), series tras hashes MD5 (50.8% el hash del vacío, más hashes de series reales). México 65.7% + Puerto Rico 33.1%. Origen de los ratings sin guion (`tv14`, `tvpg`) y del `b` de RTC México.

**3. TCL ADS - Springserve** (12.7% / 11.4% · 61.0% en cero · pond. 5.08). La ruta TCL "sana": título 99.6%, idioma 91.8%, rating 90.9%, y **`[-7]` en el 99.2%** de sus filas. Argentina 31.1% + México 25.3%. En v13 es **el primer vendedor del tráfico monetizado del dataset (18.5% del total)**, superando a Roku.

**4. iion Pty Ltd** (15.5% / 8.8% · dos cuentas · pond. 4.21). Tercera ruta TCL y **el culpable del idioma faltante: fill de contentLanguage 4.5%** (sus rutas hermanas: 92–99.9%). Con v13 mejoró algo su precio (3.63 → 4.21). Sigue el argumento de yield más directo del dataset: activar un campo que su propio inventario ya trae por otras rutas.

**5. TCL ADs (APAC)** (12.9% / 7.2% · **55.3% en cero, el mejor sell-through de las rutas TCL** · pond. 5.77). Gemela de la #3 con mejor conversión: 45% de sus filas monetizan. `[-7]` 99.1%, idioma 94.1%.

**6. Coocaa, a SKYWORTH company** (1.1% / 4.5% · **42.1% en cero, el mejor sell-through del dataset** · pond. 3.30). El content object perfecto (100% en categoría, duración, idioma, título, livestream; series 90.9%) en un solo bundle (Coolita). Persiste su rareza: distribución de filas idéntica (~9.9%) en 16 países — una sola parrilla replicada. Metadata perfecta, precio modesto.

**7. Televisa Univision via SpringServe** (1.5% / 4.3% · 57.6% en cero · pond. 2.65). ViX en 5 plataformas, metadata razonable (rating 99.2% con tv-14 63.7%, duración 50.9% toda en bucket 8, género real drama 47.6%) y el modelo broadcaster: vende mucho, barato. La única serie con volumen sigue siendo "FIFA Club World Cup".

**8. TV Azteca - Springserve** (0.4% / 4.1% · 96.4% en cero · pond. 5.53). Sigue vendiendo **Tubi México** (98.7% de sus filas) y sigue siendo el publisher más sucio por metro cuadrado: géneros `genre_*`, ratings `tvpg_tv_14`/`mpaa_r`, la macro `[{{CONTENT_CATEGORIES}}]`, título en el 0.1%.

**9. Equativ - oRTB CTV** (2.5% / 3.9% · pond. 2.69). El exchange: mezcla ViX/TCL/Roku, México 84.9%, App Name perdido en el 33.9%, metadata intermedia (categoría 23.3%, duración 25.9%). Precio bajo consistente con reventa de broadcaster.

**10. Select Plus PTE LTD (CTV)** (7.9% / 2.7% · **99.91% en cero** · pond. **10.72**). Cuarta ruta TCL, réplica del patrón OTTera pero más extremo en precio: casi nada se vende, y lo poquito que se vende, carísimo (12.7 de media). Sus dos señales rotas siguen: **livestream=1 en el 100% de sus filas** (incluyendo películas de MovieArk — señal falsa) y rating en el 21.7%.

**11. Televisa Univision via OB** (0.7% / 2.6% · 47.3% en cero · pond. **1.46**). El caso de estudio de supply path: la misma ViX que por SpringServe llega con metadata y a 2.65, por OB llega **sin título, sin serie, sin duración, sin categoría** (todo 0%) y a 1.46. La familia de ratings `dv-*` nace aquí.

**12. Vidaa** (1.5% / 2.0% · 71.5% en cero · pond. **1.41** — el más barato del top). El nuevo del top 12: la tienda de Hisense vendiendo ViX (50.1% de sus filas), su launcher (41.4%), Pluto y Tubi. Perfil curioso: **categoría 78.3% pero dominada por [IAB12] "News" (53.6%)** — sospechosamente uniforme para un mix de cine y TV (huele a valor por defecto, otra categoría "poblada" que engaña) — idioma 100% (es 93%), pero **App Name perdido en el 99.6%** y título al 77.9% con los canales de Televisa como valores top. México 62%.

---

## Síntesis — qué cambió con v13 y qué se sostiene

1. **El mapa de responsables no cambió en nada**: mismos emisores de `[-7]` (rutas TCL), del idioma faltante (iion), de los formatos sucios de rating/género (TV Azteca), de la familia `dv-*` (Televisa-OB), de los títulos/series ocultos (Roku). La lista de fixes por partner sigue vigente tal cual.
2. **Los precios siguen moviéndose entre cortes**: WhaleLive terminó de caer (10.7 → 3.0, y salió del top 12 por volumen), TCL Springserve destronó a Roku como primer vendedor del tráfico monetizado, y Select Plus quedó como el "premium fantasma" (10.72 sobre el 0.09% de su tráfico).
3. **Hallazgo nuevo con Vidaa**: su categoría 78% de fill está dominada por un solo valor ([IAB12] News en el 53.6% de las filas) que no cuadra con su mix de contenido — el patrón "campo poblado con valor por defecto" que ya vimos en `[-7]` y en el MD5 vacío, en versión más sutil. Verificar antes de usar su categoría.
4. Se mantiene la conclusión de fondo: **metadata y monetización son ejes independientes** (Coocaa perfecto y barato; Roku opaco y vendiendo 14% del tráfico; OTTera perfecto en lo descriptivo y muerto en revenue), y las rutas limpias de un mismo inventario cobran más que las sucias.
