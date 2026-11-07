<html>
<body>
<!--StartFragment--><html><head></head><body><h1><span>🤖 Tarea 4 – Agente de investigación socioeconómica: MCP, Skills y datos oficiales del Perú</span></h1><h2><span>Pregunta guía del trabajo</span></h2><blockquote><p><strong><span>¿Pueden construir un agente de inteligencia artificial capaz de investigar la realidad socioeconómica peruana utilizando datos oficiales del INEI y el BCRP, combinando servidores MCP, Skills de Claude Code y herramientas de análisis reproducible?</span></strong></p></blockquote><p><span>En este proyecto desarrollarán un </span><strong><span>agente de investigación socioeconómica</span></strong><span> que integre dos fuentes oficiales de información:</span></p><ol start="1"><li><p><strong><span>INEI – ENAHO 2024:</span></strong><span> microdatos para estudiar pobreza monetaria, desigualdades territoriales y características socioeconómicas de la población.</span></p></li><li><p><strong><span>BCRP – Series estadísticas:</span></strong><span> indicadores macroeconómicos para analizar inflación, actividad económica, tipo de cambio u otras variables relevantes.</span></p></li></ol><p><span>El agente deberá interpretar preguntas formuladas en lenguaje natural, consultar las fuentes correspondientes, procesar los datos, ejecutar cálculos verificables y producir gráficos, mapas e informes.</span></p><p><span>El objetivo principal no es construir un chatbot que responda utilizando únicamente su conocimiento previo, sino </span><strong><span>un sistema que utilice herramientas especializadas para producir respuestas verificables y reproducibles</span></strong><span>.</span></p><div><hr></div><h2><span>📌 Instrucciones generales</span></h2><p><span>El trabajo es </span><strong><span>individual</span></strong><span> y corresponde a la </span><strong><span>Tarea 4 del curso Python Intermedio</span></strong><span>.</span></p><h3><span>1. Materiales de referencia</span></h3><p><span>El proyecto deberá integrar los contenidos de las siguientes sesiones:</span></p><p><strong><span>Sesión 04 – MCP: Claude conectado a sus datos</span></strong></p><p><a href="https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-claude-code"><span>https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-claude-code</span></a></p><p><strong><span>Sesión 16 – Skills de Claude Code: limpiar, graficar y mapear la ENAHO</span></strong></p><p><a href="https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho"><span>https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho</span></a></p><p><span>Los estudiantes deberán utilizar como referencia los ejemplos de FastMCP, las pruebas del servidor BCRP y las reglas de procesamiento de la ENAHO.</span></p><p><strong><span>No será suficiente copiar y ejecutar los proyectos de las sesiones por separado.</span></strong><span> La tarea exige integrarlos en un agente funcional, desarrollar componentes propios y evaluar su desempeño.</span></p><h3><span>2. Herramientas y tecnologías</span></h3><p><span>Se utilizarán:</span></p><ul><li><p><strong><span>Claude Code:</span></strong><span> agente principal para coordinar el proyecto.</span></p></li><li><p><strong><span>Python y </span></strong><code><strong><span>uv</span></strong></code><strong><span>:</span></strong><span> desarrollo y gestión del entorno.</span></p></li><li><p><strong><span>FastMCP:</span></strong><span> construcción del servidor MCP.</span></p></li><li><p><strong><span>Pandas y PyArrow:</span></strong><span> procesamiento de microdatos.</span></p></li><li><p><strong><span>GeoPandas:</span></strong><span> análisis y representación territorial.</span></p></li><li><p><strong><span>Matplotlib o Plotly:</span></strong><span> generación de visualizaciones.</span></p></li><li><p><strong><span>Pytest:</span></strong><span> pruebas automatizadas.</span></p></li><li><p><strong><span>Git y GitHub:</span></strong><span> versionamiento, documentación y entrega.</span></p></li></ul><p><span>Pueden incorporar otras bibliotecas o herramientas cuando su utilización esté justificada.</span></p><h3><span>3. Datos obligatorios</span></h3>
Fuente | Datos | Uso
-- | -- | --
INEI | ENAHO 2024, módulo 34 (sumaria) | Pobreza e indicadores de hogares
INEI | ENAHO 2024, módulo 02 (miembros) | Características individuales
Repositorio del curso | Límites departamentales del Perú | Mapas territoriales
BCRP | Series estadísticas oficiales | Análisis macroeconómico

