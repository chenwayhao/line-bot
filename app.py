from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai
import re 
import slot_machine, nearby_restaurant
import requests



app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')
google_maps_apikey = os.getenv('GOOGLE_PLACES_APIKEY')

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
    if 'fortune_action=' in data:
        fortune = data.split('=')[1]
        user_responses[user_id]['fortune'] = fortune
        print(fortune)
        weather_message = slot_machine.buttons_template_message_weather()
        line_bot_api.push_message(user_id, weather_message)

    elif 'weather_action=' in data:
        weather = data.split('=')[1]
        user_responses[user_id]['weather'] = weather
        print(weather)
        mood_message = slot_machine.buttons_template_message_mood()
        line_bot_api.push_message(user_id, mood_message)
        
    elif 'mood_action=' in data:
        mood = data.split('=')[1]
        user_responses[user_id]['mood'] = mood
        recommendation = slot_machine.getslot_recommendation(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(recommendation))
        print(mood)
    
    elif data == "允許":
        location_message = nearby_restaurant.request_location()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請點選分享位置', quick_reply = location_message))

    elif data == "不允許":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "您已選擇不允許我們使用您的位置。"))

# Handle text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    
    if re.match('當日選配', message):
        carousel_message = slot_machine.image_carousel_template_message()
        line_bot_api.reply_message(event.reply_token, carousel_message)
    
    elif re.match('附近美食', message):
        prelocation = nearby_restaurant.ask_for_location_permission()
        prelocation_message = FlexSendMessage(alt_text="Location Permission", contents = prelocation)
        line_bot_api.reply_message(event.reply_token, prelocation_message)
    
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(gpt35_message(message)))

# Function to request location from the user
# def request_location():
#     quick_reply = QuickReply(
#                     items=[
#                         QuickReplyButton(action = LocationAction(label="分享位置"))
#                     ]
#                 )
#     return quick_reply

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    print(latitude, longitude)
    
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1000&type=restaurant&key={google_maps_apikey}"
    response = requests.get(url)
    results = response.json().get('results', [])

    columns = []
    for result in results[:10]:  # Show up to 10 results
        name = result.get('name')
        address = result.get('vicinity')
        rating = result.get('rating', 'N/A')
        place_id = result.get('place_id')
        maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        
        photo_reference = result.get('photos', [{}])[0].get('photo_reference')
        if photo_reference:
            thumbnail_image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={google_maps_apikey}"
        else:
            thumbnail_image_url = "https://via.placeholder.com/800x400?text=No+Image"

        column = CarouselColumn(
            thumbnail_image_url=thumbnail_image_url,
            title=name,
            text=f"Rating: {rating}",
            actions=[
                {
                    "type": "uri",
                    "label": "View on Map",
                    "uri": maps_url
                }
            ]
        )
        columns.append(column)
    
    carousel_template = CarouselTemplate(columns=columns)
    template_message = TemplateSendMessage(alt_text='Nearby Restaurants', template = carousel_template)
    
    line_bot_api.reply_message(event.reply_token, template_message)
    # 直接調用 ChatGPT 函式來生成回覆訊息
    # reply_text = nearby_restaurant.getnearby_recommendation(latitude, longitude)
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text = reply_text))

# def get_bars_from_chatgpt(latitude, longitude):
#     # 使用 ChatGPT 來生成查詢字串
#     map_prompt = f"請列出經緯度 {latitude}, {longitude} 附近的五家餐酒館，格式如下：\n" \
#              f"1. 餐酒館名稱\n地址：餐酒館地址\nGoogle評分：評分\n"
    
#     # 調用 ChatGPT 函式來處理查詢字串
#     map_recommendation = gpt4_message(map_prompt)

#     return map_recommendation


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
        max_tokens = 350    
    )

    gpt_reply = response.choices[0]['message']['content'].replace('。','').strip()

    return gpt_reply

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)