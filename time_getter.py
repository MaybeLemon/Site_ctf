import datetime

def timegetter():
    now = datetime.datetime.now()
    formatted_time = now.strftime("%d.%m.%Y %H:%M:%S")
    return formatted_time
