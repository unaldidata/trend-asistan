import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time

# Sayfa ayarları
st.set_page_config(page_title="Trend Ürün + Walmart Fiyat Dashboard", layout="wide")
st.title("📊 Keepa Trend Analiz + Walmart Fiyat Dashboard")

# --- Excel yükleme ---
uploaded_file = st.file_uploader("Lütfen Keepa Excel dosyanızı yükleyin (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    st.success(f"✅ {uploaded_file.name} yüklendi.")

    # Stokta olan ürünleri filtrele
    if "amazon_offer" in df.columns:
        stokta_olan = df[df["amazon_offer"].str.contains("in stock and shippable", case=False, na=False)]
    else:
        stokta_olan = df

    # Trend ürünleri sırala
    trend_urunler = stokta_olan.sort_values(by="Sales Rank: 30 days avg.", ascending=False).head(10)

    # Keepa linki
    if "url_keepa" in trend_urunler.columns:
        trend_urunler["Keepa Linki"] = trend_urunler["url_keepa"].apply(
            lambda x: f'<a href="{x}" target="_blank">🔗 Keepa Sayfası</a>' if pd.notna(x) else ""
        )
    else:
        trend_urunler["Keepa Linki"] = ""

    # Trend tablosu
    kolonlar_goster = [c for c in ["ASIN", "Title", "Brand", "Sales Rank: 30 days avg.", "Keepa Linki"] if c in trend_urunler.columns]
    st.markdown("### 🔝 En Trend 10 Ürün")
    st.write(trend_urunler[kolonlar_goster].to_html(escape=False, index=False), unsafe_allow_html=True)

    # Trend grafiği
    st.subheader("📈 Trend Grafiği (Sales Rank)")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(trend_urunler["Title"], trend_urunler["Sales Rank: 30 days avg."], color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel("Sales Rank: 30 days avg.")
    ax.set_ylabel("Ürün Adı")
    ax.set_title("Son 30 Günde En Trend 10 Ürün")
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("💲 Walmart Fiyat Analizi (Tek Ürün)")

    # SerpAPI Key
    serpapi_key = "c95ac986901e516c9b5dbdc7be961344c2b186c83b5192dc22e0a67842a5001e"

    # Kullanıcıdan ürün inputu
    urun_input = st.text_input("Fiyatını görmek istediğiniz trend ürün adını girin:")

    if urun_input and serpapi_key:
        # Önce Excel’deki trend ürünler arasında var mı kontrol et
        urun_df = trend_urunler[trend_urunler["Title"].str.contains(urun_input, case=False, na=False)]
        if urun_df.empty:
            st.warning("⚠️ Bu ürün trend ürünler listesinde bulunamadı.")
        else:
            # Walmart fiyat çekme (SerpAPI)
            row = urun_df.iloc[0]
            fiyat_info = {"Ürün": row["Title"][:60]}

            try:
                r = requests.get(
                    "https://serpapi.com/search.json",
                    params={
                        "engine": "walmart",
                        "query": row["Title"],
                        "api_key": serpapi_key
                    },
                    timeout=10
                )
                data = r.json()
                if "shopping_results" in data and data["shopping_results"]:
                    item = data["shopping_results"][0]
                    fiyat_info["Fiyat ($)"] = item.get("price", "Walmart’da bulunamadı")
                    fiyat_info["Link"] = item.get("link", "")
                else:
                    fiyat_info["Fiyat ($)"] = "Walmart’da bulunamadı"
                    fiyat_info["Link"] = ""
            except Exception:
                fiyat_info["Fiyat ($)"] = "API hatası"
                fiyat_info["Link"] = ""

            walmart_df = pd.DataFrame([fiyat_info])
            walmart_df["Link"] = walmart_df["Link"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Walmart Sayfası</a>' if x else "")
            st.dataframe(walmart_df)

else:
    st.info("📂 Lütfen önce bir Excel dosyası yükleyin.")
