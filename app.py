# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random
from urllib.parse import quote

# --- 1. FUNGSI ---
def encode_wa_message(text):
    """Encode pesan untuk WhatsApp dengan handling emoji yang benar"""
    try:
        # Pastikan text dalam UTF-8, lalu encode untuk URL
        return quote(text.encode('utf-8'), safe='')
    except:
        # Fallback jika ada error
        return quote(text, safe='')

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
        st.sidebar.header("2. Pembagian Tugas")
        
        total_data = len(df)
        
        # --- 1. MEMORI PUSAT (Single Source of Truth) ---
        if 'pos_start' not in st.session_state:
            st.session_state.pos_start = 0
        if 'pos_end' not in st.session_state:
            st.session_state.pos_end = min(50, total_data)

        # --- 2. FUNGSI PENYAMBUNG (Callback) ---
        def update_from_slider():
            val = st.session_state.slider_widget
            st.session_state.pos_start = val[0]
            st.session_state.pos_end = val[1]

        def update_from_input():
            st.session_state.pos_start = st.session_state.num_input_start - 1
            st.session_state.pos_end = st.session_state.num_input_end

        # --- 3. TAMPILAN UI ---
        
        # A. Input Angka
        c_awal, c_akhir = st.sidebar.columns(2)
        with c_awal:
            st.number_input(
                "Dari", min_value=1, max_value=total_data,
                value=st.session_state.pos_start + 1,
                key="num_input_start", on_change=update_from_input
            )
        with c_akhir:
            st.number_input(
                "Sampai", min_value=1, max_value=total_data,
                value=st.session_state.pos_end,
                key="num_input_end", on_change=update_from_input
            )

        # B. Slider
        st.sidebar.slider(
            "Geser Range Cepat:", 0, total_data,
            value=(st.session_state.pos_start, st.session_state.pos_end),
            key="slider_widget", on_change=update_from_slider
        )
        
        # --- 4. HASIL AKHIR ---
        start_idx = st.session_state.pos_start
        end_idx = st.session_state.pos_end
        
        # Validasi
        if start_idx >= end_idx:
            df_sliced = df.iloc[0:0]
            st.sidebar.error("Angka 'Dari' harus lebih kecil!")
        else:
            df_sliced = df.iloc[start_idx:end_idx]
            st.sidebar.caption(f"Menampilkan {len(df_sliced)} data ({start_idx+1} - {end_idx}).")

        st.markdown("---")

        # INPUT PESAN
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
        
        # Styling
        st.markdown("""
        <style>
        input[type="checkbox"] {
            transform: scale(1.5);
            transform-origin: center;
            margin-right: 4px;
        }
        .donor-index {
            font-size: 0.78rem;
            color: #6b7280;
        }
        .donor-name-normal {
            font-weight: 600;
            font-size: 0.9rem;
            color: #111827;
        }
        .donor-name-done {
            font-weight: 600;
            font-size: 0.9rem;
            color: #9ca3af;
            text-decoration: line-through;
        }
        .donor-meta-normal {
            font-size: 0.8rem;
            color: #6b7280;
        }
        .donor-meta-done {
            font-size: 0.8rem;
            color: #9ca3af;
            text-decoration: line-through;
        }
        </style>
        """, unsafe_allow_html=True)

        # Tampilkan data dalam grid 3 kolom
        total_slice = len(df_sliced)

        for block_start in range(0, total_slice, 3):
            row_cols = st.columns(3, gap="large")

            for col_idx in range(3):
                data_idx = block_start + col_idx
                if data_idx >= total_slice:
                    break

                row = df_sliced.iloc[data_idx]

                nama = str(row[c_nama])
                nomor_raw = row[c_nomor]
                nominal_raw = row[c_nominal]

                if pd.isna(nomor_raw) or str(nomor_raw).strip() == "":
                    continue

                nomor_bersih = bersihkan_nomor(nomor_raw)
                nominal_rp = format_rupiah(nominal_raw)

                # Rakit pesan
                body_pesan = template_pesan.replace("[nama]", nama).replace("[nominal]", nominal_rp)
                
                if pakai_salam:
                    salam = get_random_salam()
                    pesan_final = f"{salam} {nama},\n\n{body_pesan}"
                else:
                    pesan_final = body_pesan

                # FIX: Gunakan fungsi khusus untuk encode emoji dengan benar
                pesan_final_url = encode_wa_message(pesan_final)

                link_wa = f"https://wa.me/{nomor_bersih}?text={pesan_final_url}"
                
                global_idx = start_idx + data_idx

                with row_cols[col_idx]:
                    with st.container():
                        top1, top2, top3 = st.columns([0.9, 3, 1.8])

                        with top1:
                            is_done = st.checkbox(
                                "",
                                key=f"status_{global_idx}"
                            )
                            st.markdown(
                                f"<span class='donor-index'>#{global_idx+1}</span>",
                                unsafe_allow_html=True
                            )

                        name_class = "donor-name-done" if is_done else "donor-name-normal"
                        meta_class = "donor-meta-done" if is_done else "donor-meta-normal"

                        with top2:
                            st.markdown(
                                f"<div class='{name_class}'>{nama}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='{meta_class}'>💰 {nominal_rp}<br>📱 {nomor_bersih}</div>",
                                unsafe_allow_html=True
                            )

                        with top3:
                            st.link_button(
                                "Kirim WA 🚀",
                                link_wa,
                                type="primary",
                                disabled=is_done
                            )
                            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan upload file di menu sebelah kiri (Sidebar).")