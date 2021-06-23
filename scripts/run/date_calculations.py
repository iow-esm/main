from datetime import datetime
from datetime import timedelta

def days_in_month(year,month):
    next_month = month+1
    next_year = year
    if (next_month == 13):
        next_month = 1
        next_year = year+1
    date1 = datetime.strptime(str(year)+'-'+str(month)+'-01','%Y-%m-%d')
    date2 = datetime.strptime(str(next_year)+'-'+str(next_month)+'-01','%Y-%m-%d')
    return (date2-date1).days

def add_days(my_datetime, days):
    return my_datetime + timedelta(days=days)

def add_months(my_datetime, months):
    year = int(datetime.strftime(my_datetime,'%Y'))
    month = int(datetime.strftime(my_datetime,'%m'))
    day = int(datetime.strftime(my_datetime,'%d'))
    daynew = day
    monthnew = month+months
    yearnew = year
    while monthnew>12: 
        monthnew=monthnew-12
        yearnew=year+1
    if daynew > days_in_month(yearnew,monthnew):
        daynew = days_in_month(yearnew,monthnew)
    return datetime.strptime(str(yearnew)+'-'+str(monthnew)+'-'+str(daynew),'%Y-%m-%d')

def add_years(my_datetime, years):
    year = int(datetime.strftime(my_datetime,'%Y'))
    month = int(datetime.strftime(my_datetime,'%m'))
    day = int(datetime.strftime(my_datetime,'%d'))
    daynew = day
    monthnew = month
    yearnew = year+years
    if daynew > days_in_month(yearnew,monthnew):
        daynew = days_in_month(yearnew,monthnew)
    return datetime.strptime(str(yearnew)+'-'+str(monthnew)+'-'+str(daynew),'%Y-%m-%d')
