# import pre-defined Libraries
import datetime


# Calculation of expiry dates
def near_expiry():
    #today = datetime.datetime.strptime("2023-08-3","%Y-%m-%d").date()
    today = datetime.date.today()
    current_weekday = today.weekday()
    # Calculate the number of days until the next Thursday (Thursday is 3, 0=Monday, 1=Tuesday, ..., 6=Sunday)
    days_until_thursday = (3 - current_weekday + 7) % 7
    
    # Calculate the date of the next Thursday
    next_thursday = today + datetime.timedelta(days=days_until_thursday)
    next_to_next_thursday = next_thursday + datetime.timedelta(days=7)
    
    return next_thursday.strftime("%d-%b-%Y"), next_to_next_thursday.strftime("%d-%b-%Y")

def last_thursday_current_month(month = datetime.date.today().month):
    if month == 0: month=12
    #today = datetime.datetime.strptime("2023-06-3","%Y-%m-%d").date()
    today = datetime.date.today()
    year = today.year;

    # Find the last day of the current month
    last_day_of_month = datetime.date(year, month, 1) + datetime.timedelta(days=32)
    last_day_of_month = last_day_of_month.replace(day=1) - datetime.timedelta(days=1)

    # Find the weekday of the last day of the month (0 = Monday, 6 = Sunday)
    last_weekday = last_day_of_month.weekday()

    # Calculate the number of days to go back to reach the last Thursday
    days_to_last_thursday = (last_weekday - 3 + 7) % 7

    # Calculate the date of the last Thursday of the current month
    last_thursday = last_day_of_month - datetime.timedelta(days=days_to_last_thursday)

    return last_thursday.strftime("%d-%b-%Y")
    
def monthly_expiry():
    near_expiry_date,next_expiry_date = near_expiry()
    curr_month_last_thursday = last_thursday_current_month()
    if (curr_month_last_thursday == near_expiry_date) or (curr_month_last_thursday == next_expiry_date):
        monthly_expiry_date = last_thursday_current_month((datetime.date.today().month + 1)%12)
        return monthly_expiry_date
    else:
        return curr_month_last_thursday

def expiry_dates():
    near_expiry_date,next_expiry_date = near_expiry()
    monthly_expiry_date = monthly_expiry()
    return [near_expiry_date, next_expiry_date, monthly_expiry_date]
