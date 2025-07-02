import streamlit as st
import json
from collections import deque
from datetime import datetime, timedelta
from babel.dates import format_date
import datetime
import os

# File untuk menyimpan riwayat rolling
HISTORY_FILE = "rolling_history.json"

# Fungsi untuk memuat riwayat rolling dari file
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = {}

# Fungsi untuk mendapatkan tanggal pengambilan usus kotor
# Jika hari ini Sabtu, maka tanggal yang ditampilkan adalah Senin
# Selain itu, tetap menampilkan besok
def get_tomorrow_date():
    today = datetime.today()  # Menggunakan today() agar sesuai zona waktu lokal
    if today.weekday() == 5:  # Jika hari ini Sabtu (5)
        target_date = today + timedelta(days=2)  # Lompat ke Senin
    else:
        target_date = today + timedelta(days=1)  # Besok untuk hari lainnya
    return target_date.strftime('%Y-%m-%d')  # Format YYYY-MM-DD untuk penyimpanan

# Fungsi untuk rolling data selain "WSF"
def roll_data(*datasets):
    queues = []
    
    for d in datasets:
        if not isinstance(d, dict):
            continue  # Skip jika data bukan dictionary

        filtered_values = []
        for v in d.values():
            if v != 'WSF':
                filtered_values.append(v)
        queues.append(deque(filtered_values))
    
    if queues and queues[0]:
        first_value = queues[0].popleft()
        
        for i in range(len(queues) - 1):
            if queues[i + 1]:
                queues[i].append(queues[i + 1].popleft())

        queues[-1].append(first_value)

    for i, d in enumerate(datasets):
        if not isinstance(d, dict):
            continue
        keys = list(d.keys())
        new_values = iter(queues[i])
        
        for k in keys:
            if d[k] != 'WSF':
                d[k] = next(new_values, d[k])

# Streamlit UI
st.title("Rolling Jadwal Pengambilan Usus Kotor")

# Daftar pilihan
perusahaan = ["--Pilih Perusahaan--", "Wahana Sejahtera Foods", "Phalosari Unggul Jaya"]
# Dropdown untuk pilih satu
selection = st.selectbox("Silakan pilih satu perusahaan:", perusahaan)

if selection == "Wahana Sejahtera Foods" and selection != "--Pilih Perusahaan--":
    # Atur dua kolom: kolom gambar dan kolom judul
    col1, col2 = st.columns([1, 4])  # rasio 1:4 agar gambar lebih kecil dari teks

    with col1:
        st.image("logo.png", width=130)  # ganti dengan path ke file gambar kamu

    with col2:
        st.markdown("<h1 style='margin-bottom: 0;'>Wahana Sejahtera Foods</h1>", unsafe_allow_html=True)
    
    # Membuat tab
    tabs = st.tabs(["Rolling", "Riwayat Rolling"])

    with tabs[0]:
        data_input = st.text_area("**Masukkan Data (format JSON):**")
        if st.button("Rolling", type="primary"):
            if data_input:
                try:
                    # Parse input menjadi dictionary
                    data = json.loads(data_input)

                    # Pastikan data memiliki key yang sesuai
                    required_keys = ["1", "2", "3", "5", "6"]
                    if not all(k in data for k in required_keys):
                        st.error("Data harus memiliki key: 1, 2, 3, 5, dan 6", icon="🚨")
                    else:
                        # Konversi key dari string ke integer
                        data = {int(k): v for k, v in data.items()}
                        
                        # Jalankan rolling
                        target_date = get_tomorrow_date()
                        st.write("\n**Bismillah...**\n")
                        st.write(f"**Jadwal pengambilan usus kotor {format_date(datetime.strptime(target_date, '%Y-%m-%d'), format='full', locale='id')}**")

                        roll_data(data[1], data[2], data[3], data[5], data[6])

                        # Menampilkan hasil rolling dalam format teks
                        for line, entries in data.items():
                            st.write(f'\nLine - {line}')
                            for key, value in entries.items():
                                st.write(f"{key}. {value}")

                        # Simpan hasil rolling berdasarkan tanggal
                        history[target_date] = data

                        # Simpan ke file JSON
                        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                            json.dump(history, f, indent=4, ensure_ascii=False)

                        # # Menampilkan hasil rolling dalam format JSON
                        # st.subheader("Hasil Rolling Untuk Rolling Selanjutnya")
                        # output_json = json.dumps({str(k): v for k, v in data.items()}, indent=4, ensure_ascii=False)
                        # st.text_area("Output JSON", output_json, height=300)

                except json.JSONDecodeError:
                    st.error("Format data tidak valid! Harap masukkan data dalam format JSON.", icon="⚠️")
            else:
                st.warning("Anda belum memasukkan data.", icon="⚠️")

    with tabs[1]:
        st.subheader("Riwayat Rolling")
        if history:
            selected_date = st.selectbox("Pilih Tanggal Rolling", list(history.keys()))
            if selected_date:
                # st.write(f"\n**Jadwal pengambilan usus kotor {format_date(datetime.strptime(selected_date, '%Y-%m-%d'), format='full', locale='id')}**")
                
                # Menampilkan hasil rolling dalam format JSON
                st.subheader("Hasil Rolling")
                history_json = json.dumps(history[selected_date], indent=4, ensure_ascii=False)
                st.text_area(" ", history_json, height=300)
                
                if st.button("Hapus Riwayat Tanggal Ini", type="secondary"):
                    del history[selected_date]
                    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        json.dump(history, f, indent=4, ensure_ascii=False)
                    st.experimental_rerun()
        else:
            st.write("Belum ada data rolling yang tersimpan.")

