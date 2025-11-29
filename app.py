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
st.title("🚀 Laporan Donasi - CS Beramal")

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

        # MAPPING KOLOM
        with st.expander("⚙️ Pengaturan Kolom (Klik disini)", expanded=False):
            cols = df.columns.tolist()
            c_nama = st.selectbox("Kolom NAMA", cols, index=0)
            c_nomor = st.selectbox("Kolom NO HP", cols, index=min(1, len(cols)-1))
            c_nominal = st.selectbox("Kolom NOMINAL", cols, index=min(2, len(cols)-1))
        
        # FITUR BARU: PAGINATION (INPUT ANGKA)
        st.sidebar.markdown("---")
        st.sidebar.header("2. Pembagian Tugas")
        total_data = len(df)
        
        # --- 1. INISIALISASI MEMORI (Agar Slider & Angka Sinkron) ---
        if 'start_idx' not in st.session_state:
            st.session_state['start_idx'] = 0
        if 'end_idx' not in st.session_state:
            st.session_state['end_idx'] = min(50, total_data)

        # --- 2. FUNGSI UPDATE (Callback) ---
        def update_from_slider():
            # Saat slider digeser, update angka input
            st.session_state.start_idx = st.session_state.slider_key[0]
            st.session_state.end_idx = st.session_state.slider_key[1]

        def update_from_input():
            # Saat angka diketik, update slider
            # Konversi: Input Manusia (mulai 1) -> Python (mulai 0)
            st.session_state.start_idx = st.session_state.num_start - 1
            st.session_state.end_idx = st.session_state.num_end

        # --- 3. TAMPILAN INPUT ANGKA ---
        c_awal, c_akhir = st.sidebar.columns(2)
        
        with c_awal:
            # Input Start (Value diambil dari memori)
            st.number_input(
                "Dari", 
                min_value=1, max_value=total_data, 
                value=st.session_state.start_idx + 1, 
                key="num_start", on_change=update_from_input
            )
            
        with c_akhir:
            # Input End
            st.number_input(
                "Sampai", 
                min_value=1, max_value=total_data, 
                value=st.session_state.end_idx, 
                key="num_end", on_change=update_from_input
            )

        # --- 4. TAMPILAN SLIDER ---
        # Slider mengambil value dari session_state agar posisinya ikut berubah saat diketik
        slider_range = st.sidebar.slider(
            "Geser Range Cepat:",
            0, total_data,
            (st.session_state.start_idx, st.session_state.end_idx),
            key="slider_key", on_change=update_from_slider
        )
        
        # Tetapkan variable untuk pemotongan data
        start_idx = st.session_state.start_idx
        end_idx = st.session_state.end_idx
        
        df_sliced = df.iloc[start_idx:end_idx]
        
        # Info teks kecil
        st.sidebar.caption(f"Menampilkan {end_idx - start_idx} data.")


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
                # ... (Kode di atas ini biarkan saja) ...
        
        # --- GANTI DARI SINI ---
        
        # Styling agar tampilan lebih renggang dan rapi
        st.markdown("""
        <style>
            div[data-testid="column"] { align-self: center; } 
            hr { margin: 0.5rem 0 1rem 0; }
        </style>
        """, unsafe_allow_html=True)

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
            
            # --- TAMPILAN UI BARU ---
            
            # Buat container agar setiap baris ada kotaknya sedikit
            with st.container():
                # Bagi layout menjadi 4 kolom:
                # Kolom 1 (Kecil): Nomor Urut
                # Kolom 2 (Kecil): Checkbox
                # Kolom 3 (Besar): Nama & Info
                # Kolom 4 (Sedang): Tombol Kirim
                c_num, c_check, c_info, c_btn = st.columns([0.3, 0.3, 4, 1.2])
                
                # 1. Penomoran (Index Excel + 1)
                with c_num:
                    st.write(f"**#{index+1}**")
                
                # 2. Checkbox Status
                with c_check:
                    # Key unik berdasarkan index agar status tersimpan
                    is_done = st.checkbox("", key=f"status_{index}")
                
                # 3. Info Donatur (Logika Coret Teks)
                with c_info:
                    if is_done:
                        # Jika dicentang: Teks abu-abu & dicoret
                        st.markdown(f"<h3 style='color: #b2bec3; margin:0; text-decoration: line-through;'>{nama}</h3>", unsafe_allow_html=True)
                        st.caption(f"~~{nominal_rp}~~ | ~~{nomor_bersih}~~ (Terkirim ✅)")
                    else:
                        # Jika belum: Teks hitam tebal
                        st.markdown(f"<h3 style='margin:0;'>{nama}</h3>", unsafe_allow_html=True)
                        st.caption(f"💰 **{nominal_rp}** | 📱 {nomor_bersih}")

                # 4. Tombol Kirim
                with c_btn:
                    # Jika sudah selesai, tombol jadi disabled (abu-abu) agar tidak salah kirim
                    st.link_button("Kirim WA 🚀", link_wa, type="primary", disabled=is_done)
                
                st.divider()

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan upload file di menu sebelah kiri (Sidebar).")







