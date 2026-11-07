"""Descarga las 3 series de inflación del BCRP con la herramienta `serie` del servidor MCP.

    uv run scripts/descargar_bcrp.py

Llama al servidor en memoria con fastmcp.Client (igual que mcp/test_server.py), sin tocar la
API a mano ni transcribir valores, y escribe salidas/bcrp_inflacion_2020_2024.csv
con las columnas codigo, nombre, periodo, valor y fuente.
"""
from __future__ import annotations

import asyncio
import csv
import sys
from pathlib import Path

from fastmcp import Client

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "mcp"))  # como pythonpath de pytest; evita confundir con el paquete `mcp`
from server import mcp  # noqa: E402

SERIES = ["PN01273PM", "PN09822PM", "PN01279PM"]
DESDE, HASTA = "2020-01", "2024-12"
SALIDA = RAIZ / "salidas" / "bcrp_inflacion_2020_2024.csv"


async def descargar() -> list[dict]:
    async with Client(mcp) as c:
        return [(await c.call_tool("serie", {"codigo": s, "desde": DESDE, "hasta": HASTA})).data
                for s in SERIES]


def main() -> None:
    respuestas = asyncio.run(descargar())
    filas = []
    for r in respuestas:
        if len(r["datos"]) != 60:
            raise SystemExit(f"{r['codigo']}: se esperaban 60 meses y llegaron {len(r['datos'])}")
        filas += [[r["codigo"], r["nombre"], d["periodo"], d["valor"], r["fuente"]] for d in r["datos"]]
    SALIDA.parent.mkdir(exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "nombre", "periodo", "valor", "fuente"])
        w.writerows(filas)
    print(f"Guardado: {SALIDA.relative_to(RAIZ)} ({len(filas)} filas, series {', '.join(SERIES)})")


if __name__ == "__main__":
    main()
