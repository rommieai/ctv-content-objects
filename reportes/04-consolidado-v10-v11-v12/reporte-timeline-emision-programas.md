# Timeline de emisión de los programas anunciados en el inventario CTV (v10+v11+v12)

**Fuente de datos**: `inventory-consolidado-v10-v11-v12.csv` (539.190 filas; 489.750 con `contentTitle` útil). **Ventana de los bid requests**: 4–19 ago 2026 (v11 = 4–18 ago, v12 = 5–19 ago; v10 exportada 20 ago). Investigación web realizada el 24 ago 2026.

## Respuesta corta

1. **Sí hay relación, pero solo en dos publishers los títulos son programas con calendario real**: ViX/Televisa y Vidaa/Hisense (México). Ahí los bids coinciden con eventos concretos de TV abierta que estaban en emisión en la ventana:
   - **La Casa de los Famosos México 4** (feeds ViX "Acceso Total 24/7" y "Toda la Casa 24/7"): 26 jul → 4 oct 2026. Es el mayor volumen con título de todo el archivo (2.7B requests). El periodo gratis en ViX terminó ~9 ago, en mitad de la ventana.
   - **Survivor México 7** (Azteca): 20 jul → final 23 ago 2026.
   - **MasterChef México 15 "24/7"** (Azteca): 17 may → final 30 ago 2026.
   - **Telenovelas Las Estrellas**: *El renacer de Luna* y *Tan cerca de ti, nace el amor* terminaron el **20 ago** (último día de la ventana); *Guardián de mi vida* desde 29 jun; *La Rosa de Guadalupe* con capítulos nuevos; *Vecinos* T20/T21 desde 29 mar; *La vecina* en tlnovelas desde 5 may.
   - **Deportes**: Leagues Cup 2026 (4 ago–6 sep; fase 1 4–13 ago) y regreso de Liga MX Apertura J4 (15–17 ago) y J5 (21–23 ago) en Canal 5/TUDN.
2. **El resto del inventario (TCL Channel/MovieArk, Coolita, Metax, WhaleLive ≈ 85% de los requests con título) son canales FAST de catálogo en loop 24/7.** No tienen "fecha de emisión": el título es lo que estaba sonando en el loop cuando se generó el bid. Los eventos son de archivo (partidos 2025-26, peleas de 1989/2014, podcasts 2023-25, películas 2011-2021). Dos títulos de Coolita incluso traen la fecha en el nombre (`nice vs auxerre (08/23/25)`, `river plate vs blooming (05/27/26)`).
3. **Placeholders sin contenido**: Roku (`roku`, `run of video network`; 14.2B requests), AMC (`amc networks`), Samsung TV Plus (`[content_title]`), y `mxf01` en ViX.

## Timeline consolidado (eventos fechados)

| Fecha | Evento | Publisher / título en el CSV |
|---|---|---|
| 17 may 2026 | Estreno MasterChef México 15 (24/7) | Vidaa → `masterchef mexico` |
| 25 may / 22 jun 2026 | Estreno *Tan cerca de ti* / *El renacer de Luna* | Vidaa/ViX → `las estrellas` |
| 29 jun 2026 | Estreno *Guardián de mi vida* (21:30) | `las estrellas` |
| 20 jul 2026 | Estreno Survivor México 7 | Vidaa → `survivor mexico` |
| **26 jul 2026** | Estreno LCDLFM4; feeds 24/7 en ViX | ViX → `acceso total 24/7 con anuncios`, `toda la casa 24/7 con anuncios`, `canal 5`, `las estrellas` |
| 4 ago 2026 | Arranca Leagues Cup (pausa Liga MX hasta 13 ago) | ViX → `tudn` |
| **4–19 ago 2026** | **Ventana de bid requests** | — |
| ~9 ago 2026 | Fin del periodo gratis LCDLFM en ViX; eliminación Ximena Herrera | feeds ViX |
| 15–17 ago 2026 | Liga MX J4 (Canal 5/TUDN) | `canal 5`, `tudn` |
| 16 ago 2026 | Eliminación LCDLFM (Arantza Ruiz) | feeds ViX |
| 19 ago 2026 | Avaí 2–1 Sport (Série B R23) — único partido de Coolita dentro de la ventana (y ESPN exclusivo, luego el bid es de un clip/highlight) | Coolita → `sport x avai - série b` |
| **20 ago 2026** | Finales de *El renacer de Luna* y *Tan cerca de ti* | `las estrellas` |
| 21–23 ago 2026 | Liga MX J5 | `canal 5`, `tudn` |
| 23 ago 2026 | Final Survivor México 7; semifinal MasterChef | Vidaa |
| 24 ago 2026 | Estreno Exatlón 10 (post-ventana) | — |
| 30 ago 2026 | Final MasterChef 24/7 | Vidaa |
| 21 sep / 5 oct 2026 | Estrenos *Sabor a ti* / *Tierra de amor y coraje* (ViX 7 ago) | `las estrellas` |
| **4 oct 2026** | Final LCDLFM4 | feeds ViX |

