import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Sayfa ayarları
st.set_page_config(page_title="Trend Ürün + eBay Fiyat Dashboard", layout="wide")
st.title("📊 Keepa Trend Analiz + eBay Fiyat Dashboard")

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

    # Keepa linki ekle
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

    # --- eBay fiyat analizi ---
    st.markdown("---")
    st.subheader("💲 eBay Fiyat Analizi (İlk 5 Sonuç)")

    serpapi_key = "c95ac986901e516c9b5dbdc7be961344c2b186c83b5192dc22e0a67842a5001e"
    urun_input = st.text_input("Fiyatını görmek istediğiniz trend ürün adını girin:")

    if urun_input and serpapi_key:
        urun_df = trend_urunler[trend_urunler["Title"].str.contains(urun_input, case=False, na=False)]
        if urun_df.empty:
            st.warning("⚠️ Bu ürün trend ürünler listesinde bulunamadı.")
        else:
            row = urun_df.iloc[0]

            # eBay arama
            try:
                r = requests.get(
                    "https://serpapi.com/search.json",
                    params={
                        "engine": "ebay",
                        "_nkw": row["Title"],
                        "api_key": serpapi_key
                    },
                    timeout=10
                )
                data = r.json()

                if "organic_results" in data and data["organic_results"]:
                    results = []
                    for item in data["organic_results"][:5]:  # İlk 5 sonucu al
                        title = item.get("title", "Bilinmiyor")[:70]
                        price_data = item.get("price", {})
                        if isinstance(price_data, dict):
                            fiyat = price_data.get("raw") or price_data.get("extracted") or "Belirtilmemiş"
                        else:
                            fiyat = price_data or "Belirtilmemiş"

                        link = item.get("link", "")
                        results.append({
                            "Ürün": title,
                            "Fiyat ($)": fiyat,
                            "Link": f'<a href="{link}" target="_blank">🔗 eBay Sayfası</a>' if link else ""
                        })

                    ebay_df = pd.DataFrame(results)
                    st.write(ebay_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ eBay’de uygun ürün bulunamadı.")
            except Exception as e:
                st.error(f"API hatası: {e}")

else:
    st.info("📂 Lütfen önce bir Excel dosyası yükleyin.")
