# Plataforma de etiquetado del relleno (etiquetas-ctv)

Reemplaza la página autocontenida `reportes/25-auditoria-relleno-v22/recursos/revision-manual-v22.html`.
Misma tarjeta de revisión (campos llenados en naranja, un veredicto por valor, pregunta opcional de la
ficha IMDb), pero con base de datos, login y etiquetas guardadas por usuario.

En producción: **https://etiquetas-ctv.tricarro.com** (proxy host en Nginx Proxy Manager → contenedor
`etiquetas-ctv:3000` en `app-network`).

## Qué hay

| Parte | Tecnología | Dónde |
|---|---|---|
| API + estáticos | TypeScript, Hono, better-sqlite3 | `server/src/index.ts` |
| Lógica de campos/unidades/significados | port de `scripts/generar_muestra_revision.py` | `server/src/registros.ts`, `significados.ts` |
| Importador CSV → SQLite | TypeScript, csv-parse | `server/src/importar.ts` |
| Usuarios (CLI) | scrypt, sesiones en cookie httpOnly | `server/src/usuarios.ts` |
| Front | Svelte 5 (runes) + Vite + TS | `web/src` |
| Armador de deals (pestaña *Deals*) | consultas sobre `deals.db` + bot Playwright | `server/src/deals.ts`, `pubmatic.ts`, `web/src/lib/Deals.svelte` |
| Taxonomías IAB 1.0 / 2.2 / 3.0 | TSV oficiales del IAB Tech Lab | `iab/` |

La base (`data/etiquetas.db`, ~560 MB, no se versiona) tiene:

- `filas`: las 1,344,629 filas de `inventory-consolidado-v10-a-v22-relleno.csv`, todas las columnas, más
  `titulo` (legible), `n_unidades` (valores llenados a juzgar), `en_muestra` y `muestra_id`.
- `muestra`: los 500 registros de `revision-manual-v22.json` (con su información de IMDb/Wikidata),
  cada uno ubicado en su fila del CSV. Las filas de la muestra tienen `en_muestra = 1`.
- `usuarios`, `sesiones`, `etiquetas` (un veredicto por usuario × fila × campo × valor), `notas`.

## Roles

- **admin**: pestañas *Muestra*, *Datos completos* (las 1.3 M filas, con filtros por campo, método de
  relleno, país y búsqueda) y *Resultados* (avance por usuario, precisión por estrato con IC de Wilson
  y descarga del JSON).
- **revisor**: solo la muestra. La API rechaza (403) cualquier lectura o escritura fuera de ella.

El JSON de la muestra que se descarga en *Resultados* tiene el formato que exportaba la página
anterior, así que `scripts/calcular_precision_revision.py` lo lee sin cambios.

## Armador de deals

Pestaña *Deals* (solo admin). Se elige país y los content objects del reporte y compara, sobre el corte vigente, lo
que alcanzan los **filtros nativos de PubMatic** (solo lo que el publisher declara) contra **nuestra
recomendación**: eso mismo más una regla `Title is [lista]` con los títulos que la base enriquecida
clasifica así (la unión de los dos; lo que viene sin título solo lo alcanzan los filtros nativos).
Muestra requests, % vendido y eCPM histórico de cada camino, por publisher y por título. Desde ahí se
descarga el CSV de títulos o se crea el deal en PubMatic.

- **Content objects del reporte** (cambian los números): género, categoría IAB, serie, clasificación, duración
  (el código 1-8 del reporte) y en vivo entran en la recomendación también por la lista de títulos, aunque el
  publisher no los declare. El idioma y «trae título» solo valen como vienen (el idioma nunca se rellena):
  filtran igual en los dos caminos, y el idioma va además al deal como señal (`Language`, categoría
  estandarizada de PubMatic). «Título contiene» busca en el título que manda el publisher.
