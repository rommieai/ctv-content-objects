# Reporte detallado — Content Objects, inventario CTV LATAM (v11, 4–18 ago 2026)

**Archivo:** `60333-inventory-source-alcance-ctv-v11-latam-content-objetcs-20260804T00_00-20260818T23_59.csv` — 512,000 filas, 16 columnas, 427,408,026,000 requests totales. Según el nombre del archivo, el periodo cubierto es **del 4 al 18 de agosto de 2026**.
**Data completa en:** `reporte-content-objects-detallado-v11.json` (distribuciones completas por columna y por país).
**Referencia de campos content\*:** [OpenRTB 2.6 — Object: Content](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent)

**Cómo leer este reporte:**
- Cada fila del CSV es una **combinación agregada** (publisher + app + país + señales de contenido), no un evento individual. Por eso todos los análisis se dan en dos vistas: **% de filas** (variedad del inventario) y **% de requests** (volumen real de tráfico). Cuando difieren mucho, significa que pocas combinaciones concentran mucho tráfico.
- Llamamos **centinelas** a los valores que ocupan la celda pero no aportan dato: `Not Available`, `Not Applicable`, `Unknown`, `N/A`, `none`, `undefined`. El **fill rate** los excluye, junto con basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).
- La distinción entre centinelas no es aleatoria: `Not Applicable` y `Unknown` suelen venir de la capa de normalización del vendor (el SSP no mandó el campo o mandó algo no interpretable), mientras `Not Available` indica que el campo no llegó en el bid request. En la práctica todos significan "sin dato".

---

# PARTE 1 — Análisis por columna (las 16)

## 1. Publisher ID

**Glosario.** Identificador numérico interno de la cuenta del publisher/seller dentro de la plataforma (el "seat" del vendedor en el exchange). No es un campo OpenRTB del bid request; es metadato de la plataforma que generó el reporte. Un ID = una cuenta comercial.

**Datos.** 228 valores distintos, 0 vacíos (100% fill). Distribución (top):

| Publisher ID | Publisher al que corresponde | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| 161101 | OTTera.tv | 124,089 | 24.24% | 23.48% |
| 161489 | TCL ADs (APAC) | 68,413 | 13.36% | 8.95% |
| 164918 | iion Pty Ltd | 66,129 | 12.92% | 11.05% |
| 166799 | iion Pty Ltd (2ª cuenta) | 39,995 | 7.81% | 3.79% |
| 161517 | Select Plus PTE LTD (CTV) | 39,660 | 7.75% | 4.11% |
| 163091 | TCL ADS - Springserve | 37,600 | 7.34% | 3.59% |
| 160222 | PML Digital | 14,381 | 2.81% | 0.81% |
| 161212 | METAX SOFTWARE PTE. LTD. (Exchange) | 12,414 | 2.42% | 0.50% |
| 154037 | Equativ - oRTB CTV | 11,558 | 2.26% | 3.16% |
| 165045 | Roku - oRTB | 8,319 | 1.62% | **14.15%** |
| 160710 | Televisa Univision via SpringServe | 7,500 | 1.46% | 4.54% |
| 166449 | Coocaa (SKYWORTH) | 6,487 | 1.27% | 4.24% |
| 166869 | TV Azteca - Springserve | 1,981 | 0.39% | **5.50%** |
| ...otros 215 IDs | | ~177,500 | ~34.7% | ~24.1% |

**Conclusiones.**
- Hay **228 IDs para 222 nombres de publisher**: ningún ID apunta a dos nombres (la relación es limpia), pero algunos publishers operan con varias cuentas (p. ej. iion con 164918 y 166799, que sumadas son el 20.7% de las filas). Para agrupar "quién vende", usar el nombre; para reconciliar facturación, el ID.
- La asimetría filas/requests es el dato clave: **Roku con 1.62% de las filas mueve 14.2% de los requests**, y TV Azteca con 0.39% de filas mueve 5.5%. Al revés, TCL ADs (13.4% filas) solo aporta 9% del tráfico: mucho catálogo, menos volumen por combinación.

## 2. Publisher

**Glosario.** Nombre comercial del vendedor del inventario. Ojo: en CTV el "publisher" del reporte suele ser el **vendedor/integración**, no necesariamente el dueño del contenido — nombres como "Roku - oRTB", "TCL ADS - Springserve" o "Televisa Univision via OB" describen el **camino de suministro** (supply path): quién vende y por qué protocolo/ad server (oRTB = integración OpenRTB directa; SpringServe, FreeWheel, OB = el ad server intermediario).

**Datos.** 222 valores distintos, 100% fill. Top:

| Publisher | Filas | % filas | % requests |
|---|---:|---:|---:|
| OTTera.tv | 124,089 | 24.24% | 23.48% |
| iion Pty Ltd | 77,595 | 15.16% | 7.38% |
| TCL ADs (APAC) | 68,413 | 13.36% | 8.95% |
| TCL ADS - Springserve | 66,129 | 12.92% | 11.05% |
| Select Plus PTE LTD (CTV) | 39,660 | 7.75% | 4.11% |
| PML Digital | 14,383 | 2.81% | 0.81% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 12,414 | 2.42% | 0.50% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 11,558 | 2.26% | 3.16% |
| Roku - oRTB | 8,319 | 1.62% | 14.15% |
| Televisa Univision via SpringServe | 7,500 | 1.46% | 4.54% |
| Vidaa | 7,057 | 1.38% | 1.60% |
| Aluna Limited | 6,978 | 1.36% | 0.72% |
| Coocaa, a SKYWORTH company | 6,487 | 1.27% | 4.24% |
| OneFox - Tubi | 5,560 | 1.09% | 1.29% |
| Pluto LATAM via SpringServe | 4,362 | 0.85% | 0.18% |
| Kivi via Springserve | 4,225 | 0.83% | 0.22% |
| Televisa Univision via OB | 3,826 | 0.75% | 2.87% |
| TV Azteca - Springserve | 1,981 | 0.39% | 5.50% |
| ...otros 204 | ~51,500 | ~10.1% | ~7.9% |

**Conclusiones.**
- El suministro está **muy concentrado en fabricantes de TV (OEMs)**: OTTera + TCL (dos cuentas) + iion + Select Plus = **73.4% de las filas y ~55% de los requests**. TCL, Vidaa (Hisense), Coocaa (Skyworth), Kivi y Metax son todos ecosistemas de smart TV.
- Los **broadcasters locales** (TelevisaUnivision con dos rutas que suman 7.4% de requests, TV Azteca con 5.5%) pesan poco en filas pero mucho en tráfico por combinación — inventario premium y más homogéneo.
- Un mismo dueño aparece por **varias rutas** (TelevisaUnivision via SpringServe y via OB; Tubi vende via OneFox pero su app también aparece dentro del inventario de otros sellers): para análisis de supply path conviene normalizar por dueño real.

## 3. pageURL

**Glosario.** En web, sería la URL de la página. En CTV este campo transporta el **identificador de la app** (`app.bundle` de OpenRTB), y su formato delata la tienda de apps de cada plataforma:
- `com.xxx.yyy` — package name estilo Android/Google TV (com.tcl.\*, com.tubitv, tv.pluto.android).
- **Numérico** (151908, 552828, 974696...) — ID del **Roku Channel Store** (151908 = The Roku Channel, 552828 = ViX en Roku).
- `bXXXXXXXXX` (b08kj77pqy) — **ASIN de Amazon** (Fire TV).
- `gXXXXXXXXXXX` (g15147002586 = Samsung TV Plus) — ID de app de **Samsung Tizen**.
- `roku`, `+com.tcl.livetv` — valores malformados (genérico de plataforma; un `+` pegado por error de concatenación).

**Datos.** 638 valores distintos, 100% fill. Top:

| pageURL (bundle) | App | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| com.tcl.movieark | MovieArk (TCL) | 146,521 | 28.62% | 28.60% |
| com.tcl.livetv | Live TV (TCL) | 128,189 | 25.04% | 13.65% |
| com.tcl.waterfall.overseas | TCL Channel | 75,314 | 14.71% | 9.10% |
| com.tcl.browser | BrowseHere (TCL) | 52,904 | 10.33% | 4.93% |
| com.coolita.channel | Coolita (Coocaa) | 9,849 | 1.92% | 4.84% |
| 974696 | canal Roku | 7,503 | 1.47% | 1.14% |
| 151908 | The Roku Channel | 6,684 | 1.31% | **11.72%** |
| tv.vidaa.ui.plus | Vidaa (Hisense) | 6,669 | 1.30% | 1.20% |
| +com.tcl.livetv | (malformado) | 5,963 | 1.16% | 0.21% |
| 552828 | ViX (Roku) | 5,041 | 0.98% | 4.59% |
| com.univision.prendetv | ViX/PrendeTV | 4,946 | 0.97% | 3.53% |
| tv.vidaa.ui.apps.vix | ViX (Hisense) | 4,550 | 0.89% | 0.76% |
| com.tubitv | Tubi | 3,231 | 0.63% | **5.73%** |
| roku | (genérico) | 1,411 | 0.28% | 2.11% |
| ...otros ~610 | | ~58,000 | ~11.3% | ~8.7% |

**Conclusiones.**
- **Las 4 apps nativas de TCL suman el 78.7% de las filas pero solo el 56.3% de los requests** — el catálogo del dataset está sesgado a TCL; el tráfico real está más repartido.
- Hay ~7,400 filas (1.4%) con bundle malformado (`+com.tcl.livetv`, `roku`): romperían cualquier join con listas de apps o app-ads.txt. Conviene limpiar el `+` y descartar los genéricos.
- El mismo servicio aparece con **bundles distintos por plataforma** (ViX = 552828 en Roku + com.univision.prendetv en Android + tv.vidaa.ui.apps.vix en Hisense). Para medir alcance por servicio hay que mapear bundles → servicio.

## 4. App Name

**Glosario.** Nombre comercial de la app (`app.name` en OpenRTB), tal como lo declara el publisher o la tienda. Es texto libre y localizado, por eso una misma app aparece con múltiples variantes.

**Datos.** 377 valores distintos (376 útiles), fill 91.90% de filas / 93.43% de requests (el resto `Not Available`). Top:

