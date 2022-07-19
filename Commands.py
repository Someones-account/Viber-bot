from enum import Enum


class Command(Enum):
    GET = 'получить'
    WRITE = 'записать'
    CHANGE = 'изменить'
    HELP = "помощь"
    START = "старт"
    GET_SCH = "получить расписание"
    WRITE_SCH = "записать расписание"
    CHANGE_SCH = "изменить расписание"
    ACCESS = "доступ"
    GET_USERS = "получить пользователей"
    GETTER_LESSON = 'урок'
    GETTER_DATE = "дата"
    GETTER_DATE_TYPE = "тип даты"
    WRITER_LESSON = 'урок_запись'
    WRITER_DATE = "дата_запись"
    WRITER_DATE_TYPE = "тип даты_запись"
    WRITER_CONTENT = "w_c"
    MODIFIER_LESSON = 'урок_изменение'
    MODIFIER_DATE = "дата_изменение"
    MODIFIER_CONTENT = "m_c"
    UNKNOWN = "Unknown"


class CommandTypes(Enum):
    SINGULAR = 0
    SHORTENED = 1
    STANDARD = 2
    EXPANDED = 3
    EXTRA_EXPAND = 4