<p><span>La penalización se aplicará sobre la nota obtenida según la rúbrica de 20 puntos, sin que la calificación final pueda ser inferior a 0.</span></p><p><span>Se recomienda comprobar con anticipación que:</span></p><ul><li><p><span>El repositorio y todos los enlaces sean accesibles.</span></p></li><li><p><span>Los scripts, pruebas y resultados estén correctamente guardados.</span></p></li><li><p><span>Las evidencias del uso de IA estén completas.</span></p></li><li><p><span>No se hayan publicado credenciales ni información sensible.</span></p></li><li><p><span>El comentario de entrega se haya registrado correctamente dentro del plazo.</span></p></li></ul><div><hr></div><h2><span>🎯 Resultado esperado</span></h2><p><span>Al finalizar esta tarea, cada estudiante deberá contar con un </span><strong><span>agente de investigación socioeconómica funcional</span></strong><span>, capaz de consultar información oficial del BCRP mediante MCP, procesar y analizar microdatos de ENAHO mediante Skills y elaborar informes con resultados verificables.</span></p><p><strong><span>El proyecto estará completo cuando el agente pueda responder una pregunta real utilizando ambas herramientas, y cuando otra persona pueda reproducir, evaluar y comprobar los resultados obtenidos.</span></strong></p><p><span>El propósito es desarrollar competencias para construir sistemas de inteligencia artificial que no se limiten a generar respuestas, sino que sean capaces de </span><strong><span>utilizar herramientas, ejecutar procedimientos reproducibles y producir evidencia confiable para el análisis de datos y la investigación social</span></strong><span>.</span></p><p><strong><span>¡Éxitos con sus proyectos!</span></strong><span> 🚀</span></p></body></html><!--EndFragment-->
</body>
</html># 🤖 Tarea 4 – Agente de investigación socioeconómica: MCP, Skills y datos oficiales del Perú

## Pregunta guía del trabajo

> **¿Pueden construir un agente de inteligencia artificial capaz de investigar la realidad socioeconómica peruana utilizando datos oficiales del INEI y el BCRP, combinando servidores MCP, Skills de Claude Code y herramientas de análisis reproducible?**

En este proyecto desarrollarán un **agente de investigación socioeconómica** que integre dos fuentes oficiales de información:

1. **INEI – ENAHO 2024:** microdatos para estudiar pobreza monetaria, desigualdades territoriales y características socioeconómicas de la población.
2. **BCRP – Series estadísticas:** indicadores macroeconómicos para analizar inflación, actividad económica, tipo de cambio u otras variables relevantes.

El agente deberá interpretar preguntas formuladas en lenguaje natural, consultar las fuentes correspondientes, procesar los datos, ejecutar cálculos verificables y producir gráficos, mapas e informes.

El objetivo principal no es construir un chatbot que responda utilizando únicamente su conocimiento previo, sino **un sistema que utilice herramientas especializadas para producir respuestas verificables y reproducibles**.

---

## 📌 Instrucciones generales

El trabajo es **individual** y corresponde a la **Tarea 4 del curso Python Intermedio**.

### 1. Materiales de referencia

El proyecto deberá integrar los contenidos de las siguientes sesiones:

**Sesión 04 – MCP: Claude conectado a sus datos**

https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-claude-code

**Sesión 16 – Skills de Claude Code: limpiar, graficar y mapear la ENAHO**

https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho

Los estudiantes deberán utilizar como referencia los ejemplos de FastMCP, las pruebas del servidor BCRP y las reglas de procesamiento de la ENAHO.

**No será suficiente copiar y ejecutar los proyectos de las sesiones por separado.** La tarea exige integrarlos en un agente funcional, desarrollar componentes propios y evaluar su desempeño.

### 2. Herramientas y tecnologías

Se utilizarán:

- **Claude Code:** agente principal para coordinar el proyecto.
- **Python y `uv`:** desarrollo y gestión del entorno.
- **FastMCP:** construcción del servidor MCP.
- **Pandas y PyArrow:** procesamiento de microdatos.
- **GeoPandas:** análisis y representación territorial.
- **Matplotlib o Plotly:** generación de visualizaciones.
- **Pytest:** pruebas automatizadas.
- **Git y GitHub:** versionamiento, documentación y entrega.

Pueden incorporar otras bibliotecas o herramientas cuando su utilización esté justificada.

### 3. Datos obligatorios

| Fuente | Datos | Uso |
|---|---|---|
| INEI | ENAHO 2024, módulo 34 (sumaria) | Pobreza e indicadores de hogares |
| INEI | ENAHO 2024, módulo 02 (miembros) | Características individuales |
| Repositorio del curso | Límites departamentales del Perú | Mapas territoriales |
| BCRP | Series estadísticas oficiales | Análisis macroeconómico |

**Enlaces de referencia:**

