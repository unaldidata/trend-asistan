# app_trend.py
# Proaktif Pazar Trend Asistanı – Streamlit App

import os
os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
os.environ["PYARROW_INVALID_OBJECTS"] = "ignore"


import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------
# 1. Dosya yolları
# ---------------------------

BASE_DIR = Path(__file__).parent

TREND_FILE = BASE_DIR / "trend_urunler.xlsx"
TAKIP_FILE = BASE_DIR / "urun_takip_ilk10.xlsx"
KEEPA_FILE = BASE_DIR / "keepa_product_links.csv"

# ---------------------------
# 2. Veri yükleme fonksiyonları
# ---------------------------

@st.cache_data
def load_trend():
    if TREND_FILE.exists():
        return pd.read_excel(TREND_FILE)
    return pd.DataFrame()

@st.cache_data
def load_takip():
    if TAKIP_FILE.exists():
        return pd.read_excel(TAKIP_FILE)
    return pd.DataFrame()

@st.cache_data
def load_keepa():
    if KEEPA_FILE.exists():
        return pd.read_csv(KEEPA_FILE)
    return pd.DataFrame()

# ---------------------------
# 3. Ana arayüz
# ---------------------------

def main():
    st.set_page_config(
        page_title="Trend Asistanı – 7. Sprint",
        layout="wide"
    )

    st.title("📈 Proaktif Pazar Trend Asistanı")
    st.markdown(
        "Bu arayüz, 7 nolu sprint kapsamında hazırlanan **TrendAsistan.ipynb** "
        "notebook’undaki analizlerin web versiyonudur."
    )

    # Sidebar
    st.sidebar.header("Ayarlar")
    dataset = st.sidebar.selectbox(
        "Görüntülenecek veri",
        ["trend_urunler", "urun_takip_ilk10", "keepa_product_links"]
    )

    # Veri seçimi
    if dataset == "trend_urunler":
        df = load_trend()
        st.subheader("📊 trend_urunler.xlsx")
    elif dataset == "urun_takip_ilk10":
        df = load_takip()
        st.subheader("📊 urun_takip_ilk10.xlsx")
    else:
        df = load_keepa()
        st.subheader("📊 keepa_product_links.csv")

    if df.empty:
        st.warning("Seçilen dosya bulunamadı veya boş görünüyor.")
        return

    # Basit filtreler (örnek)
    st.markdown("### Veri Önizleme")
    st.dataframe(df.head(50))

    st.markdown("### Temel Bilgiler")
    col1, col2, col3 = st.columns(3)
    col1.metric("Satır sayısı", f"{len(df):,}")
    col2.metric("Sütun sayısı", f"{df.shape[1]:,}")
    col3.metric("Boş değer sayısı", int(df.isna().sum().sum()))

    with st.expander("Sütun bilgileri"):
        st.write(df.dtypes)

    # Buradan sonrasına senin notebook’taki analiz/grafikler gelecek
    st.markdown("---")
    st.markdown("🔧 Notebook’taki özel analizler bu alanın altına taşınacak.")


if __name__ == "__main__":
    main()
