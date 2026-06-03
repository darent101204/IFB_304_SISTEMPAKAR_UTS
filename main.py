import pandas as pd
import numpy as np

# ==========================
# 1. LOAD DATASET
# ==========================
file_path = "dataset_gejala.csv"

# ==========================
# 2. KAMUS PENYAKIT PADA ANJING & KUCING
# ==========================
KAMUS_PENYAKIT = {
    "Parvovirus": {
        "deskripsi": "Canine Parvovirus (CPV) adalah penyakit virus menular yang sangat berbahaya, terutama menyerang anak anjing dan anjing yang belum divaksinasi. Virus ini menyerang saluran pencernaan.",
        "solusi": "Segera bawa ke dokter hewan untuk perawatan intensif, perbaikan cairan tubuh (infus), antibiotik untuk mencegah infeksi sekunder, dan isolasi ketat."
    },
    "Coronavirus": {
        "deskripsi": "Canine Coronavirus (CCoV) adalah infeksi usus pada anjing yang umumnya ringan tetapi bisa bertambah parah jika disertai infeksi lain seperti Parvovirus.",
        "solusi": "Perawatan suportif, cairan intravena jika hewan dehidrasi karena diare, pemberian pakan khusus saluran cerna yang mudah dicerna, dan istirahat yang cukup."
    },
    "Hepatitis": {
        "deskripsi": "Infectious Canine Hepatitis (ICH) disebabkan oleh Canine Adenovirus tipe 1 (CAV-1), menyerang hati, ginjal, mata, dan selaput lendir pembuluh darah.",
        "solusi": "Pemberian cairan infus untuk mencegah dehidrasi, pengobatan simptomatik, transfusi darah pada kasus yang parah, dan perawatan suportif di klinik hewan."
    },
    "Parainfluenza": {
        "deskripsi": "Canine Parainfluenza Virus adalah salah satu penyebab utama Kennel Cough (batuk rejan pada anjing), yang merupakan infeksi saluran pernapasan menular.",
        "solusi": "Jauhkan dari hewan lain untuk mencegah penularan. Berikan obat pereda batuk dari resep dokter hewan, istirahat di ruangan dengan sirkulasi udara baik, dan nutrisi optimal."
    },
    "Distemper Cerna": {
        "deskripsi": "Canine Distemper (fase pencernaan) merupakan penyakit virus serius yang menyerang saluran pencernaan sebelum berkembang ke organ lain. Gejalanya seperti diare, muntah, dan anoreksia.",
        "solusi": "Isolasi hewan peliharaan Anda. Dibutuhkan perawatan suportif dengan pemberian cairan (infus), pengobatan untuk menghentikan muntah, dan antibiotik spektrum luas dari dokter hewan."
    },
    "Distemper Nafas": {
        "deskripsi": "Canine Distemper (fase pernapasan) menyerang organ pernapasan, sering diawali dengan demam, leleran pada mata dan hidung, lalu diikuti dengan batuk pilek berat.",
        "solusi": "Periksakan segera ke klinik hewan. Pembersihan sekret mata dan hidung secara berkala, pemberian antibiotik sekunder dari dokter, hidrasi dan uap air (nebulasi) dapat membantu pernapasan."
    },
    "Distemper Kulit": {
        "deskripsi": "Canine Distemper (fase kulit) biasanya bermanifestasi sebagai penebalan kulit atau telapak kaki (hardpad disease) serta bisa muncul lesi pada perut.",
        "solusi": "Bawa ke dokter hewan. Perawatan simptomatik meliputi salep atau krim khusus (pelembap keras) untuk telapak kaki dan antibiotik topikal jika terdapat infeksi kulit."
    },
    "Distemper Syaraf": {
        "deskripsi": "Canine Distemper (fase saraf) merupakan tahap lanjut distemper yang sangat kritis, di mana virus mulai merusak sistem saraf pusat menyebabkan kejang, kelumpuhan, dan kedutan otot (tics).",
        "solusi": "Tingkat kelangsungan hidup sangat bergantung pada perawatan medis. Segera bawa ke unit gawat darurat hewan. Perawatan fokus pada pengendalian kejang dan perawatan paliatif."
    },
    "Rabies": {
        "deskripsi": "Rabies adalah penyakit zoonosis fatal yang menyerang sistem saraf pusat. Penyakit ini dapat menular melalui air liur gigitan hewan terinfeksi.",
        "solusi": "Karantina. Lapor ke instansi atau dokter hewan berwenang secepatnya. Sangat berbahaya dan bisa mematikan serta menular ke manusia. Sayangnya tidak ada pengobatan jika gejala sudah muncul."
    }
}

