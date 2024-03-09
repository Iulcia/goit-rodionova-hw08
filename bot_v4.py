from collections import UserDict
from datetime import datetime
import pickle

# base class for forming records 
class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value: str):
        self.value = value
		
class Phone(Field):

    # returns only valid phones with 10 digits else exception
    def check_phone(self):

        if self.value.isdigit()	and len(self.value) == 10:
            return self.value
        else:
            raise ValueError("Phone number is invalid")     

class Birthday(Field):
    # returns only date with valid format else exception
    def __init__(self, value: str):
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            raise ValueError("Check date format => dd.mm.YYYY")

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")          

class Record:
    def __init__(self, name):
        self.name = Name(name) # store instance in attr
        self.phones = [] # could be more than 1 phone for each name
        self.birthday = None

    def add_phone(self, phone):
        phone_checked = Phone(phone).check_phone()
        self.phones.append(phone_checked) # adding valid Phone instance to the list of phones
         
    def edit_phone(self,old_value,new_value):
        old_phone = Phone(old_value).check_phone()
        new_phone = Phone(new_value).check_phone()

        if old_phone in self.phones:
            i = self.phones.index(old_phone) # replace old_number with new_phone
            self.phones[i] = new_phone
            return self.phones
        else:
            raise ValueError("Phone number for a change not found")

    def remove_phone(self, phone):
        try:
            checked_phone = Phone(phone).check_phone()
            self.phones.remove(checked_phone)
        except Exception as e:
            return print(f'Error: {e}')

    def find_phone(self, phone):
        checked_phone = Phone(phone).check_phone()   

        if checked_phone in self.phones:
            return checked_phone
        else:
            raise ValueError("Phone number not found")  

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        return f"Contact name: {self.name}, birthday: {self.birthday}, phones: {'; '.join(p for p in self.phones)}"

class AddressBook(UserDict):

    def __init__(self):
        self.data = {} # empty dict for initialization
  
    def add_record(self, record):
        self.data[record.name.value] = record # expand dictionary with name of user as a key and instance of Record for user as a value

    def find(self, name):
        if name in self.data:
           return self.data[name] # get instance of Record for user if found by name

    def delete(self, name):
        if name in self.data: # delete instance of Record for user if found by name
            del self.data[name]

# validations for input parameters
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Please, check your input for name, phone (10 digits) or birthday(format dd.mm.YYYY)."
        except KeyError:
            return "Person not found."
        except IndexError:
            return "Not applicable. Input parameter is missing."
        except Exception as e:
            return f'Error: {e}'

    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, phone_old, phone_new, *_ = args
    record = book.find(name)
    record.edit_phone(phone_old, phone_new)
    message = "Contact updated."

    return message

@input_error
def show_phone(args, book: AddressBook):
    record = book.find(args[0]) # name is the first arg

    return f'{args[0]} => {record.phones}'

def show_all(book: AddressBook):
    if book: 
        i = 1
        for name, record in book.data.items():
            print(f'{i} => {record}')
            i += 1
    else:
        print("No records found.")    

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name) # adds only if record exists by name
    record.add_birthday(birthday)
    return f"For {name} was added birthday date."

@input_error
def show_birthday(args, book: AddressBook) -> str:
    name = args[0]
    record = book.find(args[0]) # shows Bday only if record exists by name
    if record.birthday: 
        return f"{name} was born {record.birthday}."
    else:
        return f"Birthday day was not added yet."
   

def get_upcoming_birthdays(book) -> list:

    today_date = datetime.today().date()
    birthdays = []

    for value in book.values():
        user = {"name": value.name.value, "birthday": value.birthday.value}
        bdate = user["birthday"].date()

        #check if it's not end of the year to include early January bdays for upcoming year:
        last_day_of_this_year = datetime.strptime('31.12.'+str(today_date.year), "%d.%m.%Y").date()
        if ((last_day_of_this_year - today_date).days < 7) and bdate[3:5] == '01': 
            bdate = str(bdate.replace(year = (today_date + datetime.timedelta(days = 365).year))) # check for January birthdays next year, not current
        else:    
            bdate = str(bdate.replace(year = today_date.year)) # check bday for current year

        bdate = datetime.strptime(bdate, "%Y-%m-%d").date()
        diff = (bdate - today_date).days # delta in days btw bday date and today

        if 0 <= diff < 7: # add to the list only upcoming in 7 days bdays
            day_of_week = bdate.isoweekday() 
            if day_of_week < 6:
                birthdays.append({'name': user['name'], 'congratulation_date': bdate.strftime("%d.%m.%Y")})
            elif day_of_week == 6: # if it's Saturday, congratulate in 2 days, on Monday
                delta = datetime.timedelta(days = 2) 
                birthdays.append({'name': user['name'], 'congratulation_date': (bdate + delta).strftime("%d.%m.%Y")}) 
            else:
                delta = datetime.timedelta(days = 1) # if it's Sunday, congratulate in 1 day, on Monday
                birthdays.append({'name': user['name'], 'congratulation_date': (bdate + delta).strftime("%d.%m.%Y")}) 
    
    return birthdays

# serialization of data of book
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# deserialization of data of book. Keeps last stored state of book
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено
    
def main():
    book = AddressBook()
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args,book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            show_all(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(get_upcoming_birthdays(book))
    
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()            