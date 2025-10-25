# ==================================================
# 💹 STREAMLIT APP - ANALISIS SENTIMEN & NILAI TUKAR
# Dibuat oleh: Reza Febryadi
# ==================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import yfinance as yf
from datetime import datetime, timedelta

# =======================
# Fungsi bantu
# =======================
def get_news(query="nilai tukar rupiah inflasi", limit=8):
    """Scrape berita dari Google News"""
    url = f"https://news.google.com/search?q={query}&hl=id&gl=ID&ceid=ID:id"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    articles = soup.find_all('a', class_='JtKRv', limit=limit)
    return [a.text for a in articles if a.text]

def analyze_sentiment(headlines):
    """Analisis sentimen dari daftar berita"""
    results = []
    for text in headlines:
        score = TextBlob(text).sentiment.polarity
        if score > 0:
            label = "Positif"
        elif score < 0:
            label = "Negatif"
        else:
            label = "Netral"
        results.append({"Berita": text, "Sentimen": label, "Skor": round(score, 2)})
    return pd.DataFrame(results)

def get_currency_data(symbol="USDIDR=X", days=180):
    """Ambil data nilai tukar"""
    end = datetime.today()
    start = end - timedelta(days=days)
    data = yf.download(symbol, start=start, end=end)
    data["Inflasi (%)"] = data["Close"].pct_change() * 100
    return data

# =======================
# Tampilan Streamlit
# =======================
st.set_page_config(page_title="Sentimen & Nilai Tukar", layout="wide", page_icon="💹")

st.title("💹 Analisis Sentimen & Nilai Tukar Mata Uang Asing")
st.markdown(
    "Aplikasi interaktif untuk menganalisis **berita nilai tukar mata uang asing** "
    "dan **simulasi inflasi** berdasarkan perubahan harga harian. "
    "Dibuat dengan Streamlit, TextBlob, dan Yahoo Finance."
)

# --- Input user
col1, col2 = st.columns(2)

with col1:
    currency = st.selectbox(
        "Pilih Mata Uang:",
        {
            "USD (Dolar AS)": "USDIDR=X",
            "EUR (Euro)": "EURIDR=X",
            "JPY (Yen Jepang)": "JPYIDR=X",
            "SGD (Dolar Singapura)": "SGDIDR=X",
            "AUD (Dolar Australia)": "AUDIDR=X",
            "CNY (Yuan Tiongkok)": "CNYIDR=X",
        }
    )

with col2:
    days = st.slider("Periode Data (hari):", 30, 365, 180, 30)

mata_uang = currency[:3]
st.divider()

# =======================
# Bagian Berita & Sentimen
# =======================
st.subheader(f"📰 Berita Terkini Tentang {mata_uang}")
news = get_news(f"nilai tukar {mata_uang} rupiah inflasi")

if not news:
    st.warning("Tidak ditemukan berita terbaru untuk kata kunci ini.")
else:
    for n in news:
        st.write("•", n)

    df_sent = analyze_sentiment(news)
    st.subheader("📊 Analisis Sentimen Berita")
    st.dataframe(df_sent, use_container_width=True)

# =======================
# Grafik Nilai Tukar
# =======================
st.subheader("💹 Grafik Nilai Tukar & Simulasi Inflasi")

data = get_currency_data(currency, days)
if not data.empty:
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    ax[0].plot(data.index, data["Close"], label=f"Nilai Tukar {currency}", color="#1E88E5")
    ax[0].set_title(f"Nilai Tukar {currency} (Rupiah per unit)")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(data.index, data["Inflasi (%)"], color="orange", label="Perubahan Harian (%)")
    ax[1].set_title("Simulasi Inflasi Berdasarkan Nilai Tukar")
    ax[1].grid(True)
    ax[1].legend()

    st.pyplot(fig)
else:
    st.error("Data nilai tukar tidak ditemukan.")

st.divider()
st.caption("Dibuat oleh **Reza Febryadi** | Data dari Yahoo Finance & Google News | © 2025")
