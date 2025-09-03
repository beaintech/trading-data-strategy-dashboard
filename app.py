import streamlit as st
import plotly.graph_objects as go
from data_utils import fetch_prices

# 页面配置
st.set_page_config(page_title="Scalping Dashboard", layout="wide")
st.title("📈 Trading Data Strategy Dashboard with Python - Scalping vs Buy & Hold")

# Sidebar for stock selection
symbols = ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"]

# 一次性抓取所有股票数据
data = fetch_prices(symbols, start="2025-01-01", interval="1d")

# 用户选择当前股票（全局唯一）
sym = st.sidebar.selectbox("选择股票:", symbols)

# 当前股票数据
df = data[data["Symbol"] == sym]

# 左侧菜单
menu = st.sidebar.radio(
    "Analysebereich auswählen:",
    ["Preisentwicklung (Candlestick + EMA)",
     "Volatilitätsvergleich (ATR)",
     "RSI-Signale",
     "Zusammenfassung"]
)

# ========== 1. 价格走势 ==========
if menu == "Preisentwicklung (Candlestick + EMA)":
    fig = go.Figure(data=[
        go.Candlestick(x=df["Date"],
                       open=df["Open"],
                       high=df["High"],
                       low=df["Low"],
                       close=df["Close"],
                       name="Price"),
        go.Scatter(x=df["Date"], y=df["EMA_fast"], line=dict(color="blue"), name="EMA Fast"),
        go.Scatter(x=df["Date"], y=df["EMA_slow"], line=dict(color="red"), name="EMA Slow")
    ])
    fig.update_layout(title=f"📊 Preisentwicklung - {sym}")
    st.plotly_chart(fig, use_container_width=True)

# ========== 2. ATR ==========
elif menu == "Volatilitätsvergleich (ATR)":
    atr_summary = data.groupby("Symbol")["ATR"].mean().reset_index()

    fig = go.Figure(data=[
        go.Bar(x=atr_summary["Symbol"], y=atr_summary["ATR"], marker_color="orange")
    ])
    fig.update_layout(title="平均波动率 (ATR)", xaxis_title="Symbol", yaxis_title="ATR")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("📌 **Je höher der durchschnittliche ATR, desto größer die Volatilität → besser geeignet für Scalping**")


# ========== 3. RSI ==========
elif menu == "RSI-Signale":
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI"))
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

    fig.update_layout(title=f"RSI 信号 - {sym}", yaxis=dict(range=[0,100]))
    st.plotly_chart(fig, use_container_width=True)

# ========== 4. 总结 ==========
elif menu == "Zusammenfassung":
    st.markdown("## 🎯 Fazit")
    st.success("**Technologie-/Wachstumsaktien (AAPL, TSLA, NVDA, AMZN, META, NFLX)** → besser geeignet für Scalping")
    st.info("**Blue-Chip/Stabile Aktien (JNJ, KO, PG)** → besser geeignet für Buy & Hold")

    st.write("👇 Letzte Daten (zur Kontrolle):")
    st.write(df.tail())