- [[ENAHO 2024 – Módulo 34](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip)](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip)
- [[ENAHO 2024 – Módulo 02](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip)](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip)
- [[GeoJSON departamental del Perú](https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson)](https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson)
- [[Estadísticas del BCRP](https://estadisticas.bcrp.gob.pe/estadisticas/series/)](https://estadisticas.bcrp.gob.pe/estadisticas/series/)

**Valores de referencia para validar ENAHO 2024:**

| Indicador | Referencia |
|---|---:|
| Pobreza monetaria nacional | Aproximadamente 27.6 % |
| Residentes habituales | 108,664 |
| Unidades territoriales del mapa | 25 |
| Pobreza urbana | Aproximadamente 24.8 % |
| Pobreza rural | Aproximadamente 39.3 % |

Las estimaciones deberán reproducir razonablemente las cifras de referencia, admitiendo diferencias de redondeo y ponderación debidamente explicadas. Para la pobreza nacional se aceptará una diferencia máxima de 0.1 puntos porcentuales respecto del 27.6 % de referencia.

> [!IMPORTANT]
> Los cálculos de ENAHO deben aplicar correctamente los factores de expansión y respetar la unidad de análisis. No se aceptarán promedios simples cuando corresponda una estimación ponderada.
>
> Tampoco se deberán presentar asociaciones descriptivas como relaciones causales demostradas.
>
> **Las cifras no pueden introducirse manualmente como resultados:** deben obtenerse mediante el procesamiento de los datos y validarse posteriormente.

---

## 🤖 Uso de inteligencia artificial y evidencias de desarrollo

**Se permite y fomenta el uso de herramientas de inteligencia artificial durante todas las etapas del proyecto.**

Los estudiantes podrán utilizar Claude Code, ChatGPT, Codex, OpenCode, Gemini u otros asistentes para:

- Desarrollar y depurar código en Python.
- Configurar servidores MCP.
- Crear, modificar y ejecutar Skills.
- Procesar datos y elaborar visualizaciones.
- Diseñar pruebas automatizadas.
- Identificar y corregir errores.
- Interpretar resultados y preparar el informe final.

**No se evaluará cuánto código escribieron manualmente**, sino la funcionalidad, calidad técnica, reproducibilidad y validez de los resultados.

Sin embargo, cada estudiante deberá comprender el funcionamiento de su proyecto, verificar sus resultados y garantizar que los componentes desarrollados cumplan los requisitos establecidos.

### Evidencias obligatorias

Como requisito de entrega, deberán presentar **el registro completo de las conversaciones utilizadas con asistentes de inteligencia artificial durante el desarrollo del proyecto**, mediante una de las siguientes modalidades:

**Opción A – Capturas de pantalla**

- Capturas legibles de las conversaciones completas.
- Archivos numerados y organizados cronológicamente.
- Deben permitir identificar las instrucciones proporcionadas y las respuestas del asistente.

**Opción B – Exportación de conversaciones**

- Exportación del historial completo de las sesiones utilizadas.
- Se aceptarán formatos como Markdown, TXT, JSON o HTML.
- Los archivos deben permitir reconstruir el proceso de desarrollo.

En ambos casos, las evidencias deberán abarcar el desarrollo del servidor MCP, las Skills, la integración del agente, las pruebas, las correcciones y el informe final.

Todos los archivos deberán almacenarse en una carpeta `evidencias_ia/` dentro del repositorio. Si el tamaño impide subirlos a GitHub, se podrá incluir un enlace público a una carpeta externa que contenga las evidencias completas.

> [!WARNING]
> Antes de publicar las conversaciones, deberán ocultar claves API, contraseñas, tokens, datos personales e información confidencial.
>
> **No se aceptarán únicamente capturas aisladas de los resultados finales como sustituto del historial de desarrollo.**
>
> La documentación del uso de IA es obligatoria y será considerada en la evaluación de documentación y reproducibilidad.

---

## 🗂️ Organización del repositorio

Cada estudiante deberá crear una carpeta `tarea_4/` dentro de su repositorio del curso o utilizar un repositorio público independiente.

La estructura esperada es:

```text
tarea_4/
├── README.md
├── pyproject.toml
├── .mcp.json
├── .gitignore
│
├── mcp/
│   ├── server.py
│   └── test_server.py
│
├── .claude/
│   └── skills/
│       ├── limpiando-enaho/
│       │   ├── SKILL.md
│       │   ├── reference.md
│       │   └── scripts/
│       │       └── limpiar.py
│       │
│       ├── graficando-enaho/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │
│       └── mapeando-enaho/
│           ├── SKILL.md
│           └── scripts/
│
├── datos/
│   └── (microdatos originales ignorados por Git)
│
├── salidas/
│   ├── validacion.txt
│   └── indicadores.csv
│
├── figuras/
├── mapas/
│
├── evaluacion/
│   ├── preguntas.csv
│   ├── resultados.csv
│   └── comparacion.md
│
├── informes/
│   └── informe_final.md
│
└── evidencias_ia/
    ├── mcp/
    ├── skills/
    ├── integracion/
    └── evaluacion/
```

La organización puede adaptarse a las necesidades del proyecto, siempre que los archivos obligatorios sean identificables y el sistema pueda ejecutarse siguiendo las instrucciones del README.

**No deben subirse microdatos originales pesados, archivos temporales, credenciales ni información sensible.** Los datos originales deberán incluirse en `.gitignore`, y el README deberá explicar cómo descargarlos y reproducir el procesamiento.

Las evidencias del uso de IA deben mantenerse separadas de los datos originales y de los archivos de resultados.

### Flujo de trabajo en GitHub

Se espera que los estudiantes:

1. Utilicen Git para registrar el desarrollo.
2. Realicen commits descriptivos a medida que avanzan.
3. Mantengan los archivos del proyecto organizados.
4. Documenten los requisitos, dependencias e instrucciones de ejecución.
5. Publiquen un repositorio accesible para su revisión.

---

## 📊 Criterios de calificación (sobre 20 puntos)

| Componente | Puntos |
|---|:---:|
| **Parte 1 – Servidor MCP del BCRP** | **5 pts** |
| **Parte 2 – Skills para procesar y analizar ENAHO** | **6 pts** |
| **Parte 3 – Integración y agente de investigación** | **5 pts** |
| **Parte 4 – Evaluación, documentación y reproducibilidad** | **4 pts** |
| **Total** | **20 pts** |

---

# 🔌 Parte 1 – Servidor MCP del BCRP [5 pts]

El primer componente consiste en implementar un servidor MCP funcional que permita a Claude Code consultar series estadísticas oficiales del Banco Central de Reserva del Perú.

### Archivo principal: `mcp/server.py`

### Pasos requeridos

**1. Construcción del servidor**

Tomar como referencia el proyecto de la Sesión 04:

https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-claude-code/proyecto

Completar y adaptar `server.py`, implementando como mínimo cuatro herramientas:

| Herramienta | Función |
|---|---|
| `buscar_series` | Encontrar series oficiales mediante palabras clave |
| `serie` | Descargar datos de una serie para un período determinado |
| `resumen` | Calcular variaciones, promedios, mínimos y máximos |
| Herramienta propia | Incorporar una funcionalidad adicional de análisis |

La herramienta propia deberá ser útil y no limitarse a duplicar las funciones anteriores.

Por ejemplo:

- `comparar_series`: comparar dos indicadores en períodos compatibles.
- `correlacion`: calcular la correlación entre series, alineando períodos y tratando valores faltantes.
- `graficar_serie`: generar y guardar un gráfico de una serie oficial.
- `comparar_periodos`: comparar el comportamiento de un indicador entre dos intervalos.

Los cálculos numéricos deberán realizarse mediante código Python y no mediante estimaciones improvisadas del modelo de lenguaje.

**2. Recursos y prompts MCP**

Implementar como mínimo:

- Un recurso MCP que permita consultar información descriptiva de una serie.
- Un prompt MCP reutilizable para generar informes o interpretar indicadores.

Ambos deberán ser accesibles desde el cliente MCP utilizado.

**3. Integración con Claude Code**

Configurar el servidor mediante `.mcp.json` y demostrar su funcionamiento desde Claude Code.

El agente deberá poder:

1. Identificar una serie estadística.
2. Solicitar los datos correspondientes.
3. Ejecutar cálculos mediante las herramientas.
4. Presentar el resultado con su código de serie, período y fuente.

**4. Pruebas automatizadas**

El servidor deberá superar:

- Las **8 pruebas originales** del proyecto de la Sesión 04.
- **2 pruebas adicionales** diseñadas por el estudiante para evaluar su herramienta propia.

Las pruebas originales no deberán modificarse para facilitar su aprobación. Solo podrán realizarse los ajustes de importación necesarios si cambia la ubicación de los archivos.

El resultado esperado será:

```text
10 passed
```

### Rúbrica Parte 1 [5 pts]

| Criterio | Pts |
|---|:---:|
| Servidor funcional con búsqueda, consulta y resumen de series | 2.0 |
| Herramienta propia útil, validada y documentada | 1.0 |
| Recurso, prompt e integración efectiva con Claude Code | 1.0 |
| 10 pruebas automatizadas aprobadas | 1.0 |
| **Total** | **5.0** |

---

# 📊 Parte 2 – Skills para procesar y analizar ENAHO [6 pts]

El segundo componente consiste en desarrollar **tres Skills reutilizables** siguiendo la metodología de la Sesión 16.

No será suficiente escribir las instrucciones en `SKILL.md`. Cada Skill deberá ejecutar código funcional y generar resultados verificables.

## Skill 1 – `limpiando-enaho`

Desarrollar una Skill capaz de:

1. Leer los módulos 34 y 02 de ENAHO 2024.
2. Normalizar los nombres de las variables.
3. Filtrar residentes habituales.
4. Unir correctamente personas y hogares utilizando las llaves `conglome`, `vivienda` y `hogar`.
5. Construir indicadores de pobreza, departamento y área geográfica.
6. Aplicar los factores de expansión correspondientes.
7. Ejecutar validaciones y generar `salidas/validacion.txt`.

### Reglas técnicas

La lectura de los archivos Stata deberá respetar los tipos de datos de las llaves, evitando perder ceros iniciales.

El filtro de residentes habituales seguirá la condición utilizada en la sesión:

```python
((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))
```

La unión entre la base de personas y hogares deberá utilizar:

```python
merge(..., validate="m:1")
```

La Skill deberá verificar que la unión no genere duplicaciones inesperadas.

### Validaciones mínimas

- Pobreza monetaria nacional cercana a 27.6 %.
- 108,664 residentes habituales.
- Identificación correcta de los 25 códigos territoriales.
- Ninguna duplicación indebida de registros.
- Aplicación correcta de los factores de expansión.

El archivo `validacion.txt` deberá mostrar los resultados y señalar las verificaciones aprobadas y fallidas.

Si una validación esencial falla, la Skill deberá detener el proceso o devolver un mensaje de error explícito. No se aceptará corregir artificialmente los resultados para que coincidan con los valores de referencia.

## Skill 2 – `graficando-enaho`

Desarrollar una Skill que produzca visualizaciones a partir de los datos procesados.

Deberá permitir solicitar gráficos mediante lenguaje natural y generar, como mínimo:

1. Pobreza monetaria según área urbana y rural.
2. Pobreza por sexo u otro grupo demográfico pertinente.
3. Comparación de pobreza entre departamentos.

### Requisitos de visualización

- Utilizar estimaciones ponderadas.
- Presentar títulos claros y analíticos.
- Identificar el período y las unidades.
- Incluir la fuente de información.
- Utilizar escalas y representaciones apropiadas.
- Guardar los resultados en `figuras/`.

Los gráficos deberán permitir interpretar diferencias reales y no limitarse a mostrar datos sin contexto.

## Skill 3 – `mapeando-enaho`

Desarrollar una Skill capaz de construir un mapa coroplético de pobreza monetaria departamental.

### Requisitos

- Unir los indicadores y las geometrías mediante códigos territoriales.
- Utilizar `ubigeo[:2]` y `FIRST_IDDP` como llaves de referencia.
- Representar las 25 unidades territoriales.
- Mantener Lima y Callao separados.
- Incorporar una escala de colores interpretable.
- Mostrar la unidad de medida en la leyenda.
- Comparar los resultados con el archivo de referencia de la Sesión 16.

El mapa deberá guardarse en `mapas/`.

No se aceptarán uniones realizadas únicamente por nombres de departamentos cuando exista una llave oficial de identificación.

## Activación y coordinación de las Skills

Las tres Skills deberán encontrarse dentro de `.claude/skills/` y contar con un archivo `SKILL.md` correctamente estructurado.

Se deberá demostrar que:

- Pueden invocarse individualmente.
- Pueden activarse mediante solicitudes en lenguaje natural.
- Las Skills de gráficos y mapas pueden ejecutar previamente la Skill de limpieza cuando no exista la base procesada.

Por ejemplo, ante el pedido:

> Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.

Claude Code deberá identificar que necesita una base procesada y, si esta no existe, ejecutar primero `limpiando-enaho` y después `mapeando-enaho`.

### Rúbrica Parte 2 [6 pts]

| Criterio | Pts |
|---|:---:|
| Skill de limpieza funcional, ponderación y validación de ENAHO | 2.5 |
| Skill de gráficos con indicadores correctos | 1.5 |
| Skill de mapas con unión territorial y 25 unidades | 1.5 |
| Activación automática y coordinación entre Skills | 0.5 |
| **Total** | **6.0** |

---

# 🧠 Parte 3 – Agente de investigación socioeconómica [5 pts]

Esta es la **parte central e integradora del proyecto**.

El estudiante deberá construir un flujo de trabajo en el que Claude Code utilice coordinadamente el servidor MCP del BCRP y las Skills de ENAHO para desarrollar una investigación breve sobre la economía y las condiciones sociales del Perú.

## 1. Formulación de la pregunta de investigación

Cada estudiante deberá formular una pregunta propia que requiera información de **ambas fuentes oficiales**.

Ejemplo:

> ¿Cómo evolucionó la inflación peruana entre 2020 y 2024 y qué diferencias territoriales presentaba la pobreza monetaria al finalizar ese período?

Otros temas posibles:

- Evolución de la actividad económica y características territoriales de la pobreza.
- Inflación y diferencias socioeconómicas entre áreas urbanas y rurales.
- Evolución de indicadores macroeconómicos y desigualdades regionales.
- Tipo de cambio, precios y características de los hogares peruanos.

Los estudiantes podrán elegir otros temas, siempre que sean compatibles con las fuentes y permitan formular un análisis coherente.

> [!IMPORTANT]
> No se exige demostrar una relación causal entre las variables macroeconómicas y la pobreza. Si se utilizan datos de diferentes niveles de agregación o períodos, el informe deberá reconocer esas limitaciones.
>
> **No se aceptarán preguntas que utilicen únicamente el BCRP o únicamente ENAHO.**

## 2. Ejecución del agente

El agente deberá realizar las siguientes operaciones:

1. Interpretar la pregunta y preparar un plan de análisis.
2. Consultar las series oficiales necesarias mediante el MCP.
3. Ejecutar las Skills de procesamiento y análisis de ENAHO.
4. Construir indicadores y visualizaciones.
5. Contrastar los resultados con las fuentes oficiales.
6. Elaborar un informe final reproducible.

### Condición obligatoria de integración

En una misma ejecución demostrable deberán utilizarse:

- **Al menos 2 herramientas MCP distintas.**
- **Al menos 2 Skills distintas.**

No se aceptará ejecutar ambos proyectos de manera completamente independiente y luego copiar manualmente los resultados a un documento.

La evidencia deberá mostrar que Claude Code coordinó las herramientas necesarias para completar la investigación.

## 3. Informe final de investigación

El agente deberá generar:

`informes/informe_final.md`

El documento deberá contener:

1. **Pregunta de investigación:** tema, objetivo y delimitación del análisis.
2. **Fuentes y metodología:** datos utilizados, procesamiento e indicadores.
3. **Resultados:** al menos 3 hallazgos sustentados.
4. **Visualizaciones:** un gráfico del BCRP, un gráfico elaborado con ENAHO y un mapa departamental.
5. **Interpretación:** explicación de los principales patrones identificados.
6. **Limitaciones:** cobertura temporal, calidad de los datos y alcance de las conclusiones.
7. **Reproducibilidad:** referencias a los scripts, archivos y series utilizadas.

Todas las cifras deberán poder rastrearse hasta la fuente original o el procesamiento correspondiente.

No se aceptarán afirmaciones numéricas sin sustento o referencias inventadas.

## 4. Verificación de resultados

El estudiante deberá comprobar manualmente al menos **3 afirmaciones numéricas del informe**, incluyendo resultados provenientes de ambas fuentes.

Deberá documentar:

- La afirmación del informe.
- El valor calculado.
- La fuente o procedimiento de verificación.
- Si el resultado coincide con la referencia.
- Cualquier diferencia observada.

Cuando una herramienta falle, no encuentre datos o devuelva una respuesta incompatible, el agente deberá informar esa limitación en lugar de inventar resultados.

### Rúbrica Parte 3 [5 pts]

| Criterio | Pts |
|---|:---:|
| Pregunta pertinente y planificación coherente | 0.5 |
| Orquestación real de MCP y Skills en una ejecución | 2.0 |
| Informe con tres hallazgos, gráficos, mapa e interpretación | 1.5 |
| Verificación de cifras y manejo de errores | 1.0 |
| **Total** | **5.0** |

---

# 🧪 Parte 4 – Evaluación, documentación y reproducibilidad [4 pts]

El último componente consiste en evaluar si el uso de MCP y Skills mejora la calidad de las respuestas producidas por Claude Code.

La evaluación deberá utilizar preguntas con respuestas verificables, comparar condiciones equivalentes y documentar los resultados.

## 1. Diseño del experimento

Construir un conjunto de **10 preguntas de evaluación**:

| Tipo de pregunta | Cantidad |
|---|:---:|
| Indicadores del BCRP | 4 |
| Indicadores de ENAHO | 4 |
| Preguntas que combinan ambas fuentes | 2 |
| **Total** | **10** |

Las preguntas deberán tener respuestas esperadas verificadas mediante fuentes oficiales o cálculos independientes.

No se aceptarán preguntas cuyas respuestas correctas hayan sido inventadas o definidas únicamente a partir de lo que respondió el agente.

Guardar el conjunto de preguntas en:

`evaluacion/preguntas.csv`

## 2. Comparación de dos configuraciones

Cada estudiante deberá ejecutar las mismas 10 preguntas bajo dos condiciones.

### Modo A – Sin MCP ni Skills personalizados

Claude Code deberá responder sin acceso al servidor MCP desarrollado ni a las Skills del proyecto.

Este modo permitirá observar su desempeño sin los componentes especializados.

### Modo B – Con MCP y Skills

Claude Code dispondrá del servidor MCP y las Skills desarrolladas.

Deberá poder consultar fuentes, procesar datos y ejecutar cálculos mediante esas herramientas.

### Condiciones del experimento

- Utilizar las mismas 10 preguntas.
- Mantener, en lo posible, el mismo modelo y las mismas instrucciones.
- Ejecutar las preguntas en sesiones independientes para evitar que respuestas anteriores contaminen la comparación.
- Documentar qué otras herramientas estaban habilitadas en cada modo.
- Evitar que el modo sin herramientas personalizadas acceda indirectamente a archivos con las respuestas ya calculadas.
- No modificar las respuestas esperadas después de observar los resultados.

## 3. Métricas de evaluación

Para cada pregunta registrar:

- Pregunta formulada.
- Respuesta esperada.
- Respuesta generada.
- Fuente utilizada.
- Herramientas efectivamente utilizadas.
- Corrección del resultado según una tolerancia definida previamente.
- Tiempo de ejecución.
- Errores o ausencia de respuesta.

Para las preguntas que combinan ambas fuentes, establecer criterios que consideren tanto la exactitud de los datos como la coherencia de la interpretación.

Los resultados deberán guardarse en:

`evaluacion/resultados.csv`

El archivo `evaluacion/comparacion.md` deberá presentar una comparación entre ambos modos, indicando:

- Cantidad de respuestas correctas.
- Respuestas incorrectas o no contestadas.
- Tiempo promedio de ejecución.
- Preguntas que mejoraron o empeoraron.
- Principales errores encontrados.
- Conclusión sobre la utilidad de MCP y Skills.

**No es obligatorio que el agente obtenga 10/10 ni que mejore una cantidad determinada de respuestas.** Se evaluará la calidad y reproducibilidad del experimento, así como la capacidad de explicar sus resultados.

## 4. Documentación y reproducibilidad

El archivo `README.md` deberá contener:

1. Objetivo del proyecto.
2. Arquitectura general del agente.
3. Descripción de las herramientas MCP.
4. Descripción de las tres Skills.
5. Fuentes y enlaces para descargar los datos.
6. Procedimiento de instalación con `uv`.
7. Instrucciones para conectar el MCP a Claude Code.
8. Comandos para reproducir el procesamiento y las pruebas.
9. Resultados de la evaluación.
10. Limitaciones y problemas encontrados.
11. Ejemplo de una ejecución completa.
12. Referencia a las evidencias del uso de inteligencia artificial.

El repositorio deberá incluir las salidas necesarias para comprobar que el sistema fue ejecutado.

**Las conversaciones completas con los asistentes de IA deberán estar disponibles en `evidencias_ia/` o mediante un enlace público incluido en el README**, con la información sensible previamente ocultada.

### Rúbrica Parte 4 [4 pts]

| Criterio | Pts |
|---|:---:|
| Diseño de 10 preguntas y respuestas esperadas verificables | 1.0 |
| Experimento comparativo ejecutado en ambos modos | 1.5 |
| Análisis de aciertos, errores, uso de herramientas y tiempo | 0.5 |
| README, reproducibilidad y evidencias completas del uso de IA | 1.0 |
| **Total** | **4.0** |

---

## 💡 Ideas de innovación (opcionales)

Los estudiantes que hayan completado los requisitos principales podrán incorporar mejoras como:

- Crear una Skill adicional para generar automáticamente informes socioeconómicos.
- Integrar un segundo MCP con otra fuente oficial de datos.
- Diseñar mecanismos para detectar inconsistencias entre resultados de diferentes herramientas.
- Construir un dashboard para explorar los resultados generados por el agente.
- Implementar pruebas de robustez frente a solicitudes ambiguas o datos inexistentes.
- Incorporar análisis de cómo cambia la calidad de las respuestas al desactivar determinadas herramientas.
- Automatizar la elaboración de informes con tablas, gráficos y referencias.

Estas mejoras podrán contribuir a obtener la máxima calificación dentro de los criterios establecidos, pero no sustituyen los requisitos obligatorios ni garantizan puntos adicionales fuera de la rúbrica.

---

## ✅ Lista de verificación antes de entregar

### Servidor MCP

- [ ] El servidor MCP funciona y cuenta con las cuatro herramientas requeridas.
- [ ] Incluye un recurso y un prompt funcionales.
- [ ] Supera las 8 pruebas originales y las 2 pruebas adicionales.
- [ ] El archivo `.mcp.json` permite conectarlo a Claude Code.
- [ ] Las consultas devuelven datos de fuentes oficiales verificables.

### Skills de ENAHO

- [ ] Existen las tres Skills solicitadas con sus archivos `SKILL.md`.
- [ ] La limpieza reproduce las validaciones de ENAHO 2024.
- [ ] Los indicadores utilizan los factores de expansión adecuados.
- [ ] Los gráficos contienen títulos, unidades y fuentes.
- [ ] El mapa representa las 25 unidades territoriales.
- [ ] Las Skills pueden activarse y coordinarse correctamente.

### Integración del agente

- [ ] El agente utiliza efectivamente MCP y Skills en una misma ejecución.
- [ ] La pregunta de investigación requiere información del BCRP y ENAHO.
- [ ] Existe un informe con al menos 3 hallazgos sustentados.
- [ ] El informe contiene un gráfico del BCRP, un gráfico de ENAHO y un mapa.
- [ ] Se verificaron manualmente al menos 3 afirmaciones numéricas.

### Evaluación y documentación

- [ ] Se construyeron 10 preguntas de evaluación.
- [ ] Se ejecutó la comparación con y sin MCP/Skills.
- [ ] Los resultados están documentados en archivos reproducibles.
- [ ] El README incluye instalación, arquitectura y procedimiento de ejecución.
- [ ] El repositorio es público y sus enlaces funcionan.

### Uso de inteligencia artificial

- [ ] Se adjuntaron capturas completas o exportaciones de las conversaciones utilizadas.
- [ ] Las evidencias están organizadas en `evidencias_ia/` o mediante un enlace público.
- [ ] Los registros permiten revisar el proceso de desarrollo del MCP, las Skills, la integración y la evaluación.
- [ ] Se ocultaron claves API, contraseñas, tokens y datos personales.

---

## 📤 Formato y canal de entrega

Cada estudiante deberá publicar **un comentario en este Issue** utilizando el siguiente formato:

```markdown
### Tarea 4 – Individual

**Estudiante:** Nombre completo (@usuario_github)

**Pregunta de investigación:** ...

**Repositorio de GitHub:** https://github.com/...

**Informe final:** https://github.com/.../informes/informe_final.md

**Pruebas MCP:** XX/10 aprobadas

**Validación ENAHO:**
- Pobreza nacional 2024: XX.X %
- Residentes habituales: XX,XXX
- Unidades territoriales procesadas: XX/25

**Evaluación del agente:**
- Sin MCP/Skills: X/10 respuestas correctas
- Con MCP/Skills: X/10 respuestas correctas
- Resultados completos: https://github.com/.../evaluacion/resultados.csv

**Evidencia de integración MCP + Skills:** https://github.com/...

**Evidencias de uso de IA:** https://github.com/...
```

### Precisiones sobre la entrega

- **Repositorio de GitHub:** deberá contener el código, las configuraciones, las Skills y los resultados.
- **Informe final:** enlace directo al documento de investigación desarrollado con el agente.
- **Pruebas MCP:** cantidad de pruebas automatizadas aprobadas, respaldada por el código y su ejecución.
- **Validación ENAHO:** resultados calculados mediante el procesamiento de los microdatos.
- **Evaluación del agente:** resultados obtenidos al ejecutar las mismas diez preguntas en las dos condiciones.
- **Evidencia de integración:** registro o demostración de una ejecución en la que Claude Code utilice conjuntamente MCP y Skills.
- **Evidencias de uso de IA:** capturas completas o exportaciones de las conversaciones utilizadas durante el desarrollo.

No será necesario adjuntar nuevamente los microdatos originales de ENAHO, siempre que se proporcionen instrucciones reproducibles para obtenerlos.

Todos los enlaces deberán ser públicos y accesibles sin solicitar permisos adicionales.

---

## ⏰ Fecha límite de entrega

**Domingo 8 de noviembre de 2026, hasta las 11:59 p. m. (hora de Perú / UTC-5).**

La entrega deberá realizarse mediante un comentario en este Issue de GitHub, siguiendo el formato establecido y proporcionando todos los enlaces solicitados.

### Política de entregas fuera de plazo

> [!IMPORTANT]
> **No se aceptarán trabajos presentados después de la fecha límite sin una justificación debidamente sustentada.**
>
> Las entregas tardías únicamente podrán ser consideradas de manera excepcional, previa evaluación y autorización del equipo docente.
>
> En caso de autorizarse una entrega fuera de plazo, se aplicará una **penalización de 2 puntos sobre la calificación final por cada día de retraso**.
>
> La presentación de una justificación no garantiza la aceptación de la entrega tardía. Cada caso será evaluado individualmente por el equipo docente.

Para aplicar la penalización, se contabilizará cada período de 24 horas de retraso iniciado después del vencimiento del plazo. Cualquier fracción de un nuevo período se considerará un día adicional.

**Ejemplo:** Para un trabajo que obtiene 18/20 según la rúbrica:

| Retraso | Penalización | Nota final |
|---|:---:|:---:|
| 1 día | −2 | 16 |
| 2 días | −4 | 14 |
| 3 días | −6 | 12 |
| 4 días | −8 | 10 |

La penalización se aplicará sobre la nota obtenida según la rúbrica de 20 puntos, sin que la calificación final pueda ser inferior a 0.

Se recomienda comprobar con anticipación que:

- El repositorio y todos los enlaces sean accesibles.
- Los scripts, pruebas y resultados estén correctamente guardados.
- Las evidencias del uso de IA estén completas.
- No se hayan publicado credenciales ni información sensible.
- El comentario de entrega se haya registrado correctamente dentro del plazo.

---

## 🎯 Resultado esperado

Al finalizar esta tarea, cada estudiante deberá contar con un **agente de investigación socioeconómica funcional**, capaz de consultar información oficial del BCRP mediante MCP, procesar y analizar microdatos de ENAHO mediante Skills y elaborar informes con resultados verificables.

**El proyecto estará completo cuando el agente pueda responder una pregunta real utilizando ambas herramientas, y cuando otra persona pueda reproducir, evaluar y comprobar los resultados obtenidos.**

El propósito es desarrollar competencias para construir sistemas de inteligencia artificial que no se limiten a generar respuestas, sino que sean capaces de **utilizar herramientas, ejecutar procedimientos reproducibles y producir evidencia confiable para el análisis de datos y la investigación social**.

**¡Éxitos con sus proyectos!** 🚀