import datetime

class ExpiryCalculator:
    def near_expiry(self):
        today = datetime.date.today()
        current_weekday = today.weekday()
        days_until_thursday = (3 - current_weekday + 7) % 7
        next_thursday = today + datetime.timedelta(days=days_until_thursday)
        next_to_next_thursday = next_thursday + datetime.timedelta(days=7)
        return next_thursday.strftime("%d-%b-%Y"), next_to_next_thursday.strftime("%d-%b-%Y")

    def last_thursday_current_month(self, month=datetime.date.today().month):
        if month == 0: month = 12
        today = datetime.date.today()
        year = today.year
        last_day_of_month = datetime.date(year, month, 1) + datetime.timedelta(days=32)
        last_day_of_month = last_day_of_month.replace(day=1) - datetime.timedelta(days=1)
        last_weekday = last_day_of_month.weekday()
        days_to_last_thursday = (last_weekday - 3 + 7) % 7
        last_thursday = last_day_of_month - datetime.timedelta(days=days_to_last_thursday)
        return last_thursday.strftime("%d-%b-%Y")

    def monthly_expiry(self):
        near_expiry_date, next_expiry_date = self.near_expiry()
        curr_month_last_thursday = self.last_thursday_current_month()
        if (curr_month_last_thursday == near_expiry_date) or (curr_month_last_thursday == next_expiry_date):
            monthly_expiry_date = self.last_thursday_current_month((datetime.date.today().month + 1) % 12)
            return monthly_expiry_date
        else:
            return curr_month_last_thursday

    def expiry_dates(self):
        near_expiry_date, next_expiry_date = self.near_expiry()
        monthly_expiry_date = self.monthly_expiry()
        return [near_expiry_date, next_expiry_date, monthly_expiry_date]