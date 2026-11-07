# Referencia: limpiando-enaho

## Archivos de entrada

| Zip | `.dta` que se usa | Una fila por | Filas | Factor |
|---|---|---|---|---|
| `966-Modulo34.zip` | `sumaria-2024.dta` | hogar | 33,691 | `factor07` (× `mieperho` = personas) |
| `966-Modulo02.zip` | `enaho01-2024-200.dta` | persona | 117,721 | `facpob07` |

El zip del módulo 34 trae también `sumaria-2024-12g.dta` (242 columnas, más grupos de gasto). Da el mismo
`pobreza` y no se usa. Los zip traen además PDFs y tablas de ocupaciones que se ignoran.

## Trampas

- `facpob07` está en personas, no en la sumaria; la sumaria trae `factor07`.
- `ubigeo` y `estrato` existen en ambas bases: de la sumaria solo se traen `pobreza`, `mieperho` y `factor07`
  para evitar columnas `_x`/`_y`. El script comprueba que `ubigeo` y `estrato` coinciden entre ambas.
- `p204` tiene nulos (3,966 filas); quedan fuera del filtro de residentes sin error.
- `año` llega como texto (`'2024'`).
- Las llaves no se convierten a número: `conglome` tiene 6 caracteres, `vivienda` 3 y `hogar` 2.

## Variables de la base de salida

Todas las columnas del módulo 02 (en minúscula) más:

| Variable | Definición |
|---|---|
| `pobreza`, `mieperho`, `factor07` | de la sumaria (1 extremo, 2 no extremo, 3 no pobre) |
| `departamento` | `ubigeo[:2]` (texto, 25 códigos; Lima `15` y Callao `07` separados) |
| `urbano` | `estrato <= 5` |
| `pobre` | `pobreza <= 2` |
| `pobre_extremo` | `pobreza == 1` |

Útiles del módulo 02: `p207` sexo (1 hombre, 2 mujer), `p208a` edad, `dominio` (8 = Lima Metropolitana).

## Validaciones (`salidas/validacion.txt`)

Esenciales (si fallan, el script termina con código 1 y no guarda el parquet): columnas, variables requeridas,
llaves como texto, año, 108,664 residentes, sin duplicados de persona, llaves únicas en la sumaria, merge m:1
sin pérdida de filas, 25 códigos, rangos de `estrato`/`pobreza`/`p207`, `facpob07` positivo y pobreza
nacional dentro de 0.1 pp de 27.6 %.

Informativas (se reportan, no detienen): ponderado distinto del promedio simple, método de la sumaria,
pobreza urbana (24.8 %), rural (39.3 %), extrema (5.5 %), Lima Metropolitana (28.2 %) y departamentos contra
`referencias/pobreza_departamento_2024.csv`, con tolerancia de 0.2 pp por el redondeo de las referencias.

## Dos métodos de ponderación (resultados 2024)

| % pobre | Sumaria, `factor07 × mieperho` | Personas, `facpob07` |
|---|---:|---:|
| Nacional | 27.58 | 27.53 |
| Urbano | 24.81 | 24.74 |
| Rural | 39.30 | 39.44 |

Difieren porque la sumaria cubre todos los hogares con el factor del hogar multiplicado por sus miembros, y
personas usa solo residentes habituales con el factor de persona. La referencia departamental de la sesión 16
se reproduce con el método de la sumaria (25/25 a ≤ 0.05 pp). Con `facpob07` la diferencia llega a 0.52 pp
(Puno). Las cifras de `indicadores.csv` usan `facpob07`.

## `salidas/indicadores.csv`

Columnas: `nivel` (nacional, area, sexo, departamento), `codigo`, `nombre`, `indicador` (`pobreza`, o
`pobreza_extrema` solo a nivel nacional), `pct_ponderado` y `n_personas_muestra` (personas sin expandir).

## Git

`datos/` y `salidas/*.parquet` están en `.gitignore` (microdatos). Sí se versionan `validacion.txt` e
`indicadores.csv`.
