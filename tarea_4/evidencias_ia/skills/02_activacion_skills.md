 ▐▛███▛█   Claude Code v2.1.319
▝▜██████▀  Sonnet 5.5 · Claude Pro
 ▝▝   ▝▝   ~\Documents\Github\python_intermedio\tarea_4


❯ Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.          

● Skill(mapeando-enaho)
  ⎿  Successfully loaded skill

  Listed 1 directory (ctrl+o to expand)

● Falta salidas/personas_2024.parquet. Solo existe el .bak. Según la skill,
  primero debo correr limpiando-enaho.

● Skill(limpiando-enaho)
  ⎿  Successfully loaded skill

  Ran 1 shell command (ctrl+o to expand)

● Limpieza aprobada. Ahora el mapa.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● El mapa está listo en mapas/pobreza_departamento_2024.png.

  Qué dice el título del mapa
  - La pobreza monetaria va de 5.9 % en Ica a 45.0 % en Cajamarca.
  - 10 de los 25 departamentos superan el total nacional, que es 27.5 %.
  - La estimación usa a los residentes habituales (n = 108,664), ponderados con
    facpob07.

  Cómo se hizo
  - Base previa: faltaba salidas/personas_2024.parquet, porque solo existía el
    .bak. Corrí primero limpiando-enaho y la validación salió APROBADA.
  - Unión de datos: se unió por código (ubigeo[:2] con FIRST_IDDP), con 25 de 25
    departamentos con dato. Lima (15) y Callao (07) quedan separados. Callao,
    que es muy pequeño, se rotula con una línea (33.8 %).
  - Color: un solo tono azul, desde 0 %.

  Comparación con la referencia de la sesión 16
  - La diferencia máxima es 0.52 pp, en Puno. 16 de los 25 departamentos quedan
    dentro de 0.2 pp.
  - La diferencia viene del método de ponderación. El mapa pondera personas con
    facpob07, y la referencia usa la sumaria con factor07 × mieperho.
  - Con el método de la referencia, esta se reproduce a 0.05 pp o menos. El
    detalle por departamento está en salidas/comparacion_mapa.csv.

  No toqué salidas/personas_2024.parquet.bak.

✻ Worked for 48s · done 9:00 AM

※ recap: Hice el mapa de pobreza monetaria por departamento con ENAHO 2024 y está guardado en mapas/pobreza_departamento_2024.png, con la base limpia validada. Lo siguiente es que lo revises; si te parece bien, queda listo para commit. (disable recaps in /config)

❯ /graficando-enaho pobreza urbana y rural                                      

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● El gráfico está en figuras/pobreza_urbano_rural_2024.png. Usa la base ya
  validada y pondera con facpob07.

  - Rural: 39.4 % de las personas vive en pobreza monetaria.
  - Urbano: 24.7 % (estratos 1 a 5).
  - Brecha: la pobreza rural supera a la urbana en 14.7 puntos porcentuales.
  - Total nacional: 27.5 %, marcado con una línea punteada. La zona rural queda
    por encima y la urbana por debajo.

  Es una diferencia descriptiva entre áreas, no una relación causal. En la
  carpeta figuras/ ya había otros gráficos de corridas anteriores (sexo, sexo
  del jefe de hogar y departamento). No los regeneré.

✻ Sautéed for 18s · done 9:04 AM