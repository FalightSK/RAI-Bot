from fastapi import Request, FastAPI, HTTPException

from linebot import (
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage
)

import linebot.v3.messaging as bot

from component import FlexAdmin

import os
import time
from datetime import datetime
from dotenv import load_dotenv
import json

from Rai_libs import Agent_module, rag_system, qa_bot, sum_rag
from Database import RetriveDoc, update_link, generate, get_link
from openai import OpenAI

load_dotenv(".env", override=True)

OPENAI_CLIEN = OpenAI(
   api_key=os.getenv("TYPHOON_TOKEN"),
   base_url='https://api.opentyphoon.ai/v1'
)

print('initailizing')
cache = {}
rag_bot = Agent_module('rag_bot', rag_system, OPENAI_CLIEN, model='typhoon-v1.5x-70b-instruct')
chater = Agent_module('chat_bot', qa_bot, OPENAI_CLIEN, model='typhoon-v1.5x-70b-instruct')
sum_bot = Agent_module('sum_bot', sum_rag, OPENAI_CLIEN, model='typhoon-v1.5x-70b-instruct')
filename=None
rager = RetriveDoc() if filename is None else RetriveDoc(filename) 
print('initailized')

app = FastAPI()

cache_chat = {}
cache_rag = {}
cache_sum = {}
cache = {
    'cache_chat': cache_chat,
    'cache_rag': cache_rag,
    'cache_sum': cache_sum
}
action = {}
#you are my spacial
query_bot_glob_mem = None


channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("CHANNEL_SECRET_TOKEN") # RAI@KMITL

if not channel_access_token or not channel_secret:
    raise ValueError("Environment variables LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set")

configuration = Configuration(access_token=channel_access_token)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

@app.post("/rai")
async def callback(request: Request):
    print("entered")
    signature = request.headers.get('X-Line-Signature', None)
    if signature is None:
        raise HTTPException(status_code=400, detail="Missing signature")

    body = await request.body()
    body = body.decode() 

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        print(event)
        userId = json.loads(str(event.source))['userId']
        
        if event.type == 'message':
            if event.message['type'] != 'text':
                continue
        else: 
            continue
        response = generate_response(event)
        print(response)
        
        if type(response) == dict:
            if response["type"] == "flex":
                await line_bot_api.reply_message(ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage.from_dict(response["content"])]
                ))
            else:
                await line_bot_api.reply_message(ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response["content"])]
                ))
        elif type(response) == list:
            for i, resp in enumerate(response):
                action[userId].pop()
                if i == 0:
                    if resp["type"] == "flex":
                        await line_bot_api.reply_message(ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage.from_dict(resp["content"])]
                    ))
                    else:
                        await line_bot_api.reply_message(ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=resp["content"])]
                    ))
                else:
                    push_message(userId, resp["content"])
                print(action[userId])
                time.sleep(0.5)

    return 'OK'

def push_message(user_id: str , response_body: dict):
    global bot
    global configuration
    
    message_dict = { "to": user_id, "messages": [ response_body ] }
    
    with bot.ApiClient(configuration) as api:
        api_instance = bot.MessagingApi(api)
        push_message_request = bot.PushMessageRequest.from_dict(message_dict)
        ap = api_instance.push_message(push_message_request)

def generate_response(event) -> dict:
    global cache

    userId = json.loads(str(event.source))['userId']
    in_text = event.message.text


    #command manual
    if in_text == r"/admin get_help":
        flexCommand = FlexAdmin.Command
        return {"type": "flex", "content": flexCommand}

    if in_text == r"/admin reset_cache":
        cache_chat = {}
        cache_rag = {}
        cache_sum = {}
        cache = {
            'cache_chat': cache_chat,
            'cache_rag': cache_rag,
            'cache_sum': cache_sum
        }
        print("memory is reseted")
        return {"type":"message", "content":'cache reseted'}

    if r"/admin update_link ->" in in_text:
        url_link = in_text.split(">")
        update_link(url_link[1])
        print("link is updated")
        return {"type":"message", "content":f'link is updated {url_link[1]}'}

    if in_text == r"/admin force_updb":
        url_link = get_link()
        print(url_link)
        generate(url_link)
        print("database is updated")
        return {"type":"message", "content":'database is updated'}

    if in_text == r'/admin save_memory':
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f") 

        with open(f'chater_memory_{now}.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
        with open(f'query_memory_{now}.json', 'w', encoding='utf-8') as f:
            json.dump(query_bot_glob_mem, f, ensure_ascii=False, indent=4)

        return {"type":"message", "content":f'saved chater_memory_{now}.json | saved query_memory_{now}.json'}
    

    if userId in cache['cache_chat'].keys():
        pass
    else:
        cache['cache_chat'][userId] = {'user':[],'assistant':[]}
        cache['cache_rag'][userId] = {'user':[],'assistant':[]}
        cache['cache_sum'][userId] = {'user':[],'assistant':[]}
        action[userId] = []
    res = chat_call(in_text, userId)
    
    return {"type":"message", "content":res}



#note ask how rag
def chat_call(text, user_id) -> str:
    global rag_bot,sum_bot,chater
    global cache

    rag_bot.memory = cache['cache_rag'][user_id]
    sum_bot.memory = cache['cache_sum'][user_id]
    chater.memory = cache['cache_chat'][user_id]
    question = ""

    #if text == "reset_mem":
    #    rag_bot.reset_memory()
    #    sum_bot.reset_memory()
    #    chater.reset_memory()
    #    return 'memory is reseted'

    question += text
    query = rag_bot(question)
    information = rager.search(query)
    # try:
    #     information = rag_data['topic'] + ": "+ rag_data['detail'] + '\ncontact:' +rag_data['contact']
    # except:
    #     information = rag_data['topic'] + ": "+ rag_data['detail'] + '\ncontact:' +rag_data['link'] + '\njob oppornity'+rag_data['job']
    #print(information)
    text_rag = f"Doc: {information}\nQuestion: {question}"
    text_rag = sum_bot(text_rag)
    print(text_rag)
    msg = f"rag: {text_rag}\nquestion: {question}"
    res = chater(msg)

    cache['cache_rag'][user_id] = rag_bot.memory
    cache['cache_sum'][user_id] = sum_bot.memory
    cache['cache_chat'][user_id] = chater.memory

    return res