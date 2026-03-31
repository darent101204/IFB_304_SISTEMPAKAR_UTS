from flask import Flask, render_template, request, flash, redirect, url_for
from main import get_data_gejala, hitung_bayes, KAMUS_PENYAKIT

app = Flask(__name__)
app.secret_key = 'diagnopet_ai_super_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnosa')
def diagnosa():
    list_gejala = get_data_gejala()
    return render_template('diagnosa.html', list_gejala=list_gejala)

@app.route('/hasil', methods=['POST'])
def hasil():
    # Ambil list gejala dari input checkbox form
    gejala_user = request.form.getlist('gejala')
    
    # Validasi jika tidak ada gejala dipilih
    if not gejala_user:
        flash('Silakan pilih setidaknya satu gejala untuk memulai diagnosa!', 'danger')
        return redirect(url_for('diagnosa'))
        
    # Hitung probabilitas berdasarkan Bayes
    hasil_bayes = hitung_bayes(gejala_user)
    
    return render_template('hasil.html', 
                            gejala_user=gejala_user,
                            hasil=hasil_bayes)

@app.route('/info')
def info():
    penyakit_info = KAMUS_PENYAKIT
    list_gejala = get_data_gejala()
    return render_template('info.html', penyakit_info=penyakit_info, list_gejala=list_gejala)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
