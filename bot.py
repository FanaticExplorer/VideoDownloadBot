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
        echo_download=yt.Downloader(msg.text)
    except DownloadError:
        text_of_message=msg.text
        if "\n" in msg.text:
            text_of_message.replace("\n"," ",1)
            text_of_message.replace("\r"," ",1)
        link_from_message=re.search("(?P<url>https?://[^\s]+)", text_of_message).group("url")
        echo_download=yt.Downloader(link_from_message)
    videonote = open(echo_download.download_video(), 'rb')
    await msg.answer_video(videonote)
    videonote.close()

print("starting")
executor.start_polling(dp)