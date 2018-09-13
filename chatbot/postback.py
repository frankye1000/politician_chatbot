from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,PostbackEvent
line_bot_api = LineBotApi('***************************************************')

def postback(event):
    if event.postback.data == "國民黨":
        line_bot_api.reply_message(event.reply_token, kmt_carousel_template_message)
    if event.postback.data == "民進黨":
        line_bot_api.reply_message(event.reply_token, dpp_carousel_template_message)
    if event.postback.data == "時代力量":
        line_bot_api.reply_message(event.reply_token, power_carousel_template_message)
    if event.postback.data == "無黨籍":
        line_bot_api.reply_message(event.reply_token, noparty_carousel_template_message)
