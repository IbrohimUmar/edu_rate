import datetime
from django.utils.timezone import make_aware, get_current_timezone


def timestamp_to_date(timestamp):
    try:
        datetime_obj_with_tz = make_aware(datetime.datetime.fromtimestamp(timestamp))
        return datetime_obj_with_tz.date()
    except (OSError, OverflowError, ValueError) as e:
        print(timestamp)
        print(f"Error converting timestamp to date: {e}")
        dt_object = datetime.datetime.fromtimestamp(1666069616)
        date_object = dt_object.date()
        return date_object


# example
# timestamp = 1666069616
# created_date = timestamp_to_date(timestamp)
# print(created_date)  # result: 2022-10-18