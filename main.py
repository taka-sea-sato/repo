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

    # 答えを辞書にセットする
    with(open(ansfilename, 'r', encoding = "shift_jis")) as F:
        dic = list(set(F.read().strip().split('\n')))
    first_words = [ e[0] for e in dic ]
    used = defaultdict(int)

    players = [ 'あなた', 'わたし' ]
    shuffle(players)
    startswith = None
    for i in count(1):
        if players[i % len(players)] == 'あなた':
            if startswith == None:
                startswith = choice(first_words)
                startswith = jaconv.kata2hira(startswith)
            return '{0:3}: あなたの番です。 "{1}": '.format(i, startswith)
        
            s = jaconv.kata2hira(Msg)
            # 一文字目の確認
            while(not s.startswith(startswith)):
                print('"{0}"で始まっていません。 '.format(startswith))
                sys.stdout.write('{0:3}: あなたの番です。 "{1}": '.format(i, startswith))
                s = input()
                s = jaconv.kata2hira(s)
            # 既出単語かどうかの確認
            if s in used:
                print('"{0}"は{1}回目に{2}が使用しています。わたしの勝ちです。'.format(s, used[s], players[used[s]%len(players)]))
                break
            startswith = s[-1]
            # 最後の文字が「ん」かどうかの確認
            if startswith == 'ん':
                print('最後に、ん がついたので私の勝ちです。')
                break
            used[s] = i
        else:
            msg = '{0:3}: わたしの番です。      '.format(i)
            if startswith == None:
                word = choice(dic)
                convword = jaconv.kata2hira(word)
                startswith = convword[-1]
                used[convword] = i
                
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg + '{0}'.format(word))
            else:
                words = [ e for e in dic if jaconv.kata2hira(e).startswith(startswith) and e not in used ]
                if len(words) == 0:
                    print('もう思いつきません! あなたの勝ちです。')
                    print('{0} から始まる言葉を教えてください！'.format(startswith))
                    s = input()
                    # 回答リストに書き込む処理
                    with(open(ansfilename, 'a')) as F:
                        F.write(s)
                        F.write('\n')
                    print('ありがとうございます！これでまた賢くなりました！')
                    break
                else:
                    word = choice(words)
                    convword = jaconv.kata2hira(word)
                    startswith = convword[-1]
                    used[word] = i
                    print(msg + '{0}'.format(word))
    print('今回のしりとりでは{0}個の単語を使用しました。'.format(len(used)))


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
    
    # event.message.text # 送られてきたメッセージ
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=GetRes(event.message.text)))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
