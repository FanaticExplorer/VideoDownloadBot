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
import config as cg

if "HEROKU" in list(os.environ.keys()):
    bot = Bot(token=cg.token)
else:
    bot = Bot(token=cg.test_token)

dp = Dispatcher(bot)



@dp.message_handler(commands=['start'])
async def process_start_command(meUpdassage: types.Message):
    await message.reply("Привет!\nЭтот бот позволяет скачивать видео с любых сайтов!\nДля более подробной информации напиши /help   /available_services")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("К сожалению, эта часть еще не готова...\nПодождите немного!\nСкоро...\nОчень скоро")

@dp.message_handler(commands=['available_services'])
async def process_services_command(message: types.Message):
    await message.reply(emojize('Список всех доступных сайтов здесь: \n https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md'))


@dp.message_handler(content_types=['text'])
async def echo_download_message(message: types.Message):
    try:
        echo_download=yt.Downloader(message.text)
        await message.reply("Увидел, начинаю скачивание...")
        videonote = open(echo_download.download_video(), 'rb')
    except:
        await message.reply("К сожалению, произошла ошибка... Проверьте правильность ссылки")
        print('Error :(')
        return
    await message.reply("Готово, видео скачано на сервер.\nОтправляю...",)
    try:
        await bot.send_document(message.from_user.id, videonote)
    except:
        await bot.send_message(message.from_user.id, "К сожалению, произошла ошибка при отправке...")
    finally:
        videonote.close()




print("Starting")
executor.start_polling(dp)