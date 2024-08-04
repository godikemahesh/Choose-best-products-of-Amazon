import urllib.request
from bs4 import BeautifulSoup
import re
from gpt_data import get
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import httpx
import asyncio
import ssl


#async def fetch_data(url):
#    async with httpx.AsyncClient() as client:
 #       response = await client.get(url)
  #      return response.text


lst=[]
def get_data(url):
    #data=asyncio.run(fetch_data(url))
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    response = urllib.request.urlopen(url, context=ctx)
    soup = BeautifulSoup(response, 'html.parser')
    sp=open("specify.txt", "a", encoding="utf-8")
    title = soup.find(id='productTitle')
    if title:
        title = title.get_text(strip=True)
        ptrn=r"([a-zA-Z0-9 ]*) \("
        title1=re.findall(ptrn,title)
        lst.append(title1)
    description = soup.find('div', {'id': 'feature-bullets'})
    if description:
        description = description.get_text(strip=True)
        sp.write(title+description)
    details = {}
    tech_details_section = soup.find(id='productDetails_techSpec_section_1')
    if tech_details_section:
        rows = tech_details_section.find_all('tr')
        for row in rows:
            th = row.find('th').get_text(strip=True)
            td = row.find('td').get_text(strip=True)
            details[th] = td
        sp.write("specifications:\n")
        for key, value in details.items():
                    sp.write(f'{key}: {value}')
    tech_details_div = soup.find('div', class_='content-grid-alternate-styles', id='tech')
    if tech_details_div:
        text = tech_details_div.text
        combined_string = ' '.join(text.split())
        sp.write("specifications:\n")
        sp.write(combined_string)
    rating = soup.find('span', {'class': 'a-icon-alt'})
    if rating:
        rating = rating.get_text(strip=True)
        sp.write(rating)

    return title1,rating

def d_prompt(data):
    prompt='''I have a list of product descriptions and specifications for several products. I want to extract and compare the key features from each product and create a single dictionary that contains the best specifications. The output should be in the format of a Python dictionary, such as {"os": "android 13"}.
    Here are the descriptions and specifications for each product:'''
    for i in range(len(data)):
        prompt+=f'\nproduct{i+1}->{lst[i]}:\nhere are the description and specifications:\n"""{data[i]}"""'
    prompt+="""\nConsider the following criteria for determining the "best" specifications:
- Latest technology or version (e.g., the newest operating system)
- Highest performance metrics (e.g., CPU speed, RAM)
- Largest capacity (e.g., storage space, battery life)
- Most features or advanced options (e.g., camera quality, display resolution)

Please provide a single dictionary that consists the 10 best specifications from all the products, prioritizing the most important features as described above.give overal best specifications.just gimme what i ask , dont explain and avoid giving programming scrips."""

    my_text=get(prompt)
    # Combine texts for vectorization
    all_texts = data + [my_text]

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Calculate cosine similarity
    similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
    list=[]
    # Display similarity percentages
    for idx, similarity in enumerate(similarities[0]):
        list.append(similarity * 100)
    return my_text,all_texts,list