| App Name | Filas | % filas | % requests |
|---|---:|---:|---:|
| MovieArk: Stream Movies & Live | 146,521 | 28.62% | 28.60% |
| Live TV | 118,268 | 23.10% | 13.32% |
| TCL CHANNEL | 75,314 | 14.71% | 9.10% |
| Browser TV Web - BrowseHere | 52,904 | 10.33% | 4.93% |
| *Not Available* | 41,463 | 8.10% | 6.57% |
| Coolita Channel | 9,849 | 1.92% | 4.84% |
| ViX: TV, Sports and News | 7,407 | 1.45% | 4.07% |
| The Roku Channel | 6,684 | 1.31% | 11.72% |
| ViX: TV, Deportes y Noticias | 5,041 | 0.98% | 4.59% |
| FreeTube- Search & Watch Free | 4,057 | 0.79% | 0.09% |
| Tubi: Free Movies & Live TV | 3,231 | 0.63% | 5.73% |
| ViX: Cine y TV Gratis en Español | 3,193 | 0.62% | 0.73% |
| Plex (2 variantes) | 5,917 | 1.16% | 0.20% |
| Tubi (otras 4 variantes) | ~5,100 | ~1.0% | ~1.4% |
| ...otros | | | |

**Conclusiones.**
- **ViX aparece con al menos 6 nombres** distintos (inglés, español, portugués, por plataforma) y Tubi con 5. Sumadas, ViX ronda el 4.4% de filas y ~10% de requests — mucho más de lo que aparenta cualquier variante suelta. **Nunca agrupar por App Name; usar pageURL/bundle** y un mapa bundle→servicio.
- "Live TV", "Browser TV Web", "Runtime" o "LG" son nombres genéricos que no identifican contenido — vienen del sistema operativo del TV, no de una app editorial.
- El 8.1% sin nombre coincide en gran parte con inventario agregado de exchanges (OTTera, Metax) donde la app original se pierde en la reventa.

## 5. Country

**Glosario.** País del dispositivo (geo de `device.geo.country`), normalizado a nombre en inglés.

**Datos.** 18 valores, 100% fill. Distribución completa:

| País | Filas | % filas | % requests |
|---|---:|---:|---:|
| Mexico | 144,901 | 28.30% | **61.25%** |
| Argentina | 97,257 | 19.00% | 17.27% |
| Chile | 58,110 | 11.35% | 5.91% |
| Colombia | 50,350 | 9.83% | 6.27% |
| Peru | 42,914 | 8.38% | 2.50% |
| Ecuador | 21,686 | 4.24% | 1.39% |
| Dominican Republic | 18,986 | 3.71% | 1.23% |
| Costa Rica | 16,674 | 3.26% | 1.31% |
| Honduras | 10,681 | 2.09% | 0.23% |
| Panama | 10,316 | 2.01% | 0.58% |
| Venezuela | 8,891 | 1.74% | 0.63% |
| El Salvador | 7,639 | 1.49% | 0.22% |
| Guatemala | 7,093 | 1.39% | 0.23% |
| Puerto Rico | 7,046 | 1.38% | 0.43% |
| Uruguay | 5,017 | 0.98% | 0.40% |
| Paraguay | 1,807 | 0.35% | 0.09% |
| Nicaragua | 1,470 | 0.29% | 0.03% |
| Bolivia | 1,162 | 0.23% | 0.04% |

**Conclusiones.**
- **México es el 61% del tráfico con solo el 28% de las filas**: sus combinaciones mueven en promedio 4x más requests que las del resto (ahí están Roku, TV Azteca y TelevisaUnivision con volúmenes enormes por fila).
- Argentina es el segundo mercado en ambas vistas (19% filas, 17.3% requests). Chile, Colombia y Perú tienen mucha variedad de inventario (29.6% de filas juntas) pero solo 14.7% del tráfico.
- Los 7 países más chicos (PY, NI, BO, UY, PR, GT, SV) suman menos del 1.7% del tráfico: cualquier análisis por país ahí se basa en pocas combinaciones y hay que leerlo con cautela.

## 6. contentGenre

**Glosario.** `content.genre` de OpenRTB: "género que mejor describe el contenido". La spec lo define como **string libre** (no hay taxonomía obligatoria), y eso se nota: cada publisher manda su propio vocabulario, en minúsculas/mayúsculas distintas, a veces un solo género y a veces listas separadas por coma.

**Datos.** 7,567 valores distintos (7,564 útiles). Fill: 98.73% filas / 94.25% requests — **el campo content mejor poblado**. Top:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| drama | 49,904 | 9.75% | 10.72% |
| other | 29,895 | 5.84% | 3.11% |
| documentary | 26,571 | 5.19% | 2.95% |
| horror | 19,147 | 3.74% | 3.31% |
| comedy | 17,529 | 3.42% | 3.24% |
| drama,romance | 11,546 | 2.26% | 2.57% |
| action | 9,055 | 1.77% | 1.20% |
| thriller | 8,020 | 1.57% | 0.74% |
| music | 7,336 | 1.43% | 1.37% |
| sports | 6,520 | 1.27% | 1.85% |
| *Not Applicable* | 6,273 | 1.23% | 5.73% |
| news | 5,259 | 1.03% | 2.62% |
| horror,thriller | 4,913 | 0.96% | 1.05% |
| entertainment | 4,765 | 0.93% | **4.86%** |
| kids | 4,453 | 0.87% | 0.41% |
| romance | 4,160 | 0.81% | 0.88% |
| drama,comedy | 4,160 | 0.81% | 0.75% |
| movies | 3,934 | 0.77% | 0.42% |
| drama,thriller | 3,909 | 0.76% | 0.96% |
| crime / western / sci-fi / adventure / anime... | | <0.7% c/u | |
| ...otros 7,530+ valores | 252,394 | 49.30% | |

**Conclusiones.**
- La cardinalidad (7,567) no significa 7,567 géneros: son **combinaciones y variantes de ~30-40 géneros base**. `drama,romance` y `romance,drama` cuentan como valores distintos; hay hasta duplicados internos (`music,music`, 2,311 filas). Para usarlo hay que hacer split por coma + normalizar a minúsculas + deduplicar.
- El vocabulario mezcla niveles: géneros reales (drama, horror), **tipos de contenido** (movies, entertainment, news) y audiencias (kids). "other" (5.8%) y "Not Applicable" con 5.7% de requests indican que el volumen grande viene con género pobre.
- Aun así, es la mejor señal contextual disponible del dataset: tras normalizar quedaría una taxonomía de ~30 géneros con >90% de cobertura.

## 7. contentCategory

**Glosario.** `content.cat` de OpenRTB: array de categorías IAB del contenido. La taxonomía la define el campo `cattax` (que este reporte no incluye); si no se declara, aplica la **Content Category Taxonomy 1.0** (códigos "IABx-y", hoy deprecada). Glosario de los códigos que aparecen:
- `IAB1` Arts & Entertainment; `IAB1-4` Humor; `IAB1-5` Movies; `IAB1-6` Music; `IAB1-7` Television.
- `IAB9-30` Video & Computer Games; `IAB11` Law, Gov't & Politics; `IAB12` News; `IAB17` Sports (`IAB17-1` Auto Racing, `IAB17-12` Football); `IAB20` Travel.
- `IAB1-22` **no existe** en la taxonomía 1.0 (IAB1 solo llega a IAB1-7): es un código inválido que algún SSP inventó o mapeó mal.
- Valores solo numéricos (`[640]`, `[325]`, `[647]`, `[324]`...) parecen IDs de las **Content Taxonomy 2.x/3.x** enviados sin declarar `cattax` — sin ese campo son ambiguos.
- `[sports]`, `[Live]` — texto libre fuera de toda taxonomía.
- `[-7]` — **no es una categoría de ninguna taxonomía**; es un placeholder/bug de normalización (probablemente un código de error interno que quedó serializado como categoría).

**Datos.** 471 valores distintos. Fill real: **21.99% filas / 29.96% requests**. Top:

| Valor | Significado | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| **[-7]** | inválido (placeholder) | **399,418** | **78.01%** | **70.04%** |
| [IAB1] | Arts & Entertainment | 32,768 | 6.40% | 6.09% |
| [IAB1-22] | inválido (no existe) | 19,524 | 3.81% | 1.67% |
| [IAB1-5] | Movies | 7,251 | 1.42% | 1.10% |
| [IAB12] | News | 6,283 | 1.23% | 1.26% |
| [IAB1, IAB1-5] | A&E + Movies | 4,638 | 0.91% | 0.30% |
| [IAB1-7] | Television | 4,594 | 0.90% | **5.95%** |
| [sports] | texto libre | 4,039 | 0.79% | 0.08% |
| [IAB1-5, IAB1-7] | Movies + TV | 3,833 | 0.75% | **3.98%** |
| [IAB17] | Sports | 3,669 | 0.72% | 1.04% |
| [640], [325], [647], [324]... | taxonomía 2.x sin declarar | ~7,300 | ~1.4% | ~0.2% |
| [IAB1-6] | Music | 1,405 | 0.27% | 0.53% |
| [IAB1-7, IAB17-12] | TV + Football | 1,320 | 0.26% | 0.75% |
| [IAB9-30] | Video Games | 1,224 | 0.24% | 0.16% |
| [Live] | texto libre | 1,042 | 0.20% | 0.08% |
| ...otros ~440 | | 10,117 | 1.98% | |

**Conclusiones.**
- Es **la columna más rota del dataset**: 78% de las filas traen el placeholder `[-7]`, y de lo restante una parte usa códigos inválidos (`IAB1-22`), taxonomías sin declarar (numéricos) o texto libre. La categoría IAB limpia y válida cubre apenas ~17% de filas.
- Lo poco válido está dominado por la rama IAB1 (entretenimiento), lo cual es coherente con CTV pero aporta poca granularidad para contextual/brand safety.
- Dato útil: las filas con `[IAB1-7]` y `[IAB1-5, IAB1-7]` (Roku, TelevisaUnivision) concentran ~10% del tráfico — los players grandes sí categorizan; el placeholder viene masivamente del ecosistema TCL/OEM.

## 8. contentSeries

**Glosario.** `content.series` de OpenRTB: nombre de la serie a la que pertenece el contenido (ej. "The Office"). Valores especiales encontrados:
- `d41d8cd98f00b204e9800998ecf8427e` — **hash MD5 de la cadena vacía**. Viene del inventario de Roku, que ofusca el nombre de la serie con MD5 por privacidad; cuando la serie está vacía, el hash delata que no había valor. Es un "vacío disfrazado".
- `{{CONTENT_SERIES}}` — **macro de ad server sin reemplazar**: el publisher configuró la variable y nunca se sustituye.
- `VOD`, `No Series`, `Run Of Video Network`, `Research Unit` — placeholders operativos, no series reales.
- `OTT Studios Entertainment On Demand / Sports Livestream / Entertainment Livestream` — nombres de feeds/canales del proveedor OTT Studios, no series.

