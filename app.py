import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.data_utils import fetch_prices
from src.data_utils import fetch_rss
from src.fake_users import generate_fake_users
from src.email_utils import send_email

st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("📈 Trading Data Strategy Dashboard with Python")

symbols = ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"]

def build_email_body(user_row, df, sym):
    overbought = (df["RSI"] > 70).sum()
    oversold = (df["RSI"] < 30).sum()
    rss_df = fetch_rss("https://finance.yahoo.com/rss/headline?s=" + sym, symbol=sym)
    if not rss_df.empty:
        news_list = "\n".join([f"- {t}" for t in rss_df["title"].head(15)])
    else:
        news_list = "- Keine Nachrichten verfügbar"

    body = f"""
    Hallo {user_row['Name']},

    Hier sind die neuesten Finanznachrichten und RSI-Signale für {sym}:

    - RSI > 70: {overbought} Tage
    - RSI < 30: {oversold} Tage

    📢 Finanznachrichten {sym}:
    {news_list}

    Viele Grüße,  
    Trading Dashboard
    """
    return body
    
# 一次性抓取所有股票数据
with st.spinner("Loading..."):
    data = fetch_prices(symbols, start="2024-01-01", interval="1d")
st.success("✅ Data Loaded")

sym = st.sidebar.selectbox("Aktien auswählen:", symbols)

df = data[data["Symbol"] == sym]

menu = st.sidebar.radio(
    "Analysebereich auswählen:",
    ["Preisentwicklung (Candlestick + EMA)",
     "RSI-Signale",
     "Volatilitätsvergleich (ATR)",
     "Finanznachrichten (RSS)",
     "Benutzeranalyse (Fake Users)",
     "Zusammenfassung"]
)

# 价格走势
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

# ATR 
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


# RSI
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

# Finanznachrichten (RSS) 
elif menu == "Finanznachrichten (RSS)":
    st.markdown("## 📰 Finanznachrichten (RSS)")

    rss_df = fetch_rss("https://finance.yahoo.com/rss/headline?s=" + sym, symbol=sym)

    if not rss_df.empty:
        selected_news = st.selectbox("Wählen Sie eine Nachricht:", rss_df["title"].tolist())

        news_row = rss_df[rss_df["title"] == selected_news].iloc[0]
        st.write(f"**{news_row['title']}**")
        st.write(f"📅 {news_row['published_at']}")
        st.write(f"Sentiment Score: {news_row['sentiment_score']}")
    else:
        st.warning("⚠️ Keine Nachrichten verfügbar.")

#  Benutzeranalyse (Fake Users) 
elif menu == "Benutzeranalyse (Fake Users)":
    st.markdown("## 👤 Benutzeranalyse (Fake Users)")

    if "users_df" not in st.session_state:
        st.session_state["users_df"] = generate_fake_users(50)
    
    users_df = st.session_state["users_df"]

    selected_user = st.selectbox("Wählen Sie einen Benutzer:", users_df["Name"].tolist())

    user_row = users_df[users_df["Name"] == selected_user].iloc[0]

    st.write(f"**Name:** {user_row['Name']}")
    st.write(f"**Alter:** {user_row['Alter']}")
    st.write(f"**Geschlecht:** {user_row['Geschlecht']}")
    st.write(f"**Nationalität:** {user_row['Nationalität']}")
    st.write(f"**E-Mail:** {user_row['E-Mail']}")

    sym = st.selectbox("📈 Wählen Sie eine Aktie für die Nachrichten:", 
                       ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"])

    if st.button("📨 Send Email to This User"):
        subject = f"📊 Finanznachrichten & RSI-Signale für {sym}"
        body = build_email_body(user_row, df, sym)
        result = send_email(user_row["E-Mail"], subject, body)
        if result:
            with st.expander("✅ Email Content Preview", expanded=True):
                st.markdown(body)
        else:
            st.error(f"❌ Failed to send email to {user_row['E-Mail']}")

    gender_fig = px.pie(
        users_df,
        names="Geschlecht",
        title="📊 Geschlechterverteilung",
        color="Geschlecht",
        color_discrete_map={"Männlich": "#4F81BD", "Weiblich": "#C0504D"}
    )
    st.plotly_chart(gender_fig, use_container_width=True)

    bins = [0, 30, 40, 50, 60, 70, 80, 120]
    labels = ["18-30", "31-40", "41-50", "51-60", "61-70", "71-80", "80+"]

    users_df["AgeGroup"] = pd.cut(users_df["Alter"], bins=bins, labels=labels, right=True)

    age_group_counts = users_df["AgeGroup"].value_counts().sort_index()

    age_fig = px.bar(
        age_group_counts,
        x=age_group_counts.index,
        y=age_group_counts.values,
        title="📊 Altersverteilung nach Altersgruppen",
        color=age_group_counts.index,
        color_discrete_map={
            "18-30": "#4F81BD",  # muted blue
            "31-40": "#C0504D",  # muted red
            "41-50": "#9BBB59",  # muted green
            "51-60": "#8064A2",  # muted purple
            "61-70": "#4BACC6",  # teal
            "71-80": "#F79646",  # soft orange
            "80+":   "#7F7F7F"   # gray
        }
    )

    st.plotly_chart(age_fig, use_container_width=True)

# Fazit 
elif menu == "Zusammenfassung":
    st.markdown("## 🎯 Fazit")
    st.success("**Technologie-/Wachstumsaktien (AAPL, TSLA, NVDA, AMZN, META, NFLX)** → besser geeignet für Scalping")
    st.info("**Blue-Chip/Stabile Aktien (JNJ, KO, PG)** → besser geeignet für Buy & Hold")

    st.write("👇 Letzte Daten (zur Kontrolle):")
    st.write(df.tail())


def run_email_job(users_df, data, symbols):
    for _, user_row in users_df.iterrows():
        for sym in symbols:
            df = data[data["Symbol"] == sym]
            if df.empty:
                continue
            subject = f"📊 Finanznachrichten & RSI-Signale für {sym}"
            body = build_email_body(user_row, df, sym)
            send_email(user_row["E-Mail"], subject, body)
