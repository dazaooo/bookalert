from bs4 import BeautifulSoup
from io import StringIO
from datetime import datetime

import requests
import schedule
import time
import json
import sys

Saturday = 5
originInfoItemIndex = 0
saturdayTimestap = 0

# 如果是周六，获取当前时间戳
def init(): 
    global Saturday
    currentday = datetime.today().weekday()

    if currentday == Saturday:
        saturdayTimestap = int(time.time())
        print(saturdayTimestap)

    else:
        print('当前不是周六')
        print('脚本启动，将继续检测')
        return

    schedule.every(10).seconds.do(requestPlace)

    while True:
        schedule.run_pending()
        time.sleep(1)

def requestPlace():
    global originInfoItemIndex
    global saturdayTimestap

    url = 'https://xihuwenti.juyancn.cn/wechat/product/details?id=753&time=' + str(saturdayTimestap)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    timeLocal = time.localtime(1642348800)
    realTime = time.strftime("%Y-%m-%d", timeLocal)

    print(realTime)

    infolist = []
    # todo: 对相同场馆时间段进行分组
    for tag in soup.find_all('li', 'can-select'):
        name = tag.get('data-hall_name')
        timestart = tag.get('data-start')
        timeend = tag.get('data-end')
        if name:
            infolist.append({"name": name, "timestart": timestart, "timeend": timeend})

    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=robot.key'

    headers = {'content-type': "application/json", 'Authorization': 'APP appid = **,token = **'} 
    
    originInfoItemIndex = originInfoItemIndex + 1

    print(infolist)

    infoItem = infolist[originInfoItemIndex]
    print(infoItem)

    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": '西体3楼竞技馆\n' + 
            '>预定日期: <font color=\"warning\">'+ realTime +'</font>\n'
            '>预定场馆: <font color=\"warning\">'+ infoItem['name'] +'</font>\n'
            '>时间区间: <font color=\"info\">'+ infoItem['timestart'] + '-' + infoItem['timeend'] +'</font>'
        }
    }

    wechatresponse = requests.post(url, data = json.dumps(body), headers = headers)