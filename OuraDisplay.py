import clean as cl
import image
import os
import time
import generateGraph as gg
from datetime import datetime, timedelta

# Define a function to update data every minute and show the line graph of the data
def update():
    # Clean data from the last 3 days
    cl.clean(3)
    
    try:
        # Store daily sleep, activity, readiness, heart rate, sleep, workout, tag, and session data to a NAS
        gg.storeToNAS("daily_sleep")
        gg.storeToNAS("daily_activity")
        gg.storeToNAS("daily_readiness")
        gg.storeToNAS("heartrate")
        gg.storeToNAS("sleep")
        gg.storeToNAS("workout")
        gg.storeToNAS("tag")
        gg.storeToNAS("session")
        
        # Show a line graph of the stored data
        image.showImage(gg.generateLineGraph())
    except:
        # If an error occurs, do nothing
        pass

# Run the update function every minute
while 1:
    try:
        # Wait for 60 seconds
        time.sleep(60)
        
        # Call the update function to update data and show the line graph
        update()
        
        # Wait for an additional 5 hours before running the update function again
        dt = datetime.now() + timedelta(hours=5)
        while datetime.now() < dt:
            time.sleep(60)
    except:
        # If an error occurs, do nothing
        pass

