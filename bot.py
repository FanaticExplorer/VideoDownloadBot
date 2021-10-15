from os import link
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
import re

from youtube_dl.utils import DownloadError

import yt_download as yt
from config import token

bot = Bot(token=token)
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
async def echo_download_message(msg: types.Message):
    try:
        videonote = open(yt.download_video(msg.text), 'rb')
    except DownloadError:
        link_from_message=re.search("(?P<url>https?://[^\s]+)", msg.text).group("url")
        videonote = open(yt.download_video(link_from_message), 'rb')
    #await msg.answer_video(videonote)
    await bot.send_document(msg.from_user.id, videonote)
    videonote.close()

print("starting")
executor.start_polling(dp)