
import requests
import json
import datetime
import csv

noticeUrl=''
#星期枚举
weekDict={
    '1': '星期一',
    '2': '星期二',
    '3': '星期三',
    '4': '星期四',
    '5': '星期五',
    '6': '星期六',
    '0': '星期天',
}
'''
从读取日程，文件格式：group,name,mobile
如果日常排期，group值为大于等于0的int型，如果指定排期日，则为yyyy-MM-dd格式字串
如果一个group有多个同学，则为多条记录
返回Bean的格式为
{
    "normalGroup":[
        {
            0:[
                    {
                        "group":"1",
                        "name":"",
                        "mobile":""
                    }
                    ...
                ],
            ....
        ],
    "speciallyGroup":[
            {
                "2020-06-23":[
                        {
                            "group":"2020-06-23",
                            "name":"",
                            "mobile":""
                        },
                        ...
                    ],
                ...
            }
        ]
}
'''
def loadCalendarFromCsv():
    #日常排班组
    normalGroup = {};
    #特定日期排班组
    speciallyGroup = {};
    #打开排期配置文件
    with open("dutyCalendar.csv", newline='') as csvfile:
        '''
        以字典方式读取csv文件
        文件中的第一行会被当作key
        数据从第二行开始读取，并根据所在列匹配的key，组成map
        固定格式为：group,name,mobile
        '''
        reader = csv.DictReader(csvfile)
        for row in reader:
            #读取组标识
            index = row["group"]
            #如果用户名为空，则继续下一行
            if (row["name"]) == "":
                continue;
            #判断是否数字group
            if (index.isdigit()):
                #如果是数字，则归入日常排期组
                insertIntoGroup(row, int(index)-1, normalGroup)
            else:
                #如果非数字，即为yyyy-MM-dd字符串，则归为特定日期排期组
                insertIntoGroup(row, index, speciallyGroup)
    return {"normalGroup":normalGroup, "speciallyGroup": speciallyGroup}

#将数据加入到指定分组
def insertIntoGroup(data, index, groupMap):
    group=groupMap.get(index,[])
    group.append(data)
    #根据index，更新指定元素，相当于saveOrUpdate
    groupMap.update({index:group})


'''
根据当前日期重排排期顺序
返回bean格式为
[
    {
        "dutyDay":${yyyy-MM-dd},
        "dutyClassmate":[
                {
                    "group":"",
                    "name":"",
                    "mobile":""
                }
                ....
            ] 
    }
    ...
]
'''
def genDutyClassmateGroup():
    dutyGroup = loadCalendarFromCsv()
    # 日常排班组
    normalGroup = dutyGroup.get("normalGroup",{});
    # 特定日期排班组
    speciallyGroup = dutyGroup.get("speciallyGroup",{});
    #获取今天日期
    today=datetime.date.today()
    #设置计算排期开始时间
    beginDate=datetime.date(2020,6,7)

    #获取排期组len,取普通组和特定组最长那个
    dutyGroupSize = len(normalGroup);
    '''
       today.isoformat()：格式化获取今天日期，YYYY-MM-DD
       today.strftime('%w')：获取今天星期几的下标
       weekDict[today.strftime('%w')]：通过枚举获取今天星期几名称
    '''
    contentArr=[]
    dutyClassmateGroup=[]
    #从今天开始轮训获取每天值班小组
    for i in range(0,int(dutyGroupSize)):
        # today + i 天
        nextDay=today.__add__(datetime.timedelta(days=i))
        # 获取从指定开始时间到nextDay的天数
        nextDateBetweenDays = nextDay.__sub__(beginDate).days
        '''
            先从特定组获取值班小组
            nextDay.isoformat()：获取格式化日期 yyyy-MM-dd
        '''
        nextDutyClassmateGroup = speciallyGroup.get(nextDay.isoformat(), [])
        if len(nextDutyClassmateGroup) == 0:
            #如果没有指定值班小组，则从日常排气小组获取，下标为 nextDateBetweenDays % dutyGroupSize
            nextDutyClassmateGroup = normalGroup.get(nextDateBetweenDays % dutyGroupSize,[])
        '''
        封装值班组信息
        dutyClassmate：小组同学们
        dutyDay：排期日期
        '''
        group = {"dutyClassmate":nextDutyClassmateGroup, "dutyDay":nextDay}
        #追加到结果集中
        dutyClassmateGroup.append(group)
    print(dutyClassmateGroup)
    return dutyClassmateGroup

#组织值班同学姓名
def getGroupClassmateName(group):
    names = ''
    for classmate in group:
        names += ','+classmate["name"]
    return names.replace(',','',1)

#组装值班同学手机
def getGroupClassmatePhone(group):
    phone = []
    for classmate in group:
        phone.append(classmate['mobile'])
    return phone

#发送今天值班同学信息
def sendTodayDutyMessage(dutyMen):
    headers={"Content-Type":"application/json"}
    payload={
    "msgtype": "text",
    "text": {
        "content": "今日值班同学",
        "mentioned_mobile_list": getGroupClassmatePhone(dutyMen),
        }
    }
    #resp=requests.post(noticeUrl,headers=headers,data=json.dumps(payload))
    print(payload)

#发送值班排期信息
def sendDutyGroupMessage(dutyGroup):
    contentArr = []
    #遍历排期小组
    for duty in dutyGroup :
        #获取排期日期
        dutyDay = duty["dutyDay"]
        contentArr.append('\n> %s %s，%s' % (dutyDay.isoformat(), weekDict[dutyDay.strftime('%w')], getGroupClassmateName(duty["dutyClassmate"])))
    content=''.join(contentArr);
    headers={"Content-Type":"application/json"}
    payload={
    "msgtype": "markdown",
    "markdown": {
        "content": "**<font color=\"warning\">排班安排</font>**%s"%content
        }
    }
     #resp=requests.post(noticeUrl,headers=headers,data=json.dumps(payload))
    print(content)

#发送值班信息到企业微信
def sendToWorkWX(dutyClassmateGroup):
    sendTodayDutyMessage(dutyClassmateGroup[0]["dutyClassmate"])
    sendDutyGroupMessage(dutyClassmateGroup)

'''
main方法
'''
if __name__ == '__main__':
    #读取日程
    dutyClassmateGroup=genDutyClassmateGroup()
    #发送值班安排到企业微信
    sendToWorkWX(dutyClassmateGroup)
    #发送到Email，TODO 未完成