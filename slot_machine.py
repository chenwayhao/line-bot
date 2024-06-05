import random
from linebot.models import *
import app

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
                        display_text='您抽到的是:{fortunes[0]}?',
                        data=f'fortune_action={fortunes[0]}'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        display_text=f'您抽到的是:{fortunes[1]}',
                        data=f'fortune_action={fortunes[1]}'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        display_text=f'您抽到的是:{fortunes[2]}?',
                        data=f'fortune_action={fortunes[2]}'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/W7nI6fg.jpg',
                    action=PostbackAction(
                        label='請抽我看看運勢',
                        display_text=f'您抽到的是:{fortunes[3]}?',
                        data=f'fortune_action={fortunes[3]}'
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
                PostbackAction(
                    label='悶熱',
                    display_text='悶熱',
                    data = f'weather_action={weather[0]}'
                ),
                PostbackAction(
                    label='濕冷',
                    display_text='濕冷',
                    data = f'weather_action={weather[1]}'
                ),
                PostbackAction(
                    label='溫暖',
                    display_text='溫暖',
                    data = f'weather_action={weather[2]}'
                ),
                PostbackAction(
                    label='涼爽',
                    display_text='涼爽',
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
                PostbackAction(
                    label='很好',
                    display_text='很好！',
                    data = f'mood_action={mood[0]}'
                ),
                PostbackAction(
                    label='不好不壞',
                    display_text='不好不壞！',
                    data = f'mood_action={mood[1]}'
                ),
                PostbackAction(
                    label='很差',
                    display_text='很差！',
                    data = f'mood_action={mood[2]}'
                )
            ]
        )
    )
    return mood_message


user_responses = {}
def getslots_recommendation(user_id):
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
        f"請給出一個適合的夜生活建議，要怎麼樣度過夜生活。可能的選項有: 1.酒吧喝酒、2. 去KTV唱歌、3. 去夜店 4. 去餐酒館吃飯。並且推薦一個台北適合的地址。請利用20字以內說明 1. 適合的行程 2. 地點 3. 地點的 google map 連結(https://www.google.com/maps/search/店名的空格以+代替)"
    )

    recommendation = app.gpt35_message(prompt)

    return recommendation
