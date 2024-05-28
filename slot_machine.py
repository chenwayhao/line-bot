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
        
    weather_message = TemplateSendMessage(
        alt_text='天氣調查',
        template=ButtonsTemplate(
            thumbnail_image_url='https://img.lovepik.com/png/20231015/Cartoon-image-thunderstorm-weather-raindrop-cartoon-images-lightning_215956_wh1200.png',
            title='今日天氣你覺得如何?',
            text='請選擇適合的形容詞',
            actions=[
                MessageAction(
                    label='悶熱',
                    # display_text='悶熱',
                    text='悶熱'
                ),
                MessageAction(
                    label='濕冷',
                    # display_text='濕冷',
                    text='濕冷'
                ),
                MessageAction(
                    label='溫暖',
                    # display_text='溫暖',
                    text='溫暖'
                ),
                MessageAction(
                    label='涼爽',
                    # display_text='涼爽',
                    text='涼爽'
                )
            ]
        )
    )
    return weather_message
        
