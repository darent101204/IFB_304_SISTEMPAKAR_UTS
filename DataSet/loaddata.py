import pandas as pd

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("pet_health_dataset.csv")

# =========================
# CLEAN TEXT
# =========================
df['text'] = df['text'].astype(str)
df['text'] = df['text'].str.lower()

# =========================
# LIST GEJALA (KEYWORDS)
# =========================
symptoms_list = [
"vomiting","diarrhea","lethargy","fever","cough","sneezing",
"itching","hair loss","red eyes","dehydration","weight loss",
"aggression","seizures","paralysis","bad breath"
]

# =========================
# PENYAKIT
# =========================
diseases = df['condition'].unique()

# =========================
# HITUNG PROBABILITAS
# =========================
result = []

for disease in diseases:
    df_disease = df[df['condition'] == disease]
    total = len(df_disease)

    for symptom in symptoms_list:
        count = df_disease['text'].str.contains(symptom).sum()
        prob = count / total if total > 0 else 0

        result.append({
            "penyakit": disease,
            "gejala": symptom,
            "probabilitas": round(prob, 3)
        })

# =========================
# SAVE
# =========================
result_df = pd.DataFrame(result)
result_df.to_csv("hasil_probabilitas2.csv", index=False)

print("Selesai! 🚀")