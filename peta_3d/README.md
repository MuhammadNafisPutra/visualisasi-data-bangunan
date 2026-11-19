# Peta 3D Kondisi Bangunan Banjarmasin

Hanya bagian peta 3D dari proyek visualisasi data.

## Cara membuat
```
pip install -r requirements.txt
python buat_peta3d.py
```
Hasil: `output/peta_3d_interaktif.html`. Buka dengan browser (klik dua kali). Di dashboard, peta ini tampil lewat tautan di bawah grafik peta (`?view=peta3d`).

## Isi folder
- `buat_peta3d.py` : skrip pembuat peta (membaca data, menghitung persentase per kecamatan, membuat HTML).
- `template_peta3d.html` : kerangka peta 3D (MapLibre GL).
  Tiap kecamatan digambar sebagai 10 rumah Banjar (rumah panggung beratap bubungan tinggi) dari potongan `fill-extrusion`;
  1 rumah berwarna = 10% bangunan (dibulatkan), angka persis tertulis di label.
- `assets/` : motif sasirangan dan font Bitter serta Source Sans 3 (lisensi SIL OFL), sama dengan dashboard; disisipkan ke HTML.
- `lib/` : pustaka MapLibre GL (lisensi BSD, ada di `LICENSE-maplibre.txt`), supaya file HTML berdiri sendiri.
- Data dibaca dari folder `../data/` (sama dengan dashboard): `data_bangunan.xlsx` dan `kecamatan_perkiraan.geojson` (zona PERKIRAAN, bukan batas resmi).
- `data/batas_kota_banjarmasin_gadm.geojson` dan `buat_zona_perkiraan.py` : asal zona perkiraan (diagram Voronoi dari batas kota GADM v4.0).

## Catatan
- Peta dasar (Esri) butuh internet. Tanpa internet, rumah 3D tetap tampil tetapi latarnya kosong.
- Mengganti data: timpa `../data/data_bangunan.xlsx` (nama kolom harus sama), jalankan ulang.
- Batas resmi: simpan sebagai `../data/kecamatan.geojson` (properti `Kecamatan`), skrip memakainya lebih dulu.
- Hasil berupa indikasi awal, bukan sebab-akibat. Kelompok dengan n kecil perlu dibaca hati-hati.
