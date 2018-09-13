from linebot import LineBotApi
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, StickerSendMessage
from linebot.models import (
    TemplateSendMessage, ButtonsTemplate,
    PostbackTemplateAction, MessageTemplateAction,
    URITemplateAction, DatetimePickerTemplateAction,
    ConfirmTemplate, CarouselTemplate, CarouselColumn
)
from datetime import datetime
import re
from pymongo import MongoClient
line_bot_api = LineBotApi('UArF+E0FP1BrcUkI1Yl8iyHBOJOIYtPCzsQNGm5IcGvqoLyoQ/0/VpAgN0MadGq/Fal5OF0//W1ysC1CJivBfiA8PSrG2hrXAtl9x/mo9jpjULOiDVYBeUo/M68JDiypliqinYRB8/WEGVQANy4yhgdB04t89/1O/w1cDnyilFU=')
Webhook_URL = "https://c20a8c85.ngrok.io"
Ourweb="http://13.112.246.238:8000/politician/"

#######################################################
politician_dict={
   "柯文哲":"136845026417486",
   "蔡英文":"46251501064",
   "李錫錕":"360151611020961",
   "黃國昌":"449664581882455",
   "侯友宜":"261813197541354",
   "江啟臣":"191690867518507",
   "陳其邁":"122936517768637",
   "鄭文燦":"333058400178329",
   "賴清德":"152472278103133",
   "洪慈庸":"852926604746233",
   "朱立倫":"10150145806225128",
   "林昶佐":"365320250345879",
   "蔣萬安":"805460986214082",
   "姚文智":"1380211668909443",
   "蔡正元": "184799244894343"
}
politician_names = politician_dict.keys()

kmt_politician_dict={
   "朱立倫":"10150145806225128",
   "侯友宜":"261813197541354",
   "蔣萬安":"805460986214082",
   "蔡正元":"184799244894343",
   "江啟臣":"191690867518507"
}
kmt_politician_names = kmt_politician_dict.keys()

dpp_politician_dict={
   "蔡英文":"46251501064",
   "賴清德":"152472278103133",
   "鄭文燦":"333058400178329",
   "陳其邁":"122936517768637",
   "姚文智":"1380211668909443"
}
dpp_politician_names = dpp_politician_dict.keys()

power_politician_dict={
   "黃國昌":"449664581882455",
   "洪慈庸":"852926604746233",
   "林昶佐":"365320250345879"
}
power_politician_names = power_politician_dict.keys()

noparty_politician_dict={
   "柯文哲":"136845026417486",
   "李錫錕":"360151611020961",
}
noparty_politician_names = noparty_politician_dict.keys()
#######################################################
time=[]
if len(time)>10:
    del time[0:5]

class MongoConnection(object):
    client = None

    @staticmethod
    def getConnection():
        if MongoConnection.client is None:
            MongoConnection.client = MongoClient("mongodb://10.120.37.108:27017")
            return MongoConnection.client
        else:
            return MongoConnection.client
def db(politician_name,start="2017-01-01",end="2017-12-31"):
    data_list = []
    start_time = datetime.strptime(start, "%Y-%m-%d")
    end_time = datetime.strptime(end, "%Y-%m-%d")
    client = MongoConnection.getConnection()
    db = client["project"]
    dbs = client["projects"]
    collection_comments = db["comments"]
    collection_events = dbs["events"]

    ####events
    event = list(collection_events.find({"politician_id": politician_dict[politician_name], "created_time": {"$gte":start_time, "$lte": end_time}},
                                        {"_id": 0, "diff": 1, "events_name": 1}).sort("diff", -1))[1]

    s = event["events_name"] + "\n" + "延燒天數:" + str(event["diff"]) + " 天"
    ####hot
    hot = collection_comments.count({"politician_id": politician_dict[politician_name],
                                     "created_time": {"$gte": start_time, "$lte": end_time}})
    ####gender

    negative_comments_number = collection_comments.count(
        {"politician_id": politician_dict[politician_name], "created_time": {"$gte":start_time, "$lte": end_time},
         "score_NN": {"$lt": -0.1}})
    central_comments_number = collection_comments.count(
        {"politician_id": politician_dict[politician_name], "created_time": {"$gte":start_time, "$lte": end_time},
         "score_NN": {"$lte": 0.1, "$gte": -0.1}})
    positive_comments_number = collection_comments.count(
        {"politician_id": politician_dict[politician_name], "created_time": {"$gte":start_time, "$lte": end_time},
         "score_NN": {"$gt": 0.1}})
    total_comments_number = negative_comments_number + central_comments_number + positive_comments_number

    positive_comments_persent = positive_comments_number / total_comments_number
    central_comments_persent = central_comments_number / total_comments_number
    negative_comments_persent = negative_comments_number / total_comments_number

    politician_id = politician_dict[politician_name]

    data_list.append((politician_name,
                      hot,
                      round(positive_comments_persent*100, 2),
                      round(central_comments_persent * 100, 2),
                      round(negative_comments_persent*100, 2),
                      politician_id,
                      s
                      ))
    return data_list
