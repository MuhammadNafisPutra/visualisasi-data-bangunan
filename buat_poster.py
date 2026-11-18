"""Membuat poster A3 (data story) dari data dan insight yang sama dengan dashboard.

Jalankan : python buat_poster.py
Hasil    : poster/poster.html (bisa dibuka di browser), poster/poster.pdf (A3, untuk cetak), poster/poster.png
Butuh    : pip install playwright  lalu  playwright install chromium   (sekali saja)

Semua angka, grafik, dan kalimat insight dihitung ulang dari data/data_bangunan.xlsx,
jadi setelah data dibekukan cukup jalankan ulang skrip ini.
"""
import base64
import html
import sys
from pathlib import Path

import plotly.offline as po

import grafik as g
import insight as ins

BASE = Path(__file__).parent
OUT = BASE / "poster"
esc = html.escape
PAPER, RULE, CRIMSON, MAROON, INK, MUTED = "#F5EEE4", "#DCCFC2", "#A31239", "#6B0B26", "#2A1418", "#76645F"

# Sumber fakta di luar data survei (ditampilkan di poster). Jangan menambah klaim tanpa sumber.
MASALAH = ("Banjarmasin mencatat 135 titik kebakaran permukiman pada 2024. Menurut Kepala DPKP Kota Banjarmasin, "
           "permukiman padat dan rumah berkonstruksi kayu membuat api cepat membesar (ANTARA, 2 Januari 2025). "
           "Analisis ini memetakan bangunan rusak yang masih ditempati di lima kecamatan.")
LABEL_ATAS = "Survei lapangan"
IDENTITAS = "Muhammad Nafis Putra · 2410817210021 · Visualisasi Data 2026"


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def font_face():
    css = []
    for fam, file in (("Bitter", "bitter"), ("Source Sans 3", "source-sans-3")):
        for w in (400, 600, 700):
            f = BASE / "assets" / "fonts" / f"{file}-latin-{w}-normal.woff2"
            if f.exists():
                css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(f)}) format('woff2');}}")
    return "\n".join(css)


def plot(fig, w, h):
    """Figure plotly -> div statis berukuran tetap (px)."""
    if fig is None:
        return f'<div style="width:{w}px;height:{h}px"></div>'
    fig.update_layout(width=w, height=h, autosize=False)
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"staticPlot": True, "displayModeBar": False})


def susun(d):
    k = g.kpi(d)
    daftar = ins.hitung_semua(d)
    by = {r["grafik"]: r for r in daftar}
    utama = next((r for r in daftar if r.get("utama")), None)
    if utama is None or any(n not in by for n in (3, 4, 6, 7)):
        sys.exit("Insight belum lengkap pada data ini; poster tidak dibuat.")
    FS = 14  # huruf dasar grafik di poster

    def kartu(r, fig_html, judul_grafik):
        return (f'<div class="card"><div class="band"></div><div class="cb">'
                f'<div class="idx">{esc(r["jenis"])}</div><div class="num">{esc(r["angka"])}</div>'
                f'<div class="jd">{esc(r["judul"])}</div><div class="txt">{esc(r["pendek"])}</div>'
                f'<div class="gt">{judul_grafik}</div>{fig_html}</div></div>')

    rek = [r["sekarang_apa"] for r in [utama] + [by[3], by[7], by[4]]]
    # detail insight utama untuk poster: kalimat pembanding saja (tanpa mengulang angka besar)
    detail_utama = "Padahal " + utama["apa"].split(", padahal ", 1)[-1].split(" Pola")[0]
    bar = g.g2_bar_kecamatan(d, fs=FS - 1)
    bar.update_layout(yaxis_title=None, legend=dict(y=1.04, yanchor="bottom", x=1, xanchor="right"), margin=dict(t=28, b=5))
    hook = utama["pendek"].split(", padahal")[0]

    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<title>Poster A3 - Bangunan Banjarmasin</title>
