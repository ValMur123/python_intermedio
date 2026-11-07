---
name: graficando-enaho
description: Genera gráficos de pobreza monetaria de la ENAHO 2024 del INEI (barras ponderadas, PNG a 200 dpi en figuras/) a partir de pedidos en lenguaje natural. Úsala cuando pidan graficar, visualizar o comparar la pobreza urbana y rural, por sexo (o por sexo del jefe de hogar) o por departamento.
argument-hint: [area|sexo|departamento|todos]
---
# Graficar la ENAHO

1. **Base previa.** Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`
   y espera a que `salidas/validacion.txt` diga APROBADO. Si esa skill falla, detente y reporta el error.
2. **Elige el gráfico según el pedido** y ejecuta desde la raíz del proyecto:

   | El usuario pide… | Comando |
   |---|---|
   | pobreza urbana vs rural, por área | `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --grafico area` |
   | pobreza por sexo, hombres y mujeres | `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --grafico sexo` |
   | pobreza según el sexo del jefe de hogar | `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --grafico sexo --sexo-de jefe` |
   | pobreza por departamento, ranking, comparar regiones | `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --grafico departamento` |
   | "todos los gráficos", o un pedido amplio | `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py` |

3. Los PNG quedan en `figuras/`. Muéstralos y resume lo que dicen con las cifras de sus títulos; no inventes otras.

## Sexo de la persona o del jefe de hogar

La pobreza se mide por hogar: todos sus miembros son pobres o no pobres a la vez. Por eso:

- **Sexo de la persona (por defecto):** responde "¿qué porcentaje de hombres y de mujeres vive en pobreza?".
  Casi no difiere (27.4 % vs 27.7 %) porque hombres y mujeres comparten los mismos hogares; solo la composición
  de los hogares genera diferencia.
- **Sexo del jefe de hogar** (`p203 == 1`): responde "¿son más pobres los hogares con jefatura femenina?".
  Es el corte que muestra la diferencia entre tipos de hogar (28.3 % con jefe hombre, 26.0 % con jefa mujer),
  pero omite hogares cuyo jefe no es residente habitual (queda n = 107,855 de 108,664).

Si el usuario no precisa, usa el sexo de la persona y menciona que existe la otra opción. No interpretes la
diferencia como efecto causal del sexo: es una asociación descriptiva.

## Reglas que el script aplica

- Todo porcentaje ponderado con `facpob07` (`tasa_ponderada` de `limpiando-enaho`); nada de promedios simples.
- Barras desde cero, un solo color, valor escrito en cada barra, línea punteada del total nacional.
- Título analítico con las cifras y el año, unidad "% de personas" y nota "Fuente: INEI, ENAHO 2024".
- Departamentos ordenados de mayor a menor; PNG a 200 dpi.

Las cifras salen de la base y no se escriben a mano. Los porcentajes departamentales con `facpob07` pueden
diferir hasta 0.5 pp de `referencias/pobreza_departamento_2024.csv`, que usa el método de la sumaria;
ver `limpiando-enaho/reference.md`.
