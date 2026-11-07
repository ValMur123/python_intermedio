 ▐▛███▛█   Claude Code v2.1.319
▝▜██████▀  Sonnet 5.5 · Claude Pro
 ▝▝   ▝▝   ~\Documents\Github\python_intermedio\tarea_4


❯ Ahora la Parte 2 de la tarea (está en ENUNCIADO.md). Lee también la sesión 16 
  (https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skill  
  s-enaho), sobre todo el pipeline de limpieza y la tabla de validación. Tengo  
  los zip de los módulos 34 y 02 de la ENAHO 2024 en datos/. Pueden traer       
  varios archivos adentro (documentación, diccionarios), así que usa solo el    
  .dta. Agrega con uv pandas, pyarrow, geopandas y matplotlib.                  
                                                                                
  Crea la skill .claude/skills/limpiando-enaho con SKILL.md, reference.md y     
  scripts/limpiar.py. Trabajo con la ENAHO en el INEI, así que estas son mis    
  reglas:                                                                       
  - leer con convert_categoricals=False y las llaves conglome, vivienda, hogar  
  como texto, para no perder ceros iniciales                                    
  - columnas en minúscula (ojo con aÑo)                                         
  - residentes habituales: ((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206   
  == 1))                                                                        
  - merge personas–hogares con validate="m:1", y verificar que no se pierdan ni 
  dupliquen filas                                                               
  - departamento = ubigeo[:2], urbano = estrato <= 5, pobre = pobreza <= 2      
  - toda cifra ponderada con facpob07; nada de promedios simples                
    Antes de escribir el script, dime cómo vas a verificar cada punto.          
                                                                                
  En todos los commits de esta parte agrega (#11) al mensaje, porque estoy      
  siguiendo la Parte 2 en el issue #11 de mi repo.                              

● Voy a revisar el enunciado, los datos y la sesión 16 antes de proponerte el
  plan de verificación.

  Read 1 file, listed 1 directory, called fetch, ran 5 shell commands (ctrl+o to expand)

● Estoy en la fase de lectura y todavía no escribí ningún archivo. Extraje los
  .dta a una carpeta temporal, que ya borré, y medí cada punto sobre los datos
  reales. No pude leer la sesión 16: GitHub bloquea la descarga automática
  (robots.txt) y gh no está instalado. Por eso el plan sale del ENUNCIADO y de
  los datos. Si quieres que siga el pipeline de la sesión al pie de la letra,
  pégame el código de limpieza y la tabla de validación.

  Lo que encontré en los datos

  - Archivos que se usan: enaho01-2024-200.dta (módulo 02) y sumaria-2024.dta
    (módulo 34). El zip del 34 trae también sumaria-2024-12g.dta, con 242
    columnas. Da los mismos resultados en pobreza, así que uso solo la sumaria
    estándar y lo dejo documentado.
  - facpob07 no está en la sumaria. Esa base trae factor07 (el factor del
    hogar). facpob07 está en el módulo 02, que es el de personas. Por eso la
    pobreza ponderada por persona se calcula después del merge, con el facpob07
    de personas.
  - ubigeo y estrato están en ambas bases. Si hago el merge sin elegir columnas,
    pandas crea duplicados con sufijo _x y _y. De la sumaria traeré solo las
    llaves y pobreza.
  - La columna aÑo viene con Ñ (U+00D1). El .lower() la deja en año, que es
    correcto. Si mi terminal la muestra como a�o, es solo un problema de
    visualización.

  Cómo verifico cada punto

  Regla: Lectura con convert_categoricals=False y llaves como texto
  Verificación (el script falla con error explícito si no se cumple): Compruebo
    que conglome, vivienda y hogar son str y que sus longitudes son fijas (6, 3
  y
     2). Compruebo que ninguna lleva ceros iniciales perdidos. Las columnas ya
    vienen como texto en el .dta; aun así el script las fuerza a str.
  ────────────────────────────────────────
  Regla: Columnas en minúscula
  Verificación (el script falla con error explícito si no se cumple): Compruebo
    que all(c  ==  c.lower()) y que existen año, p204, p205, p206, facpob07,
    pobreza y estrato.
  ────────────────────────────────────────
  Regla: Residentes habituales
  Verificación (el script falla con error explícito si no se cumple): La cuenta
    tiene que dar exactamente 108,664 (ya lo confirmé: da 108,664). Compruebo
    también que no hay codperso duplicado dentro de las llaves. Los 3,966 p204
    nulos quedan fuera sin error.
  ────────────────────────────────────────
  Regla: Merge m:1 y filas intactas
  Verificación (el script falla con error explícito si no se cumple): Uso
    validate="m:1", que ya levanta error si hay duplicados en la sumaria. Además

    compruebo que len(antes)  ==  len(después), que hay 0 filas sin match
    (indicator o nulos en pobreza) y que las llaves de la sumaria son únicas. En

    los datos: 33,691 hogares, 0 duplicados y 0 filas sin match.
  ────────────────────────────────────────
  Regla: departamento = ubigeo[:2]
  Verificación (el script falla con error explícito si no se cumple): Compruebo
    que hay exactamente 25  códigos, de 01 a 25, y que 15 (Lima) y 07 (Callao)
    están separados.
  ────────────────────────────────────────
  Regla: urbano = estrato <= 5
  Verificación (el script falla con error explícito si no se cumple): Compruebo
    que estrato no tiene nulos y que el área tiene dos categorías.
  ────────────────────────────────────────
  Regla: pobre = pobreza <= 2
  Verificación (el script falla con error explícito si no se cumple): Compruebo
    que pobreza toma solo los valores 1, 2 y 3, sin nulos.
  ────────────────────────────────────────
  Regla: Ponderación con facpob07
  Verificación (el script falla con error explícito si no se cumple): Compruebo
    que facpob07 no tiene nulos ni ceros. Calculo todo con una función única
    tasa_ponderada que usa np.average(...,   weights=facpob07). Como contraste,
    calculo el promedio simple (25.6 %) y compruebo que se aleja de la cifra
    ponderada, para confirmar que el peso se aplicó.
  ────────────────────────────────────────
  Regla: Referencias
  Verificación (el script falla con error explícito si no se cumple): La pobreza

    nacional tiene que quedar a menos de 0.1 pp de 27.6 %. Hoy da 27.53  %, o
  sea
     0.07 pp de diferencia. Pobreza urbana y rural van como informativas contra
    24.8 % y 39.3 %. Hoy dan 24.74 % y 39.44 %. La rural difiere 0.14 pp, y el
    enunciado dice "aproximadamente", así que no la trato como fallo esencial.

  El resultado va a salidas/validacion.txt con cada chequeo marcado como
  APROBADO o FALLIDO. Si falla uno esencial (108,664, 25 códigos, merge,
  duplicados o pobreza nacional), el script termina con código distinto de cero.
  No ajusto nada para que coincida.

  Lo que haría después de tu visto bueno

  1. uv add pandas pyarrow geopandas matplotlib.
  2. Crear .claude/skills/limpiando-enaho/ con SKILL.md, reference.md y
     scripts/limpiar.py. Los zips se leen con zipfile, extrayendo solo los dos
     .dta. La salida procesada será un parquet, que es para lo que sirve
     pyarrow.
  3. Ejecutar la skill, revisar validacion.txt y hacer commits que terminen en
     (#11) y lleven el Co-Authored-By que me indicó el sistema.

  Dos cosas que necesito de ti

  - ¿Sigo? ¿Te sirve este plan, o quieres cambiar algo antes de escribir el
    script?
  - .gitignore: ignora **/datos/ y datos/966-Modulo02.zip, así que los zips no
    se suben. Es lo normal. El parquet procesado lo guardaría en salidas/, que
    no está ignorado. Si prefieres que tampoco se versione, dímelo.

✻ Worked for 1m 27s · done 7:48 AM

※ recap: Estamos armando la skill `limpiando-enaho` de la Parte 2, y ya te presenté cómo verificaré cada regla, con cifras medidas sobre tus datos, sin haber escrito código aún. Lo siguiente es que me confirmes ese plan para empezar con `uv add` y el script. (disable recaps in /config)

❯ El plan está bien, con estos ajustes:                                         
                                                                                
  1. La sesión 16 sí se puede bajar con curl desde raw.githubusercontent.com,   
  como hiciste en la Parte 1. Descarga https://raw.githubusercontent.com/d2cml- 
  ai/Data-Science-Python/main/sessions/16-skills-enaho/README.md y              
  referencias/pobreza_departamento_2024.csv a una carpeta referencias/ y        
  síguelos: la base se llama salidas/personas_2024.parquet y la tabla de        
  validación trae pobreza extrema 5.5 % y Lima Metropolitana (dominio == 8)     
  28.2 %.                                                                       
  2. En el INEI la pobreza oficial se calcula con la sumaria ponderando por     
  factor07 × mieperho. Agrega ese método como contraste en validacion.txt:      
  nacional, urbano y rural con los dos métodos (sumaria con factor07×mieperho y 
  personas con facpob07). Explica en una línea por qué difieren. El esencial    
  sigue siendo la nacional dentro de 0.1 pp de 27.6 %.                          
  3. No quiero subir el parquet, porque son microdatos derivados. Agrega        
  salidas/*.parquet al .gitignore. Sí se suben validacion.txt e                 
  indicadores.csv.                                                              
  4. El enunciado exige salidas/indicadores.csv: genera una tabla con la        
  pobreza ponderada nacional, urbana/rural, por sexo y por departamento         
  (código, nombre, %, n de personas en muestra).                                
                                                                                
  Procede con la skill.                                                         

  Ran 1 shell command (ctrl+o to expand)

● Descargué la sesión 16 y la tabla de validación. Instalo las dependencias y
  preparo .gitignore.

  Ran 1 shell command (ctrl+o to expand)

● Write(.claude\skills\limpiando-enaho\scripts\limpiar.py)
  ⎿  Wrote 283 lines to .claude\skills\limpiando-enaho\scripts\limpiar.py
       1 """Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO y
          valida el resultado.
       2 
       3 Salidas (en --salidas):
       4     personas_AAAA.parquet  base de personas residentes habituale
         s con pobreza y factores
       5     validacion.txt         verificaciones aprobadas y fallidas
       6     indicadores.csv        pobreza ponderada: nacional, área, se
         xo y departamento
       7 
     … +276 lines (ctrl+o to expand)

  Ran 5 shell commands (ctrl+o to expand)

● Write(.claude\skills\limpiando-enaho\SKILL.md)
  ⎿  Wrote 39 lines to .claude\skills\limpiando-enaho\SKILL.md
       1 ---
       2 name: limpiando-enaho
       3 description: Limpia los módulos 34 (sumaria) y 02 (miembros) de 
         la ENAHO 2024 del INEI y arma la base de personas residentes hab
         ituales con pobreza, departamento, área y factor de expansión, m
         ás validacion.txt e indicadores.csv. Úsala cuando pidan limpiar,
          unir, preparar o analizar la ENAHO, o calcular pobreza monetari
         a por área, sexo o departamento.
       4 argument-hint: [año]
       5 ---
     … +34 lines (ctrl+o to expand)

● Write(.claude\skills\limpiando-enaho\reference.md)
  ⎿  Wrote 68 lines to .claude\skills\limpiando-enaho\reference.md
       1 # Referencia: limpiando-enaho
       2 
       3 ## Archivos de entrada
       4 
       5 | Zip | `.dta` que se usa | Una fila por | Filas | Factor |
       6 |---|---|---|---|---|
       7 | `966-Modulo34.zip` | `sumaria-2024.dta` | hogar | 33,691 | `fa
         ctor07` (× `mieperho` = personas) |
       8 | `966-Modulo02.zip` | `enaho01-2024-200.dta` | persona | 117,72
         1 | `facpob07` |
     … +60 lines (ctrl+o to expand)

● Termino la skill y hago los commits.

  Ran 1 shell command (ctrl+o to expand)

● La skill limpiando-enaho está lista y corre de punta a punta. El script
  termina con código 0 y todas las validaciones esenciales pasan. Hice tres
  commits, todos con (#11) y con el Co-Authored-By correspondiente. No hice
  push.

  Resultados 2024

  ┌──────────┬────────────────────────────┬────────────────────┬────────────┐
  │ % pobre  │    Sumaria (factor07 ×     │     Personas       │ Referencia │
  │          │         mieperho)          │     (facpob07)     │            │
  ├──────────┼────────────────────────────┼────────────────────┼────────────┤
  │ Nacional │                      27.58 │              27.53 │       27.6 │
  ├──────────┼────────────────────────────┼────────────────────┼────────────┤
  │ Urbano   │                      24.81 │              24.74 │       24.8 │
  ├──────────┼────────────────────────────┼────────────────────┼────────────┤
  │ Rural    │                      39.30 │              39.44 │       39.3 │
  └──────────┴────────────────────────────┴────────────────────┴────────────┘

  - Otros chequeos: 108,664 residentes habituales, 25 códigos departamentales
    (Lima y Callao separados), 0 filas perdidas o duplicadas en el merge m:1,
    pobreza extrema 5.50 % y Lima Metropolitana 28.03 % (referencia 28.2 %).
  - Por qué difieren los dos métodos: validacion.txt lo explica en una línea. La
    sumaria cubre todos los hogares con el factor del hogar multiplicado por
    sus miembros. Personas usa solo residentes habituales con facpob07, que es
    otro factor.
  - Pobreza nacional como validación esencial: la mido con el método de
    personas, y queda a 0.07 pp de 27.6 %.

  Archivos

  - Skill: .claude/skills/limpiando-enaho/ tiene SKILL.md, reference.md y
    scripts/limpiar.py.
  - Salidas versionadas: salidas/validacion.txt y salidas/indicadores.csv
    (nacional, urbano/rural, sexo y los 25 departamentos, con código, nombre, %
    ponderado y n en muestra).
  - Parquet fuera de git: salidas/personas_2024.parquet quedó fuera por
    salidas/*.parquet en .gitignore. Lo comprobé con git check-ignore.
  - Referencias: referencias/ guarda el README de la sesión 16 y el CSV de
    pobreza por departamento.
  - Dependencias: agregué con uv pandas, pyarrow, geopandas y matplotlib.

  Lo que debes saber

  - Departamentos con personas: el CSV de referencia de la sesión 16 se
    reproduce con el método de la sumaria, con diferencia máxima de 0.05 pp. Con
    facpob07, que es lo que usa indicadores.csv, Puno se aleja 0.52 pp y 16 de
    25 departamentos quedan a menos de 0.2 pp. Esto está documentado en
    validacion.txt y no lo corregí.
  - Chequeos informativos: el rural (39.44 vs 39.3) y Lima Metropolitana (28.03
    vs 28.2) difieren menos de 0.2 pp, y por eso los pasa. Esa tolerancia la
    elegí yo, porque las referencias vienen redondeadas a un decimal. Solo la
    pobreza nacional tiene la tolerancia de 0.1 pp que pide el enunciado.
  - Probé la falla por zip ausente: sin el zip, el script da un error explícito
    y termina con código 1. No probé la falla por una validación esencial,
    porque no pude provocarla sin alterar los datos.
  - graficando-enaho y mapeando-enaho: son el siguiente paso de la Parte 2.
  - Avisos de Git: los avisos de LF a CRLF no afectan nada.

✻ Sautéed for 3m 22s · done 7:58 AM

※ recap: Estamos haciendo la Parte 2 de la Tarea 4 (skills para ENAHO), y `limpiando-enaho` ya está lista, validada y comprometida con (#11). Lo siguiente es crear `graficando-enaho` y después `mapeando-enaho`, si das el visto bueno. (disable recaps in /config)

❯ Excelente. Ahora crea .claude/skills/graficando-enaho con su SKILL.md y un    
  script en scripts/ que genere en figuras/, a 200 dpi:                         
  1. pobreza urbana vs rural                                                    
  2. pobreza por sexo (explícame si conviene el sexo de la persona o del jefe   
  de hogar, y por qué)                                                          
  3. pobreza por departamento, ordenada de mayor a menor                        
     Reglas: ponderado con facpob07, barras desde cero, un solo color, valor    
  escrito en cada barra, título analítico que diga qué y cuándo, unidad (% de   
  personas) y nota "Fuente: INEI, ENAHO 2024". El SKILL.md debe permitir pedir  
  gráficos en lenguaje natural y decir: si no existe                            
  salidas/personas_2024.parquet, usa primero la skill limpiando-enaho. Córrelo  
  y muéstrame las figuras. Commit con (#11).                                    
  ⎿  1 skill available

● Skill(dataviz)
  ⎿  Successfully loaded skill

● Write(.claude\skills\graficando-enaho\scripts\graficar.py)
  ⎿  Wrote 169 lines to .claude\skills\graficando-enaho\scripts\graficar.py
       1 """Gráficos de pobreza monetaria ENAHO a partir de salidas/perso
         nas_AAAA.parquet.
       2 
       3     uv run graficar.py --grafico area|sexo|departamento|todos [-
         -sexo-de persona|jefe] [--anio 2024]
       4 
       5 Todas las cifras se ponderan con facpob07 (porcentaje de persona
         s). Barras desde cero, un solo
       6 color, valor en cada barra, título analítico, fuente al pie. PNG
          a 200 dpi en --figuras.
     … +163 lines (ctrl+o to expand)

  Read 4 files, ran 1 shell command (ctrl+o to expand)

● Hay defectos de maquetación: el título se pisa con el subtítulo, los textos
  del borde derecho se cortan y el título de la figura de jefatura es torpe. Lo
  corrijo.

  Ran 1 shell command (ctrl+o to expand)

● Mi parche escribió un salto de línea literal dentro de las cadenas; lo
  arreglo.

  Read 4 files, ran 2 shell commands (ctrl+o to expand)

● La skill graficando-enaho está lista, con su SKILL.md y scripts/graficar.py.
  El script generó las figuras en figuras/ a 200 dpi y las revisé una por una.
  Hice el commit 0924210, con (#11) y sin push.

  Las cifras salen de la base procesada y todas están ponderadas con facpob07.
  Las figuras son:

  - pobreza_urbano_rural_2024.png: la pobreza rural (39.4 %) supera en 14.7
    puntos porcentuales a la urbana (24.7 %).
  - pobreza_sexo_2024.png: casi no hay diferencia entre hombres (27.4 %) y
    mujeres (27.7 %).
  - pobreza_departamento_2024.png: Cajamarca tiene la mayor pobreza (45.0 %) e
    Ica la menor (5.9 %), ordenados de mayor a menor.
  - pobreza_sexo_jefe_hogar_2024.png: es la variante por sexo del jefe de hogar,
    que generé para que compares las dos opciones.

  En la primera versión el título se pisaba con el subtítulo y varios textos se
  cortaban en el borde. El script ahora calcula el espacio según las líneas de
  texto, y volví a mirar las figuras después de corregirlo.

  Sexo de la persona o del jefe de hogar

  Conviene el sexo de la persona como opción por defecto, porque responde la
  pregunta directa: qué porcentaje de hombres y de mujeres vive en pobreza. La
  pobreza se mide por hogar, así que hombres y mujeres comparten los mismos
  hogares y casi no difieren.

  El sexo del jefe de hogar responde otra pregunta: si los hogares con jefatura
  femenina son más pobres. Esa pregunta es válida, pero cambia la unidad de
  lectura. La diferencia que aparece (28.3 % con jefe hombre y 26.0 % con jefa
  mujer) es entre tipos de hogar, no entre mujeres y hombres. Además deja fuera
  a 809 personas cuyo jefe no es residente habitual, así que queda con n =
  107,855 en vez de 108,664.

  Por eso el script usa la persona por defecto y acepta --sexo-de jefe para la
  otra. Si el pedido no es claro, SKILL.md indica elegir la persona y mencionar
  que existe la alternativa.

  Lo que debes saber

  - Departamentos distintos a la referencia: con facpob07 algunos valores se
    alejan de referencias/pobreza_departamento_2024.csv. Ica da 5.9 % frente a
    6.0 %, y Puno 40.4 % frente a 39.9 %. Es la diferencia de factor que ya
    documentamos en validacion.txt. No lo ajusté.
  - Línea del total nacional: agregué una línea punteada gris con el total
    nacional (27.5 %) como contexto. No cuenta como segundo color, pero puedes
    quitarla si prefieres.
  - Dependencia entre skills: graficar.py importa tasa_ponderada y los nombres
    de departamento de limpiando-enaho. Si mueves esa skill, el import se rompe.
  - Nombres de departamento: los acentos de los 25 nombres los puse a mano en un
    diccionario del script. Revisa que los quieras así, por ejemplo "Áncash" y
    "Apurímac".

  El encadenamiento (si falta salidas/personas_2024.parquet, se usa antes
  limpiando-enaho) está escrito en SKILL.md. Solo probé el caso en que el
  archivo existe. Cuando se pruebe la activación en lenguaje natural, hay que
  borrar el parquet y ver si Claude encadena las dos skills.

✻ Cogitated for 2m 41s · done 8:08 AM

※ recap: Estamos completando la Parte 2 de la Tarea 4 (skills de ENAHO, issue #11): ya están listas `limpiando-enaho` y `graficando-enaho`, con commits hechos. Lo siguiente es crear `mapeando-enaho`, que une por `ubigeo[:2]` y `FIRST_IDDP` y debe mostrar las 25 unidades. (disable recaps in /config)

❯ Bien, deja la persona por defecto y la del jefe como opción. Los nombres con  
  tilde están bien.                                                             
                                                                                
  Correcciones en los gráficos:                                                 
  1. En pobreza_sexo_jefe_hogar_2024.png la fuente dice n = 108,664, pero el    
  subtítulo dice n = 107,855. Haz que la nota de fuente use el n real de cada   
  gráfico.                                                                      
  2. Las etiquetas de valor chocan con la línea del total nacional (24.7 % en   
  el de área y 26.0 % en el de jefatura). Pon el texto "Total nacional" en el   
  extremo derecho de la línea, fuera de las barras, y verifica que ninguna      
  etiqueta de valor quede encima de la línea.                                   
  3. En pobreza_departamento_2024.png agrega a la nota de fuente: "Estimación   
  con facpob07; con el método oficial del INEI (factor07 × mieperho) Ica es 6.0 
  % y Puno 39.9 %. Ver salidas/validacion.txt."                                 
  4. En el título de pobreza_departamento_2024.png cambia "y Ica" por "e Ica"   
  (en español "y" se vuelve "e" antes de palabras que empiezan con sonido i).   
  Como el título se genera con los datos, aplica la regla en el código para     
  cualquier nombre que empiece con "I" o con "Hi" seguida de consonante.        
     Regenera las figuras, revísalas y haz commit con (#11).                    
                                                                                
  Después crea .claude/skills/mapeando-enaho: un mapa coroplético de pobreza    
  monetaria por departamento con el GeoJSON                                     
  https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/ 
  06-geoespacial/lab/Data/peru_departamental_simple.geojson (bájalo con curl a  
  referencias/). Reglas:                                                        
  - unir por código, ubigeo[:2] con FIRST_IDDP, nunca por nombre                
  - exigir 25 unidades con dato y fallar si falta alguna                        
  - Lima (15) y Callao (07) separados                                           
  - escala de un color de claro a oscuro desde 0, sin arcoíris; leyenda con la  
  unidad (% de personas)                                                        
  - título analítico y fuente "INEI, ENAHO 2024"                                
  - comparar cada departamento con referencias/pobreza_departamento_2024.csv y  
  guardar las diferencias en salidas/comparacion_mapa.csv, explicando que       
  vienen de facpob07 vs factor07×mieperho                                       
  - guardar en mapas/pobreza_departamento_2024.png                              
    El SKILL.md debe decir: si no existe salidas/personas_2024.parquet, usa     
  primero limpiando-enaho. Córrelo, muéstrame el mapa y haz commit con (#11).   
  ⎿  1 skill available
  Read 1 file (ctrl+o to expand)

● Primero preparo las correcciones del script de gráficos y descargo el GeoJSON
  en paralelo.

  Ran 1 shell command (ctrl+o to expand)

● Los 25 códigos vienen como texto con cero inicial. Ahora reescribo graficar.py
  con las cuatro correcciones.

● Write(.claude\skills\graficando-enaho\scripts\graficar.py)
  ⎿  Added 124 lines, removed 36 lines
       4  
       5  Todas las cifras se ponderan con facpob07 (porcentaje de person
          as). Barras desde cero, un solo
       6  color, valor en cada barra, título analítico, fuente al pie. PN
          G a 200 dpi en --figuras.
       7 +Ninguna etiqueta de valor queda sobre la línea del total nacion
         +al: el script lo verifica y falla si no.                       
       8  """
       9  from __future__ import annotations
      10  
      11  import argparse
      12 +import re                                                      
      13  import sys
      14  import textwrap
      15 +import unicodedata                                             
      16  from pathlib import Path
      17  
      18  import matplotlib
     ...
      40      return NOMBRES.get(n, n.title())
      41  
      42  
      40 -def pct(x: float) -> str:                                      
      41 -    return f"{x:.1f}".replace(".", ",") if False else f"{x:.1f}
         - %"                                                            
      43 +def y_o_e(siguiente: str) -> str:                              
      44 +    """'e' si la palabra siguiente empieza con 'i' o con 'hi' +
         + consonante; en otro caso 'y'.                                 
      45  
      46 +    Regla del proyecto: Ica -> 'e Ica'; Hilda -> 'e Hilda'; Aya
         +cucho, Huánuco -> 'y'.                                         
      47 +    (Casos con diptongo, como 'hielo' o 'hierro', conservan 'y'
         +; no aparecen en nombres de departamento.)                     
      48 +    """                                                        
      49 +    s = unicodedata.normalize("NFD", siguiente.strip().lower())
      50 +    s = "".join(c for c in s if unicodedata.category(c) != "Mn"
         +)                                                              
      51 +    return "e" if re.match(r"(i|hi(?![aeiou]))", s) else "y"   
      52  
      53 +                                                               
      54 +def nota_fuente(anio: int, n: int, extra: str = "") -> str:    
      55 +    base = f"Fuente: INEI, ENAHO {anio} (módulos 02 y 34). Resi
         +dentes habituales, n = {n:,}. Estimaciones ponderadas con facpo
         +b07."                                                          
      56 +    return f"{base} {extra}".strip()                           
      57 +                                                               
      58 +                                                               
      59  def grupo(df: pd.DataFrame, por: str) -> pd.Series:
      60      """Pobreza ponderada (% de personas) por grupo."""
      61      return df.groupby(por).apply(lambda g: tasa_ponderada(g["po
          bre"], g["facpob07"]), include_groups=False)
     ...
       86      print(f"Guardado: {ruta}")
       87  
       88  
       89 +# --- colocación de etiquetas sin choques con la línea del tot
          +al nacional ---------------------------                       
       90 +MARGEN_PX = 4  # separación mínima entre una etiqueta y la lín
          +ea, en píxeles de pantalla                                    
       91 +                                                              
       92 +                                                              
       93 +def _choca(bbox, pos_px: float, eje: str) -> bool:            
       94 +    lo, hi = (bbox.y0, bbox.y1) if eje == "y" else (bbox.x0, b
          +box.x1)                                                       
       95 +    return lo - MARGEN_PX <= pos_px <= hi + MARGEN_PX         
       96 +                                                              
       97 +                                                              
       98 +def poner_valor(fig, ax, texto: str, val: float, pos: float, x
          +: float | None = None, y: float | None = None,                
       99 +                fontsize: float = 12, bold: bool = True) -> pl
          +t.Text:                                                       
      100 +    """Escribe el valor de una barra. Prueba: fuera del extrem
          +o, dentro de la barra, o más allá de la línea.                
      101 +                                                              
      102 +    Barras verticales: x = posición de la barra, la línea es h
          +orizontal (pos = total nacional en y).                        
      103 +    Barras horizontales: y = posición de la barra, la línea es
          + vertical (pos = total nacional en x).                        
      104 +    """                                                       
      105 +    r = fig.canvas.get_renderer()                             
      106 +    vertical = x is not None                                  
      107 +    eje = "y" if vertical else "x"                            
      108 +    pos_px = ax.transData.transform((0, pos) if vertical else 
          +(pos, 0))[1 if vertical else 0]                               
      109 +    cero_px = ax.transData.transform((0, 0))[1 if vertical els
          +e 0]                                                          
      110 +    delta = 0.8 if vertical else 0.5                          
      111 +    if vertical:                                              
      112 +        cands = [(val + delta, "bottom", TEXTO, "fuera"), (val
          + - delta, "top", "white", "dentro"),                          
      113 +                 (max(val, pos) + 1.5 * delta, "bottom", TEXTO
          +, "sobre la línea")]                                          
      114 +    else:                                                     
      115 +        cands = [(val + delta, "left", TEXTO, "fuera"), (val -
          + delta, "right", "white", "dentro"),                          
      116 +                 (max(val, pos) + delta, "left", TEXTO, "tras 
          +la línea")]                                                   
      117 +    for coord, alin, color, _ in cands:                       
      118 +        kw = dict(ha="center", va=alin) if vertical else dict(
          +ha=alin, va="center")                                         
      119 +        t = ax.text(x if vertical else coord, coord if vertica
          +l else y, texto, fontsize=fontsize,                           
      120 +                    fontweight="bold" if bold else "normal", c
          +olor=color, zorder=5, **kw)                                   
      121 +        bb = t.get_window_extent(r)                           
      122 +        dentro_ok = (bb.y0 if vertical else bb.x0) >= cero_px 
          +- 1 if color == "white" else True                             
      123 +        if not _choca(bb, pos_px, eje) and dentro_ok:         
      124 +            return t                                          
      125 +        t.remove()                                            
      126 +    raise RuntimeError(f"No hay posición sin choque para la et
          +iqueta '{texto}'.")                                           
      127 +                                                              
      128 +                                                              
      129 +def verificar_sin_choques(fig, ax, etiquetas: list, pos: float
          +, eje: str) -> None:                                          
      130 +    """Falla si alguna etiqueta de valor queda sobre la línea 
          +del total nacional."""                                        
      131 +    r = fig.canvas.get_renderer()                             
      132 +    pos_px = ax.transData.transform((0, pos) if eje == "y" els
          +e (pos, 0))[1 if eje == "y" else 0]                           
      133 +    malas = [t.get_text() for t in etiquetas if _choca(t.get_w
          +indow_extent(r), pos_px, eje)]                                
      134 +    if malas:                                                 
      135 +        raise RuntimeError(f"Etiquetas sobre la línea del tota
          +l nacional: {malas}")                                         
      136 +    print(f"  verificado: {len(etiquetas)} etiquetas sin choqu
          +e con la línea del total nacional")                           
      137 +                                                              
      138 +                                                              
      139  def barras_verticales(df_vals: pd.Series, etiquetas: list[str]
           , titulo: str, subtitulo: str, nota: str,
      140                        nacional: float, ruta: Path) -> None:
      141      fig, ax = base_figura(titulo, subtitulo, nota, 7.5, 6)
      142      x = np.arange(len(df_vals))
      143      ax.bar(x, df_vals.values, width=0.5, color=COLOR, zorder=3
           )
       79 -    for xi, val in zip(x, df_vals.values):                    
       80 -        ax.text(xi, val + 0.8, f"{val:.1f} %", ha="center", va
          -="bottom", fontsize=12, fontweight="bold", color=TEXTO,       
       81 -                zorder=5, bbox=dict(facecolor="white", edgecol
          -or="none", pad=1.5))                                          
      144      ax.axhline(nacional, color=GRIS, lw=1, ls="--", zorder=2)
       83 -    ax.text((len(df_vals) - 1) / 2, nacional + 0.3, f"Total na
          -cional: {nacional:.1f} %", ha="center",                       
       84 -            va="bottom", fontsize=9, color=GRIS, zorder=5)    
       85 -    ax.set_xlim(-0.6, len(df_vals) - 0.4)                     
      145 +    # Espacio a la derecha para rotular el extremo de la línea
          + fuera de las barras.                                         
      146 +    ax.set_xlim(-0.6, len(df_vals) - 1 + 1.0)                 
      147 +    ax.set_ylim(0, max(df_vals.max(), nacional) * 1.25)       
      148 +    fig.canvas.draw()                                         
      149 +    textos = [poner_valor(fig, ax, f"{v:.1f} %", v, nacional, 
          +x=xi) for xi, v in zip(x, df_vals.values)]                    
      150 +    x_rot = len(df_vals) - 1 + 0.4                            
      151 +    rot = ax.text(x_rot, nacional + 0.4, f"Total nacional\n{na
          +cional:.1f} %", ha="left", va="bottom",                       
      152 +                  fontsize=9, color=GRIS, zorder=5, linespacin
          +g=1.1)                                                        
      153      ax.set_xticks(x, etiquetas, fontsize=11, color=TEXTO)
       87 -    ax.set_ylim(0, max(df_vals.max(), nacional) * 1.2)        
      154      ax.set_ylabel("% de personas en situación de pobreza", fon
           tsize=10, color=GRIS)
      155      ax.yaxis.grid(True, color=REJILLA, zorder=0)
      156      ax.tick_params(axis="y", colors=GRIS, length=0)
      157      ax.tick_params(axis="x", length=0)
      158      ax.spines["left"].set_visible(False)
      159 +    fig.canvas.draw()                                         
      160 +    verificar_sin_choques(fig, ax, textos, nacional, "y")     
      161 +    r = fig.canvas.get_renderer()                             
      162 +    rb = rot.get_window_extent(r)                             
      163 +    if any(rb.overlaps(p.get_window_extent(r)) for p in ax.pat
          +ches):                                                        
      164 +        raise RuntimeError("El rótulo 'Total nacional' se supe
          +rpone con una barra.")                                        
      165      guardar(fig, ruta)
      166  
      167  
       96 -def grafico_area(df, anio, nota, nacional, carpeta):          
      168 +def grafico_area(df, anio, carpeta, nacional):                
      169      urb = df["urbano"]
      170      vals = pd.Series({"Urbano": tasa_ponderada(df.loc[urb, "po
           bre"], df.loc[urb, "facpob07"]),
      171                        "Rural": tasa_ponderada(df.loc[~urb, "po
           bre"], df.loc[~urb, "facpob07"])})
      172      dif = vals["Rural"] - vals["Urbano"]
      173      titulo = f"La pobreza rural ({vals['Rural']:.1f} %) supera
            en {dif:.1f} puntos porcentuales a la urbana ({vals['Urbano']
           :.1f} %), Perú {anio}"
      102 -    barras_verticales(vals, list(vals.index), titulo.replace("
          -, Perú", ",\nPerú"),                                          
      174 +    barras_verticales(vals, list(vals.index), titulo,         
      175                        "Pobreza monetaria por área de residenci
           a · % de personas · urbano = estrato 1 a 5",
      104 -                      nota, nacional, carpeta / f"pobreza_urba
          -no_rural_{anio}.png")                                         
      176 +                      nota_fuente(anio, len(df)), nacional, ca
          +rpeta / f"pobreza_urbano_rural_{anio}.png")                   
      177  
      178  
      107 -def grafico_sexo(df, anio, nota, nacional, carpeta, sexo_de): 
      179 +def grafico_sexo(df, anio, carpeta, nacional, sexo_de):       
      180      if sexo_de == "jefe":
      181          jefes = df.loc[df["p203"] == 1, ["conglome", "vivienda
           ", "hogar", "p207"]].rename(columns={"p207": "sexo_jefe"})
      182          d = df.merge(jefes, on=["conglome", "vivienda", "hogar
           "], how="inner", validate="m:1")
      183          col, etiq = "sexo_jefe", ("Jefe hombre", "Jefa mujer")
      184          frase = ("las personas en hogares con jefe hombre", "l
           as personas en hogares con jefa mujer")
      113 -        sub = (f"Pobreza monetaria según el sexo de quien jefa
          -tura el hogar · % de personas · "                             
      114 -               f"n = {len(d):,} residentes en hogares con jefe
          -/a residente habitual")                                       
      185 +        sub = ("Pobreza monetaria según el sexo de quien jefat
          +ura el hogar · % de personas · "                              
      186 +               "solo hogares cuyo jefe o jefa es residente hab
          +itual")                                                       
      187          arch = f"pobreza_sexo_jefe_hogar_{anio}.png"
      188      else:
      189          d, col, etiq = df, "p207", ("Hombres", "Mujeres")
     ...
      193      g = grupo(d, col)
      194      vals = pd.Series({etiq[0]: g[1], etiq[1]: g[2]})
      195      dif = vals.iloc[1] - vals.iloc[0]
      124 -    if abs(dif) < 1:                                          
      125 -        titulo = (f"La pobreza apenas difiere entre {frase[0].
          -split(' ', 1)[0] if sexo_de == 'persona' else 'hogares'} "    
      126 -                  f"según sexo: {vals.iloc[0]:.1f} % frente a 
          -{vals.iloc[1]:.1f} % (diferencia de {abs(dif):.1f} pp), Perú {
          -anio}")                                                       
      127 -        if sexo_de == "persona":                              
      128 -            titulo = (f"La pobreza apenas difiere entre hombre
          -s ({vals.iloc[0]:.1f} %) y mujeres ({vals.iloc[1]:.1f} %): "  
      129 -                      f"{abs(dif):.1f} puntos porcentuales, Pe
          -rú {anio}")                                                   
      196 +    if abs(dif) < 1 and sexo_de == "persona":                 
      197 +        titulo = (f"La pobreza apenas difiere entre hombres ({
          +vals.iloc[0]:.1f} %) y mujeres ({vals.iloc[1]:.1f} %): "      
      198 +                  f"{abs(dif):.1f} puntos porcentuales, Perú {
          +anio}")                                                       
      199 +    elif abs(dif) < 1:                                        
      200 +        titulo = (f"La pobreza apenas difiere según el sexo de
          + la jefatura del hogar: {vals.iloc[0]:.1f} % con jefe hombre "
      201 +                  f"y {vals.iloc[1]:.1f} % con jefa mujer, Per
          +ú {anio}")                                                    
      202      else:
      203          k = 1 if dif > 0 else 0
      204          titulo = (f"La pobreza afecta más a {frase[k]} ({vals.
           iloc[k]:.1f} %) que a {frase[1 - k]} "
      205                    f"({vals.iloc[1 - k]:.1f} %): {abs(dif):.1f}
            puntos porcentuales, Perú {anio}")
      134 -    barras_verticales(vals, list(vals.index), titulo, sub, not
          -a, nacional, carpeta / arch)                                  
      206 +    # n real de cada gráfico: en el de jefatura son solo los r
          +esidentes de hogares con jefe/a residente.                    
      207 +    barras_verticales(vals, list(vals.index), titulo, sub, not
          +a_fuente(anio, len(d)), nacional, carpeta / arch)             
      208  
      209  
      137 -def grafico_departamento(df, anio, nota, nacional, carpeta):  
      210 +def nota_departamento(anio: int, n: int, g: pd.Series, referen
          +cias: Path) -> str:                                           
      211 +    """Nota de fuente con el contraste del método oficial; las
          + cifras salen del CSV de referencia."""                       
      212 +    extra = ""                                                
      213 +    ref_csv = referencias / "pobreza_departamento_2024.csv"   
      214 +    if ref_csv.exists():                                      
      215 +        ref = pd.read_csv(ref_csv, dtype={"ccdd": str}).set_in
          +dex("ccdd")["pobreza_pct"].reindex(g.index)                   
      216 +        menor = g.idxmin()                                    
      217 +        dif = (g - ref).abs().drop(menor)                     
      218 +        mayor = dif.idxmax()                                  
      219 +        extra = (f"Estimación con facpob07; con el método ofic
          +ial del INEI (factor07 × mieperho) {nombre(menor)} es "       
      220 +                 f"{ref[menor]:.1f} % {y_o_e(nombre(mayor))} {
          +nombre(mayor)} {ref[mayor]:.1f} %. Ver salidas/validacion.txt.
          +")                                                            
      221 +    return nota_fuente(anio, n, extra)                        
      222 +                                                              
      223 +                                                              
      224 +def grafico_departamento(df, anio, carpeta, nacional, referenc
          +ias):                                                         
      225      g = grupo(df, "departamento").sort_values(ascending=False)
      226      etiquetas = [nombre(c) for c in g.index]
      140 -    fig, ax = base_figura(                                    
      141 -        f"{etiquetas[0]} ({g.iloc[0]:.1f} %) tiene la mayor po
          -breza y {etiquetas[-1]} ({g.iloc[-1]:.1f} %) la menor entre lo
          -s 25 departamentos, Perú {anio}",                             
      142 -        "Pobreza monetaria por departamento · % de personas · 
          -ordenado de mayor a menor",                                   
      143 -        nota, 9, 9.6, left=0.16)                              
      227 +    titulo = (f"{etiquetas[0]} ({g.iloc[0]:.1f} %) tiene la ma
          +yor pobreza {y_o_e(etiquetas[-1])} {etiquetas[-1]} "          
      228 +              f"({g.iloc[-1]:.1f} %) la menor entre los 25 dep
          +artamentos, Perú {anio}")                                     
      229 +    fig, ax = base_figura(titulo, "Pobreza monetaria por depar
          +tamento · % de personas · ordenado de mayor a menor",         
      230 +                          nota_departamento(anio, len(df), g, 
          +referencias), 9, 9.6, left=0.16)                              
      231      y = np.arange(len(g))
      232      ax.barh(y, g.values, height=0.65, color=COLOR, zorder=3)
      146 -    for yi, val in zip(y, g.values):                          
      147 -        ax.text(val + 0.5, yi, f"{val:.1f} %", va="center", ha
          -="left", fontsize=9.5, color=TEXTO, zorder=5,                 
      148 -                bbox=dict(facecolor="white", edgecolor="none",
          - pad=1.2))                                                    
      233      ax.axvline(nacional, color=GRIS, lw=1, ls="--", zorder=2)
      150 -    ax.text(nacional + 0.4, len(g) - 1, f"Total nacional: {nac
          -ional:.1f} %", fontsize=9, color=GRIS, va="center")           
      234 +    ax.set_xlim(0, g.max() * 1.12)                            
      235      ax.set_yticks(y, etiquetas, fontsize=10, color=TEXTO)
      236      ax.invert_yaxis()
      153 -    ax.set_xlim(0, g.max() * 1.12)                            
      237 +    fig.canvas.draw()                                         
      238 +    textos = [poner_valor(fig, ax, f"{v:.1f} %", v, nacional, 
          +y=yi, fontsize=9.5, bold=False) for yi, v in zip(y, g.values)]
      239 +    ax.text(nacional + 0.4, len(g) - 1, f"Total nacional: {nac
          +ional:.1f} %", fontsize=9, color=GRIS, va="center")           
      240      ax.set_xlabel("% de personas en situación de pobreza", fon
           tsize=10, color=GRIS)
      241      ax.xaxis.grid(True, color=REJILLA, zorder=0)
      242      ax.tick_params(axis="x", colors=GRIS, length=0)
      243      ax.tick_params(axis="y", length=0)
      244      ax.spines["left"].set_visible(False)
      245 +    fig.canvas.draw()                                         
      246 +    verificar_sin_choques(fig, ax, textos, nacional, "x")     
      247      guardar(fig, carpeta / f"pobreza_departamento_{anio}.png")
      248  
      249  
     ...
      254      ap.add_argument("--anio", type=int, default=2024)
      255      ap.add_argument("--base", type=Path, default=None)
      256      ap.add_argument("--figuras", type=Path, default=Path("figu
           ras"))
      257 +    ap.add_argument("--referencias", type=Path, default=Path("
          +referencias"))                                                
      258      a = ap.parse_args()
      259      base = a.base or Path("salidas") / f"personas_{a.anio}.par
           quet"
      260      if not base.exists():
     ...
      263      df = pd.read_parquet(base)
      264      df["departamento"] = df["departamento"].astype(str)
      265      nacional = tasa_ponderada(df["pobre"], df["facpob07"])
      177 -    nota = f"Fuente: INEI, ENAHO {a.anio} (módulos 02 y 34). R
          -esidentes habituales, n = {len(df):,}. Estimaciones ponderadas
          - con facpob07."                                               
      266      if a.grafico in ("area", "todos"):
      179 -        grafico_area(df, a.anio, nota, nacional, a.figuras)   
      267 +        grafico_area(df, a.anio, a.figuras, nacional)         
      268      if a.grafico in ("sexo", "todos"):
      181 -        grafico_sexo(df, a.anio, nota, nacional, a.figuras, a.
          -sexo_de)                                                      
      269 +        grafico_sexo(df, a.anio, a.figuras, nacional, a.sexo_d
          +e)                                                            
      270      if a.grafico in ("departamento", "todos"):
      183 -        grafico_departamento(df, a.anio, nota, nacional, a.fig
          -uras)                                                         
      271 +        grafico_departamento(df, a.anio, a.figuras, nacional, 
          +a.referencias)                                                
      272      return 0
      273  
      274  

  Read 4 files, ran 1 shell command (ctrl+o to expand)

● Las figuras quedan bien y el script verificó que no hay choques. Hago el
  commit y paso al mapa.

  Ran 1 shell command (ctrl+o to expand)

● Write(.claude\skills\mapeando-enaho\scripts\mapear.py)
  ⎿  Wrote 168 lines to .claude\skills\mapeando-enaho\scripts\mapear.py
      1 """Mapa coroplético de pobreza monetaria departamental (ENAHO) de
        sde salidas/personas_AAAA.parquet.
      2 
      3     uv run mapear.py [--anio 2024]
      4 
      5 Une indicadores y geometrías por código (ubigeo[:2] = FIRST_IDDP)
        , nunca por nombre. Falla si no hay
      6 exactamente 25 departamentos con dato o si Lima (15) y Callao (07
        ) no están separados.
      7 Salidas: mapas/pobreza_departamento_AAAA.png y salidas/comparacio
     … +162 lines (~8 KB) (ctrl+o to expand)

  Read 1 file, ran 2 shell commands (ctrl+o to expand)

● Aprovecho para quitar la repetición de "facpob07" en la nota. También pruebo
  que el script falla si falta un departamento.

  Ran 1 shell command (ctrl+o to expand)

● Write(.claude\skills\mapeando-enaho\SKILL.md)
  ⎿  Wrote 40 lines to .claude\skills\mapeando-enaho\SKILL.md
       1 ---
       2 name: mapeando-enaho
       3 description: Construye el mapa coroplético de pobreza monetaria 
         por departamento con la ENAHO 2024 del INEI (25 departamentos, L
         ima y Callao separados, PNG en mapas/). Úsala cuando pidan un ma
         pa, mapa coroplético o distribución territorial de la pobreza po
         r departamento o región del Perú.
       4 argument-hint: [año]
       5 ---
       6 # Mapear la pobreza por departamento
     … +34 lines (ctrl+o to expand)

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● Las cuatro correcciones de los gráficos y la skill mapeando-enaho están
  listas, y las dos cosas quedaron en commits con (#11): d58de76 para los
  gráficos y 9d92797 para el mapa. No hice push.

  Correcciones a los gráficos

  Regeneré las cuatro figuras y las revisé una por una.

  1. n real por gráfico. La nota de fuente ahora usa el n de cada figura. En la
     de jefatura dice n = 107,855, igual que antes decía el subtítulo. Quité el
     n del subtítulo para no duplicarlo.
  2. Etiquetas contra la línea del total nacional.
     - "Total nacional" va ahora en el extremo derecho de la línea, fuera de las
       barras.
     - Cada valor se coloca solo si no choca con la línea: primero fuera de la
       barra, luego dentro en blanco y, si no cabe, más allá de la línea.
     - En el gráfico de área el 24.7 % quedó dentro de la barra. En el de
       jefatura pasó lo mismo con el 26.0 %.
     - Lo mismo aplica al gráfico por departamento: 7 etiquetas cercanas a 27.5
       % ahora van dentro de la barra.
     - El script comprueba el resultado y falla si alguna etiqueta queda encima
       de la línea. Pasó en las cuatro figuras.
  3. Nota del gráfico departamental. Agregué el texto del método oficial. Los
     valores 6.0 % y 39.9 % salen del CSV de referencia, no están escritos a
     mano.
  4. "y" o "e". Ahora dice "mayor pobreza e Ica". La regla está en la función
     y_o_e(). La probé con varios nombres: Ica, Hilda e Iquitos dan "e";
     Ayacucho, Huánuco y Puno dan "y"; Hierro y Hiato conservan "y".

  Mapa

  El mapa está en mapas/pobreza_departamento_2024.png. El título dice que la
  pobreza va de 5.9 % en Ica a 45.0 % en Cajamarca, y que 10 de 25 departamentos
  superan el total nacional (27.5 %).

  - Unión por código: une ubigeo[:2] con FIRST_IDDP, ambos como texto, y no por
    nombre.
  - Validaciones: exige 25 departamentos con dato y Lima (15) y Callao (07)
    separados. Probé quitando Callao de la base y el script falló con código 1 y
    el mensaje faltan ['07'].
  - Color: un solo tono, Blues, de claro a oscuro y desde 0 %. La leyenda dice
    "% de personas en situación de pobreza monetaria". Cada departamento lleva
    su valor.
  - Comparación con la referencia: salidas/comparacion_mapa.csv tiene las
    diferencias por departamento. La máxima es 0.52 pp (Puno), y 16 de 25 quedan
    dentro de 0.2 pp. La explicación (facpob07 frente a factor07 × mieperho)
    está en la consola, en el SKILL.md y en la nota al pie del mapa.
  - Callao: es muy pequeño y lo rotulé fuera, en el mar, con una línea que lo
    señala.

  Lo que debes saber

  - Umbral de 1 pp: agregué una regla tuya implícita. Si algún departamento
    difiere más de 1 pp de la referencia, el mapa falla, porque eso ya no se
    explica por el método de ponderación. El valor lo elegí yo, así que dime si
    prefieres otro umbral.
  - Etiquetas del mapa: algunas rozan los bordes, por ejemplo 45.0 (Cajamarca) y
    39.5 (Huánuco). Se leen bien, pero si quieres, las muevo a mano.
  - Activación en lenguaje natural: mapeando-enaho dice que se use primero
    limpiando-enaho si falta la base. Solo probé el caso con el parquet
    presente. El encadenamiento (borrar el parquet y pedir "haz un mapa de la
    pobreza por departamento") queda para la prueba de activación.
  - Avisos de LF y CRLF: los avisos de Git no afectan nada.

✻ Cooked for 4m 24s · done 8:38 AM

※ recap: Estamos cerrando la Parte 2 de la Tarea 4: las tres skills de ENAHO ya existen, con sus gráficos y su mapa, y todo está en commits con (#11). Lo siguiente es probar la activación en lenguaje natural borrando el parquet y pidiendo el mapa.