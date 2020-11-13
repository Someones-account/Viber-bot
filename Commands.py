from enum import Enum


class Command(Enum):
    GET = 'получить'
    WRITE = 'записать'
    CHANGE = 'изменить'
    HELP = "помощь"
    GET_SCH = "получить расписание"
    WRITE_SCH = "записать расписание"
    CHANGE_SCH = "изменить расписание"
    ACCESS = "доступ"
    GET_USERS = "получить пользователей"
    UNKNOWN = "Unknown"


class CommandTypes(Enum):
    SINGULAR = 0
    SHORTENED = 1
    STANDARD = 2
    EXPANDED = 3
    EXTRA_EXPAND = 4
