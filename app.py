from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai


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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # message = TextSendMessage(text=event.message.text)
    # line_bot_api.reply_message(event.reply_token, message)
    user_message = event.message.text


    #gpt4 version  
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages = [{"role":"user","content":user_message}],
        temperature = 0.5,
        max_tokens = 150
    )
    gpt_reply = response.choices[0]['message']['content'].replace('。','').strip()


    # response = openai.ChatCompletion.create(
    #     model = 'gpt-3.5-turbo-0125',
    #     messages = [{"role":"user","content":user_message}],
    #     temperature = 0.5,
    #     max_tokens = 250    
    # )

    # gpt_reply = response.choices[0]['message']['content']


    # gpt_reply1 = response.choices
    # print(gpt_reply1)
    #Create a TextSendMessage object with the response
    message = TextSendMessage(text=gpt_reply)

    # Reply to the user
    line_bot_api.reply_message(event.reply_token, message)
# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     if event.message.text == '位置':
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text="請傳送您的位置資訊")
#         )


# @handler.add(MessageEvent, message=LocationMessage)
# def handle_location_message(event):
#     latitude = event.message.latitude
#     longitude = event.message.longitude

#     reply_text = f"您的位置是：\n緯度：{latitude}\n經度：{longitude}"
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# @app.route("/richmenu", methods=['GET'])
# def get_richmenu_list():
#     # 獲取圖文選單列表
#     rich_menu_list = line_bot_api.get_rich_menu_list()
#     rich_menu_ids = [rich_menu.rich_menu_id for rich_menu in rich_menu_list]
#     return {'rich_menu_ids': rich_menu_ids}, 200  # 返回圖文選單 ID 列表

# @handler.add(PostbackEvent)
# def handle_postback(event):
#     # 處理圖文選單點擊事件
#     if event.message.text == '鄰近店家':
#         confirm_template = ConfirmTemplate(
#             text='您要分享您的位置信息嗎？',
#             actions=[
#                 MessageAction(label='是', text='分享位置'),
#                 MessageAction(label='否', text='取消')
#             ]
#         )
#         template_message = TemplateSendMessage(
#             alt_text='確認對話框',
#             template=confirm_template
#         )
#         line_bot_api.reply_message(event.reply_token, template_message)

# @handler.add(MessageEvent, message=LocationMessage)
# def handle_location_message(event):
#     # 處理用戶發送的位置信息
#     latitude = event.message.latitude  # 獲取緯度
#     longitude = event.message.longitude  # 獲取經度

#     # 組合回應的文字信息，包含用戶的位置經緯度
#     reply_text = f"您的位置是：\n緯度：{latitude}\n經度：{longitude}"
#     # 回應用戶位置經緯度信息
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))



import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)