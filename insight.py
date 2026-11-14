"""Perhitungan insight untuk dashboard, poster, dan laporan.

Setiap fungsi menerima DataFrame (sudah difilter bila dipakai di dashboard) dan mengembalikan dict:
  jenis, angka, judul, apa, mengapa, lalu_apa, sekarang_apa, peringatan,
  pendek (1 kalimat untuk poster), grafik (nomor visualisasi pendukung), utama (True untuk insight utama).
Kalimat disusun dari angka hasil hitung, jadi ikut berubah bila data atau filter berubah.
Bila data tidak cukup, fungsi mengembalikan None.

Catatan perubahan (v3):
- Insight "rusak masih dihuni" tidak lagi memakai porsi dari bangunan rusak (76%), karena angka itu
  hanya mencerminkan bahwa sebagian besar bangunan memang dihuni. Sekarang memakai persentase dari
  SEMUA bangunan (rusak sekaligus masih dihuni) dan perbandingan antarkecamatan.
- Insight bahan dinding menjadi insight utama: porsi kayu/papan di antara bangunan rusak yang masih dihuni.
"""
import numpy as np
import pandas as pd

KEC, JENIS, BAHAN, FISIK, HUNI, LINGK = ("Kecamatan", "Jenis Bangunan", "Bahan Dinding",
                                         "Kondisi Fisik", "Status Hunian", "Kondisi Lingkungan Sekitar")
KAYU, BATA = "Kayu/papan", "Batu bata"
MASIH_DIHUNI = ["Berpenghuni", "Dipakai usaha"]

N_KECIL = 10       # kelompok dengan n di bawah ini diberi peringatan
BEDA_TIPIS = 5.0   # selisih (poin persen) yang dianggap "hampir sama"


# ---------------- pembantu format (gaya Indonesia: koma desimal) ----------------
def pct(mask):
    """Persentase nilai True. Penyebutnya = panjang mask (kelompok yang sedang dihitung)."""
    return float(mask.mean() * 100) if len(mask) else np.nan


def p0(v):
    return "-" if pd.isna(v) else f"{v:.0f}%"


def x1(v):
    return f"{v:.1f}".replace(".", ",")


def short(k):
    return k.replace("Banjarmasin ", "")


def _peringatan(*pasangan):
    kecil = [f"{nm} (n={n})" for nm, n in pasangan if n < N_KECIL]
    return "n kecil: " + ", ".join(kecil) + ". Baca hati-hati." if kecil else ""


def _kalimat_rasio(a, b):
    """'hampir 4 dari 5' dsb. untuk proporsi a/b."""
    if not b:
        return ""
    p = a / b
    for num, den in ((1, 2), (2, 3), (3, 4), (4, 5), (9, 10)):
        if abs(p - num / den) <= 0.03:
            return f"{'sekitar ' if abs(p - num / den) > 0.005 else ''}{num} dari {den}"
    return f"{p * 100:.0f}%"


