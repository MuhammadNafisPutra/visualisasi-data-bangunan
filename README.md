# Kondisi Fisik dan Status Hunian Bangunan di Kota Banjarmasin

Dashboard, insight, dan poster A3 dari survei lapangan bangunan di lima kecamatan Kota Banjarmasin.
Hasil dibaca sebagai indikasi awal, bukan bukti sebab-akibat.

![Poster A3](docs/preview_poster.jpg)

Penulis: Muhammad Nafis Putra (2410817210021), mata kuliah Visualisasi Data, 2026.

## Problem
Banjarmasin mencatat 135 kebakaran permukiman pada 2024, dan rumah berkonstruksi kayu di permukiman padat
membuat api cepat membesar (ANTARA, 2 Januari 2025). Belum ada gambaran per kecamatan tentang bangunan rusak
yang masih ditempati.

## Dataset
Data primer, pengamatan langsung, dicatat manual di Excel (`data/data_bangunan.xlsx`, sheet pertama).
Satu baris = satu bangunan. Variabel: Kecamatan, Jenis Bangunan, Bahan Dinding, Kondisi Fisik, Status Hunian,
Kondisi Lingkungan Sekitar. Data saat ini: 150 bangunan (sementara).

## Tools
Python (pandas, NumPy), Plotly, Streamlit, Shapely, Playwright.

## Menjalankan
```
pip install -r requirements.txt
streamlit run app.py                 # dashboard
playwright install chromium          # sekali saja, untuk poster
python buat_poster.py                # poster/poster.pdf, poster.png, poster.html
```

## Struktur
- `app.py` : tampilan dashboard (KPI, filter, insight, 7 grafik, rekomendasi), tema sasirangan.
- `insight.py` : perhitungan 5 insight (APA, MENGAPA, LALU APA, SEKARANG APA) dari data.
- `grafik.py` : 7 visualisasi, dipakai bersama oleh dashboard dan poster.
- `buat_poster.py` : poster A3 dari data dan insight yang sama.
- `data/kecamatan_perkiraan.geojson` : zona kecamatan PERKIRAAN (Voronoi), bukan batas resmi.
- `poster/` : poster A3 hasil jadi (`poster.pdf`, `poster.png`); `poster.html` dibuat ulang oleh `buat_poster.py`.
- `docs/` : gambar pratinjau poster untuk README.
- `assets/` : potongan motif sasirangan, font Bitter dan Source Sans 3 (lisensi SIL OFL).

## Key Insights (data sementara, n=150)
1. 25 dari 32 bangunan rusak yang masih dihuni berdinding kayu/papan; kayu/papan hanya 28% dari bangunan.
2. 21% bangunan rusak tetapi masih dihuni; tertinggi di Utara dan Barat, terendah di Tengah.
3. Lingkungan rusak di sekitar 67% bangunan rusak, tetapi hanya 10% bangunan baik.
4. Bangunan kosong tidak lebih rusak (28% vs 28%), tetapi rumah kosong lebih sering rusak daripada rumah dihuni.
5. Ruko kosong 4,7 kali lebih sering daripada rumah (53% vs 11%).

## Recommendation
Dahulukan pemeriksaan kelayakan dan sosialisasi pencegahan kebakaran pada bangunan kayu/papan rusak yang masih
dihuni, mulai dari Utara dan Barat; arahkan kerja bakti dan pemeriksaan jentik ke sekitar bangunan rusak.

## Catatan
Kelompok dengan n < 10 diberi tanda ⚠. Selisih di bawah 5 poin persen ditulis "hampir sama".
Sampel belum acak; survei tidak mencatat usia bangunan, pendapatan, atau lama bangunan kosong.

## Lisensi
Kode memakai lisensi MIT (lihat `LICENSE`). Font memakai SIL OFL. Data dipakai untuk keperluan akademik.
