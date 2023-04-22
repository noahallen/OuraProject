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
        # Try to open the file for reading
        with open(fileName, "r") as file:
            # Load the contents of the file as JSON data
            data = json.load(file)
            # Return the data
            return data
    except:
        # If the file cannot be opened for reading, create a new file and write an empty 2D list as JSON data
        f = open(fileName, "w+")
        f.write('[[]]')
        f.close()
        # Return the empty 2D list
        return [[]]

def storeToNAS(data_type):
    # Pull data from API using makeRequest function
    if(data_type=="heartrate"):
        # If data_type is heartrate, extract "data" field from JSON response
        dataPulled = json.loads(makeRequest(0, 20, data_type, token))["data"]
    else:
        # Otherwise, extract "data" field from JSON response
        dataPulled = json.loads(makeRequest(0, 20, data_type, token))["data"]

    # Create directory path to store data for this data_type on NAS
    data_dir = os.path.join(naspath, data_type)
    if not os.path.exists(data_dir):
        # If directory doesn't already exist, create it
        os.makedirs(data_dir)

    # Create dictionary to hold data for each month
    months_data = {}

    # Loop through each item in the data pulled from the API
    for item in dataPulled:
        # Extract the day of the item based on the data_type
        if data_type == "heartrate":
            day = item["timestamp"][:10]
        else:
            day = item["day"]

        # Extract the month and year from the day
        month = day[5:7]
        year = day[0:4]

        # Create a filename for the data file for this month and year
        fileName = f"{year} {month}.json"

        # Create a full file path to the data file for this month and year
        filePath = os.path.join(data_dir, fileName)

        # If this month's data hasn't already been processed, create a new list for it
        if filePath not in months_data:
            if os.path.exists(filePath):
                # If the data file already exists, read in the existing data and convert the set to a list
                months_data[filePath] = readFile(filePath)
                months_data[filePath][0] = set(months_data[filePath][0])
            else:
                # Otherwise, create a new list with an empty set
                months_data[filePath] = [set(),]

        # Add the current item to the list for this month's data, checking for duplicates
        if data_type == "heartrate":
            if item["timestamp"] not in months_data[filePath][0]:
                months_data[filePath].append(item)
                months_data[filePath][0].add(item["timestamp"])
        else:
            if item["id"] not in months_data[filePath][0]:
                months_data[filePath].append(item)
                months_data[filePath][0].add(item["id"])

    # Loop through each month's data and write it to a file
    for filePath, currData in months_data.items():
        with open(filePath, "w") as file_object:
            if os.path.exists(filePath):
                # If the data file already exists, read in the existing data and convert the set to a list
                existing_data = readFile(filePath)
                existing_data[0] = set(existing_data[0])
                # Loop through each item in the current month's data and add it to the existing data, checking for duplicates
                for item in currData[1:]:
                    if data_type == "heartrate":
                        if item["timestamp"] not in existing_data[0]:
                            existing_data.append(item)
                            existing_data[0].add(item["timestamp"])
                    else:
                        if item["id"] not in existing_data[0]:
                            existing_data.append(item)
                            existing_data[0].add(item["id"])
                # Write the combined data to the NAS
                json.dump([list(existing_data[0])] + existing_data[1:], file_object, indent="   ")
            else:
                json.dump(currData, file_object, indent="   ")

