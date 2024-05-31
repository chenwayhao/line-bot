from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai
import re 
import slot_machine, nearby_restaurant, nightclub


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
    
    elif re.match('越夜越嗨', message):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '越夜越嗨'))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(gpt35_message(message)))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    print(latitude, longitude)

    template_message = nearby_restaurant.get_restaurant(latitude, longitude, google_maps_apikey)
    line_bot_api.reply_message(event.reply_token, template_message)


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