**Datos.** 1,814 valores distintos. Fill real: **5.33% filas / 6.72% requests — la columna con menos datos del dataset**. Distribución:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Not Available* | 480,432 | 93.83% | 82.31% |
| d41d8cd98f... (MD5 de vacío) | 4,208 | 0.82% | **10.96%** |
| VOD | 3,176 | 0.62% | 0.37% |
| OTT Studios Entertainment On Demand | 861 | 0.17% | 0.02% |
| {{CONTENT_SERIES}} | 603 | 0.12% | 0.23% |
| No Series | 488 | 0.10% | 0.01% |
| OTT Studios Sports Livestream | 473 | 0.09% | 0.04% |
| Doña Bárbara | 311 | 0.06% | 0.01% |
| series reales (Chicago Fire, MasterChef México, Doctor en Turno, J1 League, Podpah...) | ~17,900 | ~3.5% | ~2% |

**Conclusiones.**
- El 93.8% ni siquiera trae el campo, y de lo que llega "poblado", buena parte es placeholder. Las series con nombre real son ~3-4% de filas: telenovelas y TV mexicana (Doña Bárbara, MasterChef México), series US (Chicago Fire, NCIS — vía Puerto Rico/Roku), contenido brasileño (Podpah) y deportes (J1 League).
- El hash MD5 vacío pesa 11% de los requests porque va pegado al volumen gigante de Roku: **si se cuenta "series poblada" sin filtrar el hash, el fill rate por requests se infla de 6.7% a ~18%** — trampa clásica en QA de metadata.
- Tal como está, la columna solo sirve para casos puntuales de content targeting en los pocos publishers que la mandan bien.

## 9. contentIsTitlePresent

**Glosario.** **No es un campo OpenRTB**: es una bandera derivada por la plataforma del reporte que indica si el bid request traía `content.title`. Booleano `true`/`false`.

**Datos.** 2 valores, 100% fill. Distribución completa:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| true | 469,754 | 91.75% | 76.23% |
| false | 42,246 | 8.25% | 23.77% |

**Conclusiones.**
- Consistencia interna perfecta: el 8.25% de `false` coincide exactamente con el 8.26% de `Not Applicable` en contentTitle — la bandera es fiable.
- El dato interesante está en la vista por requests: **casi una cuarta parte del tráfico (23.8%) viaja sin título**, aunque solo el 8% de las combinaciones. El título se pierde justo en las rutas de mayor volumen (México, Roku/EPG, exchanges agregadores).

## 10. contentLength

**Glosario.** `content.len` de OpenRTB: **duración del contenido en segundos**. Aquí NO viene en segundos: los únicos valores son los enteros 1 a 8. Contenido CTV de 1-8 segundos no existe, así que son **buckets de duración** (o un mapeo roto). La forma de la distribución (5 y 6 dominan, con 4 y 8 detrás) sugiere buckets tipo rangos de minutos, pero **el mapeo exacto no es deducible del archivo — hay que confirmarlo con la fuente antes de usar la columna**.

**Datos.** 9 valores distintos (8 útiles). Fill: 10.94% filas / **23.61% requests**. Distribución completa:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Not Applicable* | 456,001 | 89.06% | 76.39% |
| 6 | 16,137 | 3.15% | 5.01% |
| 5 | 14,931 | 2.92% | **7.57%** |
| 4 | 13,428 | 2.62% | 5.49% |
| 8 | 7,053 | 1.38% | 3.72% |
| 7 | 2,389 | 0.47% | 1.44% |
| 3 | 1,065 | 0.21% | 0.25% |
| 2 | 858 | 0.17% | 0.11% |
| 1 | 138 | 0.03% | 0.01% |

**Conclusiones.**
- El fill por requests (23.6%) duplica el fill por filas (10.9%): quien manda duración son los publishers de alto volumen (Roku sobre todo — en Puerto Rico, donde Roku domina, el fill llega a 65%).
- La distribución es unimodal centrada en 4-6: si los buckets son crecientes con la duración, el grueso del inventario declarado sería contenido de duración media (episodios/películas), con poco contenido corto (1-3).
- **No usar como duración numérica** en ningún cálculo hasta confirmar la tabla de buckets con el proveedor del reporte.

## 11. contentLanguage

**Glosario.** `content.language` de OpenRTB: idioma del contenido en **ISO-639-1 alpha-2** (dos letras: en, es, pt...). Valores fuera de norma encontrados: `spa`, `eng`, `por` (ISO-639-2 de tres letras, que la spec reserva para el campo `langb`), `sp` (no existe), `c` (basura, probablemente truncamiento), `504` (basura numérica). `ca` es catalán — real, y cuadra con títulos como "catalunya über alles".

**Datos.** 483 valores distintos (481 útiles). Fill: 79.98% filas / 86.74% requests. Top:

| Valor | Idioma | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| en | inglés | 249,287 | 48.69% | 40.22% |
| es | español | 136,155 | 26.59% | **42.06%** |
| *Not Applicable* | | 102,189 | 19.96% | 13.25% |
| pt | portugués | 6,325 | 1.24% | 1.94% |
| ru | ruso | 2,356 | 0.46% | 0.39% |
| hi | hindi | 1,976 | 0.39% | 0.67% |
| c | basura | 1,588 | 0.31% | 0.04% |
| spa | español (formato inválido) | 1,478 | 0.29% | 0.09% |
| de | alemán | 1,052 | 0.21% | 0.11% |
| fr / ja / eng / it / he / fa / ko / ca / ka / bn / hr / zh... | | <700 c/u | <0.15% c/u | |

**Conclusiones.**
- Paradoja llamativa para LATAM: **por filas domina el inglés (48.7% vs 26.6% español), pero por requests gana el español (42.1% vs 40.2%)**. El catálogo importado en inglés es enorme, pero la audiencia consume (y los publishers priorizan) contenido en español. El español sub-representa en variedad y sobre-representa en volumen.
- Sumando variantes (`es`+`spa`+`sp`), el español real ronda 26.9% de filas; conviene normalizar los códigos de 3 letras antes de segmentar.
- La cola de idiomas (ruso, hindi, alemán, persa, georgiano...) delata catálogos globales de relleno en apps OEM — inventario probablemente de baja afinidad para audiencias LATAM.
- 483 "idiomas" distintos cuando ISO-639-1 tiene ~180 códigos: hay decenas de valores basura de baja frecuencia (la cola completa está en el JSON).

## 12. contentIsLiveStream

**Glosario.** `content.livestream` de OpenRTB: entero donde **1 = transmisión en vivo/lineal** (broadcast programado, canales FAST, eventos) y **0 = bajo demanda (VOD)** o iniciado por el usuario.

**Datos.** 3 valores distintos (1 útil). Fill: 28.90% filas / 38.02% requests. Distribución completa:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Unknown* | 207,154 | 40.46% | 35.54% |
| *Not Available* | 156,891 | 30.64% | 26.44% |
| 1 (live) | 147,955 | 28.90% | 38.02% |

**Conclusiones.**
- **Nunca llega un 0.** Los publishers solo marcan el campo cuando es live y lo omiten para VOD, así que la ausencia NO puede leerse como VOD: queda indistinguible de "no reportado". El campo sirve como señal positiva de live (38% del tráfico confirmado live) pero no permite calcular la proporción real live vs VOD.
- Que un 38% del tráfico sea live confirmado cuadra con el peso de canales FAST/lineales (Live TV de TCL, EPG de Roku, canales de TV Azteca/Televisa).
- La coexistencia de `Unknown` y `Not Available` (dos centinelas para lo mismo) confirma que el reporte mezcla capas de normalización distintas según el vendor.

## 13. contentTitle

**Glosario.** `content.title` de OpenRTB: título del contenido (ej. "A New Hope"). Valores no literales encontrados: `roku` y `epg` (placeholders de la guía de programación de Roku — el título real se oculta), `{{content_title}}` (macro sin reemplazar), `run of video network` (placeholder de red). Los sufijos ": trailer" indican inventario pre-roll sobre trailers (mucho volumen de OTTera/OTT Studios).

**Datos.** **13,648 valores distintos — la columna de mayor cardinalidad**. Fill: 91.74% filas / 76.18% requests. Top:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Not Applicable* | 42,304 | 8.26% | **23.82%** |
| roku (placeholder) | 942 | 0.18% | **3.34%** |
| the baddest bad boy | 772 | 0.15% | 0.29% |
| haus of horror | 753 | 0.15% | 0.26% |
| epg (placeholder) | 747 | 0.15% | 2.49% |
| eve | 732 | 0.14% | 0.28% |
| hatchback | 639 | 0.12% | 0.36% |
| catalunya über alles! (mojibake en origen) | 616 | 0.12% | 0.49% |
| ~16 títulos "X: trailer" | ~9,400 | ~1.9% | ~4.4% |
| {{content_title}} (macro) | 576 | 0.11% | 0.02% |
| las estrellas | 528 | 0.10% | 0.31% |
| ...otros 13,600 títulos | 451,979 | 88.28% | |

**Conclusiones.**
- Es la columna con la cola más larga: el 88% de las filas está fuera del top 30 — títulos únicos de catálogo. Eso es bueno (metadata real, no placeholders) pero inutilizable sin agrupar por serie/género.
- Los placeholders `roku`+`epg` apenas son 0.33% de filas pero **5.8% de los requests**: el inventario de mayor volumen (Roku lineal) esconde el título. Sumado al 23.8% de requests sin título, **~30% del tráfico no es targeteable por título**.
- El top está lleno de películas B de terror y sus trailers (OTT Studios/OTTera repite el mismo catálogo en todos los países) — señal de que gran parte de la "variedad" es el mismo catálogo de relleno replicado.
- Hay problemas de encoding en origen (`catalunya �ber alles!` con carácter de reemplazo ya grabado en el archivo): los joins por título exacto van a fallar en títulos con acentos.

## 14. contentRating

**Glosario.** `content.contentrating` de OpenRTB: clasificación de edad del contenido. Texto libre en la práctica; en el dataset conviven **cinco sistemas**:
- **TV Parental Guidelines (EEUU):** tv-g (todos), tv-pg (supervisión), tv-14 (14+), tv-ma (adultos). Variantes sucias: tv14, tvpg, `tvpg_tv_14` / `tvpg_tv_ma` (sistema y rating concatenados por error).
- **MPAA (cine EEUU):** g, pg, pg-13, r (17+ acompañado), nc-17 (adultos). Variante sucia: pg13.
- **Edades numéricas** (10, 12, 14, 16, 18): sistemas locales por edad — coincide con ClassInd de Brasil y otros sistemas latinoamericanos/europeos.
- **RTC México:** el valor `b` (2,290 filas) encaja con la clasificación mexicana (A/B/B15/C/D); `b15` también aparece en la cola.
- **Sin clasificar:** nr, not rated, `banned` (1,920 filas — "prohibido", valor anómalo), `dv-t` (no identificado), `13+`/`16+` (estilo app stores).

**Datos.** 182 valores distintos (177 útiles). Fill: 84.89% filas / 88.17% requests. Top:

