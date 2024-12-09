from datetime import datetime, timedelta, date

class Shceduler:

    def __init__(self, **kwargs) -> None:
        self.result = None
        self.kwargs = kwargs

    def _get_interval_convert(self):
        if self.kwargs["service_counter"] == 0: # через 5мин
            return {
                    "start": self.kwargs['now_time'].strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": (self.kwargs['now_time'] - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
                    }
        if self.kwargs["service_counter"] == 1: # за предыдущий день
            now = self.kwargs["now_time"]
            yesterday = now - timedelta(days=1)
            return {
                    "start": yesterday.strftime("%Y-%m-%dT00:01"),
                    "end": yesterday.strftime("%Y-%m-%dT23:59") 
                    }
        if self.kwargs["service_counter"] == 2: # за предыдущюю неделю
            pass
        if self.kwargs["service_counter"] == 3: # за предыдущий месяц
            pass


        

