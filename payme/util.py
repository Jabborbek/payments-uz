from datetime import datetime


def time_to_payme(datatime) -> int:
    if not datatime:
        return 0
    return int(datatime.timestamp() * 1000)


def time_to_service(milliseconds: int) -> datetime:
    return datetime.fromtimestamp(milliseconds / 1000)