| Valor | Sistema | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| *Not Applicable* | | 77,174 | 15.07% | 11.79% |
| tv-14 | TV Parental | 58,281 | 11.38% | **15.73%** |
| tv-ma | TV Parental | 57,485 | 11.23% | 9.67% |
| r | MPAA | 56,676 | 11.07% | 7.75% |
| tv-pg | TV Parental | 41,978 | 8.20% | 5.08% |
| nr | sin clasificar | 37,769 | 7.38% | 4.26% |
| g | MPAA | 29,881 | 5.84% | 4.25% |
| pg-13 | MPAA | 12,319 | 2.41% | 2.29% |
| nc-17 | MPAA | 12,055 | 2.35% | 2.29% |
| not rated | sin clasificar | 11,998 | 2.34% | 1.69% |
| 12 / 14 / 18 / 15 / 13 / 16 / 10 | edad numérica | 57,643 | 11.26% | 8.20% |
| tv-g | TV Parental | 5,852 | 1.14% | 1.25% |
| tv14 / tvpg / tvpg_tv_14 / tvpg_tv_ma | variantes sucias | 9,948 | 1.94% | **8.53%** |
| b | RTC México | 2,290 | 0.45% | 2.76% |
| banned / dv-t / 13+ / 16+ | anómalos | ~7,400 | ~1.5% | ~1.7% |
| ...otros ~150 | | 25,886 | 5.06% | |

**Conclusiones.**
- Buena cobertura (88% del tráfico trae rating) pero **sin normalizar es inservible para brand safety**: "tv-14", "tv14", "tvpg_tv_14", "14" y "13+" son la misma idea en 5 formatos. Un mapa de ~180 valores → 4-5 niveles de edad (todos / 7+ / 13+ / 16+ / adulto) es factible y cubriría >95% de lo poblado.
- Agregando por severidad, el contenido adulto/maduro (tv-ma, r, nc-17, 18) ronda el 27% de filas — relevante si hay restricciones de marca.
- ~10% de filas declaran explícitamente "sin clasificar" (nr/not rated), que para muchos anunciantes equivale a inventario no apto — conviene tratarlo como categoría propia, no como vacío.
- El 8.5% de requests con las variantes concatenadas (`tvpg_tv_14`) viene de una integración concreta (TV Azteca/Roku) — un solo fix del publisher limpiaría casi 9% del tráfico.

## 15. Total Requests

**Glosario.** Número de bid requests (solicitudes de puja) registradas para esa combinación en el periodo del reporte (4–18 ago 2026). Es la medida de **volumen/alcance potencial**, no de impresiones servidas.

**Datos.** Columna numérica, 100% fill. Estadísticos:

| Métrica | Valor |
|---|---:|
| Mínimo | 29,520 |
| Mediana | 109,440 |
| Media | 834,781 |
| p75 | 324,720 |
| p90 | 1,054,560 |
| p99 | 10,028,517 |
| Máximo | 4,547,172,800 (4.5 mil millones, WhaleLive/México) |
| **Share del top 1% de filas** | **50.09% de todos los requests** |

**Conclusiones.**
- Distribución de cola pesadísima: la media es casi 8x la mediana y **el 1% de las combinaciones concentra la mitad del tráfico**. Cualquier promedio "por fila" del dataset está dominado por ese 1%; por eso este reporte separa siempre % filas de % requests.
- El mínimo de 29,520 sugiere que el reporte tiene un umbral de corte (no hay combinaciones pequeñas), así que la cola real de inventario es aún más larga de lo visible.
- Los valores parecen redondeados/muestreados (muchos múltiplos de 80): serían estimaciones extrapoladas, no conteos exactos.

## 16. eCPM

**Glosario.** *Effective CPM*: ingresos efectivos por cada mil impresiones para esa combinación en el periodo. eCPM = 0 significa que esa combinación **no generó revenue** en el periodo (no ganó subastas o no se midió), no necesariamente que sea invendible.

**Datos.** Columna numérica, 100% fill. Estadísticos:

| Métrica | Valor |
|---|---:|
| Filas con eCPM = 0 | 422,853 (**82.59%**) |
| Filas con eCPM > 0 | 89,147 (17.41%) |
| Media (solo > 0) | 4.850 |
| Mediana (solo > 0) | 3.115 |
| p90 (solo > 0) | 10.50 |
| Máximo | 200.0 |
| **eCPM ponderado por requests (solo > 0)** | **4.98** |

Distribución por rangos:

| Rango eCPM | Filas | % filas | % requests |
|---|---:|---:|---:|
| 0 | 422,853 | 82.59% | 48.86% |
| 0 – 1 | 4,007 | 0.78% | 2.24% |
| 1 – 3 | 38,567 | 7.53% | 17.47% |
| 3 – 5 | 14,796 | 2.89% | 8.50% |
| 5 – 10 | 18,233 | 3.56% | **17.69%** |
| 10 – 20 | 13,349 | 2.61% | 5.06% |
| >= 20 | 195 | 0.04% | 0.18% |

**Conclusiones.**
- Aunque el 82.6% de las filas no monetiza, ese grupo solo representa el **48.9% de los requests**: la mitad del tráfico sí corre por combinaciones con revenue. La monetización sigue al volumen.
- El grueso del tráfico monetizado se vende entre 1 y 10 USD de eCPM, con bloques fuertes en 1-3 (17.5% del tráfico) y 5-10 (17.7%) — rango sano para CTV LATAM.
- Los eCPMs >20 son anecdóticos (195 filas, 0.18% del tráfico). **El máximo de 200.0 es un outlier claramente sospechoso** (valor "redondo" exacto, 4x el siguiente rango) — auditarlo antes de usarlo en cualquier promedio.
- Cruce con metadata (calculado sobre las 89,147 filas con eCPM > 0): las filas con `contentLanguage` poblado promedian eCPM **5.09 vs 3.70 sin él (+37%)**; contentGenre +16% (4.86 vs 4.18), contentTitle +10% (4.88 vs 4.44) y contentRating +10% (4.90 vs 4.45). En cambio contentCategory, contentSeries, contentLength y contentIsLiveStream no muestran diferencia. **La metadata descriptiva (idioma, género, título, rating) correlaciona con mejor monetización; la estructural rota, no.**

---

# PARTE 2 — Análisis por país

Metodología: para cada país se filtraron sus filas y se recalculó, columna por columna, el número de valores distintos, el fill rate y la distribución. Los porcentajes de los "top valores" son **% sobre las filas de ese país**. El top-15 completo de cada columna de cada país está en `reporte-content-objects-detallado-v11.json` (clave `countries`). "eCPM pond." = eCPM ponderado por requests sobre las filas con eCPM > 0.

## Tabla comparativa general

| País | Filas | % requests | % filas eCPM=0 | eCPM medio (>0) | eCPM pond. | Fill category | Fill livestream | Fill length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| México | 144,901 | 61.25% | 81.3% | 2.66 | 4.44 | 23.4% | 25.7% | 17.3% |
| Argentina | 97,257 | 17.27% | 80.1% | 6.23 | 6.25 | 11.3% | 31.7% | 4.4% |
| Colombia | 50,350 | 6.27% | 87.6% | 2.66 | 2.99 | 24.3% | 27.9% | 9.5% |
| Chile | 58,110 | 5.91% | 80.2% | 7.35 | **8.33** | 14.5% | 17.5% | 6.8% |
| Perú | 42,914 | 2.50% | 81.3% | 6.45 | 6.09 | 23.8% | 27.6% | 7.3% |
| Ecuador | 21,686 | 1.39% | 93.9% | 6.23 | 7.54 | 20.6% | 30.8% | 6.8% |
| Costa Rica | 16,674 | 1.31% | **61.9%** | 4.57 | 5.94 | 25.8% | 41.5% | 11.2% |
| Rep. Dominicana | 18,986 | 1.23% | 91.6% | 5.71 | 5.45 | 15.9% | 47.4% | 5.5% |
| Venezuela | 8,891 | 0.63% | **100%** | — | — | 42.0% | 45.6% | 21.5% |
| Panamá | 10,316 | 0.58% | 89.0% | 4.35 | 4.27 | 26.6% | 29.8% | 4.1% |
| Puerto Rico | 7,046 | 0.43% | 88.3% | **8.59** | 8.14 | **64.4%** | 39.6% | **65.2%** |
| Uruguay | 5,017 | 0.40% | 97.4% | 6.94 | 5.44 | 45.9% | 25.1% | 18.8% |
| Honduras | 10,681 | 0.23% | 78.7% | 3.97 | 3.99 | 26.2% | 32.7% | 3.4% |
| Guatemala | 7,093 | 0.23% | 77.4% | 4.89 | 4.63 | 49.3% | 22.5% | 8.9% |
| El Salvador | 7,639 | 0.22% | 85.6% | 6.21 | 6.43 | 42.0% | 30.3% | 3.8% |
| Paraguay | 1,807 | 0.09% | 87.2% | 5.96 | 5.94 | 21.2% | **69.3%** | 4.9% |
| Bolivia | 1,162 | 0.04% | 99.8% | 2.97 | 1.99 | **79.1%** | 59.0% | 49.6% |
| Nicaragua | 1,470 | 0.03% | 68.4% | 6.09 | 7.80 | 56.9% | 42.6% | 36.9% |

Lectura rápida: los mercados grandes tienen la peor metadata (paradójicamente), Venezuela no monetiza nada, Puerto Rico se comporta como mercado estadounidense, y en los países chicos la metadata mejora porque el mix de publishers cambia (menos TCL, más Roku/Coolita).

## México — 144,901 filas (28.3%) · 61.25% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 169 | 100% | OTTera.tv 14.6%, iion 13.0%, TCL ADS-Springserve 11.1%, TCL ADs (APAC) 11.0%, Equativ 7.1% |
| Publisher ID | 172 | 100% | (el país con más cuentas activas) |
| pageURL | 488 | 100% | com.tcl.livetv 25.3%, com.tcl.movieark 21.6%, com.tcl.browser 6.1%, 974696 (Roku) 5.1% |
| App Name | 299 | 82.8% | Live TV 22.5%, MovieArk 21.6%, *Not Available 17.2%*, BrowseHere 6.1%, TCL CHANNEL 4.2% |
| contentGenre | 5,667 | 99.0% | drama 10.6%, documentary 4.3%, other 4.1%, comedy 3.7%, horror 3.3% |
| contentLanguage | 476 | 78.6% | en 37.4%, es 36.3%, *N/A 21.2%*, pt 0.8%, spa 0.8% |
| contentRating | 149 | 84.4% | *N/A 15.6%*, tv-14 13.4%, r 10.0%, tv-ma 8.3%, tv-pg 8.1% |
| contentCategory | 308 | 23.4% | *[-7] 76.5%*, [IAB1] 4.7%, [IAB1-5] 3.8%, [IAB12] 2.7%, [IAB1-22] 2.1% |
| contentIsLiveStream | 3 | 25.7% | *Unknown 39.2%*, *N/A 35.0%*, 1 25.7% |
| contentLength | 9 | 17.3% | *N/A 82.7%*, 6 6.5%, 5 3.9%, 8 3.2%, 4 2.2% |
| contentSeries | 1,471 | 6.8% | *N/A 91.7%*, md5-vacío 1.6%, VOD 0.5%, {{CONTENT_SERIES}} 0.2% |
| contentTitle | 10,252 | 82.2% | *N/A 17.8%*, las estrellas 0.4%, canal 5 0.3%, golden 0.2% |
| contentIsTitlePresent | 2 | — | true 82.2%, false 17.8% |

