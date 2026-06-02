# FILE: nlp_processor.py

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

STOPWORDS = [
    "anjing",
    "kucing",
    "saya",
    "hewan",
    "peliharaan",
    "terlihat",
    "kelihatan",
    "sedang",
    "yang",
    "dan",
    "di",
    "ke",
    "ada",
    "itu",
    "ini"
]

KAMUS_GEJALA = {

    # LESU
    "lesu": "Lesu",
    "lemas": "Lesu",
    "lemah": "Lesu",
    "tidak aktif": "Lesu",
    "tidak berenergi": "Lesu",
    "malas bergerak": "Lesu",
    "loyo": "Lesu",
    "tidak bersemangat": "Lesu",

    # DEMAM
    "demam": "Demam",
    "panas": "Demam",
    "badan panas": "Demam",
    "suhu tinggi": "Demam",
    "tubuh panas": "Demam",

    # ANOREKSIA
    "anoreksia": "Anoreksia",
    "tidak mau makan": "Anoreksia",
    "nafsu makan turun": "Anoreksia",
    "nafsu makan berkurang": "Anoreksia",
    "susah makan": "Anoreksia",
    "tidak nafsu makan": "Anoreksia",
    "mogok makan": "Anoreksia",
    "menolak makan": "Anoreksia",

    # SENANG DI TEMPAT DINGIN
    "tempat dingin": "Senang ditempat dingin",
    "mencari tempat dingin": "Senang ditempat dingin",
    "suka tempat dingin": "Senang ditempat dingin",
    "senang dingin": "Senang ditempat dingin",

    # PUCAT
    "pucat": "Pucat",
    "gusi pucat": "Pucat",
    "warna pucat": "Pucat",

    # SUHU RENDAH
    "suhu rendah": "Suhu badan dibawah normal",
    "hipotermia": "Suhu badan dibawah normal",
    "badan dingin": "Suhu badan dibawah normal",
    "tubuh dingin": "Suhu badan dibawah normal",
    "suhu dibawah normal": "Suhu badan dibawah normal",

    # BATUK
    "batuk": "Batuk",
    "sering batuk": "Batuk",

    # BATUK TERUS
    "batuk terus": "Batuk terus menerus",
    "batuk berkepanjangan": "Batuk terus menerus",
    "batuk tidak berhenti": "Batuk terus menerus",
    "batuk terus menerus": "Batuk terus menerus",

    # BATUK TERSEDAK
    "tersedak": "Batuk seperti tersedak",
    "batuk tersedak": "Batuk seperti tersedak",
    "seperti tersedak": "Batuk seperti tersedak",

    # BATUK BERDAHAK
    "batuk berdahak": "Batuk berdahak putih berbusa",
    "dahak putih": "Batuk berdahak putih berbusa",
    "berbusa": "Batuk berdahak putih berbusa",
    "berdahak": "Batuk berdahak putih berbusa",

    # MUNTAH KUNING
    "muntah kuning": "Batuk disertai muntah kuning",
    "batuk muntah kuning": "Batuk disertai muntah kuning",

    # HIDUNG
    "hidung kering": "Hidung mengering",
    "hidung mengering": "Hidung mengering",
    "hidung pecah": "Hidung mengering",

    # BERSIN
    "bersin": "Bersin-bersin",
    "sering bersin": "Bersin-bersin",
    "bersin-bersin": "Bersin-bersin",

    # MENELAN
    "sulit menelan": "Sulit menelan makanan",
    "susah menelan": "Sulit menelan makanan",
    "tidak bisa menelan": "Sulit menelan makanan",

    # PILEK
    "pilek": "Pilek",
    "flu": "Pilek",
    "ingus encer": "Pilek",

    # SESAK
    "sesak": "Sesak nafas",
    "sesak napas": "Sesak nafas",
    "sesak nafas": "Sesak nafas",
    "sulit bernapas": "Sesak nafas",
    "susah bernapas": "Sesak nafas",
    "napas berat": "Sesak nafas",
    "nafas berat": "Sesak nafas",

    # MATA SAYU
    "mata sayu": "Mata sayu",
    "mata lesu": "Mata sayu",
    "mata redup": "Mata sayu",

    # MATA MERAH
    "mata merah": "Mata merah",
    "mata bengkak": "Mata merah",
    "mata iritasi": "Mata merah",

    # LELERAN JERNIH
    "leleran jernih": "Leleran jernih",
    "leleran": "Leleran jernih",
    "ingus": "Leleran jernih",
    "ingus bening": "Leleran jernih",
    "cairan hidung": "Leleran jernih",

    # LELERAN KUNING
    "leleran kuning": "Leleran kuning",
    "ingus kuning": "Leleran kuning",
    "cairan kuning dari hidung": "Leleran kuning",

    # MATA KUNING
    "mata kuning": "Mata kuning",
    "mata menguning": "Mata kuning",
    "bola mata kuning": "Mata kuning",

    # GUSI KUNING
    "gusi kuning": "Gusi kuning",
    "gusi menguning": "Gusi kuning",

    # MUAL
    "mual": "Mual",
    "mual-mual": "Mual",

    # MUNTAH
    "muntah": "Muntah",
    "sering muntah": "Muntah",
    "muntah-muntah": "Muntah",

    # DIARE
    "diare": "Diare",
    "mencret": "Diare",
    "buang air besar cair": "Diare",
    "bab cair": "Diare",
    "tinja cair": "Diare",

    # DIARE TERUS MENERUS
    "diare terus": "Diare terus menerus",
    "diare berkepanjangan": "Diare terus menerus",
    "diare tidak berhenti": "Diare terus menerus",
    "mencret terus": "Diare terus menerus",

    # DIARE KUNING KEHIJAUAN
    "diare kuning": "Diare kuning kehijauan",
    "diare kehijauan": "Diare kuning kehijauan",
    "diare hijau": "Diare kuning kehijauan",
    "tinja kuning hijau": "Diare kuning kehijauan",

    # DIARE BERDARAH
    "diare berdarah": "Diare berdarah",
    "diare darah": "Diare berdarah",
    "bab berdarah": "Diare berdarah",
    "tinja berdarah": "Diare berdarah",

    # DEHIDRASI
    "dehidrasi": "Dehidrasi",
    "kekurangan cairan": "Dehidrasi",
    "kulit kering": "Dehidrasi",

    # SERING MINUM
    "sering minum": "Sering minum",
    "minum terus": "Sering minum",
    "banyak minum": "Sering minum",
    "haus terus": "Sering minum",

    # PERUT MEMBESAR
    "perut membesar": "Perut membesar",
    "perut buncit": "Perut membesar",
    "perut kembung": "Perut membesar",
    "perut besar": "Perut membesar",

    # BENGKAK TUBUH
    "bengkak": "Bengkak tubuh",
    "tubuh bengkak": "Bengkak tubuh",
    "badan bengkak": "Bengkak tubuh",
    "bengkak tubuh": "Bengkak tubuh",

    # KULIT KUNING
    "kulit kuning": "Kulit kuning",
    "kulit menguning": "Kulit kuning",

    # SERING TIDUR
    "sering tidur": "Sering tidur",
    "tidur terus": "Sering tidur",
    "banyak tidur": "Sering tidur",

    # MENYENDIRI
    "menyendiri": "Menyendiri",
    "suka sendiri": "Menyendiri",
    "menjauh": "Menyendiri",

    # BERSEMBUNYI
    "bersembunyi": "Bersembunyi",
    "sembunyi": "Bersembunyi",
    "suka bersembunyi": "Bersembunyi",
    "sering bersembunyi": "Bersembunyi",

    # PENDIAM
    "pendiam": "Pendiam",
    "diam": "Pendiam",
    "tidak bersuara": "Pendiam",
    "tidak merespon": "Pendiam",

    # GELISAH
    "gelisah": "Gelisah",
    "resah": "Gelisah",
    "tidak tenang": "Gelisah",
    "gugup": "Gelisah",
    "cemas": "Gelisah",

    # AGRESIF
    "agresif": "Agresif",
    "ganas": "Agresif",
    "sering menggigit": "Agresif",
    "menyerang": "Agresif",
    "galak": "Agresif",
    "marah": "Agresif",

    # TAKUT CAHAYA
    "takut cahaya": "Takut cahaya",
    "fotofobia": "Takut cahaya",
    "menghindari cahaya": "Takut cahaya",
    "takut sinar": "Takut cahaya",

    # TAKUT AIR
    "takut air": "Takut air",
    "hidrofobia": "Takut air",
    "menghindari air": "Takut air",
    "tidak mau minum": "Takut air",

    # EKOR TURUN
    "ekor turun": "Ekor turun",
    "ekor menyelip": "Ekor turun",
    "ekor ditekuk": "Ekor turun",

    # MULUT BERBUSA
    "mulut berbusa": "Mulut berbusa",
    "busa di mulut": "Mulut berbusa",
    "liur berbusa": "Mulut berbusa",

    # MATA JULING
    "mata juling": "Mata juling",
    "juling": "Mata juling",
    "mata tidak simetris": "Mata juling",

    # KELUMPUHAN
    "lumpuh": "Kelumpuhan",
    "kelumpuhan": "Kelumpuhan",
    "tidak bisa berjalan": "Kelumpuhan",
    "tidak bisa gerak": "Kelumpuhan",
    "kaki lemas": "Kelumpuhan",
    "kaki tidak bisa digerakkan": "Kelumpuhan",

    # BAU BADAN
    "bau badan": "Bau badan",
    "bau": "Bau badan",
    "bau busuk": "Bau badan",
    "badan bau": "Bau badan",

    # BULU KUSAM
    "bulu kusam": "Bulu kusam",
    "bulu tidak mengkilap": "Bulu kusam",
    "bulu rontok": "Bulu kusam",
    "bulu kasar": "Bulu kusam",

    # KULIT MENGELUPAS
    "kulit mengelupas": "Kulit mengelupas",
    "kulit terkelupas": "Kulit mengelupas",
    "kulit mengelupas": "Kulit mengelupas",

    # KULIT BERNANAH
    "kulit bernanah": "Kulit bernanah",
    "nanah di kulit": "Kulit bernanah",
    "luka bernanah": "Kulit bernanah",
    "kulit infeksi": "Kulit bernanah",

    # TELAPAK KAKI MENGERAS
    "telapak kaki mengeras": "Telapak kaki mengeras",
    "kaki mengeras": "Telapak kaki mengeras",
    "telapak keras": "Telapak kaki mengeras",
    "hardpad": "Telapak kaki mengeras",

    # KEDUTAN
    "kedutan": "Kedutan",
    "otot kedutan": "Kedutan",
    "otot bergerak sendiri": "Kedutan",
    "tics": "Kedutan",

    # KEJANG
    "kejang": "Kejang",
    "kejang-kejang": "Kejang",
    "sering kejang": "Kejang",
    "step": "Kejang",
    "konvulsi": "Kejang",
}


def ekstrak_gejala(text):

    if not text:
        return []

    text = text.lower()

    tokens = text.split()

    tokens = [
        token
        for token in tokens
        if token not in STOPWORDS
    ]

    text = " ".join(tokens)

    hasil = []

    # Sort keywords by length (longest first) to prioritize multi-word matches
    sorted_keywords = sorted(
        KAMUS_GEJALA.keys(),
        key=len,
        reverse=True
    )

    for keyword in sorted_keywords:
        gejala = KAMUS_GEJALA[keyword]

        if keyword in text and gejala not in hasil:
            hasil.append(gejala)

    return list(set(hasil))