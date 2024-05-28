import random

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
                            data=f'action={fortunes[0]}'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/W7nI6fg.jpg',
                        action=PostbackAction(
                            label='請抽我看看運勢',
                            text='到底抽到什麼呢?',
                            data=f'action={fortunes[1]}'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/W7nI6fg.jpg',
                        action=PostbackAction(
                            label='請抽我看看運勢',
                            text='到底抽到什麼呢?',
                            data=f'action={fortunes[2]}'
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