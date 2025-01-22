import streamlit as st
import json
from collections import deque
from datetime import datetime, timedelta
from babel.dates import format_date
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
    today = datetime.now()
    if today.weekday() == 5:  # 5 berarti Sabtu
        target_date = today + timedelta(days=2)  # Lompat ke Senin
    else:
        target_date = today + timedelta(days=1)
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
            st.text_area("Output JSON", history_json, height=300)
            
            if st.button("Hapus Riwayat Tanggal Ini", type="secondary"):
                del history[selected_date]
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=4, ensure_ascii=False)
                st.experimental_rerun()
    else:
        st.write("Belum ada data rolling yang tersimpan.")