def makeRequest(daysFromNow1, daysFromNow2, urlPiece, token):
    # Get the current date
    today = date.today()
    # Calculate the dates for the time range we want to query
    timeAgo = today - timedelta(days=daysFromNow1) + timedelta(days=1)
    timeAgo2 = today - timedelta(days=daysFromNow2)

    # Construct the API endpoint URL
    url = 'https://api.ouraring.com/v2/usercollection/' + urlPiece
    
    # Depending on the endpoint we're querying, construct the request parameters
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
    
    # Construct the headers for the API request
    headers = {
        'Authorization': 'Bearer ' + token
    }
    
    # Make the API request and return the response text
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
    # Attempt to extract sleep data from the past 30 days, or load from API if there is an error
    try:
        end_date = date.today() + DT.timedelta(1)
        start_date = end_date - DT.timedelta(30)
        data = extractSleepDataFromNAS(start_date, end_date)
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(0, 30,"sleep",token))['data']

    # Initialize label and totalSleep lists
    label=[]
    totalSleep=[]

    # Loop through the sleep data and extract relevant information
    for item in data:
        if(item["type"] == "long_sleep"):
            tmpList=[]
            tmpList = item['day'].split('-')
            label.append(str(int(tmpList[1]))+"/"+tmpList[2])
            totalSleep.append(round(item["deep_sleep_duration"]/3600,2) + round((item["rem_sleep_duration"])/3600,2) + round((item["light_sleep_duration"])/3600,2))

    # Convert lists to numpy arrays
    totalSleep=np.array(totalSleep)
    label=np.array(label)

    # Create figure and axis objects
    fig, ax = plt.subplots(edgecolor="black",linewidth=10)

    # Add grid to y-axis and set title, ylabel, and ylim
    ax.grid(axis='y')
    ax.set_title('Past Month\'s Sleep')
    ax.set_ylabel('Hours')
    ax.set_ylim([0, 12])

    # Set x-axis tick spacing and plot the line graph
    myLocator = mticker.MultipleLocator(3)
    ax.xaxis.set_major_locator(myLocator)
    plt.plot(label,totalSleep, color="blue")

    # Set the background color and save the graph to a file
    ax.set_facecolor("White")
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/outputLine.jpg")

    # Return the filepath to the saved graph
    return ("/home/ourapi/Desktop/OuraStuff/images/outputLine.jpg")

def generateBarGraph():
    # Try to extract sleep data from NAS drive, if there is an error use data from API instead
    try:
        end_date = date.today()+ DT.timedelta(1)
        start_date = end_date - DT.timedelta(7)
        data = extractSleepDataFromNAS(start_date, end_date)
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(0,7,"sleep",token))['data']

    # Initialize empty lists for each type of sleep data
    label=[]
    deepSleep=[]
    remSleep=[]
    awakeTime=[]
    lightSleep=[]

    # Populate lists with sleep data from extracted data
    for item in data:
        if(item["type"] == "long_sleep"):
            tmpList=[]
            tmpList = item['day'].split('-')
            label.append(str(int(tmpList[1]))+"/"+tmpList[2])
            deepSleep.append(round(item["deep_sleep_duration"]/3600,2))
            remSleep.append(round((item["rem_sleep_duration"])/3600,2))
            lightSleep.append(round((item["light_sleep_duration"])/3600,2))
            awakeTime.append(round((item["awake_time"])/3600,2))

    # Convert lists to numpy arrays
    deepSleep=np.array(deepSleep)
    remSleep=np.array(remSleep)
    lightSleep=np.array(lightSleep)
    awakeTime=np.array(awakeTime)

    # Create a new figure and axes object
    fig, ax = plt.subplots(edgecolor="black",linewidth=10)

    # Plot each bar chart using data from lists and arrays
    ax.bar(label,deepSleep, label="Deep Sleep", color="blue", edgecolor="black")
    ax.bar(label,remSleep, label="REM Sleep", color="yellow", edgecolor="black", bottom=deepSleep )
    ax.bar(label,lightSleep, label="Light Sleep", bottom=remSleep+deepSleep, color="green", edgecolor="black")
    ax.bar(label,awakeTime, label="Time Awake", bottom=lightSleep+remSleep+deepSleep, color="red", edgecolor="black")

    # Set graph title, legend, y-axis label, and y-axis limit
    ax.set_title('Past Week\'s Sleep')
    plt.legend(bbox_to_anchor=(0.80,1.1), loc="upper left",framealpha=1,edgecolor="black")
    ax.set_ylabel('Hours')
    ax.set_ylim([0, 11])

    # Save graph image as JPEG file
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/outputBar.jpg")

    # Return filepath to saved image file
    return ("/home/ourapi/Desktop/OuraStuff/images/outputBar.jpg")
