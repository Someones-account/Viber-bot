import calendar
import datetime
import re

from Commands import Command
from DB_repository import DBRepository
import logging


logger = logging.getLogger("FlaskAppLog")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("log.txt")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_full_date(dat, sep):
    spl_date = dat.split(sep)
    day = datetime.datetime.today()
    if dat == '':
        return ''
    if re.search('[a-zA-Z]', dat) is not None:
        return "Unknown"
    if len(spl_date) == 1:
        return f'{day.year}-{day.month}-{int(spl_date[0])}'
    elif len(spl_date) == 2:
        return f'{day.year}-{int(spl_date[0])}-{int(spl_date[1])}'
    elif len(spl_date) == 3:
        return f'{int(spl_date[0])}-{int(spl_date[1])}-{int(spl_date[2])}'
    else:
        return "Unknown"


def get_date(lesson_available_info, date=''):
    today = datetime.datetime.today()
    system_date = today.day
    mon = today.month
    yea = today.year
    days = range(7)
    day_num = today.weekday()
    days_in_month = calendar.monthrange(yea, mon)[1]
    if date == '':
        last_days = list(days[day_num + 1:]) + list(days[:day_num + 1])
        for num, d_n in enumerate(last_days):
            if lesson_available_info[d_n] != 'no':
                result_date = system_date + num + 1
                break
        if result_date > days_in_month:
            result_date = result_date - days_in_month
            mon += 1
            if mon > 12:
                mon -= 12
                yea += 1
        result_date = f'{yea}-{mon}-{result_date}'
        return result_date
    else:
        return date


def executor(message, viber_request, bot_repository, d_session):
    db_repository = DBRepository(d_session)
    rgg = db_repository.get_request_group()
    group_id = db_repository.get_group_id(viber_request.sender.id)
    if message.command == Command.GET:
        if group_id != 4:
            logger.info(message)
            schedule_record = db_repository.get_schedule(message.command_args.lesson)
            get(message, viber_request, bot_repository, rgg, schedule_record, db_repository)
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.WRITE:
        if group_id < 3:
            schedule_record = db_repository.get_schedule(message.command_args.lesson)
            lesson_available_info = {0: schedule_record.monday, 1: schedule_record.tuesday, 2: schedule_record.wednesday,
                                     3: schedule_record.thursday, 4: schedule_record.friday, 5: 'no', 6: 'no'}
            result_date = get_date(lesson_available_info, message.command_args.date)
            records = db_repository.get(message.command_args.lesson, result_date)
            requests = db_repository.get_homework_requests(message.command_args.lesson, result_date)
            write(message, viber_request, bot_repository, db_repository, schedule_record, records, requests)
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.CHANGE:
        if group_id < 3:
            query_obj = db_repository.get(message.command_args.lesson, message.date)
            if query_obj is []:
                bot_repository.send_message(viber_request.sender.id, 'Извините, такой записи не существует!')
            else:
                db_repository.change(lesson=message.command_args.lesson, date=message.command_args.date,
                                     new_value=message.command_args.task)
                bot_repository.send_message(viber_request.sender.id, 'Домашнее задание успешно изменено!')
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.GET_SCH:
        if group_id == 1:
            a = db_repository.get_schedule(message.command_args.lesson)
            bot_repository.send_message(viber_request.sender.id, f'{a.lesson, a.monday, a.tuesday}'
                                                                 f'{a.wednesday, a.thursday, a.friday}')
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.WRITE_SCH:
        if group_id == 1:
            db_repository.write_schedule(message.command_args.lesson, message.command_args.mon, message.command_args.tue,
                                         message.command_args.wed, message.command_args.thu, message.command_args.fri)
            bot_repository.send_message(viber_request.sender.id, 'Готово!')
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.CHANGE_SCH:
        if group_id == 1:
            query_obj = db_repository.get_schedule(message.command_args.lesson)
            if query_obj is []:
                bot_repository.send_message(viber_request.sender.id, 'Извините, такой записи не существует!')
            else:
                db_repository.change_schedule(message.command_args.lesson, message.command_args.date,
                                              message.command_args.task)
                bot_repository.send_message(viber_request.sender.id, 'Готово!')
                # lesson, day, value
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.ACCESS:
        if group_id == 1:
            db_repository.change_access(message.command_args.lesson, message.command_args.date)
            bot_repository.send_message(viber_request.sender.id, 'Готово!')
        # id, level
        else:
            bot_repository.send_message(viber_request.sender.id, 'Извините, у вас нет доступа к данному действию!')
    elif message.command == Command.START:
        start_menu(viber_request, bot_repository)
    elif message.command == Command.HELP:
        users_help(viber_request, bot_repository)
    elif message.command == Command.GET_USERS.value:
        all_users = db_repository.get_list_users()
        username_list = (f'{user.username} | {user.user_id} | {user.group_id}' for user in all_users)
        users_data = '\n'.join(username_list)
        bot_repository.send_message(viber_request.sender.id, users_data)
    else:
        bot_repository.send_message(viber_request.sender.id, "Неизвестная команда! Повторите пожалуйста ввод.")


