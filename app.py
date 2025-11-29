import streamlit as st
import pandas as pd
import urllib.parse
import random

# --- 1. FUNGSI UTAMA ---

def bersihkan_nomor(nomor):
    n = str(nomor)
    if n.endswith('.0'): n = n[:-2]
    n = ''.join(filter(str.isdigit, n))
    
    if n.startswith('0'): return '62' + n[1:]
    elif n.startswith('62'): return n
    elif n == "": return "" 
    else: return '62' + n

def format_rupiah(angka):
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return str(angka)

def get_random_salam():
    """Acak salam biar aman dari blokir WA"""
    salam = [
        "Assalamu'alaikum #PejuangAmal", 
        "Assalamu'alaikum #SahabatBeramal", 
        "Assalamualaikum #SahabatBeramal", 
        "Assalamualaikum #PejuangAmal", 
    ]
    return random.choice(salam)

# --- 2. TAMPILAN UI ---

st.set_page_config(page_title="Donasi Reporter", page_icon="📝")
st.title("📝 Laporan Donasi Custom")

# A. UPLOAD FILE
uploaded_file = st.file_uploader("1. Upload Excel/CSV Data Donatur", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"Data dimuat: {len(df)} donatur.")
        
        with st.expander("⚙️ Pengaturan Kolom Excel (Klik jika kolom tidak terbaca)", expanded=False):
            cols = df.columns.tolist()
            c_nama = st.selectbox("Kolom NAMA", cols, index=0)
            c_nomor = st.selectbox("Kolom NO HP", cols, index=min(1, len(cols)-1))
            c_nominal = st.selectbox("Kolom NOMINAL", cols, index=min(2, len(cols)-1))
        
        st.divider()

        # C. CUSTOM PESAN
        st.subheader("2. Tulis Isi Pesan")
        
        # Template default saya ubah agar tidak ada salam di awal, karena salam nanti otomatis
        default_msg = """Tulis isi pesan laporan disini ya kak CS yang sabaar dan tidak suka marah marahh"""

        template_pesan = st.text_area("Isi Pesan (Tanpa Salam Pembuka):", value=default_msg, height=250)
        
        # Opsi Anti-Banned
        pakai_salam = st.checkbox("✅ Gunakan 'Salam + Nama' otomatis di awal pesan (Recommended)", value=True)
        
        st.divider()
        
        # D. LIST DONATUR
        st.subheader("3. Antrian Kirim WA")

        for index, row in df.iterrows():
            nama = str(row[c_nama])
            nomor_raw = row[c_nomor]
            nominal_raw = row[c_nominal]
            
            if pd.isna(nomor_raw) or str(nomor_raw).strip() == "": continue
            
            nomor_bersih = bersihkan_nomor(nomor_raw)
            nominal_rp = format_rupiah(nominal_raw)
            
            # --- LOGIKA PENYUSUNAN PESAN BARU ---
            
            # 1. Siapkan Body Pesan (Ganti [nominal] dan [nama] jika user masih pakai di body)
            body_pesan = template_pesan.replace("[nama]", nama).replace("[nominal]", nominal_rp)
            
            # 2. Gabungkan Salam + Nama + Body
            if pakai_salam:
                salam = get_random_salam()
                # Format: Salam (spasi) Nama (koma) (enter 2x) Body
                pesan_final = f"{salam} {nama},\n\n{body_pesan}"
            else:
                pesan_final = body_pesan

            # Buat Link
            link_wa = f"https://wa.me/{nomor_bersih}?text={urllib.parse.quote(pesan_final)}"
            
            # Render Card
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{nama}** | {nominal_rp}")
                with st.expander("🔍 Preview Pesan"):
                    st.text(pesan_final)
            with col2:
                st.link_button("🚀 Kirim WA", link_wa, type="primary")
            st.write("---")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

else:
    st.info("Silakan upload file Excel data donatur.")

