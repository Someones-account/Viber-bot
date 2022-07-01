# coding=utf-8
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest, ViberConversationStartedRequest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from my_parser import parse_message
from Utils import executor
from DB_repository import seek_user, DBRepository
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
engine = create_engine(
    'mysql+mysqlconnector://Viberbothomework:a111111a@Viberbothomework.mysql.pythonanywhere-services.com/Viberbothomework$Viberbot',
    pool_recycle=100)
Session = sessionmaker(bind=engine)
session = Session()
db_repository = DBRepository(session)
app = Flask(__name__)
viber = Api(BotConfiguration(
    name='HomeWorkBot',
    avatar='https://previews.123rf.com/images/benchart/benchart1204/benchart120400018/13237662-illustration-of-a-cartoon-opened-brown-book.jpg',
    auth_token='49c4a6417067d578-dc6f8feb8f05fd7c-c4250675556cac92'))


class BotRepository(object):
    def __init__(self, api_object):
        self.api = api_object

    def send_message(self, text, recipient):
        self.api.send_messages(recipient, TextMessage(text=text))


@app.route('/', methods=['POST'])
def main_app():
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)
    viber_request = viber.parse_request(request.get_data())
    if isinstance(viber_request, ViberConversationStartedRequest):
        seek_user(viber_request, session)
        db_repository.add_user(viber_request.user.id, viber_request.user.name)
        viber.send_messages(viber_request.user.id, [
            TextMessage(text='''Справка по использованию данного бота:
        Для получения домашнего задания, введите: Получить*Название урока*Дата
        Дата может указываться числом, но только в том случае, если это число текущего месяца
        Иначе нужно будет ввести дату в формате месяц-день, например: 11-30
        Если дата указывается на следующий год, то она должна указываться в формате год-месяц-день, например: 2019-10-04
        Если вы хотите получить актуальное домашнее задание, введите: Получить*Название урока*
        Учтите, что все команды и названия уроков могут быть записаны в любом регистре
        Для записи домашнего задания, введите: Записать*Название урока*Дата*Задание
        Если вы хотите записать актуальное домашнее задание, введите: Записать*Название урока**Задание
        При варианте без указания даты, символ * должен быть указан два раза!
        Для изменения домашнего задания, введите: Изменить*Название урока*Дата*Задание
        Для повторного выведения данной справки, введите: Помощь
        Со всеми вопросами по использованию данного бота обращайтесь сюда:
        Почта тех.поддержки: homework.bot2019@gmail.com
        Контакт вайбер: 0682524842''')
        ])

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        str_message = parse_message(message.text)
        bot_repository = BotRepository(viber)
        logger.info("Invoked")
        executor(str_message, viber_request, bot_repository, session)

    return Response(status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context='adhoc')