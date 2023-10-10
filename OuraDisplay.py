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
    gg.storeToNAS("daily_sleep", 0, 15)
    gg.storeToNAS("daily_activity", 0, 15)
    gg.storeToNAS("daily_readiness", 0, 15)
    gg.storeToNAS("heartrate", 0, 15)
    gg.storeToNAS("sleep", 0, 15)
    gg.storeToNAS("workout", 0, 15)
    gg.storeToNAS("tag", 0, 15)
    gg.storeToNAS("session", 0, 15)
    end_date = today.date() - DT.timedelta(0) + DT.timedelta(1)
    start_date = today.date() - DT.timedelta(31)
    image.showImage(gg.generateLineGraph("Past Month's Sleep", "Hours", start_date, end_date,"sleep","long_sleep"))
except Exception as e: 
        image.showText(e)
