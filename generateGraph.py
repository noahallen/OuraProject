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
import glob

load_dotenv()
token = os.getenv('TOKEN')
naspath = os.getenv('NASPATH')

def readFile(fileName):
    try:
        with open(fileName, "r") as file:
            data = json.load(file)
            return data
    except:
        f = open(fileName, "w+")
        f.write('[[]]')
        f.close()
        return [[]]

def storeToNAS(data_type):
    if(data_type=="heartrate"):
        dataPulled = json.loads(makeRequest(0, 20, data_type, token))["data"]
    else:
        dataPulled = json.loads(makeRequest(0, 20, data_type, token))["data"]

    data_dir = os.path.join(naspath, data_type)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    months_data = {}

    for item in dataPulled:
        if data_type == "heartrate":
            day = item["timestamp"][:10]
        else:
            day = item["day"]

        month = day[5:7]
        year = day[0:4]
        fileName = f"{year} {month}.json"
        filePath = os.path.join(data_dir, fileName)

        if filePath not in months_data:
            if os.path.exists(filePath):
                months_data[filePath] = readFile(filePath)
                months_data[filePath][0] = set(months_data[filePath][0])
            else:
                months_data[filePath] = [set(),]

        if data_type == "heartrate":
            if item["timestamp"] not in months_data[filePath][0]:
                months_data[filePath].append(item)
                months_data[filePath][0].add(item["timestamp"])
        else:
            if item["id"] not in months_data[filePath][0]:
                months_data[filePath].append(item)
                months_data[filePath][0].add(item["id"])

    for filePath, currData in months_data.items():
        with open(filePath, "w") as file_object:
            if os.path.exists(filePath):
                existing_data = readFile(filePath)
                existing_data[0] = set(existing_data[0])
                for item in currData[1:]:
                    if data_type == "heartrate":
                        if item["timestamp"] not in existing_data[0]:
                            existing_data.append(item)
                            existing_data[0].add(item["timestamp"])
                    else:
                        if item["id"] not in existing_data[0]:
                            existing_data.append(item)
                            existing_data[0].add(item["id"])
                json.dump([list(existing_data[0])] + existing_data[1:], file_object, indent="   ")
            else:
                json.dump(currData, file_object, indent="   ")

def makeRequest(daysFromNow1, daysFromNow2, urlPiece, token):
    # Dates format: YYYY-MM-DD
    today = date.today()
    timeAgo = today - DT.timedelta(daysFromNow1) + DT.timedelta(1)
    timeAgo2 = today - DT.timedelta(daysFromNow2)

    url = 'https://api.ouraring.com/v2/usercollection/' + urlPiece
    if urlPiece == 'heartrate':
        params = {
            'start_datetime': datetime.combine(timeAgo2, datetime.min.time()),
            'end_datetime': datetime.combine(timeAgo, datetime.min.time())
        }
    else:
        params = {
            'start_date': timeAgo2,
            'end_date': timeAgo
        }
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.request('GET', url, headers=headers, params=params)
    return response.text

def extractSleepDataFromNAS(start_date, end_date):
    sleep_data = []

    # Generate a list of file names that potentially have data in the time span
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    file_names = ['Sleep {} {:02d}.json'.format(d.year, d.month) for d in date_range]
    file_names = set(file_names)  # Remove duplicates

    # Loop through each relevant file in the specified directory
    for file in glob.glob(os.path.join(naspath, 'Sleep * *.json')):
        if os.path.basename(file) in file_names:
            try:
                with open(file, 'r') as f:
                    # Load the file as JSON
                    sleep_json = json.load(f)

                    # Loop through each sleep object in the file
                    for sleep in sleep_json[1:]:
                        # Get the date of the sleep object
                        sleep_date = datetime.strptime(sleep['day'], '%Y-%m-%d').date()

                        # Check if the date is within the inputted range
                        if start_date <= sleep_date <= end_date:
                            # Add the sleep object to the sleep data list
                            sleep_data.append(sleep)
            except:
                continue

    return sleep_data

def generateLineGraph():
    try:
        end_date = date.today()+DT.timedelta(1)
        start_date = end_date - DT.timedelta(30)
        data = extractSleepDataFromNAS(start_date, end_date)
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(0, 30,"sleep",token))['data']

    label=[]
    totalSleep=[]

    for item in data:
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
    try:
        end_date = date.today()+ DT.timedelta(1)
        start_date = end_date - DT.timedelta(7)
        data = extractSleepDataFromNAS(start_date, end_date)
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(0,7,"sleep",token))['data']

    label=[]
    deepSleep=[]
    remSleep=[]
    awakeTime=[]
    lightSleep=[]
    for item in data:
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
