"""Mesin forward chaining (FC) sederhana.

Membaca aturan IF-THEN dari file JSON, menanyakan fakta dasar kepada user,
lalu menyimpulkan dengan forward chaining dan menampilkan alasannya.

Pemakaian: python forward_chaining.py [aturan.json]
"""
import json
import sys


def muat_aturan(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cari_fakta_dasar(aturan):
    """Fakta dasar = syarat yang tidak pernah menjadi hasil (maka) aturan mana pun."""
    hasil = {r["maka"] for r in aturan}
    dasar = []
    for r in aturan:
        for syarat in r["jika"]:
            if syarat not in hasil and syarat not in dasar:
                dasar.append(syarat)
    return dasar


def tanya_user(fakta_dasar):
    """Tanya satu per satu, kembalikan fakta yang dijawab 'y' (urutan terjaga)."""
    memori = []
    for no, fakta in enumerate(fakta_dasar, start=1):
        while True:
            jawab = input(f"{no}. Apakah {fakta}? (y/t) > ").strip().lower()
            if jawab in ("y", "t"):
                break
            print("   Jawab hanya dengan y atau t.")
        if jawab == "y":
            memori.append(fakta)
    return memori


def syarat_terpenuhi(aturan, memori):
    ada = [s in memori for s in aturan["jika"]]
    return all(ada) if aturan["mode"] == "dan" else any(ada)


def forward_chaining(aturan, memori):
    """Jalankan FC. Mengembalikan (memori, asal, log_siklus).

    asal[fakta] = aturan yang menghasilkan fakta tersebut (bahan 'alasan').
    """
    memori = list(memori)
    asal = {}
    log = []
    while True:
        cocok = [r for r in aturan
                 if syarat_terpenuhi(r, memori) and r["maka"] not in memori]
        if not cocok:
            break
        r = cocok[0]                      # ambil aturan pertama
        memori.append(r["maka"])          # tambahkan hasilnya ke memori
        asal[r["maka"]] = r               # catat asal hasil (alasan)
        log.append(r)
    return memori, asal, log


def cetak_alasan(fakta, asal, memori, indent=1, sudah=None):
    """Cetak alasan secara rekursif: fakta <- aturan (syarat yang terpenuhi)."""
    if sudah is None:
        sudah = set()
    r = asal[fakta]
    terpenuhi = [s for s in r["jika"] if s in memori]
    print("  " * indent + f"{fakta} <- {r['id']} ({', '.join(terpenuhi)})")
    sudah.add(fakta)
    for s in terpenuhi:
        if s in asal and s not in sudah:
            cetak_alasan(s, asal, memori, indent + 1, sudah)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "aturan.json"
    data = muat_aturan(path)
    aturan = data["aturan"]

    print(data["judul"])
    print("Jawab y/t.")
    fakta_dasar = cari_fakta_dasar(aturan)
    memori_awal = tanya_user(fakta_dasar)

    print()
    print("Fakta awal: " + (", ".join(memori_awal) if memori_awal else "(tidak ada)"))
    print()

    memori, asal, log = forward_chaining(aturan, memori_awal)

    for i, r in enumerate(log, start=1):
        print(f"Siklus {i}: {r['id']} -> {r['maka']}")
    print(f"Siklus {len(log) + 1}: tidak ada aturan baru, berhenti")
    print()

    # Kesimpulan akhir = hasil yang tidak dipakai sebagai syarat aturan lain
    dipakai = {s for r in aturan for s in r["jika"]}
    kesimpulan = [f for f in asal if f not in dipakai] or list(asal)

    if kesimpulan:
        print("Kesimpulan: " + ", ".join(kesimpulan))
        print("Alasan:")
        for f in kesimpulan:
            cetak_alasan(f, asal, memori)
    else:
        print("Kesimpulan: tidak ada kesimpulan yang dapat ditarik dari fakta tersebut.")
    print()
    print("Catatan: " + data["batas"])


if __name__ == "__main__":
    main()