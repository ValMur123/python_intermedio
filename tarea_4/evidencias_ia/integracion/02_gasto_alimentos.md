# Parte 3: Hallazgo 4, gasto en alimentos (sumaria 2024)

Origen: la estudiante corrigió que la ENAHO sí mide gasto en alimentos (la sumaria trae los grupos de gasto).

| Paso | Qué se hizo | Resultado |
|---|---|---|
| 1 | Lectura de etiquetas de `sumaria-2024-12g.dta` (242 variables) | Se propusieron `gashog2d` (gasto total bruto) y los grupos 1 y 11 de alimentos; la estudiante validó numerador y denominador |
| 2 | Lectura de `ConstVarGasto-Metodologia actualizada.zip` (do-file del INEI) | El gasto de 8 grupos suma, además de los `gru*`, `g05hd*`, `ig06hd`, `sg23`–`sig28`, `sg42*`, `g07hd` e `ig08hd` |
| 3 | Reconstrucción con el do-file sobre `sumaria-2024.dta` | Suma = `gashog2d` (diferencia máxima 0.016 soles por hogar) |
| 4 | Conteo de hogares con participación 0 % | 135 de 33,691 con la definición validada; 104 se explican por rubros no incluidos; 31 sin alimentos en ningún componente |
| 5 | `scripts/gasto_alimentos.py` | `salidas/gasto_alimentos_2024.csv` con las definiciones "validada" e "inei", cociente de totales y promedio por hogar |

Decisión de diseño (revisada): en una primera versión la cifra principal usaba la definición validada por la estudiante (archivo de 12 grupos). Al comprobar que omite rubros que el INEI cuenta como alimentos (promedio sin ponderar de 9,442 frente a 12,493 soles por hogar al año), la estudiante pidió cambiar la cifra principal a la definición del INEI (26 variables, todas con etiqueta de alimentos, sin `sg42*`, `g07hd` ni `ig08hd`, que el script verifica). La definición inicial queda como `sensibilidad_12g`. El script calcula también las diferencias en pp entre grupos (`nivel = diferencia_pp`). Todo está documentado en las Limitaciones del informe.
