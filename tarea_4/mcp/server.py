"""Servidor MCP del BCRP. Empiecen aquí: buscar_series ya funciona; completen los TODO hasta que pasen las pruebas.

    uv run pytest                                           # el contrato: las 8 pruebas deben pasar
    uv run server.py                                        # el servidor, por stdio
    claude mcp add --scope project bcrp -- uv run server.py # conectarlo a Claude Code

Las cuentas las hace Python, no el modelo: así cada cifra sale de una llamada que se puede repetir.
"""
import json
import re
import time
import unicodedata
from datetime import date
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
    "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero busca el código con buscar_series; "
    "luego usa resumen para variaciones, promedios y extremos, y serie para los datos. No calcules a mano: "
    "cita siempre el código de la serie y el periodo."))


def _sin_tildes(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


@cache
def catalogo():
    """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y queda en datos/."""
    if not CATALOGO.exists():
        CATALOGO.parent.mkdir(exist_ok=True)
        r = httpx.get(URL_CATALOGO, timeout=120)
        r.raise_for_status()
        CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
    df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
    df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie": "categoria", "Grupo de serie": "grupo",
                            "Nombre de serie": "nombre", "Frecuencia": "frecuencia",
                            "Fecha de actualización": "actualizada", "Fecha de inicio": "inicio"})
    df["texto"] = (df.categoria + " " + df.grupo + " " + df.nombre).map(_sin_tildes)
    return df


def _ficha(codigo):
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    f = fila.iloc[0]
    return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
            "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada": f.actualizada}


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10) -> list[dict]:
    """Busca series del BCRP por palabras: todas deben aparecer en la categoría, el grupo o el nombre.

    Ejemplos: "ipc 12 meses", "tipo de cambio interbancario venta", "reservas internacionales netas",
    "tasa de referencia", "cobre precio". frecuencia: "Diaria", "Mensual", "Trimestral" o "Anual".
    Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay datos. Si no hay resultados,
    prueben con menos palabras.
    """
    df = catalogo()
    m = pd.Series(True, index=df.index)
    for palabra in _sin_tildes(texto).split():
        m &= df.texto.str.contains(re.escape(palabra))
    if frecuencia:
        m &= df.frecuencia.str.lower() == frecuencia.lower()
    # primero las series vigentes y, entre ellas, las de nombre más corto (las más generales)
    sel = df[m]
    orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo + sel.nombre).str.len())
    return [_ficha(c) for c in orden.sort_values(["vieja", "largo"]).head(limite).codigo]


MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
         "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}   # setiembre: según la serie llega como Set o Sep
FORMATOS = {"Mensual", "Trimestral", "Diaria", "Anual"}
INTENTOS = 5


def _fecha_api(fecha, frecuencia):
    """Lleva "2025-01" (o "2025-1", "2025-01-15", "2025") al formato que pide la API según la frecuencia."""
    partes = str(fecha).strip().split("-")
    try:
        nums = [int(x) for x in partes]
    except ValueError:
        raise ToolError(f"Fecha inválida {fecha!r}: usen 2025-01 (mensual), 2025-01-15 (diaria) o 2025 (anual).")
    if frecuencia == "Anual":
        return str(nums[0])
    if frecuencia == "Diaria":
        if len(nums) != 3:
            raise ToolError(f"La serie es diaria: la fecha {fecha!r} debe ser AAAA-MM-DD.")
        return f"{nums[0]}-{nums[1]:02d}-{nums[2]:02d}"
    if len(nums) < 2:
        raise ToolError(f"La serie es {frecuencia.lower()}: la fecha {fecha!r} debe ser AAAA-M (por ejemplo 2025-1).")
    return f"{nums[0]}-{nums[1]}"      # mensual y trimestral: sin cero a la izquierda


def _anio(dos_digitos):
    """Año de 2 dígitos a 4: si supera al año actual en 2 dígitos es del siglo pasado (97 -> 1997, 26 -> 2026)."""
    return (1900 if dos_digitos > date.today().year % 100 else 2000) + dos_digitos


