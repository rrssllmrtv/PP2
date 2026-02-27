#1
print("#1")
from datetime import datetime, timedelta

today = datetime.now()
five_days_ago = today - timedelta(days=5)

print("today:", today)
print("5 days ago:", five_days_ago)

#2
print("#2")
from datetime import datetime, timedelta

today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print("yesterday:", yesterday.date())
print("today:", today.date())
print("tomorrow:", tomorrow.date())

#3
print("#3")
from datetime import datetime

now = datetime.now()
no_microseconds = now.replace(microsecond=0)

print("with microsec:", now)
print("whithout microsec:", no_microseconds)

#4
print("#4")
from datetime import datetime

date1 = datetime(2026, 2, 6, 0, 0, 0)
date2 = datetime(2026, 5, 27, 0, 0, 0)

dif = date2 - date1
sec = dif.total_seconds()

print("difference in seconds:", sec)