# Reporte detallado — Content Objects, inventario CTV LATAM (v10)

**Archivo:** `inventory-source-alcance-ctv-v10-latam-content-objetcs.csv` — 512,000 filas, 16 columnas, 422,968,016,640 requests totales.
**Data completa en:** `reporte-content-objects-detallado.json` (distribuciones completas por columna y por país).
**Referencia de campos content\*:** [OpenRTB 2.6 — Object: Content](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent)

**Cómo leer este reporte:**
- Cada fila del CSV es una **combinación agregada** (publisher + app + país + señales de contenido), no un evento individual. Por eso todos los análisis se dan en dos vistas: **% de filas** (variedad del inventario) y **% de requests** (volumen real de tráfico). Cuando difieren mucho, significa que pocas combinaciones concentran mucho tráfico.
- Llamamos **centinelas** a los valores que ocupan la celda pero no aportan dato: `Not Available`, `Not Applicable`, `Unknown`, `N/A`, `none`, `undefined`. El **fill rate** los excluye, junto con basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).
- La distinción entre centinelas no es aleatoria: `Not Applicable` y `Unknown` suelen venir de la capa de normalización del vendor (el SSP no mandó el campo o mandó algo no interpretable), mientras `Not Available` indica que el campo no llegó en el bid request. En la práctica todos significan "sin dato".

---

# PARTE 1 — Análisis por columna (las 16)

## 1. Publisher ID

**Glosario.** Identificador numérico interno de la cuenta del publisher/seller dentro de la plataforma (el "seat" del vendedor en el exchange). No es un campo OpenRTB del bid request; es metadato de la plataforma que generó el reporte. Un ID = una cuenta comercial.

**Datos.** 235 valores distintos, 0 vacíos (100% fill). Distribución (top):

| Publisher ID | Publisher al que corresponde | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| 161101 | OTTera.tv | 120,978 | 23.63% | 21.95% |
| 161489 | TCL ADs (APAC) | 68,963 | 13.47% | 9.10% |
| 164918 | iion Pty Ltd | 65,560 | 12.80% | 10.83% |
| 161517 | Select Plus PTE LTD (CTV) | 40,892 | 7.99% | 4.60% |
| 166799 | iion Pty Ltd (2ª cuenta) | 40,846 | 7.98% | 3.99% |
| 163091 | TCL ADS - Springserve | 35,676 | 6.97% | 3.25% |
| 160222 | PML Digital | 14,276 | 2.79% | 0.75% |
| 161212 | METAX SOFTWARE PTE. LTD. (Exchange) | 12,752 | 2.49% | 0.51% |
| 154037 | Equativ - oRTB CTV | 12,234 | 2.39% | 3.19% |
| 165045 | Roku - oRTB | 8,468 | 1.65% | **14.48%** |
| 160710 | Televisa Univision via SpringServe | 8,001 | 1.56% | 4.59% |
| 166449 | Coocaa (SKYWORTH) | 6,491 | 1.27% | 4.30% |
| 166869 | TV Azteca - Springserve | 2,022 | 0.39% | **5.86%** |
| ...otros 222 IDs | | 174,841 | 34.15% | 22.60% |

**Conclusiones.**
- Hay **235 IDs para 229 nombres de publisher**: ningún ID apunta a dos nombres (la relación es limpia), pero algunos publishers operan con varias cuentas (p. ej. iion con 164918 y 166799). Para agrupar "quién vende", usar el nombre; para reconciliar facturación, el ID.
- La asimetría filas/requests es el dato clave: **Roku con 1.65% de las filas mueve 14.5% de los requests**, y TV Azteca con 0.39% de filas mueve 5.9%. Al revés, TCL ADs (13.5% filas) solo aporta 9.1% del tráfico: mucho catálogo, menos volumen por combinación.

## 2. Publisher

**Glosario.** Nombre comercial del vendedor del inventario. Ojo: en CTV el "publisher" del reporte suele ser el **vendedor/integración**, no necesariamente el dueño del contenido — nombres como "Roku - oRTB", "TCL ADS - Springserve" o "Televisa Univision via OB" describen el **camino de suministro** (supply path): quién vende y por qué protocolo/ad server (oRTB = integración OpenRTB directa; SpringServe, FreeWheel, OB = el ad server intermediario).

**Datos.** 229 valores distintos, 100% fill. Top:

| Publisher | Filas | % filas | % requests |
|---|---:|---:|---:|
| OTTera.tv | 120,978 | 23.63% | 21.95% |
| iion Pty Ltd | 76,522 | 14.95% | 7.23% |
| TCL ADs (APAC) | 68,963 | 13.47% | 9.10% |
| TCL ADS - Springserve | 65,560 | 12.80% | 10.83% |
| Select Plus PTE LTD (CTV) | 40,892 | 7.99% | 4.60% |
| PML Digital | 14,278 | 2.79% | 0.75% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 12,752 | 2.49% | 0.51% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 12,234 | 2.39% | 3.19% |
| Roku - oRTB | 8,468 | 1.65% | 14.48% |
| Televisa Univision via SpringServe | 8,001 | 1.56% | 4.59% |
| Vidaa | 7,071 | 1.38% | 1.63% |
| Aluna Limited | 7,029 | 1.37% | 0.70% |
| Coocaa, a SKYWORTH company | 6,491 | 1.27% | 4.30% |
| OneFox - Tubi | 5,688 | 1.11% | 1.33% |
| Pluto LATAM via SpringServe | 4,450 | 0.87% | 0.18% |
| Kivi via Springserve | 4,284 | 0.84% | 0.22% |
| Televisa Univision via OB | 3,926 | 0.77% | 2.97% |
| TV Azteca - Springserve | 2,022 | 0.39% | 5.86% |
| ...otros 211 | ~53,000 | ~10.7% | ~8.3% |

**Conclusiones.**
- El suministro está **muy concentrado en fabricantes de TV (OEMs)**: OTTera + TCL (dos cuentas) + iion + Select Plus = **73% de las filas y ~54% de los requests**. TCL, Vidaa (Hisense), Coocaa (Skyworth), Kivi y Metax son todos ecosistemas de smart TV.
- Los **broadcasters locales** (TelevisaUnivision con dos rutas, TV Azteca) pesan poco en filas pero mucho en tráfico por combinación — inventario premium y más homogéneo.
- Un mismo dueño aparece por **varias rutas** (TelevisaUnivision via SpringServe y via OB; Tubi vende via OneFox pero su app también aparece dentro del inventario de otros sellers): para análisis de supply path conviene normalizar por dueño real.

## 3. pageURL

**Glosario.** En web, sería la URL de la página. En CTV este campo transporta el **identificador de la app** (`app.bundle` de OpenRTB), y su formato delata la tienda de apps de cada plataforma:
- `com.xxx.yyy` — package name estilo Android/Google TV (com.tcl.\*, com.tubitv, tv.pluto.android).
- **Numérico** (151908, 552828, 974696...) — ID del **Roku Channel Store** (151908 = The Roku Channel, 552828 = ViX en Roku).
- `bXXXXXXXXX` (b08kj77pqy) — **ASIN de Amazon** (Fire TV).
- `gXXXXXXXXXXX` (g15147002586 = Samsung TV Plus) — ID de app de **Samsung Tizen**.
- `roku`, `+com.tcl.livetv` — valores malformados (genérico de plataforma; un `+` pegado por error de concatenación).

**Datos.** 661 valores distintos, 100% fill. Top:

| pageURL (bundle) | App | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| com.tcl.movieark | MovieArk (TCL) | 147,807 | 28.87% | 29.47% |
| com.tcl.livetv | Live TV (TCL) | 125,367 | 24.49% | 12.44% |
| com.tcl.waterfall.overseas | TCL Channel | 74,119 | 14.48% | 8.57% |
| com.tcl.browser | BrowseHere (TCL) | 52,046 | 10.17% | 4.67% |
| com.coolita.channel | Coolita (Coocaa) | 9,881 | 1.93% | 4.99% |
| 974696 | canal Roku | 7,736 | 1.51% | 1.15% |
| 151908 | The Roku Channel | 6,821 | 1.33% | **11.89%** |
| tv.vidaa.ui.plus | Vidaa (Hisense) | 6,601 | 1.29% | 1.23% |
| +com.tcl.livetv | (malformado) | 6,133 | 1.20% | 0.21% |
| 552828 | ViX (Roku) | 5,658 | 1.11% | 4.59% |
| com.univision.prendetv | ViX/PrendeTV | 5,141 | 1.00% | 3.57% |
| com.tubitv | Tubi | 3,286 | 0.64% | **6.10%** |
| roku | (genérico) | 1,431 | 0.28% | 2.28% |
| ...otros ~630 | | ~60,000 | ~11.7% | ~9.1% |

**Conclusiones.**
- **Las 4 apps nativas de TCL suman el 78% de las filas pero solo el 55% de los requests** — el catálogo del dataset está sesgado a TCL; el tráfico real está más repartido.
- Hay ~7,500 filas (1.5%) con bundle malformado (`+com.tcl.livetv`, `roku`): romperían cualquier join con listas de apps o app-ads.txt. Conviene limpiar el `+` y descartar los genéricos.
- El mismo servicio aparece con **bundles distintos por plataforma** (ViX = 552828 en Roku + com.univision.prendetv en Android + tv.vidaa.ui.apps.vix en Hisense). Para medir alcance por servicio hay que mapear bundles → servicio.

## 4. App Name

**Glosario.** Nombre comercial de la app (`app.name` en OpenRTB), tal como lo declara el publisher o la tienda. Es texto libre y localizado, por eso una misma app aparece con múltiples variantes.

**Datos.** 386 valores distintos (385 útiles), fill 91.81% de filas / 93.22% de requests (el resto `Not Available`). Top:

| App Name | Filas | % filas | % requests |
|---|---:|---:|---:|
| MovieArk: Stream Movies & Live | 147,807 | 28.87% | 29.47% |
| Live TV | 115,241 | 22.51% | 12.11% |
| TCL CHANNEL | 74,119 | 14.48% | 8.57% |
| Browser TV Web - BrowseHere | 52,046 | 10.17% | 4.67% |
| *Not Available* | 41,910 | 8.19% | 6.78% |
| Coolita Channel | 9,881 | 1.93% | 4.99% |
| ViX: TV, Sports and News | 7,757 | 1.52% | 4.18% |
| The Roku Channel | 6,821 | 1.33% | 11.89% |
| ViX: TV, Deportes y Noticias | 5,658 | 1.11% | 4.59% |
| FreeTube- Search & Watch Free | 4,332 | 0.85% | 0.09% |
| ViX: Cine y TV Gratis en Español | 3,417 | 0.67% | 0.75% |
| Tubi: Free Movies & Live TV | 3,286 | 0.64% | 6.10% |
| Plex (2 variantes) | 6,080 | 1.19% | 0.20% |
| Tubi (otras 4 variantes) | ~5,300 | ~1.0% | ~1.4% |
| ...otros | | | |

