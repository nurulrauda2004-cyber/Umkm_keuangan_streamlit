import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Aplikasi Keuangan UMKM", layout="wide")

# ---------- Helpers ----------

def sample_dataframe():
    data = {
        "tanggal": pd.date_range(end=pd.Timestamp.today(), periods=12, freq='M'),
        "kategori": ["penjualan","penjualan","biaya","biaya","penjualan","biaya","penjualan","biaya","penjualan","biaya","penjualan","biaya"],
        "keterangan": ["Penjualan produk A","Penjualan produk B","Bahan baku","Transport","Penjualan produk C","Gaji","Penjualan produk D","Listrik","Penjualan produk E","Sewa","Penjualan produk F","Promosi"],
        "nominal": [1500000,1200000,-500000,-200000,1800000,-700000,1600000,-150000,1400000,-300000,1700000,-100000]
    }
    df = pd.DataFrame(data)
    df['tanggal'] = pd.to_datetime(df['tanggal']).dt.date
    return df


def compute_kpis(df):
    # asumsi: pendapatan positif, pengeluaran negatif
    total_pendapatan = df[df['nominal']>0]['nominal'].sum()
    total_biaya = -df[df['nominal']<0]['nominal'].sum()
    laba_bersih = total_pendapatan - total_biaya
    return total_pendapatan, total_biaya, laba_bersih


# ---------- UI ----------

st.title("Aplikasi Keuangan UMKM")
st.markdown("Aplikasi sederhana untuk memasukkan, melihat, dan menganalisis data keuangan UMKM.")

col1, col2 = st.columns([2,1])

with col1:
    st.header("Data transaksi")
    uploaded = st.file_uploader("Unggah file CSV (format: tanggal,kategori,keterangan,nominal)", type=['csv'])

    if uploaded is None:
        if st.button("Gunakan contoh data"):
            df = sample_dataframe()
        else:
            st.info("Unggah CSV atau klik 'Gunakan contoh data' untuk mulai.")
            df = None
    else:
        try:
            df = pd.read_csv(uploaded, parse_dates=['tanggal'])
            # normalisasi
            if df['tanggal'].dtype == 'O':
                df['tanggal'] = pd.to_datetime(df['tanggal']).dt.date
            else:
                df['tanggal'] = pd.to_datetime(df['tanggal']).dt.date
            st.success("File berhasil diunggah")
        except Exception as e:
            st.error(f"Galat membaca file: {e}")
            df = None

    if df is not None:
        st.dataframe(df.sort_values('tanggal', ascending=False))

        # download csv hasil edit
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Unduh CSV (hasil)", data=csv, file_name='data_keuangan_umkm.csv', mime='text/csv')

with col2:
    st.header("Template & Petunjuk")
    st.markdown("Jika kamu belum punya file CSV, unduh template di bawah dan isi data transaksi: tanggal (YYYY-MM-DD), kategori, keterangan, nominal (pendapatan positif, pengeluaran negatif).")
    if st.button("Unduh template CSV"):
        tmp = sample_dataframe().to_csv(index=False).encode('utf-8')
        st.download_button("Klik untuk download template","", tmp, file_name='template_keuangan_umkm.csv')


# ---------- Analisis & Visualisasi ----------

if df is not None:
    st.header("Ringkasan")
    tp, tb, lb = compute_kpis(df)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Pendapatan", f"Rp {int(tp):,}")
    k2.metric("Total Biaya", f"Rp {int(tb):,}")
    k3.metric("Laba Bersih", f"Rp {int(lb):,}")

    # series bulanan
    df_time = df.copy()
    df_time['bulan'] = pd.to_datetime(df_time['tanggal']).dt.to_period('M').dt.to_timestamp()
    monthly = df_time.groupby('bulan')['nominal'].sum().reset_index()

    st.subheader("Tren Bulanan (Saldo)")
    fig1 = px.line(monthly, x='bulan', y='nominal', markers=True, title='Saldo per Bulan')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribusi Kategori")
    cat = df.groupby('kategori')['nominal'].sum().reset_index()
    fig2 = px.pie(cat, names='kategori', values='nominal', title='Proporsi per Kategori')
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabel Transaksi (filter)")
    start_date = st.date_input("Dari tanggal", value=df_time['bulan'].min().date())
    end_date = st.date_input("Sampai tanggal", value=df_time['bulan'].max().date())

    mask = (pd.to_datetime(df['tanggal']) >= pd.to_datetime(start_date)) & (pd.to_datetime(df['tanggal']) <= pd.to_datetime(end_date))
    st.dataframe(df.loc[mask].sort_values('tanggal', ascending=False))

    # Simple editing: menambahkan transaksi baru
    st.subheader("Tambah transaksi baru")
    with st.form("add_txn"):
        d = st.date_input("Tanggal", value=datetime.today())
        kat = st.selectbox("Kategori", options=["penjualan","biaya","lainnya"], index=0)
        ket = st.text_input("Keterangan")
        nom = st.number_input("Nominal (masukkan angka, pendapatan positif, pengeluaran negatif)", value=0)
        submitted = st.form_submit_button("Tambah")
        if submitted:
            new = pd.DataFrame([{'tanggal': d, 'kategori': kat, 'keterangan': ket, 'nominal': nom}])
            df = pd.concat([df, new], ignore_index=True)
            st.success("Transaksi baru ditambahkan. Unduh CSV untuk menyimpan hasilnya.")


    st.markdown("---")
    st.caption("Aplikasi ini hanya template — untuk dipakai di operasi sebenarnya, pertimbangkan backend (database), autentikasi, validasi, dan backup.")
