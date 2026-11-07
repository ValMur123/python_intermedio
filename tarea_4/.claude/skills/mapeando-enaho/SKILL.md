---
name: mapeando-enaho
description: Construye el mapa coroplético de pobreza monetaria por departamento con la ENAHO 2024 del INEI (25 departamentos, Lima y Callao separados, PNG en mapas/). Úsala cuando pidan un mapa, mapa coroplético o distribución territorial de la pobreza por departamento o región del Perú.
argument-hint: [año]
---
# Mapear la pobreza por departamento

1. **Base previa.** Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho` y
   espera a que `salidas/validacion.txt` diga APROBADO. Si esa skill falla, detente y reporta el error.
2. **GeoJSON.** Si falta `referencias/peru_departamental_simple.geojson`, descárgalo:
   `curl -fL -o referencias/peru_departamental_simple.geojson https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson`
3. **Ejecuta** desde la raíz del proyecto: `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py`
4. Muestra `mapas/pobreza_departamento_2024.png` y resume con las cifras de su título. Si el script falla
   (código de salida 1), reporta el mensaje tal cual: no completes ni corrijas datos a mano.

## Reglas que el script aplica

- **Unión por código**: `ubigeo[:2]` de la ENAHO con `FIRST_IDDP` del GeoJSON, ambos como texto (`01`…`25`).
  Nunca por nombre: «APURIMAC» no es «Apurímac».
- **25 unidades con dato**: falla si falta o sobra algún código en cualquiera de las dos fuentes, o si
  algún departamento queda sin pobreza tras la unión (`validate="1:1"`).
- **Lima (`15`) y Callao (`07`) separados**: filas y geometrías distintas; el script lo comprueba.
- **Ponderación**: pobreza de personas con `facpob07`; nada de promedios simples.
- **Color**: un solo tono (`Blues`) de claro a oscuro, escala desde 0 %, sin arcoíris. La leyenda indica la
  unidad: «% de personas en situación de pobreza monetaria». Cada departamento lleva su valor.
- Título analítico con las cifras y el año; fuente «INEI, ENAHO 2024» al pie.

## Comparación con la referencia

El script compara cada departamento con `referencias/pobreza_departamento_2024.csv` (sesión 16) y guarda
`salidas/comparacion_mapa.csv` con `ccdd`, `departamento`, `pobreza_facpob07`, `pobreza_referencia`,
`diferencia_pp`, `abs_pp` y `n_personas_muestra`.

Las diferencias (máxima 0.52 pp en Puno; 16 de 25 dentro de 0.2 pp) **vienen del método de ponderación**: el mapa
pondera personas con `facpob07`, mientras que la referencia usa la sumaria con `factor07 × mieperho`.
Con ese segundo método la referencia se reproduce a ≤ 0.05 pp (ver `salidas/validacion.txt`). Aun así el
mapa usa `facpob07`, la regla del proyecto. Si alguna diferencia supera 1 pp, el script falla porque ya no
se explica por el método.

Comunícalo así al usuario; no reemplaces los valores del mapa por los de la referencia.
