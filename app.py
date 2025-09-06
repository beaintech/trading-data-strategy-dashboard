import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.data_utils import fetch_prices

# 页面配置
st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("📈 Trading Data Strategy Dashboard with Python")

# Sidebar for stock selection
symbols = ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"]

# 一次性抓取所有股票数据
data = fetch_prices(symbols, start="2025-01-01", interval="1d")

# 用户选择当前股票（全局唯一）
sym = st.sidebar.selectbox("Aktien auswählen:", symbols)

# 当前股票数据
df = data[data["Symbol"] == sym]

# 左侧菜单
menu = st.sidebar.radio(
    "Analysebereich auswählen:",
    ["Preisentwicklung (Candlestick + EMA)",
     "RSI-Signale",
     "Volatilitätsvergleich (ATR)",
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
    # === 平均 ATR & RSI ===
    atr_summary = data.groupby("Symbol")["ATR"].mean().reset_index()
    rsi_summary = data.groupby("Symbol")["RSI"].mean().reset_index()

    # === 金叉 / 死叉 ===
    crossover_stats = []
    for s in symbols:
        df_s = data[data["Symbol"] == s].copy()
        df_s["Crossover"] = (df_s["EMA_fast"] > df_s["EMA_slow"]).astype(int)
        df_s["Signal"] = df_s["Crossover"].diff()
        golden = (df_s["Signal"] == 1).sum()
        death = (df_s["Signal"] == -1).sum()
        crossover_stats.append({"Symbol": s, "Golden Cross": golden, "Death Cross": death})

    cross_summary = pd.DataFrame(crossover_stats)

    # === RSI 超买 / 超卖天数 ===
    rsi_extremes = []
    for s in symbols:
        df_s = data[data["Symbol"] == s]
        overbought = (df_s["RSI"] > 70).sum()
        oversold = (df_s["RSI"] < 30).sum()
        rsi_extremes.append({"Symbol": s, "RSI > 70 Days": overbought, "RSI < 30 Days": oversold})

    rsi_extremes = pd.DataFrame(rsi_extremes)

    # === 合并所有表格 ===
    summary = atr_summary.merge(rsi_summary, on="Symbol") \
                         .merge(cross_summary, on="Symbol") \
                         .merge(rsi_extremes, on="Symbol")
    summary.rename(columns={"ATR": "Avg ATR", "RSI": "Avg RSI"}, inplace=True)

    # --- 柱状图 (ATR) ---
    fig = px.bar(
        atr_summary,
        x="Symbol",
        y="ATR",
        color="ATR",
        color_continuous_scale=["red", "orange", "green"]
    )
    fig.update_layout(title="Volatilitätsvergleich (ATR)", xaxis_title="Symbol", yaxis_title="ATR")
    st.plotly_chart(fig, use_container_width=True)

    # --- 矩阵表格 ---
    st.markdown("### 📊 Vergleichstabelle (ATR, RSI, Crossovers, RSI-Extremes)")
    st.dataframe(summary)


# ========== 3. RSI ==========
elif menu == "RSI-Signale":
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI"))
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

    fig.update_layout(title=f"RSI-Signale - {sym}", yaxis=dict(range=[0,100]))
    st.plotly_chart(fig, use_container_width=True)
    overbought = (df["RSI"] > 70).sum()
    oversold = (df["RSI"] < 30).sum()
    st.metric("RSI > 70 (Overbought)", overbought)
    st.metric("RSI < 30 (Oversold)", oversold)

# ========== 4. Fazit ==========
elif menu == "Zusammenfassung":
    st.markdown("## 🎯 Fazit")
    st.success("**Technologie-/Wachstumsaktien (AAPL, TSLA, NVDA, AMZN, META, NFLX)** → besser geeignet für Scalping")
    st.info("**Blue-Chip/Stabile Aktien (JNJ, KO, PG)** → besser geeignet für Buy & Hold")

    st.write("👇 Letzte Daten (zur Kontrolle):")
    st.write(df.tail())