## Lectura para el negocio (timeline detrás de los bids)

- **Cuándo se emitieron**: todo lo que tiene calendario ya estaba al aire antes de la ventana (LCDLFM desde 26 jul, Survivor desde 20 jul, MasterChef desde 17 may) y siguió después; los bids del 4–19 ago corresponden a la **mitad de temporada** de los realities y a la **recta final** de dos telenovelas.
- **Cuándo se van a emitir**: LCDLFM4 sigue hasta el 4 oct (feeds 24/7 → inventario recurrente hasta esa fecha); MasterChef hasta 30 ago; Liga MX Apertura hasta diciembre. Lo próximo que aparecerá con título nuevo: Exatlón 10 (desde 24 ago), *Sabor a ti* (21 sep), *Tierra de amor y coraje* (5 oct), remake *Guardián de mi corazón* (Amores verdaderos, sin fecha).
- **FAST de catálogo** (TCL, MovieArk, Coolita, Metax, Whale): inventario estable e independiente del calendario; se puede tratar como "always-on". Los pares `X` / `X: trailer` con ~300M requests idénticos en MovieArk son trailers interstitiales del mismo paquete de distribuidor (Level 33, Epic/DREAD) entre largometrajes en loop.
- Los VOD de telenovelas clásicas en ViX (*Lo que la vida me robó*, *Mi corazón es tuyo*, *Amores verdaderos*, *La fea más bella*…) son catálogo permanente; solo *La Rosa de Guadalupe*, *Vecinos*, *La vecina* y *True Beauty* (Canal 5 feb–mar 2026) tienen actividad de emisión 2026.

---

## ViX / TelevisaUnivision (México 23.4B req; 99% MX)

**Feeds lineales**
| Título | Qué es | Timeline |
|---|---|---|
| acceso total 24/7 con anuncios | Feed oficial 24/7 de **La Casa de los Famosos México T4** (versión AVOD gratuita) | Estreno **26 jul 2026**; galas L–V 22:00 Canal 5, dom 20:30 Las Estrellas; 10 semanas → final **4 oct 2026**. Eliminaciones en ventana: 9 ago (Ximena Herrera), 16 ago (Arantza Ruiz). Periodo "todo gratis" en ViX terminó ~9 ago (explica cambios de volumen en 4–19 ago) |
| toda la casa 24/7 con anuncios | Segundo feed 24/7 de LCDLFM4 (todas las áreas) | Ídem |
| las estrellas | Canal 2 Televisa | Ago 2026: galas LCDLFM dom 20:30; La Rosa de Guadalupe L–V 19:30; telenovelas 2026 (Mi rival, Doménica Montero, Hermanas, Somos familia); Vecinos T20/T21 dom 19:30 |
| canal 5 | XHGC | Galas LCDLFM L–V 22:00; Liga MX Apertura 2026 J4 (15–17 ago) y J5 (21–23 ago); pausa Liga MX 4–13 ago por Leagues Cup |
| tudn | TUDN | Leagues Cup 2026 (4 ago–6 sep; fase 1 4–13 ago, solo partidos puntuales p.ej. América–San Diego 6 ago); Liga MX J4/J5 |
| n foro | N+ Foro (noticias 24/7) | Sin evento especial |
| mxf01 | ID interno de feed | Sin resultado |

