# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random
from urllib.parse import quote

# --- 1. FUNGSI ---
def encode_wa_message(text):
    """
    Encode pesan untuk WhatsApp.
    Menggunakan quote() untuk memastikan karakter Unicode (termasuk emoji)
    di-encode dengan benar ke format URL-safe (UTF-8).
    
    Kami memastikan input adalah string dan meng-encode-nya ke UTF-8 sebelum di-quote.
    Ini adalah cara paling aman untuk menangani emoji.
    """
    # Pastikan input adalah string untuk menghindari error encoding dari tipe data lain (mis. int/float dari DataFrame)
    text_str = str(text) 
    
    # Kunci perbaikan: Meng-encode ke UTF-8 byte, lalu meng-quote byte tersebut.
    # Parameter safe='' memastikan semua karakter (termasuk spasi, simbol, dan karakter non-ASCII)
    # di-quote dengan benar.
    return quote(text_str.encode('utf-8'), safe='')

def bersihkan_nomor(nomor):
    n = str(nomor)
    if n.endswith('.0'): n = n[:-2]
    # Hanya ambil digit
    n = ''.join(filter(str.isdigit, n)) 
    if n.startswith('0'): return '62' + n[1:]
    elif n.startswith('62'): return n
    elif n == "": return "" 
    else: return '62' + n

def format_rupiah(angka):
    try:
        # Menggunakan locale setting untuk pemformatan, tapi kita simulasikan manual
        # dengan f-string dan replace untuk Streamlit
        return f"Rp {int(angka):,}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    except:
        return str(angka)

def get_random_salam():
    salam = ["Assalamu'alaikum #PejuangAmal", "Assalamu'alaikum #SahabatBeramal", "Assalamualaikum #SahabatBeramal", "Assalamualaikum #PejuangAmal"]
    return random.choice(salam)

# --- 2. UI & LOGIKA STREAMLIT ---
st.set_page_config(page_title="Donasi Reporter Pro", page_icon="🚀", layout="wide")
st.title("🚀 Laporan Donasi - CS Beramal")

