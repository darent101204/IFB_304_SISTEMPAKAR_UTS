from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from main import get_data_gejala, hitung_bayes, KAMUS_PENYAKIT
from nlp_processor import ekstrak_gejala
import pandas as pd
import re

app = Flask(__name__)
app.secret_key = 'diagnopet_ai_super_secret_key'

# ============================
# KNOWLEDGE BASE HELPERS
# ============================

def get_all_gejala_list():
    """Mengembalikan seluruh daftar gejala dari dataset"""
    return get_data_gejala()

def get_gejala_relevan(gejala_terkumpul):
    """
    Berdasarkan gejala yang sudah terkumpul, hitung penyakit paling mungkin saat ini,
    lalu kembalikan gejala-gejala lain yang relevan (likelihood tinggi) untuk penyakit tersebut
    yang BELUM ditanyakan/disebutkan.
    """
    if not gejala_terkumpul:
        return []

    df = pd.read_csv("dataset_gejala.csv")
    penyakit_list = list(df.columns[1:])

    # Hitung skor kasar tiap penyakit berdasarkan gejala terkumpul
    skor = {}
    for penyakit in penyakit_list:
        total = 0
        for gejala in gejala_terkumpul:
            data = df[df['Gejala'] == gejala]
            if not data.empty:
                total += data[penyakit].values[0]
        skor[penyakit] = total

    # Ambil top 3 penyakit paling mungkin
    top_penyakit = sorted(skor, key=skor.get, reverse=True)[:3]

    # Cari gejala yang relevan (likelihood > 0.3) untuk top penyakit tapi belum disebutkan
    gejala_relevan = []
    for penyakit in top_penyakit:
        for _, row in df.iterrows():
            gejala_nama = row['Gejala']
            if gejala_nama not in gejala_terkumpul and gejala_nama not in gejala_relevan:
                if row[penyakit] >= 0.5:
                    gejala_relevan.append(gejala_nama)

    return gejala_relevan[:4]  # Max 4 saran gejala


def get_gejala_sudah_ditanya(session_data):
    """Mengembalikan gejala yang sudah ditanya sebagai follow-up"""
    return session_data.get('gejala_ditanya', [])


# ============================
# CHATBOT CONVERSATION ENGINE
# ============================

def detect_intent(text):
    """Deteksi intent dari pesan user"""
    text_lower = text.lower().strip()

    def contains_word(t, token):
        return re.search(rf"\b{re.escape(token)}\b", t) is not None

    def contains_phrase(t, phrase):
        return re.search(rf"\b{re.escape(phrase)}\b", t) is not None

    # Intent: Salam
    salam_keywords = ["halo", "hai", "hi", "hello", "selamat pagi", "selamat siang",
                       "selamat sore", "selamat malam", "hey", "assalamualaikum"]
    if any(contains_word(text_lower, kata) for kata in salam_keywords):
        return "salam"

    # Intent: Tanya kemampuan
    if any(contains_phrase(text_lower, phrase) for phrase in [
        "apa yang bisa kamu lakukan", "bisa apa", "fungsi kamu",
        "kemampuan kamu", "kamu bisa apa", "apa fungsimu"
    ]):
        return "kemampuan"

    # Intent: Tanya identitas
    if any(contains_phrase(text_lower, phrase) for phrase in [
        "siapa kamu", "kamu siapa", "nama kamu", "siapa namamu"
    ]):
        return "identitas"

    # Intent: Terima kasih
    if any(contains_word(text_lower, kata) for kata in [
        "terima kasih", "makasih", "thanks", "thank you", "trims"
    ]):
        return "terima_kasih"

    # Intent: Reset / mulai ulang
    if any(contains_phrase(text_lower, phrase) for phrase in [
        "mulai ulang", "reset", "ulang", "diagnosa baru",
        "mulai lagi", "dari awal", "ulangi"
    ]):
        return "reset"

    # Intent: User bilang cukup / minta diagnosa
    if any(contains_phrase(text_lower, phrase) for phrase in [
        "cukup", "diagnosa", "itu saja", "itu aja", "hanya itu",
        "tidak ada lagi", "sudah", "udah", "analisis",
        "proses", "hasil", "selesai", "sekian"
    ]):
        return "diagnosa"

    # Intent: Jawaban ya (untuk follow-up)
    if text_lower in ["ya", "iya", "yap", "yoi", "betul", "benar", "yes", "y"]:
        return "jawab_ya"

    # Intent: Jawaban tidak (untuk follow-up)
    if text_lower in ["tidak", "nggak", "enggak", "no", "n", "tdk", "gak", "ga", "ngga"]:
        return "jawab_tidak"

    # Intent: Set mode stepwise (tanya bertahap)
    if any(contains_phrase(text_lower, phrase) for phrase in ["tanya bertahap", "bertahap", "tanya jawab", "satu per satu", "tanyakan satu per satu"]):
        return "set_stepwise"

    # Intent: Set mode immediate (langsung diagnosa)
    if any(contains_phrase(text_lower, phrase) for phrase in ["diagnosa langsung", "langsung", "segera", "diagnosa sekarang", "langsung diagnosa"]):
        return "set_immediate"

    # Intent: Pertanyaan sebab-akibat (kenapa/mengapa ...)
    if contains_phrase(text_lower, 'kenapa') or contains_phrase(text_lower, 'mengapa'):
        return 'sebab'

    # Default: coba ekstrak gejala
    return "gejala"


