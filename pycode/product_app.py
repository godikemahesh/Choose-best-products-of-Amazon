import streamlit as st
from find_product import get_data, d_prompt
import re
import pandas as pd
import plotly.express as px

# ---------------------------- 🎨 Page Styling ----------------------------
st.set_page_config(page_title="SURAJ® OptiChoice", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #f6d365, #fda085);
    }
    .centered-heading {
        text-align: center;
        background: linear-gradient(to right, #ff6a00, #ee0979);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 65px;
        font-weight: bold;
        margin-top: 0;
        animation: glow 2s infinite alternate;
    }
    @keyframes glow {
        from { text-shadow: 0 0 10px #f5a623; }
        to { text-shadow: 0 0 20px #f5a623, 0 0 30px #f39c12; }
    }
    .block {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    h3 {
        color: #6a11cb;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='centered-heading'>SURAJ® OptiChoice</h2>", unsafe_allow_html=True)
st.title("🛒 Choose Your Product Wisely")
st.write("Paste the Amazon product URLs below and get the best product recommendations based on ratings and specifications. 🚀")

# ---------------------------- ✅ API Status ----------------------------
try:
    from find_product import check_scrapingbee_status
    status = check_scrapingbee_status()
    if status['status'] == 'connected':
        st.sidebar.success("✅ ScrapingBee Connected")
    else:
        st.sidebar.error(f"❌ API Error: {status.get('message', 'Unknown error')}")
except:
    st.sidebar.warning("⚠️ ScrapingBee API not configured")

# ---------------------------- 🧠 Session State ----------------------------
if "urls" not in st.session_state:
    st.session_state.urls = ["", ""]
if "content" not in st.session_state:
    st.session_state.content = []
if "figure" not in st.session_state:
    st.session_state.figure = []

# ---------------------------- ➕ Add Input ----------------------------
def add_text_input():
    st.session_state.urls.append("")

st.sidebar.title("🔗 Enter URLs")

for i, url in enumerate(st.session_state.urls):
    st.session_state.urls[i] = st.sidebar.text_input(f"URL {i + 1}", url, key=f"url_{i}")

# ---------------------------- ⚙️ Generate Logic ----------------------------
def generate():
    lst, title, rate, keys, values, urls = [], [], [], [], [], []

    for i, url in enumerate(st.session_state.urls):
        if url != "":
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
                st.session_state.content.append(f"### 📦 {tit}")
                st.session_state.content.append(df)
                keys.clear()
                values.clear()

    my_text, all_texts, sim = d_prompt(lst)

    st.session_state.content.append("### ✅ Retrieved Best Specifications:")
    try:
        import json
        my_text = json.loads(my_text) if isinstance(my_text, str) else my_text
        best_df = pd.DataFrame(list(my_text.items()), columns=["Feature", "Value"])
    except:
        best_df = pd.DataFrame([["Could not parse", my_text]], columns=["Feature", "Value"])

    st.session_state.content.append(best_df)

    df = pd.DataFrame({'Percentage': sim, 'Text': title, 'urls': urls}).sort_values(by='Percentage', ascending=False)
    df1 = pd.DataFrame({'rating': rate, 'Text': title, 'urls': urls}).sort_values(by='rating', ascending=False)

    # Rankings
    st.session_state.content.append("<h3>🏆 Ranking by Specifications</h3>")
    for i, row in df.iterrows():
        st.session_state.content.append(f"{i+1}) [{row['Text']}]({row['urls']})")

    st.session_state.content.append("<h3>⭐ Ranking by Ratings</h3>")
    for i, row in df1.iterrows():
        st.session_state.content.append(f"{i+1}) [{row['Text']}]({row['urls']})")

    # Pie Charts
    fig = px.pie(values=rate, names=title, title="🌟 Ratings Pie Chart")
    fig2 = px.pie(values=sim, names=title, title="📊 Specifications Pie Chart")

    st.session_state.figure.append(fig)
    st.session_state.figure.append(fig2)

# ---------------------------- 🔘 Buttons ----------------------------
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add URL", key="button1"):
            add_text_input()
    with col3:
        if st.button("🚀 Process", key="button3"):
            generate()
    with col2:
        if st.button("🔄 Rerun", key="button2"):
            generate()

# ---------------------------- 📤 Display Output ----------------------------
for i in st.session_state.content:
    if isinstance(i, str) and "Ranking" in i:
        st.markdown(i, unsafe_allow_html=True)
    else:
        st.write(i)

st.session_state.content.clear()

for fig in st.session_state.figure:
    st.plotly_chart(fig)

st.session_state.figure.clear()
