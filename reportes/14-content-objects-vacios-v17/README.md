# Content objects vacíos — qué traen las demás columnas cuando uno falta (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` — 959,442 filas, 380,355,807,040 requests (métricas del corte v17).
**Generado con:** `scripts/analizar.py --solo-vacios-en <columna>` (un JSON por content object) + `scripts/generar_reporte_vacios.py` (el markdown) + `scripts/generar_visual_paises.py` (el SVG).

Un reporte por content object, con la misma estructura del detallado por país (México, Colombia, Chile) pero **restringido a las filas donde ese content object no trae dato útil** — vacío, `Not Available`, `Not Applicable`, `Unknown`, `[-7]` en categoría o el hash MD5 de cadena vacía en serie. Cada reporte muestra cómo se distribuyen las demás columnas dentro de ese subconjunto y lo compara con todo el dataset del país. `contentIsTitlePresent` no tiene reporte: viene en el 100% de las filas.

| Content object vacío | Filas | % de las filas | % de los requests | eCPM pond. (todo: 4.04) | Quién domina el subconjunto | Reporte |
|---|---:|---:|---:|---:|---|---|
| `contentGenre` | 60,981 | 6.36% | 13.87% | 4.384 | iion 30%, OTTera 17%, TCL ADS - Springserve 13% | [reporte](reporte-vacios-contentGenre.md) |
| `contentCategory` | 749,518 | 78.12% | 67.54% | 3.997 | iion 24%, OTTera 17%, TCL ADS - Springserve 16% | [reporte](reporte-vacios-contentCategory.md) |
| `contentSeries` | 895,551 | 93.34% | 92.46% | 4.112 | OTTera 22%, iion 20%, TCL ADS - Springserve 13% | [reporte](reporte-vacios-contentSeries.md) |
| `contentLength` | 842,777 | 87.84% | 74.78% | 3.983 | OTTera 24%, iion 21%, TCL ADS - Springserve 14% | [reporte](reporte-vacios-contentLength.md) |
| `contentLanguage` | 323,330 | 33.7% | 32.28% | 4.231 | iion 55%, TCL ADS - Springserve 9%, Select Plus 7% | [reporte](reporte-vacios-contentLanguage.md) |
| `contentIsLiveStream` | 683,273 | 71.22% | 57.89% | 4.124 | iion 26%, OTTera 24%, TCL ADs 14% | [reporte](reporte-vacios-contentIsLiveStream.md) |
| `contentTitle` | 67,762 | 7.06% | 29.49% | 3.975 | Roku 15%, Pluto LATAM via SpringServe 10%, OneFox - Tubi 9% | [reporte](reporte-vacios-contentTitle.md) |
| `contentRating` | 246,533 | 25.7% | 26.0% | 3.636 | Select Plus 26%, iion 22%, TCL ADS - Springserve 10% | [reporte](reporte-vacios-contentRating.md) |

**Lectura transversal:**

- Hay dos familias de vacíos. **Los estructurales** (categoría 78%, serie 93%, duración 88%, livestream 71%) son la norma del dataset: los manda un puñado de rutas (Roku, Coocaa, Vidaa, ViX) y el resto no; cuando falta uno, faltan los otros, y lo descriptivo (género, título) se mantiene. **Los descriptivos** (idioma 34%, rating 26%, género 6%) tienen responsables concretos — iion y Select Plus — y desde v16 la escritura nueva de la fuente, que descarta los tres a la vez; vienen en paquete entre sí y con título presente, por lo que son los que el relleno intra-título recupera.
- **El título es el caso aparte**: 7% de las filas pero 29.5% de los requests, con un perfil invertido (Roku, Pluto, Tubi, Plex: categoría y duración altas, identidad nula) y sin llave posible para rellenar. Es el vacío que más tráfico compromete y el único que solo el vendedor puede resolver.
- **El precio no castiga el vacío**: en Colombia y Chile el tráfico sin categoría, serie, duración, idioma o livestream paga igual o más que el país; en México paga menos porque quien sí completa (Roku) es también quien más cobra. Lo que mueve el eCPM es la ruta de venta, no la completitud del content object.
