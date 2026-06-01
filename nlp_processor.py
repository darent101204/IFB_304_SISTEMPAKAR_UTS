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

    # DEMAM
    "demam": "Demam",
    "panas": "Demam",
    "badan panas": "Demam",
    "suhu tinggi": "Demam",

    # ANOREKSIA
    "anoreksia": "Anoreksia",
    "tidak mau makan": "Anoreksia",
    "nafsu makan turun": "Anoreksia",
    "nafsu makan berkurang": "Anoreksia",
    "susah makan": "Anoreksia",
    "tidak nafsu makan": "Anoreksia",

    # SENANG DI TEMPAT DINGIN
    "tempat dingin": "Senang ditempat dingin",
    "mencari tempat dingin": "Senang ditempat dingin",
    "suka tempat dingin": "Senang ditempat dingin",

    # PUCAT
    "pucat": "Pucat",
    "gusi pucat": "Pucat",

    # SUHU RENDAH
    "suhu rendah": "Suhu badan dibawah normal",
    "hipotermia": "Suhu badan dibawah normal",

    # BATUK
    "batuk": "Batuk",
    "sering batuk": "Batuk",

    # BATUK TERUS
    "batuk terus": "Batuk terus menerus",
    "batuk berkepanjangan": "Batuk terus menerus",

    # BATUK TERSEDAK
    "tersedak": "Batuk seperti tersedak",

    # BATUK BERDAHAK
    "batuk berdahak": "Batuk berdahak putih berbusa",
    "dahak putih": "Batuk berdahak putih berbusa",
    "berbusa": "Batuk berdahak putih berbusa",

    # MUNTAH KUNING
    "muntah kuning": "Batuk disertai muntah kuning",

    # HIDUNG
    "hidung kering": "Hidung mengering",

    # BERSIN
    "bersin": "Bersin-bersin",
    "sering bersin": "Bersin-bersin",

    # MENELAN
    "sulit menelan": "Sulit menelan makanan",
    "susah menelan": "Sulit menelan makanan",

    # PILEK
    "pilek": "Pilek",
    "flu": "Pilek",

    # SESAK
    "sesak": "Sesak nafas",
    "sesak napas": "Sesak nafas",
    "sulit bernapas": "Sesak nafas",
    "susah bernapas": "Sesak nafas",

    # MATA
    "mata sayu": "Mata sayu",
    "mata lesu": "Mata sayu",
    "mata merah": "Mata merah",

    # LELERAN
    "leleran": "Leleran jernih",
    "ingus": "Leleran jernih",
    "ingus bening": "Leleran jernih"
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

    for keyword, gejala in KAMUS_GEJALA.items():

        if keyword in text:
            hasil.append(gejala)

    return list(set(hasil))