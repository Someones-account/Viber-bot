import calendar
import datetime
import re

from Commands import Command
from Session_control import write_session


def create_button(cols, rows, text, reply):
    return {
            "Columns": cols,
            "Rows": rows,
            "BgColor": "#3beb28",
            "ActionType": "reply",
            "ActionBody": reply,
            "ReplyType": "message",
            "Text": text
        }


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


def access_control(user_level, required_level):
    if user_level > required_level:
        raise PermissionError("Inappropriate access level")


def executor(message, viber_request, bot_repository, db_repository, sys_logger):
    try:
        group_id = db_repository.get_group_id(viber_request.sender.id)
        rgg = db_repository.get_request_group()
        if message.command == Command.START:
            start_menu(viber_request, bot_repository)
        elif message.command == Command.GETTER_LESSON:
            access_control(group_id, 3)
            all_lessons = db_repository.get_lessons()
            message_lesson(viber_request, bot_repository, all_lessons, "получить")
        elif message.command == Command.GETTER_DATE_TYPE:
            message_date_type(viber_request, bot_repository, message.full_message)
        elif message.command == Command.GETTER_DATE:
            message_date(viber_request, bot_repository, message.command_args.datetype)
            write_session(db_repository, viber_request.sender.id, message.full_message)
        elif message.command == Command.GET:
            access_control(group_id, 3)
            schedule_record = db_repository.get_schedule(message.command_args.lesson)
            get(message, viber_request, bot_repository, rgg, schedule_record, db_repository, sys_logger)
            start_menu(viber_request, bot_repository)
        elif message.command == Command.WRITER_LESSON:
            access_control(group_id, 2)
            all_lessons = db_repository.get_lessons()
            message_lesson(viber_request, bot_repository, all_lessons, "записать")
        elif message.command == Command.WRITER_DATE_TYPE:
            message_date_type(viber_request, bot_repository, message.full_message)
        elif message.command == Command.WRITER_DATE:
            message_date(viber_request, bot_repository, message.command_args.datetype)
            write_session(db_repository, viber_request.sender.id, message.full_message)
        elif message.command == Command.WRITER_CONTENT:
            record_content(viber_request, bot_repository)
            write_session(db_repository, viber_request.sender.id, message.full_message)
        elif message.command == Command.WRITE:
            access_control(group_id, 2)
            schedule_record = db_repository.get_schedule(message.command_args.lesson)
            write(message, viber_request, bot_repository, db_repository, schedule_record)
            start_menu(viber_request, bot_repository)
        elif message.command == Command.MODIFIER_LESSON:
            access_control(group_id, 2)
            all_lessons = db_repository.get_lessons()
            message_lesson(viber_request, bot_repository, all_lessons, "изменить")
        elif message.command == Command.MODIFIER_DATE:
            message_date(viber_request, bot_repository, "вручную")
            write_session(db_repository, viber_request.sender.id, message.full_message)
        elif message.command == Command.MODIFIER_CONTENT:
            record_content(viber_request, bot_repository)
            write_session(db_repository, viber_request.sender.id, message.full_message)
        elif message.command == Command.CHANGE:
            access_control(group_id, 2)
            change(viber_request, bot_repository, db_repository, message.command_args.lesson,
                   message.command_args.datetype, message.command_args.date)
            start_menu(viber_request, bot_repository)
        elif message.command == Command.HELP:
            users_help(viber_request, bot_repository)
        elif message.command == Command.UNKNOWN:
            bot_repository.send_message(viber_request.sender.id, 'Неизвестная комманда! Повторите ввод.')
    except PermissionError:
        bot_repository.send_message(viber_request.sender.id, "У вас недостаточный уровень доступа!")


def message_lesson(user_request, bot_repository, lessons, command):
    bot_repository.send_keyboard(user_request.sender.id, [
        create_button(3, 1, lesson, f"{command}*{lesson}") for lesson in lessons])


def message_date_type(user_request, bot_repository, message):
    bot_repository.send_keyboard(user_request.sender.id, [
        create_button(3, 1, "Следующий урок", f"{message}*автоматически*"),
        create_button(3, 1, "Ввести дату", f"{message}*вручную")
    ])


def message_date(user_request, bot_repository, date_type):
    if date_type == 'вручную':
        bot_repository.send_message(user_request.sender.id, "Введите пожалуйста дату:")


def record_content(user_request, bot_repository):
    bot_repository.send_message(user_request.sender.id, "Введите задание:")


def get(message, user_request, bot_repository, rgg, schedule_record, db_repository, logger):
    command_dict = {0: schedule_record.monday, 1: schedule_record.tuesday, 2: schedule_record.wednesday,
                    3: schedule_record.thursday, 4: schedule_record.friday, 5: 'no', 6: 'no'}
    full_date = get_full_date(message.command_args.date, '-')
    if full_date == "Unknown":
        raise ValueError('Incorrect date type!')
    result_date = get_date(command_dict, full_date)
    records = db_repository.get(message.command_args.lesson, result_date)
    requests = db_repository.get_homework_requests(message.command_args.lesson, result_date)
    weekday = datetime.datetime.strptime(result_date, "%Y-%m-%d").weekday()
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
            record = records[len(records) - 1]
            bot_repository.send_message(user_request.sender.id,
                                        f'Домашнее задание по "{message.command_args.lesson}" на {record.date}: {record.task}')
    else:
        bot_repository.send_message(user_request.sender.id, 'Извините, в указанный день нет этого урока!')


def write(message, user_request, bot_repository, db_repository, schedule_record):
    command_dict = {0: schedule_record.monday, 1: schedule_record.tuesday, 2: schedule_record.wednesday,
                    3: schedule_record.thursday, 4: schedule_record.friday, 5: 'no', 6: 'no'}
    records = db_repository.get(message.command_args.lesson, message.command_args.date)
    requests = db_repository.get_homework_requests(message.command_args.lesson, message.command_args.date)
    full_date = get_full_date(message.command_args.date, '-')
    if full_date == "Unknown":
        raise ValueError('Incorrect date type!')
    result_date = get_date(command_dict, full_date)
    weekday = datetime.datetime.strptime(result_date, "%Y-%m-%d").weekday()
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


def change(user_request, bot_repository, db_repository, lesson, date, task):
    query_obj = db_repository.get(lesson, date)
    if query_obj is []:
        bot_repository.send_message(user_request.sender.id, 'Извините, такой записи не существует!')
    else:
        db_repository.change(lesson=lesson, date=date, new_value=task)
        bot_repository.send_message(user_request.sender.id, 'Домашнее задание успешно изменено!')


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
        create_button(6, 2, "Назад", "Старт")])


def start_menu(user_request, bot_repository):
    bot_repository.send_keyboard(user_request.sender.id, [
        create_button(3, 1, "Помощь", "Помощь"),
        create_button(3, 1, "Получить", "Получить"),
        create_button(3, 1, "Записать", "Записать"),
        create_button(3, 1, "Изменить", "Изменить")
    ])
