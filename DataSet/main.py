import pandas as pd
import numpy as np

# ==========================
# 1. LOAD DATASET
# ==========================
file_path = "dataset_gejala.csv"  # pastikan file ada di folder yang sama
df = pd.read_csv(file_path)

# Ambil daftar penyakit
penyakit_list = list(df.columns[1:])

# ==========================
# 2. TAMPILKAN GEJALA
# ==========================
print("=== SISTEM PAKAR DIAGNOSA PENYAKIT HEWAN ===\n")
print("Pilih gejala yang dialami:\n")

for i, gejala in enumerate(df['Gejala']):
    print(f"{i+1}. {gejala}")

print("\nContoh input: 1,3,5")

# ==========================
# 3. INPUT USER
# ==========================
pilihan = input("\nMasukkan nomor gejala: ")

try:
    index_gejala = [int(x.strip()) - 1 for x in pilihan.split(",")]
except:
    print("Input tidak valid!")
    exit()

gejala_user = []

for i in index_gejala:
    if 0 <= i < len(df):
        gejala_user.append(df['Gejala'][i])

if not gejala_user:
    print("Tidak ada gejala dipilih!")
    exit()

print("\nGejala yang dipilih:")
for g in gejala_user:
    print("-", g)

# ==========================
# 4. HITUNG PRIOR
# ==========================
jumlah_penyakit = len(penyakit_list)
prior = {p: 1 / jumlah_penyakit for p in penyakit_list}

# ==========================
# 5. HITUNG NAIVE BAYES
# ==========================
hasil = {}

for penyakit in penyakit_list:
    likelihood = 1

    for gejala in gejala_user:
        data = df[df['Gejala'] == gejala]

        if not data.empty:
            nilai = data[penyakit].values[0]
            likelihood *= nilai
        else:
            likelihood *= 0.01  # smoothing

    hasil[penyakit] = likelihood * prior[penyakit]

# ==========================
# 6. NORMALISASI
# ==========================
total = sum(hasil.values())

probabilitas = {}
for penyakit in hasil:
    if total > 0:
        probabilitas[penyakit] = hasil[penyakit] / total
    else:
        probabilitas[penyakit] = 0

# ==========================
# 7. OUTPUT HASIL
# ==========================
print("\n=== HASIL DIAGNOSA ===")

for penyakit, prob in probabilitas.items():
    print(f"{penyakit}: {prob*100:.2f}%")

# Ambil hasil tertinggi
diagnosa = max(probabilitas, key=probabilitas.get)

print("\n===================================")
print(f"Diagnosa paling mungkin: {diagnosa}")
print("===================================")

# ==========================
# 8. SARAN (OPSIONAL)
# ==========================
print("\nSaran:")
print("- Segera konsultasikan ke dokter hewan")
print("- Lakukan penanganan sesuai gejala")