**Conclusiones.**
- **ViX aparece con al menos 6 nombres** distintos (inglés, español, portugués, por plataforma) y Tubi con 5. Sumadas, ViX ronda el 4.5% de filas y ~10% de requests — mucho más de lo que aparenta cualquier variante suelta. **Nunca agrupar por App Name; usar pageURL/bundle** y un mapa bundle→servicio.
- "Live TV", "Browser TV Web", "Runtime" o "LG" son nombres genéricos que no identifican contenido — vienen del sistema operativo del TV, no de una app editorial.
- El 8.2% sin nombre coincide en gran parte con inventario agregado de exchanges (OTTera, Metax) donde la app original se pierde en la reventa.

## 5. Country

**Glosario.** País del dispositivo (geo de `device.geo.country`), normalizado a nombre en inglés.

**Datos.** 18 valores, 100% fill. Distribución completa:

| País | Filas | % filas | % requests |
|---|---:|---:|---:|
| Mexico | 146,426 | 28.60% | **61.77%** |
| Argentina | 96,040 | 18.76% | 16.78% |
| Chile | 57,727 | 11.27% | 5.85% |
| Colombia | 50,566 | 9.88% | 6.49% |
| Peru | 42,991 | 8.40% | 2.53% |
| Ecuador | 21,503 | 4.20% | 1.31% |
| Dominican Republic | 19,162 | 3.74% | 1.19% |
| Costa Rica | 16,794 | 3.28% | 1.28% |
| Panama | 10,132 | 1.98% | 0.54% |
| Honduras | 10,046 | 1.96% | 0.21% |
| Venezuela | 8,941 | 1.75% | 0.65% |
| El Salvador | 7,683 | 1.50% | 0.22% |
| Guatemala | 7,256 | 1.42% | 0.22% |
| Puerto Rico | 7,235 | 1.41% | 0.44% |
| Uruguay | 5,022 | 0.98% | 0.37% |
| Paraguay | 1,827 | 0.36% | 0.09% |
| Nicaragua | 1,513 | 0.30% | 0.03% |
| Bolivia | 1,136 | 0.22% | 0.04% |

**Conclusiones.**
- **México es el 62% del tráfico con solo el 29% de las filas**: sus combinaciones mueven en promedio 4x más requests que las del resto (ahí están Roku, TV Azteca y TelevisaUnivision con volúmenes enormes por fila).
- Argentina es el segundo mercado en ambas vistas. Chile, Colombia y Perú tienen mucha variedad de inventario (30% de filas juntas) pero solo 15% del tráfico.
- Los 7 países más chicos (PY, NI, BO, UY, PR, GT, SV) suman menos del 1.5% del tráfico: cualquier análisis por país ahí se basa en pocas combinaciones y hay que leerlo con cautela.

## 6. contentGenre

**Glosario.** `content.genre` de OpenRTB: "género que mejor describe el contenido". La spec lo define como **string libre** (no hay taxonomía obligatoria), y eso se nota: cada publisher manda su propio vocabulario, en minúsculas/mayúsculas distintas, a veces un solo género y a veces listas separadas por coma.

**Datos.** 7,658 valores distintos (7,655 útiles). Fill: 98.71% filas / 93.94% requests — **el campo content mejor poblado**. Top:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| drama | 50,815 | 9.92% | 10.80% |
| other | 29,826 | 5.83% | 3.07% |
| documentary | 26,454 | 5.17% | 2.84% |
| horror | 19,231 | 3.76% | 3.31% |
| comedy | 17,735 | 3.46% | 3.25% |
| drama,romance | 11,536 | 2.25% | 2.50% |
| action | 9,159 | 1.79% | 1.24% |
| thriller | 8,033 | 1.57% | 0.73% |
| music | 7,215 | 1.41% | 1.38% |
| sports | 6,578 | 1.28% | 1.82% |
| *Not Applicable* | 6,375 | 1.25% | 6.04% |
| news | 5,329 | 1.04% | 2.64% |
| horror,thriller | 4,837 | 0.94% | 1.01% |
| entertainment | 4,800 | 0.94% | **4.93%** |
| kids | 4,469 | 0.87% | 0.40% |
| romance | 4,217 | 0.82% | 0.90% |
| drama,comedy | 4,146 | 0.81% | 0.73% |
| movies | 3,942 | 0.77% | 0.42% |
| drama,thriller | 3,883 | 0.76% | 0.93% |
| crime / western / sci-fi / adventure / anime... | | <0.7% c/u | |
| ...otros 7,600+ valores | 251,220 | 49.07% | |

**Conclusiones.**
- La cardinalidad (7,658) no significa 7,658 géneros: son **combinaciones y variantes de ~30-40 géneros base**. `drama,romance` y `romance,drama` cuentan como valores distintos; hay hasta duplicados internos (`music,music`, 2,269 filas). Para usarlo hay que hacer split por coma + normalizar a minúsculas + deduplicar.
- El vocabulario mezcla niveles: géneros reales (drama, horror), **tipos de contenido** (movies, entertainment, news) y audiencias (kids). "other" (5.8%) y "Not Applicable" con 6% de requests indican que el volumen grande viene con género pobre.
- Aun así, es la mejor señal contextual disponible del dataset: tras normalizar quedaría una taxonomía de ~30 géneros con >90% de cobertura.

## 7. contentCategory

**Glosario.** `content.cat` de OpenRTB: array de categorías IAB del contenido. La taxonomía la define el campo `cattax` (que este reporte no incluye); si no se declara, aplica la **Content Category Taxonomy 1.0** (códigos "IABx-y", hoy deprecada). Glosario de los códigos que aparecen:
- `IAB1` Arts & Entertainment; `IAB1-4` Humor; `IAB1-5` Movies; `IAB1-6` Music; `IAB1-7` Television.
- `IAB9-30` Video & Computer Games; `IAB11` Law, Gov't & Politics; `IAB12` News; `IAB17` Sports (`IAB17-1` Auto Racing, `IAB17-12` Football); `IAB20` Travel.
- `IAB1-22` **no existe** en la taxonomía 1.0 (IAB1 solo llega a IAB1-7): es un código inválido que algún SSP inventó o mapeó mal.
- Valores solo numéricos (`[640]`, `[324]`, `[333, 647]`...) parecen IDs de las **Content Taxonomy 2.x/3.x** enviados sin declarar `cattax` — sin ese campo son ambiguos.
- `[sports]`, `[Live]` — texto libre fuera de toda taxonomía.
- `[-7]` — **no es una categoría de ninguna taxonomía**; es un placeholder/bug de normalización (probablemente un código de error interno que quedó serializado como categoría).

**Datos.** 478 valores distintos. Fill real: **21.98% filas / 29.99% requests**. Top:

| Valor | Significado | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| **[-7]** | inválido (placeholder) | **399,480** | **78.02%** | **70.01%** |
| [IAB1] | Arts & Entertainment | 32,443 | 6.34% | 5.77% |
| [IAB1-22] | inválido (no existe) | 18,799 | 3.67% | 1.51% |
| [IAB1-5] | Movies | 7,469 | 1.46% | 1.13% |
| [IAB12] | News | 6,060 | 1.18% | 1.24% |
| [IAB1, IAB1-5] | A&E + Movies | 4,826 | 0.94% | 0.31% |
| [IAB1-7] | Television | 4,635 | 0.91% | **6.17%** |
| [sports] | texto libre | 4,075 | 0.80% | 0.08% |
| [IAB1-5, IAB1-7] | Movies + TV | 3,827 | 0.75% | **4.03%** |
| [IAB17] | Sports | 3,741 | 0.73% | 1.07% |
| [640], [325], [647], [324]... | taxonomía 2.x sin declarar | ~7,500 | ~1.5% | ~0.2% |
| [IAB1-6] | Music | 1,423 | 0.28% | 0.55% |
| [IAB1-7, IAB17-12] | TV + Football | 1,321 | 0.26% | 0.77% |
| [IAB9-30] | Video Games | 1,295 | 0.25% | 0.19% |
| [Live] | texto libre | 1,068 | 0.21% | 0.09% |
| ...otros ~450 | | 10,392 | 2.03% | |

**Conclusiones.**
- Es **la columna más rota del dataset**: 78% de las filas traen el placeholder `[-7]`, y de lo restante una parte usa códigos inválidos (`IAB1-22`), taxonomías sin declarar (numéricos) o texto libre. La categoría IAB limpia y válida cubre apenas ~17% de filas.
- Lo poco válido está dominado por la rama IAB1 (entretenimiento), lo cual es coherente con CTV pero aporta poca granularidad para contextual/brand safety.
- Dato útil: las filas con `[IAB1-7]` y `[IAB1-5, IAB1-7]` (Roku, TelevisaUnivision) concentran 10% del tráfico — los players grandes sí categorizan; el placeholder viene masivamente del ecosistema TCL/OEM.

## 8. contentSeries

**Glosario.** `content.series` de OpenRTB: nombre de la serie a la que pertenece el contenido (ej. "The Office"). Valores especiales encontrados:
- `d41d8cd98f00b204e9800998ecf8427e` — **hash MD5 de la cadena vacía**. Viene del inventario de Roku, que ofusca el nombre de la serie con MD5 por privacidad; cuando la serie está vacía, el hash delata que no había valor. Es un "vacío disfrazado".
- `{{CONTENT_SERIES}}` — **macro de ad server sin reemplazar**: el publisher configuró la variable y nunca se sustituye.
- `VOD`, `No Series`, `Run Of Video Network`, `Research Unit` — placeholders operativos, no series reales.
- `OTT Studios Entertainment On Demand / Sports Livestream / Entertainment Livestream` — nombres de feeds/canales del proveedor OTT Studios, no series.

