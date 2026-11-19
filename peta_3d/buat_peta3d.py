"""Membuat peta 3D interaktif kondisi bangunan per kecamatan (satu file HTML).

Jalankan:  python buat_peta3d.py
Hasil   :  output/peta_3d_interaktif.html  (buka di browser, tidak butuh internet
           untuk kode petanya; peta dasar Esri butuh internet agar tampil)

Tinggi balok = persentase "rusak dan masih dihuni" per kecamatan (bisa diganti di peta).
"""
import base64
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).parent
DATA = BASE.parent / "data"                               # data yang sama dengan dashboard
DATA_FILE = DATA / "data_bangunan.xlsx"
GEO_RESMI = DATA / "kecamatan.geojson"                    # batas RESMI (properti "Kecamatan"), kalau kamu punya
GEO_PERKIRAAN = DATA / "kecamatan_perkiraan.geojson"      # zona perkiraan (dari buat_zona_perkiraan.py)
OUT = BASE / "output"; OUT.mkdir(exist_ok=True)
DATA_DUMMY = False   # ubah ke True kalau datanya hanya contoh

KEC, JENIS, BAHAN, FISIK, HUNI, LINGK = ("Kecamatan", "Jenis Bangunan", "Bahan Dinding",
                                         "Kondisi Fisik", "Status Hunian", "Kondisi Lingkungan Sekitar")
KAYU, BATA, KEL, SUMBER = "Kayu/papan", "Batu bata", "Kelurahan", "Sumber"
C_KEC = ["#2F6690", "#D1495B", "#EDAE49", "#00798C", "#8E6C8A"]

d = pd.read_excel(DATA_FILE, sheet_name=0)
for c in [c for c in d.columns if not pd.api.types.is_numeric_dtype(d[c])]:
    d[c] = d[c].astype(str).str.strip().replace({"nan": np.nan, "": np.nan})
print("membaca data:", DATA_FILE, d.shape)
KECS = sorted(d[KEC].unique())


def agregat():
    huni = d[HUNI].isin(["Berpenghuni", "Dipakai usaha"])
    d2 = d.assign(_rd=(d[FISIK] == "Rusak") & huni, _r=d[FISIK] == "Rusak", _k=d[HUNI] == "Kosong")
    pct = lambda m: float(m.mean() * 100) if len(m) else None
    # % kayu dihitung dari bangunan yang bahannya jelas (kayu/papan atau batu bata), sama seperti dashboard
    kayu = lambda g: pct(g.loc[g[BAHAN].isin([KAYU, BATA]), BAHAN] == KAYU)
    out = {}
    for i, kec in enumerate(KECS):
        g = d2[d2[KEC] == kec]
        kel = []
        if KEL in g.columns:   # kelurahan tidak tercatat untuk seluruh bangunan
            for nama, gk in g.dropna(subset=[KEL]).groupby(KEL):
                kel.append({"nama": nama, "n": int(len(gk)), "rusak": pct(gk._r), "rd": pct(gk._rd),
                            "kayu": kayu(gk), "ling_buruk": pct(gk[LINGK].dropna() == "Rusak")})
            kel.sort(key=lambda x: -x["n"])
        out[kec] = {"n": int(len(g)), "n_kel": int(g[KEL].notna().sum()) if KEL in g.columns else 0,
                    "color": C_KEC[i % len(C_KEC)],
                    "baik": pct(g[FISIK] == "Baik"), "sedang": pct(g[FISIK] == "Sedang"),
                    "rusak": pct(g._r), "kosong": pct(g._k), "rusak_dihuni": pct(g._rd),
                    "kayu": kayu(g),
                    "ling_buruk": pct(g[LINGK].dropna() == "Rusak"),
                    "ling_baik": pct(g[LINGK].dropna() == "Baik"), "kel": kel}
    return out


def muat_geo():
    if GEO_RESMI.exists():
        return json.load(open(GEO_RESMI)), "batas kecamatan RESMI (data/kecamatan.geojson)"
    if GEO_PERKIRAAN.exists():
        return json.load(open(GEO_PERKIRAAN)), "zona kecamatan PERKIRAAN, bukan batas resmi"
    raise FileNotFoundError("Tidak ada batas kecamatan. Jalankan: python buat_zona_perkiraan.py")


agg = agregat()
geo, ket_geo = muat_geo()
nama_ok = {f["properties"]["Kecamatan"] for f in geo["features"]}
if nama_ok != set(KECS):
    raise ValueError(f"Nama kecamatan di GeoJSON {sorted(nama_ok)} tidak sama dengan data {KECS}")

tpl = (BASE / "template_peta3d.html").read_text(encoding="utf-8")
banner = (("<b>DATA CONTOH (dummy)</b>, bukan hasil survei. " if DATA_DUMMY
           else f"Seluruh data dari survei lapangan (pengamatan langsung): {len(d):,} bangunan".replace(",", ".")
                + ". Bangunan tidak dipilih acak; hasil berupa indikasi awal. ")
          + f"Batas kecamatan: {ket_geo}. Batas kota dari GADM. Peta dasar: Esri.")
ASET = BASE / "assets"
b64 = lambda p: base64.b64encode((ASET / p).read_bytes()).decode()
FONTS = "\n".join(  # font disisipkan supaya HTML tetap rapi tanpa internet
    f"@font-face{{font-family:'{nama}';font-weight:{w};font-display:swap;"
    f"src:url(data:font/woff2;base64,{b64(f'fonts/{berkas}-latin-{w}-normal.woff2')}) format('woff2')}}"
    for nama, berkas in (("Bitter", "bitter"), ("Source Sans 3", "source-sans-3")) for w in (400, 600, 700))
tpl = (tpl.replace("__FONTS__", FONTS).replace("__MAROON__", b64("maroon.jpg"))
          .replace("__STRIP__", b64("strip.png")))
html = (tpl.replace("__MAPLIBRE_CSS__", (BASE / "lib/maplibre-gl.css").read_text(encoding="utf-8"))
           .replace("__MAPLIBRE_JS__", (BASE / "lib/maplibre-gl.js").read_text(encoding="utf-8").replace("</script", "<\\/script"))
           .replace("__BANNER__", banner)
           .replace("__DATA__", json.dumps(agg, ensure_ascii=False))
           .replace("__GEOJSON__", json.dumps(geo)))
(OUT / "peta_3d_interaktif.html").write_text(html, encoding="utf-8")
print("tersimpan:", OUT / "peta_3d_interaktif.html")
PAGES = BASE.parent / "docs" / "peta-3d"                 # disajikan GitHub Pages (folder docs/ di branch main)
PAGES.mkdir(parents=True, exist_ok=True)
(PAGES / "index.html").write_text(html, encoding="utf-8")
(BASE.parent / "docs" / ".nojekyll").touch()
print("tersimpan:", PAGES / "index.html")
