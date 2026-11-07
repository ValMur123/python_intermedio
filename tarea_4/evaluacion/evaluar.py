"""Experimento de la Parte 4: las mismas 10 preguntas sin MCP ni Skills (modo A) y con ellos (modo B).

    uv run evaluacion/evaluar.py                                   # 10 preguntas, modos A y B, Sonnet
    uv run evaluacion/evaluar.py --ids q01 q05 --salida evaluacion/resultados_prueba.csv

Cada pregunta corre con `claude -p` en una sesión independiente (--no-session-persistence) y con el mismo modelo.
Las herramientas usadas se leen del stream de salida (stream-json), no se suponen.
Configuración detallada de cada modo: evaluacion/configuracion.md. Criterios de q09 y q10: evaluacion/criterios.md.
"""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent          # evaluacion/
RAIZ = AQUI.parent                    # raíz del proyecto (tarea_4/)
CLAUDE = shutil.which("claude") or "claude"

ESQUEMA = {
    "type": "object", "required": ["valores", "fuente", "interpretacion"],
    "properties": {
        "valores": {"type": "array", "items": {"type": ["number", "null"]}},
        "unidades": {"type": "string"},
        "periodo": {"type": "string"},
        "fuente": {"type": "string"},
        "interpretacion": {"type": "string"},
    },
}
# Una sola instrucción, idéntica en los dos modos.
INSTRUCCION = (
    "Responde con un JSON. En «valores» pon una lista con un número por cada dato que pide la pregunta, en el orden "
    "en que los pide y en la unidad que corresponde. Si la pregunta pide un mes, indícalo en «periodo» (AAAA-MM). "
    "En «fuente» di de dónde sale cada cifra. En «interpretacion» da una explicación breve (1 a 3 frases) cuando la "
    "pregunta pida interpretar; si no, déjala vacía. Si no puedes saber una cifra con certeza, pon null en su lugar: "
    "no estimes.\n\n"
)

# Rutas con respuestas esperadas o transcripciones: el modo B no puede leerlas con la herramienta Read.
RUTAS_PROHIBIDAS = ["evaluacion", "preguntas.csv", "referencias", "evidencias_ia"]
# Modo A: sin ninguna herramienta, sin MCP, sin skills y desde un directorio vacío fuera del repositorio.
# Modo B: MCP bcrp (solo ese), Skill, Read y Bash limitado a `uv run`; sin WebSearch ni WebFetch.
MODOS = {
    "A": ["--tools", "", "--strict-mcp-config", "--disable-slash-commands"],
    "B": ["--tools", "Skill,Read,Bash",
          "--strict-mcp-config", "--mcp-config", str(AQUI / "mcp_bcrp.json"),
          "--allowedTools", "mcp__bcrp,Skill,Read,Bash(uv run:*)",
          "--disallowedTools", ",".join(f"Read(./{r}/**),Read(./{r})" for r in RUTAS_PROHIBIDAS)],
}
PATRON_SOSPECHOSO = re.compile(r"evaluacion|preguntas\.csv|referencias|evidencias_ia")
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "sep": 9,
         "oct": 10, "nov": 11, "dic": 12}


def resumir_herramientas(eventos):
    """Cuenta las herramientas usadas y marca llamadas que tocan rutas con respuestas esperadas."""
    usos, sospechosas = Counter(), []
    for ev in eventos:
        if ev.get("type") != "assistant":
            continue
        for bloque in ev.get("message", {}).get("content", []):
            if bloque.get("type") == "tool_use":
                if bloque["name"] != "StructuredOutput":   # herramienta interna para entregar el JSON
                    usos[bloque["name"]] += 1
                entrada = json.dumps(bloque.get("input", {}), ensure_ascii=False)
                if PATRON_SOSPECHOSO.search(entrada):
                    sospechosas.append(f"{bloque['name']}: {entrada[:150]}")
    return "; ".join(f"{n} x{c}" for n, c in usos.items()), " | ".join(sospechosas)


def preguntar(pregunta, modo, modelo, tmp_vacio):
    cmd = [CLAUDE, "-p", INSTRUCCION + pregunta, "--output-format", "stream-json", "--verbose",
           "--json-schema", json.dumps(ESQUEMA), "--no-session-persistence", "--model", modelo, *MODOS[modo]]
    cwd = tmp_vacio if modo == "A" else RAIZ
    t = time.time()
    fila = {"respuesta": "", "periodo": "", "interpretacion": "", "fuente_declarada": "", "herramientas_usadas": "",
            "accesos_sospechosos": "", "disponibles": "", "turnos": None, "error": ""}
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900, cwd=cwd)
    except subprocess.TimeoutExpired:
        return {**fila, "error": "timeout (900 s)", "segundos": round(time.time() - t, 1)}
    fila["segundos"] = round(time.time() - t, 1)
    eventos = []
    for linea in proc.stdout.splitlines():
        try:
            eventos.append(json.loads(linea))
        except json.JSONDecodeError:
            pass
    fila["herramientas_usadas"], fila["accesos_sospechosos"] = resumir_herramientas(eventos)
    ini = next((e for e in eventos if e.get("type") == "system" and e.get("subtype") == "init"), {})
    fila["disponibles"] = ", ".join(sorted(t for t in ini.get("tools", []) if t != "StructuredOutput")) or "(ninguna)"
    if ini.get("mcp_servers"):
        fila["disponibles"] += " | MCP: " + ", ".join(m.get("name", "?") for m in ini["mcp_servers"])
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), None)
    if final is None:
        fila["error"] = ("sin resultado: " + (proc.stderr or proc.stdout)[-300:]).strip()
        return fila
    fila["turnos"] = final.get("num_turns")
    if final.get("is_error"):
        fila["error"] = str(final.get("result", ""))[:300]
    r = final.get("structured_output") or {}
    if not r and not fila["error"]:
        fila["error"] = "sin salida estructurada: " + str(final.get("result", ""))[:300]
    fila.update(respuesta=json.dumps(r.get("valores"), ensure_ascii=False) if r else "",
                periodo=r.get("periodo", ""), interpretacion=r.get("interpretacion", ""),
                fuente_declarada=r.get("fuente", ""))
    return fila