**Datos.** 1,841 valores distintos. Fill real: **5.52% filas / 6.94% requests — la columna con menos datos del dataset**. Distribución:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Not Available* | 479,394 | 93.63% | 81.93% |
| d41d8cd98f... (MD5 de vacío) | 4,287 | 0.84% | **11.10%** |
| VOD | 3,354 | 0.66% | 0.40% |
| OTT Studios Entertainment On Demand | 963 | 0.19% | 0.02% |
| {{CONTENT_SERIES}} | 614 | 0.12% | 0.23% |
| No Series | 525 | 0.10% | 0.01% |
| OTT Studios Sports Livestream | 512 | 0.10% | 0.05% |
| Doña Bárbara | 321 | 0.06% | 0.01% |
| series reales (Chicago Fire, MasterChef México, Doctor en Turno, J1 League, Podpah...) | ~18,000 | ~3.5% | ~2% |

**Conclusiones.**
- El 93.6% ni siquiera trae el campo, y de lo que llega "poblado", buena parte es placeholder. Las series con nombre real son ~3-4% de filas: telenovelas y TV mexicana (Doña Bárbara, MasterChef México), series US (Chicago Fire, NCIS — vía Puerto Rico/Roku), contenido brasileño (Podpah) y deportes (J1 League).
- El hash MD5 vacío pesa 11% de los requests porque va pegado al volumen gigante de Roku: **si se cuenta "series poblada" sin filtrar el hash, el fill rate por requests se infla de 6.9% a 18%** — trampa clásica en QA de metadata.
- Tal como está, la columna solo sirve para casos puntuales de content targeting en los pocos publishers que la mandan bien.

## 9. contentIsTitlePresent

**Glosario.** **No es un campo OpenRTB**: es una bandera derivada por la plataforma del reporte que indica si el bid request traía `content.title`. Booleano `true`/`false`.

**Datos.** 2 valores, 100% fill. Distribución completa:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| true | 468,751 | 91.55% | 75.44% |
| false | 43,249 | 8.45% | 24.56% |

**Conclusiones.**
- Consistencia interna perfecta: el 8.45% de `false` coincide exactamente con el 8.46% de `Not Applicable` en contentTitle — la bandera es fiable.
- El dato interesante está en la vista por requests: **una cuarta parte del tráfico viaja sin título**, aunque solo el 8% de las combinaciones. El título se pierde justo en las rutas de mayor volumen (México, Roku/EPG, exchanges agregadores).

## 10. contentLength

**Glosario.** `content.len` de OpenRTB: **duración del contenido en segundos**. Aquí NO viene en segundos: los únicos valores son los enteros 1 a 8. Contenido CTV de 1-8 segundos no existe, así que son **buckets de duración** (o un mapeo roto). La forma de la distribución (5 y 6 dominan, con 4 y 8 detrás) sugiere buckets tipo rangos de minutos, pero **el mapeo exacto no es deducible del archivo — hay que confirmarlo con la fuente antes de usar la columna**.

**Datos.** 9 valores distintos (8 útiles). Fill: 11.33% filas / **24.07% requests**. Distribución completa:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Not Applicable* | 453,996 | 88.67% | 75.93% |
| 6 | 16,548 | 3.23% | 5.10% |
| 5 | 15,315 | 2.99% | **7.72%** |
| 4 | 13,661 | 2.67% | 5.62% |
| 8 | 7,947 | 1.55% | 3.76% |
| 7 | 2,434 | 0.48% | 1.47% |
| 3 | 1,104 | 0.22% | 0.26% |
| 2 | 867 | 0.17% | 0.11% |
| 1 | 128 | 0.03% | 0.01% |

**Conclusiones.**
- El fill por requests (24%) duplica el fill por filas (11%): quien manda duración son los publishers de alto volumen (Roku sobre todo — en Puerto Rico, donde Roku domina, el fill llega a 65%).
- La distribución es unimodal centrada en 4-6: si los buckets son crecientes con la duración, el grueso del inventario declarado sería contenido de duración media (episodios/películas), con poco contenido corto (1-3).
- **No usar como duración numérica** en ningún cálculo hasta confirmar la tabla de buckets con el proveedor del reporte.

## 11. contentLanguage

**Glosario.** `content.language` de OpenRTB: idioma del contenido en **ISO-639-1 alpha-2** (dos letras: en, es, pt...). Valores fuera de norma encontrados: `spa`, `eng`, `por` (ISO-639-2 de tres letras, que la spec reserva para el campo `langb`), `sp` (no existe), `c` (basura, probablemente truncamiento), `504` (basura numérica). `ca` es catalán — real, y cuadra con títulos como "catalunya über alles".

**Datos.** 484 valores distintos (482 útiles). Fill: 79.85% filas / 86.85% requests. Top:

| Valor | Idioma | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| en | inglés | 247,778 | 48.39% | 40.00% |
| es | español | 136,657 | 26.69% | **42.38%** |
| *Not Applicable* | | 102,852 | 20.09% | 13.15% |
| pt | portugués | 6,297 | 1.23% | 1.97% |
| ru | ruso | 2,345 | 0.46% | 0.38% |
| hi | hindi | 1,956 | 0.38% | 0.66% |
| c | basura | 1,665 | 0.33% | 0.05% |
| spa | español (formato inválido) | 1,584 | 0.31% | 0.10% |
| de | alemán | 1,039 | 0.20% | 0.11% |
| eng | inglés (formato inválido) | 688 | 0.13% | 0.02% |
| fr / ja / it / he / fa / ko / ka / bn / hr / zh... | | <700 c/u | <0.15% c/u | |

**Conclusiones.**
- Paradoja llamativa para LATAM: **por filas domina el inglés (48% vs 27% español), pero por requests gana el español (42% vs 40%)**. El catálogo importado en inglés es enorme, pero la audiencia consume (y los publishers priorizan) contenido en español. El español sub-representa en variedad y sobre-representa en volumen.
- Sumando variantes (`es`+`spa`+`sp`), el español real ronda 27% de filas; conviene normalizar los códigos de 3 letras antes de segmentar.
- La cola de idiomas (ruso, hindi, alemán, persa, georgiano...) delata catálogos globales de relleno en apps OEM — inventario probablemente de baja afinidad para audiencias LATAM.
- 484 "idiomas" distintos cuando ISO-639-1 tiene ~180 códigos: hay decenas de valores basura de baja frecuencia (la cola completa está en el JSON).

## 12. contentIsLiveStream

**Glosario.** `content.livestream` de OpenRTB: entero donde **1 = transmisión en vivo/lineal** (broadcast programado, canales FAST, eventos) y **0 = bajo demanda (VOD)** o iniciado por el usuario.

**Datos.** 3 valores distintos (1 útil). Fill: 29.13% filas / 38.71% requests. Distribución completa:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Unknown* | 205,942 | 40.22% | 34.45% |
| *Not Available* | 156,888 | 30.64% | 26.84% |
| 1 (live) | 149,170 | 29.13% | 38.71% |

**Conclusiones.**
- **Nunca llega un 0.** Los publishers solo marcan el campo cuando es live y lo omiten para VOD, así que la ausencia NO puede leerse como VOD: queda indistinguible de "no reportado". El campo sirve como señal positiva de live (~39% del tráfico confirmado live) pero no permite calcular la proporción real live vs VOD.
- Que casi 39% del tráfico sea live confirmado cuadra con el peso de canales FAST/lineales (Live TV de TCL, EPG de Roku, canales de TV Azteca/Televisa).
- La coexistencia de `Unknown` y `Not Available` (dos centinelas para lo mismo) confirma que el reporte mezcla capas de normalización distintas según el vendor.

## 13. contentTitle

**Glosario.** `content.title` de OpenRTB: título del contenido (ej. "A New Hope"). Valores no literales encontrados: `roku` y `epg` (placeholders de la guía de programación de Roku — el título real se oculta), `{{content_title}}` (macro sin reemplazar), `run of video network` (placeholder de red). Los sufijos ": trailer" indican inventario pre-roll sobre trailers (mucho volumen de OTTera/OTT Studios).

**Datos.** **13,613 valores distintos — la columna de mayor cardinalidad**. Fill: 91.54% filas / 75.40% requests. Top:

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| *Not Applicable* | 43,297 | 8.46% | **24.60%** |
| roku (placeholder) | 955 | 0.19% | **3.41%** |
| the baddest bad boy | 768 | 0.15% | 0.28% |
| epg (placeholder) | 765 | 0.15% | 2.53% |
| haus of horror | 757 | 0.15% | 0.26% |
| eve | 736 | 0.14% | 0.27% |
| hatchback | 645 | 0.13% | 0.36% |
| catalunya über alles! (mojibake en origen) | 635 | 0.12% | 0.48% |
| ~15 títulos "X: trailer" | ~9,000 | ~1.8% | ~4.2% |
| {{content_title}} (macro) | 592 | 0.12% | 0.02% |
| las estrellas | 545 | 0.11% | 0.31% |
| ...otros 13,570 títulos | 450,905 | 88.07% | |

**Conclusiones.**
- Es la columna con la cola más larga: el 88% de las filas está fuera del top 30 — títulos únicos de catálogo. Eso es bueno (metadata real, no placeholders) pero inutilizable sin agrupar por serie/género.
- Los placeholders `roku`+`epg` apenas son 0.34% de filas pero **6% de los requests**: el inventario de mayor volumen (Roku lineal) esconde el título. Sumado al 24.6% de requests sin título, **~30% del tráfico no es targeteable por título**.
- El top está lleno de películas B de terror y sus trailers (OTT Studios/OTTera repite el mismo catálogo en todos los países) — señal de que gran parte de la "variedad" es el mismo catálogo de relleno replicado.
- Hay problemas de encoding en origen (`catalunya �ber alles!` con carácter de reemplazo ya grabado en el archivo): los joins por título exacto van a fallar en títulos con acentos.

## 14. contentRating

**Glosario.** `content.contentrating` de OpenRTB: clasificación de edad del contenido. Texto libre en la práctica; en el dataset conviven **cinco sistemas**:
- **TV Parental Guidelines (EEUU):** tv-g (todos), tv-pg (supervisión), tv-14 (14+), tv-ma (adultos). Variantes sucias: tv14, tvpg, `tvpg_tv_14` / `tvpg_tv_ma` (sistema y rating concatenados por error).
- **MPAA (cine EEUU):** g, pg, pg-13, r (17+ acompañado), nc-17 (adultos). Variante sucia: pg13.
- **Edades numéricas** (10, 12, 14, 16, 18): sistemas locales por edad — coincide con ClassInd de Brasil y otros sistemas latinoamericanos/europeos.
- **RTC México:** el valor `b` (2,337 filas) encaja con la clasificación mexicana (A/B/B15/C/D); `b15` también aparece en la cola.
- **Sin clasificar:** nr, not rated, `banned` (1,921 filas — "prohibido", valor anómalo), `dv-t` (no identificado), `13+`/`16+` (estilo app stores).

