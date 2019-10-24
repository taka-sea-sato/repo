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

gameflg = 0

def GetRes(Msg,flg):
    
    if flg == 0:
        return "しりとりしよ　って言ってみて"

    ansfilename = r"ans.txt"

    # 答えを辞書にセットする
    with(open(ansfilename, 'r', encoding = "shift_jis")) as F:
        dic = list(set(F.read().strip().split('\n')))
    first_words = [ e[0] for e in dic ]
    #used = defaultdict(int)
    
    word = jaconv.kata2hira(Msg)
    
    if len(used) == 0:
        startswith = Msg[-1]
        startswith = jaconv.kata2hira(startswith)
    
    used[word] = len(used)
    
    msg = 'わたしの番です。'

    words = [ e for e in dic if jaconv.kata2hira(e).startswith(startswith) and e not in used ]
    if len(words) == 0:
        return 'もう思いつきません! あなたの勝ちです。'
        print('{0} から始まる言葉を教えてください！'.format(startswith))
        # 回答リストに書き込む処理
        with(open(ansfilename, 'a')) as F:
            F.write(s)
            F.write('\n')
        print('ありがとうございます！これでまた賢くなりました！')
    else:
        word = choice(words)
        convword = jaconv.kata2hira(word)
        startswith = convword[-1]
        used[word] = len(used)
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
    
    if event.message.text == "しりとりしよ":
        gameflg = 1
        used = defaultdict(int)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="なんか言葉入れてみて"))
    elif event.message.text == "しりとりおわり":
        gameflg = 0
        used = defaultdict(int)   
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="おつかれさま"))
    else:    
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=GetRes(event.message.text,gameflg)))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
