"""Membuat data/kecamatan_perkiraan.geojson: zona kecamatan PERKIRAAN (bukan batas resmi).
Cara: poligon resmi kota (GADM, data/batas_kota_banjarmasin_gadm.geojson) dibagi 5 dengan diagram
Voronoi dari 5 titik pusat perkiraan kecamatan. Perlu: pip install shapely
UNTUK LAPORAN ASLI, ganti dengan batas kecamatan resmi (lihat README): simpan sebagai
data/kecamatan.geojson dengan properti "Kecamatan" berisi nama persis seperti di data survei."""
import json
from shapely.geometry import shape, mapping, MultiPoint, Point
from shapely.ops import voronoi_diagram

PUSAT = {  # (lon, lat) PERKIRAAN KASAR, bukan koordinat resmi
    "Banjarmasin Utara": (114.595, -3.290), "Banjarmasin Selatan": (114.600, -3.345),
    "Banjarmasin Barat": (114.565, -3.325), "Banjarmasin Timur": (114.630, -3.315),
    "Banjarmasin Tengah": (114.595, -3.318),
}
kota = shape(json.load(open("data/batas_kota_banjarmasin_gadm.geojson"))["features"][0]["geometry"])
sel = voronoi_diagram(MultiPoint([Point(p) for p in PUSAT.values()]), envelope=kota.envelope.buffer(0.1))
fitur = []
for nama, p in PUSAT.items():
    sel_i = next(g for g in sel.geoms if g.contains(Point(p)))
    bagian = kota.intersection(sel_i)
    fitur.append({"type": "Feature", "properties": {"Kecamatan": nama, "catatan": "zona perkiraan, bukan batas resmi"},
                  "geometry": mapping(bagian)})
json.dump({"type": "FeatureCollection", "features": fitur}, open("../data/kecamatan_perkiraan.geojson", "w"))
print("Selesai: ../data/kecamatan_perkiraan.geojson")
