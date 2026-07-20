from datetime import datetime


def time_to_uzum(dt) -> int:
    if not dt:
        return 0
    return int(dt.timestamp() * 1000)


def time_to_service(milliseconds: int) -> datetime:
    return datetime.fromtimestamp(milliseconds / 1000)