def numeros(texto):
    """Primer número de cada parte separada por '|' (la verdad puede traer notas entre paréntesis)."""
    return [float(re.search(r"-?\d+(?:\.\d+)?", parte).group()) for parte in str(texto).split("|")]


def mes_esperado(verdad):
    """Devuelve (año, mes) si la verdad trae un mes entre paréntesis, p. ej. '(feb-2023)'."""
    m = re.search(r"\((\w{3})\w*-(\d{4})\)", str(verdad))
    return (int(m.group(2)), MESES[m.group(1).lower()]) if m else None


def mes_coincide(periodo, esperado):
    anio, mes = esperado
    p = str(periodo).lower()
    return bool(re.search(rf"{anio}[-/ ]0?{mes}\b|0?{mes}[-/ ]{anio}", p) or
                (re.search(str(anio), p) and any(k in p and v == mes for k, v in MESES.items())))


def calificar(fila, verdad, tolerancia):
    """acierta / se equivoca / no sabe. Compara solo las cifras (y el mes en q09); la coherencia es manual."""
    try:
        dado = json.loads(fila["respuesta"]) if fila["respuesta"] else None
    except json.JSONDecodeError:
        dado = None
    if not dado or all(v is None for v in dado):
        return "no sabe" if not fila["error"] else "error"
    esperados, tols = numeros(verdad), numeros(tolerancia)
    if len(dado) != len(esperados) or any(v is None for v in dado):
        return "no sabe" if all(v is None for v in dado) else "se equivoca"   # cifra faltante o de más
    bien = all(abs(v - e) <= t for v, e, t in zip(dado, esperados, tols))
    mes = mes_esperado(verdad)
    if mes and not mes_coincide(fila["periodo"], mes):
        bien = False
    return "acierta" if bien else "se equivoca"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--modos", nargs="+", default=["A", "B"], choices=list(MODOS))
    p.add_argument("--modelo", default="sonnet")
    p.add_argument("--ids", nargs="+", help="solo estas preguntas (por defecto, todas)")
    p.add_argument("--preguntas", default=str(AQUI / "preguntas.csv"))
    p.add_argument("--salida", default=str(AQUI / "resultados.csv"))
    p.add_argument("--paralelo", type=int, default=1, help="1 por defecto para que los tiempos sean comparables")
    a = p.parse_args()

    preguntas = pd.read_csv(a.preguntas, dtype=str, keep_default_na=False)
    if a.ids:
        preguntas = preguntas[preguntas.id.isin(a.ids)]
    casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
    print(f"{len(casos)} llamadas a claude -p con {a.modelo}...", flush=True)
    with tempfile.TemporaryDirectory(prefix="modoA_") as vacio, ThreadPoolExecutor(a.paralelo) as ex:
        respuestas = list(ex.map(lambda c: preguntar(c[0].pregunta, c[1], a.modelo, vacio), casos))

    filas = []
    for (q, m), r in zip(casos, respuestas):
        filas.append({"id": q.id, "tipo": q.tipo, "modo": m, "pregunta": q.pregunta, "verdad": q.verdad,
                      **{k: r[k] for k in ("respuesta", "periodo", "interpretacion", "fuente_declarada",
                                            "herramientas_usadas", "disponibles", "accesos_sospechosos")},
                      "resultado": calificar(r, q.verdad, q.tolerancia),
                      "segundos": r["segundos"], "turnos": r["turnos"], "error": r["error"],
                      "coherencia": "", "resultado_final": ""})   # las dos últimas, a mano (q09 y q10)
    res = pd.DataFrame(filas)
    res.to_csv(a.salida, index=False, encoding="utf-8")

    print("\n" + res[["id", "modo", "verdad", "respuesta", "resultado", "segundos", "herramientas_usadas"]].to_string())
    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos_prom"] = res.groupby("modo").segundos.mean().round(1)
    print("\n" + tabla.to_string())
    if res.accesos_sospechosos.any():
        print("\nATENCIÓN: llamadas que tocan rutas con respuestas esperadas, ver columna accesos_sospechosos.")
