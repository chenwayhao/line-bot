from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai


app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # message = TextSendMessage(text=event.message.text)
    # line_bot_api.reply_message(event.reply_token, message)
    user_message = event.message.text


    # gpt4 version  
    # response = openai.ChatCompletion.create(
    #     model='gpt-4',
    #     messages = [{"role":"user","content":user_message}],
    #     temperature = 0.5,
    #     max_tokens = 150
    # )
    # gpt_reply = response.choices[0]['message']['content'].replace('。','').strip()


    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo-0125',
        messages = [{"role":"user","content":user_message}],
        temperature = 0.5,
        max_tokens = 250    
    )

    gpt_reply = response.choices[0]['text']


    gpt_reply1 = response.choices
    print(gpt_reply1)
    # Create a TextSendMessage object with the response
    message = TextSendMessage(text=gpt_reply)

    # Reply to the user
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)