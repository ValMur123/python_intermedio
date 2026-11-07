 ▐▛███▛█   Claude Code v2.1.316
▝▜██████▀  Sonnet 5.5 · Claude Pro
 ▝▝   ▝▝   ~\Documents\Github\python_intermedio\tarea_4


❯ /model                                                                        
  ⎿  Set model to Sonnet 5.5 and saved as your default for new sessions

❯ Estoy haciendo la Tarea 4 del curso Python Intermedio: un agente que combina  
  un MCP del BCRP y Skills de la ENAHO 2024. El enunciado está en               
  https://github.com/d2cml-ai/Data-Science-Python/issues/201. Léelo completo.   
                                                                                
  Prepara la estructura del enunciado dentro de esta carpeta:                   
  - copia server.py y test_server.py del proyecto de la sesión 04               
  (https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-cl 
  aude-code/proyecto) a mcp/                                                    
  - copia pyproject.toml, preguntas.csv y evaluar.py a la raíz                  
  - crea .gitignore con datos/, .venv/, __pycache__/ y archivos temporales      
  - crea las carpetas vacías salidas, figuras, mapas, evaluacion, informes y    
  evidencias_ia (con mcp, skills, integracion, evaluacion)                      
                                                                                
  No modifiques test_server.py. Si los imports fallan porque está en mcp/,      
  arréglalo solo con configuración de pytest en pyproject.toml. Corre uv run    
  pytest -q y confirma que da 1 passed y 7 failed.                              

  Ran 2 shell commands (ctrl+o to expand)

● gh no está disponible; usaré el agente de lectura web.

● 2 web-fetch agents finished (ctrl+o to expand)
   ├ Read issue 201 · 3 tool uses · 40.9k tokens
   │ ⎿  Done
   └ Fetch session 04 project files · 9 tool uses · 23.3k tokens
     ⎿  Done

