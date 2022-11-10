import dotenv
from dotenv import load_dotenv

load_dotenv()
import os
token = os.getenv('TOKEN')
import json
import requests 

import datetime as DT
from datetime import date
import matplotlib.pyplot as plt
import numpy as np



def makeRequest(lookbackDays,urlPiece,token):
    #Dates format: YYYY-MM-DD
    today = date.today()+DT.timedelta(1)
    weekAgo = today - DT.timedelta(lookbackDays)

    url = 'https://api.ouraring.com/v2/usercollection/'+urlPiece 
    params={ 
        'start_date': today - DT.timedelta(lookbackDays), 
        'end_date': today 
    }
    headers = { 
    'Authorization': 'Bearer '+token 
    }
    response = requests.request('GET', url, headers=headers, params=params) 
    return response.text


def generate():
    data = json.loads(makeRequest(7,"sleep",token))

    label=[]
    deepSleep=[]
    remSleep=[]
    awakeTime=[]
    lightSleep=[]
    for item in data['data']:
        if(item["type"] == "long_sleep" or item["type"] == "sleep"):
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
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/output.jpg")

    print("Graph Generated!")
    return ("/home/ourapi/Desktop/OuraStuff/images/output.jpg")

