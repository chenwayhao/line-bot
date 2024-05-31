import app
from linebot.models import *

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

def getnearby_recommendation(latitude, longitude):
    # 使用 ChatGPT 來生成查詢字串
    # map_prompt = (
    #     f"請列出經緯度 {latitude}, {longitude} 附近的五家餐酒館，格式如下：\n" \
    #     f"1. 餐酒館名稱\n地址：餐酒館地址\nGoogle評分：評分\n"
    # )
    prompt =( f'請列出經緯度{latitude},{longitude} 附近的五家餐酒館：'
        f'(利用https://www.google.com/maps/search/bistro/@經緯度)'
        f'1. 餐廳名稱 2. 餐廳地址 3. 餐廳 google map 評分'
    )
    # 調用 ChatGPT 函式來處理查詢字串
    map_recommendation = app.gpt35_message(prompt)

    return map_recommendation

