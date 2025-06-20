from openai import OpenAI
import sys
#import spacy
#nlp=spacy.load("en_core_web_sm")
#def lemitization(lst):
#    lemed=[]
#    for i in range(len(lst)):
#        doc=nlp(lst[i])
#        processed_text = " ".join([token.lemma_ for token in doc if not token.is_stop])
#        lemed.append(processed_text)
#    return lemed

from groq import Groq


def get(prompt):
    client = Groq(api_key="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")
    response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role": "user", "content": prompt}
    ],
    stream=False
    )
    return response.choices[0].message.content.strip()
