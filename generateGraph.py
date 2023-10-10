from dotenv import load_dotenv
import os
import json
import requests 
import datetime as DT
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
from matplotlib.dates import AutoDateLocator, DateFormatter

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

def getValByIndex(json_data, index_str):
    # Split the index string into a list of keys
    keys = index_str.split('/')
    # Loop through the keys to access the nested dictionaries
    for key in keys:
        json_data = json_data.get(key)
        if json_data is None:
            return None
    # Return the final value
    return json_data

def storeToNAS(data_type, days_back, date_width):

    #For some reason this API call only allows around a max of 15 days so ideally store in small increments then use NAS data
    if(data_type=="heartrate"):
        end_date = date.today() - timedelta(days=days_back) + DT.timedelta(1)
        start_date = end_date - DT.timedelta(date_width)
        
        
    else:
        end_date = date.today() - timedelta(days=days_back) + DT.timedelta(1)
        start_date = end_date - DT.timedelta(date_width)

    dataPulled = json.loads(makeRequest(start_date, end_date, data_type, token))["data"]

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

def makeRequest(dateStart, dateEnd, urlPiece, token):

    # Construct the API endpoint URL
    url = 'https://api.ouraring.com/v2/usercollection/' + urlPiece
    
    # Depending on the endpoint we're querying, construct the request parameters
    if urlPiece == 'heartrate':
        params = {
            'start_datetime': datetime.combine(dateStart, datetime.min.time()),
            'end_datetime': datetime.combine(dateEnd, datetime.min.time())
        }
    else:
        params = {
            'start_date': dateStart,
            'end_date': dateEnd
        }
    
    # Construct the headers for the API request
    headers = {
        'Authorization': 'Bearer ' + token
    }
    
    # Make the API request and return the response text
    response = requests.request('GET', url, headers=headers, params=params)
    return response.text

def get_files(data_type):
    data_path = os.path.join(naspath, data_type.lower())
    file_names = os.listdir(data_path)
    files = [os.path.join(data_path, f) for f in file_names]

    # Sort the file names based on their year and month information
    sorted_files = sorted(files, key=lambda f: tuple(map(int, os.path.splitext(os.path.basename(f))[0].split()[::-1]))[::-1])

    return sorted_files

def extractDataFromNAS(start_date, end_date, data_type):
    files = get_files(data_type)
    data = []
    for file in files:
        with open(file) as f:
            file_data = json.load(f)

            for record in file_data[1:]:
                if data_type == "heartrate":
                    date = datetime.fromisoformat(record["timestamp"]).date()
                    if start_date <= date <= end_date:
                        data.append(record)
                else:
                    day = datetime.strptime(record["day"], '%Y-%m-%d').date()
                    if start_date <= day <= end_date:
                        data.append(record)
    return data

def generateBarGraph(title, ylabel, start_date, end_date, graph_type, item_type):
    # Attempt to extract data for the given time period and graph type,
    # or load from API if there is an error
    try:
        data = extractDataFromNAS(start_date, end_date, graph_type)
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(start_date, end_date, graph_type, token))['data']

    # Initialize label and value lists
    label=[]
    values=[]

    # Loop through the data and extract relevant information
    if graph_type == "heartrate":
        heartrate_data = {}
        for item in data:
            day = datetime.fromisoformat(item["timestamp"]).date()
            if day not in heartrate_data:
                heartrate_data[day] = [getValByIndex(item, item_type)]
            else:
                heartrate_data[day].append(getValByIndex(item, item_type))
        for day, heartrate_values in heartrate_data.items():
            label.append(day.strftime("%m/%d"))
            values.append(round(sum(heartrate_values)/len(heartrate_values), 2))
    elif graph_type == "sleep":
        for item in data:
            if item["type"] == item_type:
                day = datetime.strptime(item['day'], '%Y-%m-%d').date()
                label.append(day.strftime("%m/%d"))
                values.append(round(item["deep_sleep_duration"]/3600,2) + round((item["rem_sleep_duration"])/3600,2) + round((item["light_sleep_duration"])/3600,2))
    else:
        for item in data:
            day = datetime.strptime(item['day'], '%Y-%m-%d').date()
            label.append(day.strftime("%m/%d"))
            tmp = getValByIndex(item, item_type)
            values.append(tmp)

    # Convert lists to numpy arrays
    values = np.array(values)
    label = np.array(label)

    # Create figure and axis objects
    fig, ax = plt.subplots(edgecolor="black",linewidth=10)

    # Add grid to y-axis and set title, ylabel, and ylim
    ax.grid(axis='y')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_ylim(np.mean(values) - 4*np.std(values), np.mean(values) + 5*np.std(values))

    # Set x-axis tick spacing and plot the line graph
    locator = AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    plt.bar(label, values, color="orange")

    # Set the background color and save the graph to a file
    ax.set_facecolor("White")
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/"+title+" bar graph.jpg")

    # Return the filepath to the saved graph
    return ("/home/ourapi/Desktop/OuraStuff/images/"+title+" bar graph.jpg")

