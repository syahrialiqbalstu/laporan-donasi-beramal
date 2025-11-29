import streamlit as st
import pandas as pd
import urllib.parse
import random

# --- 1. FUNGSI LOGIKA DI BELAKANG LAYAR ---

def bersihkan_nomor(nomor):
    """Mengubah 08xx atau +62xx menjadi format 628xx"""
    n = str(nomor)
    # Buang karakter non-angka
    n = ''.join(filter(str.isdigit, n))
    
    if n.startswith('0'):
        return '62' + n[1:]
    elif n.startswith('62'):
        return n
    else:
        return '62' + n # Asumsi default tambah 62

def generate_pesan(nama, nominal):
    """Membuat pesan dengan variasi sapaan agar aman dari spam detector"""
    sapaan_list = [
        "Assalamualaikum Kak", 
        "Halo Kak", 
        "Selamat Pagi Kak", 
        "Hai Kak"
    ]
    sapaan = random.choice(sapaan_list)
    
    pesan = f"""{sapaan} {nama},
    
Terima kasih banyak atas donasinya sebesar Rp {nominal:,.0f}.
Dana sudah kami terima. Semoga menjadi keberkahan untuk Kakak sekeluarga.

- Admin Yayasan"""
    return pesan

def buat_link_wa(nomor, pesan):
    pesan_encoded = urllib.parse.quote(pesan)
    return f"https://wa.me/{nomor}?text={pesan_encoded}"

# --- 2. TAMPILAN WEB (UI) ---

st.set_page_config(page_title="Donasi Reporter", page_icon="💚")

st.title("💚 Alat Laporan Donasi WA")
st.write("Upload data Excel, lalu klik tombol untuk kirim.")

# Upload File
uploaded_file = st.file_uploader("Upload Excel Data Donatur", type=['xlsx', 'csv'])

if uploaded_file is not None:
    # Baca data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"Berhasil memuat {len(df)} data donatur.")
        
        # Tampilkan Data dalam bentuk List Antrian
        st.divider()
        
        for index, row in df.iterrows():
            # Ambil data per baris (Sesuaikan nama kolom dengan Excel Anda)
            # Pastikan di Excel nama kolomnya: 'Nama', 'Nomor', 'Nominal'
            nama = row.get('Nama', 'Donatur')
            nomor_raw = row.get('Nomor', 0)
            nominal = row.get('Nominal', 0)
            
            # Proses Data
            nomor_bersih = bersihkan_nomor(nomor_raw)
            pesan_teks = generate_pesan(nama, nominal)
            link_wa = buat_link_wa(nomor_bersih, pesan_teks)
            
            # Tampilan Per Donatur (Card Style)
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{nama}")
                st.text(f"Nominal: Rp {nominal:,.0f} | No: {nomor_bersih}")
                # Preview pesan kecil (opsional)
                with st.expander("Lihat isi pesan"):
                    st.write(pesan_teks)
            
            with col2:
                # Tombol Ajaib
                st.link_button("🚀 Kirim WA", link_wa, type="primary")
            
            st.divider()
            
    except Exception as e:
        st.error(f"Terjadi kesalahan membaca file: {e}")
        st.info("Pastikan nama kolom di Excel adalah: Nama, Nomor, Nominal")

else:
    st.info("Silakan upload file Excel terlebih dahulu.")