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

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["dVa2cmL4Jls/fx6ge+ivk0YgF7QD3/BIeBjcpn3IZ2Xf/CLOqYvVY14NG8rgCBYxrRF1Jh81LyHCNZ/IK/JSHzHWvbEQ4KLE2x+8iWny2k7W+Xz/5ZEpwR/ybNrf/8kHTb/m2l/bI30P4hVOo3/icgdB04t89/1O/w1cDnyilFU="]
YOUR_CHANNEL_SECRET = os.environ["ef2e04317f7581af614f2b21af9fb0b9"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)