def generateLineGraph(title, ylabel, start_date, end_date, graph_type, item_type):
    # Attempt to extract data for the given time period and graph type,
    # or load from API if there is an error
    try:
        data = extractDataFromNAS(start_date, end_date, graph_type)
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(start_date, end_date, graph_type, token))['data']

    # Initialize label and value lists
    label=[]
    values=[]

    # Loop through the data and extract relevant information
    if graph_type == "heartrate":
        heartrate_data = {}
        for item in data:
            day = datetime.fromisoformat(item["timestamp"]).date()
            if day not in heartrate_data:
                heartrate_data[day] = [getValByIndex(item, item_type)]
            else:
                heartrate_data[day].append(getValByIndex(item, item_type))
        for day, heartrate_values in heartrate_data.items():
            label.append(day.strftime("%m/%d"))
            values.append(round(sum(heartrate_values)/len(heartrate_values), 2))
    elif graph_type == "sleep":
        for item in data:
            if item["type"] == item_type:
                day = datetime.strptime(item['day'], '%Y-%m-%d').date()
                label.append(day.strftime("%m/%d"))
                values.append(round(item["deep_sleep_duration"]/3600,2) + round((item["rem_sleep_duration"])/3600,2) + round((item["light_sleep_duration"])/3600,2))
    else:
        for item in data:
            day = datetime.strptime(item['day'], '%Y-%m-%d').date()
            label.append(day.strftime("%m/%d"))
            tmp = getValByIndex(item, item_type)
            values.append(tmp)
            
    # Convert lists to numpy arrays
    values = np.array(values)
    label = np.array(label)


    # Create figure and axis objects
    fig, ax = plt.subplots(edgecolor="black",linewidth=10)

    # Add grid to y-axis and set title, ylabel, and ylim
    ax.grid(axis='y')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_ylim(np.mean(values) - 4*np.std(values), np.mean(values) + 5*np.std(values))

    # Set x-axis tick spacing and plot the line graph
    locator = AutoDateLocator()
    ax.xaxis.set_major_locator(locator)

    plt.plot(label, values, color="blue")

    # Set the background color and save the graph to a file
    ax.set_facecolor("White")
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/"+title+" line graph.jpg")

    # Return the filepath to the saved graph
    return ("/home/ourapi/Desktop/OuraStuff/images/"+title+" line graph.jpg")

def generateSleepLineGraph():
    # Attempt to extract sleep data from the past 30 days, or load from API if there is an error
    end_date = date.today() - timedelta(days=0) + DT.timedelta(1)
    start_date = end_date - DT.timedelta(30)
    try:
        data = extractDataFromNAS(start_date, end_date, "sleep")
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(start_date, end_date,"sleep",token))['data']

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
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/Sleep Line Graph Hardcode.jpg")

    # Return the filepath to the saved graph
    return ("/home/ourapi/Desktop/OuraStuff/images/Sleep Line Graph Hardcode.jpg")