**VOD (catálogo ViX)**
| Título | Emisión original | Evidencia jul–ago 2026 |
|---|---|---|
| lo que la vida me robó | Las Estrellas oct 2013–jul 2014 | Solo catálogo ViX (189 caps gratis). Última retransmisión MX jul 2024; Univision USA desde 1 sep 2025 |
| mi corazón es tuyo | Las Estrellas jun 2014–mar 2015 | Retransmisión tlnovelas MX desde 5 ene 2026; Univision tlnovelas 13 oct 2025–16 jun 2026 |
| amores verdaderos | Las Estrellas sep 2012–may 2013 | Remake "Guardián de mi corazón" anunciado 2026 ("próximamente" Las Estrellas/ViX) |
| la fea más bella | 2006–2007 | Última retransmisión Las Estrellas desde 10 mar 2025. Sin evidencia 2026 |
| destilando amor | 2007 | Última retransmisión 2024. Sin evidencia 2026 |
| corazón indomable | 2013 | Sin evidencia 2026 |
| la rosa de guadalupe | desde 2008, en producción | **Capítulos nuevos 2026**, L–V 19:30 Las Estrellas; subidos semanalmente a ViX → explica VOD alto |
| rubí 2005 | 2004 | Sin evidencia específica 2026 (listada como clásico tlnovelas 2026 sin fecha) |
| la familia p. luche | 2002–2012 | Solo catálogo; rumor reboot (29 may 2026) |
| la vecina | 2015–2016 | **Retransmisión activa tlnovelas MX desde 5 may 2026** (confirmada parrilla 10 ago 2026) |
| nosotros los guapos | 2016–2020 | Solo catálogo |
| soy tu dueña | 2010 | Solo catálogo |
| true beauty | K-drama tvN 2020–21 (doblado, en ViX desde 14 ago 2024) | Canal 5 lo emitió 9 feb–12 mar 2026 |
| vecinos | desde 2005 | **T20 en ViX 27 feb 2026, Las Estrellas desde 29 mar 2026, seguida de T21** → en emisión en ventana |

Fuentes: lacasadelosfamososmexico.tv/en-vivo-nomx; en.wikipedia.org/wiki/La_casa_de_los_famosos_México_season_4; milenio.com (fecha final); nmas.com.mx (gratis en ViX hasta 9 ago); gatotv.com/canal/5_mexico/2026-08-15; infobae.com (Leagues Cup 4 ago 2026); vix.com/es-es/detail/series-654; televisa.com/tlnovelas (La vecina); corporate.televisaunivision.com/press/2026/03/26 (Vecinos); celebriteen.com.mx (True Beauty).

## Vidaa (Hisense) / AWG Media — MX 5.5B (≈96% MX)

**Con fechas concretas en la ventana**
| Título | Qué es | Timeline |
|---|---|---|
| survivor mexico | Reality TV Azteca (Azteca Uno), T7 "La Reliquia en Llamas"; en bid requests probablemente el live/simulcast | **Estreno 20 jul 2026** L–V 18:30; **gran final dom 23 ago 2026** 18:00. Le sigue Exatlón 10 (24 ago) |
| masterchef mexico | Reality TV Azteca, T15 formato "MasterChef 24/7" | **Estreno 17 may 2026**; L–V 20:30 + dom 20:00; semifinal 23 ago; **gran final dom 30 ago 2026** |
| las estrellas | Señal lineal Canal 2 | L–V ago 2026: *El renacer de Luna* 18:30 (22 jun → **final 20 ago**), *Tan cerca de ti, nace el amor* 20:30 (25 may → **final 20 ago**), *Guardián de mi vida* 21:30 (desde 29 jun), La Rosa de Guadalupe 19:30, repeticiones Rubí 17:30 y Destilando amor 16:30; LCDLFM4 galas. Próximos: *Sabor a ti* 21 sep, *Tierra de amor y coraje* (ViX 7 ago; TV 5 oct) |

