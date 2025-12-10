# Aplikasi Keuangan UMKM (Streamlit)


Template repo ini berisi aplikasi Streamlit untuk mencatat dan melihat ringkasan keuangan UMKM.


## Cara pakai lokal
1. Clone repo
2. Buat virtualenv dan install: `pip install -r requirements.txt`
3. Jalankan: `streamlit run app.py`


## Deploy ke Streamlit Cloud
1. Push repo ke GitHub
2. Masuk ke share.streamlit.io dan sambungkan repo
3. Pilih file `app.py` sebagai entrypoint


## Catatan
- Format CSV: `tanggal,kategori,keterangan,nominal`
- Nominal pendapatan ditulis positif, pengeluaran negatif.
