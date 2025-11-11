import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Excel'i oku
df = pd.read_csv("keepa_product_links.csv")  # Dosya adını kendi Excel'inle değiştir
# Eğer sütun adı 'Url:Keepa' ise
df = df.rename(columns={"URL: Keepa": "url_keepa"})

results = []

for url in df["url_keepa"].head(10):  # İlk 10 ürün
    try:
        print(f"Çekiliyor: {url}")
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        price_tag = soup.select_one(".a-price-whole")  # Keepa / Amazon fiyat etiketi
        price = price_tag.text.strip() if price_tag else "Fiyat bulunamadı"
        
        results.append({"url_keepa": url, "price": price})
        time.sleep(1)
    except Exception as e:
        results.append({"url_keepa": url, "price": f"Hata: {e}"})

# Sonuçları Excel olarak kaydet
df_out = pd.DataFrame(results)
df_out.to_excel("fiyat_sonuc.xlsx", index=False)
print("✅ Fiyatlar alındı, 'fiyat_sonuc.xlsx' kaydedildi")
