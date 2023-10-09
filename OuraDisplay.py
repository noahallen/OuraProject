import clean as cl
import image
import os
import time
import generateGraph as gg
import datetime as DT
from datetime import datetime, timedelta


cl.clean(3)
try:
    today = datetime.now()
    gg.storeToNAS("daily_sleep")
    gg.storeToNAS("daily_activity")
    gg.storeToNAS("daily_readiness")
    gg.storeToNAS("heartrate")
    gg.storeToNAS("sleep")
    gg.storeToNAS("workout")
    gg.storeToNAS("tag")
    gg.storeToNAS("session")
    end_date = today.date() - DT.timedelta(0) + DT.timedelta(1)
    start_date = today.date() - DT.timedelta(31)
    image.showImage(gg.generateLineGraph("Past Month's Sleep", "Hours", start_date, end_date,"sleep","long_sleep"))
except Exception as e: 
        image.showText(e)


# def update(today):
#     cl.clean(3)
#     try:
#         gg.storeToNAS("daily_sleep")
#         gg.storeToNAS("daily_activity")
#         gg.storeToNAS("daily_readiness")
#         gg.storeToNAS("heartrate")
#         gg.storeToNAS("sleep")
#         gg.storeToNAS("workout")
#         gg.storeToNAS("tag")
#         gg.storeToNAS("session")
#         end_date = today.date() - DT.timedelta(0) + DT.timedelta(1)
#         start_date = today.date() - DT.timedelta(31)
#         image.showImage(gg.generateLineGraph("Past Month's Sleep", "Hours", start_date, end_date,"sleep","long_sleep"))
#     except Exception as e: 
#         image.showText(e)

# while 1:
#     try:
#         time.sleep(60)
#         update(datetime.now())
#         dt = datetime.now() + timedelta(hours=5)
#         while datetime.now() < dt:
#             time.sleep(60)
#     except:
#         pass