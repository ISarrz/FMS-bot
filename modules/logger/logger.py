import traceback

from modules.database_api.interaction.insert import insert_logs
from datetime import datetime


def logger(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            text = f'{now}: {func.__name__}\n{repr(e)}\n'
            text +=  traceback.format_exc()
            insert_logs(text)

    return wrapper


def async_logger(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            text = f'{now}: {func.__name__}\n{repr(e)}\n'
            text += traceback.format_exc()
            insert_logs(text)

    return wrapper