**Canales FAST / lineales (loop 24/7, sin estrenos fechados)**
| Título | Qué es | Operador |
|---|---|---|
| cine de oro, jajaja, grandes parejas, las 3 marías, galanes, como dice el dicho, rebelde / rebelde hd, pequeños gigantes, porque el amor manda, amor real, la que no podía amar, hasta que el dinero nos separe, fuego en la sangre, 40 y 20, distrito comedia, canal 5, n foro | Canales FAST de ViX (13 en VIDAA desde oct 2023) + single-title de telenovelas/sitcoms | TelevisaUnivision/ViX |
| canal 6 cdmx / monterrey / guadalajara, milenio, telediario now | Señales Multimedios (Canal 6 local, Milenio TV noticias 24/7, Telediario Now rota ediciones locales) | Grupo Multimedios |
| dw español, dw english, france 24, rcn noticias, rcn más | Noticias 24/7 | DW / FMM / RCN (Colombia) |
| teenvee spanish / teenvee | FAST juvenil | TheSoul Publishing |
| latinocircuit tv | FAST cine indie latino (lanzado ago 2025) | DFEZ / FAST Channels TV |
| panic tv | FAST terror | Cape May Studios / Amagi |
| cine friki latino | FAST acción/sci-fi | n/i (canal español) |
| pilotos del ártico / la fiebre del jade | Single-IP de *Ice Pilots NWT* / *Jade Fever* (Omnifilm) | n/i |
| daystar español, red bull tv | Religioso / deportes-música | Daystar / Red Bull |
| amour, acelerados, cindie tv, glitchplus, dude perfect, cirque du soleil | No verificados como canales FAST | — |

**VOD cine videohome mexicano** (loop de catálogo, sin canal identificado; coincide con catálogo AVOD ViX): el hijo de simón blanco (2001), la noche del halcón (1968), coyotes de la frontera (2013), el plebe chakaloso (2010), el as de oro (2012), los hermanos fierro (2012), estrategia de escape (2016, estudio ViX), los bravos de guerrero (2006).

**Ottera vía Kivi**: descendientes del sol = *Descendants of the Sun* (KBS2 2016); el peso del amor = *Oh My Venus* (KBS2 2015–16). K-dramas doblados en catálogo; "Kivi" no identificado (cliente white-label OTTera).

Fuentes: tvazteca.com (Survivor estreno; MasterChef final); publimetro.com.mx 2026/08/11 (final Survivor); milenio.com (MasterChef 24/7); excelsior.com.mx (semifinal 23 ago); en.wikipedia.org El_renacer_de_Luna / Tan_cerca_de_ti / Guardián_de_mi_vida; corporate.televisaunivision.com/press/2023/10/30 (ViX–VIDAA 13 canales); digitaltv.prensariozone.com/multimedios; canela.tv/channel/telediario-now; advanced-television.com 2025/08/19 (LatinoCircuit); vix.com/es-es/canales.

## TCL Channel / MovieArk / Live TV / BrowseHere (OTTera, TCL Ads, iion, PML, Select Plus) — MX 98.7B, AR 49.5B, CL 20.3B, CO 20.1B

