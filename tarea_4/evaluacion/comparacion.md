# Comparación entre el modo A (sin MCP ni Skills) y el modo B (con MCP y Skills)

Mismo modelo (Sonnet), misma instrucción y 10 preguntas en sesiones independientes. Datos: `evaluacion/resultados.csv`.
Configuración de cada modo y límites del diseño: `evaluacion/configuracion.md`. Criterios de q09 y q10: `evaluacion/criterios.md`.

## Resumen

| | Correctas | Incorrectas | No contestadas | Puntaje final | Tiempo promedio |
|---|:---:|:---:|:---:|:---:|:---:|
| Modo A (sin herramientas) | 0 | 0 | 9 («no sabe») + 1 parcial | 0.5 / 10 | 15.1 s |
| Modo B (MCP bcrp + Skills) | 9 | 0 | 1 («no sabe») | 9 / 10 | 35.5 s |

Notas sobre la tabla:
- El puntaje cuenta 1 por respuesta correcta y 0.5 por parcial. En q09 y q10 la calificación de coherencia es manual
  (según `criterios.md`); en las demás preguntas coincide con la exactitud automática.
- La única respuesta parcial del modo A es q10 (27.6 correcto, la otra cifra en null). El script la marcó «se equivoca»
  y la calificación manual la corrigió a parcial (0.5).
- Ninguna respuesta de ninguno de los dos modos fue una cifra inventada fuera de tolerancia.

## Preguntas que mejoraron o empeoraron (B frente a A)

| Pregunta | Modo A | Modo B | Cambio |
|---|---|---|---|
| q01 a q04 (BCRP) | no sabe | acierta, con `buscar_series` y `serie` | mejoró |
| q05, q06, q07 (ENAHO) | no sabe | acierta (27.6, 39.3, 44.99) | mejoró |
| q08 (Ica) | no sabe | no sabe | sin cambio |
| q09 (combinada) | no sabe | correcta (1) | mejoró |
| q10 (combinada) | parcial (0.5) | correcta (1) | mejoró |

Ninguna pregunta empeoró. Mejoraron 9 de 10 y una quedó igual.

Por qué mejoraron:
- **BCRP (q01 a q04):** son datos de 2026 y de diciembre de 2024 que el modelo no conoce. Sin herramientas no tiene cómo
  saberlos. Con el MCP los consulta y los cita con su código de serie.
- **ENAHO (q05 a q07, q09, q10):** el modo B encontró la cifra en archivos locales del proyecto. Ver la limitación 1:
  no la calculó en la sesión.

## Principales errores

1. **q08 en el modo B (Ica, pobreza 2024): no encontró la cifra.** `buscar_series` no tiene series de pobreza y los
   permisos de `Bash` (solo `uv run`) le impidieron leer los archivos locales. Respondió null y lo explicó. Quedó
   «no sabe», no una cifra errónea. Este caso muestra que el modo B depende de que la herramienta correcta exista y esté
   permitida, y no de que el modelo «sepa más».
2. **q10 en el modo A: respuesta incompleta.** Dio 27.6 (pobreza nacional) de memoria, que era correcto, pero dejó null
   la inflación subyacente y no pudo decir si estaba dentro del rango meta. Reconoció que no podía verificarla. Es una
   limitación de falta de información, no de razonamiento. Calificación: parcial (0.5).

## Hallazgo: el modo A no inventó cifras

En 10 preguntas, el modo A no entregó ninguna cifra equivocada. Respondió null en 9 y en la décima acertó una cifra.
Con la instrucción «si no puedes saberlo, pon null; no estimes», el modelo sin herramientas prefirió reconocer que no sabía
antes que adivinar. El error típico de un modelo sin acceso a datos (inventar una cifra verosímil) no apareció en esta
muestra. Sirve de punto de referencia: lo que el modo B aporta es la capacidad de responder, no evitar alucinaciones.

## Limitaciones

1. **En la ENAHO, el modo B leyó salidas ya generadas, no ejecutó las skills en la sesión.** En q05 a q07, q09 y q10
   consultó `salidas/validacion.txt` e `salidas/indicadores.csv`, calculados antes con los scripts del proyecto. Por eso
   la mejora en ENAHO muestra que el agente encuentra y cita resultados previos, no que las skills calculen la
   cifra en el momento. Esa comparación no queda probada por este experimento. Además, el modo B pudo ver resultados
   calculados con mis propios scripts, que son la fuente que se quiere evaluar. La verdad esperada, en cambio, viene del
   INEI y no de esos scripts.
2. **Llamada a `Grep` sin resolver.** En q10 del modo B hay un `Grep x1` aunque esa herramienta no estaba habilitada.
   No se sabe si se ejecutó o fue rechazada: el stream original no se guardó y el intento de repetir la corrida se trabó.
   La respuesta de q10 en B es correcta de todos modos.
3. **Una sola corrida por modo.** No se midió la variabilidad. En el piloto, q05 en el modo A acertó con 27.6 de
   memoria, y en la corrida completa, con la frase adicional en la instrucción, respondió null. Con una corrida por modo
   no puedo separar el efecto de esa frase de la variabilidad del modelo. Las diferencias entre modos son claras
   (9 frente a 0 correctas), pero los detalles de cada pregunta podrían cambiar al repetir.
4. **El modo B tarda más del doble:** 35.5 s frente a 15.1 s de promedio (2.3 veces). Parte del tiempo del modo A es
   solo la respuesta de memoria, que a menudo es «no sé».
5. **Acceso por `Bash`:** no se puede restringir por ruta con fiabilidad. El modo B tuvo un intento de `ls` sobre
   `evaluacion/` (q08), denegado por no ser `uv run`, y respondió null. No hay evidencia de que viera las respuestas
   esperadas.
6. **Muestra pequeña:** 10 preguntas, de las cuales 4 comparten fuente (BCRP). No permite estadística.

## Conclusión

Para datos oficiales recientes o exactos, como las series del BCRP de 2024 y 2026, un MCP vale la pena: sin él, el
modelo no puede responder, y con él responde con la cifra y el código de la serie, aunque tarde más del doble. Para la
ENAHO, este experimento no demuestra el valor de las Skills, porque el modo B leyó resultados ya generados en lugar de
ejecutarlas. Su ventaja práctica sería la reproducibilidad y la trazabilidad del cálculo, y eso habría que medirlo
pidiendo que se ejecuten desde cero. Una limitación del MCP y de las skills es su cobertura: q08 falló porque ninguna
herramienta cubría esa consulta con los permisos dados. Un MCP o una Skill se justifican cuando la información no está en
el modelo, cuando importa citar la fuente y cuando el costo en tiempo es aceptable. Si el modelo ya conoce el dato y
una cifra aproximada basta, el beneficio es menor.
