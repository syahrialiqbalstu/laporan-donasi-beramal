import streamlit as st
import pandas as pd
import urllib.parse
import random

# --- 1. FUNGSI UTAMA ---

def bersihkan_nomor(nomor):
    """Membersihkan format nomor HP"""
    n = str(nomor)
    if n.endswith('.0'): n = n[:-2]
    n = ''.join(filter(str.isdigit, n))
    
    if n.startswith('0'): return '62' + n[1:]
    elif n.startswith('62'): return n
    elif n == "": return "" 
    else: return '62' + n

def format_rupiah(angka):
    """Mengubah angka jadi format Rp 100.000"""
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return str(angka)

def get_random_salam():
    """Acak salam biar aman dari blokir WA"""
    salam = [
        "Assalamualaikum Kak", 
        "Halo Kak", 
        "Selamat Pagi Kak", 
        "Siang Kak", 
        "Hai Kak"
    ]
    return random.choice(salam)

# --- 2. TAMPILAN UI ---

st.set_page_config(page_title="Donasi Reporter", page_icon="📝")
st.title("📝 Laporan Donasi Custom")
st.write("Upload data, atur kata-kata, lalu kirim.")

# A. UPLOAD FILE
uploaded_file = st.file_uploader("1. Upload Excel/CSV Data Donatur", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # Baca File
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"Data dimuat: {len(df)} donatur.")
        
        # B. PILIH KOLOM (Mapping)
        with st.expander("⚙️ Pengaturan Kolom Excel (Klik jika kolom tidak terbaca)", expanded=False):
            cols = df.columns.tolist()
            c_nama = st.selectbox("Kolom NAMA", cols, index=0)
            c_nomor = st.selectbox("Kolom NO HP", cols, index=min(1, len(cols)-1))
            c_nominal = st.selectbox("Kolom NOMINAL", cols, index=min(2, len(cols)-1))
        
        st.divider()

        # C. CUSTOM PESAN (Bagian Baru!)
        st.subheader("2. Tulis Pesan Laporan")
        
        default_msg = """Terima kasih banyak atas donasinya sebesar [nominal] untuk Program Jumat Berkah.
        
Semoga menjadi amal jariyah dan berkah untuk [nama] sekeluarga. 
Sehat selalu ya Kak!

- Admin Yayasan"""

        # Input Text Area
        template_pesan = st.text_area("Edit pesan di bawah ini:", value=default_msg, height=180)
        
        st.info("💡 **Tips:** Gunakan kode `[nama]` dan `[nominal]` di dalam teks. Sistem akan menggantinya otomatis sesuai data Excel.")

        # Opsi Anti-Banned
        pakai_salam = st.checkbox("Tambahkan salam acak di awal pesan? (Disarankan AKTIF agar anti-blokir)", value=True)
        
        st.divider()
        
        # D. LIST DONATUR
        st.subheader("3. Antrian Kirim WA")

        for index, row in df.iterrows():
            # Ambil Data
            nama = str(row[c_nama])
            nomor_raw = row[c_nomor]
            nominal_raw = row[c_nominal]
            
            # Skip nomor kosong
            if pd.isna(nomor_raw) or str(nomor_raw).strip() == "": continue
            
            # Format Data
            nomor_bersih = bersihkan_nomor(nomor_raw)
            nominal_rp = format_rupiah(nominal_raw)
            
            # RAKIT PESAN FINAL
            # 1. Ambil template dari user
            pesan_final = template_pesan
            
            # 2. Ganti [nama] dan [nominal]
            pesan_final = pesan_final.replace("[nama]", nama)
            pesan_final = pesan_final.replace("[nominal]", nominal_rp)
            
            # 3. Tambah salam acak di depan (opsional tapi recommended)
            if pakai_salam:
                salam = get_random_salam()
                # Gabungkan: Salam + Spasi + Nama + Koma + Enter + Isi Pesan User
                # Tapi karena user mungkin sudah tulis nama di body, kita taruh salam saja
                # Strategi aman: Salam + Enter + Pesan User
                pesan_final = f"{salam} {nama},\n\n{pesan_final.replace('[nama]', '')}" 
                # Trik kecil: kalau user pakai [nama] di template, kita biarkan. 
                # Kalau pakai salam otomatis, biasanya strukturnya: "Halo Budi, (Isi pesan)"
                # Jadi kode di atas saya ubah sedikit biar lebih natural:
                
                pesan_final = f"{salam},\n\n{template_pesan.replace('[nama]', nama).replace('[nominal]', nominal_rp)}"

            else:
                # Kalau tidak pakai salam otomatis, pakai template murni
                pesan_final = pesan_final.replace("[nama]", nama).replace("[nominal]", nominal_rp)

            # Buat Link
            link_wa = f"https://wa.me/{nomor_bersih}?text={urllib.parse.quote(pesan_final)}"
            
            # Render Card
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{nama}** | {nominal_rp}")
                with st.expander("🔍 Preview Pesan"):
                    st.text(pesan_final)
            with col2:
                st.link_button("🚀 Kirim", link_wa, type="primary")
            st.write("---")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

else:
    st.info("Silakan upload file Excel data donatur.")