**Conclusiones — México:**
- Es el único país con **casi paridad inglés/español** (37.4% vs 36.3%): el peso de los broadcasters locales (Televisa con "Las Estrellas" y "Canal 5" como top títulos, TV Azteca, ViX) equilibra el catálogo importado.
- Concentra la peor tasa de títulos del continente fuera de Puerto Rico: 17.8% de filas sin título (vs 2-5% en el resto). La gran mayoría de las filas sin título del dataset son mexicanas — la ruta Roku/EPG y los agregadores pierden el título justo en el mercado más grande.
- El eCPM medio no-cero es el más bajo de los mercados grandes (2.66), pero el ponderado sube a 4.44: hay mucha cola barata y un núcleo premium de alto volumen (Roku, que mueve el 14.2% de los requests globales casi todo desde aquí, y TV Azteca con eCPMs en el rango de 6).
- Con 169 publishers y 488 bundles es, por lejos, el mercado más fragmentado: la deduplicación de supply paths importa más aquí que en ningún otro país.

## Argentina — 97,257 filas (19.0%) · 17.27% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 101 | 100% | OTTera.tv 21.2%, TCL ADS-Springserve 20.5%, iion 20.3%, TCL ADs (APAC) 17.8%, PML Digital 5.5% |
| pageURL | 148 | 100% | com.tcl.waterfall 31.6%, com.tcl.livetv 25.6%, com.tcl.movieark 18.7%, com.tcl.browser 17.7% |
| App Name | 110 | 96.0% | TCL CHANNEL 31.6%, Live TV 23.7%, MovieArk 18.7%, BrowseHere 17.7% |
| contentGenre | 2,372 | 98.9% | drama 7.9%, documentary 6.1%, other 6.0%, horror 3.4%, comedy 3.3% |
| contentLanguage | 48 | 78.3% | en 39.4%, es 35.9%, *N/A 21.7%*, pt 0.9%, ru 0.4% |
| contentRating | 120 | 87.3% | tv-ma 13.2%, *N/A 12.6%*, g 12.0%, r 10.9%, tv-14 8.6% |
| contentCategory | 112 | 11.3% | *[-7] 88.7%*, [IAB1-22] 3.9%, [IAB1] 3.2%, [IAB17] 0.4% |
| contentIsLiveStream | 3 | 31.7% | *N/A 38.3%*, 1 31.7%, *Unknown 30.0%* |
| contentLength | 9 | 4.4% | *N/A 95.6%*, 4 1.8%, 5 1.0%, 6 0.9% |
| contentSeries | 449 | 2.5% | *N/A 97.5%*, VOD 0.5%, {{CONTENT_SERIES}} 0.1% |
| contentTitle | 7,529 | 97.5% | *N/A 2.5%*, the baddest bad boy 0.1%, haus of horror 0.1% |
| contentIsTitlePresent | 2 | — | true 97.5%, false 2.5% |

**Conclusiones — Argentina:**
- **El mercado más "TCL" del dataset**: las 4 apps nativas de TCL suman el 93.6% de las filas. Eso explica sus dos extremos: excelente fill de título (97.5%, TCL siempre lo manda) y el peor fill de categoría de los mercados grandes (11.3%) junto con duración casi inexistente (4.4%), que TCL no manda.
- Segundo mercado por volumen y con buen precio: eCPM ~6.2 tanto medio como ponderado (sin la cola barata de México — la distribución es más pareja).
- Sin presencia relevante de broadcasters locales en el top: el inventario argentino de este dataset es esencialmente OEM + catálogo internacional (el top de títulos son las mismas películas B de OTT Studios que en todos lados).

## Colombia — 50,350 filas (9.8%) · 6.27% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 91 | 100% | iion 30.1%, OTTera.tv 24.6%, Select Plus 11.5%, TCL ADs (APAC) 11.1%, METAX 7.8% |
| pageURL | 170 | 100% | com.tcl.movieark 34.7%, com.tcl.livetv 28.8%, com.tcl.waterfall 13.3%, com.tcl.browser 8.0% |
| App Name | 129 | 96.6% | MovieArk 34.7%, Live TV 28.6%, TCL CHANNEL 13.3%, BrowseHere 8.0% |
| contentGenre | 1,311 | 98.5% | drama 10.2%, other 7.7%, documentary 5.0%, horror 4.1%, comedy 3.1% |
| contentLanguage | 30 | **62.1%** | en 42.0%, *N/A 37.9%*, es 15.2%, c (basura) 1.9%, pt 0.7% |
| contentRating | 97 | 80.2% | *N/A 19.8%*, r 11.9%, tv-14 9.8%, tv-pg 9.5%, nr 8.9% |
| contentCategory | 128 | 24.3% | *[-7] 75.7%*, [IAB1] 7.2%, [IAB1-22] 3.5%, [IAB1, IAB1-5] 2.5%, [sports] 1.9% |
| contentIsLiveStream | 3 | 27.9% | *Unknown 45.1%*, 1 27.9%, *N/A 27.0%* |
| contentLength | 9 | 9.5% | *N/A 90.5%*, 4 3.2%, 5 2.7%, 6 2.4% |
| contentSeries | 569 | 5.5% | *N/A 94.4%*, VOD 0.9%, No Series 0.1%, Esmeraldas 0.1% |
| contentTitle | 4,167 | 95.0% | *N/A 5.0%*, {{content_title}} 0.2%, eve 0.2%, haus of horror 0.2% |
| contentIsTitlePresent | 2 | — | true 95.0%, false 5.0% |

**Conclusiones — Colombia:**
- **El peor mercado en monetización de los grandes**: 87.6% de filas sin revenue y eCPM ponderado de 2.99 — menos de la mitad que Argentina y ~un tercio de Chile. Y no es por falta de volumen (es el 3° mercado por requests).
- Tiene además el peor fill de idioma de los mercados grandes (62.1%) y la mayor desproporción inglés/español (42.0% vs 15.2%): el inventario colombiano de este dataset es mayormente catálogo importado sin señal local. La combinación "no sé qué idioma es + no monetiza" difícilmente es casualidad.
- iion es aquí el seller líder (30.1%), a diferencia de todos los demás mercados grandes donde lidera OTTera o TCL.
- Aparece la macro sin reemplazar `{{content_title}}` entre los top títulos — el bug de configuración está activo en el supply colombiano. Como nota local, asoma la telenovela "Esmeraldas" en el top de series.

## Chile — 58,110 filas (11.3%) · 5.91% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 91 | 100% | iion 21.2%, TCL ADS-Springserve 19.3%, TCL ADs (APAC) 17.5%, OTTera.tv 17.4%, PML Digital 6.3% |
| pageURL | 144 | 100% | com.tcl.movieark 41.7%, com.tcl.livetv 34.9%, com.tcl.waterfall 7.4%, com.tcl.browser 5.4% |
| App Name | 106 | 92.2% | MovieArk 41.7%, Live TV 30.3%, *N/A 7.8%*, TCL CHANNEL 7.4% |
| contentGenre | 1,371 | 99.5% | drama 8.5%, other 6.8%, documentary 6.0%, horror 3.6%, comedy 3.3% |
| contentLanguage | 43 | 75.5% | en 53.0%, *N/A 24.5%*, es 18.3%, pt 1.4%, ru 0.5% |
| contentRating | 93 | 84.0% | *N/A 16.0%*, tv-ma 13.8%, r 11.9%, tv-14 10.6%, nr 9.3% |
| contentCategory | 109 | 14.5% | *[-7] 85.5%*, [IAB1] 6.5%, [IAB1-22] 0.8%, [IAB1, IAB1-5] 0.7% |
| contentIsLiveStream | 3 | **17.5%** | *N/A 42.3%*, *Unknown 40.2%*, 1 17.5% |
| contentLength | 9 | 6.8% | *N/A 93.2%*, 4 2.7%, 5 1.8%, 6 1.5% |
| contentSeries | 488 | 4.5% | *N/A 95.5%*, VOD 0.9%, {{CONTENT_SERIES}} 0.1%, QWEST 0.1% |
| contentTitle | 3,897 | 96.7% | *N/A 3.3%*, catalunya über alles! 0.2%, haus of horror 0.2% |
| contentIsTitlePresent | 2 | — | true 96.7%, false 3.3% |

**Conclusiones — Chile:**
- **El mercado grande con mejor precio**: eCPM ponderado 8.33 y medio 7.35, con una tasa de monetización normal (80% ceros). El inventario chileno monetizado paga un tercio más que el argentino y casi el triple que el colombiano.
- Perfil de consumo muy VOD/película: MovieArk (la app de películas de TCL) sola es el 41.7% de las filas, y el fill de livestream es el más bajo del dataset (17.5%) — inventario mayormente on-demand.
- Muy anglófono en catálogo: 53.0% en vs 18.3% es, el contenido local pesa poco en variedad.
- La metadata estructural (category 14.5%, length 6.8%) es pobre — el precio alto viene del mercado (demanda/poder adquisitivo), no de la calidad de señales.

## Perú — 42,914 filas (8.4%) · 2.50% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 83 | 100% | OTTera.tv 26.8%, iion 25.0%, Select Plus 12.9%, TCL ADs (APAC) 9.3%, Aluna 6.3% |
| pageURL | 100 | 100% | com.tcl.movieark 40.3%, com.tcl.livetv 26.8%, com.tcl.waterfall 15.2%, com.tcl.browser 5.9% |
| App Name | 70 | 95.0% | MovieArk 40.3%, Live TV 24.5%, TCL CHANNEL 15.2%, BrowseHere 5.9% |
| contentGenre | 1,640 | 98.0% | drama 11.2%, other 6.7%, documentary 5.0%, horror 4.5%, comedy 3.8% |
| contentLanguage | 28 | 69.8% | en 45.3%, *N/A 30.2%*, es 19.6%, pt 1.3%, c 0.8% |
| contentRating | 98 | 83.5% | *N/A 16.4%*, tv-ma 14.3%, tv-14 11.9%, r 11.8%, tv-pg 8.8% |
| contentCategory | 115 | 23.8% | *[-7] 76.2%*, [IAB1] 9.8%, [IAB1-22] 3.0%, [sports] 2.5% |
| contentIsLiveStream | 3 | 27.6% | *Unknown 52.1%*, 1 27.6%, *N/A 20.3%* |
| contentLength | 9 | 7.3% | *N/A 92.7%*, 4 2.8%, 5 1.7%, 6 1.5% |
| contentSeries | 475 | 4.2% | *N/A 95.7%*, VOD 0.9%, QWEST 0.2%, QWESTTV 0.1% |
| contentTitle | 4,421 | 95.9% | *N/A 4.1%*, the baddest bad boy 0.2%, catalunya über alles! 0.2% |
| contentIsTitlePresent | 2 | — | true 95.9%, false 4.1% |