def init_session():
    """Inisialisasi session chatbot jika belum ada"""
    if 'chatbot_gejala' not in session:
        session['chatbot_gejala'] = []
    if 'chatbot_gejala_ditanya' not in session:
        session['chatbot_gejala_ditanya'] = []
    if 'chatbot_state' not in session:
        session['chatbot_state'] = 'idle'  # idle, collecting, follow_up
    if 'chatbot_pending_gejala' not in session:
        session['chatbot_pending_gejala'] = None
    if 'chatbot_sudah_diagnosa' not in session:
        session['chatbot_sudah_diagnosa'] = False
    if 'chatbot_mode' not in session:
        # 'immediate' = langsung diagnosa, 'stepwise' = tanya jawab bertahap
        session['chatbot_mode'] = 'immediate'


def reset_session():
    """Reset semua data chatbot di session"""
    session['chatbot_gejala'] = []
    session['chatbot_gejala_ditanya'] = []
    session['chatbot_state'] = 'idle'
    session['chatbot_pending_gejala'] = None
    session['chatbot_sudah_diagnosa'] = False


def format_gejala_list(gejala_list):
    """Format list gejala menjadi string bullet"""
    return "\n".join([f"• {g}" for g in gejala_list])


def build_diagnosa_response(gejala_list):
    """Bangun respons diagnosa lengkap dari gejala yang terkumpul"""
    hasil = hitung_bayes(gejala_list)

    diagnosa = hasil['diagnosa_tertinggi']
    prob = hasil['probabilitas'][diagnosa] * 100
    detail = hasil['detail']

    # Build top 3 probabilitas
    top3 = list(hasil['probabilitas'].items())[:3]
    prob_text = "\n".join([
        f"{'🥇' if i == 0 else '🥈' if i == 1 else '🥉'} {p}: {v*100:.1f}%"
        for i, (p, v) in enumerate(top3)
    ])

    response = f"""📋 **HASIL DIAGNOSA**

Berdasarkan {len(gejala_list)} gejala yang teridentifikasi:
{format_gejala_list(gejala_list)}

🏥 **Diagnosa Utama: {diagnosa}**
📊 Probabilitas: **{prob:.1f}%**

📝 **Deskripsi:**
{detail.get('deskripsi', '-')}

💊 **Solusi & Saran:**
{detail.get('solusi', '-')}

📊 **Perbandingan Probabilitas:**
{prob_text}

⚠️ *Hasil ini merupakan prediksi berdasarkan algoritma Naive Bayes. Segera konsultasikan ke dokter hewan untuk pemeriksaan lebih lanjut.*"""

    # Bersihkan whitespace berlebih (lebih dari satu baris kosong -> satu baris kosong)
    response = re.sub(r"\n\s*\n+", "\n\n", response).strip()

    return response, hasil