- **Señales que solo existen en PubMatic** (no cambian los números; solo van al deal): canal, cadena,
  temporada, episodio, palabras clave, productora y su dominio, ID, calificación de usuarios, calidad de
  producción, tipo de contenido, clasificación IQG, relación con la fuente y si se puede incrustar. En
  PubMatic todas son texto libre con operador `is`, `contains` o `is any`; las que son códigos de OpenRTB se
  ofrecen aquí como lista. Como el reporte no las trae, el deal real alcanza menos de lo que muestra la
  comparación.
- **Datos**: `data/deals.db` (~60 MB), que genera `scripts/exportar_deals_db.py` desde el relleno y el
  corte de cada tanda (`scripts/correr_tanda.py --deals` lo genera y lo sube a la VM si el `.env` de la
  raíz trae `DEALS_DESTINO` y `DEALS_LLAVE_SSH`). El servidor lo relee solo cuando cambia; sin el archivo
  la pestaña avisa que no hay datos.
- **Crear en PubMatic**: un bot (Playwright, Chromium sin ventana dentro del contenedor) inicia sesión con
  la cuenta de `.env` (ver `.env.example`), llena el asistente de Auction Package Deal (DSP y buyer del
  `.env`, video en CTV, países, CSV de títulos), lo crea y **lo pausa enseguida**, porque en PubMatic un
  deal nace Live. La web devuelve el enlace al deal.
- **Condiciones del deal** (se llenan en la sección 3 y el bot las pone tal cual en el paso Configuration):
  Transaction Date (desde / hasta, o sin fecha de fin), Transaction Fee (no, o sí con CPM Fixed en USD o
  Percentage) y Auction Type con su Media CPM (Fixed Price: obligatorio; First Price: piso opcional). Por
  defecto: sin fee, First Price, piso de PubMatic, desde hoy y sin fin. Las fechas se eligen en el
  calendario de PubMatic (sus campos no aceptan texto). Antes de crear, el bot comprueba que el resumen de
  PubMatic diga lo mismo que se pidió, y lo que PubMatic mostró queda guardado con el trabajo
  (`deals_trabajos.resumen_pm`). Los límites los valida PubMatic (p. ej. fee fijo máximo de $10): si rechaza
  algo, el trabajo falla con ese mensaje y no se crea nada.
- Las creaciones se encolan (todos usan la misma cuenta) y quedan en la tabla `deals_trabajos`. Si un
  deal se crea y no se logra pausar, queda marcado «SIN PAUSAR»: hay que pausarlo a mano en PubMatic.
- `DEALS_ENSAYO=1` hace que el bot recorra todo y se detenga en el resumen, sin crear nada.
- Límites de PubMatic que respeta: 10,000 valores por deal y 500 KB por CSV, y 3 señales por regla.
- **Cómo une PubMatic las reglas de contenido** (comprobado en el asistente): las señales de una misma regla
  van con AND; las reglas normales van con OR entre sí; la regla de una lista **subida por CSV** va con AND
  contra lo que sigue; y después de una categoría estandarizada no deja agregar más señales a la regla. Por
  eso el deal que crea el bot es `lista de títulos AND (señal AND señal AND idioma)`: las señales adicionales
  van todas en una segunda regla (máximo 3, el idioma cuenta y va al final). La recomendación completa
  siguen siendo dos deals: el de la lista de títulos (el que crea el bot) y otro con los filtros nativos.
- `deals.db` de una versión anterior (sin las columnas de los content objects nuevos) sigue funcionando: la
  pestaña ofrece solo género y categoría hasta que se regenere con `scripts/exportar_deals_db.py`.

## AI Deals

Segunda pestaña de deals (admin y perfil `deals`): el deal se arma a partir del brief de la campaña.

- **Entradas:** brief (texto), DSP (lista de PubMatic, `server/src/dsps.ts`), ID de la cuenta (seat ID), CPM,
  mercado (un país de los que hay en el corte; lo elige la persona, no el modelo), tipo de campaña (solo
  Connected TV), formato (solo Video) y fechas (Transaction Date: desde / hasta o sin fecha de fin, igual que
  en la pestaña Deals; el bot las pone en PubMatic y comprueba que el resumen las muestre antes de crear).
