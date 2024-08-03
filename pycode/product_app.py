import streamlit as st
import find_product
import re
import pandas as pd
from gpt_data import lemitization
# Initialize session state for text inputs
path=r"C:\Users\mahes\Downloads\suraj logo.png"
st.logo(path)
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

# Use HTML to set the heading with the custom CSS class

st.markdown("<h2 class='centered-heading'>SURAJ® OptiChoice</h2>", unsafe_allow_html=True)
st.title("Choose Your Product")
#st.write("<h2 style='text-align: center;color: yellow;font-size:65px;'>SURAJ® OptChoice</h2>", unsafe_allow_html=True)
st.write("Paste the Urls and get to choose best products in the amazon..\n")


if "urls" not in st.session_state:
    st.session_state.urls = ["",""]  # Start with one empty URL field
if "content" not in st.session_state:
    st.session_state.content = []


# Function to add a new text input
def add_text_input():
    st.session_state.urls.append("")  # Add an empty string for a new URL

# Sidebar layout
st.sidebar.title("Enter URLs here")

# Display text inputs and collect user input
for i, url in enumerate(st.session_state.urls):
    st.session_state.urls[i] = st.sidebar.text_input(f"URL {i + 1}", url, key=f"url_{i}")

# Button to add new text input
st.sidebar.button("Add URL", on_click=add_text_input)

def generate():
    lst=[]
    title=[]
    rate=[]
    urls=[]
    specifications=[]
    for i ,url in enumerate(st.session_state.urls):
        if st.session_state.urls[i]!="":
            tit,rank=find_product.get_data(st.session_state.urls[i])
            urls.append(st.session_state.urls[i])
            pattern2 = r"(\d.\d) out of 5"
            rank=re.findall(pattern2,rank)
            title.append(tit)
            rate.append(rank)
            with open("specify.txt", "r+",encoding="utf-8") as ps:
                content = ps.read()
                ps.truncate(0)
                data = re.sub(r"â€Ž|â|€|Ž", "", content)
                lst.append(data)
                spec=re.search(r"specifications:",data)
                start=spec.end()
                specifications.append(data[start:].split())
    adata=lemitization(lst)
    my_text,all_texts,sim=find_product.d_prompt(adata)
    st.session_state.content.append(f"retrived best specifications:\n{my_text}")
    for i in specifications:
        st.session_state.content.append(i)
    # Combine the two lists into a list of tuples
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

    # Extract the sorted lists
    sorted_percentages = df_sorted['Percentage'].tolist()
    sorted_texts = df_sorted['Text'].tolist()
    sorted_urls=df_sorted["urls"].tolist()

    sorted_percentages1 = df_sorted1['rating'].tolist()
    sorted_texts1 = df_sorted1['Text'].tolist()
    sorted_urls1 = df_sorted1["urls"].tolist()


    st.session_state.content.append("<h3 style='text-align: left;color: white;font-size:45px;'>Ranking by Specifications</h3>")
    for i in range(len(title)):
        #st.write("[Click here to visit Streamlit](https://www.streamlit.io)")
        st.session_state.content.append(f"{i+1})[{sorted_texts[i]}]({sorted_urls[i]})")
        st.session_state.content.append("\n")
    st.session_state.content.append("<h3 style='text-align: left;color: white;font-size:45px;'>Ranking by Rating</h3>")
    for i in range(len(title)):
        st.session_state.content.append(f"{i+1})[{sorted_texts1[i]}]({sorted_urls1[i]})")
        st.session_state.content.append("\n")



st.sidebar.button("process",on_click=generate)
for i in st.session_state.content:
    if "Ranking" in i:
        st.write(i,unsafe_allow_html=True)
    else:
        st.write(i)