**Datos.** 182 valores distintos (177 útiles). Fill: 84.74% filas / 87.42% requests. Top:

| Valor | Sistema | Filas | % filas | % requests |
|---|---|---:|---:|---:|
| *Not Applicable* | | 77,929 | 15.22% | 12.55% |
| tv-14 | TV Parental | 59,043 | 11.53% | **15.70%** |
| tv-ma | TV Parental | 57,360 | 11.20% | 9.44% |
| r | MPAA | 56,271 | 10.99% | 7.49% |
| tv-pg | TV Parental | 41,685 | 8.14% | 4.95% |
| nr | sin clasificar | 37,769 | 7.38% | 4.14% |
| g | MPAA | 29,689 | 5.80% | 4.25% |
| pg-13 | MPAA | 12,414 | 2.42% | 2.24% |
| not rated | sin clasificar | 12,036 | 2.35% | 1.64% |
| nc-17 | MPAA | 12,026 | 2.35% | 2.24% |
| 12 / 14 / 18 / 15 / 13 / 16 / 10 | edad numérica | 56,351 | 11.01% | 7.86% |
| tv-g | TV Parental | 5,977 | 1.17% | 1.25% |
| tv14 / tvpg / tvpg_tv_14 / tvpg_tv_ma | variantes sucias | 10,147 | 1.98% | **8.85%** |
| b | RTC México | 2,337 | 0.46% | 2.80% |
| banned / dv-t / 13+ / 16+ | anómalos | ~7,500 | ~1.5% | ~1.7% |
| ...otros ~150 | | 26,162 | 5.11% | |

**Conclusiones.**
- Buena cobertura (87% del tráfico trae rating) pero **sin normalizar es inservible para brand safety**: "tv-14", "tv14", "tvpg_tv_14", "14" y "13+" son la misma idea en 5 formatos. Un mapa de ~180 valores → 4-5 niveles de edad (todos / 7+ / 13+ / 16+ / adulto) es factible y cubriría >95% de lo poblado.
- Agregando por severidad, el contenido adulto/maduro (tv-ma, r, nc-17, 18) ronda el 27% de filas — relevante si hay restricciones de marca.
- ~10% de filas declaran explícitamente "sin clasificar" (nr/not rated), que para muchos anunciantes equivale a inventario no apto — conviene tratarlo como categoría propia, no como vacío.
- El 8.85% de requests con las variantes concatenadas (`tvpg_tv_14`) viene de una integración concreta (TV Azteca/Roku) — un solo fix del publisher limpiaría casi 9% del tráfico.

## 15. Total Requests

**Glosario.** Número de bid requests (solicitudes de puja) registradas para esa combinación en el periodo del reporte. Es la medida de **volumen/alcance potencial**, no de impresiones servidas.

**Datos.** Columna numérica, 100% fill. Estadísticos:

| Métrica | Valor |
|---|---:|
| Mínimo | 28,560 |
| Mediana | 107,040 |
| Media | 826,109 |
| p75 | 315,600 |
| p90 | 1,006,880 |
| p99 | 9,757,290 |
| Máximo | 4,507,794,880 (4.5 mil millones, WhaleLive/México) |
| **Share del top 1% de filas** | **50.45% de todos los requests** |

**Conclusiones.**
- Distribución de cola pesadísima: la media es 8x la mediana y **el 1% de las combinaciones concentra la mitad del tráfico**. Cualquier promedio "por fila" del dataset está dominado por ese 1%; por eso este reporte separa siempre % filas de % requests.
- El mínimo de 28,560 sugiere que el reporte tiene un umbral de corte (no hay combinaciones pequeñas), así que la cola real de inventario es aún más larga de lo visible.
- Los valores parecen redondeados/muestreados (muchos múltiplos de 80): serían estimaciones extrapoladas, no conteos exactos.

## 16. eCPM

**Glosario.** *Effective CPM*: ingresos efectivos por cada mil impresiones para esa combinación en el periodo. eCPM = 0 significa que esa combinación **no generó revenue** en el periodo (no ganó subastas o no se midió), no necesariamente que sea invendible.

**Datos.** Columna numérica, 100% fill. Estadísticos:

| Métrica | Valor |
|---|---:|
| Filas con eCPM = 0 | 424,037 (**82.82%**) |
| Filas con eCPM > 0 | 87,963 (17.18%) |
| Media (solo > 0) | 4.905 |
| Mediana (solo > 0) | 3.20 |
| p90 (solo > 0) | 10.83 |
| Máximo | 104.5 |
| **eCPM ponderado por requests (solo > 0)** | **4.97** |

Distribución por rangos:

| Rango eCPM | Filas | % filas | % requests |
|---|---:|---:|---:|
| 0 | 424,037 | 82.82% | 48.07% |
| 0 – 1 | 3,830 | 0.75% | 2.20% |
| 1 – 3 | 37,487 | 7.32% | 16.85% |
| 3 – 5 | 14,824 | 2.90% | 9.21% |
| 5 – 10 | 17,928 | 3.50% | **18.46%** |
| 10 – 20 | 13,703 | 2.68% | 5.06% |
| >= 20 | 191 | 0.04% | 0.16% |

**Conclusiones.**
- Aunque el 83% de las filas no monetiza, ese grupo solo representa el **48% de los requests**: la mitad del tráfico sí corre por combinaciones con revenue. La monetización sigue al volumen.
- El grueso del tráfico monetizado se vende entre 1 y 10 USD de eCPM, con un bloque fuerte en 5-10 (18.5% del tráfico total) — rango sano para CTV LATAM.
- Los eCPMs >20 son anecdóticos (191 filas, 0.16% del tráfico) y probablemente deals puntuales; el máximo de 104.5 es un outlier a auditar antes de usarlo en cualquier promedio.
- Cruce clave con metadata (de la parte 1 del análisis previo): las filas con `contentLanguage` poblado promedian eCPM 5.15 vs 3.76 sin él, y las filas con los 9 campos content completos promedian 4x más que las incompletas. **La metadata rica correlaciona con mejor monetización.**

---

# PARTE 2 — Análisis por país

Metodología: para cada país se filtraron sus filas y se recalculó, columna por columna, el número de valores distintos, el fill rate y la distribución. Los porcentajes de los "top valores" son **% sobre las filas de ese país**. El top-15 completo de cada columna de cada país está en `reporte-content-objects-detallado.json` (clave `countries`). "eCPM pond." = eCPM ponderado por requests sobre las filas con eCPM > 0.

## Tabla comparativa general

| País | Filas | % requests | % filas eCPM=0 | eCPM medio (>0) | eCPM pond. | Fill category | Fill livestream | Fill length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| México | 146,426 | 61.77% | 81.3% | 2.73 | 4.40 | 23.3% | 25.8% | 17.9% |
| Argentina | 96,040 | 16.78% | 80.5% | 6.37 | 6.39 | 11.4% | 31.8% | 4.6% |
| Colombia | 50,566 | 6.49% | 87.8% | 2.65 | 2.97 | 24.5% | 27.9% | 9.7% |
| Chile | 57,727 | 5.85% | 80.4% | 7.54 | **8.60** | 14.4% | 18.1% | 7.0% |
| Perú | 42,991 | 2.53% | 82.1% | 6.58 | 6.15 | 24.0% | 27.9% | 7.6% |
| Ecuador | 21,503 | 1.31% | 94.1% | 6.25 | 7.55 | 20.4% | 31.9% | 7.0% |
| Costa Rica | 16,794 | 1.28% | **62.8%** | 4.65 | 6.04 | 25.4% | 42.3% | 11.4% |
| Rep. Dominicana | 19,162 | 1.19% | 91.7% | 5.70 | 5.47 | 15.6% | 48.9% | 5.6% |
| Venezuela | 8,941 | 0.65% | **100%** | — | — | 41.6% | 46.0% | 21.7% |
| Panamá | 10,132 | 0.54% | 89.6% | 4.31 | 4.19 | 26.7% | 31.4% | 4.3% |
| Puerto Rico | 7,235 | 0.44% | 88.7% | **8.62** | 7.99 | **62.5%** | 39.2% | **65.3%** |
| Uruguay | 5,022 | 0.37% | 97.5% | 7.25 | 5.47 | 46.5% | 24.8% | 18.9% |
| Guatemala | 7,256 | 0.22% | 77.5% | 4.73 | 4.50 | 47.9% | 22.9% | 9.2% |
| El Salvador | 7,683 | 0.22% | 85.8% | 6.09 | 6.31 | 41.9% | 30.1% | 4.1% |
| Honduras | 10,046 | 0.21% | 78.1% | 3.88 | 3.88 | 26.4% | 30.6% | 3.8% |
| Paraguay | 1,827 | 0.09% | 88.4% | 5.96 | 5.94 | 23.0% | **71.9%** | 5.4% |
| Bolivia | 1,136 | 0.04% | 99.9% | 1.98 | 1.98 | **75.4%** | 63.6% | 50.7% |
| Nicaragua | 1,513 | 0.03% | 70.7% | 6.01 | 7.77 | 56.6% | 42.7% | 37.0% |

Lectura rápida: los mercados grandes tienen la peor metadata (paradójicamente), Venezuela no monetiza nada, Puerto Rico se comporta como mercado estadounidense, y en los países chicos la metadata mejora porque el mix de publishers cambia (menos TCL, más Roku/Coolita).

## México — 146,426 filas (28.6%) · 61.77% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 172 | 100% | OTTera.tv 14.1%, iion 12.8%, TCL ADs (APAC) 11.0%, TCL ADS-Springserve 11.0%, Equativ 7.6% |
| Publisher ID | 175 | 100% | (el país con más cuentas activas) |
| pageURL | 505 | 100% | com.tcl.livetv 24.4%, com.tcl.movieark 21.5%, com.tcl.browser 6.1%, 974696 (Roku) 5.2% |
| App Name | 303 | 82.8% | Live TV 21.5%, MovieArk 21.5%, *Not Available 17.2%*, BrowseHere 6.1%, TCL CHANNEL 4.2% |
| contentGenre | 5,682 | 99.0% | drama 10.9%, documentary 4.3%, other 4.1%, comedy 3.8%, horror 3.3% |
| contentLanguage | 476 | 78.4% | en 36.8%, es 36.7%, *N/A 21.3%*, spa 0.8%, pt 0.8% |
| contentRating | 149 | 84.5% | *N/A 15.5%*, tv-14 13.7%, r 9.8%, tv-ma 8.3%, tv-pg 8.2% |
| contentCategory | 310 | 23.3% | *[-7] 76.7%*, [IAB1] 4.6%, [IAB1-5] 3.8%, [IAB12] 2.6%, [IAB1-22] 2.0% |
| contentIsLiveStream | 3 | 25.8% | *Unknown 38.9%*, *N/A 35.3%*, 1 25.8% |
| contentLength | 9 | 17.9% | *N/A 82.1%*, 6 6.5%, 5 4.0%, 8 3.7%, 4 2.2% |
| contentSeries | 1,488 | 6.9% | *N/A 91.5%*, md5-vacío 1.6%, VOD 0.5%, {{CONTENT_SERIES}} 0.2% |
| contentTitle | 10,341 | 82.1% | *N/A 17.9%*, las estrellas 0.4%, canal 5 0.3%, golden 0.2% |
| contentIsTitlePresent | 2 | — | true 82.1%, false 17.9% |