if selection == "Phalosari Unggul Jaya" and selection != "--Pilih Perusahaan--":
    # Data lengkap
    data = {
        "1": "Pak Zainuri", "2": "Bu Nur", "3": "Bu Nur", "4": "Pak Lukman",
        "5": "Bu Yuni", "6": "Bu Sujadmi", "7": "Pak Zainuri", "8": "Pak Sudarsono",
        "9": "Pemuda 1", "10": "Pak Lukman", "11": "Pak Ferry", "12": "Pemuda 1",
        "13": "Pak Sudarsono", "14": "Pak Zainuri", "15": "Bu Nur", "16": "Bu Wulan",
        "17": "Bu Yuni", "18": "Pemuda 2", "19": "Pak Ferry", "20": "Pak Zainuri",
        "21": "Bu Nur", "22": "Pak Sudarsono", "23": "Pak Zainuri", "24": "Bu Yuni",
        "25": "Pak Ferry", "26": "Pemuda 1", "27": "Pak Zainuri", "28": "Pak Zainuri",
        "29": "Bu Nur", "30": "Paduka", "31": "Pak David", "32": "Pemuda 2",
        "33": "Pak Ferry", "34": "Pak Sudarsono", "35": "Paduka", "36": "Pak David",
        "37": "Bu Via", "38": "Bu Wulan", "39": "Pak Sudarsono", "40": "Pak Dicky",
        "41": "Bu Via", "42": "Pak Bowo", "43": "Bu Wulan", "44": "Pak Faizal",
        "45": "Pak Bowo", "46": "Bu Wulan", "47": "Pak Dicky", "48": "Pak Bowo",
        "49": "Pak Faizal", "50": "Pak Bowo", "51": "Formaju"
    }

    col1, col2 = st.columns([1, 4])  # rasio 1:4 agar gambar lebih kecil dari teks

    with col1:
        st.image("logo puj.png", width=130)  # ganti dengan path ke file gambar kamu

    with col2:
        st.markdown("<h1 style='margin-bottom: 0;'>Phalosari Unggul Jaya</h1>", unsafe_allow_html=True)
    # Jumlah_Rit_Libur = st.number_input("Jumlah Rit Libur:", min_value=0, max_value=51, value=0)
    awal = st.number_input("Rit Libur Awal:", min_value=0, max_value=51, value=0)
    akhir = st.number_input("Rit Libur Akhir:", min_value=0 , max_value=51, value=0)

    # Ambil tanggal dari input
    tanggal = st.date_input("Pilih tanggal:", value=datetime.date.today())

    # Mapping nama hari ke Bahasa Indonesia
    hari_indo = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }

    # Ambil nama hari dalam bahasa Indonesia
    hari = hari_indo[tanggal.strftime('%A')]

    # Tampilkan tanggal dengan tanda *
    st.markdown(f"<p>*{hari}, {tanggal.strftime('%d / %m / %Y')}*</p>", unsafe_allow_html=True)
    # Tampilkan keterangan libur
    st.markdown(f"Libur rit {awal} s/d {akhir}")


    # Step 1: Buat daftar key libur
    libur_keys = []
    if awal <= akhir:
        libur_keys = list(range(awal, akhir + 1))
    else:
        libur_keys = list(range(awal, 52)) + list(range(1, akhir + 1))

    # Step 2: Buat daftar rolling_keys dari semua key yang tidak libur (dalam urutan rotasi)
    total_keys = list(range(1, 52))  # 1-51
    # Rotasi dimulai dari (akhir + 1)
    start = (akhir % 51) + 1
    rotated_keys = total_keys[start - 1:] + total_keys[:start - 1]

    # Filter yang bukan libur
    rolling_keys = [k for k in rotated_keys if k not in libur_keys]


    # Step 3: Ambil nama dari rolling_keys
    rolling_result = [(index + 1, str(k), data[str(k)]) for index, k in enumerate(rolling_keys)]

    # Step 4: Bagi hasil rolling sesuai ketentuan:
    # - RPA 1 == RPA 2
    # - RPB ≈ setengah dari RPA 1 (boleh kurang/lebih 1)

    total_data = len(rolling_result)

    def cari_n_terbaik(total):
        for n in range(total // 2, 0, -1):
            sisa = total - 2 * n
            if abs(sisa - n // 2) <= 1:  # RPB ≈ setengah dari RPA, toleransi ±1
                return n, sisa
        return 0, 0

    rpa_len, rpb_len = cari_n_terbaik(total_data)

    # Potong data sesuai jumlah
    blok1 = rolling_result[:rpa_len]
    blok2 = rolling_result[rpa_len:rpa_len + rpa_len]
    blok3 = rolling_result[rpa_len + rpa_len:rpa_len + rpa_len + rpb_len]

    # Fungsi tampilkan blok (nomor urut mulai dari 1 di tiap blok)
    def tampilkan_semua_blok(blok_data):
        hasil = ""
        for judul, blok in blok_data:
            hasil += f"<span>&#42;{judul}&#42;</span><br>"
            for i, (_, key, nama) in enumerate(blok, start=1):
                hasil += f"{i}/{key}. {nama}<br>"
        st.markdown(hasil, unsafe_allow_html=True)



    tampilkan_semua_blok([
        ("RPA 1 PUJ - WSF (DO)", blok1),
        ("RPA 2 PUJ - WSF (DO)", blok2),
        ("RPB PUJ", blok3)
    ])
