from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, number):
        self.value = self.validate_number(number)

    def validate_number(self, number):
        if len(number) != 10:
            raise ValueError("Phone number must contain 10 digits")
        if not number.isdigit():
            raise ValueError("Phone number must contain only numbers")
        return number
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        phones = ', '.join(phone.value for phone in self.phones)
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday else "Not set"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

    def add_phone(self, number: str):
        if any(p.value == number for p in self.phones):
            raise ValueError("Phone already exists.")
        self.phones.append(Phone(number))

    def remove_phone(self, number: str):
        self.phones = list(filter(lambda phone: phone == number, self.phones))

    def edit_phone(self, old_phone: str, new_phone: str):
         for i, phone in enumerate(self.phones):
             if phone.value == old_phone:
                 self.phones[i] = Phone(new_phone)
                 return
         raise ValueError(f"Phone '{old_phone}' not found for contact '{self.name.value}'.")

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
            
    def add_birthday(self, date_str: str):
        self.birthday = Birthday(date_str)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                delta = (bday_this_year - today).days
                if 0 <= delta <= 7:
                    greet_date = bday_this_year
                    if greet_date.weekday() in [5, 6]:  # субота або неділя
                        # переносимо на понеділок
                        greet_date += timedelta(days=(7 - greet_date.weekday()))
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": greet_date.strftime("%d.%m.%Y")
                    })
        return upcoming
    
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return wrapper

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
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    return f"Phones: {', '.join(p.value for p in record.phones)}"

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, date_str = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_birthday(date_str)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        raise ValueError("Birthday not found.")
    return f"Birthday: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join([f"{b['name']}: {b['birthday']}" for b in upcoming])

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()