import asyncio
import logging.config

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from config import API_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH, WEBAPP_PORT, admins
from logger_config import logger_config
from parse import parse

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = 'localhost'

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

waiting_up = []
waiting_down = []
waiting_time = []
waiting_id = []

up = 2
lower = 1

available_products = []
sleep_time = 2

id_ = 'AsA4HchyP9ksD9Rw7iAEdVa9hxD47RtNx1ETuySbAxdo'


def del_actions(tg_id):
    if tg_id in waiting_down:
        waiting_down.remove(tg_id)

    if tg_id in waiting_down:
        waiting_up.remove(tg_id)

    if tg_id in waiting_time:
        waiting_time.remove(tg_id)

    if tg_id in waiting_time:
        waiting_id.remove(tg_id)


async def send_info(data):
    if len(data) == 2:
        text = f'''Товар "{data[0]}"[{data[1]}] исчез из продажи'''
    elif len(data) == 4:
        text = f'''Товар "{data[0]}"[{data[1]}] появился в наличии.
Размеры: {data[2]}
{data[3]}'''
    else:
        return

    for admin in admins:
        await bot.send_message(admin, text)


async def parse_cycle():
    while True:
        price = await parse(id_)
        if price:
            print(price)
        print('-----------')
        await asyncio.sleep(5)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    text = '''
/up - Установить верхний порог
/lower - Установить нижний порог
/cancel - Отменить действие
/time - Изменить время задержки
/id - Изменить отслеживание'''

    await message.answer(text)


@dp.message_handler(commands=['up'])
async def add_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_up.append(message.from_user.id)

    await message.answer(f'Верхний порог {up}. Введите новый порог:')


@dp.message_handler(commands=['lower'])
async def del_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_down.append(message.from_user.id)

    await message.answer(f'Нижний порог {lower}. Введите новый порог:')


@dp.message_handler(commands=['cancel'])
async def cancel_command(message: types.Message):
    tg_id = message.from_user.id
    if tg_id not in admins:
        return

    del_actions(tg_id)

    await message.answer('Действие отменено')


@dp.message_handler(commands=['id'])
async def list_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_id.append(message.from_user.id)

    await message.answer(f'Сейчас отслеживается {id_}. Введите amm_id:')


@dp.message_handler(commands=['time'])
async def time_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_time.append(message.from_user.id)
    text = f'''Сейчас задержка составляет {sleep_time} секунд.
Введите задержку в секундах:'''

    await message.answer(text)


@dp.message_handler()
async def listen_url(message: types.Message):
    global sleep_time
    global up
    global lower
    global id_
    tg_id = message.from_user.id
    if tg_id not in admins:
        return

    if tg_id in waiting_up:
        try:
            up = float(message.text)
        except ValueError:
            await message.delete()
        else:
            await message.answer('Порог изменен')

    elif tg_id in waiting_down:
        try:
            lower = float(message.text)
        except ValueError:
            await message.delete()
        else:
            await message.answer('Порог изменен')

    elif tg_id in waiting_time:
        try:
            time = int(message.text)
            sleep_time = time
        except Exception as e:
            await message.delete()
        else:
            await message.answer('Задержка изменена')

    elif tg_id in waiting_id:
        id_ = message.text
        await message.answer('amm_id изменен')

    else:
        await message.delete()

    del_actions(message.from_user.id)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    await parse_cycle()


async def on_shutdown(dp):
    logger.warning('Shutting down..')
    await bot.delete_webhook()
    logger.warning('Bye!')


if __name__ == '__main__':
    try:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    except Exception as e:
        logger.exception('STOP_WEBHOOK')