**Estructura (lo relevante para el timeline)**
- MovieArk es app de TCL (`com.tcl.movieark`, publisher "FALCON GLOBAL TECH", build TCL.2026051911 del 19 may 2026): "3.000+ películas, 200+ canales en vivo con EPG". BrowseHere también es de TCL. MovieArk y TCL Channel comparten canales (alemdatela.com, 14 nov 2025).
- TCL Channel LATAM: arrancó en Brasil ago 2024 (~200 canales); Atresmedia desde abr 2025; jul 2026 sumó BandNews, Goat TV, Rede Vida, Sessão Trash (telaviva.com.br 03/07/2026).
- **No hay EPG público ni prensa que fije la programación por título en ago 2026.** El "timeline" real es: loops de catálogo 24/7 durante toda la ventana.
- Los títulos MovieArk se agrupan en **dos bloques de distribuidor** → uno o dos canales FAST licenciados en paquete:
  - **Level 33 Entertainment**: Corona (2020), Rollers (2021), Eve (2020), Penance Lane (2020), Companion (2021), American Apocalypse (2018), La Flamme Rouge = Hide and Bleed (2021), Brooklyn Love Stories (2019), Beast No More (2019), Ovid and the Art of Love (2019).
  - **Epic Pictures / DREAD** (canal DreadTV, vendido a Be Afraid Media ene 2026 con distribución multianual Epic): Doors (2021), Mark of the Witch (2014), Uncle Peckerhead (2020), Transference (2020), Big Ass Spider! (2013), The Dark Tapes (2017), Chronic Horror (serie Dread Central), Tainted (2020), The Winter Lake (2020), Killer Party (2016), Torpedo: U-235 (2019), Curse of Audrey Earnshaw (2020), Howling Village (2019), Nail in the Coffin: Vampiro (2019), Space Dogs 3 (2020), Dread the Unsolved (serie 2018–).
  - Cineverse / Dark Matter TV: Haus of Horror (2020), The Baddest Bad Boy (2020), Entrepreneur TV (canal FAST 2022, ya en TCL Channel).
- Pares "X" + "X: trailer" con ~300M requests cada uno = trailers interstitiales del mismo paquete entre largometrajes en loop (pod breaks uniformes).

**TCL Channel (títulos sueltos)**: BabyBus Canciones Infantiles "T8" (etiquetado del proveedor), Two Heartbeats (film 1972), CGTN Documentary (canal lineal 24/7, FAST global desde 2023), 5 Souls (2011), Zoobabu (BRB 2010–22), Catalunya über alles! (2011), Bluff (2022 UK), A Short Documentary About People Fighting (2019), The Next Dance (2014), The Pinnacle of Rush (doc speedriding), Chicken Stew "S7" (Fantawild 2009–11), O Último Duende (=The Last Leprechaun 1998; título PT → feed Brasil), The Garfield Show (2008–16), Animacars S2, Drive Thru History S6 (2020, TBN), Real Stories with Christ S3. Ninguno con fecha de emisión en TCL Channel 2026.