**Conclusiones — México:**
- Es el único país con **paridad inglés/español** (36.8% vs 36.7%): el peso de los broadcasters locales (Televisa con "Las Estrellas" y "Canal 5" como top títulos, TV Azteca, ViX) equilibra el catálogo importado.
- Concentra la peor tasa de títulos del continente fuera de Puerto Rico: 17.9% de filas sin título (vs 2-5% en el resto). Casi el 80% de todas las filas sin título del dataset son mexicanas — la ruta Roku/EPG y los agregadores pierden el título justo en el mercado más grande.
- El eCPM medio no-cero es el más bajo de los mercados grandes (2.73), pero el ponderado sube a 4.40: hay mucha cola barata y un núcleo premium de alto volumen (Roku 14.5% de requests globales sale casi todo de aquí, TV Azteca eCPMs tipo 6).
- Con 172 publishers y 505 bundles es, por lejos, el mercado más fragmentado: la deduplicación de supply paths importa más aquí que en ningún otro país.

## Argentina — 96,040 filas (18.8%) · 16.78% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 118 | 100% | OTTera.tv 21.0%, TCL ADS-Springserve 20.3%, iion 19.8%, TCL ADs (APAC) 18.2%, PML Digital 5.7% |
| pageURL | 160 | 100% | com.tcl.waterfall 31.7%, com.tcl.livetv 25.4%, com.tcl.movieark 18.5%, com.tcl.browser 17.6% |
| App Name | 120 | 95.9% | TCL CHANNEL 31.7%, Live TV 23.4%, MovieArk 18.5%, BrowseHere 17.6% |
| contentGenre | 2,369 | 98.9% | drama 8.0%, documentary 6.1%, other 6.0%, horror 3.4%, comedy 3.3% |
| contentLanguage | 51 | 78.6% | en 39.8%, es 35.7%, *N/A 21.4%*, pt 1.0%, ru 0.4% |
| contentRating | 121 | 87.8% | tv-ma 13.2%, *N/A 12.1%*, g 11.8%, r 11.0%, tv-14 8.7% |
| contentCategory | 119 | 11.4% | *[-7] 88.6%*, [IAB1-22] 3.8%, [IAB1] 3.2%, [IAB17] 0.4% |
| contentIsLiveStream | 3 | 31.8% | *N/A 38.0%*, 1 31.8%, *Unknown 30.2%* |
| contentLength | 9 | 4.6% | *N/A 95.4%*, 4 1.8%, 5 1.1%, 6 1.0% |
| contentSeries | 464 | 2.6% | *N/A 97.3%*, VOD 0.6%, {{CONTENT_SERIES}} 0.1% |
| contentTitle | 7,410 | 97.4% | *N/A 2.6%*, haus of horror 0.1%, the baddest bad boy 0.1% |
| contentIsTitlePresent | 2 | — | true 97.4%, false 2.6% |

**Conclusiones — Argentina:**
- **El mercado más "TCL" del dataset**: las 4 apps nativas de TCL suman el 93% de las filas. Eso explica sus dos extremos: excelente fill de título (97.4%, TCL siempre lo manda) y el segundo peor fill de categoría (11.4%) y de duración (4.6%), que TCL no manda.
- Segundo mercado por volumen y con buen precio: eCPM ~6.4 tanto medio como ponderado (sin la cola barata de México — la distribución es más pareja).
- Sin presencia relevante de broadcasters locales en el top: el inventario argentino de este dataset es esencialmente OEM + catálogo internacional (el top de títulos son las mismas películas B de OTT Studios que en todos lados).

## Colombia — 50,566 filas (9.9%) · 6.49% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 91 | 100% | iion 30.3%, OTTera.tv 24.1%, Select Plus 11.5%, TCL ADs (APAC) 11.2%, METAX 7.8% |
| pageURL | 172 | 100% | com.tcl.movieark 34.4%, com.tcl.livetv 28.8%, com.tcl.waterfall 13.0%, com.tcl.browser 8.1% |
| App Name | 132 | 96.7% | MovieArk 34.4%, Live TV 28.6%, TCL CHANNEL 13.0%, BrowseHere 8.1% |
| contentGenre | 1,308 | 98.5% | drama 10.2%, other 7.8%, documentary 4.9%, horror 4.1%, comedy 3.1% |
| contentLanguage | 30 | **61.9%** | en 41.6%, *N/A 38.1%*, es 15.3%, c (basura) 1.9%, pt 0.7% |
| contentRating | 97 | 80.0% | *N/A 19.9%*, r 11.8%, tv-14 9.8%, tv-pg 9.4%, nr 8.9% |
| contentCategory | 128 | 24.5% | *[-7] 75.5%*, [IAB1] 7.2%, [IAB1-22] 3.5%, [IAB1, IAB1-5] 2.6%, [sports] 1.9% |
| contentIsLiveStream | 3 | 27.9% | *Unknown 45.1%*, 1 27.9%, *N/A 27.0%* |
| contentLength | 9 | 9.7% | *N/A 90.3%*, 4 3.3%, 5 2.8%, 6 2.5% |
| contentSeries | 577 | 5.8% | *N/A 94.2%*, VOD 0.9%, No Series 0.1% |
| contentTitle | 4,157 | 94.9% | *N/A 5.1%*, {{content_title}} 0.2%, eve 0.2%, blink and friends 0.2% |
| contentIsTitlePresent | 2 | — | true 94.9%, false 5.1% |

**Conclusiones — Colombia:**
- **El peor mercado en monetización de los grandes**: 87.8% de filas sin revenue y eCPM ponderado de 2.97 — la mitad que Argentina y un tercio de Chile. Y no es por falta de volumen (es el 4° mercado).
- Tiene además el peor fill de idioma de los mercados grandes (61.9%) y la mayor desproporción inglés/español (41.6% vs 15.3%): el inventario colombiano de este dataset es mayormente catálogo importado sin señal local. La combinación "no sé qué idioma es + no monetiza" difícilmente es casualidad.
- iion es aquí el seller líder (30.3%), a diferencia de todos los demás mercados grandes donde lidera OTTera o TCL.
- Aparece la macro sin reemplazar `{{content_title}}` entre los top títulos — el bug de configuración está activo en el supply colombiano.

## Chile — 57,727 filas (11.3%) · 5.85% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 91 | 100% | iion 21.0%, TCL ADS-Springserve 19.5%, TCL ADs (APAC) 17.7%, OTTera.tv 17.3%, PML Digital 5.8% |
| pageURL | 140 | 100% | com.tcl.movieark 42.3%, com.tcl.livetv 34.0%, com.tcl.waterfall 7.5%, com.tcl.browser 5.3% |
| App Name | 102 | 92.1% | MovieArk 42.3%, Live TV 29.2%, *N/A 7.9%*, TCL CHANNEL 7.5% |
| contentGenre | 1,374 | 99.5% | drama 8.6%, other 6.7%, documentary 6.0%, horror 3.7%, comedy 3.3% |
| contentLanguage | 44 | 75.5% | en 52.9%, *N/A 24.5%*, es 18.4%, pt 1.4%, ru 0.5% |
| contentRating | 95 | 84.2% | *N/A 15.8%*, tv-ma 13.9%, r 11.9%, tv-14 10.8%, nr 9.3% |
| contentCategory | 110 | 14.4% | *[-7] 85.6%*, [IAB1] 6.4%, [IAB1, IAB1-5] 0.8%, [IAB17] 0.7% |
| contentIsLiveStream | 3 | **18.1%** | *N/A 41.9%*, *Unknown 40.1%*, 1 18.1% |
| contentLength | 9 | 7.0% | *N/A 93.0%*, 4 2.7%, 5 1.9%, 6 1.6% |
| contentSeries | 490 | 4.6% | *N/A 95.3%*, VOD 0.9%, {{CONTENT_SERIES}} 0.1% |
| contentTitle | 3,937 | 96.6% | *N/A 3.4%*, catalunya über alles! 0.2%, haus of horror 0.2%, {{content_title}} 0.2% |
| contentIsTitlePresent | 2 | — | true 96.6%, false 3.4% |

**Conclusiones — Chile:**
- **El mercado grande con mejor precio**: eCPM ponderado 8.60 y medio 7.54, con una tasa de monetización normal (80% ceros). El inventario chileno monetizado paga casi el doble que el argentino y el triple que el colombiano.
- Perfil de consumo muy VOD/película: MovieArk (la app de películas de TCL) sola es el 42% de las filas, y el fill de livestream es el más bajo del dataset (18.1%) — inventario mayormente on-demand.
- Muy anglófono en catálogo: 52.9% en vs 18.4% es, el contenido local pesa poco en variedad.
- La metadata estructural (category 14.4%, length 7%) es pobre — el precio alto viene del mercado (demanda/poder adquisitivo), no de la calidad de señales.