def _periodo(nombre, frecuencia):
    """Convierte el nombre que devuelve la API ("Ene.2025", "01.Oct.26", "T1.25", "2025") a un periodo ordenable."""
    try:
        if frecuencia == "Anual":
            return str(int(nombre))
        if frecuencia == "Mensual":
            mes, anio = nombre.split(".")
            return f"{int(anio)}-{MESES[mes]:02d}"
        if frecuencia == "Diaria":
            dia, mes, anio = nombre.split(".")
            return f"{_anio(int(anio))}-{MESES[mes]:02d}-{int(dia):02d}"
        if frecuencia == "Trimestral":
            trim, anio = nombre.split(".")
            return f"{_anio(int(anio))}-T{int(trim.lstrip('T'))}"
    except (ValueError, KeyError):
        pass
    raise ToolError(f"No pude interpretar el periodo {nombre!r} de una serie {frecuencia.lower()}.")


@cache
def _descargar(codigo, desde, hasta):
    """Pide la serie a la API. Si responde HTML (límite de pedidos) espera y reintenta. Los errores no se guardan en caché."""
    url = f"{API}/{codigo}/json/{desde}/{hasta}"
    ultimo = ""
    for intento in range(1, INTENTOS + 1):
        try:
            r = httpx.get(url, timeout=60)
            return url, r.json()
        except (httpx.HTTPError, ValueError) as e:      # ValueError: llegó HTML en vez de JSON
            ultimo = f"{type(e).__name__}: {e}"[:150]
            if intento < INTENTOS:
                time.sleep(2 * intento)
    raise ToolError(f"El BCRP no respondió con datos para {codigo} ({desde} a {hasta}) tras {INTENTOS} intentos. "
                    f"Esperen unos segundos y reintenten. Último error: {ultimo}")


def _serie(codigo, desde, hasta):
    """Lógica de serie(), separada para que resumen y otras herramientas la reutilicen."""
    f = _ficha(codigo)
    frec = f["frecuencia"]
    if frec not in FORMATOS:
        raise ToolError(f"La serie {codigo} tiene frecuencia {frec!r}, que serie() no sabe consultar.")
    url, js = _descargar(codigo, _fecha_api(desde, frec), _fecha_api(hasta, frec))
    datos = []
    for p in js.get("periods", []):
        v = p["values"][0] if p.get("values") else "n.d."
        if v in ("n.d.", "", None):
            continue
        datos.append({"periodo": _periodo(p["name"], frec), "valor": float(v)})
    if not datos:
        raise ToolError(f"La serie {codigo} no tiene datos entre {desde} y {hasta}. Prueben con otro rango.")
    return {"codigo": codigo, "nombre": f["nombre"], "frecuencia": frec, "datos": datos, "fuente": url}


@mcp.tool(annotations=SOLO_LECTURA)
def serie(codigo: str, desde: str, hasta: str) -> dict:
    """Descarga los datos de una serie del BCRP entre dos fechas, ambas incluidas.

    Úsala cuando ya tengas el código (búscalo antes con buscar_series). Fechas según la frecuencia de la serie:
    "2025-01" (mensual y trimestral), "2025-01-15" (diaria), "2025" (anual). Ejemplo: codigo="PN01271PM",
    desde="2025-01", hasta="2025-12". Devuelve los periodos como "2025-01", "2026-10-01", "2025-T1" o "2025",
    los valores numéricos (se omiten los n.d.) y la URL de la fuente. Si hay muchos datos y solo quieres variaciones,
    promedios o extremos, usa resumen en vez de calcular a mano.
    """
    return _serie(codigo, desde, hasta)


def _resumen(codigo, desde, hasta):
    """Lógica de resumen(), separada para que comparar_periodos la reutilice."""
    r = _serie(codigo, desde, hasta)
    d = r["datos"]
    primero, ultimo = d[0], d[-1]
    mx = max(d, key=lambda x: x["valor"])
    mn = min(d, key=lambda x: x["valor"])
    var = (ultimo["valor"] / primero["valor"] - 1) * 100 if primero["valor"] != 0 else None
    return {"codigo": codigo, "nombre": r["nombre"], "frecuencia": r["frecuencia"], "n_datos": len(d),
            "primero": primero, "ultimo": ultimo,
            "cambio": ultimo["valor"] - primero["valor"], "variacion_pct": var,
            "promedio": sum(x["valor"] for x in d) / len(d), "maximo": mx, "minimo": mn,
            "fuente": r["fuente"]}