**Conclusiones — Perú:**
- Mucho catálogo y poco tráfico: 8.4% de las filas pero solo 2.5% de los requests — las combinaciones peruanas mueven poco volumen cada una (el reparto entre OEMs sin un player dominante de alto volumen).
- Precio sano (eCPM ponderado 6.09, medio 6.45) con tasa de ceros normal (81.3%): mercado pequeño pero eficiente.
- Mismo patrón OEM que Chile (MovieArk 40.3%) y misma pobreza de metadata estructural. Nada local relevante en el top de títulos o series.

## Ecuador — 21,686 filas (4.2%) · 1.39% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 51 | 100% | OTTera.tv 39.7%, TCL ADs (APAC) 39.0%, Select Plus 6.3%, PML Digital 5.0% |
| pageURL | 56 | 100% | com.tcl.livetv 38.4%, com.tcl.movieark 24.9%, com.tcl.waterfall 19.6%, +com.tcl.livetv 4.6% |
| App Name | 41 | 93.9% | Live TV 37.5%, MovieArk 24.9%, TCL CHANNEL 19.6% |
| contentGenre | 1,254 | 99.1% | drama 9.7%, other 7.2%, documentary 5.9%, horror 3.7% |
| contentLanguage | 25 | **98.3%** | en 64.9%, es 27.4%, pt 1.6%, c 1.2% |
| contentRating | 83 | 87.6% | tv-ma 12.5%, *N/A 12.4%*, r 11.9%, tv-14 10.8%, tv-pg 10.5% |
| contentCategory | 92 | 20.6% | *[-7] 79.4%*, [IAB1] 8.8%, [sports] 5.0% |
| contentIsLiveStream | 3 | 30.8% | *Unknown 40.7%*, 1 30.8%, *N/A 28.5%* |
| contentLength | 9 | 6.8% | *N/A 93.2%*, 4 2.1%, 5 1.9%, 8 1.5% |
| contentSeries | 336 | 3.2% | *N/A 96.7%*, VOD 0.5%, OTT Studios Sports 0.1%, J1 League 0.1% |
| contentTitle | 3,973 | 97.4% | *N/A 2.6%*, la mujer del anarquista 0.2%, catalunya über alles! 0.2% |
| contentIsTitlePresent | 2 | — | true 97.4%, false 2.6% |

**Conclusiones — Ecuador:**
- Duopolio OTTera + TCL (78.7% de filas entre ambos) con solo 51 publishers — mercado poco profundo.
- La monetización es rara pero buena: 93.9% de filas con eCPM cero (de las peores tasas), pero lo que paga, paga bien (ponderado 7.54). Pocas campañas activas con buen precio.
- Curiosamente tiene el mejor fill de idioma del dataset (98.3%) — casi todo su inventario pasa por integraciones que sí normalizan idioma. El bundle malformado `+com.tcl.livetv` está concentrado aquí (4.6% de sus filas).

## Costa Rica — 16,674 filas (3.3%) · 1.31% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 69 | 100% | OTTera.tv 38.4%, TCL ADS-Springserve 33.3%, Select Plus 9.6%, Aluna 4.2% |
| pageURL | 83 | 100% | com.tcl.movieark 35.8%, com.tcl.waterfall 25.4%, com.tcl.browser 16.8%, com.tcl.livetv 7.6% |
| App Name | 70 | 98.5% | MovieArk 35.8%, TCL CHANNEL 25.4%, BrowseHere 16.8%, Live TV 7.6%, Coolita 6.8% |
| contentGenre | 1,157 | 98.9% | drama 9.4%, other 6.8%, documentary 5.7%, horror 3.9% |
| contentLanguage | 32 | 96.5% | en 71.7%, es 18.4%, pt 2.8% |
| contentRating | 66 | 87.4% | tv-ma 12.9%, *N/A 12.6%*, r 11.7%, tv-14 11.0%, g 8.9% |
| contentCategory | 100 | 25.8% | *[-7] 74.2%*, [IAB1-22] 8.1%, [IAB1] 7.5%, [IAB17] 1.6% |
| contentIsLiveStream | 3 | 41.5% | 1 41.5%, *Unknown 38.3%*, *N/A 20.2%* |
| contentLength | 9 | 11.2% | *N/A 88.8%*, 4 4.4%, 5 3.1%, 6 1.5% |
| contentSeries | 352 | 7.5% | *N/A 92.4%*, VOD 0.4%, OTT Studios Sports 0.1%, The Cube USA 0.1% |
| contentTitle | 3,066 | 95.7% | *N/A 4.3%*, catalunya über alles! 0.2%, eve 0.2% |
| contentIsTitlePresent | 2 | — | true 95.7%, false 4.3% |

**Conclusiones — Costa Rica:**
- **El mercado con mejor tasa de monetización del dataset**: solo 61.9% de filas con eCPM cero (vs 82.6% global). Casi 4 de cada 10 combinaciones generan revenue — hay demanda activa comprando Costa Rica de forma amplia.
- 41.5% de filas confirmadas live (el doble del promedio): fuerte peso de canales lineales/FAST.
- Muy anglófono (71.7% en) y con el mismo catálogo OEM internacional del resto de Centroamérica.

## República Dominicana — 18,986 filas (3.7%) · 1.23% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 52 | 100% | OTTera.tv 34.3%, TCL ADS-Springserve 28.6%, TCL ADs (APAC) 22.2%, Select Plus 7.9% |
| pageURL | 81 | 100% | com.tcl.waterfall 35.3%, com.tcl.movieark 31.9%, com.tcl.browser 23.0%, com.tcl.livetv 3.0% |
| App Name | 56 | 99.0% | TCL CHANNEL 35.3%, MovieArk 31.9%, BrowseHere 23.0%, Live TV 2.9%, Coolita 2.6% |
| contentGenre | 1,134 | 99.3% | drama 7.8%, other 6.9%, documentary 6.5%, horror 3.8% |
| contentLanguage | 27 | 98.4% | en 77.7%, es 15.4%, pt 1.8% |
| contentRating | 71 | 90.2% | g 14.0%, r 13.1%, tv-14 10.9%, tv-ma 10.5%, *N/A 9.8%* |
| contentCategory | 94 | 15.9% | *[-7] 84.1%*, [IAB1-22] 8.2%, [IAB1] 1.5%, [IAB1-7] 0.7% |
| contentIsLiveStream | 3 | 47.4% | 1 47.4%, *N/A 26.7%*, *Unknown 25.9%* |
| contentLength | 9 | 5.5% | *N/A 94.5%*, 5 1.9%, 4 1.7%, 6 1.2% |
| contentSeries | 341 | 3.5% | *N/A 96.5%*, VOD 0.2%, Run Of Video Network 0.1%, WDBJ News 0.1% |
| contentTitle | 3,022 | 96.9% | *N/A 3.1%*, catalunya über alles! 0.2%, humble pie 0.2% |
| contentIsTitlePresent | 2 | — | true 96.9%, false 3.1% |

**Conclusiones — República Dominicana:**
- El inventario más anglófono del grupo hispano (77.7% en / 15.4% es) y con la mayor proporción de live confirmado tras Paraguay (47.4%): perfil de canales lineales internacionales sobre TVs TCL.
- TCL (tres apps) + OTTera = ~90% de las filas; casi sin supply local.
- Monetización floja: 91.6% de ceros, aunque el precio cuando paga es decente (5.45 ponderado). Buen fill de rating (90.2%) con `g` como valor top — mucho contenido familiar.

## Venezuela — 8,891 filas (1.7%) · 0.63% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 51 | 100% | OTTera.tv 45.8%, Select Plus 28.1%, Coocaa 6.5%, Xapads 5.2% |
| pageURL | 65 | 100% | com.tcl.movieark 55.0%, com.tcl.browser 16.5%, com.coolita.channel 11.7% |
| App Name | 48 | 97.7% | MovieArk 55.0%, BrowseHere 16.5%, Coolita 11.7%, TCL CHANNEL 3.8% |
| contentGenre | 967 | 99.2% | drama 10.2%, documentary 6.9%, other 5.5%, horror 4.5% |
| contentLanguage | 24 | 95.8% | en 70.1%, es 18.7%, pt 4.0% |
| contentRating | 62 | 70.8% | *N/A 29.2%*, tv-pg 12.0%, tv-14 9.3%, tv-ma 8.4% |
| contentCategory | 90 | 42.0% | *[-7] 58.0%*, [IAB1-22] 15.1%, [IAB1] 4.9%, [640] 2.4% |
| contentIsLiveStream | 3 | 45.6% | *Unknown 51.4%*, 1 45.6%, *N/A 3.0%* |
| contentLength | 8 | 21.5% | *N/A 78.5%*, 5 7.5%, 4 6.8%, 6 5.2% |
| contentSeries | 339 | 12.0% | *N/A 88.0%*, OTT Studios Ent. On Demand 0.5%, The Cube USA 0.2% |
| contentTitle | 2,786 | 90.0% | *N/A 10.0%*, the baddest bad boy 0.2%, haus of horror 0.2% |
| contentIsTitlePresent | 2 | — | true 90.0%, false 10.0% |

**Conclusiones — Venezuela:**
- **El 100% de sus 8,891 filas tiene eCPM = 0: ni una sola combinación venezolana registró revenue en el periodo.** Consecuencia esperable de que la demanda programática internacional excluye el país (sanciones/riesgo cambiario). El inventario existe (2,699 millones de requests) pero nadie lo compra.
- Irónicamente su metadata es mejor que la media (category 42.0%, length 21.5%, series 12%): la calidad de señal no es el problema.
- Su supply está desplazado a MovieArk (55.0%) y Coolita — el perfil OEM puro, sin broadcasters.

