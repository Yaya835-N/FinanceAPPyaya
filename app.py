import os
import time
import pandas as pd
import streamlit as st
import requests
from pathlib import Path

CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
SERVICE_NAME = os.getenv("SERVICE_NAME", "apotek-price-streamlit")
SERVICE_ID = os.getenv("SERVICE_ID", SERVICE_NAME + "-" + str(int(time.time())))
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8501))

DATA_PATH = Path(__file__).parent / "data" / "obat.csv"

st.set_page_config(page_title="Harga Obat Apotek", layout="wide")

def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame(columns=["kode", "nama", "sediaan", "stok", "harga"])

def save_data(df):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

def register_to_consul():
    try:
        url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
        payload = {
            "Name": SERVICE_NAME,
            "ID": SERVICE_ID,
            "Address": "localhost",
            "Port": SERVICE_PORT,
            "Tags": ["streamlit", "apotek"],
            "Check": {
                "HTTP": f"http://localhost:{SERVICE_PORT}/",
                "Interval": "10s",
                "Timeout": "3s"
            }
        }
        requests.put(url, json=payload, timeout=2)
    except:
        pass

try:
    register_to_consul()
except:
    pass

st.title("Daftar Harga Obat Apotek")

df = load_data()

col_list, col_form = st.columns([2, 1])

with col_list:
    st.subheader("Daftar Obat")
    q = st.text_input("Cari obat")

    if q:
        filtered = df[df["nama"].str.contains(q, case=False)]
    else:
        filtered = df

    st.dataframe(filtered)

with col_form:
    st.subheader("Tambah/Edit")
    with st.form("form"):
        kode = st.text_input("Kode")
        nama = st.text_input("Nama")
        sediaan = st.selectbox("Sediaan", ["Tablet", "Kapsul", "Sirup", "Injeksi", "Salep"])
        stok = st.number_input("Stok", min_value=0, step=1)
        harga = st.number_input("Harga", min_value=0, step=100)

        submitted = st.form_submit_button("Simpan")

    if submitted:
        if kode == "":
            st.warning("Kode wajib diisi")
        else:
            if kode in df["kode"].astype(str).values:
                df.loc[df["kode"] == kode, ["nama", "sediaan", "stok", "harga"]] = [nama, sediaan, stok, harga]
            else:
                df = df.append(
                    {"kode": kode, "nama": nama, "sediaan": sediaan, "stok": stok, "harga": harga},
                    ignore_index=True
                )
            save_data(df)
            st.success("Disimpan")

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Unduh CSV", csv, "daftar_obat.csv", "text/csv")

st.sidebar.write("Jumlah obat:", len(df))
st.sidebar.write("Total stok:", int(df["stok"].sum()))