# ---------------- Insight UTAMA: kayu di antara bangunan rusak yang masih dihuni ----------------
def insight_kayu(d):
    b = d[d[BAHAN].isin([KAYU, BATA])]
    dk, db = b[b[BAHAN] == KAYU], b[b[BAHAN] == BATA]
    if dk.empty or db.empty:
        return None
    rd = b[(b[FISIK] == "Rusak") & b[HUNI].isin(MASIH_DIHUNI)]
    if rd.empty:
        return None
    k_rd, n_rd = int((rd[BAHAN] == KAYU).sum()), len(rd)
    porsi_rd = k_rd / n_rd * 100
    porsi_kayu = pct(b[BAHAN] == KAYU)
    pk, pb = pct(dk[FISIK] == "Rusak"), pct(db[FISIK] == "Rusak")

    # konsistensi antarkecamatan (hanya kecamatan yang punya kedua bahan)
    sama = total = 0
    for _, g in b.groupby(KEC):
        gk, gb = g[g[BAHAN] == KAYU], g[g[BAHAN] == BATA]
        if len(gk) and len(gb):
            total += 1
            sama += pct(gk[FISIK] == "Rusak") > pct(gb[FISIK] == "Rusak")
    konsisten = f" Pola kayu lebih sering rusak muncul di {sama} dari {total} kecamatan." if total >= 2 else ""
    rasio = f" ({x1(pk / pb)} kali lipat)" if pb > 0 else ""
    terlalu_sedikit = len(d) - len(b)   # bangunan dengan bahan belum dikonfirmasi

    return dict(
        utama=True, grafik=5,
        jenis="Insight utama · Kontribusi",
        angka=f"{k_rd} dari {n_rd}",
        judul="bangunan rusak yang masih dihuni berdinding kayu/papan",
        pendek=(f"{_kalimat_rasio(k_rd, n_rd).capitalize()} bangunan rusak yang masih dihuni berdinding kayu/papan, "
                f"padahal kayu/papan hanya {p0(porsi_kayu)} dari bangunan."),
        apa=(f"{k_rd} dari {n_rd} bangunan rusak yang masih ditempati ({p0(porsi_rd)}) berdinding kayu/papan, "
             f"padahal kayu/papan hanya {p0(porsi_kayu)} dari seluruh bangunan. "
             f"Bangunan kayu/papan yang rusak {p0(pk)} (n={len(dk)}), batu bata {p0(pb)} (n={len(db)}){rasio}.{konsisten}"),
        mengapa=("Dugaan: bangunan kayu cenderung lebih tua dan lebih cepat lapuk di lingkungan lembap. "
                 "Usia bangunan tidak dicatat, jadi pengaruh bahan dan usia belum bisa dipisahkan."),
        lalu_apa=("Orang masih tinggal atau bekerja di bangunan rusak yang mudah terbakar. Kepala DPKP Banjarmasin menyebut "
                  "permukiman padat dan rumah kayu membuat api cepat membesar (ANTARA, 2 Jan 2025)."),
        sekarang_apa="Dahulukan pemeriksaan kelayakan dan sosialisasi pencegahan kebakaran pada bangunan kayu/papan rusak yang masih dihuni.",
        peringatan=_peringatan((KAYU, len(dk)), (BATA, len(db)), ("Rusak & dihuni", n_rd))
                   + (f" {terlalu_sedikit} bangunan dengan bahan belum dikonfirmasi tidak dihitung." if terlalu_sedikit else ""),
    )


# ---------------- Insight 2: sebaran rusak & masih dihuni antarkecamatan ----------------
def insight_rusak_dihuni(d):
    if d.empty:
        return None
    rusak, dihuni = d[FISIK] == "Rusak", d[HUNI].isin(MASIH_DIHUNI)
    n_rd = int((rusak & dihuni).sum())
    per = (d.assign(_rd=rusak & dihuni).groupby(KEC).agg(n=("_rd", "size"), rd=("_rd", "mean")))
    per["rd"] *= 100
    per = per.sort_values("rd", ascending=False)

    if len(per) >= 2:
        a, b, z = per.index[0], per.index[1], per.index[-1]
        selisih = per.loc[a, "rd"] - per.loc[b, "rd"]
        if selisih < BEDA_TIPIS:
            banding = (f"Tertinggi di {short(a)} ({p0(per.loc[a, 'rd'])}) dan {short(b)} ({p0(per.loc[b, 'rd'])}), "
                       f"selisihnya hanya {x1(selisih)} poin.")
            target = f"{short(a)} dan {short(b)}"
        else:
            banding = f"Tertinggi di {short(a)} ({p0(per.loc[a, 'rd'])}), {x1(selisih)} poin di atas {short(b)}."
            target = short(a)
        banding += f" Terendah di {short(z)} ({p0(per.loc[z, 'rd'])})."
        warn = _peringatan(*[(short(k), int(per.loc[k, "n"])) for k in per.index])
        pendek = f"Tertinggi di {target}, terendah di {short(z)}."
    else:
        k = per.index[0]
        banding, target, pendek = "", short(k), ""
        warn = _peringatan((short(k), int(per.loc[k, "n"])))

    return dict(
        utama=False, grafik=3,
        jenis="Perbandingan antarwilayah",
        angka=p0(pct(rusak & dihuni)),
        judul="bangunan rusak tetapi masih dihuni atau dipakai usaha",
        pendek=f"{n_rd} dari {len(d)} bangunan rusak tetapi masih ditempati. {pendek}",
        apa=f"{n_rd} dari {len(d)} bangunan rusak tetapi masih ditempati. {banding}",
        mengapa="Dugaan: penghuni belum mampu memperbaiki atau pindah. Survei tidak mencatat pendapatan, jadi dugaan ini belum bisa dibuktikan.",
        lalu_apa="Kerusakan pada bangunan yang ditempati menyangkut keselamatan orang yang tinggal atau bekerja di dalamnya.",
        sekarang_apa=f"Mulai pemeriksaan kelayakan bangunan dari {target}.",
        peringatan=warn + (" Selisih antarkecamatan kecil dan n tiap kecamatan terbatas; jangan dibaca sebagai peringkat."
                           if len(per) >= 2 else ""),
    )