## Panamá — 10,316 filas (2.0%) · 0.58% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 62 | 100% | OTTera.tv 42.4%, TCL ADS-Springserve 33.4%, Select Plus 13.1%, Vidaa 1.6% |
| pageURL | 74 | 100% | com.tcl.movieark 43.9%, com.tcl.browser 20.0%, com.tcl.livetv 13.8%, com.tcl.waterfall 12.0% |
| App Name | 60 | 96.4% | MovieArk 43.9%, BrowseHere 20.0%, Live TV 13.8%, TCL CHANNEL 12.0% |
| contentGenre | 913 | 98.1% | drama 11.3%, other 7.1%, documentary 5.6%, horror 4.7% |
| contentLanguage | 24 | 97.0% | en 77.8%, es 13.9%, pt 1.3% |
| contentRating | 60 | 84.6% | *N/A 15.4%*, tv-ma 13.1%, tv-14 12.1%, r 12.0%, tv-pg 10.2% |
| contentCategory | 55 | 26.6% | *[-7] 73.4%*, [IAB1] 11.0%, [IAB1-22] 9.6%, [IAB12] 1.4% |
| contentIsLiveStream | 3 | 29.8% | *Unknown 54.0%*, 1 29.8%, *N/A 16.2%* |
| contentLength | 9 | 4.1% | *N/A 95.9%*, 8 1.3%, 4 1.2% |
| contentSeries | 31 | 2.0% | *N/A 98.0%*, VOD 0.6%, OTT Studios Sports 0.3% |
| contentTitle | 2,443 | 95.8% | *N/A 4.2%*, catalunya über alles! 0.3%, the baddest bad boy 0.3% |
| contentIsTitlePresent | 2 | — | true 95.8%, false 4.1% |

**Conclusiones — Panamá:**
- Mercado calcado a Costa Rica en estructura (OTTera + TCL Springserve + Select Plus, catálogo en inglés 77.8%) pero con mucha peor tasa de monetización (89.0% ceros) y precio menor (4.27 ponderado).
- Solo 31 valores de series y fill de 2.0% (el más pobre junto a Paraguay): inventario de canal/película, no de series. Aparece TelevisaUnivision con presencia marginal (1.5%).

## Puerto Rico — 7,046 filas (1.4%) · 0.43% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 109 | 100% | **Roku - oRTB 38.1%**, OTTera.tv 17.9%, Seedtag 5.2%, Plex 4.6%, Scripps-FreeWheel 4.4% |
| Publisher ID | 111 | 100% | (109 sellers en un mercado de 7K filas — profundidad inusual) |
| pageURL | 206 | 100% | **151908 (Roku Channel) 48.1%**, com.tcl.movieark 13.1%, com.tcl.browser 6.9%, 13535 (Plex) 3.4% |
| App Name | 146 | 96.3% | The Roku Channel 48.1%, MovieArk 13.1%, BrowseHere 6.9%, Plex 3.4% |
| contentGenre | 1,532 | 94.2% | drama 8.1%, entertainment 7.4%, *N/A 5.7%*, crime 3.2%, news 2.5% |
| contentLanguage | 26 | 89.0% | en 70.0%, es 16.8%, *N/A 11.0%* |
| contentRating | 57 | 91.2% | tv-14 18.7%, tvpg 14.7%, tv14 13.0%, *N/A 8.7%*, r 8.0% |
| contentCategory | 286 | **64.4%** | *[-7] 35.6%*, [IAB1-5, IAB1-7] 9.6%, [IAB1-7] 8.8%, [IAB1] 8.7%, [IAB1-22] 6.2% |
| contentIsLiveStream | 3 | 39.6% | *Unknown 51.4%*, 1 39.6%, *N/A 9.0%* |
| contentLength | 9 | **65.2%** | *N/A 34.8%*, 5 30.6%, 6 17.1%, 4 9.6%, 7 4.2% |
| contentSeries | 465 | 24.0% | *N/A 48.9%*, **md5-vacío 27.1%**, Chicago Fire 1.9%, NCIS 1.3%, FBI 1.2% |
| contentTitle | 1,257 | **55.2%** | *N/A 44.8%*, roku 10.1%, epg 9.2%, run of video network 0.8%, local news 0.6% |
| contentIsTitlePresent | 2 | — | true 55.2%, false 44.8% |

**Conclusiones — Puerto Rico:**
- **Es un mercado estadounidense dentro del dataset LATAM**: domina Roku (38.1% del supply, The Roku Channel 48.1% de filas), aparecen sellers US (Scripps, Plex, FreeWheel) y las series top son procedurales de networks US (Chicago Fire, NCIS, FBI). 109 publishers para 7K filas — la mayor profundidad de supply relativa.
- Tiene la **mejor metadata estructural** por mucho: category 64.4%, length 65.2%, series 24.0%. Pero con las trampas de Roku: el 27.1% de "series" es el hash MD5 vacío, y los títulos se ocultan tras `roku`/`epg` — solo 55.2% de fill de título, el peor del dataset.
- El mejor eCPM medio (8.59) y ponderado alto (8.14): precio de mercado US. Para campañas hispanas en EEUU este es probablemente el inventario más interesante del archivo, con la salvedad del título oculto.
- Sus ratings vienen con las variantes sucias (`tvpg`, `tv14` sin guión): el fix de normalización de ratings es principalmente para este supply.

## Uruguay — 5,017 filas (1.0%) · 0.40% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 42 | 100% | **OTTera.tv 69.2%**, Coocaa 11.4%, Pluto LATAM 3.8%, METAX 3.7% |
| pageURL | 43 | 100% | com.tcl.movieark 47.3%, com.tcl.livetv 22.5%, com.coolita.channel 11.4%, tv.pluto.android 3.6% |
| App Name | 35 | 96.8% | MovieArk 47.3%, Live TV 22.5%, Coolita 11.4%, PlutoTV 3.6% |
| contentGenre | 920 | 98.3% | drama 7.3%, documentary 5.9%, other 5.2%, horror 3.3% |
| contentLanguage | 24 | 98.3% | en 72.0%, es 19.2%, pt 3.7% |
| contentRating | 57 | 94.2% | **tv-pg 21.0%**, tv-ma 12.5%, tv-14 10.9%, r 10.3% |
| contentCategory | 89 | 45.9% | *[-7] 54.1%*, [IAB1] 22.0%, [IAB17] 3.1%, [sports] 2.7% |
| contentIsLiveStream | 3 | 25.1% | *Unknown 69.9%*, 1 25.1% |
| contentLength | 9 | 18.8% | *N/A 81.2%*, 4 6.6%, 5 6.0%, 6 3.8% |
| contentSeries | 323 | 11.4% | *N/A 88.5%*, VOD 0.5%, The Cube USA 0.2%, J1 League 0.2% |
| contentTitle | 2,800 | 92.6% | *N/A 7.4%*, soul storm 0.3%, red bull tv 0.3% |
| contentIsTitlePresent | 2 | — | true 92.6%, false 7.4% |

**Conclusiones — Uruguay:**
- La mayor dependencia de un solo seller del dataset: OTTera concentra el 69.2% de las filas. Riesgo de supply path único.
- 97.4% de filas sin revenue (solo Venezuela y Bolivia están peor): la demanda casi no compra Uruguay pese a precio razonable cuando paga (5.44 ponderado).
- Es el único país cuyo rating top es tv-pg (contenido familiar) y con Pluto TV en el top de apps.

## Honduras — 10,681 filas (2.1%) · 0.23% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 50 | 100% | TCL ADS-Springserve 41.9%, OTTera.tv 37.5%, Select Plus 11.0% |
| pageURL | 74 | 100% | com.tcl.movieark 33.0%, com.tcl.browser 20.1%, com.tcl.livetv 20.0%, com.tcl.waterfall 18.1% |
| App Name | 63 | 96.9% | MovieArk 33.0%, BrowseHere 20.1%, Live TV 20.0%, TCL CHANNEL 18.1% |
| contentGenre | 600 | 97.9% | drama 12.2%, other 7.0%, horror 5.6%, documentary 4.1% |
| contentLanguage | 23 | 95.6% | en 75.4%, es 14.3%, pt 1.6% |
| contentRating | 45 | 86.6% | tv-ma 17.8%, *N/A 13.4%*, r 12.9%, tv-14 12.7% |
| contentCategory | 45 | 26.2% | *[-7] 73.8%*, [IAB1] 10.8%, [IAB1-22] 9.3%, [IAB12] 1.1% |
| contentIsLiveStream | 3 | 32.7% | *Unknown 44.1%*, 1 32.7%, *N/A 23.1%* |
| contentLength | 7 | **3.4%** | *N/A 96.6%*, 4 1.4%, 6 1.1% |
| contentSeries | 58 | 2.8% | *N/A 97.2%*, VOD 0.5%, OTT Studios Ent. On Demand 0.5% |
| contentTitle | 1,325 | 97.7% | *N/A 2.3%*, catalunya über alles! 0.3%, the baddest bad boy 0.3% |
| contentIsTitlePresent | 2 | — | true 97.7%, false 2.3% |

**Conclusiones — Honduras:** único país donde TCL-Springserve es el líder individual (41.9%). eCPM bajo (3.99 ponderado) pero con tasa de monetización mejor que la media (78.7% ceros). El fill de length más bajo del dataset (3.4%) y el mejor fill de título (97.7%). Metadata y catálogo idénticos al patrón centroamericano.

## Guatemala — 7,093 filas (1.4%) · 0.23% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 56 | 100% | OTTera.tv 63.4%, TCL ADs (APAC) 13.5%, Televisa Univision via Springserve 5.0%, Vidaa 4.1% |
| pageURL | 66 | 100% | com.tcl.livetv 34.6%, com.tcl.movieark 18.1%, com.tcl.browser 15.4%, com.tcl.waterfall 13.7% |
| App Name | 53 | 91.6% | Live TV 34.6%, MovieArk 18.1%, BrowseHere 15.4%, TCL CHANNEL 13.7% |
| contentGenre | 640 | 99.0% | drama 13.5%, other 6.5%, comedy 4.5%, horror 4.2% |
| contentLanguage | 23 | 96.5% | en 71.1%, es 20.1%, pt 1.2% |
| contentRating | 52 | **96.1%** | tv-ma 18.5%, tv-14 18.1%, r 13.3%, tv-pg 8.2% |
| contentCategory | 50 | 49.3% | *[-7] 50.7%*, [IAB1] 22.4%, [IAB1-22] 14.0%, [IAB12] 3.1% |
| contentIsLiveStream | 3 | 22.5% | *Unknown 67.6%*, 1 22.5%, *N/A 9.9%* |
| contentLength | 7 | 8.9% | *N/A 91.1%*, 8 4.1%, 4 2.0% |
| contentSeries | 55 | 4.3% | *N/A 95.7%*, VOD 1.1%, OTT Studios Ent. On Demand 0.5% |
| contentTitle | 1,695 | 95.6% | *N/A 4.4%*, catalunya über alles! 0.3%, la mujer del anarquista 0.3% |
| contentIsTitlePresent | 2 | — | true 95.6%, false 4.4% |