def get(message, user_request, bot_repository, rgg, schedule_record, db_repository):
    command_dict = {0: schedule_record.monday, 1: schedule_record.tuesday, 2: schedule_record.wednesday,
                    3: schedule_record.thursday, 4: schedule_record.friday, 5: 'no', 6: 'no'}
    check_result = get_full_date(message.command_args.date, '-')
    if check_result == "Unknown":
        raise ValueError('Incorrect date type!')
    result_date = get_date(command_dict, check_result)
    records = db_repository.message_lesson(message.command_args.lesson, result_date)
    requests = db_repository.get_homework_requests(message.command_args.lesson, result_date)
    weekday = datetime.datetime.today().weekday()
    if command_dict[weekday] != 'no':
        if len(records) == 0:
            if len(requests) == 0:
                db_repository.write_homework_request(message.command_args.lesson, result_date, user_request.sender.id)
                for us in rgg:
                    if us.user_rel.viber_id != user_request.sender.id:
                        bot_repository.send_message(us.user_rel.viber_id,
                                                    f'Можете пожалуйста дать домашнее задание по "{message.command_args.lesson}" на {message.date}?')
                bot_repository.send_message(user_request.sender.id,
                                            '''Извините, домашнего задания по данному уроку пока нет.''')
            else:
                bot_repository.send_message(user_request.sender.id,
                                            '''Извините, домашнего задания по данному уроку пока нет.''')
        else:
            records = records[len(records) - 1]
            bot_repository.send_message(user_request.sender.id,
                                        f'Домашнее задание по "{message.command_args.lesson}" на {records.date}: {records.task}')
    else:
        bot_repository.send_message(user_request.sender.id, 'Извините, в указанный день нет этого урока!')


def write(message, user_request, bot_repository, db_repository, schedule_record, records, requests):
    command_dict = {0: schedule_record.monday, 1: schedule_record.tuesday, 2: schedule_record.wednesday,
                    3: schedule_record.thursday, 4: schedule_record.friday, 5: 'no', 6: 'no'}
    full_date = get_full_date(message.command_args.date, '-')
    result_date = get_date(command_dict, full_date)
    weekday = datetime.datetime.today().weekday()
    if command_dict[weekday] != 'no':
        if len(records) == 0:
            db_repository.insert(message.command_args.lesson,  result_date, message.command_args.task)
            bot_repository.send_message(user_request.sender.id,
                                        f'Домашнее задание по "{message.command_args.lesson}" успешно записано. Спасибо!')
            for req in requests:
                bot_repository.send_message(req.user_id,
                                            f'Домашнее задание по "{message.command_args.task}" на {result_date}: {message.command_args.task}')
        else:
            bot_repository.send_message(user_request.sender.id,
                                        f'Домашнее задание по "{message.command_args.lesson}" уже существует!')
    else:
        bot_repository.send_message(user_request.sender.id, 'Извините, в указанный день нет этого урока!')


def users_help(user_request, bot_repository):
    bot_repository.send_message(user_request.sender.id, f'''Справка по использованию данного бота:
Для получения домашнего задания, введите: Получить*Название урока*Дата
Дата должна указываться в формате год-месяц-день, например: 2019-10-04
Если вы хотите получить актуальное домашнее задание, напишите и отправьте сообщение в Viber : Получить*Название урока*
Учтите, что все команды и названия уроков могут быть записаны в любом регистре.
Если вы хотите внести домашнее задание в базу данных,
напишите и отправьте сообщение в Viber: Записать*Название урока*Дата*Задание
Если вы хотите записать актуальное домашнее задание, введите: Записать*Название урока**Задание
При варианте без указания даты, символ * должен быть указан два раза!
Для изменения домашнего задания, введите: Изменить*Название урока*Дата*Задание
Для повторного выведения данной инструкции, введите: Помощь
Со всеми вопросами по использованию данного бота обращайтесь сюда:
Почта тех.поддержки: homework.bot2019@gmail.com
Контакт вайбер: 0682524842''')
    bot_repository.send_keyboard(user_request.sender.id, [
        {
            "Columns": 6,
            "Rows": 2,
            "BgColor": "#e6f5ff",
            "ActionType": "reply",
            "ActionBody": "Старт",
            "ReplyType": "message",
            "Text": "Назад"
        }])


def start_menu(user_request, bot_repository):
    bot_repository.send_keyboard(user_request.sender.id, [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "ActionType": "reply",
            "ActionBody": "Помощь",
            "ReplyType": "message",
            "Text": "Помощь"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "ActionType": "reply",
            "ActionBody": "Получить",
            "ReplyType": "message",
            "Text": "Получить"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "ActionType": "reply",
            "ActionBody": "Записать",
            "ReplyType": "message",
            "Text": "Записать"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "ActionType": "reply",
            "ActionBody": "Изменить",
            "ReplyType": "message",
            "Text": "Изменить"
        }
    ])