#######################################################
def kmt_carousel_template_message(start="2017-01-01",end="2017-12-31"):
    kmt_data = []
    for politician_name in kmt_politician_dict:
        kmt_data.append(db(politician_name, start, end)[0])
    print(kmt_data)
    kmt_carousel_template_message = TemplateSendMessage(
    alt_text='Carousel template',
    template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(kmt_data[0][5]),
                title='{}'.format(kmt_data[0][0]),
                text='想了解更多資訊\n請點擊『更多』',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(kmt_data[0][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(kmt_data[0][2], kmt_data[0][3], kmt_data[0][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+kmt_data[0][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(kmt_data[1][5]),
                title='{}'.format(kmt_data[1][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(kmt_data[1][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(kmt_data[1][2], kmt_data[1][3], kmt_data[1][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+kmt_data[1][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(kmt_data[2][5]),
                title='{}'.format(kmt_data[2][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(kmt_data[2][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(kmt_data[2][2], kmt_data[2][3], kmt_data[2][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+kmt_data[2][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(kmt_data[3][5]),
                title='{}'.format(kmt_data[3][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(kmt_data[3][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(kmt_data[3][2], kmt_data[3][3], kmt_data[3][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+kmt_data[3][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(kmt_data[4][5]),
                title='{}'.format(kmt_data[4][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(kmt_data[4][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(kmt_data[4][2], kmt_data[4][3], kmt_data[4][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+kmt_data[4][5]
                    )

                ]
            )
        ]))
    return kmt_carousel_template_message
######################################################
def dpp_carousel_template_message(start="2017-01-01",end="2017-12-31"):
    dpp_data = []
    for politician_name in dpp_politician_dict:
        dpp_data.append(db(politician_name, start, end)[0])
    dpp_carousel_template_message = TemplateSendMessage(
    alt_text='Carousel template',

    template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(dpp_data[0][5]),
                title='{}'.format(dpp_data[0][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(dpp_data[0][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(dpp_data[0][2], dpp_data[0][3], dpp_data[0][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+dpp_data[0][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(dpp_data[1][5]),
                title='{}'.format(dpp_data[1][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(dpp_data[1][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(dpp_data[1][2], dpp_data[1][3], dpp_data[1][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+dpp_data[1][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(dpp_data[2][5]),
                title='{}'.format(dpp_data[2][0]),
                text='想了解更多資訊\n請點擊『更多』 ',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(dpp_data[2][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(dpp_data[2][2], dpp_data[2][3], dpp_data[2][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+dpp_data[2][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(dpp_data[3][5]),
                title='{}'.format(dpp_data[3][0]),
                text='想了解更多資訊\n請點擊『更多』',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(dpp_data[3][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(dpp_data[3][2], dpp_data[3][3], dpp_data[3][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+dpp_data[3][5]
                    )

                ]
            ),
            CarouselColumn(
                thumbnail_image_url=Webhook_URL + '/static/images/{}'.format(dpp_data[4][5]),
                title='{}'.format(dpp_data[4][0]),
                text='想了解更多資訊\n請點擊『更多』',
                actions=[
                    PostbackTemplateAction(
                        label='臉書粉絲回應',
                        data="{} 則回應數".format(dpp_data[4][1])
                    ),
                    PostbackTemplateAction(
                        label='情緒正負向',
                        data="正向:{}% \n中立:{}% \n負向:{}%".format(dpp_data[4][2], dpp_data[4][3],
                                                               dpp_data[4][4])
                    ),
                    URITemplateAction(
                        label='更多',
                        uri=Ourweb+dpp_data[4][5]
                    )

                ]
            ),
        ]))
    return dpp_carousel_template_message
######################################################
def power_carousel_template_message(start="2017-01-01",end="2017-12-31"):
    power_data = []
    for politician_name in power_politician_dict:
        power_data.append(db(politician_name, start, end)[0])
    power_carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(power_data[0][5]),
                    title='{}'.format(power_data[0][0]),
                    text='想了解更多資訊\n請點擊『更多』 ',
                    actions=[
                        PostbackTemplateAction(
                            label='臉書粉絲回應',
                            data="{} 則回應數".format(power_data[0][1])
                        ),
                        PostbackTemplateAction(
                            label='情緒正負向',
                            data="正向:{}% \n中立:{}% \n負向:{}%".format(power_data[0][2], power_data[0][3], power_data[0][4])
                        ),
                        URITemplateAction(
                            label='更多',
                            uri=Ourweb+power_data[0][5]
                        )

                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(power_data[1][5]),
                    title='{}'.format(power_data[1][0]),
                    text='想了解更多資訊\n請點擊『更多』 ',
                    actions=[
                        PostbackTemplateAction(
                            label='臉書粉絲回應',
                            data="{} 則回應數".format(power_data[1][1])
                        ),
                        PostbackTemplateAction(
                            label='情緒正負向',
                            data="正向:{}% \n中立:{}% \n負向:{}%".format(power_data[1][2], power_data[1][3], power_data[1][4])
                        ),
                        URITemplateAction(
                            label='更多',
                            uri=Ourweb+power_data[1][5]
                        )

                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(power_data[2][5]),
                    title='{}'.format(power_data[2][0]),
                    text='想了解更多資訊\n請點擊『更多』 ',
                    actions=[
                        PostbackTemplateAction(
                            label='臉書粉絲回應',
                            data="{} 則回應數".format(power_data[2][1])
                        ),
                        PostbackTemplateAction(
                            label='情緒正負向',
                            data="正向:{}% \n中立:{}% \n負向:{}%".format(power_data[2][2], power_data[2][3], power_data[2][4])
                        ),
                        URITemplateAction(
                            label='更多',
                            uri=Ourweb+power_data[2][5]
                        )

                    ]
                ),
            ]))
    return power_carousel_template_message
######################################################
def noparty_carousel_template_message(start="2017-01-01",end="2017-12-31"):
    noparty_data = []
    for politician_name in noparty_politician_dict:
        noparty_data.append(db(politician_name, start, end)[0])
    noparty_carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(noparty_data[0][5]),
                    title='{}'.format(noparty_data[0][0]),
                    text='想了解更多資訊\n請點擊『更多』',
                    actions=[
                        PostbackTemplateAction(
                            label='臉書粉絲回應',
                            data="{} 則回應數".format(noparty_data[0][1])
                        ),
                        PostbackTemplateAction(
                            label='情緒正負向',
                            data="正向:{}% \n中立:{}% \n負向:{}%".format(noparty_data[0][2], noparty_data[0][3], noparty_data[0][4])
                        ),
                        URITemplateAction(
                            label='更多',
                            uri=Ourweb+noparty_data[0][5]
                        )

                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(noparty_data[1][5]),
                    title='{}'.format(noparty_data[1][0]),
                    text='想了解更多資訊\n請點擊『更多』',
                    actions=[
                        PostbackTemplateAction(
                            label='臉書粉絲回應',
                            data="{} 則回應數".format(noparty_data[1][1])
                        ),
                        PostbackTemplateAction(
                            label='情緒正負向',
                            data="正向:{}% \n中立:{}% \n負向:{}%".format(noparty_data[1][2], noparty_data[1][3], noparty_data[1][4])
                        ),
                        URITemplateAction(
                            label='更多',
                            uri=Ourweb+noparty_data[1][5]
                        )

                    ]
                )
            ]))
    return noparty_carousel_template_message
#########################################################
def buttons_template_message(event,start="2017-01-01",end="2017-12-31"):
    btm=[]
    buttons_data = []
    for politician_name in politician_dict:
        if len(re.findall(politician_name, event)) != 0:
            buttons_data.append(db(politician_name, start, end)[0])

    for button_data in buttons_data:
        print(buttons_data)
        buttons_template_message = \
            TemplateSendMessage(
                alt_text='Buttons template',

                template=ButtonsTemplate(
                    thumbnail_image_url=Webhook_URL+'/static/images/{}'.format(button_data[5]),
                    title='{}'.format(button_data[0]),
                    text='欲知更多資訊\n請點擊更多 ',

                    actions=[
                        PostbackTemplateAction(
                            label='粉絲回應數',
                            data="{} 則回應數".format(button_data[1])
                        ),
                        PostbackTemplateAction(
                            label='情緒正負向',
                            data="正向:{}% \n中立:{}% \n負向:{}%".format(button_data[2], button_data[3], button_data[4])
                        ),
                        PostbackTemplateAction(
                            label='熱門事件關鍵字',
                            data="{}".format(button_data[6])
                        ),
                        URITemplateAction(
                            label='更多',
                            uri=Ourweb
                        )

                    ]
                )
            )
        btm.append(buttons_template_message)

    return btm
######################################################
party_buttons_template_message = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        thumbnail_image_url=Webhook_URL+'/static/images/party',
        title='選擇你想知道的人物政黨',
        text='Please select',
        actions=[
            PostbackTemplateAction(
                label='國民黨',
                data='國民黨'
            ),
            PostbackTemplateAction(
                label='民進黨',
                data='民進黨'
            ),
            PostbackTemplateAction(
                label='時代力量',
                data='時代力量'
            ),
            PostbackTemplateAction(
                label='無黨籍',
                data='無黨籍'
            )
        ]
    )
)
######################################################
time_buttons_template_message = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        thumbnail_image_url=Webhook_URL+'/static/images/time',
        title='請選擇時間區間',
        text='Please select',
        actions=[
            DatetimePickerTemplateAction(
                label="開始時間",
                data="輸入結束時間",
                mode="date",
                initial="2017-08-01",
                min="2017-01-01",
                max="2017-12-31"
            ),
            DatetimePickerTemplateAction(
                label="結束時間",
                data="輸入想查詢的『政治人名』或『政黨』",
                mode="date",
                initial="2017-08-01",
                min="2017-01-01",
                max="2017-12-31"
            ),

        ]
    )
)
######################################################

def response(event):
    if "你好" in event.message.text:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您好，\n歡迎使用聊天機器人"))
        line_bot_api.push_message(event.source.user_id,
                                  TextSendMessage(text="輸入想查詢的『政治人名』或『政黨』"))
        line_bot_api.push_message(event.source.user_id,
                                  TextSendMessage(text="輸入『時間』查詢更詳細的資料"))
        line_bot_api.reply_message(event.reply_token, time_buttons_template_message)
    elif "時間" in event.message.text:
        line_bot_api.reply_message(event.reply_token, time_buttons_template_message)
    elif "政黨" in event.message.text:
        line_bot_api.reply_message(event.reply_token, party_buttons_template_message)
    elif time :
        if "國民黨" in event.message.text:
            line_bot_api.reply_message(event.reply_token, kmt_carousel_template_message(time[-2],time[-1]))
        if "民進黨" in event.message.text:
            line_bot_api.reply_message(event.reply_token, dpp_carousel_template_message(time[-2],time[-1]))
        if "時代力量" in event.message.text:
            line_bot_api.reply_message(event.reply_token, power_carousel_template_message(time[-2],time[-1]))
        if "無黨籍" in event.message.text:
            line_bot_api.reply_message(event.reply_token, noparty_carousel_template_message(time[-2],time[-1]))

        for data in buttons_template_message(event.message.text,time[-2],time[-1]):
            line_bot_api.push_message(event.source.user_id, data)
        if len(buttons_template_message(event.message.text))==0:
            line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id='2', sticker_id='149'))
    elif len(time) <= 1:
        if "國民黨" in event.message.text:
            line_bot_api.reply_message(event.reply_token, kmt_carousel_template_message())
        if "民進黨" in event.message.text:
            line_bot_api.reply_message(event.reply_token, dpp_carousel_template_message())
        if "時代力量" in event.message.text:
            line_bot_api.reply_message(event.reply_token, power_carousel_template_message())
        if "無黨籍" in event.message.text:
            line_bot_api.reply_message(event.reply_token, noparty_carousel_template_message())


        for data in buttons_template_message(event.message.text):

            if data:
                line_bot_api.push_message(event.source.user_id, data)
                print(data)
        if len(buttons_template_message(event.message.text))==0:
            line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id='2', sticker_id='149'))



def postback(event):

    if event.postback.data == "輸入結束時間":
        # global start_temp
        start_temp = event.postback.params["date"]
        time.append(start_temp)
    if event.postback.data == "輸入想查詢的『政治人名』或『政黨』":
        # global end_temp
        end_temp = event.postback.params["date"]
        if time[-1] <= end_temp:
            time.append(end_temp)
        else:
            line_bot_api.push_message(event.source.user_id, StickerSendMessage(package_id='2', sticker_id='38'))
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="時間輸入錯誤，請重新輸入"))
            line_bot_api.reply_message(event.reply_token, time_buttons_template_message)
            del time[:]
    print(time)
    if time:
        if event.postback.data == "國民黨":
            line_bot_api.reply_message(event.reply_token, kmt_carousel_template_message(time[-2],time[-1]))
        if event.postback.data == "民進黨":
            line_bot_api.reply_message(event.reply_token, dpp_carousel_template_message(time[-2],time[-1]))
        if event.postback.data == "時代力量":
            line_bot_api.reply_message(event.reply_token, power_carousel_template_message(time[-2],time[-1]))
        if event.postback.data == "無黨籍":
            line_bot_api.reply_message(event.reply_token, noparty_carousel_template_message(time[-2],time[-1]))
    else:
        if event.postback.data == "國民黨":
            line_bot_api.reply_message(event.reply_token, kmt_carousel_template_message())
        if event.postback.data == "民進黨":
            line_bot_api.reply_message(event.reply_token, dpp_carousel_template_message())
        if event.postback.data == "時代力量":
            line_bot_api.reply_message(event.reply_token, power_carousel_template_message())
        if event.postback.data == "無黨籍":
            line_bot_api.reply_message(event.reply_token, noparty_carousel_template_message())

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.postback.data))