def process_chatbot_message(text):
    """Main chatbot processing logic"""
    init_session()

    intent = detect_intent(text)

    # ---- SALAM ----
    if intent == "salam":
        if session.get('chatbot_gejala'):
            return {
                "response": f"Halo kembali! 👋\n\nKita masih dalam sesi diagnosa. Saat ini sudah teridentifikasi {len(session['chatbot_gejala'])} gejala:\n{format_gejala_list(session['chatbot_gejala'])}\n\nSilakan lanjutkan menceritakan gejala lain, atau ketik \"diagnosa\" jika sudah cukup.",
                "type": "bot",
                "quick_replies": ["Diagnosa sekarang", "Reset percakapan"]
            }
        return {
            "response": "Halo! 👋 Saya **DiagnoPet AI**, asisten diagnosa penyakit hewan peliharaan Anda.\n\nCeritakan gejala yang dialami hewan Anda, dan saya akan membantu menganalisisnya.\n\n**Contoh:**\n• \"Anjing saya lemas dan tidak mau makan\"\n• \"Kucing saya batuk dan pilek\"\n• \"Hewan saya demam dan muntah-muntah\"",
            "type": "bot",
            "quick_replies": []
        }

    # ---- IDENTITAS ----
    if intent == "identitas":
        return {
            "response": "Saya **DiagnoPet AI** 🤖, chatbot sistem pakar yang membantu mendiagnosis penyakit pada anjing dan kucing.\n\nSaya menggunakan metode **Naive Bayes** untuk menganalisis gejala dan memberikan kemungkinan penyakit beserta solusinya.",
            "type": "bot",
            "quick_replies": []
        }

    # ---- KEMAMPUAN ----
    if intent == "kemampuan":
        return {
            "response": "Saya dapat membantu Anda dengan:\n\n🔍 **Analisis Gejala** — Ceritakan gejala hewan Anda\n🧠 **Diagnosa AI** — Menggunakan Naive Bayes untuk menentukan kemungkinan penyakit\n💊 **Rekomendasi Solusi** — Memberikan saran penanganan\n📊 **Perbandingan** — Menampilkan probabilitas beberapa penyakit\n\nSaya mengenali **9 jenis penyakit** pada anjing dan kucing dengan **53 gejala** yang berbeda.",
            "type": "bot",
            "quick_replies": ["Mulai diagnosa"]
        }

    # ---- TERIMA KASIH ----
    if intent == "terima_kasih":
        reset_session()
        return {
            "response": "Sama-sama! 😊 Semoga hewan peliharaan Anda segera sehat kembali.\n\nJika ingin melakukan diagnosa lagi, silakan ceritakan gejala baru kapan saja.",
            "type": "bot",
            "quick_replies": []
        }

    # ---- RESET ----
    if intent == "reset":
        reset_session()
        return {
            "response": "🔄 Sesi telah direset!\n\nSilakan ceritakan gejala hewan Anda dari awal.",
            "type": "bot",
            "quick_replies": []
        }

    # ---- SET MODE: STEPWISE / IMMEDIATE ----
    if intent == "set_stepwise":
        session['chatbot_mode'] = 'stepwise'
        session.modified = True
        return {
            "response": "✅ Mode diubah: Tanya jawab bertahap aktif. Saya akan mengajukan pertanyaan follow-up untuk memperjelas gejala.",
            "type": "bot",
            "quick_replies": ["Mulai diagnosa", "Reset percakapan"]
        }

    if intent == "set_immediate":
        session['chatbot_mode'] = 'immediate'
        session.modified = True
        return {
            "response": "✅ Mode diubah: Diagnosa langsung aktif. Saya akan memberikan hasil diagnosa segera setelah gejala tercatat.",
            "type": "bot",
            "quick_replies": ["Mulai diagnosa", "Reset percakapan"]
        }

    # ---- JAWAB YA (untuk follow-up) ----
    if intent == "jawab_ya":
        pending = session.get('chatbot_pending_gejala')
        if pending:
            gejala_list = session['chatbot_gejala']
            if pending not in gejala_list:
                gejala_list.append(pending)
                session['chatbot_gejala'] = gejala_list

            session['chatbot_pending_gejala'] = None
            session.modified = True

            # Cari follow-up berikutnya
            gejala_relevan = get_gejala_relevan(gejala_list)
            gejala_ditanya = session.get('chatbot_gejala_ditanya', [])
            gejala_belum_tanya = [g for g in gejala_relevan if g not in gejala_ditanya and g not in gejala_list]

            if gejala_belum_tanya:
                next_gejala = gejala_belum_tanya[0]
                session['chatbot_pending_gejala'] = next_gejala
                gejala_ditanya.append(next_gejala)
                session['chatbot_gejala_ditanya'] = gejala_ditanya
                session.modified = True

                return {
                    "response": f"✅ Gejala **{pending}** dicatat!\n\n📝 Gejala terkumpul: {len(gejala_list)}\n\nApakah hewan Anda juga mengalami **{next_gejala}**?",
                    "type": "bot",
                    "quick_replies": ["Ya", "Tidak", "Diagnosa sekarang"]
                }
            else:
                return {
                    "response": f"✅ Gejala **{pending}** dicatat!\n\n📝 Total gejala terkumpul: {len(gejala_list)}\n{format_gejala_list(gejala_list)}\n\nApakah ada gejala lain? Atau ketik **\"diagnosa\"** untuk melihat hasil analisis.",
                    "type": "bot",
                    "quick_replies": ["Diagnosa sekarang", "Tidak ada lagi"]
                }

        return {
            "response": "Silakan ceritakan gejala yang dialami hewan Anda.",
            "type": "bot",
            "quick_replies": []
        }

    # ---- JAWAB TIDAK (untuk follow-up) ----
    if intent == "jawab_tidak":
        pending = session.get('chatbot_pending_gejala')
        session['chatbot_pending_gejala'] = None
        session.modified = True

        gejala_list = session.get('chatbot_gejala', [])

        if gejala_list:
            # Cari follow-up berikutnya
            gejala_relevan = get_gejala_relevan(gejala_list)
            gejala_ditanya = session.get('chatbot_gejala_ditanya', [])
            gejala_belum_tanya = [g for g in gejala_relevan if g not in gejala_ditanya and g not in gejala_list]

            if gejala_belum_tanya:
                next_gejala = gejala_belum_tanya[0]
                session['chatbot_pending_gejala'] = next_gejala
                gejala_ditanya.append(next_gejala)
                session['chatbot_gejala_ditanya'] = gejala_ditanya
                session.modified = True

                return {
                    "response": f"Baik, dicatat.\n\nApakah hewan Anda mengalami **{next_gejala}**?",
                    "type": "bot",
                    "quick_replies": ["Ya", "Tidak", "Diagnosa sekarang"]
                }
            else:
                return {
                    "response": f"Baik. Saat ini sudah terkumpul {len(gejala_list)} gejala:\n{format_gejala_list(gejala_list)}\n\nApakah ada gejala lain? Atau ketik **\"diagnosa\"** untuk melihat hasil.",
                    "type": "bot",
                    "quick_replies": ["Diagnosa sekarang", "Tidak ada lagi"]
                }

        return {
            "response": "Silakan ceritakan gejala yang dialami hewan Anda.",
            "type": "bot",
            "quick_replies": []
        }

    # ---- DIAGNOSA ----
    if intent == "diagnosa":
        gejala_list = session.get('chatbot_gejala', [])
        if not gejala_list:
            return {
                "response": "⚠️ Belum ada gejala yang teridentifikasi.\n\nSilakan ceritakan gejala hewan Anda terlebih dahulu.\n\n**Contoh:** \"Anjing saya lemas, demam, dan tidak mau makan\"",
                "type": "bot",
                "quick_replies": []
            }

        response_text, hasil = build_diagnosa_response(gejala_list)
        session['chatbot_sudah_diagnosa'] = True
        session.modified = True

        return {
            "response": response_text,
            "type": "bot",
            "quick_replies": ["Diagnosa ulang", "Terima kasih"],
            "diagnosa_data": {
                "diagnosa": hasil['diagnosa_tertinggi'],
                "probabilitas": {k: round(v * 100, 1) for k, v in hasil['probabilitas'].items()},
                "gejala_count": len(gejala_list)
            }
        }

    # ---- SEBAB / KENAPA (pertanyaan sebab-akibat) ----
    if intent == 'sebab':
        # coba ekstrak gejala dari kalimat
        gejala_terkait = ekstrak_gejala(text)

        # jika tidak ditemukan, coba hapus kata tanya awal dan ekstrak lagi
        if not gejala_terkait:
            text2 = re.sub(r'^(kenapa|mengapa)\b', '', text.lower()).strip()
            gejala_terkait = ekstrak_gejala(text2)

        if not gejala_terkait:
            return {
                "response": "Maaf, saya kurang paham gejalanya. Bisa jelaskan lebih spesifik (mis. 'mata kuning', 'batuk berdahak')?",
                "type": "bot",
                "quick_replies": []
            }

        # lakukan bayes dengan gejala yang diekstrak
        hasil = hitung_bayes(gejala_terkait)
        diagnosa_utama = hasil['diagnosa_tertinggi']
        prob = hasil['probabilitas'][diagnosa_utama] * 100
        detail = hasil.get('detail', {})

        # buat ringkasan singkat
        top3 = list(hasil['probabilitas'].items())[:3]
        prob_text = "\n".join([f"- {p}: {v*100:.1f}%" for p, v in top3])

        response = f"Berdasarkan gejala {format_gejala_list(gejala_terkait)} kemungkinan penyebabnya antara lain:\n{prob_text}\n\nDiagnosa teratas: {diagnosa_utama} ({prob:.1f}%)\n{detail.get('deskripsi', '-') }\n{detail.get('solusi', '-') }"

        # rapikan whitespace
        response = re.sub(r"\n\s*\n+", "\n\n", response).strip()

        return {
            "response": response,
            "type": "bot",
            "quick_replies": ["Diagnosa sekarang", "Reset percakapan"]
        }

    # ---- GEJALA (DEFAULT) ----
    gejala_baru = ekstrak_gejala(text)

    if not gejala_baru:
        all_gejala = get_all_gejala_list()
        # Tampilkan contoh gejala
        contoh = all_gejala[:10]
        return {
            "response": f"Maaf, saya belum dapat mengenali gejala dari kalimat tersebut. 🤔\n\nCoba gunakan kata-kata seperti:\n{format_gejala_list(contoh)}\n\n... dan masih banyak lagi.\n\n**Contoh kalimat:** \"Anjing saya demam, lemas, dan muntah-muntah\"",
            "type": "bot",
            "quick_replies": []
        }

    # Tambahkan gejala baru ke session
    gejala_list = session.get('chatbot_gejala', [])
    gejala_ditambahkan = []

    for g in gejala_baru:
        if g not in gejala_list:
            gejala_list.append(g)
            gejala_ditambahkan.append(g)

    session['chatbot_gejala'] = gejala_list
    session['chatbot_state'] = 'collecting'
    session.modified = True

    # Jika tidak ada gejala baru
    if not gejala_ditambahkan:
        return {
            "response": f"Gejala tersebut sudah tercatat sebelumnya. ✅\n\nGejala saat ini ({len(gejala_list)}):\n{format_gejala_list(gejala_list)}\n\nApakah ada gejala lain? Atau ketik **\"diagnosa\"** untuk melihat hasil.",
            "type": "bot",
            "quick_replies": ["Diagnosa sekarang", "Tidak ada lagi"]
        }

    # Mode: immediate = langsung diagnosa, stepwise = tanya jawab bertahap
    if session.get('chatbot_mode', 'immediate') == 'immediate':
        response_text, hasil = build_diagnosa_response(gejala_list)
        session['chatbot_sudah_diagnosa'] = True
        session.modified = True

        return {
            "response": response_text,
            "type": "bot",
            "quick_replies": ["Diagnosa ulang", "Terima kasih"],
            "diagnosa_data": {
                "diagnosa": hasil['diagnosa_tertinggi'],
                "probabilitas": {k: round(v * 100, 1) for k, v in hasil['probabilitas'].items()},
                "gejala_count": len(gejala_list)
            }
        }

    # Jika mode 'stepwise': konfirmasi gejala dan lanjutkan pertanyaan follow-up
    konfirmasi = f"✅ Gejala terdeteksi:\n{format_gejala_list(gejala_ditambahkan)}"

    if len(gejala_list) > len(gejala_ditambahkan):
        konfirmasi += f"\n\n📝 Total gejala terkumpul: {len(gejala_list)}"

    # Cari pertanyaan follow-up yang relevan
    gejala_relevan = get_gejala_relevan(gejala_list)
    gejala_ditanya = session.get('chatbot_gejala_ditanya', [])
    gejala_belum_tanya = [g for g in gejala_relevan if g not in gejala_ditanya and g not in gejala_list]

    if gejala_belum_tanya:
        next_gejala = gejala_belum_tanya[0]
        session['chatbot_pending_gejala'] = next_gejala
        gejala_ditanya.append(next_gejala)
        session['chatbot_gejala_ditanya'] = gejala_ditanya
        session.modified = True

        konfirmasi += f"\n\nUntuk membantu diagnosa lebih akurat, apakah hewan Anda juga mengalami **{next_gejala}**?"

        return {
            "response": konfirmasi,
            "type": "bot",
            "quick_replies": ["Ya", "Tidak", "Diagnosa sekarang"]
        }
    else:
        konfirmasi += f"\n\nApakah ada gejala lain? Atau ketik **\"diagnosa\"** untuk melihat hasil analisis."
        return {
            "response": konfirmasi,
            "type": "bot",
            "quick_replies": ["Diagnosa sekarang", "Tidak ada lagi"]
        }


