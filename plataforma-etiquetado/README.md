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

Pestaña *Deals* (solo admin). Se elige país, género y/o categoría y compara, sobre el corte vigente, lo
que alcanzan los **filtros nativos de PubMatic** (solo lo que el publisher declara) contra **nuestra
recomendación**: una regla `Title is [lista]` con los títulos que la base enriquecida clasifica así.
Muestra requests, % vendido y eCPM histórico de cada camino, por publisher y por título. Desde ahí se
descarga el CSV de títulos o se crea el deal en PubMatic.

- **Datos**: `data/deals.db` (~40 MB), que genera `scripts/exportar_deals_db.py` desde el relleno y el
  corte de cada tanda (`scripts/correr_tanda.py --deals` lo genera y lo sube a la VM si el `.env` de la
  raíz trae `DEALS_DESTINO` y `DEALS_LLAVE_SSH`). El servidor lo relee solo cuando cambia; sin el archivo
  la pestaña avisa que no hay datos.
- **Crear en PubMatic**: un bot (Playwright, Chromium sin ventana dentro del contenedor) inicia sesión con
  la cuenta de `.env` (ver `.env.example`), llena el asistente de Auction Package Deal (DSP y buyer del
  `.env`, video en CTV, países, CSV de títulos; sin fee, First Price, piso por defecto), lo crea y **lo
  pausa enseguida**, porque en PubMatic un deal nace Live. La web devuelve el enlace al deal.
- Las creaciones se encolan (todos usan la misma cuenta) y quedan en la tabla `deals_trabajos`. Si un
  deal se crea y no se logra pausar, queda marcado «SIN PAUSAR»: hay que pausarlo a mano en PubMatic.
- `DEALS_ENSAYO=1` hace que el bot recorra todo y se detenga en el resumen, sin crear nada.
- Límites de PubMatic que respeta: 10,000 valores por deal y 500 KB por CSV. Dos reglas de contenido se
  unen con AND, por eso la recomendación va sola en su deal y no junto al filtro nativo.

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
