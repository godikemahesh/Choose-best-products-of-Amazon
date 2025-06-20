import streamlit as st
from find_product import get_data, d_prompt
import re
import pandas as pd
import plotly.express as px

# ---------------------------------- CONFIG -------------------------------
st.set_page_config(page_title="SURAJ® OptiChoice", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #ffe6cc, #ffccf2, #d5ccff);
        color: #000000;
    }

    .main-title {
        font-size: 64px;
        text-align: center;
        background: linear-gradient(90deg, #ff5e62, #ff9966);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        margin-top: 20px;
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
        from { text-shadow: 0 0 10px #ff9a00; }
        to { text-shadow: 0 0 20px #ff6600, 0 0 30px #ff3300; }
    }

    .block {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    }

    h3 {
        color: #663399;
        font-size: 28px;
        margin-top: 30px;
    }

    .sidebar .sidebar-content {
        background-color: #f8f0ff !important;
    }

    .stButton>button {
        background-color: #ff7f50;
        color: white;
        border: None;
        border-radius: 8px;
        padding: 8px 20px;
        margin-top: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff5722;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🛍️ SURAJ® OptiChoice</div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:#444;'>Find the best product using smart comparison 🔍✨</h4>", unsafe_allow_html=True)

# ---------------------------- API STATUS ----------------------------
try:
    from find_product import check_scrapingbee_status
    status = check_scrapingbee_status()
    if status['status'] == 'connected':
        st.sidebar.success("✅ APP Connected")
    else:
        st.sidebar.error(f"❌ API Error: {status.get('message', 'Unknown error')}")
except:
    st.sidebar.warning("⚠️ ScrapingBee API not configured")

# ---------------------------- SESSION INIT ----------------------------
if "urls" not in st.session_state:
    st.session_state.urls = ["", ""]
if "content" not in st.session_state:
    st.session_state.content = []
if "figure" not in st.session_state:
    st.session_state.figure = []

# ---------------------------- ADD INPUT ----------------------------
def add_text_input():
    st.session_state.urls.append("")

st.sidebar.title("🔗 Paste Amazon URLs")

for i, url in enumerate(st.session_state.urls):
    st.session_state.urls[i] = st.sidebar.text_input(f"URL {i+1}", url, key=f"url_{i}")

# ---------------------------- PROCESSING FUNCTION ----------------------------
def generate():
    lst, title, rate, keys, values, urls = [], [], [], [], [], []

    for url in st.session_state.urls:
        if url:
            details, tit, rank = get_data(url)
            urls.append(url)
            title.append(tit)

            match = re.search(r"(\d\.\d) out of 5", rank)
            rate.append(float(match.group(1)) if match else 0)

            with open("specify.txt", "r+", encoding="utf-8") as ps:
                content = re.sub(r"â€Ž|â|€|Ž", "", ps.read())
                ps.truncate(0)
                lst.append(content)

                for k, v in details.items():
                    keys.append(k)
                    values.append(v)

                df = pd.DataFrame({'Name': keys, 'Value': values})
                st.session_state.content.append(("📦 " + tit, df))
                keys.clear()
                values.clear()

    my_text, _, sim = d_prompt(lst)

    st.session_state.content.append(("✅ Best Specifications", json_to_df(my_text)))

    df = pd.DataFrame({'Percentage': sim, 'Text': title, 'urls': urls}).sort_values(by='Percentage', ascending=False)
    df1 = pd.DataFrame({'rating': rate, 'Text': title, 'urls': urls}).sort_values(by='rating', ascending=False)

    st.session_state.content.append(("🏆 Ranking by Specifications", format_ranking(df)))
    st.session_state.content.append(("⭐ Ranking by Rating", format_ranking(df1)))

    fig1 = px.pie(values=rate, names=title, title="🌟 Rating Pie Chart")
    fig2 = px.pie(values=sim, names=title, title="📊 Specifications Pie Chart")

    st.session_state.figure.extend([fig1, fig2])

def json_to_df(data):
    import json
    try:
        if isinstance(data, str):
            data = json.loads(data)
        return pd.DataFrame(list(data.items()), columns=["Feature", "Value"])
    except:
        return pd.DataFrame([["Parse Error", str(data)]], columns=["Feature", "Value"])

def format_ranking(df):
    output = ""
    for i, row in enumerate(df.itertuples()):
        output += f"{i+1}) [{row.Text}]({row.urls})  \n"
    return output

# ---------------------------- BUTTONS ----------------------------
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add URL"):
            add_text_input()
    with col2:
        if st.button("🔁 Rerun"):
            generate()
    with col3:
        if st.button("🚀 Compare"):
            generate()

# ---------------------------- DISPLAY OUTPUT ----------------------------
for header, content in st.session_state.content:
    with st.container():
        st.markdown(f"<div class='block'><h3>{header}</h3>", unsafe_allow_html=True)
        if isinstance(content, str):
            st.markdown(content)
        else:
            st.dataframe(content, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.session_state.content.clear()

for fig in st.session_state.figure:
    st.plotly_chart(fig, use_container_width=True)

st.session_state.figure.clear()