<script>{po.get_plotlyjs()}</script>
<style>
{font_face()}
@page {{ size: 297mm 420mm; margin: 0; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; background:#ddd; }}
body {{ font-family:'Source Sans 3', Arial, sans-serif; color:{INK}; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.page {{ width:1123px; height:1587px; background:{PAPER}; padding:34px 38px 26px; margin:0 auto; overflow:hidden; display:flex; flex-direction:column; gap:8px; }}
.serif {{ font-family:Bitter, Georgia, serif; }}
.hdr {{ display:grid; grid-template-columns:1.55fr 1fr; height:190px; position:relative; }}
.hdr:after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:13px; background:url(data:image/png;base64,{b64(BASE / 'assets' / 'strip.png')}) repeat-x left center/auto 100%; }}
.hl {{ background:url(data:image/jpeg;base64,{b64(BASE / 'assets' / 'maroon.jpg')}) center/cover; color:white; padding:18px 26px 26px; display:flex; flex-direction:column; justify-content:center; }}
.hr {{ background:url(data:image/jpeg;base64,{b64(BASE / 'assets' / 'banner.jpg')}) center/cover; }}
.over {{ font-size:13px; letter-spacing:.16em; text-transform:uppercase; color:#F2B7C3; font-weight:700; }}
.hook {{ font-family:Bitter, Georgia, serif; font-weight:700; font-size:31px; line-height:1.14; margin:7px 0 8px; }}
.sub {{ font-size:17px; color:#F6DCE2; font-weight:600; }}
.strip {{ height:13px; margin-top:-10px; background:url(data:image/png;base64,{b64(BASE / 'assets' / 'strip.png')}) repeat-x left center/auto 100%; }}
.band2 {{ display:grid; grid-template-columns:1.05fr 1fr; gap:22px; align-items:center; border-bottom:1px solid {RULE}; padding-bottom:10px; }}
.lab {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; font-weight:700; color:{CRIMSON}; }}
.masalah p {{ margin:4px 0 0; font-size:15.5px; line-height:1.4; }}
.kpis {{ display:grid; grid-template-columns:repeat(4,1fr); border-top:2px solid {INK}; }}
.kpi {{ padding:7px 10px 2px; border-right:1px solid {RULE}; }} .kpi:last-child {{ border-right:0; }}
.kpi .v {{ font-family:Bitter, Georgia, serif; font-weight:700; font-size:34px; line-height:1.05; }}
.kpi .l {{ font-size:13.5px; font-weight:600; }} .kpi .l i {{ display:inline-block; width:9px; height:9px; margin-right:6px; }}
.main {{ display:grid; grid-template-columns:600px 1fr; gap:14px; height:442px; }}
.panel {{ background:white; border:1px solid {RULE}; padding:10px 12px; }}
.ptitle {{ font-family:Bitter, Georgia, serif; font-weight:700; font-size:20px; }}
.pnote {{ font-size:13.5px; color:{MUTED}; margin:2px 0 4px; line-height:1.35; }}
.uta {{ background:url(data:image/jpeg;base64,{b64(BASE / 'assets' / 'maroon.jpg')}) center/cover; color:white; padding:14px 18px 10px; display:flex; flex-direction:column; }}
.uta .lab {{ color:#F2B7C3; }}
.uta .num {{ font-family:Bitter, Georgia, serif; font-weight:700; font-size:66px; line-height:1; margin:6px 0 4px; }}
.uta .jd {{ font-size:19px; font-weight:700; line-height:1.25; }}
.uta .txt {{ font-size:15px; line-height:1.38; color:#FBE9ED; margin:6px 0 8px; }}
.uta .fig {{ background:white; padding:4px 4px 0; margin-top:auto; }}
.uta .gt {{ color:{INK}; font-size:13px; font-weight:700; padding:2px 6px; }}
.row2 {{ display:grid; grid-template-columns:560px 1fr; gap:14px; height:222px; }}
.row3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; height:340px; }}
.card {{ background:white; border:1px solid {RULE}; display:flex; flex-direction:column; }}
.card .band {{ height:11px; background:url(data:image/png;base64,{b64(BASE / 'assets' / 'strip.png')}) repeat-x left center/auto 100%; }}
.cb {{ padding:8px 12px 4px; display:flex; flex-direction:column; flex:1; }}
.idx {{ font-size:11.5px; letter-spacing:.13em; text-transform:uppercase; font-weight:700; color:{CRIMSON}; }}
.num {{ font-family:Bitter, Georgia, serif; font-weight:700; font-size:36px; line-height:1.05; margin-top:2px; }}
.jd {{ font-size:15.5px; font-weight:700; line-height:1.25; }}
.txt {{ font-size:14.5px; line-height:1.35; margin-top:3px; }}
.gt {{ font-size:12.5px; color:{MUTED}; font-weight:600; margin-top:auto; padding-top:4px; }}
.rek {{ background:url(data:image/jpeg;base64,{b64(BASE / 'assets' / 'maroon.jpg')}) center/cover; color:white; padding:12px 20px; display:grid; grid-template-columns:160px 1fr; gap:14px; align-items:center; }}
.rek .h {{ font-family:Bitter, Georgia, serif; font-weight:700; font-size:24px; line-height:1.1; }}
.rek ol {{ list-style:none; counter-reset:n; margin:0; padding:0; display:grid; grid-template-columns:1fr 1fr; gap:6px 22px; }}
.rek li {{ counter-increment:n; display:flex; gap:10px; font-size:14.5px; line-height:1.32; color:#FBE9ED; }}
.rek li:before {{ content:counter(n); font-family:Bitter, Georgia, serif; font-weight:700; font-size:22px; color:#F2B7C3; line-height:1; }}
.foot {{ display:flex; justify-content:space-between; gap:20px; font-size:12px; color:{MUTED}; line-height:1.35; border-top:1px solid {RULE}; padding-top:6px; }}
.leg {{ display:flex; gap:14px; flex-wrap:wrap; font-size:12.5px; margin-top:2px; }}
.leg span:before {{ content:""; display:inline-block; width:10px; height:10px; margin-right:5px; background:var(--c); }}
@media print {{ html, body {{ background:none; }} .page {{ margin:0; }} }}
</style></head><body><div class="page">

<div class="hdr"><div class="hl">
  <div class="over">{LABEL_ATAS} · {k['n']} bangunan · {k['n_kec']} kecamatan</div>
  <div class="hook">{esc(hook)}.</div>
  <div class="sub">Kondisi Fisik dan Status Hunian Bangunan di Kota Banjarmasin</div>
</div><div class="hr"></div></div>

<div class="band2">
  <div class="masalah"><div class="lab">Masalah</div><p>{esc(MASALAH)}</p></div>
  <div class="kpis">
    <div class="kpi"><div class="v">{k['n']}</div><div class="l"><i style="background:{CRIMSON}"></i>bangunan</div></div>
    <div class="kpi"><div class="v">{g.fmt(k['rusak'])}</div><div class="l"><i style="background:{g.C_KONDISI['Rusak']}"></i>rusak</div></div>
    <div class="kpi"><div class="v">{g.fmt(k['rd'])}</div><div class="l"><i style="background:{MAROON}"></i>rusak & dihuni</div></div>
    <div class="kpi"><div class="v">{g.fmt(k['kayu'])}</div><div class="l"><i style="background:{g.C_KAYU}"></i>dinding kayu</div></div>
  </div>
</div>

<div class="main">
  <div class="panel">
    <div class="ptitle">Di mana bangunan rusak masih ditempati?</div>
    <div class="pnote">{esc(by[3]['pendek'])} Zona kecamatan perkiraan, bukan batas resmi.</div>
    {plot(g.g3_peta(d, 'rd', 'Rusak dan masih dihuni', fs=FS + 1, colorbar=False), 574, 338)}
  </div>
  <div class="uta">
    <div class="lab">Insight utama</div>
    <div class="num">{esc(utama['angka'])}</div>
    <div class="jd">{esc(utama['judul'])}</div>
    <div class="txt">{esc(detail_utama)}</div>
    <div class="fig"><div class="gt">% rusak menurut bahan dinding (luas lingkaran = % rusak)</div>
      {plot(g.g5_balon(d, fs=FS, maks=30, luar=True), 392, 182)}</div>
  </div>
</div>

<div class="row2">
  <div class="panel"><div class="ptitle" style="font-size:17px">Komposisi kondisi fisik per kecamatan</div>
    {plot(g.g1_waffle_kecamatan(d, fs=FS - 1), 534, 178)}</div>
  <div class="panel"><div class="ptitle" style="font-size:17px">Bangunan kosong dan rusak per kecamatan</div>
    {plot(bar, 440, 178)}</div>
</div>

<div class="row3">
  {kartu(by[7], plot(g.g7_garis(d, fs=FS - 2, ringkas=True), 316, 160), "Lingkungan sekitar menurut kondisi bangunan")}
  {kartu(by[4], plot(g.g4_donat(d, fs=FS - 2), 316, 160), "Kondisi fisik menurut status hunian (angka tengah = % rusak)")}
  {kartu(by[6], plot(g.g6_waffle_jenis(d, fs=FS - 2), 316, 160), "Status hunian: rumah dan ruko (1 kotak = 1%)")}
</div>

<div class="rek"><div class="h">Dampak &amp;<br>Rekomendasi</div><ol>
  {''.join(f'<li><span>{esc(t)}</span></li>' for t in rek)}
</ol></div>

<div class="foot">
  <div>Sumber: {g.sumber_teks(d)}, n = {k['n']} bangunan. Indikasi awal, bukan bukti sebab-akibat.
    Persen peta = bangunan rusak yang masih dihuni ÷ semua bangunan di kecamatan. ⚠ = n &lt; {ins.N_KECIL}.</div>
  <div style="text-align:right;white-space:nowrap">{esc(IDENTITAS)}</div>
</div>
</div></body></html>"""


def main():
    OUT.mkdir(exist_ok=True)
    d = g.muat()
    html_file = OUT / "poster.html"
    html_file.write_text(susun(d), encoding="utf-8")
    print("HTML :", html_file)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright belum terpasang; hanya poster.html yang dibuat.")
        return
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:   # Chromium Playwright belum dipasang: pakai Edge/Chrome yang sudah ada di komputer
            try:
                b = p.chromium.launch(channel="msedge")
            except Exception:
                b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1123, "height": 1587}, device_scale_factor=3)
        pg.goto(html_file.resolve().as_uri())
        pg.wait_for_timeout(1500)
        luber = pg.evaluate("(() => {const e=document.querySelector('.page'); return e.scrollHeight - e.clientHeight;})()")
        if luber > 0:
            print(f"PERINGATAN: isi poster melebihi A3 sebanyak {luber}px")
        pg.pdf(path=str(OUT / "poster.pdf"), width="297mm", height="420mm", print_background=True,
               margin=dict(top="0", right="0", bottom="0", left="0"))
        pg.locator(".page").screenshot(path=str(OUT / "poster.png"))
        b.close()
    print("PDF  :", OUT / "poster.pdf")
    print("PNG  :", OUT / "poster.png")


if __name__ == "__main__":
    main()