def generateSleepBarGraph():
    # Try to extract sleep data from NAS drive, if there is an error use data from API instead
    end_date = date.today() - timedelta(days=0) + DT.timedelta(1)
    start_date = end_date - DT.timedelta(7)
    try:
        data = extractDataFromNAS(start_date, end_date, "sleep")
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(start_date, end_date,"sleep",token))['data']

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
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/Sleep Bar Graph Hardcode.jpg")

    # Return filepath to saved image file
    return ("/home/ourapi/Desktop/OuraStuff/images/Sleep Bar Graph Hardcode.jpg")

def generateActivityBarGraph():
    # Attempt to extract activity data from the past 30 days, or load from API if there is an error
    end_date = date.today() - timedelta(days=0) + DT.timedelta(1)
    start_date = end_date - DT.timedelta(10)
    try:
        data = extractDataFromNAS(start_date, end_date, "daily_activity")
    except Exception as e:
        print(f"Error: {e}")
        data = json.loads(makeRequest(start_date, end_date,"daily_activity",token))['data']

    # Initialize label and stepCount lists
    label=[]
    activityCount=[]

    # Loop through the activity data and extract relevant information
    for item in data:
        day = datetime.strptime(item['day'], '%Y-%m-%d').date()
        label.append(day.strftime("%m/%d"))
        activityCount.append(item['total_calories'])

    # Convert lists to numpy arrays
    activityCount=np.array(activityCount)
    label=np.array(label)

    # Create figure and axis objects
    fig, ax = plt.subplots(edgecolor="black",linewidth=10)

    # Add grid to y-axis and set title, ylabel, and ylim
    ax.grid(axis='y')
    ax.set_title('Daily Activity')
    ax.set_ylabel('Calories')
    ax.set_ylim([0, 5000])

    # Set x-axis tick spacing and plot the bar graph
    myLocator = mticker.MultipleLocator(1)
    ax.xaxis.set_major_locator(myLocator)
    ax.bar(label, activityCount, color="orange")

    # Set the background color and save the graph to a file
    ax.set_facecolor("White")
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/outputActivityBar.jpg")

    # Return the filepath to the saved graph
    return ("/home/ourapi/Desktop/OuraStuff/images/outputActivityBar.jpg")

