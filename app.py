from flask import Flask, render_template, request, flash, redirect, url_for
from main import get_data_gejala, hitung_bayes, KAMUS_PENYAKIT
from nlp_processor import ekstrak_gejala

app = Flask(__name__)
app.secret_key = 'diagnopet_ai_super_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnosa')
def diagnosa():
    list_gejala = get_data_gejala()
    return render_template(
        'diagnosa.html',
        list_gejala=list_gejala
    )


@app.route('/hasil', methods=['POST'])
def hasil():

    # checkbox
    gejala_checkbox = request.form.getlist('gejala')

    # text input
    gejala_text = request.form.get('gejala_text', '')

    # NLP
    gejala_nlp = ekstrak_gejala(gejala_text)

    print("INPUT USER")
    print(gejala_text)
    print("GEJALA NLP")
    print(gejala_nlp)

    # gabungkan
    gejala_user = list(
        set(
            gejala_checkbox +
            gejala_nlp
        )
    )

    if not gejala_user:
        flash(
            'Silakan pilih gejala atau tuliskan gejala terlebih dahulu!',
            'danger'
        )
        return redirect(url_for('diagnosa'))

    hasil_bayes = hitung_bayes(gejala_user)

    return render_template(
        'hasil.html',
        gejala_user=gejala_user,
        gejala_nlp=gejala_nlp,
        gejala_text=gejala_text,
        hasil=hasil_bayes
    )

@app.route('/info')
def info():
    penyakit_info = KAMUS_PENYAKIT
    list_gejala = get_data_gejala()

    return render_template(
        'info.html',
        penyakit_info=penyakit_info,
        list_gejala=list_gejala
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


@app.route('/chatbot/process', methods=['POST'])
def chatbot_process():

    text = request.form.get('message', '')

    text_lower = text.lower()

    if any(kata in text_lower for kata in ["halo", "hai", "hi", "selamat"]):
        return {
            "response":
            "Halo! Saya DiagnoPet AI. Silakan ceritakan gejala yang dialami hewan Anda."
        }

    if "siapa kamu" in text_lower:
        return {
            "response":
            "Saya DiagnoPet AI, chatbot sistem pakar yang membantu mendiagnosis penyakit hewan berdasarkan gejala yang Anda berikan."
        }

    if any(kata in text_lower for kata in ["terima kasih", "makasih", "thanks"]):
        return {
            "response":
            "Sama-sama. Semoga hewan peliharaan Anda segera sehat kembali."
        }

    if "apa yang bisa kamu lakukan" in text_lower:
        return {
            "response":
            "Saya dapat membantu menganalisis gejala hewan dan memberikan kemungkinan penyakit menggunakan metode Naive Bayes."
        }

    gejala = ekstrak_gejala(text)

    if not gejala:
        return {
            "response":
            """
    Maaf, saya belum mengenali gejala tersebut.

    Contoh gejala yang dapat saya kenali:

    ✓ Lesu
    ✓ Demam
    ✓ Batuk
    ✓ Pilek
    ✓ Bersin-bersin
    ✓ Sesak nafas
    ✓ Mata merah
    ✓ Hidung kering
            """
        }

    hasil = hitung_bayes(gejala)

    response = f"""
Gejala terdeteksi:

{chr(10).join(['✓ ' + g for g in gejala])}

Kemungkinan penyakit:

✓ {hasil['diagnosa_tertinggi']}

Probabilitas:
{hasil['probabilitas'][hasil['diagnosa_tertinggi']] * 100:.2f}%

Saran:
{hasil['detail']['solusi']}
"""

    return {
        "response": response
    }

if __name__ == '__main__':
    app.run(debug=True)