## Perú — 42,991 filas (8.4%) · 2.53% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 83 | 100% | OTTera.tv 27.1%, iion 24.4%, Select Plus 13.2%, TCL ADs (APAC) 8.9%, Aluna 6.5% |
| pageURL | 102 | 100% | com.tcl.movieark 41.5%, com.tcl.livetv 25.9%, com.tcl.waterfall 14.6%, com.tcl.browser 5.8% |
| App Name | 71 | 94.8% | MovieArk 41.5%, Live TV 23.5%, TCL CHANNEL 14.6%, BrowseHere 5.8% |
| contentGenre | 1,656 | 97.9% | drama 11.2%, other 6.6%, documentary 5.1%, horror 4.6%, comedy 3.8% |
| contentLanguage | 28 | 70.0% | en 45.4%, *N/A 30.0%*, es 19.6%, pt 1.3%, c 0.9% |
| contentRating | 99 | 83.1% | *N/A 16.9%*, tv-ma 14.2%, tv-14 11.8%, r 11.6%, tv-pg 8.8% |
| contentCategory | 119 | 24.0% | *[-7] 76.0%*, [IAB1] 9.8%, [IAB1-22] 2.9%, [sports] 2.5% |
| contentIsLiveStream | 3 | 27.9% | *Unknown 52.2%*, 1 27.9%, *N/A 19.9%* |
| contentLength | 9 | 7.6% | *N/A 92.4%*, 4 2.9%, 5 1.8%, 6 1.6% |
| contentSeries | 484 | 4.4% | *N/A 95.5%*, VOD 1.0%, QWEST 0.2% |
| contentTitle | 4,444 | 95.8% | *N/A 4.2%*, the baddest bad boy 0.2%, catalunya über alles! 0.2% |
| contentIsTitlePresent | 2 | — | true 95.8%, false 4.2% |

**Conclusiones — Perú:**
- Mucho catálogo y poco tráfico: 8.4% de las filas pero solo 2.5% de los requests — las combinaciones peruanas mueven poco volumen cada una (el reparto entre OEMs sin un player dominante de alto volumen).
- Precio sano (eCPM ponderado 6.15, medio 6.58) con tasa de ceros normal (82%): mercado pequeño pero eficiente.
- Mismo patrón OEM que Chile (MovieArk 41.5%) y misma pobreza de metadata estructural. Nada local relevante en el top de títulos o series.

## Ecuador — 21,503 filas (4.2%) · 1.31% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 53 | 100% | TCL ADs (APAC) 40.4%, OTTera.tv 37.2%, Select Plus 6.9%, PML Digital 5.1% |
| pageURL | 57 | 100% | com.tcl.livetv 37.9%, com.tcl.movieark 24.5%, com.tcl.waterfall 20.0%, +com.tcl.livetv 4.7% |
| App Name | 42 | 93.7% | Live TV 37.0%, MovieArk 24.5%, TCL CHANNEL 20.0% |
| contentGenre | 1,265 | 99.1% | drama 9.8%, other 7.1%, documentary 5.8%, horror 3.8% |
| contentLanguage | 25 | **98.2%** | en 64.5%, es 27.6%, pt 1.6%, c 1.3% |
| contentRating | 82 | 86.4% | *N/A 13.6%*, tv-ma 12.6%, r 12.1%, tv-14 10.9% |
| contentCategory | 92 | 20.4% | *[-7] 79.6%*, [IAB1] 8.3%, [sports] 5.1% |
| contentIsLiveStream | 3 | 31.9% | *Unknown 38.4%*, 1 31.9%, *N/A 29.8%* |
| contentLength | 9 | 7.0% | *N/A 93.0%*, 4 2.1%, 5 1.9%, 8 1.6% |
| contentSeries | 336 | 3.3% | *N/A 96.7%*, VOD 0.5%, OTT Studios Sports 0.1%, J1 League 0.1% |
| contentTitle | 3,999 | 97.3% | *N/A 2.7%*, la mujer del anarquista 0.2%, catalunya über alles! 0.2% |
| contentIsTitlePresent | 2 | — | true 97.3%, false 2.7% |

**Conclusiones — Ecuador:**
- Duopolio TCL + OTTera (77.6% de filas entre ambos) con solo 53 publishers — mercado poco profundo.
- La monetización es rara pero buena: 94.1% de filas con eCPM cero (de las peores tasas), pero lo que paga, paga bien (ponderado 7.55). Pocas campañas activas con buen precio.
- Curiosamente tiene el segundo mejor fill de idioma (98.2%) — casi todo su inventario pasa por integraciones que sí normalizan idioma. El bundle malformado `+com.tcl.livetv` está concentrado aquí (4.7% de sus filas).

## Costa Rica — 16,794 filas (3.3%) · 1.28% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 71 | 100% | OTTera.tv 37.4%, TCL ADS-Springserve 32.9%, Select Plus 10.9%, Aluna 4.2% |
| pageURL | 88 | 100% | com.tcl.movieark 37.0%, com.tcl.waterfall 24.8%, com.tcl.browser 16.4%, com.tcl.livetv 7.1% |
| App Name | 75 | 98.5% | MovieArk 37.0%, TCL CHANNEL 24.8%, BrowseHere 16.4%, Live TV 7.1%, Coolita 6.8% |
| contentGenre | 1,144 | 98.9% | drama 9.7%, other 6.7%, documentary 5.5%, horror 4.0% |
| contentLanguage | 32 | 95.5% | en 70.8%, es 18.4%, pt 2.8% |
| contentRating | 65 | 86.2% | *N/A 13.8%*, tv-ma 12.8%, r 11.5%, tv-14 11.0%, g 8.6% |
| contentCategory | 101 | 25.4% | *[-7] 74.6%*, [IAB1-22] 7.8%, [IAB1] 7.2%, [IAB17] 1.6% |
| contentIsLiveStream | 3 | 42.3% | 1 42.3%, *Unknown 37.2%*, *N/A 20.5%* |
| contentLength | 9 | 11.4% | *N/A 88.6%*, 4 4.3%, 5 3.1%, 6 1.6% |
| contentSeries | 354 | 7.5% | *N/A 92.4%*, VOD 0.4%, The Cube USA 0.1% |
| contentTitle | 3,076 | 95.6% | *N/A 4.4%*, catalunya über alles! 0.2%, eve 0.2% |
| contentIsTitlePresent | 2 | — | true 95.6%, false 4.4% |

**Conclusiones — Costa Rica:**
- **El mercado con mejor tasa de monetización del dataset**: solo 62.8% de filas con eCPM cero (vs 83% global). Más de un tercio de su inventario genera revenue — hay demanda activa comprando Costa Rica de forma amplia.
- 42.3% de filas confirmadas live (el doble del promedio): fuerte peso de canales lineales/FAST.
- Muy anglófono (70.8% en) y con el mismo catálogo OEM internacional del resto de Centroamérica.

## República Dominicana — 19,162 filas (3.7%) · 1.19% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 55 | 100% | OTTera.tv 33.3%, TCL ADS-Springserve 28.1%, TCL ADs (APAC) 22.0%, Select Plus 9.4% |
| pageURL | 82 | 100% | com.tcl.waterfall 35.1%, com.tcl.movieark 33.2%, com.tcl.browser 22.3%, com.coolita.channel 2.6% |
| App Name | 56 | 99.0% | TCL CHANNEL 35.1%, MovieArk 33.2%, BrowseHere 22.3%, Coolita 2.6% |
| contentGenre | 1,133 | 99.3% | drama 8.0%, other 7.0%, documentary 6.6%, horror 3.8% |
| contentLanguage | 27 | 97.8% | en 77.0%, es 15.5%, pt 1.8% |
| contentRating | 72 | 88.6% | g 13.9%, r 12.8%, *N/A 11.4%*, tv-14 10.8%, tv-ma 10.2% |
| contentCategory | 94 | 15.6% | *[-7] 84.5%*, [IAB1-22] 7.9%, [IAB1] 1.4% |
| contentIsLiveStream | 3 | 48.9% | 1 48.9%, *N/A 26.2%*, *Unknown 24.9%* |
| contentLength | 9 | 5.6% | *N/A 94.4%*, 5 1.9%, 4 1.7%, 6 1.3% |
| contentSeries | 342 | 3.5% | *N/A 96.5%*, VOD 0.3%, Run Of Video Network 0.1% |
| contentTitle | 3,024 | 96.9% | *N/A 3.1%*, catalunya über alles! 0.2%, humble pie 0.2% |
| contentIsTitlePresent | 2 | — | true 96.9%, false 3.1% |

**Conclusiones — República Dominicana:**
- El inventario más anglófono del grupo hispano (77% en / 15.5% es) y con la mayor proporción de live confirmado tras Paraguay (48.9%): perfil de canales lineales internacionales sobre TVs TCL.
- TCL (tres apps) + OTTera = ~90% de las filas; casi sin supply local.
- Monetización floja: 91.7% de ceros, aunque el precio cuando paga es decente (5.47 ponderado).

## Venezuela — 8,941 filas (1.8%) · 0.65% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 48 | 100% | OTTera.tv 45.1%, Select Plus 28.5%, Coocaa 6.5%, Xapads 5.1% |
| pageURL | 67 | 100% | com.tcl.movieark 55.3%, com.tcl.browser 16.0%, com.coolita.channel 11.6% |
| App Name | 48 | 97.7% | MovieArk 55.3%, BrowseHere 16.0%, Coolita 11.6%, TCL CHANNEL 3.8% |
| contentGenre | 972 | 99.2% | drama 10.4%, documentary 6.9%, other 5.5%, horror 4.5% |
| contentLanguage | 24 | 95.3% | en 69.5%, es 18.8%, pt 4.0% |
| contentRating | 63 | 70.7% | *N/A 29.3%*, tv-pg 12.0%, tv-14 9.3%, tv-ma 8.6% |
| contentCategory | 93 | 41.6% | *[-7] 58.4%*, [IAB1-22] 14.6%, [IAB1] 4.9%, [640] 2.4% |
| contentIsLiveStream | 3 | 46.0% | *Unknown 50.9%*, 1 46.0%, *N/A 3.1%* |
| contentLength | 8 | 21.7% | *N/A 78.3%*, 5 7.5%, 4 6.8%, 6 5.3% |
| contentSeries | 340 | 12.0% | *N/A 88.0%*, OTT Studios Ent. On Demand 0.5%, VOD 0.3% |
| contentTitle | 2,794 | 89.8% | *N/A 10.2%*, the baddest bad boy 0.2%, haus of horror 0.2% |
| contentIsTitlePresent | 2 | — | true 89.8%, false 10.2% |

**Conclusiones — Venezuela:**
- **El 100% de sus 8,941 filas tiene eCPM = 0: ni una sola combinación venezolana registró revenue en el periodo.** Consecuencia esperable de que la demanda programática internacional excluye el país (sanciones/riesgo cambiario). El inventario existe (2,755 millones de requests) pero nadie lo compra.
- Irónicamente su metadata es mejor que la media (category 41.6%, length 21.7%, series 12%): la calidad de señal no es el problema.
- Su supply está desplazado a MovieArk (55.3%) y Coolita — el perfil OEM puro, sin broadcasters.

