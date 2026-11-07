---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2024 del INEI y arma la base de personas residentes habituales con pobreza, departamento, área y factor de expansión, más validacion.txt e indicadores.csv. Úsala cuando pidan limpiar, unir, preparar o analizar la ENAHO, o calcular pobreza monetaria por área, sexo o departamento.
argument-hint: [año]
---
# Limpiar la ENAHO

Pipeline fijo en `scripts/limpiar.py`: se corre tal cual, no se reescribe.

1. Si faltan los zip en `datos/` (`966-Modulo34.zip` y `966-Modulo02.zip`), pide al usuario bajarlos del INEI
   (código 966 = ENAHO 2024). No los descargues por tu cuenta. El script usa solo `sumaria-AAAA.dta` y
   `enaho01-AAAA-200.dta`; ignora PDFs, diccionarios y los demás `.dta` de los zip.
2. Ejecuta desde la raíz del proyecto: `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio ${0:-2024}`
3. Lee `salidas/validacion.txt`. Si el script termina con error, o la pobreza nacional se aleja más de 0.1 pp
   de 27.6 %, **detente** y reporta qué validación falló. No ajustes filtros, factores ni cifras para que coincida.
4. Responde con `salidas/personas_AAAA.parquet` (base) e `salidas/indicadores.csv` (tabla de resultados).

## Reglas que el script aplica y que no se negocian

- Lectura con `convert_categoricals=False`; `conglome`, `vivienda`, `hogar` como texto (ceros iniciales).
- Columnas en minúscula (`aÑo` → `año`).
- Residentes habituales: `((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))` → 108,664 personas.
- Unión personas–hogares con `merge(..., validate="m:1")`, sin pérdida ni duplicación de filas.
- `departamento = ubigeo[:2]`, `urbano = estrato <= 5`, `pobre = pobreza <= 2`.
- Toda cifra ponderada con `facpob07`; nunca promedios simples.

## Al usar la base

- Calcula porcentajes con `np.average(x, weights=df["facpob07"])`. `factor07` es del hogar y solo se usa con
  `mieperho` para el contraste del método oficial de la sumaria.
- Lee las llaves y `departamento` como texto (`dtype={"codigo": str}` en el CSV) para no perder el cero de `01`…`09`.
- Variables que no están aquí (edad `p208a`, sexo `p207`, `dominio`, etc.), el contraste de métodos y la
  validación completa: lee `reference.md`.
- Una diferencia es descriptiva, no causal: no la presentes como relación demostrada.

## Si otra skill la necesita

`graficando-enaho` y `mapeando-enaho` deben comprobar que existe `salidas/personas_2024.parquet`; si no existe,
ejecutan primero esta skill.
