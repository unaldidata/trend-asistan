# walmart_app.py

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

st.set_page_config(page_title="Walmart Ürün Fiyat Takip", layout="wide")

st.title("🛒 Walmart Ürün Fiyat Takip App")

# Kullanıcıdan arama sorgusu al
arama = st.text_input("Aramak istediğiniz ürün adı:", "Orient Therapy Lavender Gift Box")

if st.button("Ara"):
    st.info("🔹 Ürünler çekiliyor, lütfen bekleyin...")

    # Chrome headless ayarları
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # webdriver-manager ile ChromeDriver otomatik yönetimi
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = f"https://www.walmart.com/search?q={arama.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)  # Sayfanın yüklenmesi için basit bekleme

    urunler_list = []
    urunler = driver.find_elements(By.CSS_SELECTOR, "div.search-result-gridview-item-wrapper")

    for u in urunler:
        try:
            baslik = u.find_element(By.CSS_SELECTOR, "a.product-title-link span").text
            fiyat = u.find_element(By.CSS_SELECTOR, "span.price-characteristic").get_attribute("content")
            urunler_list.append({"Başlık": baslik, "Fiyat (USD)": fiyat})
        except:
            continue

    driver.quit()

    if urunler_list:
        df = pd.DataFrame(urunler_list)
        st.success(f"✅ {len(df)} ürün bulundu!")
        st.dataframe(df)
        excel_file = f"{arama.replace(' ','_')}_walmart.xlsx"
        df.to_excel(excel_file, index=False)
        st.download_button("📥 Excel olarak indir", data=open(excel_file, "rb"), file_name=excel_file)
    else:
        st.warning("⚠️ Ürün bulunamadı veya sayfa yüklenmedi.")
