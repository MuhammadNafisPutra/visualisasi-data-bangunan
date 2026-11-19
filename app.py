"""Dashboard Kondisi Fisik dan Status Hunian Bangunan - Kota Banjarmasin (tema sasirangan).

Jalankan : streamlit run app.py
Data     : data/data_bangunan.xlsx (sheet pertama) atau unggah lewat sidebar.
Struktur : insight.py (perhitungan insight) · grafik.py (7 visualisasi) · app.py (tampilan).
"""
import base64
import html
from pathlib import Path

import pandas as pd
import streamlit as st

LABEL_SUMBER = "Survei lapangan"

import grafik as g
import insight as ins

BASE = Path(__file__).parent
PAPER, RULE = "#F5EEE4", "#DCCFC2"
CRIMSON, MAROON = "#A31239", "#6B0B26"
INK, MUTED = "#2A1418", "#76645F"
esc = html.escape

st.set_page_config(page_title="Dashboard Bangunan Banjarmasin", page_icon=str(Path(__file__).parent / "assets" / "logo.png"), layout="wide")

# ---- peta 3D interaktif: halaman terpisah di GitHub Pages (dibuat oleh peta_3d/buat_peta3d.py) ----
URL_PETA_3D = "https://muhammadnafisputra.github.io/visualisasi-data-bangunan/peta-3d/"


@st.cache_data
def b64(nama):
    return base64.b64encode((BASE / "assets" / nama).read_bytes()).decode()


