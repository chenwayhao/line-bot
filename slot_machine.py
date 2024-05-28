import random
from linebot.models import *

def image_carousel_template_message():
    fortunes = ['大吉', '吉', '凶', '大凶']
    random.shuffle(fortunes)
    
    fortune_message = TemplateSendMessage(
        alt_text='請抽籤',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        text='到底抽到什麼呢?',
                        data=f'fortune_action={fortunes[0]}'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        text='到底抽到什麼呢?',
                        data=f'fortune_action={fortunes[1]}'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        text='到底抽到什麼呢?',
                        data=f'fortune_action={fortunes[2]}'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        text='到底抽到什麼呢?',
                        data=f'action={fortunes[3]}'
                    )
                )
            ]
        )
    )
    return fortune_message

def buttons_template_message_weather():
    weather = ['悶熱', '濕冷', '溫暖', '涼爽']

    weather_message = TemplateSendMessage(
        alt_text='天氣調查',
        template=ButtonsTemplate(
            thumbnail_image_url='https://img.lovepik.com/png/20231015/Cartoon-image-thunderstorm-weather-raindrop-cartoon-images-lightning_215956_wh1200.png',
            title='今日天氣你覺得如何?',
            text='請選擇適合的形容詞',
            actions=[
                MessageAction(
                    label='悶熱',
                    text='悶熱',
                    data = f'weather_action={weather[0]}'
                ),
                MessageAction(
                    label='濕冷',
                    text='濕冷',
                    data = f'weather_action={weather[1]}'
                ),
                MessageAction(
                    label='溫暖',
                    text='溫暖',
                    data = f'weather_action={weather[2]}'
                ),
                MessageAction(
                    label='涼爽',
                    text='涼爽',
                    data = f'weather_action={weather[3]}'
                )
            ]
        )
    )
    return weather_message
        
def buttons_template_message_mood():
    mood = ['很好！', '不好不壞！', '很差！']

    mood_message = TemplateSendMessage(
        alt_text='心情調查',
        template=ButtonsTemplate(
            thumbnail_image_url='https://www.mindfulness.com.tw/upfile/editor/images/8.png',
            title='今日心情如何?',
            text='請選擇適合的形容詞',
            actions=[
                MessageAction(
                    label='很好',
                    text='很好！',
                    data = f'mood_action={mood[0]}'
                ),
                MessageAction(
                    label='不好不壞',
                    text='不好不壞！',
                    data = f'mood_action={mood[1]}'
                ),
                MessageAction(
                    label='很差',
                    text='很差！',
                    data = f'mood_action={mood[2]}'
                )
            ]
        )
    )
    return mood_message

# def get_recommendation(user_responses):
#     response = user_responses.get(user_id, {})
#     fortune = response.get('fortune', 'unknown')
#     weather = response.get('weather', 'unknown')
#     mood = response.get('mood', 'unknown')

#     print(fortune, weather, mood)


#     # Generate a prompt for ChatGPT
#     prompt = (
#         f"基於以下條件，給出一個夜生活推薦：\n"
#         f"運勢：{fortune}\n"
#         f"天氣：{weather}\n"
#         f"心情：{mood}\n"
#         f"請給出一個適合的行程，1. 夜生活 、2.酒吧、3. KTV唱歌、4. 夜店。並且推薦一個台北適合的地點。請利用20字以內說明 1. 適合的行程 2. 地點 3. 地點的 google map 連結(https://www.google.com/maps/search/店名)"
#     )

#     return prompt
