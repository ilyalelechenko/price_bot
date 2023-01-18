import asyncio
import logging
import urlextract
import sql
import tests

from aiogram import Bot, Dispatcher, types
from aiogram.utils.markdown import hlink
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from conf import webdriver, opts
from donotimport import token
from parcer import parcer_ozon, parcer_ozon2
from parcWB import parse_wb, parse_wb2

extractor = urlextract.URLExtract()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
sites = {'ozon.ru', 'wildberries.ru', 'www.ozon.ru', 'www.wildberries.ru'}


class Form(StatesGroup):
    match = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Отменил, можешь скидывать ссылку по новой.')


# Хэндлер на команду /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет, скинь ссылку на товар на озон или ВБ!"
                         "\n А и ещё, если у тебя есть персональная скидка на WB"
                         "напиши команду /discount и она будет тебе засчитываться")


# Хэндлер на команду /help
@dp.message_handler(state='*', commands='help')
@dp.message_handler(Text(equals='help', ignore_case=True), state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Этот бот, пока что, ищет только похожий товар по названию, а процент показывает, "
                         "насколько точное название необходимо найти")
    current_state = await state.get_state()
    if current_state is None:
        await message.answer('Скиньте ссылку и проверьте меня')
    else:
        await Form.match.set()
        await message.answer('Введите % совпадения названия')


"""
@dp.message_handler(state='*', commands='discount')
@dp.message_handler(Text(equals='discount', ignore_case=True), state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await Form.discount.set()
    # Дополнить проверку, есть ли уже персоналка
    await message.answer("Введите свою персональную скидку на ВБ, а если захотите её изменить"
                         "введите команду /discount")
"""


@dp.message_handler(content_types=["text"])
async def message_text(message: Message, state: FSMContext):
    print(message)
    sql.add_user(message.from_user.first_name,
                 message.from_user.username,
                 message.from_user.id)
    url_bot = extractor.find_urls(f'{message.text}')
    if len(url_bot) == 1 and bool(set(url_bot[0].split('/')) & sites):
        async with state.proxy() as data:
            data['url_bot'] = url_bot[0]
        await Form.match.set()
        await message.answer('Введите % совпадения названия'
                             '\nЕсли не понимаете о чем речь нажмите на команду /help'
                             '\nА если ошиблись с сылкой нажмите /cancel')
    else:
        return await message.reply('Не увидел ссылку, помните Озон или ВБ'
                                   '\nПопробуйте еще раз')


@dp.message_handler(lambda message: tests.for_check(message.text) is False, state=[Form.match])
async def message_match_incorrect(message: Message):
    return await message.reply('Необходимы цифры от 1 до 100'
                               '\nЕсли запутались нажмите /cancel что бы начать сначала')


"""
персоналку не расчитать, вб на каждый товар считает ее по своему
@dp.message_handler(lambda message: tests.for_check(message.text), state=Form.discount)
async def message_match(message: Message, state: FSMContext):
    sql.dicount_on_WB(message.from_user.id, int(message.text))
    await message.reply('Записал, теперь будет учитываться')
    await state.finish()
    await message.answer('Скиньте ссылку и проверьте меня')
"""


@dp.message_handler(lambda message: tests.for_check(message.text), state=Form.match)
async def message_match(message: Message, state: FSMContext):
    async with state.proxy() as data:
        url_bot = data['url_bot']
        match = int(message.text)
    browser = webdriver.Firefox(options=opts)
    if 'ozon.ru' in url_bot:
        await message.answer(f'Выбран озон сейчас попробуем найти на вб')
        about = parcer_ozon2(url_bot.split('/?')[0], browser)
        price1 = about[0].split()[0]
        price2 = about[0].split()[1]
        await message.answer(
            f'Вы выбрали {about[1]} и его цена со скидкой {price1} и без {price2}')
        sql.add_links(message.from_user.id, ozon=url_bot.split('/?')[0], price=price1)
        onWB = parse_wb2(about[1].lower(), browser, match)
        browser.close()
        if onWB is None:
            await message.answer('Ну чет , вроде, ни чего не нашел')
        else:
            await message.answer(f'Вот цена на ВБ {onWB[1]}')
            links2 = hlink('ссылка', onWB[0])
            await message.answer(f'А вот и {links2}, проверь', parse_mode="HTML")

    elif 'wildberries.ru' in url_bot:
        await message.answer(f'Выбран вб сейчас посмотрим на озон')
        about = parse_wb(url_bot, browser)
        await message.answer(f'Вы выбрали {about[0]} и его цена {about[1]}')
        sql.add_links(message.from_user.id, wb=url_bot, price=about[1])
        onOzon = parcer_ozon(about[0].lower(), browser, match)
        browser.close()
        if onOzon is None:
            await message.answer('Ну чет , вроде, ни чего не нашел')
        else:
            price1 = onOzon[0].split()[0]
            price2 = onOzon[0].split()[1]
            await message.answer(f'Вот цена на Озоне со скидкой {price1} и без {price2}')
            links2 = hlink('ссылка', onOzon[1])
            await message.answer(f'А вот и {links2}, проверьте', parse_mode='HTML')
    else:
        await message.answer(f'Что-то пошло не так')
    await state.finish()


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
