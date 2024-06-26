from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai
import re 
import slot_machine, alcohol
import requests
import urllib.parse


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

    def fortune_action():
        fortune = data.split('=')[1]
        user_responses[user_id]['fortune'] = fortune
        print(fortune)
        weather_message = slot_machine.buttons_template_message_weather()
        line_bot_api.push_message(user_id, weather_message)

    def weather_action():
        weather = data.split('=')[1]
        user_responses[user_id]['weather'] = weather
        print(weather)
        mood_message = slot_machine.buttons_template_message_mood()
        line_bot_api.push_message(user_id, mood_message)   

    def mood_action():
        mood = data.split('=')[1]
        user_responses[user_id]['mood'] = mood
        # response = user_responses.get(user_id, {})
        recommendation = slot_machine.getslots_recommendation(user_id, user_responses)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(recommendation))
        print(mood)

    def location_approve():
        location_message = request_location()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請點選分享位置', quick_reply = location_message))
    
    def location_denied():
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "您已選擇不允許我們使用您的位置。"))

    # def alcohol_action():
    #     key_value = data.split('&')
    #     key = key_value[0].split('=')[1]  # 提取 action 的值作為 key
    #     value = key_value[1].split('=')[1]  # 提取 value 的值

    #     # 如果 key 是 'flavor'，則需要處理多選
    #     if key == 'flavor':
    #         # 如果用戶沒有 flavor 記錄，則初始化一個空的列表
    #         if 'flavor' not in user_responses[user_id]:
    #             user_responses[user_id]['flavor'] = []
    #         user_responses[user_id]['flavor'].append(value)  # 將值添加到 flavor 列表中
    #         recommendation = alcohol.getalcohol_recommendation(user_id)
    #         line_bot_api.reply_message(event.reply_token, TextSendMessage(recommendation))
        
    #     else:
    #         user_responses[user_id][key] = value  # 將值添加到用戶的 responses 中

    #     # 根據 key 的不同，提出不同的下一個問題
    #     if key == 'base':
    #         degreeOfalcohol = alcohol.degreeOfalcohol()  # 如果是基底問題，則詢問第二個問題
    #         line_bot_api.push_message(user_id, degreeOfalcohol)
    #     elif key == 'preference':
    #         flavorOfalcohol = alcohol.flavorOfalcohol()  # 如果是偏好問題，則詢問第三個問題
    #         line_bot_api.push_message(user_id, flavorOfalcohol)

    def base_action():
        base = data.split('=')[1]
        user_responses[user_id]['base'] = base
        print(base)
        degree_message = alcohol.degreeOfalcohol()
        line_bot_api.push_message(user_id, degree_message)
    
    def preference_action():
        preference = data.split('=')[1]
        user_responses[user_id]['preference'] = preference
        print(preference)
        flavor_message = alcohol.flavorOfalcohol()
        line_bot_api.push_message(user_id, flavor_message)
    
    def flavor_action():
        flavor = data.split('=')[1]
        user_responses[user_id]['flavor'] = flavor
        recommendation = alcohol.getalcohol_recommendation(user_id, user_responses)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(recommendation))
        print(flavor)

    action_map = {
        'fortune_action=': fortune_action,
        'weather_action=': weather_action,
        'mood_action=': mood_action,
        '允許': location_approve,
        '不允許':location_denied,
        'base_action=':base_action,
        'preference_action=': preference_action,
        'flavor_action=':flavor_action
    }

    for action_key in action_map:
        if action_key in data:
            action_map[action_key]()
            break


# Handle text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    user_id = event.source.user_id

    def today_selection():
        carousel_message = slot_machine.image_carousel_template_message()
        line_bot_api.reply_message(event.reply_token, carousel_message)

    def nearby_food():
        user_responses[user_id] = {'activity': 'restaurant'}
        prelocation_message = prelocation()
        line_bot_api.reply_message(event.reply_token, prelocation_message)

    def nearby_hotel():
        user_responses[user_id] = {'activity': 'lodging'}
        prelocation_message = prelocation()
        line_bot_api.reply_message(event.reply_token, prelocation_message)

    def shot_selection():
        baseOfalcohol = alcohol.baseOfalcohol()
        line_bot_api.push_message(user_id, baseOfalcohol)


    def default():
        line_bot_api.reply_message(event.reply_token, TextSendMessage(gpt35_message(message)))

    action_map = {
        '當日選配': today_selection,
        '附近美食': nearby_food,
        '不醉不歸': nearby_hotel,
        '越夜越嗨': shot_selection
    }

    for pattern, function in action_map.items():
        if re.match(pattern, message):
            function()
            break
    else:
        default()

def prelocation():
    prelocation = ask_for_location_permission()
    prelocation_message = FlexSendMessage(alt_text="Location Permission", contents = prelocation)
    return prelocation_message

# 問使用者是否允許取得位置的函數
def ask_for_location_permission():
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
    
    return richmenu_json

def request_location():
    quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action = LocationAction(label="分享位置"))
                    ]
                )
    return quick_reply

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    user_id = event.source.user_id
    response = user_responses.get(user_id, {})
    activity = response.get('activity', 'unknown')

    latitude = event.message.latitude
    longitude = event.message.longitude
    print(latitude, longitude)
    template_message = get_googledata(latitude, longitude, google_maps_apikey, activity)
    line_bot_api.reply_message(event.reply_token, template_message)

def get_googledata(latitude, longitude, google_maps_apikey, activity):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1000&type={activity}&language=zh-TW&key={google_maps_apikey}"
    response = requests.get(url)
    results = response.json().get('results', [])

    columns = []
    places_data = []
    for result in results[:10]:  # Show up to 10 results
        name = result.get('name')
        if len(name) > 40:
            name = name[:37] + '...'
        address = result.get('vicinity')
        rating = result.get('rating', 'N/A')
        place_id = result.get('place_id')
        places_data.append({
            'name': name,
            'address': address,
            'rating': rating,
            'place_id': place_id,
            'photos': result.get('photos', [{}])
        })

    gpt_input = "請幫我查月以下地點的評論，並返回10個最好的地點：\n"
    for place in places_data:
        gpt_input += f"名稱: {place['name']}, 地址: {place['address']}, 評分: {place['rating']}\n"
    
    gpt_reply = gpt35_message(gpt_input)

    sorted_places_data = parse_gpt_reply(gpt_reply, places_data)

    for place in sorted_places_data:
        name = place['name']
        address = place['address']
        rating = place['rating']
        photos = place['photos']

        encoded_name = urllib.parse.quote(name)
        maps_url = f"https://www.google.com/maps/place/?q={encoded_name}"
        
        photo_reference = photos[0].get('photo_reference') if photos else None
        if photo_reference:
            thumbnail_image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={google_maps_apikey}"
        else:
            thumbnail_image_url = "https://via.placeholder.com/800x400?text=No+Image"

        column = CarouselColumn(
            thumbnail_image_url=thumbnail_image_url,
            title=name,
            text=f"評分: {rating}⭐\n地址：{address}",
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
    template_message = TemplateSendMessage(alt_text=f'Nearby {activity}', template = carousel_template)

    return template_message

def parse_gpt_reply(gpt_reply, places_data):
    place_names = gpt_reply.split('\n')
    sorted_places_data = []
    for name in place_names:
        for place in places_data:
            if place['name'] in name:
                sorted_places_data.append(place)
                break
    return sorted_places_data

def gpt4_message(message):

    response = openai.ChatCompletion.create(
        model='gpt-4-turbo',
        messages = [{"role":"user","content":message}],
        temperature = 0.5,
        max_tokens = 750
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