# ============================
# ROUTES
# ============================

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
    text = request.form.get('message', '').strip()
    if not text:
        return jsonify({
            "response": "Silakan ketik pesan Anda.",
            "type": "bot",
            "quick_replies": []
        })

    result = process_chatbot_message(text)
    return jsonify(result)


@app.route('/chatbot/reset', methods=['POST'])
def chatbot_reset():
    reset_session()
    return jsonify({
        "response": "🔄 Sesi direset! Silakan ceritakan gejala hewan Anda.",
        "type": "bot",
        "quick_replies": []
    })


@app.route('/chatbot/status', methods=['GET'])
def chatbot_status():
    """Endpoint untuk cek status session chatbot saat ini"""
    init_session()
    return jsonify({
        "gejala_count": len(session.get('chatbot_gejala', [])),
        "gejala_list": session.get('chatbot_gejala', []),
        "state": session.get('chatbot_state', 'idle'),
        "sudah_diagnosa": session.get('chatbot_sudah_diagnosa', False),
        "mode": session.get('chatbot_mode', 'immediate')
    })


@app.route('/chatbot/mode', methods=['POST'])
def chatbot_set_mode():
    """Endpoint untuk mengubah mode chatbot (immediate | stepwise)"""
    mode = request.form.get('mode', '').strip()
    if mode not in ('immediate', 'stepwise'):
        return jsonify({"error": "invalid mode"}), 400

    session['chatbot_mode'] = mode
    session.modified = True
    return jsonify({"mode": mode, "message": f"Mode diubah menjadi {mode}"})


if __name__ == '__main__':
    app.run(debug=True)