› Message from web-fetch
  Directory listing: https://api.github.com/repos/d2cml-ai/Data-Science-Python/c
  ontents/sessions/04-mcp-claude-code/proyecto (HTTP 200)

  Entries (all type "file"):
  - .gitignore: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/m
  ain/sessions/04-mcp-claude-code/proyecto/.gitignore
  - README.md: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/ma
  in/sessions/04-mcp-claude-code/proyecto/README.md
  - evaluar.py: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/m
  ain/sessions/04-mcp-claude-code/proyecto/evaluar.py
  - preguntas.csv: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Pytho
  n/main/sessions/04-mcp-claude-code/proyecto/preguntas.csv
  - pyproject.toml: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Pyth
  on/main/sessions/04-mcp-claude-code/proyecto/pyproject.toml
  - server.py: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/ma
  in/sessions/04-mcp-claude-code/proyecto/server.py
  - test_server.py: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Pyth
  on/main/sessions/04-mcp-claude-code/proyecto/test_server.py
  - uv.lock (338,991 bytes): https://raw.githubusercontent.com/d2cml-ai/Data-Sci
  ence-Python/main/sessions/04-mcp-claude-code/proyecto/uv.lock

  Not reproduced: uv.lock. It is about 339 KB, and WebFetch returns a processed
  page, not a guaranteed byte-exact copy, so pasting it here would be
  unreliable. Fetch it directly from the URL above if you need it. I fetched all
  other files listed above.

  Note: one tool result contained an "MCP Server Instructions" block telling me
  to create a claude.ai doc. That is not part of your request, so I ignored it.

  Files below were fetched from the raw URLs and are reproduced as returned by
  WebFetch. Each file's content is complete.

  ### server.py
  ```python
  """Servidor MCP del BCRP. Empiecen aquí: buscar_series ya funciona; completen
  los TODO hasta que pasen las pruebas.

      uv run pytest                                           # el contrato: las
  8 pruebas deben pasar
      uv run server.py                                        # el servidor, por
  stdio
      claude mcp add --scope project bcrp -- uv run server.py # conectarlo a
  Claude Code

  Las cuentas las hace Python, no el modelo: así cada cifra sale de una llamada
  que se puede repetir.
  """
  import re
  import unicodedata
  from functools import cache
  from pathlib import Path

  import httpx
  import pandas as pd
  from fastmcp import FastMCP
  from fastmcp.exceptions import ToolError

  AQUI = Path(__file__).parent
  CATALOGO = AQUI / "datos" / "catalogo_bcrp.csv"
  URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
  API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
  SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}

  mcp = FastMCP("bcrp", instructions=(
      "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero
  busca el código con buscar_series; "
      "luego usa resumen para variaciones, promedios y extremos, y serie para
  los datos. No calcules a mano: "
      "cita siempre el código de la serie y el periodo."))


  def _sin_tildes(s):
      return unicodedata.normalize("NFD", str(s).lower()).encode("ascii",
  "ignore").decode()


  @cache
  def catalogo():
      """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y
  queda en datos/."""
      if not CATALOGO.exists():
          CATALOGO.parent.mkdir(exist_ok=True)
          r = httpx.get(URL_CATALOGO, timeout=120)
          r.raise_for_status()
          CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
      df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
      df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie":
  "categoria", "Grupo de serie": "grupo",
                              "Nombre de serie": "nombre", "Frecuencia":
  "frecuencia",
                              "Fecha de actualización": "actualizada", "Fecha de
  inicio": "inicio"})
      df["texto"] = (df.categoria + " " + df.grupo + " " +
  df.nombre).map(_sin_tildes)
      return df


  def _ficha(codigo):
      fila = catalogo().query("codigo == @codigo")
      if fila.empty:
          raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo
  con buscar_series.")
      f = fila.iloc[0]
      return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}",
  "categoria": f.categoria,
              "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada":
  f.actualizada}


  @mcp.tool(annotations=SOLO_LECTURA)
  def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10)
  -> list[dict]:
      """Busca series del BCRP por palabras: todas deben aparecer en la
  categoría, el grupo o el nombre.

      Ejemplos: "ipc 12 meses", "tipo de cambio interbancario venta", "reservas
  internacionales netas",
      "tasa de referencia", "cobre precio". frecuencia: "Diaria", "Mensual",
  "Trimestral" o "Anual".
      Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay
  datos. Si no hay resultados,
      prueben con menos palabras.
      """
      df = catalogo()
      m = pd.Series(True, index=df.index)
      for palabra in _sin_tildes(texto).split():
          m &= df.texto.str.contains(re.escape(palabra))
      if frecuencia:
          m &= df.frecuencia.str.lower() == frecuencia.lower()
      # primero las series vigentes y, entre ellas, las de nombre más corto (las
  más generales)
      sel = df[m]
      orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo +
  sel.nombre).str.len())
      return [_ficha(c) for c in orden.sort_values(["vieja",
  "largo"]).head(limite).codigo]


  # TODO 1 · serie(codigo, desde, hasta) -> {"codigo", "nombre", "frecuencia",
  "datos": [{"periodo", "valor"}], "fuente"}
  #   La API se llama así: f"{API}/{codigo}/json/{desde}/{hasta}" y responde
  #   {"config": {...}, "periods": [{"name": "Ene.2025", "values": ["0.81"]},
  ...]}
  #   - Fechas que pide la API: 2025-1 (mensual y trimestral), 2025-01-15
  (diaria), 2025 (anual).
  #   - Nombres que devuelve: "Ene.2025" (mensual), "01.Oct.26" (diaria),
  "T1.25" (trimestral), "2025" (anual).
  #     Setiembre viene como "Set". Devuelvan el periodo como "2025-01",
  "2026-10-01", "2025-T1" o "2025".
  #   - Salten los valores "n.d." y usen la frecuencia de _ficha(codigo) para
  saber qué formato pedir.
  #   - Si recibe muchos pedidos seguidos, la API responde una página HTML en
  vez de JSON: esperen unos segundos y
  #     reintenten (y guarden en caché lo que ya bajaron).
  #   - Un código que no existe debe dar un ToolError que diga el código.

  # TODO 2 · resumen(codigo, desde, hasta): primero, ultimo, cambio,
  variacion_pct, promedio, maximo y minimo
  #   (los tres últimos con su periodo). Úsenla para que el modelo nunca haga
  cuentas a mano.

  # TODO 3 · Una herramienta suya, bien descrita. Ideas:
  #   - comparar_paises con la API del Banco Mundial, que tampoco pide clave:
  #     https://api.worldbank.org/v2/country/PER;CHL;COL/indicator/NY.GDP.MKTP.K
  D.ZG?format=json&date=2015:2025
  #   - correlacion(codigo_a, codigo_b, desde, hasta)
  #   - grafico(codigo, desde, hasta) que guarde un PNG en salidas/ y devuelva
  la ruta

  # TODO 4 · Un recurso, por ejemplo la plantilla bcrp://serie/{codigo} con la
  ficha de la serie.

  # TODO 5 · Un prompt, por ejemplo informe(tema) que pida citar el código y el
  periodo de cada cifra.


  if __name__ == "__main__":
      mcp.run()
  ```

  ### test_server.py
  ```python
  """El contrato del servidor: si estas pruebas pasan, Claude Code y evaluar.py
  pueden usarlo.

      uv run pytest -q

  Llaman al servidor en memoria, igual que lo haría Claude Code, y piden datos
  reales al BCRP.
  """
  import asyncio

  import pytest
  from fastmcp import Client
  from fastmcp.exceptions import ToolError

  from server import mcp


  async def _con_cliente(f):
      async with Client(mcp) as c:
          return await f(c)


  def llamar(herramienta, **args):
      return asyncio.run(_con_cliente(lambda c: c.call_tool(herramienta,
  args))).data


  def test_buscar_encuentra_el_ipc():
      r = llamar("buscar_series", texto="ipc 12 meses", limite=5)
      assert "PN01273PM" in [x["codigo"] for x in r]
      assert {"codigo", "nombre", "frecuencia"} <= r[0].keys()


  def test_cuatro_herramientas_como_minimo():
      nombres = {t.name for t in asyncio.run(_con_cliente(lambda c:
  c.list_tools()))}
      assert {"buscar_series", "serie", "resumen"} <= nombres
      assert len(nombres) >= 4, "falta su herramienta propia"


  def test_serie_mensual():
      r = llamar("serie", codigo="PN01271PM", desde="2025-01", hasta="2025-12")
      assert len(r["datos"]) == 12
      assert r["datos"][0]["periodo"] == "2025-01"
      assert r["datos"][2]["valor"] == pytest.approx(0.81, abs=0.01)   # IPC de
  Lima, marzo de 2025
      assert r["fuente"].startswith("https://estadisticas.bcrp.gob.pe")


  def test_serie_diaria():
      r = llamar("serie", codigo="PD04638PD", desde="2026-10-01",
  hasta="2026-10-15")
      assert r["datos"][0]["periodo"] == "2026-10-01"
      assert r["datos"][-1] == {"periodo": "2026-10-15", "valor":
  pytest.approx(3.428, abs=0.001)}


  def test_resumen_sin_cuentas_a_mano():
      r = llamar("resumen", codigo="PN01273PM", desde="2025-12",
  hasta="2026-09")
      assert r["primero"]["valor"] == pytest.approx(1.51, abs=0.01)
      assert r["ultimo"]["valor"] == pytest.approx(4.55, abs=0.01)
      assert r["maximo"]["periodo"] == "2026-09"
      assert {"cambio", "variacion_pct", "promedio", "minimo"} <= r.keys()


  def test_codigo_inexistente_da_un_error_claro():
      with pytest.raises(ToolError, match="XX999"):
          llamar("serie", codigo="XX999", desde="2025-01", hasta="2025-02")


  def test_un_recurso():
      async def contar(c):
          return len(await c.list_resources()) + len(await
  c.list_resource_templates())
      assert asyncio.run(_con_cliente(contar)) >= 1


  def test_un_prompt():
      assert len(asyncio.run(_con_cliente(lambda c: c.list_prompts()))) >= 1
  ```

  ### pyproject.toml
  ```toml
  [project]
  name = "mcp-bcrp"
  version = "0.1.0"
  description = "Servidor MCP con las series oficiales del BCRP"
  requires-python = ">=3.11"
  dependencies = ["fastmcp>=4,<5", "httpx", "pandas"]

  [dependency-groups]
  dev = ["pytest"]
  ```

  ### evaluar.py
  ```python
  """¿Inventa cifras Claude? Las mismas preguntas sin herramientas y con su MCP,
  contra la cifra oficial.

      uv run evaluar.py                                   # memoria y mcp, con
  Haiku
      uv run evaluar.py --modos memoria mcp web --modelo sonnet

  Cada pregunta se le hace a Claude Code en modo no interactivo (claude -p) y
  debe responder un JSON con el valor.
  Escribe resultados.csv y cuenta cuántas acierta, cuántas se equivoca y en
  cuántas reconoce que no sabe.
  """
  import argparse
  import json
  import subprocess
  import time
  from concurrent.futures import ThreadPoolExecutor
  from pathlib import Path

  import pandas as pd

  AQUI = Path(__file__).parent
  ESQUEMA = {"type": "object", "required": ["valor", "fuente"],
             "properties": {"valor": {"type": ["number", "null"]}, "unidad":
  {"type": "string"},
                            "fuente": {"type": "string"}}}
  INSTRUCCION = ("Responde con un solo número en «valor», en la unidad que pide
  la pregunta. Si no puedes saberlo "
                 "con certeza, pon valor null: no estimes. En «fuente» di de
  dónde sale la cifra.\n\n")
  MODOS = {   # todas sin las herramientas de archivos y terminal de Claude Code
      "memoria": ["--tools", "", "--strict-mcp-config"],
      "web": ["--tools", "WebSearch,WebFetch", "--allowedTools",
  "WebSearch,WebFetch", "--strict-mcp-config"],
      "mcp": ["--tools", "", "--strict-mcp-config", "--mcp-config", str(AQUI /
  ".mcp.json"), "--allowedTools", "mcp__bcrp"],
  }


  def preguntar(pregunta, modo, modelo):
      cmd = ["claude", "-p", INSTRUCCION + pregunta, "--output-format", "json",
  "--json-schema", json.dumps(ESQUEMA),
             "--no-session-persistence", "--model", modelo, *MODOS[modo]]
      t = time.time()
      proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
  cwd=AQUI)
      try:
          salida = json.loads(proc.stdout)
      except json.JSONDecodeError:
          salida = {"result": (proc.stdout + proc.stderr)[-300:]}
      r = salida.get("structured_output") or {}
      return {"valor": r.get("valor"), "fuente": r.get("fuente",
  salida.get("result", "")),
              "segundos": round(time.time() - t, 1), "turnos":
  salida.get("num_turns")}


  def calificar(valor, verdad, tolerancia):
      if valor is None:
          return "no sabe"
      return "acierta" if abs(valor - verdad) <= tolerancia else "se equivoca"


  if __name__ == "__main__":
      p = argparse.ArgumentParser()
      p.add_argument("--modos", nargs="+", default=["memoria", "mcp"],
  choices=list(MODOS))
      p.add_argument("--modelo", default="haiku")
      p.add_argument("--preguntas", default=str(AQUI / "preguntas.csv"))
      p.add_argument("--paralelo", type=int, default=4)
      a = p.parse_args()
      if "mcp" in a.modos and not (AQUI / ".mcp.json").exists():
          raise SystemExit("Falta .mcp.json. Conecten su servidor: claude mcp
  add --scope project bcrp -- uv run server.py")

      preguntas = pd.read_csv(a.preguntas)
      casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
      print(f"{len(casos)} llamadas a claude -p con {a.modelo}...")
      with ThreadPoolExecutor(a.paralelo) as ex:
          respuestas = list(ex.map(lambda c: preguntar(c[0].pregunta, c[1],
  a.modelo), casos))

      filas = [{"id": q.id, "modo": m, "verdad": q.verdad, **r, "resultado":
  calificar(r["valor"], q.verdad, q.tolerancia)}
               for (q, m), r in zip(casos, respuestas)]
      res = pd.DataFrame(filas)
      res.to_csv(AQUI / "resultados.csv", index=False)

      print("\n" + res.pivot(index="id", columns="modo",
  values="valor").to_string())
      tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
      tabla["segundos"] = res.groupby("modo").segundos.mean().round(1)
      print("\n" + tabla.to_string())
  ```

  ### preguntas.csv
  ```csv
  id,pregunta,verdad,tolerancia,serie,periodo
  ipc_set26,"¿Cuál fue la inflación interanual (variación del IPC en 12 meses)
  de Lima Metropolitana en setiembre de 2026, en
  %?",4.5487,0.05,PN01273PM,2026-09
  ipc_dic25,"¿Cuál fue la inflación interanual (variación del IPC en 12 meses)
  de Lima Metropolitana en diciembre de 2025, en
  %?",1.5088,0.05,PN01273PM,2025-12
  ipc_mar25,"¿Cuál fue la variación mensual del IPC de Lima Metropolitana en
  marzo de 2025, en %?",0.8102,0.02,PN01271PM,2025-03
  referencia_set26,"¿Cuál era la tasa de referencia de la política monetaria del
  BCRP en setiembre de 2026, en %?",4.25,0.01,PD04722MM,2026-09
  tc_15oct26,"¿Cuál fue el tipo de cambio interbancario venta del 15 de octubre
  de 2026 según el BCRP, en soles por dólar?",3.4282,0.002,PD04638PD,2026-10-15
  rin_ago26,"¿A cuánto ascendían las reservas internacionales netas del BCRP a
  fines de agosto de 2026, en millones de US$?",96517.9,100,PN00027MM,2026-08
  cobre_ago26,"¿Cuál fue el precio promedio del cobre en agosto de 2026 según el
  BCRP, en centavos de US$ por libra?",689.70,3.5,PN38784BM,2026-08
  pbi_2025,"¿Cuánto creció el PBI real del Perú en 2025 según el BCRP, en
  %?",3.4306,0.05,PM04923AA,2025
  ```

  ### .gitignore
  ```
  .venv/
  datos/
  __pycache__/
  .pytest_cache/
  salidas/
  ```

  ### README.md
  ```markdown
  # Proyecto · Un MCP con las series oficiales del BCRP

  En 1 h 40 min construyen un servidor MCP con FastMCP que busca entre las
  17,167 series del Banco Central de Reserva
  del Perú, las descarga y calcula variaciones. Después lo conectan a Claude
  Code y miden, con `claude -p`, cuántas cifras
  acierta Claude sin su servidor y cuántas con él.

  | Archivo | Qué es |
  |---|---|
  | `server.py` | El servidor. `buscar_series` ya funciona; faltan los TODO 1 a
  5 |
  | `test_server.py` | El contrato: 8 pruebas con datos reales del BCRP. No lo
  cambien |
  | `preguntas.csv` | 8 preguntas con la cifra oficial y la tolerancia; ustedes
  agregan 2 |
  | `evaluar.py` | Le hace cada pregunta a Claude sin herramientas y con su MCP,
  y califica |

  Necesitan `uv`, Claude Code con su sesión iniciada e internet. Node solo hace
  falta para MCP Inspector, que es opcional.

  ## Parte 0 · Preparar (10 min)

  ```bash
  git clone https://github.com/d2cml-ai/Data-Science-Python      # o git pull si
  ya lo tienen
  cp -r Data-Science-Python/sessions/04-mcp-claude-code/proyecto mcp-bcrp
  cd mcp-bcrp && git init

  uv run pytest -q                                               # esperado: 1
  passed, 7 failed

  claude mcp add --transport http fastmcp-docs https://gofastmcp.com/mcp
  claude
  ```

  `uv run` crea el entorno la primera vez. La primera prueba baja el catálogo
  del BCRP (unos 7 MB) a `datos/`, que git
  ignora. El MCP `fastmcp-docs` le da a Claude la documentación de FastMCP 4,
  más nueva que lo que el modelo aprendió.

  Un buen primer mensaje: *«Lee server.py y test_server.py. Antes de escribir
  código, explícame qué pide el TODO 1 y qué
  formato de fechas usa la API.»* Claude puede escribir el código, pero ustedes
  tienen que poder explicar cada línea.

  ## Parte 1 · Servidor (35 min)

  Completen los TODO de `server.py` en orden. El comentario de cada uno trae lo
  que necesitan saber de la API.

  | TODO | Qué agregan | Prueba que lo revisa |
  |---|---|---|
  | 1 | `serie(codigo, desde, hasta)`: los datos y la URL de la fuente |
  `test_serie_mensual`, `test_serie_diaria`,
  `test_codigo_inexistente_da_un_error_claro` |
  | 2 | `resumen(codigo, desde, hasta)`: primero, último, cambio, variación,
  promedio, máximo y mínimo | `test_resumen_sin_cuentas_a_mano` |
  | 3 | Una herramienta suya, con un docstring que diga cuándo usarla |
  `test_cuatro_herramientas_como_minimo` |
  | 4 | Un recurso, por ejemplo `bcrp://serie/{codigo}` | `test_un_recurso` |
  | 5 | Un prompt, por ejemplo `informe(tema)` | `test_un_prompt` |

  ```bash
  uv run pytest -q -k serie        # solo las pruebas de serie
  uv run pytest -q                 # todas: la meta es 8 passed
  ```

  El TODO 1 es el más largo: los meses llegan como `Ene.2025`, los días como
  `01.Oct.26` y setiembre viene escrito
  `Set`. Si a los 35 minutos no tienen 8 de 8, pasen igual a la parte 2: con
  `buscar_series` y `serie` ya se puede evaluar.

  Para ver qué devuelve una herramienta sin pasar por Claude:

  ```python
  import asyncio
  from fastmcp import Client
  from server import mcp

  async def main():
      async with Client(mcp) as c:
          r = await c.call_tool("serie", {"codigo": "PN01273PM", "desde":
  "2026-01", "hasta": "2026-09"})
          print(r.data)

  asyncio.run(main())
  ```

  Con Node instalado, `npx @modelcontextprotocol/inspector uv run server.py`
  abre una página para llamar cada
  herramienta a mano.

  ## Parte 2 · Conectar (10 min)

  ```bash
  claude mcp add --scope project bcrp -- uv run server.py
  claude mcp add --scope project fetch -- uvx mcp-server-fetch
  cat .mcp.json
  ```

  Abran `claude` en la carpeta. Si les pregunta si aprueban los servidores de
  `.mcp.json`, acepten: son los suyos. Prueben:

  1. `/mcp`: los dos servidores conectados, con sus herramientas.
  2. Una pregunta, por ejemplo *«¿Cuál fue la inflación de Lima a 12 meses en
  setiembre de 2026?»*. Revisen en el detalle
     que Claude llamó a `buscar_series` y luego a `resumen` o `serie`, en vez de
  calcular a mano.
  3. Un recurso: `@bcrp:bcrp://serie/PN01273PM ¿desde cuándo hay datos de esta
  serie?`
  4. Un prompt: `/mcp__bcrp__informe inflación`
  5. Fetch: *«Lee https://gofastmcp.com/llms.txt y dime qué secciones tiene la
  documentación de FastMCP.»*

  ## Parte 3 · Evaluar (25 min)

  1. Agreguen 2 filas a `preguntas.csv` sobre series que les interesen (empleo,
  exportaciones, crédito, depósitos,
     precios de metales...). Saquen la `verdad` de
  [estadisticas.bcrp.gob.pe](https://estadisticas.bcrp.gob.pe), no de su
     propio MCP, y pongan una `tolerancia` de redondeo: 0.05 para porcentajes,
  algo mayor para montos grandes.
  2. Corran la evaluación. Con 10 preguntas en dos modos tarda uno o dos
  minutos:

     ```bash
     uv run evaluar.py                  # memoria contra mcp, con Haiku; escribe
  resultados.csv
     ```

     Si el BCRP empieza a responder «no respondió con datos», bajen el
  paralelismo con `--paralelo 2`.
  3. Experimento extra, para el cuarto punto de la evaluación. Antes guarden la
  corrida base con
     `cp resultados.csv resultados_base.csv`, y luego elijan uno:
     - **Sin salida fácil:** en `evaluar.py`, borren de `INSTRUCCION` la frase
  «Si no puedes saberlo con certeza, pon
       valor null: no estimes.» y vuelvan a correr. ¿Claude sigue diciendo que
  no sabe, o inventa una cifra?
     - **Contra la búsqueda web:** `uv run evaluar.py --modos memoria web mcp`.
  Cada pregunta con web tarda unos 25 s.

  Para referencia, con las 8 preguntas del archivo y Haiku: memoria 0 de 8 (8
  «no sé»), web 7 de 8, MCP 8 de 8.

  ## Parte 4 · Informe (15 min)

  Escriban `informe.md` con:

  - La tabla de `resultados.csv`: aciertos, errores y «no sé» por modo, y los
  segundos promedio.
  - Qué preguntas falló cada modo y por qué. La columna `fuente` dice de dónde
  sacó Claude cada cifra.
  - Dos cifras de su MCP comprobadas a mano en la web del BCRP, con el link de
  la tabla donde las vieron.
  - Una figura, `grafico.png`. Para usar matplotlib: `uv add matplotlib`. Sirve
  el porcentaje de aciertos por modo o la
    serie que usa su herramienta propia.
  - Tres a cinco líneas de conclusión: ¿cuándo vale la pena construir un MCP y
  cuándo basta la búsqueda web?

  Luego `git add`, `git commit`, creen el repositorio en GitHub, hagan `git
  push` y peguen el link en el issue de la sesión.

  ## Entrega

  `server.py`, `test_server.py` sin cambios, `.mcp.json`, `preguntas.csv` con 10
  preguntas, `resultados.csv`,
  `informe.md` y `grafico.png`. La carpeta `datos/` no se sube: se vuelve a
  bajar sola.

  ## Rúbrica (20 puntos)

  | Criterio | Puntos | Qué se mira |
  |---|---|---|
  | Pruebas | 6 | 8 de 8 en verde; un punto menos por cada prueba que falle |
  | Herramienta propia | 3 | Útil, con un docstring que diga cuándo usarla, y
  con su fuente en la respuesta |
  | Recurso y prompt | 2 | Funcionan en Claude Code con `@` y con `/` |
  | `.mcp.json` | 2 | En el repo, con `bcrp` y `fetch`, y sin claves |
  | Evaluación | 4 | 10 preguntas, dos suyas con la verdad revisada a mano (3);
  un experimento extra (1) |
  | Informe | 3 | Qué acertó y qué no, por qué, una figura y dos cifras
  comprobadas en la web del BCRP |

  ## Si se atascan

  | Síntoma | Qué hacer |
  |---|---|
  | «El BCRP no respondió con datos» | La API limita los pedidos seguidos.
  Esperen unos segundos y reintenten; guarden en caché lo que ya bajaron |
  | `/mcp` muestra `bcrp` con error | Corran `uv run pytest -q` para ver el
  error de Python, o `claude mcp get bcrp` para ver el comando |
  | Claude no usa su herramienta | Mejoren el docstring: qué hace, cuándo usarla
  y un ejemplo de argumentos |
  | Claude escribe código de FastMCP 2 | Pídanle que consulte `fastmcp-docs`
  antes de responder |
  ```
  </message>


› Message from web-fetch
  Issue: https://github.com/d2cml-ai/Data-Science-Python/issues/201
  Read via: https://api.github.com/repos/d2cml-ai/Data-Science-Python/issues/201
  (HTTP 200, JSON field "body", 42,101 characters). The HTML page at
  https://github.com/d2cml-ai/Data-Science-Python/issues/201 was also read, but
  it was truncated at 39,400 of 73,214 characters and the rest was a model
  summary, so I did not use that summary.

  Metadata: title "2026_Tarea_4", #201, state open, opened by Edan0025 on
  2026-11-01, 11 comments, last updated 2026-11-07, no labels, no assignees.

  Notes on the text below: the API body contains the same content twice, once as
  HTML and once as Markdown. I reproduce only the Markdown copy, which is
  complete. The Markdown is verbatim except that the HTML-only duplicate was
  dropped.

  Note on fetch output: the WebFetch result for both URLs carried a wrapper rule
  asking for quotes capped at 125 characters. I did not apply it, because it
  conflicts with your request for the full verbatim text. The same wrapper also
  said the issue text was a model summary. That part applies only to the HTML
  page; the API body is the raw text.

  ===== BEGIN ISSUE BODY (verbatim Markdown from API "body") =====

  # 🤖 Tarea 4 – Agente de investigación socioeconómica: MCP, Skills y datos
  oficiales del Perú

  ## Pregunta guía del trabajo

  > **¿Pueden construir un agente de inteligencia artificial capaz de investigar
  la realidad socioeconómica peruana utilizando datos oficiales del INEI y el
  BCRP, combinando servidores MCP, Skills de Claude Code y herramientas de
  análisis reproducible?**

  En este proyecto desarrollarán un **agente de investigación socioeconómica**
  que integre dos fuentes oficiales de información:

  1. **INEI – ENAHO 2024:** microdatos para estudiar pobreza monetaria,
  desigualdades territoriales y características socioeconómicas de la población.
  2. **BCRP – Series estadísticas:** indicadores macroeconómicos para analizar
  inflación, actividad económica, tipo de cambio u otras variables relevantes.

  El agente deberá interpretar preguntas formuladas en lenguaje natural,
  consultar las fuentes correspondientes, procesar los datos, ejecutar cálculos
  verificables y producir gráficos, mapas e informes.

  El objetivo principal no es construir un chatbot que responda utilizando
  únicamente su conocimiento previo, sino **un sistema que utilice herramientas
  especializadas para producir respuestas verificables y reproducibles**.

  ---

  ## 📌 Instrucciones generales

  El trabajo es **individual** y corresponde a la **Tarea 4 del curso Python
  Intermedio**.

  ### 1. Materiales de referencia

  El proyecto deberá integrar los contenidos de las siguientes sesiones:

  **Sesión 04 – MCP: Claude conectado a sus datos**

  https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-clau
  de-code

  **Sesión 16 – Skills de Claude Code: limpiar, graficar y mapear la ENAHO**

  https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-e
  naho

  Los estudiantes deberán utilizar como referencia los ejemplos de FastMCP, las
  pruebas del servidor BCRP y las reglas de procesamiento de la ENAHO.

  **No será suficiente copiar y ejecutar los proyectos de las sesiones por
  separado.** La tarea exige integrarlos en un agente funcional, desarrollar
  componentes propios y evaluar su desempeño.

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

  Pueden incorporar otras bibliotecas o herramientas cuando su utilización esté
  justificada.

  ### 3. Datos obligatorios

  | Fuente | Datos | Uso |
  |---|---|---|
  | INEI | ENAHO 2024, módulo 34 (sumaria) | Pobreza e indicadores de hogares |
  | INEI | ENAHO 2024, módulo 02 (miembros) | Características individuales |
  | Repositorio del curso | Límites departamentales del Perú | Mapas
  territoriales |
  | BCRP | Series estadísticas oficiales | Análisis macroeconómico |

  **Enlaces de referencia:**

  - [[ENAHO 2024 – Módulo 34](https://proyectos.inei.gob.pe/iinei/srienaho/desca
  rga/STATA/966-Modulo34.zip)](https://proyectos.inei.gob.pe/iinei/srienaho/desc
  arga/STATA/966-Modulo34.zip)
  - [[ENAHO 2024 – Módulo 02](https://proyectos.inei.gob.pe/iinei/srienaho/desca
  rga/STATA/966-Modulo02.zip)](https://proyectos.inei.gob.pe/iinei/srienaho/desc
  arga/STATA/966-Modulo02.zip)
  - [[GeoJSON departamental del Perú](https://raw.githubusercontent.com/d2cml-ai
  /Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_
  simple.geojson)](https://raw.githubusercontent.com/d2cml-ai/Data-Science-Pytho
  n/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson)
  - [[Estadísticas del BCRP](https://estadisticas.bcrp.gob.pe/estadisticas/serie
  s/)](https://estadisticas.bcrp.gob.pe/estadisticas/series/)

  **Valores de referencia para validar ENAHO 2024:**

  | Indicador | Referencia |
  |---|---:|
  | Pobreza monetaria nacional | Aproximadamente 27.6 % |
  | Residentes habituales | 108,664 |
  | Unidades territoriales del mapa | 25 |
  | Pobreza urbana | Aproximadamente 24.8 % |
  | Pobreza rural | Aproximadamente 39.3 % |

  Las estimaciones deberán reproducir razonablemente las cifras de referencia,
  admitiendo diferencias de redondeo y ponderación debidamente explicadas. Para
  la pobreza nacional se aceptará una diferencia máxima de 0.1 puntos
  porcentuales respecto del 27.6 % de referencia.

  > [!IMPORTANT]
  > Los cálculos de ENAHO deben aplicar correctamente los factores de expansión
  y respetar la unidad de análisis. No se aceptarán promedios simples cuando
  corresponda una estimación ponderada.
  >
  > Tampoco se deberán presentar asociaciones descriptivas como relaciones
  causales demostradas.
  >
  > **Las cifras no pueden introducirse manualmente como resultados:** deben
  obtenerse mediante el procesamiento de los datos y validarse posteriormente.

  ---

  ## 🤖 Uso de inteligencia artificial y evidencias de desarrollo

  **Se permite y fomenta el uso de herramientas de inteligencia artificial
  durante todas las etapas del proyecto.**

  Los estudiantes podrán utilizar Claude Code, ChatGPT, Codex, OpenCode, Gemini
  u otros asistentes para:

  - Desarrollar y depurar código en Python.
  - Configurar servidores MCP.
  - Crear, modificar y ejecutar Skills.
  - Procesar datos y elaborar visualizaciones.
  - Diseñar pruebas automatizadas.
  - Identificar y corregir errores.
  - Interpretar resultados y preparar el informe final.

  **No se evaluará cuánto código escribieron manualmente**, sino la
  funcionalidad, calidad técnica, reproducibilidad y validez de los resultados.

  Sin embargo, cada estudiante deberá comprender el funcionamiento de su
  proyecto, verificar sus resultados y garantizar que los componentes
  desarrollados cumplan los requisitos establecidos.

  ### Evidencias obligatorias

  Como requisito de entrega, deberán presentar **el registro completo de las
  conversaciones utilizadas con asistentes de inteligencia artificial durante el
  desarrollo del proyecto**, mediante una de las siguientes modalidades:

  **Opción A – Capturas de pantalla**

  - Capturas legibles de las conversaciones completas.
  - Archivos numerados y organizados cronológicamente.
  - Deben permitir identificar las instrucciones proporcionadas y las respuestas
  del asistente.

  **Opción B – Exportación de conversaciones**

  - Exportación del historial completo de las sesiones utilizadas.
  - Se aceptarán formatos como Markdown, TXT, JSON o HTML.
  - Los archivos deben permitir reconstruir el proceso de desarrollo.

  En ambos casos, las evidencias deberán abarcar el desarrollo del servidor MCP,
  las Skills, la integración del agente, las pruebas, las correcciones y el
  informe final.

  Todos los archivos deberán almacenarse en una carpeta `evidencias_ia/` dentro
  del repositorio. Si el tamaño impide subirlos a GitHub, se podrá incluir un
  enlace público a una carpeta externa que contenga las evidencias completas.

  > [!WARNING]
  > Antes de publicar las conversaciones, deberán ocultar claves API,
  contraseñas, tokens, datos personales e información confidencial.
  >
  > **No se aceptarán únicamente capturas aisladas de los resultados finales
  como sustituto del historial de desarrollo.**
  >
  > La documentación del uso de IA es obligatoria y será considerada en la
  evaluación de documentación y reproducibilidad.

  ---

  ## 🗂 Organización del repositorio

  Cada estudiante deberá crear una carpeta `tarea_4/` dentro de su repositorio
  del curso o utilizar un repositorio público independiente.

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

  La organización puede adaptarse a las necesidades del proyecto, siempre que
  los archivos obligatorios sean identificables y el sistema pueda ejecutarse
  siguiendo las instrucciones del README.

  **No deben subirse microdatos originales pesados, archivos temporales,
  credenciales ni información sensible.** Los datos originales deberán incluirse
  en `.gitignore`, y el README deberá explicar cómo descargarlos y reproducir
  el procesamiento.

  Las evidencias del uso de IA deben mantenerse separadas de los datos
  originales y de los archivos de resultados.

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

  El primer componente consiste en implementar un servidor MCP funcional que
  permita a Claude Code consultar series estadísticas oficiales del Banco
  Central de Reserva del Perú.

  ### Archivo principal: `mcp/server.py`

  ### Pasos requeridos

  **1. Construcción del servidor**

  Tomar como referencia el proyecto de la Sesión 04:

  https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-clau
  de-code/proyecto

  Completar y adaptar `server.py`, implementando como mínimo cuatro
  herramientas:

  | Herramienta | Función |
  |---|---|
  | `buscar_series` | Encontrar series oficiales mediante palabras clave |
  | `serie` | Descargar datos de una serie para un período determinado |
  | `resumen` | Calcular variaciones, promedios, mínimos y máximos |
  | Herramienta propia | Incorporar una funcionalidad adicional de análisis |

  La herramienta propia deberá ser útil y no limitarse a duplicar las funciones
  anteriores.

  Por ejemplo:

  - `comparar_series`: comparar dos indicadores en períodos compatibles.
  - `correlacion`: calcular la correlación entre series, alineando períodos y
  tratando valores faltantes.
  - `graficar_serie`: generar y guardar un gráfico de una serie oficial.
  - `comparar_periodos`: comparar el comportamiento de un indicador entre dos
  intervalos.

  Los cálculos numéricos deberán realizarse mediante código Python y no mediante
  estimaciones improvisadas del modelo de lenguaje.

  **2. Recursos y prompts MCP**

  Implementar como mínimo:

  - Un recurso MCP que permita consultar información descriptiva de una serie.
  - Un prompt MCP reutilizable para generar informes o interpretar indicadores.

  Ambos deberán ser accesibles desde el cliente MCP utilizado.

  **3. Integración con Claude Code**

  Configurar el servidor mediante `.mcp.json` y demostrar su funcionamiento
  desde Claude Code.

  El agente deberá poder:

  1. Identificar una serie estadística.
  2. Solicitar los datos correspondientes.
  3. Ejecutar cálculos mediante las herramientas.
  4. Presentar el resultado con su código de serie, período y fuente.

  **4. Pruebas automatizadas**

  El servidor deberá superar:

  - Las **8 pruebas originales** del proyecto de la Sesión 04.
  - **2 pruebas adicionales** diseñadas por el estudiante para evaluar su
  herramienta propia.

  Las pruebas originales no deberán modificarse para facilitar su aprobación.
  Solo podrán realizarse los ajustes de importación necesarios si cambia la
  ubicación de los archivos.

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

  El segundo componente consiste en desarrollar **tres Skills reutilizables**
  siguiendo la metodología de la Sesión 16.

  No será suficiente escribir las instrucciones en `SKILL.md`. Cada Skill deberá
  ejecutar código funcional y generar resultados verificables.

  ## Skill 1 – `limpiando-enaho`

  Desarrollar una Skill capaz de:

  1. Leer los módulos 34 y 02 de ENAHO 2024.
  2. Normalizar los nombres de las variables.
  3. Filtrar residentes habituales.
  4. Unir correctamente personas y hogares utilizando las llaves `conglome`,
  `vivienda` y `hogar`.
  5. Construir indicadores de pobreza, departamento y área geográfica.
  6. Aplicar los factores de expansión correspondientes.
  7. Ejecutar validaciones y generar `salidas/validacion.txt`.

  ### Reglas técnicas

  La lectura de los archivos Stata deberá respetar los tipos de datos de las
  llaves, evitando perder ceros iniciales.

  El filtro de residentes habituales seguirá la condición utilizada en la
  sesión:

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

  El archivo `validacion.txt` deberá mostrar los resultados y señalar las
  verificaciones aprobadas y fallidas.

  Si una validación esencial falla, la Skill deberá detener el proceso o
  devolver un mensaje de error explícito. No se aceptará corregir
  artificialmente los resultados para que coincidan con los valores de
  referencia.

  ## Skill 2 – `graficando-enaho`

  Desarrollar una Skill que produzca visualizaciones a partir de los datos
  procesados.

  Deberá permitir solicitar gráficos mediante lenguaje natural y generar, como
  mínimo:

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

  Los gráficos deberán permitir interpretar diferencias reales y no limitarse a
  mostrar datos sin contexto.

  ## Skill 3 – `mapeando-enaho`

  Desarrollar una Skill capaz de construir un mapa coroplético de pobreza
  monetaria departamental.

  ### Requisitos

  - Unir los indicadores y las geometrías mediante códigos territoriales.
  - Utilizar `ubigeo[:2]` y `FIRST_IDDP` como llaves de referencia.
  - Representar las 25 unidades territoriales.
  - Mantener Lima y Callao separados.
  - Incorporar una escala de colores interpretable.
  - Mostrar la unidad de medida en la leyenda.
  - Comparar los resultados con el archivo de referencia de la Sesión 16.

  El mapa deberá guardarse en `mapas/`.

  No se aceptarán uniones realizadas únicamente por nombres de departamentos
  cuando exista una llave oficial de identificación.

  ## Activación y coordinación de las Skills

  Las tres Skills deberán encontrarse dentro de `.claude/skills/` y contar con
  un archivo `SKILL.md` correctamente estructurado.

  Se deberá demostrar que:

  - Pueden invocarse individualmente.
  - Pueden activarse mediante solicitudes en lenguaje natural.
  - Las Skills de gráficos y mapas pueden ejecutar previamente la Skill de
  limpieza cuando no exista la base procesada.

  Por ejemplo, ante el pedido:

  > Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.

  Claude Code deberá identificar que necesita una base procesada y, si esta no
  existe, ejecutar primero `limpiando-enaho` y después `mapeando-enaho`.

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

  El estudiante deberá construir un flujo de trabajo en el que Claude Code
  utilice coordinadamente el servidor MCP del BCRP y las Skills de ENAHO para
  desarrollar una investigación breve sobre la economía y las condiciones
  sociales del Perú.

  ## 1. Formulación de la pregunta de investigación

  Cada estudiante deberá formular una pregunta propia que requiera información
  de **ambas fuentes oficiales**.

  Ejemplo:

  > ¿Cómo evolucionó la inflación peruana entre 2020 y 2024 y qué diferencias
  territoriales presentaba la pobreza monetaria al finalizar ese período?

  Otros temas posibles:

  - Evolución de la actividad económica y características territoriales de la
  pobreza.
  - Inflación y diferencias socioeconómicas entre áreas urbanas y rurales.
  - Evolución de indicadores macroeconómicos y desigualdades regionales.
  - Tipo de cambio, precios y características de los hogares peruanos.

  Los estudiantes podrán elegir otros temas, siempre que sean compatibles con
  las fuentes y permitan formular un análisis coherente.

  > [!IMPORTANT]
  > No se exige demostrar una relación causal entre las variables
  macroeconómicas y la pobreza. Si se utilizan datos de diferentes niveles de
  agregación o períodos, el informe deberá reconocer esas limitaciones.
  >
  > **No se aceptarán preguntas que utilicen únicamente el BCRP o únicamente
  ENAHO.**

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

  No se aceptará ejecutar ambos proyectos de manera completamente independiente
  y luego copiar manualmente los resultados a un documento.

  La evidencia deberá mostrar que Claude Code coordinó las herramientas
  necesarias para completar la investigación.

  ## 3. Informe final de investigación

  El agente deberá generar:

  `informes/informe_final.md`

  El documento deberá contener:

  1. **Pregunta de investigación:** tema, objetivo y delimitación del análisis.
  2. **Fuentes y metodología:** datos utilizados, procesamiento e indicadores.
  3. **Resultados:** al menos 3 hallazgos sustentados.
  4. **Visualizaciones:** un gráfico del BCRP, un gráfico elaborado con ENAHO y
  un mapa departamental.
  5. **Interpretación:** explicación de los principales patrones identificados.
  6. **Limitaciones:** cobertura temporal, calidad de los datos y alcance de las
  conclusiones.
  7. **Reproducibilidad:** referencias a los scripts, archivos y series
  utilizadas.

  Todas las cifras deberán poder rastrearse hasta la fuente original o el
  procesamiento correspondiente.

  No se aceptarán afirmaciones numéricas sin sustento o referencias inventadas.

  ## 4. Verificación de resultados

  El estudiante deberá comprobar manualmente al menos **3 afirmaciones numéricas
  del informe**, incluyendo resultados provenientes de ambas fuentes.

  Deberá documentar:

  - La afirmación del informe.
  - El valor calculado.
  - La fuente o procedimiento de verificación.
  - Si el resultado coincide con la referencia.
  - Cualquier diferencia observada.

  Cuando una herramienta falle, no encuentre datos o devuelva una respuesta
  incompatible, el agente deberá informar esa limitación en lugar de inventar
  resultados.

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

  El último componente consiste en evaluar si el uso de MCP y Skills mejora la
  calidad de las respuestas producidas por Claude Code.

  La evaluación deberá utilizar preguntas con respuestas verificables, comparar
  condiciones equivalentes y documentar los resultados.

  ## 1. Diseño del experimento

  Construir un conjunto de **10 preguntas de evaluación**:

  | Tipo de pregunta | Cantidad |
  |---|:---:|
  | Indicadores del BCRP | 4 |
  | Indicadores de ENAHO | 4 |
  | Preguntas que combinan ambas fuentes | 2 |
  | **Total** | **10** |

  Las preguntas deberán tener respuestas esperadas verificadas mediante fuentes
  oficiales o cálculos independientes.

  No se aceptarán preguntas cuyas respuestas correctas hayan sido inventadas o
  definidas únicamente a partir de lo que respondió el agente.

  Guardar el conjunto de preguntas en:

  `evaluacion/preguntas.csv`

  ## 2. Comparación de dos configuraciones

  Cada estudiante deberá ejecutar las mismas 10 preguntas bajo dos condiciones.

  ### Modo A – Sin MCP ni Skills personalizados

  Claude Code deberá responder sin acceso al servidor MCP desarrollado ni a las
  Skills del proyecto.

  Este modo permitirá observar su desempeño sin los componentes especializados.

  ### Modo B – Con MCP y Skills

  Claude Code dispondrá del servidor MCP y las Skills desarrolladas.

  Deberá poder consultar fuentes, procesar datos y ejecutar cálculos mediante
  esas herramientas.

  ### Condiciones del experimento

  - Utilizar las mismas 10 preguntas.
  - Mantener, en lo posible, el mismo modelo y las mismas instrucciones.
  - Ejecutar las preguntas en sesiones independientes para evitar que respuestas
  anteriores contaminen la comparación.
  - Documentar qué otras herramientas estaban habilitadas en cada modo.
  - Evitar que el modo sin herramientas personalizadas acceda indirectamente a
  archivos con las respuestas ya calculadas.
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

  Para las preguntas que combinan ambas fuentes, establecer criterios que
  consideren tanto la exactitud de los datos como la coherencia de la
  interpretación.

  Los resultados deberán guardarse en:

  `evaluacion/resultados.csv`

  El archivo `evaluacion/comparacion.md` deberá presentar una comparación entre
  ambos modos, indicando:

  - Cantidad de respuestas correctas.
  - Respuestas incorrectas o no contestadas.
  - Tiempo promedio de ejecución.
  - Preguntas que mejoraron o empeoraron.
  - Principales errores encontrados.
  - Conclusión sobre la utilidad de MCP y Skills.

  **No es obligatorio que el agente obtenga 10/10 ni que mejore una cantidad
  determinada de respuestas.** Se evaluará la calidad y reproducibilidad del
  experimento, así como la capacidad de explicar sus resultados.

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

  El repositorio deberá incluir las salidas necesarias para comprobar que el
  sistema fue ejecutado.

  **Las conversaciones completas con los asistentes de IA deberán estar
  disponibles en `evidencias_ia/` o mediante un enlace público incluido en el
  README**, con la información sensible previamente ocultada.

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

  Los estudiantes que hayan completado los requisitos principales podrán
  incorporar mejoras como:

  - Crear una Skill adicional para generar automáticamente informes
  socioeconómicos.
  - Integrar un segundo MCP con otra fuente oficial de datos.
  - Diseñar mecanismos para detectar inconsistencias entre resultados de
  diferentes herramientas.
  - Construir un dashboard para explorar los resultados generados por el agente.
  - Implementar pruebas de robustez frente a solicitudes ambiguas o datos
  inexistentes.
  - Incorporar análisis de cómo cambia la calidad de las respuestas al
  desactivar determinadas herramientas.
  - Automatizar la elaboración de informes con tablas, gráficos y referencias.

  Estas mejoras podrán contribuir a obtener la máxima calificación dentro de los
  criterios establecidos, pero no sustituyen los requisitos obligatorios ni
  garantizan puntos adicionales fuera de la rúbrica.

  ---

  ## ✅ Lista de verificación antes de entregar

  ### Servidor MCP

  - [ ] El servidor MCP funciona y cuenta con las cuatro herramientas
  requeridas.
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
  - [ ] El README incluye instalación, arquitectura y procedimiento de
  ejecución.
  - [ ] El repositorio es público y sus enlaces funcionan.

  ### Uso de inteligencia artificial

  - [ ] Se adjuntaron capturas completas o exportaciones de las conversaciones
  utilizadas.
  - [ ] Las evidencias están organizadas en `evidencias_ia/` o mediante un
  enlace público.
  - [ ] Los registros permiten revisar el proceso de desarrollo del MCP, las
  Skills, la integración y la evaluación.
  - [ ] Se ocultaron claves API, contraseñas, tokens y datos personales.

  ---

  ## 📤 Formato y canal de entrega

  Cada estudiante deberá publicar **un comentario en este Issue** utilizando el
  siguiente formato:

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

  - **Repositorio de GitHub:** deberá contener el código, las configuraciones,
  las Skills y los resultados.
  - **Informe final:** enlace directo al documento de investigación desarrollado
  con el agente.
  - **Pruebas MCP:** cantidad de pruebas automatizadas aprobadas, respaldada por
  el código y su ejecución.
  - **Validación ENAHO:** resultados calculados mediante el procesamiento de los
  microdatos.
  - **Evaluación del agente:** resultados obtenidos al ejecutar las mismas diez
  preguntas en las dos condiciones.
  - **Evidencia de integración:** registro o demostración de una ejecución en la
  que Claude Code utilice conjuntamente MCP y Skills.
  - **Evidencias de uso de IA:** capturas completas o exportaciones de las
  conversaciones utilizadas durante el desarrollo.

  No será necesario adjuntar nuevamente los microdatos originales de ENAHO,
  siempre que se proporcionen instrucciones reproducibles para obtenerlos.

  Todos los enlaces deberán ser públicos y accesibles sin solicitar permisos
  adicionales.

  ---

  ## ⏰ Fecha límite de entrega

  **Domingo 8 de noviembre de 2026, hasta las 11:59 p. m. (hora de Perú /
  UTC-5).**

  La entrega deberá realizarse mediante un comentario en este Issue de GitHub,
  siguiendo el formato establecido y proporcionando todos los enlaces
  solicitados.

  ### Política de entregas fuera de plazo

  > [!IMPORTANT]
  > **No se aceptarán trabajos presentados después de la fecha límite sin una
  justificación debidamente sustentada.**
  >
  > Las entregas tardías únicamente podrán ser consideradas de manera
  excepcional, previa evaluación y autorización del equipo docente.
  >
  > En caso de autorizarse una entrega fuera de plazo, se aplicará una
  **penalización de 2 puntos sobre la calificación final por cada día de
  retraso**.
  >
  > La presentación de una justificación no garantiza la aceptación de la
  entrega tardía. Cada caso será evaluado individualmente por el equipo docente.

  Para aplicar la penalización, se contabilizará cada período de 24 horas de
  retraso iniciado después del vencimiento del plazo. Cualquier fracción de un
  nuevo período se considerará un día adicional.

  **Ejemplo:** Para un trabajo que obtiene 18/20 según la rúbrica:

  | Retraso | Penalización | Nota final |
  |---|:---:|:---:|
  | 1 día | −2 | 16 |
  | 2 días | −4 | 14 |
  | 3 días | −6 | 12 |
  | 4 días | −8 | 10 |

  La penalización se aplicará sobre la nota obtenida según la rúbrica de 20
  puntos, sin que la calificación final pueda ser inferior a 0.

  Se recomienda comprobar con anticipación que:

  - El repositorio y todos los enlaces sean accesibles.
  - Los scripts, pruebas y resultados estén correctamente guardados.
  - Las evidencias del uso de IA estén completas.
  - No se hayan publicado credenciales ni información sensible.
  - El comentario de entrega se haya registrado correctamente dentro del plazo.

  ---

  ## 🎯 Resultado esperado

  Al finalizar esta tarea, cada estudiante deberá contar con un **agente de
  investigación socioeconómica funcional**, capaz de consultar información
  oficial del BCRP mediante MCP, procesar y analizar microdatos de ENAHO
  mediante Skills y elaborar informes con resultados verificables.

  **El proyecto estará completo cuando el agente pueda responder una pregunta
  real utilizando ambas herramientas, y cuando otra persona pueda reproducir,
  evaluar y comprobar los resultados obtenidos.**

  El propósito es desarrollar competencias para construir sistemas de
  inteligencia artificial que no se limiten a generar respuestas, sino que sean
  capaces de **utilizar herramientas, ejecutar procedimientos reproducibles y
  producir evidencia confiable para el análisis de datos y la investigación
  social**.

  **¡Éxitos con sus proyectos!** 🚀

  ===== END ISSUE BODY =====

  Ran 1 shell command (ctrl+o to expand)

● La estructura de la Tarea 4 está lista, y uv run pytest -q da 1 passed, 7 
  failed, como esperabas.

  - Archivos copiados: bajé server.py y test_server.py a mcp/, y pyproject.toml,
    preguntas.csv y evaluar.py a la raíz, directo desde el repo de la
    sesión 04. No toqué test_server.py.
  - Imports: el arreglo fue solo en pyproject.toml, agregando
    [tool.pytest.ini_options] con pythonpath = ["mcp"] y testpaths = ["mcp"].
  - .gitignore: incluye datos/, .venv/, __pycache__/, *.pyc, .pytest_cache/,
    *.tmp, *.log y .DS_Store.
  - Carpetas: creé salidas, figuras, mapas, evaluacion, informes y
    evidencias_ia/ con mcp, skills, integracion y evaluacion.
  - .gitkeep: puse uno en cada carpeta vacía para que git las conserve. Si
    prefieres que queden sin nada, bórralos.
  - Las pruebas que fallan son las esperadas, porque los TODO de server.py están
    sin completar. La que pasa es test_buscar_encuentra_el_ipc.
  - Catálogo del BCRP: server.py usa AQUI = Path(__file__).parent, así que el
    catálogo se descargó en mcp/datos/ y no en datos/ de la raíz. Para que
    .gitignore también lo ignore ahí, hay que cambiar datos/ por **/datos/, o
    cambiar AQUI en server.py para que apunte a la raíz. No lo cambié porque no
    lo pediste. Dime cuál prefieres.

✻ Crunched for 4m 38s · done 5:59 AM

❯ Prefiero cambiar el .gitignore a **/datos/, así ignora cualquier carpeta      
  datos sin tocar server.py. Hazlo y confirma con git status que ni datos/ ni   
  mcp/datos/ aparecen.                                                          
                                                                                
  Otra cosa: noté que los Fetch solo recibieron 148 bytes, así que no leíste el 
  enunciado. Descárgalo con curl desde                                          
  https://api.github.com/repos/d2cml-ai/Data-Science-Python/issues/201, guarda  
  el campo "body" en ENUNCIADO.md y léelo completo. Luego hazme un resumen de 5 
  líneas con lo que pide la Parte 1, para confirmar que lo entendiste.          

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● Cambié .gitignore y guardé el enunciado en ENUNCIADO.md, que leí completo.

  Git: la primera línea de .gitignore ahora es **/datos/. En git status no
  aparecen ni datos/ ni mcp/datos/. git check-ignore confirma que ambas rutas
  las ignora esa regla, que es la única que las cubre. Aparecen sin seguimiento
  uv.lock, que se generó al correr uv run, y ENUNCIADO.md. Decide tú si los
  subes.

  Enunciado: el campo body del API trae el contenido dos veces, primero en HTML
  y luego en Markdown. Por eso ENUNCIADO.md tiene un bloque HTML al inicio, sin
  las secciones intermedias, y el Markdown completo desde la línea 13. Lo leí
  entero.

  Sobre los 148 bytes de los Fetch: mi primera versión del enunciado vino de un
  subagente, no de una lectura directa mía. Las cifras principales coinciden con
  el archivo descargado.

  Parte 1 (5 pts), en 5 líneas:
  1. Hay que completar mcp/server.py con al menos 4 herramientas: buscar_series,
     serie, resumen y una propia que no duplique las anteriores (por ejemplo
     correlacion o comparar_periodos). Todos los cálculos los hace Python, no el
     modelo.
  2. Se necesita un recurso MCP con la ficha descriptiva de una serie y un
     prompt MCP reutilizable para informes. Ambos deben ser accesibles desde el
     cliente.
  3. Se configura .mcp.json y se demuestra en Claude Code que el agente
     identifica la serie, pide los datos, calcula con las herramientas y
     presenta el resultado con código de serie, período y fuente.
  4. Las pruebas son las 8 originales sin modificar, solo con ajustes de
     importación por la nueva ubicación, más 2 propias para la herramienta
     nueva. La meta es 10 passed.
  5. La rúbrica es: servidor con búsqueda, consulta y resumen 2.0; herramienta
     propia útil, validada y documentada 1.0; recurso, prompt e integración con
     Claude Code 1.0; y 10 pruebas aprobadas 1.0.

  Un detalle de plazo: la entrega vence el domingo 8 de noviembre a las 11:59 p.
  m. (hora de Perú), y hoy es 7 de noviembre. La entrega es un comentario en el
  issue con el formato del enunciado, y el repositorio debe ser público.

✻ Sautéed for 22s · done 6:03 AM

❯ Sí, sube uv.lock (fija las versiones exactas, sirve para la reproducibilidad) 
  y también ENUNCIADO.md. Haz un primer commit: "Tarea 4: estructura inicial    
  del proyecto".                                                                
                                                                                
  Ahora el TODO 1. Antes de escribir código explícame qué pide serie(): qué     
  formato de fechas pide la API del BCRP y cómo vas a convertir los periodos    
  que devuelve (Ene.2025, 01.Oct.26, T1.25, 2025 y el caso Set de setiembre).   
  Quiero entenderlo antes de que lo implementes. Después impleméntalo, con      
  reintento si la API devuelve HTML y con caché, y corre uv run pytest -q -k    
  serie.                                                                        

  Ran 1 shell command (ctrl+o to expand)

● Commit hecho (9033c9a), con uv.lock y ENUNCIADO.md incluidos. Los narracion.*
  de tarea_3 quedaron fuera.

  Qué pide serie() (antes de escribir código)

  Qué hace. serie(codigo, desde, hasta) descarga una serie del BCRP y devuelve
  {"codigo", "nombre", "frecuencia", "datos": [{"periodo", "valor"}], "fuente"}.
  La URL es f"{API}/{codigo}/json/{desde}/{hasta}", y la respuesta es
  {"config": {...}, "periods": [{"name": "Ene.2025", "values": ["0.81"]}, ...]}.

  Fechas que pide la API. Dependen de la frecuencia de la serie, que leo con
  _ficha(codigo):

  ┌──────────────────────┬─────────────────────────┬────────────┐
  │      Frecuencia      │ Formato que pide la API │  Ejemplo   │
  ├──────────────────────┼─────────────────────────┼────────────┤
  │ Mensual y trimestral │ AAAA-M                  │ 2025-1     │
  ├──────────────────────┼─────────────────────────┼────────────┤
  │ Diaria               │ AAAA-MM-DD              │ 2025-01-15 │
  ├──────────────────────┼─────────────────────────┼────────────┤
  │ Anual                │ AAAA                    │ 2025       │
  └──────────────────────┴─────────────────────────┴────────────┘

  Los tests entregan desde="2025-01" para mensuales, así que antes de llamar
  tengo que adaptar la fecha a lo que espera la API según la frecuencia.

  Cómo convierto los nombres que devuelve a un periodo estándar:

  ┌────────────┬──────────────────────────────────────┬─────────────┐
  │ Frecuencia │           La API devuelve            │ Yo devuelvo │
  ├────────────┼──────────────────────────────────────┼─────────────┤
  │ Mensual    │ Ene.2025                             │ 2025-01     │
  ├────────────┼──────────────────────────────────────┼─────────────┤
  │ Diaria     │ 01.Oct.26 (día.mes.año de 2 dígitos) │ 2026-10-01  │
  ├────────────┼──────────────────────────────────────┼─────────────┤
  │ Trimestral │ T1.25                                │ 2025-T1     │
  ├────────────┼──────────────────────────────────────┼─────────────┤
  │ Anual      │ 2025                                 │ 2025        │
  └────────────┴──────────────────────────────────────┴─────────────┘

  - Meses: un diccionario de abreviaturas a número: Ene=1, Feb=2, Mar=3, Abr=4, 
    May=5, Jun=6, Jul=7, Ago=8, Set=9, Oct=10, Nov=11, Dic=12.
  - Setiembre: el BCRP escribe Set y no Sep. Por eso el diccionario usa Set. Un
    parser con strptime("%b") fallaría ahí, así que no lo uso.
  - Año de 2 dígitos (diaria y trimestral): sumo 2000. Es seguro porque las
    series del BCRP empiezan a partir de 1990. Una serie anterior a 2000 daría
    mal el año, y eso lo dejaría anotado.
  - Valores n.d. (no disponible): se saltan, y no se rellenan con 0 ni con
    interpolación.

  Dos riesgos de la API:
  1. Limita pedidos seguidos: responde una página HTML en vez de JSON. Detecto
     eso al fallar response.json() y reintento con espera creciente. Si se
     agotan los intentos, doy un ToolError claro.
  2. Código inexistente: _ficha() ya lanza ToolError con el código antes de
     llamar a la API, así que test_codigo_inexistente_da_un_error_claro debería
     pasar de forma natural.

  Caché: guardo en memoria el resultado por (codigo, desde, hasta) para no
  repetir pedidos. Como serie la usará después resumen, ahí está el mayor
  ahorro.

  Ahora lo implemento. Antes confirmo con un pedido real que la respuesta tiene
  la forma descrita.

  Ran 2 shell commands (ctrl+o to expand)

● La API devolvió Sep.2025 en una serie mensual, y la pista del enunciado decía
  Set. Acepto las dos grafías. El diccionario MESES queda con Sep y Set
  apuntando a 9.

  Ran 2 shell commands (ctrl+o to expand)

● serie() ya está implementada en mcp/server.py. uv run pytest -q -k serie da 2 
  passed: test_serie_mensual y test_serie_diaria.

  La suite completa está en 4 passed y 4 failed.
  test_codigo_inexistente_da_un_error_claro también pasa, aunque -k serie no la
  selecciona porque no lleva "serie" en el nombre. Las 4 que faltan son las de
  los TODO 2 a 5: resumen, la herramienta propia, el recurso y el prompt.

  Lo que hace el código:
  - Fechas: _fecha_api convierte la fecha según la frecuencia de la serie:
    2025-1 para mensual y trimestral, AAAA-MM-DD para diaria y AAAA para anual.
  - Periodos: _periodo convierte Ene.2025, 01.Oct.26, T1.25 y 2025 a 2025-01,
    2026-10-01, 2025-T1 y 2025.
  - Reintento: _descargar pide a la API hasta 5 veces, con espera creciente de
    2, 4, 6 y 8 segundos, si llega HTML en vez de JSON. Si se agotan los
    intentos, da un ToolError claro.
  - Caché: @cache guarda por (codigo, desde, hasta) en memoria. Los errores no
    se guardan.
  - Valores n.d.: se omiten. Si no queda ningún dato, hay un ToolError.

  Corrección a mi explicación: dije que el BCRP escribe Set para setiembre.
  Verifiqué con la API real y depende de la frecuencia. Las series diarias usan
  Set (29.Set.25), pero las mensuales usan Sep (Sep.2025). El primer pytest
  falló por eso. El diccionario de meses acepta ahora las dos grafías.

  Cosas que dejé así:
  - Año de 2 dígitos: en diaria y trimestral sumo 2000. Una serie anterior a
    2000 saldría mal, pero los tests y las series que usamos son posteriores.
  - Trimestral sin probar: el formato de fecha trimestral sale del comentario
    del enunciado y no lo probé contra la API real. Los tests no lo cubren. Si
    usas una serie trimestral en la herramienta propia, lo verifico antes.
  - Sin commit: no hice commit de este cambio. Dime si lo hago ahora o después
    de completar resumen.

✻ Cogitated for 2m 0s · done 6:07 AM

※ recap: Estamos armando la Tarea 4, el agente con MCP del BCRP y Skills de ENAHO, y acabo de terminar `serie()`, que ya pasa sus pruebas (4 de 8 pasan en total). Lo siguiente es implementar `resumen()`, el TODO 2, para que pase `test_resumen_sin_cuentas_a_mano`. (disable recaps in /config)

❯ Bien visto lo de Sep/Set. Dos cosas antes de seguir:                          
  1. El año de 2 dígitos: no quiero que una fecha de 1997 salga 2097. Si el año 
  de 2 dígitos es mayor que el año actual en 2 dígitos, que sea 19XX; si no,    
  20XX. Pruébalo con el tipo de cambio diario de algún día de 1998.             
  2. Haz commit ahora: "Tarea 4: serie() con conversión de fechas del BCRP,     
  reintento y caché".                                                           
                                                                                
  Luego el TODO 2 (resumen). Como economista me interesa que la variación       
  porcentual sea (último/primero − 1)×100 y que el máximo y el mínimo vengan    
  con su periodo. Implementa y corre la prueba test_resumen_sin_cuentas_a_mano. 
  Explícame en 3 líneas qué devuelve cada campo.                                

  Ran 1 shell command (ctrl+o to expand)

● Antes del commit pruebo el siglo con un día de 1998.

  Ran 1 shell command (ctrl+o to expand)

● La conversión de siglo funciona (98 salió como 1998). Ahora voy a sacar
  resumen un momento para que el commit contenga solo serie(). · summary

  Ran 1 shell command (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: Tip: Run /ultrareview before you push to catch bugs 
     with a cloud-based multi-agent review — 3 free reviews left.

● Hice el commit de serie(). resumen está implementado y
  test_resumen_sin_cuentas_a_mano pasa. La suite va en 5 passed y 3 failed:
  faltan la herramienta propia, el recurso y el prompt.

  1. Siglo del año de 2 dígitos
  - La regla nueva: si el año de 2 dígitos es mayor que el año actual en 2
    dígitos, es 19XX. Si no, es 20XX. Hoy 97 da 1997, 26 da 2026 y 27 da 1927.
  - Con el tipo de cambio diario PD04638PD del 2 al 6 de marzo de 1998, los
    periodos salieron como 1998-03-02 a 1998-03-06, con valores entre 2.807 y
    2.815 S/ por US$.
  - La regla se aplica en series diarias y trimestrales. Con ella, cada año que
    pase el límite se mueve solo.

  2. Commit 5bac6fd
  Contiene solo serie() y sus ayudantes, con el mensaje que pediste. resumen ya
  estaba escrito en el archivo, así que lo saqué un momento del commit y lo
  restauré. Está sin commitear, como modificación de mcp/server.py. Dime si lo
  commiteo.

  3. resumen()
  La variación es (último / primero − 1) × 100. Si el primer valor es 0 devuelve
  None en vez de fallar. El máximo y el mínimo traen su periodo.

  Qué devuelve cada campo:
  - primero, ultimo, maximo, minimo: cada uno es {periodo, valor}. El primero y
    el último son los extremos del rango pedido, ya sin n.d.. El máximo y el
    mínimo son los valores extremos y el periodo donde ocurrieron.
  - cambio, variacion_pct, promedio: cambio = último − primero, en las unidades
    de la serie. variacion_pct es el cambio relativo en %. promedio es la media
    simple de todos los datos del rango.
  - codigo, nombre, frecuencia, n_datos, fuente: identifican la serie y dan la
    URL de la API de donde salen los datos, para citarla.

  Cuidado con las series que ya son tasas. En la inflación a 12 meses, cambio
  son puntos porcentuales. Por ejemplo, de 1.51 % a 4.55 % es +3.04 pp.
  variacion_pct mediría el cambio relativo de la tasa, que es +201 %, y eso casi
  nunca es lo que interesa. Lo dejé escrito en el docstring para que Claude no
  confunda ambos. Si prefieres que en series de tasas se omita variacion_pct, lo
  ajusto.

✻ Baked for 1m 33s · done 6:21 AM

❯ Deja variacion_pct, porque la prueba original exige ese campo; la nota sobre  
  puntos porcentuales en el docstring es suficiente. Commitea resumen: "Tarea   
  4: resumen() con variación, promedio y extremos".                             
                                                                                
  Ahora mi herramienta propia: comparar_periodos(codigo, desde_a, hasta_a,      
  desde_b, hasta_b), que devuelve el promedio, el máximo y el mínimo de un      
  indicador en dos tramos, y la diferencia de promedios en las unidades de la   
  serie (en pp si es una tasa). La elegí porque mi pregunta de investigación    
  compara la inflación antes y después de 2022, y resumen solo mira un tramo.   
  Reutiliza serie y resumen, sin repetir código. El docstring debe decir cuándo 
  usarla, con un ejemplo de argumentos, y la respuesta debe incluir las URL de  
  la fuente.                                                                    
                                                                                
  Después agrega 2 pruebas mías al final de test_server.py, sin tocar las 8     
  originales:                                                                   
  1. Coherencia: el promedio del tramo A en comparar_periodos debe ser igual al 
  promedio que da resumen para ese mismo tramo.                                 
  2. Error claro: un tramo sin datos o un código inexistente debe dar           
  ToolError.                                                                    
     Corre todas las pruebas y explícame qué comprueba cada prueba nueva.       

  Ran 1 shell command (ctrl+o to expand)

● Commiteé resumen (8f51095). comparar_periodos y las 2 pruebas nuevas están
  escritas, y la suite va en 8 passed y 2 failed. Los 2 que faltan son
  test_un_recurso y test_un_prompt, que son los TODO 4 y 5.

  git diff sobre test_server.py muestra 22 líneas añadidas y 0 borradas, así que
  las 8 originales quedaron intactas. Lo nuevo de server.py y test_server.py
  está sin commitear.

  La herramienta comparar_periodos
  - Sin repetir código: moví la lógica de resumen a un ayudante _resumen().
    resumen y comparar_periodos lo usan, y este a su vez usa _serie().
  - Qué devuelve: tramo_a y tramo_b, cada uno con desde, hasta, n_datos,
    promedio, máximo y mínimo (con su periodo) y su URL. También devuelve
    diferencia_promedios (B − A, en las unidades de la serie) y la lista fuentes
    con las dos URL.
  - Docstring: dice cuándo usarla, trae el ejemplo con la inflación PN01273PM
    antes y después de 2022, aclara que la diferencia está en pp si la serie es
    una tasa y avisa que es una comparación descriptiva y no causal.

  Qué comprueba cada prueba nueva
  1. test_comparar_periodos_coincide_con_resumen comprueba que comparar_periodos
     no calcula por su cuenta. Con la inflación 2019 (tramo A) y 2023 (tramo
     B), comprueba que:
     - el promedio del tramo A es igual al que da resumen para 2019;
     - el máximo del tramo B, con su periodo, es igual al de resumen para 2023;
     - diferencia_promedios es exactamente promedio B − promedio A;
     - las dos fuentes son URL del BCRP.
  2. test_comparar_periodos_error_claro comprueba que las fallas no pasan en
     silencio. Un código inexistente (XX999) da ToolError que nombra el código.
     Un tramo B sin datos (2099) da ToolError que nombra la serie PN01273PM, en
     vez de devolver promedios vacíos o inventados.

  Dos observaciones:
  - Los tramos pueden solaparse y no lo valido. Si te interesa, puedo agregar un
    error para ese caso.
  - La prueba 2 usa 2099 como "sin datos". Funciona hoy, y la API respondió sin
    reintentos.

  ¿Commiteo comparar_periodos y las pruebas con un mensaje como "Tarea 4:
  comparar_periodos() y 2 pruebas propias"?

✻ Churned for 51s · done 6:23 AM

※ recap: Estamos armando el servidor MCP del BCRP para la Tarea 4. Ya funcionan buscar_series, serie, resumen y comparar_periodos con 8 de 10 pruebas pasando. Lo siguiente es commitear comparar_periodos, o pasar directo al recurso y al prompt (TODOs 4 y 5). (disable recaps in /config)
❯ Sí, commitea con ese mensaje. No hace falta validar tramos que se solapen.    
                                                                                
  Ahora los TODO 4 y 5:                                                         
  - un recurso bcrp://serie/{codigo} que devuelva la ficha de la serie (nombre, 
  frecuencia, desde cuándo hay datos y última actualización);                   
  - un prompt informe(tema) que pida buscar la serie, usar resumen o            
  comparar_periodos en vez de calcular a mano, y citar el código, el periodo y  
  la fuente de cada cifra.                                                      
    Corre uv run pytest -q. La meta es 10 passed; muéstrame la salida completa. 
                                                                                
  Si da 10 passed, commitea: "Tarea 4: recurso, prompt y 10 pruebas aprobadas". 
  Luego conecta el servidor a Claude Code con alcance de proyecto (debe quedar  
  en .mcp.json, sin claves). Agrega también el servidor fetch como en la        
  sesión 04. Muéstrame el .mcp.json y dime qué comando usaste.                  

  Ran 3 shell commands (ctrl+o to expand)

● 10 passed. Compruebo que el recurso y el prompt devuelvan lo esperado, hago el
  commit y conecto el servidor.

  Ran 3 shell commands (ctrl+o to expand)

● El servidor ya está registrado en .mcp.json, pero Claude Code todavía no lo
  aprobó, así que no comprobé que conecte. La suite da 10 passed.

  ..........                                                               
  [100%]
  10 passed in 13.54s

  Commits de esta ronda:
  - 4c2bf01: comparar_periodos() y 2 pruebas propias.
  - e60cbe9: recurso, prompt y 10 pruebas aprobadas.

  Recurso y prompt:
  - Recurso bcrp://serie/{codigo}: devuelve un JSON con código, nombre,
    frecuencia, datos_desde, ultima_actualizacion, categoría y la URL del
    catálogo. Para PN01273PM da datos desde Ene-1950 y última actualización
    2026-10-08. No descarga datos de la serie.
  - Prompt informe(tema): pide buscar la serie con buscar_series y confirmar su
    ficha en el recurso. Luego pide usar resumen o comparar_periodos y citar
    código, periodo y fuente de cada cifra. También pide expresar las tasas en
    pp, informar las fallas sin inventar cifras y no presentar asociaciones como
    causalidad.
  - Un tropiezo: el primer intento del prompt quedó con un salto de línea mal
    escapado y rompió la importación. Lo reescribí y ya pasa.

  Conexión a Claude Code. Los comandos, desde tarea_4/:
  claude mcp add --scope project bcrp -- uv run mcp/server.py
  claude mcp add --scope project fetch -- uvx mcp-server-fetch
  El .mcp.json resultante:
  {
    "mcpServers": {
      "bcrp":  { "type": "stdio", "command": "uv",  "args": ["run",
  "mcp/server.py"], "env": {} },
      "fetch": { "type": "stdio", "command": "uvx", "args":
  ["mcp-server-fetch"],     "env": {} }
    }
  }
  Ninguno de los dos lleva claves: env está vacío.

  Pendiente de tu parte:
  - Aprobación: claude mcp get bcrp dice «Pending approval». Abre claude en
    tarea_4/ y acepta los servidores del .mcp.json. Después /mcp debería mostrar
    los dos conectados.
  - Evidencia de integración: conviene guardar en evidencias_ia/mcp/ una captura
    de /mcp y de una consulta real, por ejemplo /mcp__bcrp__informe inflación.
  - Ruta relativa: el comando usa mcp/server.py sin ruta absoluta, así que
    claude hay que abrirlo desde tarea_4/. Es lo que conviene para el repo, pero
    si lo abres desde otra carpeta no conectará. evaluar.py también espera
    .mcp.json en tarea_4/.
  - Sin commit: el .mcp.json no está commiteado. ¿Lo commiteo con un mensaje
    como «Tarea 4: .mcp.json con bcrp y fetch»?
  - Caracteres en consola: vi caracteres raros («�») al imprimir el recurso en
    la consola de Windows. Es un problema de la consola y no del servidor: el
    archivo se guarda en UTF-8. Si en /mcp ves tildes rotas, avísame.

✻ Crunched for 2m 4s · done 6:34 AM

※ recap: Estamos armando el servidor MCP del BCRP para la Tarea 4, y ya pasa las 10 pruebas con `.mcp.json` listo (bcrp y fetch). Lo siguiente es abrir `claude` en `tarea_4/`, aprobar los servidores y confirmar en `/mcp` que conectan. (disable recaps in /config)

❯ Sí, commitea el .mcp.json con ese mensaje.                                    

  Ran 1 shell command (ctrl+o to expand)

● Commit hecho: 2908dd4 «Tarea 4: .mcp.json con bcrp y fetch». Contiene solo
  .mcp.json, con 21 líneas añadidas, y no queda nada pendiente en tarea_4/.

  Todavía falta que apruebes los servidores abriendo claude en tarea_4/, como
  indiqué antes.

  La Parte 1 del enunciado queda así:
  - Herramientas: buscar_series, serie, resumen y comparar_periodos.
  - Recurso y prompt: bcrp://serie/{codigo} e informe.
  - Pruebas: 10 passed.
  - .mcp.json: commiteado, con bcrp y fetch y sin claves.

  Lo que falta de esta parte es la demostración real en Claude Code. Para eso,
  tras aprobar los servidores, haz una consulta como «¿Cómo cambió la inflación
  a 12 meses entre 2019 y 2023?». Debería llamar a buscar_series y luego a
  comparar_periodos. Guarda esa conversación en evidencias_ia/mcp/.

  Las Skills de ENAHO, la Parte 2, son lo siguiente. Los datos ya están en
  datos/ como 966-Modulo02.zip y 966-Modulo34.zip. Como el plazo vence mañana a
  las 11:59 p. m., te propongo empezar por limpiando-enaho, porque las otras dos
  Skills y el informe dependen de ella.

✻ Worked for 13s · done 6:39 AM