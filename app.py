import streamlit as st
import pandas as pd
import urllib.parse
import random

# --- 1. FUNGSI ---
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
    salam = ["Assalamu'alaikum #PejuangAmal", "Assalamu'alaikum #SahabatBeramal", "Assalamualaikum #SahabatBeramal", "Assalamualaikum #PejuangAmal"]
    return random.choice(salam)

# --- 2. UI ---
st.set_page_config(page_title="Donasi Reporter Pro", page_icon="🚀", layout="wide")
st.title("🚀 Laporan Donasi WA - Tim CS")

# SIDEBAR: UPLOAD & SETTING
with st.sidebar:
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("File Excel/CSV", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.info("💡 **Tips Format WA:**\n\n- Gunakan bintang `*teks*` untuk **Tebal**\n- Gunakan `_teks_` untuk *Miring*")

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # FITUR BARU: PAGINATION / BATASI BARIS
        total_data = len(df)
        st.sidebar.markdown("---")
        st.sidebar.header("2. Pembagian Tugas")
        
        # Slider untuk memilih range baris
        range_data = st.sidebar.slider(
            "Tampilkan baris ke berapa?",
            0, total_data, (0, min(50, total_data)) # Default 0 - 50
        )
        start_idx, end_idx = range_data
        
        # Filter DataFrame berdasarkan slider
        df_sliced = df.iloc[start_idx:end_idx]
        
        st.success(f"Menampilkan data ke-{start_idx+1} sampai {end_idx} (Dari total {total_data} data)")

        # INPUT PESAN
        st.markdown("---")
        st.subheader("3. Tulis Pesan")
        
        col_msg1, col_msg2 = st.columns([2, 1])
        with col_msg1:
            default_msg = """Tulis isi pesan laporan disini ya kak CS yang sabaar dan suka membantu Program"""
            template_pesan = st.text_area("Isi Pesan (Gunakan * untuk bold):", value=default_msg, height=350)
        
        with col_msg2:
            st.write("Options:")
            pakai_salam = st.checkbox("✅ Auto Salam + Nama", value=True)
            st.caption("*Lebih aman dari blokir karena pesan unik.*")

        st.markdown("---")
        
        # LIST DATA
        st.subheader("4. Eksekusi")

        # Gunakan container agar rapi
        for index, row in df_sliced.iterrows():
            nama = str(row[c_nama])
            nomor_raw = row[c_nomor]
            nominal_raw = row[c_nominal]
            
            if pd.isna(nomor_raw) or str(nomor_raw).strip() == "": continue
            
            nomor_bersih = bersihkan_nomor(nomor_raw)
            nominal_rp = format_rupiah(nominal_raw)
            
            # RAKIT PESAN
            body_pesan = template_pesan.replace("[nama]", nama).replace("[nominal]", nominal_rp)
            
            if pakai_salam:
                salam = get_random_salam()
                pesan_final = f"{salam} {nama},\n\n{body_pesan}"
            else:
                pesan_final = body_pesan

            link_wa = f"https://wa.me/{nomor_bersih}?text={urllib.parse.quote(pesan_final)}"
            
            # TAMPILAN PER BARIS (Lebih Padat)
            with st.container():
                c1, c2, c3 = st.columns([0.5, 3, 1])
                with c1:
                    # Checkbox visual saja (Streamlit akan refresh jika diklik, tapi membantu mata)
                    st.checkbox("", key=f"chk_{index}") 
                with c2:
                    st.markdown(f"**{nama}** | {nominal_rp}")
                    st.caption(f"No: {nomor_bersih}")
                with c3:
                    st.link_button("Kirim WA ➡", link_wa, type="primary")
                st.divider()

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan upload file di menu sebelah kiri (Sidebar).")

