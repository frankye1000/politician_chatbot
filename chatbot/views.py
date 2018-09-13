from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FollowEvent,TemplateSendMessage,StickerSendMessage,PostbackEvent,TextSendMessage
from .robot import response, postback



# Create your views here.
handler = WebhookHandler('************')
line_bot_api = LineBotApi('***********************************************')


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    response(event)

@handler.add(PostbackEvent)
def handle_postback_message(event):
    # print(event.postback.data)
    postback(event)

    # line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id='1', sticker_id='1'))


@handler.add(FollowEvent)
def handle_follow_event(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您好，\n歡迎使用聊天機器人"))
    line_bot_api.push_message(event.source.user_id, StickerSendMessage(package_id='1', sticker_id='13'))
    line_bot_api.push_message(event.source.user_id,
                               TextSendMessage(text="可直接輸入人名、政黨名"))
    line_bot_api.push_message(event.source.user_id,
                               TextSendMessage(text="或輸入『時間』查詢更詳細的資料"))