BANNER, STRIP, MAROON_IMG = b64("banner.jpg"), b64("strip.png"), b64("maroon.jpg")
LOGO = b64("logo.png")

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bitter:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, p, li {{font-family:'Source Sans 3', sans-serif;}}
.stApp {{background:{PAPER};}}
.block-container {{padding-top:3rem; max-width:1320px;}}
h1,h2,h3,h4 {{font-family:Bitter, Georgia, serif !important; color:{INK}; letter-spacing:0;}}
h3 {{font-size:1.05rem !important; font-weight:600 !important; margin:0 0 .1rem 0 !important;}}
.hdr {{display:grid; grid-template-columns:1.3fr 1fr; min-height:190px; border-radius:2px; overflow:hidden;}}
.hdr .hl {{background:url(data:image/jpeg;base64,{MAROON_IMG}) center/cover; padding:1.5rem 1.8rem; color:white;}}
.hdr .hr {{background:url(data:image/jpeg;base64,{BANNER}) center/cover;}}
.hdr .brand {{display:flex; gap:1.1rem; align-items:center;}}
.hdr .brand img {{width:82px; height:82px; border-radius:12px; flex:none; box-shadow:0 0 0 2px rgba(255,255,255,.18);}}
.hdr .over {{font-size:.74rem; letter-spacing:.14em; text-transform:uppercase; color:#F2B7C3; font-weight:600; margin-bottom:.55rem;}}
.hdr h1 {{color:white !important; font-size:1.95rem; font-weight:700 !important; margin:0 0 .6rem 0; padding:0; line-height:1.2;}}
.hdr p {{color:#F4D9DF; margin:0; font-size:.95rem; max-width:520px;}}
.strip {{height:16px; background:url(data:image/png;base64,{STRIP}) repeat-x left center/auto 100%; margin:0 0 .3rem 0;}}
.kpis {{display:grid; grid-template-columns:repeat(6,1fr); border-top:2px solid {INK}; border-bottom:1px solid {RULE}; margin:1rem 0 .2rem 0;}}
.kpi {{padding:.8rem 1.1rem; border-right:1px solid {RULE};}}
.kpi:last-child {{border-right:0;}} .kpi:first-child {{padding-left:0;}}
.kpi .v {{font-family:Bitter,serif; font-size:2.3rem; font-weight:700; color:{INK}; line-height:1.1;}}
.kpi .l {{font-size:.9rem; color:{INK}; font-weight:600; margin-top:.15rem;}}
.kpi .l i {{display:inline-block; width:9px; height:9px; margin-right:7px; background:var(--c);}}
.kpi .s {{font-size:.78rem; color:{MUTED};}}
.sec {{display:flex; align-items:center; gap:.9rem; font-family:Bitter,serif; font-size:1.3rem; font-weight:600; color:{INK}; margin:1.5rem 0 .75rem 0;}}
.sec:after {{content:""; flex:1; height:1px; background:{RULE};}}
/* insight utama */
.main-ins {{display:grid; grid-template-columns:minmax(220px,1fr) 2.4fr; background:#FFFFFF; border:1px solid {RULE}; border-radius:2px; margin-bottom:.9rem;}}
.main-ins .l {{background:url(data:image/jpeg;base64,{MAROON_IMG}) center/cover; color:white; padding:1.1rem 1.3rem;}}
.main-ins .l .idx {{font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:#F2B7C3; font-weight:700;}}
.main-ins .l .big {{font-family:Bitter,serif; font-size:3rem; font-weight:700; line-height:1.05; margin:.35rem 0 .3rem;}}
.main-ins .l .jd {{font-size:1rem; font-weight:600; color:#FBE9ED;}}
.main-ins .r {{padding:.9rem 1.2rem; display:grid; grid-template-columns:1fr 1fr; gap:.2rem 1.4rem;}}
.row {{border-top:1px solid #F0E6DC; padding-top:.4rem; margin-top:.4rem; font-size:.86rem; line-height:1.42; color:{INK};}}
.row b {{display:block; color:{MUTED}; font-size:.66rem; letter-spacing:.1em; font-weight:700;}}
.warn {{font-size:.76rem; color:#8A4B12; background:#FCF1DE; padding:.25rem .5rem; margin-top:.5rem;}}
/* insight pendukung */
.ins-grid {{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:.9rem;}}
.ins {{background:#FFFFFF; border:1px solid {RULE}; border-radius:2px;}}
.ins .band {{height:12px; background:url(data:image/png;base64,{STRIP}) repeat-x left center/auto 100%;}}
.ins .body {{padding:.75rem 1rem 1rem;}}
.ins .idx {{font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:{CRIMSON}; font-weight:700;}}
.ins .big {{font-family:Bitter,serif; font-size:2.2rem; font-weight:700; color:{INK}; line-height:1.1; margin-top:.2rem;}}
.ins .jd {{font-weight:600; font-size:.92rem; margin:.1rem 0 .3rem 0;}}
.card-h {{font-size:.84rem; color:{MUTED}; margin:.15rem 0 .35rem 0;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{background:#FFFFFF; border-radius:2px; border-color:{RULE};}}
section[data-testid="stSidebar"] {{background:#EBDDD0;}}
.rek {{background:url(data:image/jpeg;base64,{MAROON_IMG}) center/cover; color:white; border-radius:2px; padding:1.3rem 1.6rem; margin-top:1.4rem;}}
.rek h4 {{color:white !important; font-size:1.25rem; margin:0 0 .6rem 0;}}
.rek ol {{list-style:none; counter-reset:n; margin:0; padding:0;}}
.rek li {{counter-increment:n; display:flex; align-items:baseline; gap:.9rem; padding:.45rem 0; border-top:1px solid rgba(255,255,255,.18); font-size:.95rem; color:#FBE9ED;}}
.rek li:before {{content:counter(n); font-family:Bitter,serif; font-size:1.35rem; color:#F2B7C3; min-width:1.2rem;}}
.rek li small {{color:#F2B7C3; font-size:.78rem; margin-left:.4rem; white-space:nowrap;}}
@media (max-width: 900px) {{ .kpis {{grid-template-columns:repeat(2,1fr);}} .hdr, .main-ins, .main-ins .r {{grid-template-columns:1fr;}} .hdr .hr {{min-height:80px;}} }}
</style>""", unsafe_allow_html=True)

# ======================= data =======================
muat = st.cache_data(g.muat)


@st.cache_data
def muat_file(path: str, versi: float):
    """Data bawaan; 'versi' = waktu ubah file, jadi cache otomatis diperbarui saat file data diganti."""
    return g.muat(path)

if hasattr(st, "logo"):
    st.logo(str(Path(__file__).parent / "assets" / "logo.png"), size="large")
st.sidebar.header("Filter")
unggah = st.sidebar.file_uploader("Ganti data (opsional, .xlsx)", type=["xlsx"])
if unggah is not None:
    df = muat(unggah)
elif g.DATA_FILE.exists():
    df = muat_file(str(g.DATA_FILE), g.DATA_FILE.stat().st_mtime)
else:
    st.error("Data tidak ditemukan. Taruh file di data/data_bangunan.xlsx atau unggah lewat sidebar.")
    st.stop()
hilang = [c for c in g.WAJIB if c not in df.columns]
if hilang:
    st.error(f"Kolom ini tidak ada di data: {hilang}")
    st.stop()

SEMUA_KEC = g.kecamatan(df)
f_kec = st.sidebar.multiselect("Kecamatan", SEMUA_KEC, default=SEMUA_KEC, format_func=g.short)
opsi = {c: sorted(df[c].dropna().unique()) for c in (g.JENIS, g.BAHAN)}
f_jenis = st.sidebar.multiselect("Jenis bangunan", opsi[g.JENIS], default=opsi[g.JENIS])
f_bahan = st.sidebar.multiselect("Bahan dinding", opsi[g.BAHAN], default=opsi[g.BAHAN])
f_huni = st.sidebar.multiselect("Status hunian", g.ORD_HUNI, default=g.ORD_HUNI)
st.sidebar.caption("Semua grafik dan kartu insight mengikuti filter. Baris yang kosong pada suatu kolom "
                   "tidak dihitung di grafik yang memakai kolom itu.")
d = df[df[g.KEC].isin(f_kec) & df[g.JENIS].isin(f_jenis) & df[g.BAHAN].isin(f_bahan) & df[g.HUNI].isin(f_huni)].copy()

# ======================= header =======================
st.markdown(f"""<div class="hdr"><div class="hl">
<div class="over">{LABEL_SUMBER} · {len(df)} bangunan · {len(SEMUA_KEC)} kecamatan</div>
<div class="brand"><img src="data:image/png;base64,{LOGO}" alt="Logo"><h1>Kondisi Fisik dan Status Hunian Bangunan di Kota Banjarmasin</h1></div>
<p style="margin-top:.6rem">Seluruh data berasal dari pengamatan langsung di lapangan. Hasil dibaca sebagai indikasi awal, bukan bukti sebab-akibat.</p>
</div><div class="hr"></div></div><div class="strip"></div>""", unsafe_allow_html=True)

if d.empty:
    st.warning("Tidak ada bangunan yang cocok dengan filter. Longgarkan filter di sidebar.")
    st.stop()

# ======================= KPI =======================
k = g.kpi(d)
kartu = [(f"{k['n']}", "Bangunan tercatat", f"dari {len(df)} pada data", CRIMSON),
         (g.fmt(k["rusak"]), "Rusak", f"{k['n_rusak']} bangunan", g.C_KONDISI["Rusak"]),
         (g.fmt(k["rd"]), "Rusak & masih dihuni", f"{k['n_rd']} bangunan", MAROON),
         (g.fmt(k["kosong"]), "Kosong", f"{k['n_kosong']} bangunan", g.C_HUNI["Kosong"]),
         (g.fmt(k["kayu"]), "Dinding kayu/papan",
          f"{round(k['kayu'] * k['n_bahan'] / 100)} dari {k['n_bahan']} bangunan" if k["n_bahan"] == k["n"]
          else f"dari {k['n_bahan']} yang bahannya pasti", g.C_KAYU),
         (g.fmt(k["lingk"]), "Lingkungan rusak",
          f"{k['n_lingk_rusak']} dari {k['n_lingk']} bangunan" if k["n_lingk"] == k["n"]
          else f"{k['n_lingk_rusak']} dari {k['n_lingk']} yang tercatat", "#5E7C3A")]
st.markdown('<div class="kpis">' + "".join(
    f'<div class="kpi"><div class="v">{v}</div><div class="l"><i style="--c:{c}"></i>{l}</div><div class="s">{s}</div></div>'
    for v, l, s, c in kartu) + "</div>", unsafe_allow_html=True)


# ======================= insight =======================
def baris(r):
    return "".join(f'<div class="row"><b>{lbl}</b>{esc(r[key])}</div>' for lbl, key in
                   (("APA", "apa"), ("MENGAPA (DUGAAN)", "mengapa"), ("LALU APA", "lalu_apa"), ("SEKARANG APA", "sekarang_apa")))


daftar = ins.hitung_semua(d)
st.markdown('<div class="sec">Temuan utama</div>', unsafe_allow_html=True)
if daftar:
    utama = [r for r in daftar if r.get("utama")]
    lain = [r for r in daftar if not r.get("utama")]
    no = 1
    for r in utama:
        warn = f'<div class="warn">⚠ {esc(r["peringatan"])}</div>' if r["peringatan"] else ""
        st.markdown(f'<div class="main-ins"><div class="l"><div class="idx">Insight {no} · {esc(r["jenis"])}</div>'
                    f'<div class="big">{esc(r["angka"])}</div><div class="jd">{esc(r["judul"])}</div></div>'
                    f'<div class="r">{baris(r)}{warn}</div></div>', unsafe_allow_html=True)
        no += 1
    kartu_lain = []
    for r in lain:
        warn = f'<div class="warn">⚠ {esc(r["peringatan"])}</div>' if r["peringatan"] else ""
        kartu_lain.append(f'<div class="ins"><div class="band"></div><div class="body">'
                          f'<div class="idx">Insight {no} · {esc(r["jenis"])}</div><div class="big">{esc(r["angka"])}</div>'
                          f'<div class="jd">{esc(r["judul"])}</div>{baris(r)}{warn}</div></div>')
        no += 1
    st.markdown('<div class="ins-grid">' + "".join(kartu_lain) + "</div>", unsafe_allow_html=True)
else:
    st.info("Data pada filter ini belum cukup untuk menghitung insight.")

st.markdown('<div class="sec">Grafik</div>', unsafe_allow_html=True)


def judul_grafik(no, teks, tanya):
    st.markdown(f"### {no}. {teks}")
    st.markdown(f'<div class="card-h">{tanya}</div>', unsafe_allow_html=True)


def tampil(fig, pesan="Tidak ada data pada filter ini."):
    if fig is None:
        st.info(pesan)
    else:
        st.plotly_chart(fig, width="stretch")


# baris 1
c1, c2 = st.columns(2, gap="medium")
with c1, st.container(border=True):
    judul_grafik(1, "Komposisi kondisi fisik per kecamatan",
                 "Bagaimana komposisi kondisi fisik bangunan di tiap kecamatan? Satu kotak = 1% bangunan.")
    tampil(g.g1_waffle_kecamatan(d))
with c2, st.container(border=True):
    judul_grafik(2, "Bangunan kosong dan rusak per kecamatan",
                 "Kecamatan mana yang memiliki persentase bangunan kosong dan rusak tertinggi?")
    tampil(g.g2_bar_kecamatan(d))

# baris 2
c3, c4 = st.columns([3, 2], gap="medium")
with c3, st.container(border=True):
    judul_grafik(3, "Peta sebaran per kecamatan",
                 "Bagaimana sebaran bangunan rusak yang masih dihuni antarkecamatan? "
                 "<b>Zona kecamatan adalah perkiraan (diagram Voronoi), bukan batas resmi.</b>")
    pilih = st.radio("Ukuran yang ditampilkan", list(g.UKURAN_PETA), horizontal=True, label_visibility="collapsed")
    if g.GEO_FILE.exists():
        tampil(g.g3_peta(d, g.UKURAN_PETA[pilih], pilih))
        if pilih == "Rusak dan masih dihuni":
            st.caption("Bangunan rusak yang masih dihuni (berpenghuni atau dipakai usaha) dibagi seluruh bangunan di kecamatan itu.")
        elif pilih == "Dinding kayu/papan":
            st.caption("Dihitung dari bangunan yang bahan dindingnya sudah pasti.")
        elif pilih == "Lingkungan rusak":
            st.caption("Dihitung dari bangunan yang kondisi lingkungannya tercatat. Lingkungan rusak = tumpukan sampah, semak lebat, genangan, atau wadah berair.")
    else:
        st.info("File zona kecamatan tidak ditemukan, jadi peta tidak ditampilkan.")
    st.markdown(
            f'<a href="{URL_PETA_3D}" target="_blank" rel="noopener" style="display:inline-block;margin-top:.3rem;padding:.4rem .9rem;'
            f'background:{MAROON};color:#fff;text-decoration:none;border-radius:2px;font-weight:600;font-size:.9rem">'
            'Buka peta 3D interaktif (rumah Banjar) &#8599;</a>'
            f'<div style="font-size:.78rem;color:{MUTED};margin-top:.25rem">Peta 3D memakai data lengkap, belum mengikuti filter di samping.</div>',
            unsafe_allow_html=True)
with c4, st.container(border=True):
    judul_grafik(4, "Kondisi fisik menurut status hunian",
                 "Apakah bangunan kosong lebih rusak daripada bangunan yang dihuni? Angka di tengah = % rusak.")
    tampil(g.g4_donat(d))
    st.markdown(
        "".join(f'<span style="display:inline-block;width:12px;height:12px;background:{c};margin:0 4px 0 0"></span>'
                f'<span style="font-size:.85rem;margin-right:12px">Kondisi {n}</span>' for n, c in g.C_KONDISI.items())
        + "<br>" +
        "".join(f'<span style="display:inline-block;width:12px;height:12px;background:{c};margin:0 4px 0 0"></span>'
                f'<span style="font-size:.85rem;margin-right:12px">{n}</span>' for n, c in g.C_HUNI.items()),
        unsafe_allow_html=True)
    st.caption("Hijau pada status hunian berarti Berpenghuni, bukan kondisi Baik.")

# baris 3
c5, c6, c7 = st.columns(3, gap="medium")
with c5, st.container(border=True):
    judul_grafik(5, "Rusak menurut bahan dinding",
                 "Apakah dinding kayu/papan lebih sering rusak? Luas lingkaran sebanding dengan % rusak.")
    tampil(g.g5_balon(d))
with c6, st.container(border=True):
    judul_grafik(6, "Status hunian: rumah dan ruko",
                 "Apakah ruko lebih sering kosong daripada rumah? Satu kotak = 1% bangunan.")
    tampil(g.g6_waffle_jenis(d))
with c7, st.container(border=True):
    judul_grafik(7, "Lingkungan sekitar menurut kondisi bangunan",
                 "Apakah lingkungan mengikuti kondisi bangunan? Garis menghubungkan tingkat kondisi, bukan waktu.")
    tampil(g.g7_garis(d))

# ======================= rekomendasi =======================
if daftar:
    st.markdown('<div class="rek"><h4>Rekomendasi</h4><ol>' + "".join(
        f'<li><span>{esc(r["sekarang_apa"])}</span><small>insight {i}</small></li>' for i, r in enumerate(
            [r for r in daftar if r.get("utama")] + [r for r in daftar if not r.get("utama")], 1))
        + "</ol></div>", unsafe_allow_html=True)
st.markdown('<div class="strip" style="margin-top:1.4rem"></div>', unsafe_allow_html=True)

with st.expander("Catatan data"):
    ex_b = int((~d[g.BAHAN].isin([g.KAYU, g.BATA])).sum())
    ex_l = int(d[g.LINGK].isna().sum())
    lengkap = ("- Data lengkap: seluruh bangunan memiliki isian bahan dinding, kondisi fisik, status hunian, "
               "dan kondisi lingkungan, sehingga semua bangunan dihitung pada setiap grafik dan insight.\n")
    if ex_b or ex_l:
        lengkap = ((f"- {ex_b} bangunan dengan bahan dinding belum dikonfirmasi tidak dihitung pada grafik 5, insight bahan dinding, dan KPI kayu/papan.\n" if ex_b else "")
                   + (f"- {ex_l} bangunan tanpa penilaian lingkungan tidak dihitung pada grafik 7 dan insight lingkungan.\n" if ex_l else ""))
    st.markdown(
        f"- Sumber: {g.sumber_teks(df)}, {len(df)} bangunan.\n"
        + lengkap +
        f"- Kelompok dengan n di bawah {ins.N_KECIL} diberi tanda ⚠. Selisih di bawah 5 poin persen ditulis \"hampir sama\".\n"
        "- Zona kecamatan pada peta adalah perkiraan (diagram Voronoi), bukan batas resmi.\n"
        "- Bagian MENGAPA berisi dugaan. Data tidak mencatat usia bangunan, pendapatan, atau lama bangunan kosong.")
with st.expander("Tabel data (hasil filter)"):
    st.dataframe(d.drop(columns=["Sumber"], errors="ignore"), width="stretch", hide_index=True)