# ---------------- Insight 3: hubungan kondisi lingkungan - kondisi fisik ----------------
def insight_lingkungan(d):
    l = d.dropna(subset=[LINGK])
    gr, gb = l[l[FISIK] == "Rusak"], l[l[FISIK] == "Baik"]
    if gr.empty or gb.empty:
        return None
    pr, pb = pct(gr[LINGK] == "Rusak"), pct(gb[LINGK] == "Rusak")
    arah = "jauh lebih sering" if pr - pb >= BEDA_TIPIS else ("lebih jarang" if pb - pr >= BEDA_TIPIS else "hampir sama seringnya")
    return dict(
        utama=False, grafik=7,
        jenis="Hubungan",
        angka=f"{p0(pr)} vs {p0(pb)}",
        judul="lingkungan rusak di sekitar bangunan rusak vs bangunan baik",
        pendek=f"Lingkungan rusak ditemukan di sekitar {p0(pr)} bangunan rusak, tetapi hanya {p0(pb)} bangunan baik.",
        apa=(f"Lingkungan sekitar bangunan rusak {arah} berkategori rusak ({p0(pr)}, n={len(gr)}) "
             f"dibanding sekitar bangunan baik ({p0(pb)}, n={len(gb)})."),
        mengapa=("Dugaan: bangunan dan sekitarnya sama-sama kurang terawat. Kemungkinan lain, keduanya dinilai oleh orang yang sama "
                 "pada waktu yang sama, sehingga penilaian bisa saling memengaruhi."),
        lalu_apa="Tumpukan sampah, genangan, dan wadah berair dapat menjadi tempat nyamuk bertelur. Survei ini tidak mengukur jentik, jadi ini indikasi.",
        sekarang_apa="Arahkan kerja bakti dan pemeriksaan jentik ke sekitar bangunan rusak lebih dulu.",
        peringatan=_peringatan(("Bangunan rusak", len(gr)), ("Bangunan baik", len(gb))),
    )


# ---------------- Insight 4: anomali kosong vs dihuni ----------------
def insight_kosong(d):
    kos, huni = d[d[HUNI] == "Kosong"], d[d[HUNI].isin(MASIH_DIHUNI)]
    if kos.empty or huni.empty:
        return None
    pk, ph = pct(kos[FISIK] == "Rusak"), pct(huni[FISIK] == "Rusak")
    selisih = pk - ph
    if abs(selisih) < BEDA_TIPIS:
        apa = f"Bangunan kosong ({p0(pk)} rusak, n={len(kos)}) hampir sama rusaknya dengan bangunan yang dihuni ({p0(ph)}, n={len(huni)})."
        judul = "rusak: bangunan kosong vs dihuni, hampir sama"
        pendek = f"Bangunan kosong tidak lebih rusak: {p0(pk)} vs {p0(ph)} pada bangunan dihuni."
    else:
        arah = "lebih sering" if selisih > 0 else "lebih jarang"
        apa = f"Bangunan kosong {arah} rusak ({p0(pk)}, n={len(kos)}) daripada yang dihuni ({p0(ph)}, n={len(huni)})."
        judul = "rusak: bangunan kosong vs dihuni"
        pendek = f"Bangunan kosong {arah} rusak: {p0(pk)} vs {p0(ph)}."

    porsi_ruko = pct(kos[JENIS] == "Ruko")
    rk, rh = kos[kos[JENIS] == "Rumah"], huni[huni[JENIS] == "Rumah"]
    tambahan, warn_pairs = "", [("Kosong", len(kos))]
    mengapa = "Survei tidak mencatat sudah berapa lama bangunan kosong, jadi penyebab perbedaan ini belum bisa dipastikan."
    if len(rk) and len(rh):
        prk, prh = pct(rk[FISIK] == "Rusak"), pct(rh[FISIK] == "Rusak")
        tambahan = (f" Namun {p0(porsi_ruko)} bangunan kosong adalah ruko. Jika hanya rumah yang dilihat, "
                    f"rumah kosong yang rusak {p0(prk)} (n={len(rk)}), rumah yang dihuni {p0(prh)} (n={len(rh)}).")
        warn_pairs.append(("Rumah kosong", len(rk)))
        if (prk - prh) - selisih >= BEDA_TIPIS:
            mengapa = ("Ruko kosong sebagian besar masih baik, sehingga menutupi pola pada rumah. "
                       "Survei tidak mencatat sudah berapa lama bangunan kosong.")

    return dict(
        utama=False, grafik=4,
        jenis="Anomali · Pola tersembunyi",
        angka=f"{p0(pk)} vs {p0(ph)}",
        judul=judul, pendek=pendek,
        apa=apa + tambahan,
        mengapa=mengapa,
        lalu_apa="Status kosong saja belum cukup untuk menandai bangunan bermasalah. Jenis bangunan perlu dilihat bersama.",
        sekarang_apa="Pisahkan rumah dan ruko saat membaca data kosong, dan catat lama kosong pada survei lanjutan.",
        peringatan=_peringatan(*warn_pairs),
    )