# SIDEBAR: UPLOAD & SETTING
with st.sidebar:
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("File Excel/CSV", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.info("💡 **Tips Format WA:**\n\n- Gunakan bintang `*teks*` untuk **Tebal**\n- Gunakan `_teks_` untuk *Miring*\n- **Emoji** akan di-encode secara otomatis.")

if uploaded_file is not None:
    try:
        # Membaca Dataframe
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # MAPPING KOLOM
        with st.expander("⚙️ Pengaturan Kolom (Klik disini)", expanded=False):
            cols = df.columns.tolist()
            # Mencoba memprediksi kolom default
            def find_col(keywords):
                for kw in keywords:
                    for col in cols:
                        if kw.lower() in col.lower():
                            return col
                return cols[0] if cols else ""

            default_nama = find_col(['nama', 'name', 'donatur'])
            default_nomor = find_col(['nomor', 'no', 'hp', 'phone'])
            default_nominal = find_col(['nominal', 'jumlah', 'amount'])
            
            c_nama = st.selectbox("Kolom NAMA", cols, index=cols.index(default_nama) if default_nama in cols else 0)
            c_nomor = st.selectbox("Kolom NO HP", cols, index=cols.index(default_nomor) if default_nomor in cols else min(1, len(cols)-1))
            c_nominal = st.selectbox("Kolom NOMINAL", cols, index=cols.index(default_nominal) if default_nominal in cols else min(2, len(cols)-1))
        
        
        # --- Pembagian Tugas/Pagination (Di Sidebar) ---
        st.sidebar.header("2. Pembagian Tugas")
        
        total_data = len(df)
        
        if 'pos_start' not in st.session_state:
            st.session_state.pos_start = 0
        if 'pos_end' not in st.session_state:
            st.session_state.pos_end = min(50, total_data)

        def update_from_slider():
            val = st.session_state.slider_widget
            st.session_state.pos_start = val[0]
            st.session_state.pos_end = val[1]

        def update_from_input():
            # Pastikan start tidak melebihi end
            new_start = st.session_state.num_input_start - 1
            new_end = st.session_state.num_input_end
            
            if new_start < new_end:
                 st.session_state.pos_start = new_start
            else:
                 st.session_state.pos_start = new_end - 1
            
            st.session_state.pos_end = new_end


        # A. Input Angka
        c_awal, c_akhir = st.sidebar.columns(2)
        with c_awal:
            # Gunakan st.session_state.pos_start + 1 agar angka mulai dari 1
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
        
        # --- Potong DataFrame ---
        start_idx = st.session_state.pos_start
        end_idx = st.session_state.pos_end
        
        if start_idx >= end_idx:
            df_sliced = df.iloc[0:0]
            st.sidebar.error("Angka 'Dari' harus lebih kecil dari 'Sampai'!")
        else:
            df_sliced = df.iloc[start_idx:end_idx]
            st.sidebar.caption(f"Menampilkan {len(df_sliced)} data (Index {start_idx+1} - {end_idx}).")

        st.markdown("---")

        # INPUT PESAN
        st.subheader("3. Tulis Pesan")
        
        col_msg1, col_msg2 = st.columns([2, 1])
        with col_msg1:
            default_msg = """Terima kasih banyak atas donasi Rp[nominal] untuk program X. Semoga Allah membalas kebaikan [nama] dengan pahala yang berlipat ganda. Aamiin yaa Rabbal 'alamiin. 🙏

Link Laporan: [link_laporan_program]"""
            template_pesan = st.text_area(
                "Isi Pesan (Gunakan [nama] dan [nominal] sebagai placeholder):", 
                value=default_msg, 
                height=350
            )
        
        with col_msg2:
            st.write("Options:")
            pakai_salam = st.checkbox("✅ Auto Salam + Nama (Unik)", value=True)
            st.caption("*Meningkatkan variasi pesan untuk menghindari potensi blokir massal.*")

        st.markdown("---")
        
        # Styling CSS
        st.markdown("""
        <style>
        input[type="checkbox"] {
            transform: scale(1.5);
            transform-origin: center;
            margin-right: 4px;
        }
        .donor-index, .donor-meta-normal, .donor-meta-done {
            font-size: 0.8rem;
            color: #6b7280;
        }
        .donor-name-normal, .donor-name-done {
            font-weight: 600;
            font-size: 0.95rem;
        }
        .donor-name-done, .donor-meta-done {
            color: #9ca3af;
            text-decoration: line-through;
        }
        .stButton button {
            width: 100%;
            font-weight: bold;
            height: 2.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

        # Tampilkan data dalam grid 3 kolom
        total_slice = len(df_sliced)

        st.subheader(f"Daftar Donatur ({total_slice} Data)")
        st.warning("Klik 'Kirim WA 🚀' untuk membuka chat di WhatsApp. Gunakan checkbox untuk menandai sudah selesai (Done).")
        
        for block_start in range(0, total_slice, 3):
            row_cols = st.columns(3, gap="large")

            for col_idx in range(3):
                data_idx = block_start + col_idx
                if data_idx >= total_slice:
                    break

                row = df_sliced.iloc[data_idx]

                # Mengakses data dengan aman
                nama = str(row[c_nama]) if c_nama in row else "Nama Tidak Ditemukan"
                nomor_raw = row[c_nomor] if c_nomor in row else None
                nominal_raw = row[c_nominal] if c_nominal in row else 0

                if pd.isna(nomor_raw) or str(nomor_raw).strip() == "" or nomor_raw is None:
                    # Skip jika nomor kosong
                    continue

                nomor_bersih = bersihkan_nomor(nomor_raw)
                nominal_rp = format_rupiah(nominal_raw)

                # Rakit pesan
                body_pesan = template_pesan.replace("[nama]", nama).replace("[nominal]", nominal_rp)
                
                if pakai_salam:
                    salam = get_random_salam()
                    # Menambahkan dua baris baru untuk pemisah yang baik
                    pesan_final = f"{salam}, {nama}!\n\n{body_pesan}" 
                else:
                    pesan_final = body_pesan

                # --- PENGGUNAAN FUNGSI YANG DIPERBAIKI ---
                pesan_final_url = encode_wa_message(pesan_final)

                link_wa = f"https://wa.me/{nomor_bersih}?text={pesan_final_url}"
                
                global_idx = start_idx + data_idx

                with row_cols[col_idx]:
                    # Menggunakan st.container() untuk batas visual
                    with st.container(border=True):
                        top1, top2, top3 = st.columns([0.8, 3, 2])

                        with top1:
                            # Checkbox Status
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
                            # Button WA
                            st.link_button(
                                "Kirim WA 🚀",
                                link_wa,
                                type="primary",
                                disabled=is_done,
                                help="Klik untuk membuka WhatsApp Web/Desktop dengan pesan terisi otomatis."
                            )
                        
    except KeyError as e:
        st.error(f"Kolom yang dipilih tidak valid: {e}. Harap periksa kembali pengaturan kolom Anda.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")
else:
    st.info("Silakan upload file Excel/CSV di menu sebelah kiri (Sidebar).")
