import datetime
from django.utils.timezone import make_aware, get_current_timezone

from services.handle_exception import handle_exception


def timestamp_to_datetime(timestamp):
    try:
        datetime_obj_with_tz = make_aware(datetime.datetime.fromtimestamp(timestamp))
        return datetime_obj_with_tz

    except (OSError, OverflowError, ValueError) as e:
        handle_exception(e)
        dt_object = datetime.datetime.fromtimestamp(1601882705)
        return dt_object

# example
# timestamp = 1666069616
# created_at = timestamp_to_datetime(timestamp)
# print(created_at)  # result: 2022-10-18 09:00:16+00:00