## Panamá — 10,132 filas (2.0%) · 0.54% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 63 | 100% | OTTera.tv 40.7%, TCL ADS-Springserve 33.0%, Select Plus 14.5% |
| pageURL | 78 | 100% | com.tcl.movieark 42.9%, com.tcl.browser 20.1%, com.tcl.livetv 14.0%, com.tcl.waterfall 12.0% |
| App Name | 62 | 96.3% | MovieArk 42.9%, BrowseHere 20.1%, Live TV 14.0%, TCL CHANNEL 12.0% |
| contentGenre | 879 | 98.0% | drama 11.5%, other 7.1%, documentary 5.5%, horror 4.9% |
| contentLanguage | 24 | 96.5% | en 77.2%, es 13.8%, pt 1.3% |
| contentRating | 60 | 83.5% | *N/A 16.5%*, tv-ma 13.2%, tv-14 12.2%, r 12.1% |
| contentCategory | 58 | 26.7% | *[-7] 73.3%*, [IAB1] 10.8%, [IAB1-22] 9.6% |
| contentIsLiveStream | 3 | 31.4% | *Unknown 52.0%*, 1 31.4%, *N/A 16.6%* |
| contentLength | 9 | 4.3% | *N/A 95.7%*, 4 1.3%, 8 1.3% |
| contentSeries | 31 | 2.2% | *N/A 97.8%*, VOD 0.7%, OTT Studios Sports 0.4% |
| contentTitle | 2,290 | 95.5% | *N/A 4.5%*, catalunya über alles! 0.3%, haus of horror 0.3% |
| contentIsTitlePresent | 2 | — | true 95.5%, false 4.5% |

**Conclusiones — Panamá:**
- Mercado calcado a Costa Rica en estructura (OTTera + TCL Springserve + Select Plus, catálogo en inglés 77%) pero con la mitad de tasa de monetización (89.6% ceros) y precio menor (4.19 ponderado).
- Solo 31 valores de series (el más pobre en variedad de series): inventario de canal/película, no de series.

## Puerto Rico — 7,235 filas (1.4%) · 0.44% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 109 | 100% | **Roku - oRTB 38.2%**, OTTera.tv 17.1%, Seedtag 5.0%, Plex 4.6%, Scripps-FreeWheel 4.2% |
| Publisher ID | 111 | 100% | (109 sellers en un mercado de 7K filas — profundidad inusual) |
| pageURL | 209 | 100% | **151908 (Roku Channel) 47.9%**, com.tcl.movieark 14.3%, com.tcl.browser 5.0%, 13535 (Plex) 3.5% |
| App Name | 150 | 96.0% | The Roku Channel 47.9%, MovieArk 14.3%, BrowseHere 5.0%, Plex 3.5% |
| contentGenre | 1,619 | 94.1% | drama 8.0%, entertainment 7.3%, *N/A 5.8%*, crime 3.2%, news 2.5% |
| contentLanguage | 26 | 88.6% | en 69.7%, es 16.8%, *N/A 11.4%* |
| contentRating | 58 | 91.1% | tv-14 18.7%, tvpg 14.7%, tv14 12.8%, *N/A 8.8%*, r 8.0% |
| contentCategory | 293 | **62.5%** | *[-7] 37.5%*, [IAB1-5, IAB1-7] 9.7%, [IAB1-7] 8.9%, [IAB1] 8.4% |
| contentIsLiveStream | 3 | 39.2% | *Unknown 51.4%*, 1 39.2%, *N/A 9.3%* |
| contentLength | 9 | **65.3%** | *N/A 34.7%*, 5 30.6%, 6 17.0%, 4 9.7%, 7 4.3% |
| contentSeries | 480 | 24.3% | *N/A 48.7%*, **md5-vacío 26.9%**, Chicago Fire 1.7%, NCIS 1.4%, FBI 1.2% |
| contentTitle | 1,341 | **54.3%** | *N/A 45.7%*, roku 10.0%, epg 9.2%, run of video network 0.9%, local news 0.6% |
| contentIsTitlePresent | 2 | — | true 54.3%, false 45.7% |

**Conclusiones — Puerto Rico:**
- **Es un mercado estadounidense dentro del dataset LATAM**: domina Roku (38% del supply, The Roku Channel 48% de filas), aparecen sellers US (Scripps, Plex, FreeWheel) y las series top son procedurales de networks US (Chicago Fire, NCIS, FBI). 109 publishers para 7K filas — la mayor profundidad de supply relativa.
- Tiene la **mejor metadata estructural** por mucho: category 62.5%, length 65.3%, series 24.3%. Pero con las trampas de Roku: el 26.9% de "series" es el hash MD5 vacío, y los títulos se ocultan tras `roku`/`epg` — solo 54.3% de fill de título, el peor del dataset.
- El mejor eCPM medio (8.62): precio de mercado US. Para campañas hispanas en EEUU este es probablemente el inventario más interesante del archivo, con la salvedad del título oculto.
- Sus ratings vienen con las variantes sucias (`tvpg`, `tv14` sin guión): el fix de normalización de ratings es principalmente para este supply.

## Uruguay — 5,022 filas (1.0%) · 0.37% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 43 | 100% | **OTTera.tv 67.9%**, Coocaa 11.3%, METAX 4.3%, Pluto LATAM 3.8% |
| pageURL | 41 | 100% | com.tcl.movieark 47.6%, com.tcl.livetv 22.6%, com.coolita.channel 11.3%, tv.pluto.android 3.7% |
| App Name | 34 | 96.8% | MovieArk 47.6%, Live TV 22.6%, Coolita 11.3%, PlutoTV 3.7% |
| contentGenre | 915 | 98.2% | drama 7.3%, documentary 5.9%, other 5.2%, horror 3.3% |
| contentLanguage | 24 | 98.2% | en 71.5%, es 19.4%, pt 3.7% |
| contentRating | 57 | 93.9% | **tv-pg 21.1%**, tv-ma 12.0%, tv-14 11.0%, r 10.2% |
| contentCategory | 89 | 46.5% | *[-7] 53.5%*, [IAB1] 22.0%, [IAB17] 3.0%, [sports] 2.9% |
| contentIsLiveStream | 3 | 24.8% | *Unknown 69.9%*, 1 24.8% |
| contentLength | 9 | 18.9% | *N/A 81.1%*, 4 6.6%, 5 6.0%, 6 3.8% |
| contentSeries | 323 | 11.4% | *N/A 88.5%*, VOD 0.4%, The Cube USA 0.2%, J1 League 0.2% |
| contentTitle | 2,808 | 92.5% | *N/A 7.5%*, red bull tv 0.3%, soul storm 0.3% |
| contentIsTitlePresent | 2 | — | true 92.5%, false 7.5% |

**Conclusiones — Uruguay:**
- La mayor dependencia de un solo seller del dataset: OTTera concentra el 67.9% de las filas. Riesgo de supply path único.
- 97.5% de filas sin revenue (solo Venezuela y Bolivia están peor): la demanda casi no compra Uruguay pese a precio razonable cuando paga (5.47).
- Es el único país cuyo rating top es tv-pg (contenido familiar) y con Pluto TV en el top de apps.

## Guatemala — 7,256 filas (1.4%) · 0.22% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 54 | 100% | OTTera.tv 62.1%, TCL ADs (APAC) 14.0%, Televisa Univision via Springserve 5.1%, Vidaa 4.0% |
| pageURL | 69 | 100% | com.tcl.livetv 34.1%, com.tcl.movieark 19.3%, com.tcl.browser 15.0%, com.tcl.waterfall 13.4% |
| App Name | 56 | 92.1% | Live TV 34.1%, MovieArk 19.3%, BrowseHere 15.0%, TCL CHANNEL 13.4% |
| contentGenre | 635 | 99.1% | drama 13.9%, other 6.4%, horror 4.5%, comedy 4.4% |
| contentLanguage | 22 | 95.6% | en 70.8%, es 19.3%, pt 1.2% |
| contentRating | 51 | **95.1%** | tv-ma 18.6%, tv-14 18.1%, r 13.1%, tv-pg 7.9% |
| contentCategory | 52 | 47.9% | *[-7] 52.1%*, [IAB1] 21.8%, [IAB1-22] 13.6%, [IAB12] 2.9% |
| contentIsLiveStream | 3 | 22.9% | *Unknown 66.9%*, 1 22.9% |
| contentLength | 7 | 9.2% | *N/A 90.8%*, 8 4.2%, 4 2.2% |
| contentSeries | 57 | 4.5% | *N/A 95.5%*, VOD 1.2%, OTT Studios Ent. On Demand 0.6% |
| contentTitle | 1,692 | 95.5% | *N/A 4.5%*, catalunya über alles! 0.4%, eve 0.3% |
| contentIsTitlePresent | 2 | — | true 95.5%, false 4.5% |

**Conclusiones — Guatemala:**
- El mejor fill de rating del dataset (95.1%) y buen fill de categoría (47.9%): su mix OTTera+Televisa manda señales completas.
- Única presencia relevante de TelevisaUnivision fuera de México (5.1% del supply local).
- Tasa de monetización buena (77.5% ceros, mejor que la media) aunque a precio moderado (4.50).

## El Salvador — 7,683 filas (1.5%) · 0.22% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 48 | 100% | OTTera.tv 59.7%, TCL ADs (APAC) 15.4%, Select Plus 15.4% |
| pageURL | 51 | 100% | com.tcl.livetv 36.6%, com.tcl.movieark 28.1%, com.tcl.browser 15.8%, com.tcl.waterfall 11.9% |
| App Name | 44 | 97.5% | Live TV 36.6%, MovieArk 28.1%, BrowseHere 15.8%, TCL CHANNEL 11.9% |
| contentGenre | 711 | 98.6% | drama 12.4%, other 7.5%, horror 6.0%, documentary 4.6% |
| contentLanguage | 24 | 96.9% | en 76.6%, es 14.5%, pt 1.3% |
| contentRating | 47 | 84.1% | tv-ma 16.1%, *N/A 15.9%*, r 12.5%, tv-14 12.5% |
| contentCategory | 47 | 41.9% | *[-7] 58.1%*, [IAB1] 21.5%, [IAB1-22] 14.4% |
| contentIsLiveStream | 3 | 30.1% | *Unknown 63.5%*, 1 30.1% |
| contentLength | 7 | 4.1% | *N/A 95.9%*, 4 1.8%, 6 1.2% |
| contentSeries | 29 | 2.4% | *N/A 97.6%*, VOD 0.7% |
| contentTitle | 1,724 | 96.9% | *N/A 3.1%*, catalunya über alles! 0.3% |
| contentIsTitlePresent | 2 | — | true 96.9%, false 3.1% |