- **Content objects:** `server/src/ai.ts` le pasa al modelo (salida estructurada) el brief y el
  catálogo del corte vigente en el mercado elegido (géneros, categorías IAB, clasificaciones e idiomas con su
  peso en requests). Devuelve un plan con valores de ese catálogo: 1 a 4 géneros, y categoría, clasificación o
  idioma solo si el brief los pide, más una explicación y las palabras clave del nombre. El modelo es
  Claude (`claude-opus-5-5`, con `ANTHROPIC_API_KEY`) o `openai/gpt-oss-120b` servido por Groq (con
  `GROQ_API_KEY`, capa gratuita: 1,000 solicitudes al día y 8,000 tokens por minuto). Si están las dos
  llaves se usa Claude, salvo `AI_DEALS_PROVEEDOR=groq`.
- **CPM:** se reparte mitad y mitad: transaction fee fijo y Media CPM a precio fijo (CPM 4 = $2 + $2). Se
  admite de $1 a $20 (la puja no baja de $0.50 y PubMatic no deja un fee fijo mayor a $10).
- **Nombre:** palabras clave del brief + `ctv-video` + DSP + CPM + fecha y hora, en minúsculas con guiones.
- **En PubMatic:** el bot elige el DSP y el buyer por su seat ID (si no existe en ese DSP, falla sin crear
  nada), y aplica los content objects igual que la pestaña Deals: lista de títulos que la base clasifica así,
  más la regla de idioma. Varios valores de un mismo content object se suman (OR); entre content objects
  distintos se cruzan (AND). El deal queda en pausa.
- **Salida:** nombre del deal, ID (PM-…) y CPM. El brief y el plan quedan en `deals_trabajos`
  (`tipo = 'ai'`, `brief`, `plan`, `dsp`, `cuenta`, `cpm`).
- Rutas: `GET /api/admin/deals/ai/opciones`, `POST /api/admin/deals/ai/plan` (lee el brief, no crea nada) y
  `POST /api/admin/deals/ai/crear`.

## Despliegue

```bash
cd plataforma-etiquetado
docker compose build

# 1) importar (reemplaza filas/muestra/meta; conserva usuarios y etiquetas)
docker compose run --rm -u $(id -u):$(id -g) \
  -v /ruta/inventory-consolidado-v10-a-v22-relleno.csv:/import/relleno.csv:ro \
  -v $PWD/../reportes/25-auditoria-relleno-v22/recursos/revision-manual-v22.json:/import/muestra.json:ro \
  etiquetas-ctv node dist/importar.js /import/relleno.csv /import/muestra.json

# 2) usuarios (sin clave se genera una y se imprime una sola vez)
docker compose run --rm -u $(id -u):$(id -g) etiquetas-ctv node dist/usuarios.js crear diego.gonzalez admin "Diego Gonzalez"
docker compose run --rm -u $(id -u):$(id -g) etiquetas-ctv node dist/usuarios.js clave elizabeth.garcia   # cambiar clave
docker compose run --rm -u $(id -u):$(id -g) etiquetas-ctv node dist/usuarios.js listar
# perfil que solo ve la pestaña Deals (entra directo ahí; no ve la muestra, los datos ni los resultados)
docker compose run --rm -u $(id -u):$(id -g) etiquetas-ctv node dist/usuarios.js crear alguien@empresa.com deals "Nombre Apellido"

# 3) levantar
docker compose up -d
```

Las etiquetas apuntan a `fila_id` = posición de la fila en el CSV. Reimportar **el mismo CSV** conserva
todo; con un CSV distinto (otro corte) hay que empezar una base nueva.

## Desarrollo

```bash
# API en :3000 con una base ya importada
cd server && npm install && npm run build && DB_PATH=../data/etiquetas.db IAB_DIR=../iab PUBLIC_DIR=../web/dist node dist/index.js
# front con recarga en caliente (proxy de /api a :3000)
cd web && npm install && npm run dev
```
