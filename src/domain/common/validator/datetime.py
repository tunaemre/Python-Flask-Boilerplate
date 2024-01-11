from datetime import datetime


def check_valid_until(v: datetime) -> datetime:
    if v < datetime.utcnow():
        raise ValueError('valid_until time must be later than now!')

    return v
