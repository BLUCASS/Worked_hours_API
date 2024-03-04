from model import engine, WorkedHours
from sqlalchemy.orm import sessionmaker
from sqlalchemy import between


Session = sessionmaker(bind=engine)
session = Session()


class Week:
    """This class will deal with the week"""
    def __init__(self) -> None:
        self.total_hours = 0
        self.total_money = 0

    def get_week(self, data) -> str:
        """This function will manage the whole week, including the daily journey,
        daily salary, weekly salary, etc...And it will add everything in a dict."""
        from datetime import datetime
        try:
            date = datetime.strptime(data["date"], "%Y-%m-%d")
        except:
            date = datetime.now()
        salary = self.__verify_salary(data["salary"], data["sunday_salary"])
        monday = self.__get_day(data['monday_in'], 
                                data['monday_out'], 
                                salary[0],
                                self.__get_date(date, 0))
        tuesday = self.__get_day(data['tuesday_in'], 
                                 data['tuesday_out'], 
                                 salary[0],
                                 self.__get_date(date, 1))
        wednesday = self.__get_day(data['wednesday_in'], 
                                   data['wednesday_out'], 
                                   salary[0],
                                   self.__get_date(date, 2))
        thursday = self.__get_day(data['thursday_in'], 
                                  data['thursday_out'], 
                                  salary[0],
                                  self.__get_date(date, 3))
        friday = self.__get_day(data['friday_in'], 
                                data['friday_out'], 
                                salary[0],
                                self.__get_date(date, 4))
        saturday = self.__get_day(data['saturday_in'], 
                                  data['saturday_out'], 
                                  salary[0],
                                  self.__get_date(date, 5))
        sunday = self.__get_day(data['sunday_in'], 
                                data['sunday_out'], 
                                salary[1],
                                self.__get_date(date, 6))
        dates = [monday[0], tuesday[0], wednesday[0], thursday[0], 
                 friday[0], saturday[0], sunday[0]]
        exists = self.__check_if_exists(dates)
        if exists: return False
        new_list = self.__get_list(monday, tuesday, wednesday, thursday, friday,
                                   saturday, sunday)
        return new_list
    
    def __check_if_exists(self, dates):
        exists = False
        for date in dates:
            ok = session.query(WorkedHours).filter(WorkedHours.date == date).first() is not None
            if ok: exists = True
        return exists

    def __get_date(self, date, days) -> str:
        """This function receives a datetime object and returns it as a str."""
        from datetime import timedelta
        new_day = date + timedelta(days=days)
        formatted_day = new_day.strftime("%d/%m/%Y")
        return formatted_day
    
    def __get_list(self, monday, tuesday, wednesday, thursday, 
                   friday, saturday, sunday) -> list:
        """This function receives the day with its values and returns a list
        linking the values to the week day"""
        new_list = {
            'monday': monday,
            'tuesday': tuesday,
            'wednesday': wednesday,
            'thursday': thursday,
            'friday': friday,
            'saturday': saturday,
            'sunday': sunday,
        }
        for day in new_list.items():
            DbManagement().insert_day(day[0], day[1])
        return new_list

    def __verify_salary(self, salary, sunday_salary) -> str:
        """This function will verify the salary, if there is no value, it will
        return the mininum wage in Ireland today (24/02/2024)"""
        if salary == '': salary = 12.7
        if sunday_salary == '': sunday_salary = 12.7
        return float(salary), float(sunday_salary)

    def __get_day(self, begin, finish, salary, day) -> str:
        """This function will return the day in the right format, including the
        journey, the salary, the total for the day and the total for the week."""
        from datetime import datetime
        clockin = datetime.strptime(begin, "%H:%M")
        clockout = datetime.strptime(finish, "%H:%M")
        shift = clockout - clockin
        hours_number = shift.total_seconds()/3600
        self.total_hours += hours_number
        daily_rate = ((shift.total_seconds()/3600) * salary)
        self.total_money += daily_rate
        return day, str(shift), salary, round(daily_rate, 2), round(self.total_hours, 2), round(self.total_money, 2)


class DbManagement:

    def insert_day(self, name, day) -> None:
        try:
            worked_day = WorkedHours(day=name,
                                     date=day[0],
                                     hours=day[1],
                                     salary=day[2],
                                     day_total=day[3],
                                     week_hours=day[4],
                                     week_money=day[5])
            session.add(worked_day)
        except:
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    def view(self, data) ->str:
        from datetime import datetime
        try:
            start = datetime.strptime(data["start"], "%Y-%m-%d")
            formatted_start = start.strftime("%d/%m/%Y")
            finish = datetime.strptime(data["finish"], "%Y-%m-%d")
            formatted_finish = finish.strftime("%d/%m/%Y")
            data = self.__search_range(formatted_start, formatted_finish)
            if len(data) == 0: raise IndexError
            return data
        except:
            return False

    def update(self, date):
        exists = self.__check_date(date)
        if exists == False: return False
        return True

    def __check_date(self, date) -> bool:
        try:
            data = session.query(WorkedHours).filter(WorkedHours.date == date).first()
            if len(data) == 0: raise IndexError
        except: return False
        else: return data

    def __search_range(self, start, finish):
        try:
            date1 = session.query(WorkedHours).filter(WorkedHours.date == start).first() is not None
            date2 = session.query(WorkedHours).filter(WorkedHours.date == finish).first() is not None
            if date1 == False or date2 == False: raise IndexError
            first_date = session.query(WorkedHours).filter(WorkedHours.date == start).first()
            first_id = first_date.id
            last_id = first_id + 7
            data = session.query(WorkedHours).filter(WorkedHours.id.between(first_id, last_id)).all()
            if len(data) == 0: raise IndexError
        except: return False
        else:
            return data