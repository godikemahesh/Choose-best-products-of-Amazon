from openai import OpenAI
import sys
import spacy
nlp=spacy.load("en_core_web_sm")
def lemitization(lst):
    lemed=[]
    for i in range(len(lst)):
        doc=nlp(lst[i])
        processed_text = " ".join([token.lemma_ for token in doc if not token.is_stop])
        lemed.append(processed_text)
    return lemed

def get(state):
    client = OpenAI(
        api_key="211fa21c08be45e86847eff9d61cb4e6bc7374995f3b7ac894d34f2395a415dd",
        base_url='https://llm.mdb.ai/')
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'user', 'content': state}
        ],
        stream=False
    )

    return completion.choices[0].message.content