**Conclusiones — El Salvador:** perfil centroamericano estándar (OTTera dominante, catálogo en inglés 76.6%, metadata de categoría decente 41.9% por la vía OTTera). Precio bueno para la región (6.31 ponderado). Sin nada local en el top.

## Honduras — 10,046 filas (2.0%) · 0.21% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 49 | 100% | TCL ADS-Springserve 43.9%, OTTera.tv 33.6%, Select Plus 12.1% |
| pageURL | 76 | 100% | com.tcl.movieark 35.1%, com.tcl.livetv 20.5%, com.tcl.browser 20.1%, com.tcl.waterfall 14.6% |
| App Name | 65 | 96.7% | MovieArk 35.1%, Live TV 20.5%, BrowseHere 20.1%, TCL CHANNEL 14.6% |
| contentGenre | 587 | 97.8% | drama 12.5%, other 6.8%, horror 5.7%, documentary 4.1% |
| contentLanguage | 23 | 94.7% | en 74.5%, es 14.3%, pt 1.6% |
| contentRating | 46 | 85.7% | tv-ma 18.3%, *N/A 14.3%*, r 12.8%, tv-14 12.8% |
| contentCategory | 47 | 26.4% | *[-7] 73.6%*, [IAB1] 10.7%, [IAB1-22] 9.1% |
| contentIsLiveStream | 3 | 30.6% | *Unknown 45.1%*, 1 30.6%, *N/A 24.3%* |
| contentLength | 6 | 3.8% | *N/A 96.2%*, 4 1.5%, 6 1.2% |
| contentSeries | 64 | 3.2% | *N/A 96.8%*, VOD 0.6% |
| contentTitle | 1,317 | 97.5% | *N/A 2.5%*, catalunya über alles! 0.3% |
| contentIsTitlePresent | 2 | — | true 97.5%, false 2.5% |

**Conclusiones — Honduras:** único país donde TCL-Springserve es el líder individual (43.9%). eCPM bajo (3.88) pero con tasa de monetización mejor que la media (78.1% ceros). El fill de length más bajo del dataset (3.8%). Metadata y catálogo idénticos al patrón centroamericano.

## Paraguay — 1,827 filas (0.4%) · 0.09% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 38 | 100% | **Select Plus 54.6%**, METAX 12.9%, TCL ADs (APAC) 12.2%, iion 5.3% |
| pageURL | 34 | 100% | com.tcl.movieark 55.2%, com.tcl.browser 12.9%, com.seraphic.metaxplay 9.6%, tv.vidaa.ui.plus 6.0% |
| App Name | 24 | 92.2% | MovieArk 55.2%, BrowseHere 12.9%, Metax TV 9.6% |
| contentGenre | 183 | 93.2% | **drama 20.4%**, horror 8.3%, action 5.4%, documentary 5.0% |
| contentLanguage | 21 | 92.5% | en 70.0%, es 16.6%, pt 1.6% |
| contentRating | 34 | **37.1%** | *N/A 62.9%*, tv-g 8.9%, tv-14 7.4%, tv-ma 4.8% |
| contentCategory | 48 | 23.0% | *[-7] 77.0%*, [IAB12] 3.8%, [IAB1, IAB1-5] 3.6% |
| contentIsLiveStream | 3 | **71.9%** | 1 71.9%, *N/A 20.1%*, *Unknown 7.9%* |
| contentLength | 6 | 5.4% | *N/A 94.6%*, 5 2.1%, 6 1.9%, 1 0.8% |
| contentSeries | 9 | 2.1% | *N/A 97.9%*, VOD 0.8%, OTT Studios Sports 0.6% |
| contentTitle | 1,167 | 93.3% | *N/A 6.7%*, soul storm 0.7%, humble pie 0.5% |
| contentIsTitlePresent | 2 | — | true 93.3%, false 6.7% |

**Conclusiones — Paraguay:** muestra chica (1,827 filas) con dos récords: el **peor fill de rating** (37.1% — casi dos tercios sin clasificación, problema para brand safety) y el **mayor porcentaje de live confirmado** (71.9%). Select Plus es el único líder de mercado que no aparece primero en ningún otro país. Solo 9 valores de series. Leer con cautela por el tamaño.

## Bolivia — 1,136 filas (0.2%) · 0.04% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 31 | 100% | **Coocaa (SKYWORTH) 41.6%**, METAX 11.3%, OTTera.tv 9.9%, iion 8.2% |
| pageURL | 33 | 100% | com.coolita.channel 41.6%, com.tcl.movieark 9.2%, com.tcl.browser 7.8%, com.seraphic.metaxplay 7.0% |
| App Name | 26 | 95.4% | Coolita Channel 41.6%, MovieArk 9.2%, BrowseHere 7.8%, Metax TV 7.0% |
| contentGenre | 243 | 89.1% | *N/A 10.9%*, drama 7.6%, **animation,family,sport 6.9%**, sports 4.4%, news 4.0% |
| contentLanguage | 13 | 88.0% | en 59.1%, **pt 12.9%**, es 12.2% |
| contentRating | 34 | 79.2% | *N/A 20.8%*, tv-14 15.8%, tv-pg 13.6%, g 11.8% |
| contentCategory | 68 | **75.4%** | *[-7] 24.6%*, [IAB1] 9.7%, [IAB17] 9.6%, [IAB1-7, IAB17-12] 6.9%, [IAB12] 6.0% |
| contentIsLiveStream | 3 | 63.6% | 1 63.6%, *Unknown 21.4%* |
| contentLength | 8 | 50.7% | *N/A 49.3%*, 4 20.3%, 5 16.7%, 6 7.9% |
| contentSeries | 302 | **39.0%** | *N/A 60.9%*, The Cube USA 1.0%, J1 League 0.9%, Podpah 0.7% |
| contentTitle | 623 | 86.4% | *N/A 13.6%*, pacman 0.5%, pixel_dash 0.5%, sponge_bob_bounce 0.5% |
| contentIsTitlePresent | 2 | — | true 86.4%, false 13.6% |

**Conclusiones — Bolivia:**
- La muestra más chica (1,136 filas) y un perfil totalmente distinto: domina **Coocaa/Coolita** (Skyworth), no TCL. Y con la **mejor metadata del dataset** (category 75.4%, length 50.7%, series 39%): las apps de Skyworth mandan el content object completo.
- Pero no sirve de nada: **99.9% de filas con eCPM cero** (una sola combinación monetizó, a 1.98). Metadata perfecta sin demanda.
- Rarezas: títulos que son **juegos casuales** (pacman, sponge_bob_bounce — la app "Free Games by PlayWorks" clasificada como CTV), el género combinado `animation,family,sport`, y más portugués (12.9%) que casi cualquier país hispano por catálogo brasileño (Podpah).

## Nicaragua — 1,513 filas (0.3%) · 0.03% de los requests

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 42 | 100% | Coocaa 26.3%, TCL ADs (APAC) 18.1%, OTTera.tv 12.5%, METAX 6.9% |
| pageURL | 48 | 100% | com.coolita.channel 26.3%, com.tcl.livetv 17.2%, com.tcl.movieark 11.6% |
| App Name | 45 | 89.1% | Coolita 26.3%, Live TV 17.2%, MovieArk 11.6%, *N/A 10.9%* |
| contentGenre | 275 | 94.0% | drama 10.7%, sports 5.1%, animation,family,sport 4.8%, news 4.0% |
| contentLanguage | 13 | 92.7% | en 61.7%, es 16.7%, pt 9.1% |
| contentRating | 38 | 89.7% | tv-14 20.9%, tv-ma 12.8%, g 10.1%, tv-pg 8.8% |
| contentCategory | 68 | 56.6% | *[-7] 43.4%*, [IAB12] 6.9%, [sports] 6.5%, [IAB17] 5.7% |
| contentIsLiveStream | 3 | 42.7% | 1 42.7%, *Unknown 35.8%* |
| contentLength | 8 | 37.0% | *N/A 63.0%*, 4 13.9%, 5 11.8%, 6 7.1% |
| contentSeries | 265 | 31.3% | *N/A 68.7%*, OTT Studios Ent. On Demand 2.2%, OTT Studios Sports 1.5% |
| contentTitle | 675 | 91.6% | *N/A 8.4%*, catalunya über alles! 1.1%, humble pie 0.9% |
| contentIsTitlePresent | 2 | — | true 91.6%, false 8.4% |

**Conclusiones — Nicaragua:** el mercado más chico en tráfico (0.03%) pero con señales sorprendentemente buenas: segunda mejor metadata (category 56.6%, series 31.3% — otra vez el efecto Coocaa/Coolita) y buena tasa de monetización (70.7% ceros) con precio alto cuando paga (7.77 ponderado, aunque sobre poquísimas filas). Mismo perfil que Bolivia: OEM Skyworth + catálogo mixto con portugués.

---

# Síntesis transversal

1. **La metadata depende del publisher, no del país.** Los fills por país se explican casi por completo por el mix de sellers: donde domina TCL (Argentina, Chile) la categoría y la duración desaparecen; donde pesa Roku (Puerto Rico, México en volumen) aparecen categoría/duración pero se ocultan títulos y series; donde pesa Coocaa/Coolita (Bolivia, Nicaragua) el content object llega casi completo. Las correcciones hay que negociarlas con 4-5 integraciones, no con 18 países.
2. **Calidad de señal y monetización no van de la mano por país.** Venezuela y Bolivia tienen metadata sobre la media y monetización nula (ahí el bloqueo es de demanda); Chile tiene metadata pobre y el mejor precio. La correlación metadata→eCPM que sí existe a nivel de fila (parte 1) opera dentro de cada mercado, no entre mercados.
3. **El catálogo de relleno es el mismo en todos lados**: las películas B de OTT Studios ("catalunya über alles!", "haus of horror", "the baddest bad boy" y sus trailers) aparecen en el top de títulos de 15 de los 18 países. La "variedad" aparente del dataset es en gran parte un único catálogo replicado.
4. **Prioridades de limpieza con mayor retorno:** (a) normalizar ratings (~180 valores → 5 niveles; desbloquea brand safety en el 87% del tráfico); (b) reclamar el fix de `content.cat` = `[-7]` al ecosistema TCL/OEM (recuperaría categoría en ~70% del tráfico); (c) mapear bundles→servicio para consolidar ViX/Tubi/Plex; (d) confirmar la tabla de buckets de contentLength con el proveedor del reporte antes de usarla.