@mcp.tool(annotations=SOLO_LECTURA)
def resumen(codigo: str, desde: str, hasta: str) -> dict:
    """Calcula con Python el resumen de una serie del BCRP entre dos fechas: primero, último, cambio, variación %,
    promedio, máximo y mínimo (estos con su periodo).

    Úsala siempre que pregunten por variaciones, promedios o extremos de una serie, en vez de calcular a mano con
    los datos de serie(). Mismas fechas que serie(): "2025-01" (mensual), "2025-01-15" (diaria), "2025" (anual).
    Ejemplo: codigo="PN01273PM", desde="2025-12", hasta="2026-09". Ojo: si la serie ya es una tasa (por ejemplo
    inflación a 12 meses), "cambio" son puntos porcentuales y "variacion_pct" es el cambio relativo de la tasa.
    """
    return _resumen(codigo, desde, hasta)


@mcp.tool(annotations=SOLO_LECTURA)
def comparar_periodos(codigo: str, desde_a: str, hasta_a: str, desde_b: str, hasta_b: str) -> dict:
    """Compara el comportamiento de una serie del BCRP en dos tramos: promedio, máximo y mínimo de cada uno
    (con su periodo) y la diferencia de promedios B − A.

    Úsala para preguntas del tipo "¿cómo estaba el indicador antes y después de X?": inflación antes y después de
    2022, tipo de cambio en dos gobiernos, reservas en dos crisis. Si solo importa un tramo, usa resumen.
    Ejemplo: codigo="PN01273PM" (inflación a 12 meses), desde_a="2018-01", hasta_a="2021-12",
    desde_b="2022-01", hasta_b="2025-12". Las fechas siguen el formato de serie() y los tramos no deben pedir
    meses sin datos. "diferencia_promedios" está en las unidades de la serie: si la serie es una tasa (%), son
    puntos porcentuales (pp), no un cambio relativo. Es una comparación descriptiva, no prueba causalidad.
    Devuelve la URL de la fuente de cada tramo.
    """
    a = _resumen(codigo, desde_a, hasta_a)
    b = _resumen(codigo, desde_b, hasta_b)
    tramo = lambda r, d, h: {"desde": d, "hasta": h, "n_datos": r["n_datos"], "promedio": r["promedio"],
                             "maximo": r["maximo"], "minimo": r["minimo"], "fuente": r["fuente"]}
    return {"codigo": codigo, "nombre": a["nombre"], "frecuencia": a["frecuencia"],
            "tramo_a": tramo(a, desde_a, hasta_a), "tramo_b": tramo(b, desde_b, hasta_b),
            "diferencia_promedios": b["promedio"] - a["promedio"],
            "fuentes": [a["fuente"], b["fuente"]]}


@mcp.resource("bcrp://serie/{codigo}", mime_type="application/json")
def ficha_serie(codigo: str) -> str:
    """Ficha descriptiva de una serie del BCRP: nombre, frecuencia, desde cuándo hay datos y última actualización.

    Ejemplo: bcrp://serie/PN01273PM. No descarga datos: para eso usen serie o resumen.
    """
    f = _ficha(codigo)
    ficha = {"codigo": f["codigo"], "nombre": f["nombre"], "frecuencia": f["frecuencia"],
             "datos_desde": f["inicio"], "ultima_actualizacion": f["actualizada"], "categoria": f["categoria"],
             "fuente": URL_CATALOGO}
    return json.dumps(ficha, ensure_ascii=False, indent=2)


@mcp.prompt
def informe(tema: str) -> str:
    """Pide un informe breve sobre un tema económico usando solo las herramientas del servidor BCRP."""
    pasos = [
        f"Redacta un informe breve sobre «{tema}» con datos oficiales del BCRP.",
        "1. Busca la serie con buscar_series (prueba con pocas palabras si no aparece) y confirma su ficha en bcrp://serie/{codigo}.",
        "2. Para variaciones, promedios, máximos y mínimos usa resumen; para comparar dos tramos (por ejemplo antes y después de una fecha) usa comparar_periodos. No calcules nada a mano.",
        "3. Cita en cada cifra el código de la serie, el periodo y la fuente (la URL que devuelve la herramienta).",
        "4. Si una serie es una tasa, expresa sus cambios en puntos porcentuales y no en %.",
        "5. Si una herramienta falla o no hay datos, dilo; no inventes cifras.",
        "6. Presenta los resultados como asociaciones descriptivas, no como causalidad demostrada.",
    ]
    return "\n".join(pasos)


if __name__ == "__main__":
    mcp.run()
