import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="📈 Trend Dashboard + Mail", layout="wide")
st.title("📊 Keepa Trend Dashboard + Otomatik Mail (SMTP)")

# 1️⃣ Excel yükleme
uploaded_file = st.file_uploader("Trend Ürün Excel dosyasını yükleyin (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    sira_sutun = "Sales Rank: 30 days avg."
    url_sutun = "url_keepa"

    if sira_sutun not in df.columns or url_sutun not in df.columns:
        st.error("❌ Gerekli sütunlar bulunamadı.")
        st.stop()

    # 2️⃣ Trend grafiği
    st.subheader("📈 Trend Grafiği")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["Title"], df[sira_sutun], color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel(sira_sutun)
    ax.set_ylabel("Ürün Adı")
    ax.set_title("Son 30 Günde En Trend Ürünler")
    st.pyplot(fig)

    # 3️⃣ Tıklanabilir Keepa linkleri
    st.subheader("🔗 Ürün Linkleri (Tıklayınca Keepa sayfası açılır)")
    for idx, row in df.iterrows():
        title = row["Title"]
        url = row[url_sutun]
        if pd.notna(url):
            st.markdown(f"- **{title}**: [Go to Keepa]({url})")
        else:
            st.markdown(f"- **{title}**: Link yok")

    # 4️⃣ En trend ürünü tespit et
    en_trend = df.sort_values(by=sira_sutun, ascending=False).iloc[0]
    title = en_trend["Title"]
    asin = en_trend.get("ASIN", "Bilinmiyor")
    brand = en_trend.get("Brand", en_trend.get("Product Group", "Bilinmiyor"))
    keepa_link = en_trend.get(url_sutun, "Link yok")
    sales_rank = en_trend[sira_sutun]

    st.success(f"📢 En trend ürün: {title} ({brand}), Sales Rank: {sales_rank}")

    # 5️⃣ Mail gönderme alanı (SMTP)
    st.subheader("📤 Trend Ürünü Mail ile Gönder (SMTP)")

    sender_email = st.text_input("Gönderen E-posta")
    sender_password = st.text_input("Gönderen E-posta App Password", type="password")
    receiver_email = st.text_area("Alıcı E-posta Adresleri (virgülle ayırın)")

    smtp_server = st.text_input("SMTP Sunucu", "smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)

    if st.button("📬 Mail Gönder"):
        if not sender_email or not sender_password or not receiver_email:
            st.error("❌ Lütfen tüm bilgileri doldurun.")
        else:
            try:
                # Mail içeriği
                subject = f"Trend Ürün Bildirimi: {title}"
                body = f"""
En trend ürün bilgisi:

Ürün: {title}
ASIN: {asin}
Marka / Grup: {brand}
Sales Rank (30 gün): {sales_rank}
Keepa Link: {keepa_link}
"""
                # SMTP bağlantısı
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)

                # Alıcı listesi
                receivers = [x.strip() for x in receiver_email.split(",") if x.strip()]
                for r in receivers:
                    msg = MIMEText(body)
                    msg['From'] = sender_email
                    msg['To'] = r
                    msg['Subject'] = subject
                    server.sendmail(sender_email, r, msg.as_string())

                server.quit()
                st.success(f"✅ E-posta başarıyla gönderildi {len(receivers)} alıcıya!")

            except Exception as e:
                st.error(f"❌ Mail gönderilemedi: {e}")

else:
    st.info("👆 Trend ürün Excel dosyanızı yükleyin.")
