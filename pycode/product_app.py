import streamlit as st
from .find_product import get_data,d_prompt
import re
import pandas as pd
from .gpt_data import lemitization
import plotly.express as px

#path=r"C:\Users\mahes\Downloads\suraj logo.png"
#st.logo(path)
st.markdown(
    """
    <style>
    .centered-heading {
        text-align: center;
        color: yellow;
        font-size: 65px;
        margin-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h2 class='centered-heading'>SURAJ® OptiChoice</h2>", unsafe_allow_html=True)
st.title("Choose Your Product")
#st.write("<h2 style='text-align: center;color: yellow;font-size:65px;'>SURAJ® OptiChoice</h2>", unsafe_allow_html=True)
st.write("Paste the Urls and get to choose best products in the amazon..\n")


if "urls" not in st.session_state:
    st.session_state.urls = ["", ""]  # Start with one empty URL field
if "content" not in st.session_state:
    st.session_state.content = []
if "figure" not in st.session_state:
    st.session_state.figure=[]

# Function to add a new text input
def add_text_input():
    st.session_state.urls.append("")  # Add an empty string for a new URL

# Sidebar layout
st.sidebar.title("Enter URLs here")

# Display text inputs and collect user input
for i, url in enumerate(st.session_state.urls):
    st.session_state.urls[i] = st.sidebar.text_input(f"URL {i + 1}", url, key=f"url_{i}")



def generate():
    lst=[]
    title=[]
    rate=[]
    keys=[]
    values=[]
    urls=[]
    for i ,url in enumerate(st.session_state.urls):
        if st.session_state.urls[i]!="":
            details,tit,rank=get_data(st.session_state.urls[i])
            urls.append(st.session_state.urls[i])
            pattern2 = r"(\d.\d) out of 5"
            rank=re.findall(pattern2,rank)
            title.append(tit)
            cnt=0
            for i in rank[0]:
                if cnt==0:
                    rate.append(eval(str(i)))
                    cnt+=1
            with open("specify.txt", "r+",encoding="utf-8") as ps:
                content = ps.read()
                ps.truncate(0)
                data = re.sub(r"â€Ž|â|€|Ž", "", content)
                lst.append(data)
                for key, value in details.items():
                    keys.append(key)
                    values.append(value)

                dataf = pd.DataFrame({
                    'Name': keys,
                    'Value': values
                })

                st.session_state.content.append(f"***{tit}:***")
                st.session_state.content.append(dataf)
                keys.clear()
                values.clear()
    adata=lemitization(lst)
    my_text,all_texts,sim=d_prompt(adata)
    st.session_state.content.append(f"retrived best specifications:\n\n{my_text}")
    df = pd.DataFrame({
        'Percentage': sim,
        'Text': title,
        "urls":urls
    })

    df1 = pd.DataFrame({
        'rating': rate,
        'Text': title,
        'urls':urls
    })

    # Sort the DataFrame by the 'Percentage' column
    df_sorted = df.sort_values(by='Percentage',ascending=False)
    df_sorted1 = df1.sort_values(by='rating', ascending=False)


    sorted_percentages = df_sorted['Percentage'].tolist()
    sorted_texts = df_sorted['Text'].tolist()
    sorted_urls=df_sorted["urls"].tolist()

    sorted_percentages1 = df_sorted1['rating'].tolist()
    sorted_texts1 = df_sorted1['Text'].tolist()
    sorted_urls1 = df_sorted1["urls"].tolist()


    st.session_state.content.append("<h3 style='text-align: left;color: white;font-size:45px;'>Ranking by Specifications</h3>")
    for i in range(len(title)):
        st.session_state.content.append(f"{i+1})[{sorted_texts[i]}]({sorted_urls[i]})")
        st.session_state.content.append("\n")
    st.session_state.content.append("<h3 style='text-align: left;color: white;font-size:45px;'>Ranking by Rating</h3>")
    for i in range(len(title)):
        st.session_state.content.append(f"{i+1})[{sorted_texts1[i]}]({sorted_urls1[i]})")
        st.session_state.content.append("\n")

    # Create a pie chart using Plotly
    fig= px.pie(values=rate, names=title, title='rating Pie Chart')
    fig2= px.pie(values=sim, names=title, title='specifications Pie Chart')
    # Display the pie chart in Streamlit
    st.session_state.figure.append(fig)
    st.session_state.figure.append(fig2)

with st.sidebar:
    col1, col2 ,col3= st.columns(3)
    with col1:
        if st.button("Add URL", key="button1"):
            add_text_input()
    with col3:
        if st.button("Process", key="button3"):
            generate()
    with col2:
        if st.button("Rerun",key="button2"):
            generate()
for i in st.session_state.content:
    if "Ranking" in i:
        st.write(i,unsafe_allow_html=True)
    else:
        st.write(i)
st.session_state.content.clear()
for i in st.session_state.figure:
    st.plotly_chart(i)
st.session_state.figure.clear()


