import dotenv
from dotenv import load_dotenv
import os
import json
import requests 
import datetime as DT
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker

load_dotenv()
token = os.getenv('TOKEN')
naspath = os.getenv('NASPATH')


def readFile(fileName):
    try:
        with open(naspath + fileName + ".json", "r") as file:
            data = json.load(file)
            return data
    except:
        f = open(naspath + fileName + ".json", "w+")
        f.write('[[]]')
        f.close()
        return [[]]



def storeToNAS():
    month1 = ""
    month2 = ""
    flag = True

    dataPulled = json.loads(makeRequest(25,"sleep",token))['data']
    for item in dataPulled:
        if(flag):
            month1 = item["day"][5:7]
            year1 = item["day"][0:4]
            flag=False
        else:
            if(item["day"][5:6] != month1):
                month2 = item["day"][5:7]
                year2 = item["day"][0:4]
    
    if(month1 != ""):
        fileName1 = str(year1) + " " + str(month1)
        currData1 = readFile(fileName1)

        for item in dataPulled:
            if(item["id"] not in currData1[0] and item["day"][5:7] == month1):
                currData1.append(item)
                currData1[0].append(item["id"])
        
        with open(naspath + fileName1 + ".json", "w") as file_object:
            json.dump(currData1, file_object, indent = "   ")

    if(month2 != ""):
        fileName2 = str(year2) + " " + str(month2)
        currData2 = readFile(fileName2)

        for item in dataPulled:
            if(item["id"] not in currData2[0] and item["day"][5:7] == month2):
                currData2.append(item)
                currData2[0].append(item["id"])
        
        with open(naspath + fileName2 + ".json", "w") as file_object:
            json.dump(currData2, file_object, indent = "   ")


def makeRequest(lookbackDays,urlPiece,token):
    #Dates format: YYYY-MM-DD
    today = date.today()+DT.timedelta(1)
    timeAgo = today - DT.timedelta(lookbackDays)

    url = 'https://api.ouraring.com/v2/usercollection/'+urlPiece 
    params={ 
        'start_date': timeAgo, 
        'end_date': today 
    }
    headers = { 
    'Authorization': 'Bearer ' + token 
    }
    response = requests.request('GET', url, headers=headers, params=params) 
    return response.text

def generateLineGraph():
    data = json.loads(makeRequest(30,"sleep",token))

    label=[]
    totalSleep=[]

    for item in data['data']:
        if(item["type"] == "long_sleep"):
            tmpList=[]
            tmpList = item['day'].split('-')
            label.append(str(int(tmpList[1]))+"/"+tmpList[2])
            totalSleep.append(round(item["deep_sleep_duration"]/3600,2) + round((item["rem_sleep_duration"])/3600,2) + round((item["light_sleep_duration"])/3600,2))


    totalSleep=np.array(totalSleep)
    label=np.array(label)

    fig, ax = plt.subplots(edgecolor="black",linewidth=10)
    ax.grid(axis='y')
    ax.set_title('Past Month\'s Sleep')
    ax.set_ylabel('Hours')
    myLocator = mticker.MultipleLocator(3)
    ax.xaxis.set_major_locator(myLocator)
    ax.set_ylim([0, 12])
    plt.plot(label,totalSleep, color="blue")
    ax.set_facecolor("White")
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/outputLine.jpg")

    # print("Graph Generated!")
    return ("/home/ourapi/Desktop/OuraStuff/images/outputLine.jpg")

def generateBarGraph():
    data = json.loads(makeRequest(7,"sleep",token))

    label=[]
    deepSleep=[]
    remSleep=[]
    awakeTime=[]
    lightSleep=[]
    for item in data['data']:
        if(item["type"] == "long_sleep"):
            tmpList=[]
            tmpList = item['day'].split('-')
            label.append(str(int(tmpList[1]))+"/"+tmpList[2])
            deepSleep.append(round(item["deep_sleep_duration"]/3600,2))
            remSleep.append(round((item["rem_sleep_duration"])/3600,2))
            lightSleep.append(round((item["light_sleep_duration"])/3600,2))
            awakeTime.append(round((item["awake_time"])/3600,2))


    deepSleep=np.array(deepSleep)
    remSleep=np.array(remSleep)
    lightSleep=np.array(lightSleep)
    awakeTime=np.array(awakeTime)

    fig, ax = plt.subplots(edgecolor="black",linewidth=10)
    ax.bar(label,deepSleep, label="Deep Sleep", color="blue", edgecolor="black")
    ax.bar(label,remSleep, label="REM Sleep", color="yellow", edgecolor="black", bottom=deepSleep )
    ax.bar(label,lightSleep, label="Light Sleep", bottom=remSleep+deepSleep, color="green", edgecolor="black")
    ax.bar(label,awakeTime, label="Time Awake", bottom=lightSleep+remSleep+deepSleep, color="red", edgecolor="black")
    ax.set_title('Past Week\'s Sleep')
    plt.legend(bbox_to_anchor=(0.80,1.1), loc="upper left",framealpha=1,edgecolor="black")
    ax.set_ylabel('Hours')
    ax.set_ylim([0, 11])
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/outputBar.jpg")

    # print("Graph Generated!")
    return ("/home/ourapi/Desktop/OuraStuff/images/outputBar.jpg")


