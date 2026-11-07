# Parte 3: ejecución integrada de MCP y Skills (sesión única de Claude Code)

Pregunta: inflación en Lima 2020-2024 (alimentos) y pobreza monetaria 2024 por área y departamento.

Orden real de ejecución en la misma sesión:

| Paso | Componente | Llamada | Resultado |
|---|---|---|---|
| 1 | MCP `bcrp` | `buscar_series` ("ipc 12 meses", "alimentos y bebidas", "subyacente") | PN01273PM, PN09822PM y PN01279PM confirmadas: IPC de Lima Metropolitana, var. % 12 meses, mensual |
| 2 | MCP `bcrp` | `serie` × 3 (2020-01 a 2024-12) | 60 datos por serie → `salidas/bcrp_inflacion_2020_2024.csv` (180 filas) |
| 3 | Skill | `limpiando-enaho` (ejecutada aunque la base ya existía) | Validación APROBADA: 108,664 residentes, 25 códigos, pobreza nacional 27.53 % |
| 4 | Script propio | `uv run scripts/grafico_bcrp.py` (lee solo el CSV) | `figuras/inflacion_lima_2020_2024.png`, `salidas/indicadores_bcrp.csv` |
| 5 | MCP `bcrp` | `resumen` y `comparar_periodos` sobre PN09822PM | Contraste con el script: máx. 13.16 % (2023-02); promedio 2020-2021 = 3.29 %, 2022-2023 = 10.42 % |
| 6 | Skill | `graficando-enaho` (todos los gráficos) | PNG en `figuras/` |
| 7 | Skill | `mapeando-enaho` | `mapas/pobreza_departamento_2024.png`, 25/25 unidades, Lima y Callao separados |
| 8 | Informe | `informes/informe_final.md` y `informes/verificacion.md` | Cifras tomadas de los CSV de salida |

Herramientas MCP distintas usadas: `buscar_series`, `serie`, `resumen`, `comparar_periodos` (4).
Skills usadas: `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho` (3).

## Incidencias

- Primer intento de guardar las series con un heredoc en Bash falló por un error de sintaxis del shell; se reintentó escribiendo los archivos con la herramienta Write y convirtiéndolos a CSV con un script.
- La primera ejecución de `scripts/grafico_bcrp.py` falló por `UnicodeEncodeError` (carácter "−" en la consola cp1252). Se corrigió reconfigurando `stdout` a UTF-8.
- Primera versión del gráfico: la anotación de dic-2024 tapaba la línea subyacente y el título decía "volvió al rango meta en 2024", cosa que los datos no respaldan (alimentos bajó de 1 % en varios meses de 2024). Se corrigieron la posición de la anotación y el título.
- Los CSV del BCRP se guardaron transcribiendo la salida literal de la herramienta `serie` a archivos JSON y convirtiéndolos con código; no se re-consultó la API por otra vía.
