from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

import sys
from random import shuffle, choice
from itertools import count
from collections import defaultdict
import jaconv

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

def GetRes(Msg):

    ansfilename = r"ans.txt"
    usefilename = r"used.txt"
    lastfilename = r"lastans.txt"
    playtxt = r"play.txt"

    # 答えを辞書にセットする
    with(open(ansfilename, 'r')) as F:
        dic = list(set(F.read().strip().split('\n')))
    first_words = [ e[0] for e in dic ]
    
    with(open(usefilename, 'r')) as U:
        used = list(set(U.read().strip().split('\n')))
        
    with(open(lastfilename, 'r')) as L:
        Lastword = list(set(L.read().strip().split('\n')))
        
    with(open(playtxt, 'r')) as P:
        play = list(set(P.read().strip().split('\n')))
           
    word = jaconv.kata2hira(Msg)
    startswith = word[-1]
    
    for last in Lastword:
        print(last)
        last = jaconv.kata2hira(last)
    
    if(last[0] != "1"):
        if(not word.startswith(last[-1])):
            return '"{0}"で始まっていません。 '.format(last[-1])
    
    msg = 'わたしの番です。'

    words = [ e for e in dic if jaconv.kata2hira(e).startswith(startswith) and e not in used ]
    if len(words) == 0:
        with(open(ansfilename, 'a')) as F:
            for e in play:
                F.write(e)
                F.write('\n')
        return 'もう思いつきません! あなたの勝ちです。\n今回使った言葉を覚えました。'
    else:
        word = choice(words)
        convword = jaconv.kata2hira(word)
        startswith = convword[-1]
        with(open(usefilename, 'a')) as UA:
            UA.write(word)
            UA.write('\n')
           
        with(open(playtxt, 'a')) as P:
            P.write(Msg)
            
        with(open(lastfilename, 'w')) as L:
            L.write(word)
            L.write('\n')
        return msg + '{0}'.format(word)

def GetTes(Msg):

    ansfilename = r"ans.txt"
    usefilename = r"used.txt"
    lastfilename = r"used.txt"

    # 答えを辞書にセットする
    with(open(ansfilename, 'r')) as F:
        dic = list(set(F.read().strip().split('\n')))
    first_words = [ e[0] for e in dic ]
    
    with(open(usefilename, 'r')) as U:
        used = list(set(U.read().strip().split('\n')))
        
    with(open(lastfilename, 'r')) as L:
        Lastword = list(set(L.read().strip().split('\n')))
        
    for last in Lastword:
        print(last)
    return last[-1]

def GetWord():

    ansfilename = r"ans.txt"

    # 答えを辞書にセットする
    with(open(ansfilename, 'r')) as F:
        dic = list(set(F.read().strip().split('\n')))

    return '今{}個の言葉を覚えてます'.format(len(dic))



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
        if event.message.text == "しりとりおわり":
            usedname = r"used.txt"
            with(open(usedname, 'w')) as UA:
                UA.write("1")
                UA.write('\n')
            
            usedname = r"lastans.txt"
            play = r"play.txt"
            with(open(usedname, 'w')) as LA:
                LA.write("1")
                LA.write('\n')
            with(open(play, 'w')) as P:
                P.write('\n')
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="お疲れさまでした"))
            return
        
        if event.message.text == "てすと":
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=GetTes(event.message.text)))
            return
        
        if event.message.text == "いくつおぼえた？":
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=GetWord()))
    
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=GetRes(event.message.text)))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