def generateScatterPlot(title, xlabel, ylabel, start_date, end_date, graph_type1, graph_type2, item_type1,item_type2):
# Attempt to extract data for the given time period and graph type,
    # or load from API if there is an error
    try:
        data1 = extractDataFromNAS(start_date, end_date, graph_type1)
    except Exception as e:
        print(f"Error: {e}")
        data1 = json.loads(makeRequest(start_date, end_date, graph_type1, token))['data']

    try:
        data2 = extractDataFromNAS(start_date, end_date, graph_type2)
    except Exception as e:
        print(f"Error: {e}")
        data2 = json.loads(makeRequest(start_date, end_date, graph_type2, token))['data']

    # Initialize label and value lists
    values1=[]
    values2=[]

    # Loop through the data and extract relevant information
    if graph_type1 == "heartrate":
        heartrate_data = {}
        for item in data1:
            day = datetime.fromisoformat(item["timestamp"]).date()
            if day not in heartrate_data:
                heartrate_data[day] = [getValByIndex(item, item_type1)]
            else:
                heartrate_data[day].append(getValByIndex(item, item_type1))
        for day, heartrate_values in heartrate_data.items():
            values1.append(round(sum(heartrate_values)/len(heartrate_values), 2))

    elif graph_type1 == "sleep":
        for item in data1:
            if item["type"] == item_type1:
                day = datetime.strptime(item['day'], '%Y-%m-%d').date()
                values1.append(round(item["deep_sleep_duration"]/3600,2) + round((item["rem_sleep_duration"])/3600,2) + round((item["light_sleep_duration"])/3600,2))
    else:
        for item in data1:
            day = datetime.strptime(item['day'], '%Y-%m-%d').date()
            tmp = getValByIndex(item, item_type1)
            values1.append(tmp)


    # Loop through the data and extract relevant information
    if graph_type2 == "heartrate":
        heartrate_data = {}
        for item in data2:
            day = datetime.fromisoformat(item["timestamp"]).date()
            if day not in heartrate_data:
                heartrate_data[day] = [getValByIndex(item, item_type2)]
            else:
                heartrate_data[day].append(getValByIndex(item, item_type2))
        for day, heartrate_values in heartrate_data.items():
            values2.append(round(sum(heartrate_values)/len(heartrate_values), 2))

    elif graph_type2 == "sleep":
        for item in data2:
            if item["type"] == item_type2:
                day = datetime.strptime(item['day'], '%Y-%m-%d').date()
                values2.append(round(item["deep_sleep_duration"]/3600,2) + round((item["rem_sleep_duration"])/3600,2) + round((item["light_sleep_duration"])/3600,2))
    else:
        for item in data2:
            day = datetime.strptime(item['day'], '%Y-%m-%d').date()
            tmp = getValByIndex(item, item_type2)
            values2.append(tmp)
            
    # Convert lists to numpy arrays
    values1 = np.array(values1)
    values2 = np.array(values2)

    # Create figure and axis objects
    fig, ax = plt.subplots(edgecolor="black",linewidth=10)

    # Add grid to y-axis and set title, ylabel, and ylim
    ax.grid(axis='y')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    # ax.set_ylim(np.mean(values1) - 4*np.std(values1), np.mean(values1) + 5*np.std(values1))

    # Set x-axis tick spacing and plot the scatter plot
    locator = AutoDateLocator()
    ax.xaxis.set_major_locator(locator)

    plt.scatter(values1, values2, color="orange")

    # Set the background color and save the graph to a file
    ax.set_facecolor("White")
    plt.savefig("/home/ourapi/Desktop/OuraStuff/images/"+title+" scatter plot.jpg")

    # Return the filepath to the saved graph
    return ("/home/ourapi/Desktop/OuraStuff/images/"+title+" scatter plot.jpg")
    
'''

---------------------------------------------------
Some example functions I can call are here:
---------------------------------------------------

# end_date = date.today() - DT.timedelta(1) + DT.timedelta(0)
# start_date = date.today() - DT.timedelta(40)+ DT.timedelta(0)

generateSleepLineGraph()
generateSleepBarGraph()

# generateBarGraph("Daily Sleep Total", "Hours", start_date, end_date,"sleep","long_sleep")
# generateBarGraph("Calories Burned in a Day", "Calories", start_date, end_date,"daily_activity","total_calories")
# generateLineGraph("Past Month's Sleep", "Hours", start_date, end_date,"sleep","long_sleep")
# generateLineGraph("Past Month's Calories Burned", "Calories", start_date, end_date,"daily_activity","total_calories")
# generateLineGraph("Past Month's Body Temperature", "Temperature", start_date, end_date,"daily_readiness","contributors/body_temperature")
# generateBarGraph("Past Month's Average Heartrate", "BPM", start_date, end_date,"heartrate","bpm")
# generateLineGraph("Past Month's Average Heartrate", "BPM", start_date, end_date,"heartrate","bpm")
# generateLineGraph("Past Month's Sedentary Time", "Seconds", start_date, end_date,"daily_activity","sedentary_time")
# generateLineGraph("Past Year's Calories Burned", "Calories", start_date, end_date,"daily_activity","total_calories")
# generateLineGraph("Past Year's Calories Burned", "Calories", start_date, end_date,"daily_activity","total_calories")
# generateBarGraph("Past Month's Sleep", "Hours", start_date, end_date,"sleep","long_sleep")

# generateScatterPlot("Calories Burned vs Average Heartrate", "Average Heartrate (BPM)","Calories Burned", start_date, end_date,"heartrate","daily_activity","bpm","total_calories")
'''