# ---------------- Insight 5: kesenjangan rumah - ruko ----------------
def insight_ruko(d):
    ru, rm = d[d[JENIS] == "Ruko"], d[d[JENIS] == "Rumah"]
    if ru.empty or rm.empty:
        return None
    pru, prm = pct(ru[HUNI] == "Kosong"), pct(rm[HUNI] == "Kosong")
    if prm > 0:
        angka = f"{x1(pru / prm)}×"
        banding = f"{p0(pru)} ruko kosong (n={len(ru)}), sedangkan rumah hanya {p0(prm)} (n={len(rm)})."
    else:
        angka = p0(pru)
        banding = f"{p0(pru)} ruko kosong (n={len(ru)}), sedangkan tidak ada rumah yang kosong (n={len(rm)})."
    kos_ru = ru[ru[HUNI] == "Kosong"]
    baik = f" Dari ruko kosong itu, {p0(pct(kos_ru[FISIK] == 'Baik'))} masih berkondisi baik." if len(kos_ru) else ""
    return dict(
        utama=False, grafik=6,
        jenis="Kesenjangan",
        angka=angka,
        judul="lebih sering kosong: ruko dibanding rumah" if pru > prm else "persentase kosong: ruko dan rumah",
        pendek=f"{p0(pru)} ruko kosong, rumah hanya {p0(prm)}.",
        apa=banding + baik,
        mengapa="Dugaan: sebagian ruko sedang menunggu penyewa atau pembeli. Survei tidak mencatat alasan bangunan kosong.",
        lalu_apa="Ruko kosong yang masih baik adalah ruang yang belum terpakai. Bila lama dibiarkan, kondisinya bisa menurun.",
        sekarang_apa="Pantau ruko kosong agar tetap terawat, dan catat alasan serta lama kosongnya pada survei lanjutan.",
        peringatan=_peringatan(("Ruko", len(ru)), ("Rumah", len(rm))),
    )


SEMUA = [insight_kayu, insight_rusak_dihuni, insight_lingkungan, insight_kosong, insight_ruko]


def hitung_semua(d):
    """List insight yang datanya cukup pada filter saat ini (urutan: utama dulu)."""
    hasil = []
    for f in SEMUA:
        try:
            r = f(d)
        except Exception as e:  # satu insight gagal tidak boleh menjatuhkan dashboard
            r = dict(utama=False, grafik=None, jenis="Galat", angka="-", judul=f.__name__, pendek="",
                     apa=f"Insight gagal dihitung: {e}", mengapa="", lalu_apa="", sekarang_apa="", peringatan="")
        if r:
            r["peringatan"] = r["peringatan"].strip()
            hasil.append(r)
    return hasil
