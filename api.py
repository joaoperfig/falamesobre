import requests
from IPython import embed
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import openai
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Conversation(BaseModel):
  parts: List[str]

siteSearch = [
  'https://noticias.sapo.pt/',
  'https://www.jornaldenegocios.pt/',
  'https://www.tsf.pt/',
  'https://sol.sapo.pt/',
  'https://www.lux.iol.pt/',
  'https://www.iol.pt/',
  'https://www.tvi24.iol.pt/',
  'https://www.ionline.pt/',
  'https://www.sapo.pt/',
  'https://www.jn.pt/',
  'https://expresso.sapo.pt/',
  'https://dnoticias.pt/',
  'https://abola.pt/',
  'https://www.dinheirovivo.pt/',
  'https://economico.sapo.pt/',
  'https://sicnoticias.sapo.pt/',
  'https://www.aeiou.pt/',
  'https://www.sabado.pt/',
  'https://www.cmjornal.pt/',
  'http://publico.pt/',
  'http://www.rtp.pt/',
  'http://www.dn.pt/',
  'http://news.google.pt/'
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def dateconvert(date):
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second
    string = "{:0>4d}{:0>2d}{:0>2d}{:0>2d}{:0>2d}{:0>2d}".format(year, month, day, hour, minute, second)
    return string

def arquivorequest(query, startdate=None, enddate=None, domains=[]):
    maxItems = 5
    if startdate != None:
        startdate = dateconvert(startdate)
    if enddate != None:
        enddate = dateconvert(enddate)

    payloads = []
    if len(domains) == 0:
        payload = {'q': query,'maxItems': maxItems}
    else:
        payload = {'q': query,'maxItems': maxItems, 'siteSearch': domains}

    if startdate != None:
        payload["from"] = startdate
    if enddate != None:
        payload["to"] = enddate

    r = requests.get('http://arquivo.pt/textsearch', params=payload)
    contentsJSon = r.json()
    for item in contentsJSon["response_items"]:
        title = item["title"]
        url = item["linkToArchive"]
        time = item["tstamp"]
        page = requests.get(item["linkToExtractedText"])
        # Note a existencia de decode, para garantirmos que o conteudo devolvido pelo Arquivo.pt (no formato ISO-8859-1) e impresso no formato (UTF-8)
        content = page.content.decode('utf-8')
        item["content"] = content

    return contentsJSon["response_items"]


def gptsummary(topic, texts):
    with open("secrets.txt", "r") as f:
        key = f.read().strip()
    openai.api_key = key

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
            {"role": "user", "content": " I need your help to summarize relevant information related to a specific query topic. I will provide you with multiple texts and a query word or expression. Your task is to filter out any irrelevant content and generate a concise summary of the relevant information. Please ensure that the summary captures the essential details of the text while avoiding unnecessary information. The summarized information will be used later, so accuracy is crucial.  Summaries should be around 500 words long. Include as many specific details as possible. Thank you for your assistance!"},
            {"role": "assistant", "content": "Of course, I will reply with the summary."},
            {"role": "user", "content": "This time the topic is: "+topic+"\n\nHere are the texts:\n\n"+texts}
        ]
    )
    summary = completion["choices"][0]["message"]["content"]
    return summary

def gptchat(topic, summary, conversation):
    with open("secrets.txt", "r") as f:
        key = f.read().strip()
    openai.api_key = key

    messages = [{"role": "system", "content": "You are a helpful assistant that provides accurate information about the recent developments on different topics. You will be given a summary with information on the topic over the last few years. You can use this information to inform yourself and you can also use information that you already knew beyond that. You emphasize how things changed over the years. The conversation will be held in european portuguese. You are part of a project called 'Fala-me sobre'. You keep your answers very short, only providing the requested information, and avoiding sharing more than what was asked. The topic for this conversation is "+topic+" and the summaries are:\n"+summary}]
    current = "user"
    for message in conversation:
        messages += [{"role":current, "content":message}]
        if current == "user":
            current = "assistant"
        else:
            current = "user"

    print("Sending chat to chatgpt")

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    response = completion["choices"][0]["message"]["content"]
    return response

@app.get("/resumo/{query}")
async def makesummary(query: str):

    print("Sending general query of",query,"to arquivo")
    items = arquivorequest(query, None, None, [])
    texts = ""
    for item in items:
        texts += item["content"][:1000]
    print("Sending texts to chatgpt")
    summary = gptsummary(query, texts)
    fullsummary = "General info:\n\n"+summary

    for year in [2006, 2009, 2011, 2014, 2017, 2020]:
        startyear = year
        endyear = year+3
        startdate = datetime(year=startyear, month=1, day=1)
        enddate = datetime(year=endyear, month=1, day=1)
        print("Sending",query,"in",startyear,"to",endyear,"to arquivo")
        items = arquivorequest(query, startdate, enddate, siteSearch)
        print("Got",len(items),"items")
        texts = ""
        for item in items:
            texts += item["content"][:1000]
        print("Sending texts to chatgpt")
        summary = gptsummary(query, texts)
        print(summary[:500])
        fullsummary += "From year "+str(startyear) + " to year " + str(endyear) + ":\n\n" + summary + "\n\n"


    with open("latestsummary.txt", "w") as f:
        f.write(fullsummary)

    with open("latestopic.txt", "w") as f:
        f.write(query)

    return {"summary": fullsummary}

@app.post("/chat")
async def chat(conversation: Conversation):

    with open("latestsummary.txt", "r") as f:
        summary = f.read()

    with open("latestopic.txt", "r") as f:
        topic = f.read()

    parts = conversation.parts

    response = gptchat(topic, summary, conversation.parts)

    print("Got response",response)

    return {"response": response}
