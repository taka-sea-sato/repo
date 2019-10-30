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

    # 答えを辞書にセットする
    with(open(ansfilename, 'r')) as F:
        dic = list(set(F.read().strip().split('\n')))
    first_words = [ e[0] for e in dic ]
    
    with(open(usefilename, 'r')) as U:
        used = list(set(U.read().strip().split('\n')))
    
    word = jaconv.kata2hira(Msg)
    startswith = word[-1]
    
    if(len(used) != 1):
        if(not used[-1].startswith(startswith)):
            return '"{0}"で始まっていません。 '.format(startswith)
    
    msg = 'わたしの番です。'

    words = [ e for e in dic if jaconv.kata2hira(e).startswith(startswith) and e not in used ]
    if len(words) == 0:
        return 'もう思いつきません! あなたの勝ちです。'
    else:
        word = choice(words)
        convword = jaconv.kata2hira(word)
        startswith = convword[-1]
        with(open(usefilename, 'a')) as UA:
            UA.write(word)
            UA.write('\n')
        return msg + '{0}'.format(word)


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
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="お疲れさまでした"))
            return
    
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=GetRes(event.message.text)))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
