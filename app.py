from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai
import re 
import random
import slot_machine


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


user_responses = {}
# Handle postback events
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    # Log the response
    if user_id not in user_responses:
        user_responses[user_id] = {}
    # if 'action=' in data:
        fortune = data.split('=')[1]
        user_responses[user_id]['fortune'] = fortune
    if 'fortune_action=' in data:
        fortune = data.split('=')[1]
        user_responses[user_id]['fortune'] = fortune
        weather_message = slot_machine.buttons_template_message_weather()
        line_bot_api.push_message(user_id, weather_message)
    elif 'weather_action' in data:
        weather = data.split('=')[1]
        user_responses[user_id]['weather'] = weather

        print(weather)
        

# Handle text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    user_id = event.source.user_id
    if re.match('當日選配', message):

        carousel_message = slot_machine.image_carousel_template_message()

        line_bot_api.reply_message(event.reply_token, carousel_message)

    elif message in ['悶熱', '濕冷', '溫暖', '涼爽']:

        buttons_template_message_mood = TemplateSendMessage(
            alt_text='心情調查',
            template=ButtonsTemplate(
                thumbnail_image_url='https://www.mindfulness.com.tw/upfile/editor/images/8.png',
                title='今日心情如何?',
                text='請選擇適合的形容詞',
                actions=[
                    MessageAction(
                        label='很好',
                        # display_text='GOOD',
                        text='很好！'
                    ),
                    MessageAction(
                        label='不好不壞',
                        # display_text='SOSO',
                        text='不好不壞！'
                    ),
                    MessageAction(
                        label='很差',
                        # display_text='Bad',
                        text='很差！'
                    )
                ]
            )
        )
        line_bot_api.push_message(user_id, buttons_template_message_mood)
        print(buttons_template_message_mood)
        
    elif message in ['很好！','不好不壞！','很差！']:
        user_responses[user_id]['mood'] = message
        recommendation = get_recommendation(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(recommendation))
    
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(gpt35_message(message)))

def get_recommendation(user_id):
    response = user_responses.get(user_id, {})
    fortune = response.get('fortune', 'unknown')
    weather = response.get('weather', 'unknown')
    mood = response.get('mood', 'unknown')

    print(fortune, weather, mood)


    # Generate a prompt for ChatGPT
    prompt = (
        f"基於以下條件，給出一個夜生活推薦：\n"
        f"運勢：{fortune}\n"
        f"天氣：{weather}\n"
        f"心情：{mood}\n"
        f"請給出一個適合的行程，1. 夜生活 、2.酒吧、3. KTV唱歌、4. 夜店。並且推薦一個台北適合的地點。請利用20字以內說明 1. 適合的行程 2. 地點 3. 地點的 google map 連結(https://www.google.com/maps/search/店名)"
    )

    recommendation = gpt35_message(prompt)

    return recommendation

def gpt4_message(message):

    response = openai.ChatCompletion.create(
        model='gpt-4-turbo',
        messages = [{"role":"user","content":message}],
        temperature = 0.5,
        max_tokens = 150
    )

    gpt_reply = response.choices[0]['message']['content'].replace('。','').strip()
    return gpt_reply

def gpt35_message(message):
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo-0125',
        messages = [{"role":"user", "content":message}],
        temperature = 0.5,
        max_tokens = 150    
    )

    gpt_reply = response.choices[0]['message']['content'].replace('。','').strip()

    return gpt_reply

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     user_message = event.message.text
#     #gpt4 version  
#     response = openai.ChatCompletion.create(
#         model='gpt-4o',
#         messages = [{"role":"user","content":user_message}],
#         temperature = 0.5,
#         max_tokens = 150
#     )
# #--------------------------------------------------------
#     # response = openai.ChatCompletion.create(
#     #     model = 'gpt-3.5-turbo-0125',
#     #     messages = [{"role":"user","content":user_message}],
#     #     temperature = 0.5,
#     #     max_tokens = 250    
#     # )
# #--------------------------------------------------------
#     gpt_reply = response.choices[0]['message']['content'].replace('。','').strip()
#     gpt_reply1 = response.choices
#     print(gpt_reply1)
#     #Create a TextSendMessage object with the response
#     message = TextSendMessage(text=gpt_reply)

#     # Reply to the user
#     line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)