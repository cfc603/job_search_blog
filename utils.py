from datetime import datetime


def get_datetime_obj(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')


def get_now_str():
    return str(datetime.now())