# ==========================
# 3. DESKRIPSI GEJALA (untuk tooltip bantuan pengguna)
# ==========================
DESKRIPSI_GEJALA = {
    "Lesu": "Hewan terlihat tidak bersemangat, malas bergerak, dan lebih banyak berbaring.",
    "Demam": "Suhu tubuh hewan lebih tinggi dari normal (di atas 39.5°C pada anjing/kucing).",
    "Anoreksia": "Hewan kehilangan nafsu makan dan menolak untuk makan sama sekali.",
    "Senang ditempat dingin": "Hewan cenderung mencari tempat yang sejuk atau dingin untuk berbaring.",
    "Pucat": "Warna gusi, lidah, atau bagian dalam telinga tampak lebih pucat dari biasanya.",
    "Suhu badan dibawah normal": "Suhu tubuh hewan lebih rendah dari normal (di bawah 37.5°C), tubuh terasa dingin saat disentuh.",
    "Batuk": "Hewan mengeluarkan suara batuk sesekali.",
    "Batuk terus menerus": "Hewan batuk secara berulang-ulang tanpa henti dalam waktu yang lama.",
    "Batuk seperti tersedak": "Batuk yang disertai suara seperti ada sesuatu yang tersangkut di tenggorokan.",
    "Batuk berdahak putih berbusa": "Batuk yang mengeluarkan lendir berwarna putih dan berbusa.",
    "Batuk disertai muntah kuning": "Hewan batuk dan kemudian mengeluarkan cairan muntah berwarna kuning.",
    "Hidung mengering": "Hidung hewan yang biasanya basah menjadi kering dan pecah-pecah.",
    "Bersin-bersin": "Hewan bersin berulang kali, menandakan iritasi pada saluran pernapasan atas.",
    "Sulit menelan makanan": "Hewan tampak kesulitan atau kesakitan saat mencoba menelan makanan atau air.",
    "Pilek": "Keluar cairan/ingus dari hidung hewan secara terus-menerus.",
    "Sesak nafas": "Hewan bernafas dengan cepat, berat, atau tampak kesulitan bernafas.",
    "Mata sayu": "Mata hewan tampak tidak bercahaya, layu, dan kurang responsif.",
    "Mata merah": "Bagian putih mata atau kelopak mata hewan tampak memerah atau meradang.",
    "Leleran jernih": "Keluar cairan bening/transparan dari mata atau hidung hewan.",
    "Leleran kuning": "Keluar cairan kental berwarna kuning atau kehijauan dari mata atau hidung, menandakan infeksi.",
    "Mata kuning": "Bagian putih mata (sklera) berubah warna menjadi kuning, tanda gangguan hati.",
    "Gusi kuning": "Gusi hewan berubah warna menjadi kuning (ikterus/jaundice), tanda masalah hati.",
    "Mual": "Hewan tampak tidak nyaman, sering menjilat bibir, menelan berulang kali, atau mengeluarkan air liur berlebihan.",
    "Muntah": "Hewan mengeluarkan isi perut melalui mulut.",
    "Diare": "Feses hewan encer atau berair, lebih sering buang air besar dari biasanya.",
    "Diare terus menerus": "Diare yang berlangsung terus-menerus tanpa membaik selama beberapa hari.",
    "Diare kuning kehijauan": "Feses encer dengan warna kuning kehijauan yang tidak normal.",
    "Diare berdarah": "Feses mengandung darah segar (merah) atau darah yang sudah tercerna (hitam).",
    "Dehidrasi": "Tubuh hewan kekurangan cairan. Ditandai dengan kulit yang lambat kembali saat dicubit dan gusi kering.",
    "Sering minum": "Hewan minum air jauh lebih banyak dari biasanya (polidipsia).",
    "Perut membesar": "Perut hewan tampak kembung, membesar, atau terasa keras saat diraba.",
    "Bengkak tubuh": "Terdapat pembengkakan pada bagian tubuh hewan seperti kaki, wajah, atau perut.",
    "Kulit kuning": "Kulit hewan berubah warna menjadi kekuningan, terutama di area perut dan telinga bagian dalam.",
    "Sering tidur": "Hewan tidur lebih lama dari biasanya dan sulit dibangunkan.",
    "Menyendiri": "Hewan menjauh dari pemilik atau hewan lain, lebih suka berada sendirian.",
    "Bersembunyi": "Hewan bersembunyi di tempat-tempat tersembunyi seperti bawah meja atau lemari.",
    "Pendiam": "Hewan yang biasanya aktif menjadi diam dan tidak banyak bersuara.",
    "Gelisah": "Hewan tampak tidak tenang, mondar-mandir, dan tidak bisa diam.",
    "Agresif": "Hewan menunjukkan perilaku menyerang, menggigit, atau menggeram tanpa alasan yang jelas.",
    "Takut cahaya": "Hewan menghindari cahaya terang dan lebih memilih tempat gelap (fotofobia).",
    "Takut air": "Hewan menunjukkan ketakutan berlebihan terhadap air (hidrofobia), gejala khas rabies.",
    "Ekor turun": "Ekor hewan selalu dalam posisi turun/menjepit di antara kaki belakang.",
    "Mulut berbusa": "Keluar busa atau air liur berlebihan dari mulut hewan, gejala serius yang perlu penanganan segera.",
    "Mata juling": "Posisi bola mata tidak sejajar atau bergerak tidak normal (strabismus).",
    "Kelumpuhan": "Hewan kehilangan kemampuan menggerakkan sebagian atau seluruh anggota tubuhnya.",
    "Bau badan": "Tubuh hewan mengeluarkan bau yang tidak sedap secara tidak normal.",
    "Bulu kusam": "Bulu hewan terlihat tidak berkilau, kering, dan kasar.",
    "Kulit mengelupas": "Kulit hewan mengelupas atau bersisik, mungkin disertai kemerahan.",
    "Kulit bernanah": "Terdapat luka bernanah atau bisul pada kulit hewan (pyoderma).",
    "Telapak kaki mengeras": "Bantalan kaki hewan menjadi keras, tebal, dan pecah-pecah (hardpad).",
    "Kedutan": "Gerakan otot yang tidak terkontrol dan berulang pada bagian tubuh tertentu (myoclonus).",
    "Kejang": "Hewan mengalami kontraksi otot yang tidak terkendali, tubuh kaku, dan mungkin kehilangan kesadaran."
}

