from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import aiogram
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.emoji import emojize

import re
import os

from time import sleep

import yt_download as yt
from config import token,test_token

if "HEROKU" in list(os.environ.keys()):
    bot = Bot(token=token)
else:
    bot = Bot(token=test_token)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЭтот бот позволяет скачивать видео с любых сайтов!\nДля более подробной информации напиши /help   /available_services")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("К сожалению, эта часть еще не готова...\nПодождите немного!")

@dp.message_handler(commands=['available_services'])
async def process_services_command(message: types.Message):
    await message.reply(emojize('Список всех доступных сайтов здесь :point_down: : \n https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md'))


@dp.message_handler(content_types=['text'])
async def echo_download_message(message: types.Message):
    global videonote
    inline_btn_video = InlineKeyboardButton('Скачать как об.видео', callback_data='download_as_video')
    inline_btn_file = InlineKeyboardButton('Скачать как файл(пока нерабочее -_-)', callback_data='download_as_file')
    choose_inline = InlineKeyboardMarkup(row_width=1)
    choose_inline.add(inline_btn_video)
    choose_inline.add(inline_btn_file)
    echo_download=yt.Downloader(message.text)
    await message.reply("Увидел, начинаю скачивание...")

    try:
        videonote = open(echo_download.download_video(), 'rb')
    except:
        await message.reply("К сожалению, произошла ошибка...")
        print('Error :(')
        return
    await message.reply("Готово, видео скачано на сервер.\nКак вы хотите получить это видео?", reply_markup=choose_inline)


@dp.callback_query_handler(text='download_as_video')
async def choose_inline_video_callback_handler(query: types.CallbackQuery):
    await bot.send_message(query.from_user.id, 'Начинаю отправку')
    sleep(0.5)
    try:
        await bot.send_video(query.from_user.id, videonote)
    except:
        await bot.send_message(query.from_user.id, "К сожалению, произошла ошибка при отправке...")
    finally:
        videonote.close()

@dp.callback_query_handler(text='download_as_file')
async def choose_inline_video_callback_handler(query: types.CallbackQuery):
    await bot.send_message(query.from_user.id, 'Начинаю отправку')
    sleep(0.5)
    try:
        await bot.send_document(query.from_user.id, videonote)
    except:
        await bot.send_message(query.from_user.id, "К сожалению, произошла ошибка при отправке...")
    finally:
        videonote.close()



print("Starting")
executor.start_polling(dp)