**Conclusiones — Guatemala:** el mejor fill de rating del dataset (96.1%) y buen fill de categoría (49.3%): su mix OTTera+Televisa manda señales completas. Única presencia relevante de TelevisaUnivision fuera de México (5.0% del supply local). Tasa de monetización buena (77.4% ceros, mejor que la media) aunque a precio moderado (4.63 ponderado).

## El Salvador — 7,639 filas (1.5%) · 0.22% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 47 | 100% | OTTera.tv 61.7%, TCL ADs (APAC) 15.2%, Select Plus 13.9% |
| pageURL | 47 | 100% | com.tcl.livetv 36.5%, com.tcl.movieark 26.4%, com.tcl.browser 16.3%, com.tcl.waterfall 13.5% |
| App Name | 40 | 97.5% | Live TV 36.5%, MovieArk 26.4%, BrowseHere 16.3%, TCL CHANNEL 13.5% |
| contentGenre | 720 | 98.6% | drama 12.2%, other 7.5%, horror 5.8%, documentary 4.5% |
| contentLanguage | 24 | 97.5% | en 76.9%, es 14.7%, pt 1.4% |
| contentRating | 46 | 85.8% | tv-ma 16.3%, *N/A 14.2%*, r 13.0%, tv-14 12.7% |
| contentCategory | 44 | 42.0% | *[-7] 58.0%*, [IAB1] 21.3%, [IAB1-22] 14.9%, [sports] 1.9% |
| contentIsLiveStream | 3 | 30.3% | *Unknown 63.7%*, 1 30.3%, *N/A 6.0%* |
| contentLength | 7 | 3.8% | *N/A 96.2%*, 4 1.6%, 6 1.1% |
| contentSeries | 25 | 2.1% | *N/A 97.8%*, VOD 0.7%, OTT Studios Ent. On Demand 0.5% |
| contentTitle | 1,692 | 97.0% | *N/A 3.0%*, catalunya über alles! 0.3%, haus of horror 0.3% |
| contentIsTitlePresent | 2 | — | true 97.0%, false 3.0% |

**Conclusiones — El Salvador:** perfil centroamericano estándar (OTTera dominante con 61.7%, catálogo en inglés 76.9%, metadata de categoría decente 42.0% por la vía OTTera). Precio bueno para la región (6.43 ponderado, el mejor de Centroamérica). Sin nada local en el top.

## Paraguay — 1,807 filas (0.4%) · 0.09% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 38 | 100% | **Select Plus 53.4%**, TCL ADs (APAC) 15.3%, METAX 11.2%, iion 5.6% |
| pageURL | 34 | 100% | com.tcl.movieark 54.0%, com.tcl.browser 16.2%, com.seraphic.metaxplay 8.5%, tv.vidaa.ui.plus 5.8% |
| App Name | 24 | 92.3% | MovieArk 54.0%, BrowseHere 16.2%, Metax TV 8.5% |
| contentGenre | 207 | 92.7% | **drama 20.2%**, horror 8.1%, action 5.4%, documentary 5.1% |
| contentLanguage | 21 | 92.0% | en 70.7%, es 15.1%, pt 2.1% |
| contentRating | 33 | **38.0%** | *N/A 62.0%*, tv-g 8.3%, tv-14 7.0%, tv-ma 5.9% |
| contentCategory | 46 | 21.2% | *[-7] 78.8%*, [IAB12] 3.2%, [IAB1, IAB1-5] 2.8%, [IAB1] 2.7% |
| contentIsLiveStream | 3 | **69.3%** | 1 69.3%, *N/A 23.2%*, *Unknown 7.5%* |
| contentLength | 6 | 4.9% | *N/A 95.1%*, 5 1.8%, 6 1.7%, 1 0.9% |
| contentSeries | 9 | 2.0% | *N/A 98.0%*, VOD 0.9%, Hell on Wheels 0.2% |
| contentTitle | 1,122 | 93.7% | *N/A 6.3%*, soul storm 0.7%, humble pie 0.5%, kung fu 0.4% |
| contentIsTitlePresent | 2 | — | true 93.7%, false 6.3% |

**Conclusiones — Paraguay:** muestra chica (1,807 filas) con dos récords: el **peor fill de rating** (38.0% — casi dos tercios sin clasificación, problema para brand safety) y el **mayor porcentaje de live confirmado** (69.3%). Select Plus es el único líder de mercado que no aparece primero en ningún otro país. Solo 9 valores de series. Leer con cautela por el tamaño.

## Bolivia — 1,162 filas (0.2%) · 0.04% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 33 | 100% | **Coocaa (SKYWORTH) 41.2%**, OTTera.tv 14.8%, METAX 10.4%, iion 8.1% |
| pageURL | 34 | 100% | com.coolita.channel 41.2%, com.tcl.browser 13.1%, com.seraphic.metaxplay 6.9%, 300620 (Roku) 6.5% |
| App Name | 25 | 94.9% | Coolita Channel 41.2%, BrowseHere 13.1%, Metax TV 6.9%, MovieArk 5.8% |
| contentGenre | 265 | 89.2% | *N/A 10.8%*, drama 7.3%, **animation,family,sport 6.7%**, sports 4.0%, comedy 4.0% |
| contentLanguage | 13 | 88.3% | en 58.3%, es 13.8%, **pt 12.7%** |
| contentRating | 35 | 82.2% | *N/A 17.8%*, tv-14 15.6%, tv-pg 12.9%, g 11.7% |
| contentCategory | 68 | **79.1%** | *[-7] 20.9%*, [IAB1-22] 10.9%, [IAB1] 9.5%, [IAB17] 9.3%, [IAB1-7, IAB17-12] 6.7% |
| contentIsLiveStream | 3 | 59.0% | 1 59.0%, *Unknown 26.1%*, *N/A 14.9%* |
| contentLength | 8 | 49.6% | *N/A 50.4%*, 4 20.3%, 5 16.0%, 6 7.6% |
| contentSeries | 309 | **38.5%** | *N/A 61.4%*, The Cube USA 0.9%, J1 League 0.9%, Podpah 0.7% |
| contentTitle | 672 | 87.3% | *N/A 12.7%*, pacman 0.5%, pixel_dash 0.5%, sponge_bob_bounce 0.5% |
| contentIsTitlePresent | 2 | — | true 87.3%, false 12.7% |

**Conclusiones — Bolivia:**
- La muestra más chica (1,162 filas) y un perfil totalmente distinto: domina **Coocaa/Coolita** (Skyworth), no TCL. Y con la **mejor metadata del dataset** (category 79.1%, length 49.6%, series 38.5%): las apps de Skyworth mandan el content object completo.
- Pero no sirve de nada: **99.8% de filas con eCPM cero** (un par de combinaciones monetizaron, ponderado 1.99). Metadata casi perfecta sin demanda.
- Rarezas: títulos que son **juegos casuales** (pacman, sponge_bob_bounce — la app "Free Games by PlayWorks" clasificada como CTV), el género combinado `animation,family,sport`, y más portugués (12.7%) que casi cualquier país hispano por catálogo brasileño (Podpah).

## Nicaragua — 1,470 filas (0.3%) · 0.03% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 42 | 100% | Coocaa 26.9%, TCL ADs (APAC) 18.6%, OTTera.tv 12.2%, METAX 6.9% |
| pageURL | 47 | 100% | com.coolita.channel 26.9%, com.tcl.livetv 17.2%, com.tcl.movieark 10.8% |
| App Name | 43 | 88.9% | Coolita 26.9%, Live TV 17.2%, *N/A 11.1%*, MovieArk 10.8% |
| contentGenre | 274 | 93.5% | drama 10.5%, sports 4.9%, animation,family,sport 4.9%, news 3.9% |
| contentLanguage | 13 | 92.5% | en 61.0%, es 16.7%, pt 9.5% |
| contentRating | 38 | 90.1% | tv-14 21.3%, tv-ma 12.9%, g 9.9%, tv-pg 8.9% |
| contentCategory | 67 | 56.9% | *[-7] 43.1%*, [IAB12] 7.3%, [sports] 6.7%, [IAB17] 5.7% |
| contentIsLiveStream | 3 | 42.6% | 1 42.6%, *Unknown 35.2%*, *N/A 22.1%* |
| contentLength | 7 | 36.9% | *N/A 63.1%*, 4 13.9%, 5 12.1%, 6 6.9% |
| contentSeries | 261 | 31.2% | *N/A 68.8%*, OTT Studios Ent. On Demand 2.0%, OTT Studios Sports 1.4% |
| contentTitle | 662 | 91.6% | *N/A 8.4%*, catalunya über alles! 1.1%, humble pie 0.9% |
| contentIsTitlePresent | 2 | — | true 91.6%, false 8.4% |

**Conclusiones — Nicaragua:** el mercado más chico en tráfico (0.03%) pero con señales sorprendentemente buenas: segunda mejor metadata (category 56.9%, series 31.2% — otra vez el efecto Coocaa/Coolita) y la segunda mejor tasa de monetización (68.4% ceros) con precio alto cuando paga (7.80 ponderado, aunque sobre poquísimas filas). Mismo perfil que Bolivia: OEM Skyworth + catálogo mixto con portugués.

---

# Síntesis transversal

1. **La metadata depende del publisher, no del país.** Los fills por país se explican casi por completo por el mix de sellers: donde domina TCL (Argentina, Chile) la categoría y la duración desaparecen; donde pesa Roku (Puerto Rico, México en volumen) aparecen categoría/duración pero se ocultan títulos y series; donde pesa Coocaa/Coolita (Bolivia, Nicaragua) el content object llega casi completo. Las correcciones hay que negociarlas con 4-5 integraciones, no con 18 países.
2. **Calidad de señal y monetización no van de la mano por país.** Venezuela y Bolivia tienen metadata sobre la media y monetización nula (ahí el bloqueo es de demanda); Chile tiene metadata pobre y el mejor precio. La correlación metadata→eCPM que sí existe a nivel de fila (sección 16 de la parte 1: idioma +37%, género +16%) opera dentro de cada mercado, no entre mercados.
3. **El catálogo de relleno es el mismo en todos lados**: las películas B de OTT Studios ("catalunya über alles!", "haus of horror", "the baddest bad boy" y sus trailers) aparecen en el top de títulos de 15 de los 18 países. La "variedad" aparente del dataset es en gran parte un único catálogo replicado.
4. **Prioridades de limpieza con mayor retorno:** (a) normalizar ratings (~180 valores → 5 niveles; desbloquea brand safety en el 88% del tráfico); (b) reclamar el fix de `content.cat` = `[-7]` al ecosistema TCL/OEM (recuperaría categoría en ~70% del tráfico); (c) mapear bundles→servicio para consolidar ViX/Tubi/Plex; (d) confirmar la tabla de buckets de contentLength con el proveedor del reporte antes de usarla; (e) auditar el eCPM máximo de 200.0, que huele a valor de prueba.

