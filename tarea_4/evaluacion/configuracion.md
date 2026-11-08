# Configuración del experimento (Parte 4)

Script: `evaluacion/evaluar.py`. Cada pregunta corre con `claude -p`, con el mismo modelo (`sonnet`), la misma
instrucción y una sesión independiente (`--no-session-persistence`). Las preguntas se ejecutan una por una
(`--paralelo 1`) para que los tiempos sean comparables.

## Ajuste posterior al piloto

El piloto (q01 y q05 en los dos modos, `evaluacion/resultados_prueba.csv`, que se conserva como evidencia) mostró que
en q05 el modo B respondió de memoria sin usar herramientas. Por eso se agregó a la instrucción común, idéntica en
los dos modos, la frase: «Si tienes herramientas disponibles, úsalas para obtener y verificar la cifra; no respondas
de memoria si puedes consultarla.» El piloto se corrió con la instrucción anterior, sin esa frase.
No se modificó ninguna pregunta ni ninguna respuesta esperada.

## Qué tiene habilitado cada modo

| | Modo A (sin MCP ni Skills) | Modo B (con MCP y Skills) |
|---|---|---|
| Herramientas de Claude Code | ninguna (`--tools ""`) | `Skill`, `Read`, `Bash` |
| MCP | ninguno (`--strict-mcp-config` sin `--mcp-config`) | solo `bcrp` (`evaluacion/mcp_bcrp.json`) |
| Skills | desactivadas (`--disable-slash-commands`) | las tres del proyecto (`.claude/skills/`) |
| WebSearch / WebFetch | no | no |
| Servidor `fetch` del `.mcp.json` | no | no: `mcp_bcrp.json` solo declara `bcrp` |
| Permisos | no aplican, no hay herramientas | `mcp__bcrp`, `Skill`, `Read`, `Bash(uv run:*)` |
| Lectura prohibida | no aplica | `Read` denegado en `evaluacion/`, `preguntas.csv`, `referencias/`, `evidencias_ia/` |
| Directorio de trabajo | directorio temporal vacío fuera del repo | raíz del proyecto (`tarea_4/`) |

La columna `disponibles` de `resultados.csv` guarda la lista de herramientas que Claude Code reporta al iniciar cada
sesión (evento `init` del stream). Así queda comprobado y no solo declarado.

## Cómo se garantiza que el modo A no accede a archivos con respuestas

1. **No tiene herramientas.** Con `--tools ""` no puede leer archivos, ejecutar comandos ni navegar. Lo único que
   puede hacer es responder desde su memoria.
2. **No tiene MCP.** `--strict-mcp-config` sin `--mcp-config` ignora el `.mcp.json` del proyecto y cualquier otro MCP,
   incluido `fetch`.
3. **No tiene Skills.** `--disable-slash-commands` desactiva skills y comandos.
4. **Corre en un directorio vacío fuera del repositorio**, por lo que no carga el `.claude/` ni la configuración
   de este proyecto, aunque tuviera herramientas. Esto evita que vea `salidas/`, `figuras/`, `informes/`, ni
   `evaluacion/preguntas.csv`.

## Límites que hay que declarar

- **Modo B puede leer `salidas/`, `figuras/` e `informes/`**, donde están resultados ya calculados. No se bloquearon
  porque las skills escriben y leen ahí (`salidas/personas_2024.parquet`, `salidas/indicadores.csv`). Se bloquea la
  lectura con `Read` de las rutas con las respuestas esperadas (`evaluacion/`, `preguntas.csv`, `referencias/`,
  `evidencias_ia/`).
- **`Bash` no se puede restringir por ruta con fiabilidad** (solo se permite `uv run`, pero un script podría leer
  cualquier archivo). Por eso `resultados.csv` registra `accesos_sospechosos`: toda llamada a una herramienta cuyo
  argumento mencione `evaluacion`, `preguntas.csv`, `referencias` o `evidencias_ia`. Se revisa antes de analizar.
- **Las herramientas usadas se leen del stream** (`--output-format stream-json --verbose`), contando los bloques
  `tool_use`. `StructuredOutput`, que Claude Code usa para entregar el JSON, no se cuenta.
- **Llamada a `Grep` sin resolver.** En q10 del modo B, `herramientas_usadas` registra un `Grep x1`, aunque `Grep` no
  estaba habilitado (`disponibles` no lo lista). No se sabe si la llamada se ejecutó o fue rechazada: el stream de la
  corrida original no se guardó (`--no-session-persistence`, y `evaluar.py` solo conserva el resumen). Se intentó
  repetir q10 en modo B guardando el stream, pero la repetición se trabó y se detuvo sin resultado. Queda como
  limitación sin resolver. `resultados.csv` conserva la corrida original sin cambios.
- **Memoria del modelo.** En la prueba corta, el modo A respondió q05 (pobreza nacional 2024, 27.6 %) de memoria y
  acertó. Las cifras de la ENAHO publicadas antes del corte de conocimiento pueden salir correctas sin herramientas.
  No se cambian las preguntas por esto, porque la verdad y las preguntas no se modifican tras ver resultados.
  Se discutirá en `comparacion.md`.
- **Autocalificación parcial.** El script califica solo la exactitud de las cifras (y el mes en q09). La coherencia y
  el `resultado_final` de q09 y q10 se completan a mano según `evaluacion/criterios.md`.

## Calificación automática

- `acierta`: todas las cifras dentro de su tolerancia (en q09, también el mes).
- `se equivoca`: alguna cifra fuera de tolerancia o con otra cantidad de cifras.
- `no sabe`: todas las cifras `null`.
- `error`: la llamada falló o no devolvió salida estructurada.
