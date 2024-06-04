from linebot.models import *

def baseOfalcohol():
    buttons_template_message = TemplateSendMessage(
        alt_text='請選擇您喜歡喝的調酒基底',
        template=ButtonsTemplate(
            title='請選擇您喜歡喝的調酒基底',
            text='請選擇一個選項',
            actions=[
                PostbackAction(
                    label='烈酒基底',
                    display_text='烈酒基底',
                    data='alcohol_action=base&value=烈酒基底'
                ),
                PostbackAction(
                    label='葡萄酒基底',
                    display_text='葡萄酒基底',
                    data='alcohol_action=base&value=葡萄酒基底'
                ),
                PostbackAction(
                    label='啤酒基底',
                    display_text='啤酒基底',
                    data='alcohol_action=base&value=啤酒基底'
                ),
                PostbackAction(
                    label='利口酒基底',
                    display_text='利口酒基底',
                    data='alcohol_action=base&value=利口酒基底'
                )
            ]
        )
    )
    return buttons_template_message

def degreeOfalcohol():
    buttons_template_message = TemplateSendMessage(
        alt_text='請選擇您對特定成分或酒精度數的偏好或限制',
        template=ButtonsTemplate(
            title='您對特定成分或酒精度數的偏好或限制',
            text='請選擇一個選項',
            actions=[
                PostbackAction(
                    label='高度數酒品',
                    display_text='高度數酒品',
                    data='action=preference&value=高度數酒品'
                ),
                PostbackAction(
                    label='低度數酒品',
                    display_text='低度數酒品',
                    data='action=preference&value=低度數酒品'
                ),
                PostbackAction(
                    label='限制酒精攝入',
                    display_text='限制酒精攝入',
                    data='action=preference&value=限制酒精攝入'
                )
            ]
        )
    )
    return buttons_template_message

def flavorOfalcohol():
    flex_message = FlexSendMessage(
        alt_text='請選擇您喜歡喝的調酒風味',
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "請選擇您喜歡喝的調酒風味",
                        "weight": "bold",
                        "size": "md",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "香甜的",
                            "data": "action=flavor&value=香甜的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "酸味的",
                            "data": "action=flavor&value=酸味的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "濃烈的",
                            "data": "action=flavor&value=濃烈的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "清爽的",
                            "data": "action=flavor&value=清爽的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "不知道，想嘗試新口味",
                            "data": "action=flavor&value=不知道，想嘗試新口味"
                        }
                    }
                ]
            }
        }
    )
    return flex_message