Fuentes: play.google.com/store/apps/dev?id=8205295586766089949; apkpure.com/movieark-freestream-movies/com.tcl.movieark; alemdatela.com/tcl-channel-e-movieark-recebem-novos-canais/; telaviva.com.br/03/07/2026/tcl-channel-adiciona-bandnews...; cveintiuno.com (TCL Brasil); variety.com/2026/film/news/be-afraid-media-launches-acquisition-dread-central-1236624749/; epic-pictures.com/film/*; mediaplaynews.com (Level 33).

## Coolita Channel (Coocaa/Skyworth; SSPs Coocaa + Xapads) — AR 10.2B, MX 2.9B, CL 2.2B, CO 2.2B (no Brasil pese al contenido en portugués)

**Estructura**: Coolita Channel = app FAST de COOLITA TECHNOLOGY PTE. LTD. (Singapur, Skyworth), "400+ FAST channels", v3.0.1 del 03 ago 2026; agrega canales de terceros vía NetRange/ACCESS Europe. No hay lineup público LATAM ni evidencia de CazéTV/Podpah en Coolita. Por propietario del contenido, los canales probables son: **Canal GOAT** (SPL, Bundesliga, J-League, serie GOATS), **Flow** (Portas Abertas, Kritikê), **Desimpedidos**, **Motorvision** (Put Your Car on TV), **Films & Stars**, **MLW** (Azteca Lucha), Podpah (YouTube).

**Conclusión: casi todo es archivo en loop, no directo.** Dos títulos ya traen la fecha (`08/23/25`, `05/27/26`); varios partidos son imposibles en vivo en la ventana (St Pauli descendió, Ittihad–Neom se juega el 5 nov 2026).

| Título | Fecha original del evento/episodio | Canal probable |
|---|---|---|
| sport x avaí - série b | Avaí 2–1 Sport **19 ago 2026** (R23, ESPN) — único dentro de la ventana; ida sin fecha hallada | ESPN/archivo |
| goiás x cuiabá - série b | Cuiabá x Goiás 22 ago 2026 (posterior); ida 1er turno sin fecha | archivo |
| brighton x manchester city | 31 ago 2025 / 7 ene 2026; el de 23 ago 2026 es posterior | CazéTV/ESPN (archivo) |
| al ittihad x neom - saudi pro league | 31 dic 2025 (Neom 1–3) / vuelta 2026; próximo 5 nov 2026 | Canal GOAT |
| al nassr x al najma | 25 feb 2026 (5–0); Al Najma descendió | Canal GOAT |
| nagoya grampus x avispa fukuoka | 6 dic 2025 / 7 mar 2026 (1–5) | Canal GOAT |
| mito hollyhock x kashima antlers | 4 abr 2026 (1–1, pen.) / 6 may 2026 | Canal GOAT |
| urawa red diamonds x tokyo verdy | 2025/26 (próximo 19 sep 2026) | Canal GOAT |
| st pauli x colonia - bundesliga | 6 dic 2025 / 17 abr 2026 (1–1) | Canal GOAT/OneFootball |
| darmstadt 98 x elversberg (2.BL) | 2 ago 2025 (4–1) / 14 sep 2025 | Canal GOAT/OneFootball |
| osnabrück x verl (3. Liga) | 9 ago 2025 (2–2) / 30 nov 2025 | archivo |
| nice vs auxerre (08/23/25) | 23 ago 2025 (3–1) | archivo Ligue 1 |
| river plate vs blooming (05/27/26) | 27 may 2026 (3–0, Copa Sudamericana) | archivo |
| evander holyfield vs michael dokes | 11 mar 1989 | boxeo clásico |
| floyd mayweather vs marcos maidana | 3 may 2014 / 13 sep 2014 | boxeo clásico |
| azteca lucha - místico vs templario vs ikuro kwon | 10 may 2025 (MLW) | MLW FAST |
| endrick x luis guilherme shoot out | ~2022 | Desimpedidos |
| films & stars | Serie 2008–2019 (canal FAST de cine) | Films & Stars |
| put your car on tv | 2013 | Motorvision TV |
| salsichão atômico com matheus canella (Rango Brabo #16) | 21 mar 2023 | Podpah |
| cozinhando macarrão parafuso com mc carol (Rango Brabo #28) | 13 jun 2023 | Podpah |
| 10 mulheres vs mc tuto - podpaquera #2 | 20 oct 2024 | Podpah |
| martina vs 10 nerds - podpaquera #11 | 3 jun 2025 | Podpah |
| aqueles caras - podpah #834 | 18 oct 2024 | Podpah |
| de mala e cuia em joão pessoa / manaus (Rumo ao Hexa) | 5 may 2026 / ~3 may 2026 | PodpahTV |
| a copa méxico não vai ser como você imagina (Visitantes) | 1 may 2026 | PodpahTV + PELEJA |
| é por isso que futebol e gangsta rap… (Visitantes LA) | 8 may 2026 | PodpahTV + PELEJA |
| mari nolasco - venus podcast #584 | 15 jul 2024 | Venus Podcast |
| igor 3k - portas abertas #09 | 25 jul 2023 | Flow |
| rogério vilela - portas abertas #16 | 13 sep 2023 | Flow |
| luiz felipe pondé - kritikê #318 | 22 mar 2024 | Flow |
| goats - nelsinho baptista (#7) / cicinho (#5) | 11 sep 2025 / 28 ago 2025 | Canal GOAT |

Fuentes: apkpure.com/coolita-channel; broadbandtvnews.com 2024/10/30 (ACCESS–Coocaa); news.samsung.com/br (Canal GOAT); telaviva.com.br 09/06/2026 (CazéTV en LG); gazetaesportiva.com (Série B R23/R24); espn.com / fotmob.com / sofascore.com (fixtures); api.openligadb.de (2.BL/3.Liga 2025); en.wikipedia.org (Holyfield, Mayweather–Maidana, Azteca Lucha, CazéTV); YouTube/Spotify (episodios Podpah, Flow, GOAT).

## Metax TV / WhaleLive (Zeasn) / Samsung TV Plus MX / Roku / AMC

| Título | Qué es | Timeline |
|---|---|---|
| kung fu (Metax) | Canal FAST "Kung Fu Movies" (cine artes marciales 70s/80s) de FAST Channels TV (SotalCloud, Toronto); paquete de 180 canales integrado en MetaX en jun 2022 | Lineal 24/7 de catálogo, sin fechas |
| cgtn english / cctv4 americas (Metax) | Canales de noticias/generalistas de China Media Group | Lineal 24/7 |
| africanews / euronews (Metax) | Canales de noticias Euronews | Lineal 24/7 |
| best action tv, mango tv ancient romance drama (Metax) | Canales temáticos (acción; dramas chinos de época de Mango TV) | Lineal 24/7 |
| cinemás, shift, space series (Metax) | No encontrados | — |
| WhaleLive (Zeasn/Whale TV): buffalo air, flowers and relax, calm rain, snow, *_tube, play_ibiza… | Whale TV+ (ex rlaxx TV) — canales O&O ambientales/relax; los `_tube` parecen IDs internos. "theperfecthumandiet" = documental 2012 (asset VOD). "play_ibiza" = canal Play Ibiza. "buffalo air" no encontrado | Lineal 24/7; sin fechas |
| Samsung TV Plus MX: the european debrief, global week-end | Programas de Euronews (en Español): Debrief diario (~15:00 UK), Global Week-end vie noche–dom | Emitidos toda la ventana (parrilla vigente ago 2026) |
| Samsung TV Plus MX: bloomberg tv | Canal Bloomberg TV, en Samsung TV Plus MX desde lanzamiento | Lineal 24/7 |
| Roku: roku / run of video network | Placeholders run-of-network; no es contenido | N/A |
| AMC: amc networks / amcn | Nombre del vendedor (AMC Global Media, 40+ canales FAST), no del canal | N/A |

Fuentes: metaxsoft.com/ott; streamingmedia.com (MetaX + FAST Channels TV 2022); advanced-television.com/2023/01/24 (Kung Fu Movies); whaletv.com/news/zeasn-is-now-whale-tv; tvguide.co.uk (European Debrief / Global Weekend); news.samsung.com/mx (lanzamiento TV Plus MX); experienceleague.adobe.com (Roku inventory); philo.com/blog (AMC FAST).

## Limitaciones
- No existe EPG público de TCL Channel, MovieArk, Coolita, Metax ni WhaleLive; la programación hora a hora de la ventana no es reconstruible desde la web. Para eso haría falta el EPG del publisher o el campo `content.episode`/`content.livestream` con timestamp en el bid stream.
- No se localizó lista oficial de canales FAST de Vidaa México 2026 (v-home.com solo dice "hasta 100 canales por país"); la asignación de canales se basa en el acuerdo ViX–VIDAA (oct 2023) y en comunicados de Multimedios/otros.
- Sin verificar: `amour`, `acelerados`, `cindie tv`, `glitchplus`, `buffalo air`, `cinemás`, `shift`, `space series`, `mxf01`, app "Kivi".
- El CSV no trae fecha por fila; la ventana se deduce de los nombres de archivo v11/v12.
