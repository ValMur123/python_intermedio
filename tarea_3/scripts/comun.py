"""Rutas y utilidades compartidas por los tres scripts."""
from pathlib import Path
import unicodedata

RAIZ = Path(__file__).resolve().parents[1]          # carpeta tarea_3/
ORIGINALES = RAIZ / "datos" / "originales"
PROCESADOS = RAIZ / "datos" / "procesados"
WEB_DATA = RAIZ / "web" / "data"

for carpeta in (ORIGINALES, PROCESADOS, WEB_DATA):
    carpeta.mkdir(parents=True, exist_ok=True)

# Dataset del curso en Hugging Face (el mismo de la sesión 07-raster)
HF_REPO = "aquiro1994/ds-python-up"
HF_ARCHIVOS = {
    "luces": "_data/VIIRS_NTL_Peru_YearlyComposite_2021.tif",
    "minas": "_data/Global_mining/global_miningarea_v1_30arcsecond.tif",
    "precip": "Labs/Python_Notebooks/LAB7/Prec_raster_peru.tif",
    "distritos": "_data/Folium/DISTRITOS",          # shapefile (sin extensión)
}

# PBI por departamentos, INEI vía BCRP (millones de S/ de 2007).
# Códigos RD17000DA ... RD17023DA, en orden alfabético de departamento.
DEPARTAMENTOS_BCRP = [
    "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO", "CAJAMARCA",
    "CUSCO", "HUANCAVELICA", "HUANUCO", "ICA", "JUNIN", "LA LIBERTAD",
    "LAMBAYEQUE", "LIMA", "LORETO", "MADRE DE DIOS", "MOQUEGUA", "PASCO",
    "PIURA", "PUNO", "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI",
]
CODIGOS_PBI = {f"RD170{i:02d}DA": d for i, d in enumerate(DEPARTAMENTOS_BCRP)}

ANIO = 2021   # año del raster de luces


def traer(ruta: str) -> str:
    """Descarga (o reutiliza del caché) un archivo del dataset del curso."""
    from huggingface_hub import hf_hub_download
    return hf_hub_download(HF_REPO, ruta, repo_type="dataset")


def traer_shapefile(base: str) -> str:
    principal = traer(f"{base}.shp")
    for ext in ("dbf", "shx", "prj", "cpg"):
        try:
            traer(f"{base}.{ext}")
        except Exception:
            pass
    return principal


def normalizar(texto: str) -> str:
    """'Áncash ' -> 'ANCASH' para poder unir tablas de fuentes distintas."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.upper().split())