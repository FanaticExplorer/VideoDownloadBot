from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
import re


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
async def echo_download_message(message: types.Message):
    echo_download=yt.Downloader(message.text)
    try:
        videonote = open(echo_download.download_video(), 'rb')
    # except:
    #     try:
    #         text_of_message=message.text
    #         link_from_message=re.search("(?P<url>https?://[^\s]+)", text_of_message).group("url")
    #         echo_download=yt.Downloader(link_from_message)
    #     except:
    #         await message.reply("К сожалению, произошла ошибка...\nПопробуйте вставить именно ссылку, без доп.текста!")
    #         print('Failure finding the link')
    #         return
    except:
        await message.reply("К сожалению, произошла ошибка...\n")
        print('Error :(')
        return
    await message.reply("Готово, видео скачано на сервер.\nНачинаю отправку вам...")
    await message.answer_video(videonote)
    videonote.close()

print("Starting")
executor.start_polling(dp)