def get_data_gejala():
    """Mengembalikan daftar semua gejala dari dataset untuk ditampilkan di form"""
    df = pd.read_csv(file_path)
    return list(df['Gejala'])

def hitung_bayes(gejala_user):
    """
    Fungsi untuk menghitung probabilitas penyakit menggunakan algoritma Naive Bayes
    Berdasarkan gejala yang dinput user.
    """
    df = pd.read_csv(file_path)
    
    # Ambil daftar penyakit dari kolom dataset (mulai dari kolom ke-1, kolom 0 adalah Gejala)
    penyakit_list = list(df.columns[1:])
    jumlah_penyakit = len(penyakit_list)
    
    # Prior probability asumsikan seragam (uninformative prior)
    prior = {p: 1 / jumlah_penyakit for p in penyakit_list}
    
    # Hitung Likelihood
    hasil = {}
    for penyakit in penyakit_list:
        likelihood = 1
        for gejala in gejala_user:
            data = df[df['Gejala'] == gejala]
            if not data.empty:
                nilai = data[penyakit].values[0]
                likelihood *= nilai
            else:
                likelihood *= 0.01  # smoothing jika data tidak ada
                
        hasil[penyakit] = likelihood * prior[penyakit]
        
    # Normalisasi agar total probabilitas menjadi 1
    total = sum(hasil.values())
    probabilitas = {}
    for penyakit in hasil:
        if total > 0:
            probabilitas[penyakit] = hasil[penyakit] / total
        else:
            probabilitas[penyakit] = 0
            
    # Mengurutkan probabilitas dari terbesar ke terkecil
    probabilitas_sorted = {k: v for k, v in sorted(probabilitas.items(), key=lambda item: item[1], reverse=True)}
    
    # Ambil hasil probabilitas tertinggi
    diagnosa_tertinggi = list(probabilitas_sorted.keys())[0]
    
    return {
        "probabilitas": probabilitas_sorted,
        "diagnosa_tertinggi": diagnosa_tertinggi,
        "detail": KAMUS_PENYAKIT.get(diagnosa_tertinggi, {})
    }
