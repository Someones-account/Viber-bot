from datetime import datetime


def get_session(db_repository, user_id):
    current_time = datetime.now()
    session = db_repository.get_session(user_id)
    if session is not None:
        if session.validation > current_time:
            return session.previous_data
    return ""


def write_session(db_repository, user_id, data):
    current_time = datetime.now()
    minutes = int(current_time.strftime("%M")) + 5
    hours = int(current_time.strftime("%H"))
    if minutes > 59:
        hours += 1
        minutes -= 60
    expiration_time = current_time.replace(hour=hours, minute=minutes)
    db_repository.write_session(user_id, data, expiration_time)


def delete_session(db_repository, user_id):
    db_repository.delete_session(user_id)
