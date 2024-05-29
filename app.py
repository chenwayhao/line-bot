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
        print(fortune)
        weather_message = slot_machine.buttons_template_message_weather()
        line_bot_api.push_message(user_id, weather_message)

    if 'weather_action=' in data:
        weather = data.split('=')[1]
        user_responses[user_id]['weather'] = weather
        print(weather)
        mood_message = slot_machine.buttons_template_message_mood()
        line_bot_api.push_message(user_id, mood_message)
        
    if 'mood_action=' in data:
        mood = data.split('=')[1]
        user_responses[user_id]['mood'] = mood
        recommendation = get_recommendation(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(recommendation))
        print(mood)

# Handle text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if re.match('當日選配', message):
        carousel_message = slot_machine.image_carousel_template_message()
        line_bot_api.reply_message(event.reply_token, carousel_message)
    
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

# 處理使用者文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    message = event.message.text
    if re.match('附近美食', message):
        ask_for_location_permission(event.reply_token)

# 問使用者是否允許取得位置的函數
def ask_for_location_permission(reply_token):
    # Rich menu JSON 結構
    richmenu_json = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://media.istockphoto.com/id/1421460958/photo/hand-of-young-woman-searching-location-in-map-online-on-smartphone.jpg?s=612x612&w=0&k=20&c=Kw8yHXSKmEhfjJVscY51Zob6IRjof0N2wmj2zp2-iRI=",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": "https://line.me/"
            },
            "align": "center"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "要允許『夜貓Fun生活』使用您的位置嗎?",
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 6,
                                    "style": "italic",
                                    "weight": "bold"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "允許",
                        "data": "允許"
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "不允許",
                        "data": "不允許"
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }


# 發送 Rich Menu 給使用者
    message = FlexSendMessage(alt_text="Location Permission", contents=richmenu_json)
    line_bot_api.reply_message(reply_token, message)



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

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)