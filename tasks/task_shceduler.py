from datetime import datetime, timedelta, date

class Shceduler:

    def __init__(self, **kwargs) -> None:
        self.result = None
        self.kwargs = kwargs

    def _get_interval_convert(self):
        now = self.kwargs["now_time"]
        if self.kwargs["service_counter"] == 0: # через 5мин
            return {
                    "start": now.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
                    }
        if self.kwargs["service_counter"] == 1: # за предыдущий день
            yesterday = now - timedelta(days=1)
            return {
                    "start": yesterday.strftime("%Y-%m-%dT00:01"),
                    "end": yesterday.strftime("%Y-%m-%dT23:59") 
                    }
        if self.kwargs["service_counter"] == 2: # за предыдущюю неделю
            yesterday = now - timedelta(days=1)
            last_week = yesterday - timedelta(weeks=1)
            return {
                "start": last_week.strftime("%Y-%m-%dT00:01"),
                "end": yesterday.strftime("%Y-%m-%dT23:59")
            }
        if self.kwargs["service_counter"] == 3: # за предыдущий месяц
            last_month = now.replace(day=1) - timedelta(days=1)
            return {
                "start": last_month.replace(day=1).strftime("%Y-%m-%dT00:01"),
                "end": last_month.strftime("%Y-%m-%dT23:59")
            }


        

