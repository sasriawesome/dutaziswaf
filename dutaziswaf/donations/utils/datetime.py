from django.utils import timezone


def add_time(time, duration):
    old_date = timezone.datetime(
        2000, 1, 1, hour=time.hour, minute=time.minute, second=time.second)
    new_date = old_date + timezone.timedelta(minutes=90)
    return new_date.time()
