from flask import Flask, request, abort

import json

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    TextMessage
   
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessageContent,
)

import os
app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


# 載入外部的回應資料
with open('responses.json', 'r', encoding='utf-8') as f:
    response_dict = json.load(f)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 加入好友事件
@line_handler.add(FollowEvent)
def handle_follow(event):
    print(f'Got {event.type} event')

# # 訊息事件
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text

   # 收集所有匹配的回應
    matched_responses = [response for keyword, response in response_dict.items() if keyword in user_message]

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if matched_responses:
            # 如果有匹配，將所有結果顯示
            messages = [TextMessage(text=response) for response in matched_responses]
        else:
            # 沒有匹配時顯示預設訊息
            messages = [TextMessage(text="LineBot自動回覆中")]

        # 傳送回覆
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )
            
    




# # 訊息事件
# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         user_message = event.message.text
#         if event.message.text == 'postback':
#             buttons_template = ButtonsTemplate(
#                 title='Postback Sample',
#                 text='Postback 開始',
#                 actions=[
#                     PostbackAction(label='Postback Action', text='Postback Action Button Clicked!', data='postback'),
#                 ])
#             template_message = TemplateMessage(
#                 alt_text='Postback Sample',
#                 template=buttons_template
#             )
#             line_bot_api.reply_message(
#                 ReplyMessageRequest(
#                     reply_token=event.reply_token,
#                     messages=[template_message]
#                 )
#             )
#         elif event.message.text == 'abc':
#             line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text='LineBot自動回覆中')]
#             )
#             )
#         elif '你好' in user_message or '哈囉' in user_message:
#             line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text="你好！很高興認識你，可以如何幫助你呢？")]
#             )
#             )
#         elif '珍奶' in user_message or '飲料' in user_message:
#             line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text="哇!好喝，一定很愉悅！")]
#             )
#             )
        
@line_handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback':
        print('Postback event is triggered')


if __name__ == "__main__":
    app.run()
