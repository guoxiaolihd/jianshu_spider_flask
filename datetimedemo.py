from datetime import datetime


def date_to_week(str_date):
    time_date = datetime.strptime(str_date,'%Y-%m-%d %H:%M:%S')
    week_day_dict = {0: '0周一', 1: '1周二', 2: '2周三', 3: '3周四',
                     4: '4周五', 5: '5周六', 6: '6周日'}
    print(time_date)
    print(type(time_date))
    return week_day_dict[time_date.weekday()]

if __name__ == '__main__':
    str_date = '2020-09-29 12:32:21'
    week = date_to_week(str_date)
    print(week)