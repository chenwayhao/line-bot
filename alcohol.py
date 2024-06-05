from linebot.models import *
import app

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
                    data='base_action=烈酒基底'
                ),
                PostbackAction(
                    label='葡萄酒基底',
                    display_text='葡萄酒基底',
                    data='base_action=葡萄酒基底'
                ),
                PostbackAction(
                    label='啤酒基底',
                    display_text='啤酒基底',
                    data='base_action=啤酒基底'
                ),
                PostbackAction(
                    label='利口酒基底',
                    display_text='利口酒基底',
                    data='base_action=利口酒基底'
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
                    data='preference_action=高度數酒品'
                ),
                PostbackAction(
                    label='低度數酒品',
                    display_text='低度數酒品',
                    data='preference_action=低度數酒品'
                ),
                PostbackAction(
                    label='限制酒精攝入',
                    display_text='限制酒精攝入',
                    data='preference_action=限制酒精攝入'
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
                            "data": "flavor_action=香甜的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "酸味的",
                            "data": "flavor_action=酸味的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "濃烈的",
                            "data": "flavor_action=濃烈的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "清爽的",
                            "data": "flavor_action=清爽的"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "不知道，想嘗試新口味",
                            "data": "flavor_action=不知道，想嘗試新口味"
                        }
                    }
                ]
            }
        }
    )
    return flex_message

user_responses = {}
def getalcohol_recommendation(user_id):
    response = user_responses.get(user_id, {})
    base = response.get('base', 'unknown')
    preference = response.get('preference', 'unknown')
    flavor = response.get('flavor', 'unknown')
    
    print(base, preference, flavor)

    # Generate a prompt for ChatGPT
    prompt = (
        f"基於以下條件，給出一個調酒推薦：\n"
        f"基底：{base}\n"
        f"偏好或限制：{preference}\n"
        f"風味：{flavor}\n"
        f"請給出一個適合的調酒推薦。"
    )

    recommendation = app.gpt35_message(prompt)

    return recommendation

