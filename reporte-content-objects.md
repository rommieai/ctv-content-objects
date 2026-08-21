# Reporte — Content Objects en inventario CTV LATAM (v10)

**Archivo analizado:** `inventory-source-alcance-ctv-v10-latam-content-objetcs.csv`
**Data detallada:** `reporte-content-objects.json`
**Referencia de campos:** [OpenRTB 2.6 — Object: Content](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent)

## Resumen del dataset

- **512,000 filas** (combinaciones de publisher + app + país + señales de contenido).
- **423 mil millones de requests** totales (`Total Requests` sumado).
- **229 publishers**, 18 países. Por requests: México 61.8%, Argentina 16.8%, Colombia 6.5%, Chile 5.9%, y el resto por debajo del 3%.
- Top publishers por volumen: OTTera.tv, Roku (oRTB), TCL ADS, iion, TV Azteca, Select Plus, TelevisaUnivision.
- **Ojo con el eCPM:** el 82.8% de las filas (424,037) tiene eCPM = 0. Solo 87,963 filas tienen eCPM > 0, así que cualquier análisis de precio hay que hacerlo sobre ese subconjunto.

## Qué tan poblado viene cada campo

Un campo se consideró "vacío" cuando viene en blanco o con centinelas (`Not Available`, `Not Applicable`, `Unknown`, `N/A`, `null`, `none`, etc.), y también cuando trae basura equivalente a vacío (ver hallazgos de calidad más abajo). El "% por requests" pondera por volumen de tráfico, que es lo que realmente importa para alcance.

| Campo (OpenRTB) | % filas con dato | % requests con dato | Comentario |
|---|---:|---:|---|
| contentGenre (`content.genre`) | 98.7% | 93.9% | El mejor poblado, pero es texto libre: 7,655 valores distintos |
| contentTitle (`content.title`) | 91.5% | 75.4% | Bien poblado aunque con valores genéricos ("roku", "epg") |
| contentRating (`content.contentrating`) | 84.7% | 87.4% | 177 valores; domina el sistema TV Parental Guidelines (tv-14, tv-ma) y MPAA (r, pg-13) |
| contentLanguage (`content.language`) | 79.9% | 86.9% | en 48%, es 27%; formatos mezclados (ver hallazgos) |
| contentIsLiveStream (`content.livestream`) | 29.1% | 38.7% | Cuando viene, **siempre vale 1** (live); nunca reportan 0 (VOD) |
| contentCategory (`content.cat`) | 22.0% | 30.0% | El 78% de las filas trae `[-7]`, que no es una categoría IAB válida |
| contentLength (`content.len`) | 11.3% | 24.1% | Valores 1–8: **no son segundos** como pide la spec; parecen buckets |
| **contentSeries** (`content.series`) | **5.5%** | **6.9%** | **La columna con menos datos** |

`contentIsTitlePresent` es una bandera derivada (no es campo OpenRTB): true en 91.5% de filas, consistente con el fill de contentTitle. `Publisher ID`, `Publisher`, `pageURL`, `Country`, `Total Requests` y `eCPM` vienen al 100%. `App Name` está al 91.8% (el resto "Not Available").

## Hallazgos de calidad de datos

Estos valores vienen "poblados" pero en realidad son basura, y ya están descontados de la tabla anterior:

1. **`contentCategory = [-7]` en 399,480 filas (78%).** `-7` no existe en ninguna taxonomía IAB; es un placeholder/error de algún SSP. Las categorías reales que sí llegan usan la Content Category Taxonomy 1.0 (IAB1-x), que está deprecada — nadie está mandando `cattax` con taxonomías nuevas. También llegan valores no estándar como `[sports]`.
2. **`contentSeries` con hash MD5 de string vacío** (`d41d8cd98f00b204e9800998ecf8427e`) en 4,287 filas: alguien está hasheando el valor vacío en vez de omitir el campo.
3. **Macro sin reemplazar:** `{{CONTENT_SERIES}}` aparece literal en 614 filas — un publisher tiene mal configurado su ad server.
4. **`contentLength` con valores 1 a 8.** La spec define `len` en segundos; contenido CTV de 1–8 segundos no existe. Son buckets de duración o un campo mal mapeado — no usar como duración real sin confirmar con la fuente.
5. **`contentIsLiveStream` nunca reporta 0.** Solo se puebla cuando es live (149,170 filas con "1"). La ausencia del campo NO se puede interpretar como VOD, porque 71% viene Unknown/Not Available.
6. **`contentLanguage` sucio:** mezcla ISO-639-1 (`en`, `es`) con ISO-639-2 (`spa`, no permitido por la spec en `language`) y basura (`c`). 482 "idiomas" distintos delatan texto libre.
7. **Encoding roto en títulos:** hay mojibake tipo `catalunya �ber alles!`, señal de doble codificación en algún punto del pipeline.
8. **`contentGenre` es texto libre**, a veces con listas separadas por coma (`drama,romance`). Para segmentar por género habría que normalizarlo.

## Cuáles campos son relevantes (y cuáles no)

Comparando el eCPM promedio (solo filas con eCPM > 0) según si el campo viene poblado:

- **contentLanguage es la señal más asociada a precio:** eCPM 5.15 con dato vs 3.76 sin dato (+37%). Tiene sentido: es la señal mínima de targeting en LATAM (es/pt vs en).
- **contentRating** (+10%), **contentTitle** (+11%) y **contentGenre** (+18%) también correlacionan positivo — el inventario con metadata de contenido decente se vende mejor.
- Las filas con los 9 campos content* poblados promedian eCPM 1.74 vs ~0.4–1.1 en el resto (promedio incluyendo ceros), o sea que la riqueza de metadata sí acompaña la monetización.
- **contentSeries, contentLength y contentCategory hoy no aportan**: poco fill, sin diferencia de eCPM, y con los problemas de calidad descritos. contentCategory sería valiosa si llegara limpia (es la base de brand safety / contextual), pero con 78% de `[-7]` no es usable tal como está.

## Conclusión

Para trabajar hoy con este inventario, los campos confiables son **genre, title, rating y language** (75–99% de cobertura por requests), con normalización previa. **Series, length, category y livestream** están entre inservibles y parciales: si se necesitan (p. ej. category para contextual/brand safety, o distinguir live vs VOD), hay que pedirles a los SSPs/publishers que corrijan el paso de `content.cat` (el `[-7]`), que manden `livestream=0` para VOD, y que `len` venga en segundos como dice la spec.
