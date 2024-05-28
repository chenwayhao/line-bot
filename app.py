from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai
import re 
import random


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
    if 'action=' in data:
        fortune = data.split('=')[1]
        user_responses[user_id]['fortune'] = fortune

        buttons_template_message_weather = TemplateSendMessage(
            alt_text='天氣調查',
            template=ButtonsTemplate(
                thumbnail_image_url='https://img.lovepik.com/png/20231015/Cartoon-image-thunderstorm-weather-raindrop-cartoon-images-lightning_215956_wh1200.png',
                title='今日天氣你覺得如何?',
                text='請選擇適合的形容詞',
                actions=[
                    MessageAction(
                        label='悶熱',
                        display_text='悶熱',
                        text='悶熱'
                    ),
                    MessageAction(
                        label='濕冷',
                        display_text='濕冷',
                        text='濕冷'
                    ),
                    MessageAction(
                        label='溫暖',
                        display_text='溫暖',
                        text='溫暖'
                    ),
                    MessageAction(
                        label='涼爽',
                        display_text='涼爽',
                        text='涼爽'
                    )
                ]
            )
        )
        # Then push the buttons template message
        line_bot_api.push_message(user_id, buttons_template_message_weather)

# Handle text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    user_id = event.source.user_id
    if re.match('當日選配', message):
        fortunes = ['大吉', '吉', '凶', '大凶']
        random.shuffle(fortunes)

        image_carousel_template_message = TemplateSendMessage(
            alt_text='請抽籤',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/W7nI6fg.jpg',
                        action=PostbackAction(
                            label='請抽我看看運勢',
                            display_text='到底抽到什麼呢?',
                            data=f'action={fortunes[0]}'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/W7nI6fg.jpg',
                        action=PostbackAction(
                            label='請抽我看看運勢',
                            display_text='到底抽到什麼呢?',
                            data=f'action={fortunes[1]}'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/W7nI6fg.jpg',
                        action=PostbackAction(
                            label='請抽我看看運勢',
                            display_text='到底抽到什麼呢?',
                            data=f'action={fortunes[2]}'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/W7nI6fg.jpg',
                        action=PostbackAction(
                            label='請抽我看看運勢',
                            display_text='到底抽到什麼呢?',
                            data=f'action={fortunes[3]}'
                        )
                    )
                ]
            )
        )
        # Reply with the image carousel template message first
        line_bot_api.reply_message(event.reply_token, image_carousel_template_message)

        # buttons_template_message_weather = TemplateSendMessage(
        #     alt_text='天氣調查',
        #     template=ButtonsTemplate(
        #         thumbnail_image_url='https://img.lovepik.com/png/20231015/Cartoon-image-thunderstorm-weather-raindrop-cartoon-images-lightning_215956_wh1200.png',
        #         title='今日天氣你覺得如何?',
        #         text='請選擇適合的形容詞',
        #         actions=[
        #             MessageAction(
        #                 label='悶熱',
        #                 display_text='悶熱',
        #                 text='今天確實很悶熱耶'
        #             ),
        #             MessageAction(
        #                 label='濕冷',
        #                 display_text='濕冷',
        #                 text='今天確實很濕冷耶'
        #             ),
        #             MessageAction(
        #                 label='溫暖',
        #                 display_text='溫暖',
        #                 text='今天確實很溫暖耶'
        #             ),
        #             MessageAction(
        #                 label='涼爽',
        #                 display_text='涼爽',
        #                 text='今天確實很涼爽耶'
        #             )
        #         ]
        #     )
        # )
        # # Then push the buttons template message
        # line_bot_api.push_message(user_id, buttons_template_message_weather)

    elif message in ['悶熱', '濕冷', '溫暖', '涼爽']:
        user_responses[user_id]['weather'] = message

        buttons_template_message_mood = TemplateSendMessage(
            alt_text='心情調查',
            template=ButtonsTemplate(
                thumbnail_image_url='https://www.mindfulness.com.tw/upfile/editor/images/8.png',
                title='今日心情如何?',
                text='請選擇適合的形容詞',
                actions=[
                    MessageAction(
                        label='很好',
                        display_text='GOOD',
                        text='讚!'
                    ),
                    MessageAction(
                        label='不好不壞',
                        display_text='SOSO',
                        text='讚!'
                    ),
                    MessageAction(
                        label='很差',
                        display_text='Bad',
                        text='還好吧?'
                    )
                ]
            )
        )
        # Then push the buttons template message
        line_bot_api.push_message(user_id, buttons_template_message_mood)

    elif message in ['讚!','還好吧?']:
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
        f"請給出一個適合的行程，1. 夜生活 、2.酒吧、3. KTV唱歌、4. 夜店。並且推薦一個適合的地點。請利用20字以內說明 1. 適合的行程 2. 地點 3. 該地點的 google map 連結"
    )

    recommendation = gpt4_message(prompt)

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