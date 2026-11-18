import re
"""Tujuh visualisasi (sesuai Tabel 6 laporan UTS), dipakai bersama oleh dashboard (app.py) dan poster (buat_poster.py).

Setiap fungsi menerima DataFrame dan mengembalikan plotly Figure.
Parameter `fs` = ukuran huruf dasar (dashboard 12, poster lebih besar).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from plotly.subplots import make_subplots
from shapely.geometry import shape

import insight as ins

BASE = Path(__file__).parent
DATA_FILE = BASE / "data" / "data_bangunan.xlsx"
GEO_FILE = BASE / "data" / "kecamatan_perkiraan.geojson"   # zona PERKIRAAN (Voronoi), bukan batas resmi

KEC, JENIS, BAHAN, FISIK, HUNI, LINGK = ins.KEC, ins.JENIS, ins.BAHAN, ins.FISIK, ins.HUNI, ins.LINGK
WAJIB = [KEC, JENIS, BAHAN, FISIK, HUNI, LINGK]
ORD_FISIK = ["Baik", "Sedang", "Rusak"]
ORD_HUNI = ["Berpenghuni", "Dipakai usaha", "Kosong"]
KAYU, BATA, MASIH_DIHUNI = ins.KAYU, ins.BATA, ins.MASIH_DIHUNI

# ---- warna data (arti tetap di semua output) ----
C_KONDISI = {"Baik": "#4C9F70", "Sedang": "#F2B84B", "Rusak": "#C8553D"}
C_HUNI = {"Berpenghuni": "#4C9F70", "Dipakai usaha": "#2F6690", "Kosong": "#8E6C8A"}
C_KAYU, C_BATA = "#9C6B3F", "#2F6690"
SKALA_PETA = [[0, "#F8E7E3"], [1, "#C8553D"]]
INK, GRID = "#2A1418", "#EEE5DC"
FONT = "'Source Sans 3', 'Source Sans Pro', Arial, sans-serif"   # dikutip: nama berakhiran angka tidak sah tanpa kutip

UKURAN_PETA = {
    "Rusak dan masih dihuni": "rd",
    "Rusak": "rusak",
    "Kosong": "kosong",
    "Dinding kayu/papan": "kayu",
    "Lingkungan rusak": "lingk",
}

short, pct, fmt = ins.short, ins.pct, ins.p0


# ======================= data =======================
def muat(sumber=DATA_FILE):
    """Baca sheet pertama; rapikan spasi; sel kosong menjadi NaN. Data mentah tidak diubah di disk."""
    d = pd.read_excel(sumber, sheet_name=0)
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]):
            d[c] = d[c].astype(str).str.strip().replace({"nan": np.nan, "": np.nan})
    return d


def muat_geo():
    with open(GEO_FILE, encoding="utf-8") as f:
        gj = json.load(f)
    pusat = {}
    for ft in gj["features"]:
        p = shape(ft["geometry"]).representative_point()
        pusat[ft["properties"]["Kecamatan"]] = (p.x, p.y)
    return gj, pusat


def kecamatan(d):
    return sorted(d[KEC].dropna().unique())


def kecil(n):
    return " ⚠" if n < ins.N_KECIL else ""


# ======================= helper =======================
def _sel_waffle(serie, urut):
    """100 kotak sesuai proporsi (metode sisa terbesar), 1 kotak = 1%."""
    s = serie.value_counts().reindex(urut).fillna(0)
    raw = s / s.sum() * 100
    n = np.floor(raw).astype(int)
    for k in (raw - n).sort_values(ascending=False).index[: 100 - int(n.sum())]:
        n[k] += 1
    kode = [i for i, k in enumerate(urut) for _ in range(int(n[k]))]
    return np.array(kode).reshape(10, 10)


def _waffle(panel, urut, warna, tinggi, fs):
    fig = make_subplots(rows=1, cols=len(panel), horizontal_spacing=0.03)
    k = len(urut)
    skala = []
    for i, nm in enumerate(urut):
        skala += [[i / k, warna[nm]], [(i + 1) / k, warna[nm]]]
    for i, (judul, serie) in enumerate(panel, 1):
        kode = _sel_waffle(serie, urut)
        fig.add_trace(go.Heatmap(z=kode, zmin=-0.5, zmax=k - 0.5, colorscale=skala, showscale=False, xgap=2, ygap=2,
                                 customdata=np.array(urut, dtype=object)[kode],
                                 hovertemplate="%{customdata}<extra></extra>"), row=1, col=i)
        ax = "x" if i == 1 else f"x{i}"
        fig.update_xaxes(visible=False, row=1, col=i)
        fig.update_yaxes(visible=False, autorange="reversed", scaleanchor=ax, constrain="domain", row=1, col=i)
        fig.add_annotation(text=judul, xref="x domain" if i == 1 else f"x{i} domain", yref="paper", x=0.5, y=1.02,
                           yanchor="bottom", showarrow=False, font=dict(size=fs - 1, color=INK))
    for nm in urut:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=nm,
                                 marker=dict(size=fs, symbol="square", color=warna[nm])), row=1, col=1)
    fig.update_layout(height=tinggi, margin=dict(l=5, r=5, t=int(fs * 4.4), b=5), font=dict(family=FONT, color=INK, size=fs),
                      legend=dict(orientation="h", y=-0.02, x=0.5, xanchor="center", yanchor="top"),
                      plot_bgcolor="white", paper_bgcolor="white")
    return fig


def tata(fig, tinggi, fs=12, legend_y=-0.2):
    fig.update_layout(height=tinggi, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family=FONT, color=INK, size=fs),
                      legend=dict(orientation="h", y=legend_y, x=0.5, xanchor="center"))
    return fig


# ======================= 1. waffle per kecamatan =======================
def g1_waffle_kecamatan(d, tinggi=250, fs=12):
    panel = []
    for k in kecamatan(d):
        dk = d[d[KEC] == k]
        panel.append((f"<b>{short(k)}</b> (n={len(dk)}){kecil(len(dk))}<br>{fmt(pct(dk[FISIK] == 'Rusak'))} rusak", dk[FISIK]))
    return _waffle(panel, ORD_FISIK, C_KONDISI, tinggi, fs)


# ======================= 2. grouped bar kosong & rusak =======================
def g2_bar_kecamatan(d, tinggi=300, fs=12):
    kecs = kecamatan(d)
    rk = d.groupby(KEC).agg(n=(FISIK, "size"), Kosong=(HUNI, lambda s: pct(s == "Kosong")),
                            Rusak=(FISIK, lambda s: pct(s == "Rusak"))).reindex(kecs)
    lab = [f"{short(k)}<br>(n={int(rk.loc[k, 'n'])})" for k in rk.index]
    fig = go.Figure()
    for nm, wr in (("Kosong", C_HUNI["Kosong"]), ("Rusak", C_KONDISI["Rusak"])):
        fig.add_bar(x=lab, y=rk[nm], name=f"% {nm.lower()}", marker_color=wr, text=[fmt(v) for v in rk[nm]],
                    textposition="outside", cliponaxis=False, textfont=dict(size=fs - 1),
                    hovertemplate="%{x}<br>" + nm + ": %{y:.1f}%<extra></extra>")
    fig.update_layout(barmode="group", bargap=0.25,
                      yaxis=dict(title="% bangunan di kecamatan", gridcolor=GRID,
                                 range=[0, max(10, float(rk[["Kosong", "Rusak"]].max().max()) * 1.22)]))
    return tata(fig, tinggi, fs)


# ======================= 3. peta =======================
def nilai_peta(d, kunci="rd"):
    """{kecamatan: (nilai %, n)} untuk ukuran yang dipilih."""
    hasil = {}
    for k in kecamatan(d):
        dk = d[d[KEC] == k]
        if kunci == "rd":
            v, n = pct((dk[FISIK] == "Rusak") & dk[HUNI].isin(MASIH_DIHUNI)), len(dk)
        elif kunci == "rusak":
            v, n = pct(dk[FISIK] == "Rusak"), len(dk)
        elif kunci == "kosong":
            v, n = pct(dk[HUNI] == "Kosong"), len(dk)
        elif kunci == "lingk":
            dl = dk[dk[LINGK].isin(["Baik", "Sedang", "Rusak"])]
            v, n = pct(dl[LINGK] == "Rusak"), len(dl)
        else:
            db = dk[dk[BAHAN].isin([KAYU, BATA])]
            v, n = pct(db[BAHAN] == KAYU), len(db)
        hasil[k] = (v, n)
    return hasil


def g3_peta(d, kunci="rd", label="Rusak dan masih dihuni", tinggi=430, fs=12, colorbar=True):
    gj, pusat = muat_geo()
    hit = nilai_peta(d, kunci)
    nilai = [v for v, _ in hit.values() if not pd.isna(v)]
    zmax = max(max(nilai), 1) if nilai else 1
    fig = go.Figure()
    terang = {}
    for ft in gj["features"]:
        k = ft["properties"]["Kecamatan"]
        ring = ft["geometry"]["coordinates"][0]
        v, n = hit.get(k, (np.nan, 0))
        warna = "#E6E9EC" if pd.isna(v) else sample_colorscale(SKALA_PETA, [min(v / zmax, 1)])[0]
        rgb = [float(x) for x in re.findall(r"[\d.]+", warna)[:3]] if warna.startswith("rgb") else [int(warna[i:i + 2], 16) for i in (1, 3, 5)]
        terang[k] = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255 > 0.6
        info = f"{k}<br>{label}: {fmt(v)}<br>n = {n}" if n else f"{k}<br>tidak ada data pada filter"
        fig.add_trace(go.Scatter(x=[p[0] for p in ring], y=[p[1] for p in ring], mode="lines", fill="toself",
                                 fillcolor=warna, line=dict(color="white", width=2.5), text=info, hoverinfo="text",
                                 hoveron="fills", showlegend=False))
    ks = [k for k in hit if k in pusat]
    for k in ks:
        v, n = hit[k]
        gelap = not terang.get(k, True)
        fig.add_annotation(x=pusat[k][0], y=pusat[k][1], showarrow=False,
                           text=f"<b>{short(k)}</b><br><span style='font-size:{fs + 6}px'><b>{fmt(v)}</b></span><br>n={n}{kecil(n)}",
                           font=dict(size=fs, color="white" if gelap else INK, family=FONT))
    if colorbar:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
                                 marker=dict(colorscale=SKALA_PETA, cmin=0, cmax=zmax, color=[0], showscale=True,
                                             colorbar=dict(title=dict(text="%", font=dict(size=fs)), thickness=12, len=0.7,
                                                           tickfont=dict(size=fs - 1)))))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", constrain="domain")
    fig.update_layout(height=tinggi, margin=dict(l=0, r=0, t=5, b=0), paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(family=FONT, size=fs))
    return fig


# ======================= 4. donat =======================
def g4_donat(d, tinggi=280, fs=12):
    fig = go.Figure()
    for i, h in enumerate(ORD_HUNI):
        dh = d[d[HUNI] == h]
        a, b = i / 3 + 0.01, (i + 1) / 3 - 0.01
        cnt = dh[FISIK].value_counts().reindex(ORD_FISIK).fillna(0)
        fig.add_trace(go.Pie(labels=ORD_FISIK, values=cnt, hole=0.66, sort=False, direction="clockwise",
                             domain=dict(x=[a, b], y=[0.0, 0.76]),
                             marker=dict(colors=[C_KONDISI[k] for k in ORD_FISIK], line=dict(color="white", width=2)),
                             textinfo="none", showlegend=(i == 0),
                             hovertemplate="%{label}: %{value} bangunan (%{percent})<extra></extra>"))
        fig.add_annotation(text=f"{h}<br>(n={len(dh)}){kecil(len(dh))}", x=(a + b) / 2, y=0.8, yanchor="bottom", xanchor="center",
                           xref="paper", yref="paper", showarrow=False, font=dict(size=fs - 1))
        fig.add_annotation(text=f"<b>{fmt(pct(dh[FISIK] == 'Rusak'))}</b>" if len(dh) else "-", x=(a + b) / 2, y=0.38, xanchor="center",
                           xref="paper", yref="paper", showarrow=False, font=dict(size=fs, color=C_KONDISI["Rusak"]))
    return tata(fig, tinggi, fs)


# ======================= 5. balon bahan dinding =======================
def g5_balon(d, tinggi=340, fs=12, maks=46, luar=False):
    kecs = kecamatan(d)
    fig = go.Figure()
    for nm, wr in ((KAYU, C_KAYU), (BATA, C_BATA)):
        ys, sz, tx, tc, tp = [], [], [], [], []
        for k in kecs:
            sub = d[(d[KEC] == k) & (d[BAHAN] == nm)]
            if sub.empty:
                continue
            p = pct(sub[FISIK] == "Rusak")
            besar = p >= 45 and not luar
            ys.append(short(k))
            sz.append(max(8, maks * np.sqrt(p / 100)))   # akar: LUAS lingkaran sebanding dengan %
            tx.append(f"{p:.0f}% · n={len(sub)}" if not besar else f"{p:.0f}%<br>n={len(sub)}")
            tc.append("white" if besar else INK)
            tp.append("middle center" if besar else "middle right")
        if ys:
            fig.add_trace(go.Scatter(y=ys, x=[nm] * len(ys), mode="markers+text", name=nm, text=tx, textposition=tp,
                                     textfont=dict(color=tc, size=fs - 2), cliponaxis=False,
                                     marker=dict(size=sz, color=wr, opacity=0.93, line=dict(color="white", width=1.5)),
                                     hovertemplate="%{y}<br>" + nm + "<br>%{text}<extra></extra>"))
    fig.update_xaxes(categoryorder="array", categoryarray=[KAYU, BATA], range=[-0.55, 1.95], gridcolor=GRID, side="top")
    fig.update_yaxes(categoryorder="array", categoryarray=[short(k) for k in kecs][::-1], gridcolor=GRID)
    fig.update_layout(showlegend=False)
    fig = tata(fig, tinggi, fs)
    fig.update_layout(margin=dict(t=int(fs * 2.6), l=10, r=10, b=10))
    return fig


# ======================= 6. waffle rumah vs ruko =======================
def g6_waffle_jenis(d, tinggi=320, fs=12):
    pj = []
    for j in ["Rumah", "Ruko"]:
        dj = d[d[JENIS] == j]
        if len(dj):
            pj.append((f"<b>{j}</b> (n={len(dj)}){kecil(len(dj))}<br>{fmt(pct(dj[HUNI] == 'Kosong'))} kosong", dj[HUNI]))
    return _waffle(pj, ORD_HUNI, C_HUNI, tinggi, fs) if pj else None


# ======================= 7. garis lingkungan vs kondisi fisik =======================
def g7_garis(d, tinggi=340, fs=12, ringkas=False):
    l = d.dropna(subset=[LINGK])
    ct = pd.crosstab(l[FISIK], l[LINGK]).reindex(index=ORD_FISIK, columns=ORD_FISIK).fillna(0)
    tot = ct.sum(axis=1)
    if tot.sum() == 0:
        return None
    pc = ct.div(tot.replace(0, np.nan), axis=0) * 100
    xl = [f"{f}<br>(n={int(tot[f])})" for f in ORD_FISIK]
    fig = go.Figure()
    for k in ORD_FISIK:
        fig.add_trace(go.Scatter(x=xl, y=pc[k], mode="lines+markers+text", name=f"Lingk. {k.lower()}",
                                 line=dict(color=C_KONDISI[k], width=3), marker=dict(size=9),
                                 text=[fmt(v) for v in pc[k]], textfont=dict(size=fs - 2),
                                 # label titik terendah di tiap kategori ditaruh di bawah agar tidak bertumpuk
                                 textposition=["bottom center" if pc.loc[f, k] == pc.loc[f].min() else "top center"
                                               for f in ORD_FISIK],
                                 hovertemplate="%{x}<br>Lingkungan " + k + ": %{y:.1f}%<extra></extra>"))
    fig.update_layout(yaxis=dict(title="% bangunan", range=[-5, 108], gridcolor=GRID),
                      xaxis=dict(gridcolor=GRID, title="Kondisi fisik bangunan", tickangle=0))
    fig = tata(fig, tinggi, fs)
    if ringkas:   # poster: legenda di atas, tanpa judul sumbu x
        fig.update_layout(legend=dict(y=1.02, yanchor="bottom", font=dict(size=fs - 1)), margin=dict(t=30, b=5),
                          xaxis_title=None, yaxis_title=None, yaxis_range=[-22, 112])
    else:
        fig.update_layout(legend=dict(y=-0.38))
    return fig


def sumber_teks(d):
    """'survei lapangan oleh penulis (150 bangunan) dan tim survei (866 bangunan)', dihitung dari kolom Sumber."""
    if "Sumber" not in d.columns:
        return "survei lapangan"
    n = d["Sumber"].value_counts()
    bagian = [f"{nm.lower()} ({int(n[nm])} bangunan)" for nm in ("Penulis", "Tim survei") if nm in n]
    return "survei lapangan oleh " + " dan ".join(bagian) if bagian else "survei lapangan"


def kpi(d):
    """Angka KPI yang sama untuk dashboard dan poster."""
    b = d[d[BAHAN].isin([KAYU, BATA])]
    rd = (d[FISIK] == "Rusak") & d[HUNI].isin(MASIH_DIHUNI)
    lg = d[d[LINGK].isin(["Baik", "Sedang", "Rusak"])]  # hanya lingkungan yang tercatat
    return dict(
        n=len(d),
        rusak=pct(d[FISIK] == "Rusak"), n_rusak=int((d[FISIK] == "Rusak").sum()),
        rd=pct(rd), n_rd=int(rd.sum()),
        kosong=pct(d[HUNI] == "Kosong"), n_kosong=int((d[HUNI] == "Kosong").sum()),
        kayu=pct(b[BAHAN] == KAYU), n_bahan=len(b),
        lingk=pct(lg[LINGK] == "Rusak"), n_lingk_rusak=int((lg[LINGK] == "Rusak").sum()), n_lingk=len(lg),
        n_kec=d[KEC].nunique(),
    )
