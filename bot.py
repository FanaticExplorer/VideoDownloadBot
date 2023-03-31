from aiogram import Bot, types
# from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.bot.api import TelegramAPIServer
from aiogram.utils import exceptions as tg_errors
import asyncio

from rich.logging import RichHandler
from rich.console import Console
import logging
from os import remove as fdel


from urlextract import URLExtract
import tldextract
from yt_dlp.utils import DownloadError
import pretty_errors


import downloader as dl
import config as cg


pretty_errors.activate()

c = Console()
rlog = logging.getLogger("rich")
extractor = URLExtract()

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])
# logger = logging.getLogger(__name__)

local_server = TelegramAPIServer.from_base('http://localhost:8081')
try:
    bot = Bot(token=cg.token, server=local_server)
except:
    bot = Bot(token=cg.token)
dp = Dispatcher(bot)
queue = asyncio.Queue(maxsize=100)
is_working = False

with open(cg.start_msg_path, encoding='utf8') as f_start:
    start_msg = f_start.read()

with open(cg.help_msg_path, encoding='utf8') as f_help:
    help_msg = f_help.read()



@dp.message_handler(commands = ['start'])
async def process_start_command(msg: types.message):
    await msg.reply(start_msg)



@dp.message_handler(commands = ['help'])
async def process_help_command(msg: types.message):
    await msg.reply(help_msg, disable_web_page_preview = True)


@dp.message_handler(commands = ['available_services'])
async def process_services_command(msg: types.message):
    await bot.send_message(msg.from_user.id, 
                        '''<a href = 'https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md'>'''
                        +'📜Список всех доступных сайтов</a>', 
                        parse_mode = 'HTML', 
                        disable_web_page_preview = True)


async def downloader(**args):
    global is_working
    is_working = True
    while not queue.empty():
        queue_get = await queue.get()
        user_msg = queue_get[0]
        video_status_msg = queue_get[1]
        await video_status_msg.edit_text('👍Ваша очередь!')
        user_id=user_msg.from_user.id
        user_urls = extractor.find_urls(user_msg.text)
        for user_url in user_urls:
            sdm, dm, suf = tldextract.extract(user_url)

            await video_status_msg.edit_text('👍Начинаю загрузку!')
            try:
                video_path = await asyncio.to_thread(dl.download, user_url, f'{user_id}')
                c.log(f'Downloaded from site: {user_url}')
                c.log(f'Requested by user @{user_msg.from_user.username} ({user_id})')
            except DownloadError:
                if dm == 'instagram':
                    await video_status_msg.edit_text(text='❌Ошибка скачивания!\n'+
                                    'Эта ошибка может возникнуть при попытке скачать сториз. '+
                                    'Данная функция будет добавлена позже.')
                    return
                else:
                    await video_status_msg.edit_text(text='❌Ошибка скачивания! '+
                                    'Проверьте, правильная ли ссылка, или повторите загрузку')
                    rlog.exception(f'Failed to download video from: [blue u]{user_url}')
                    return
            except:
                await video_status_msg.edit_text(text='❌Во время скачивания произошла ошибка!'+
                                    'Проверьте, правильная ли ссылка, или повторите загрузку')
                rlog.exception(f'Failed to download video from: [blue u]{user_url}')
                return
            
            await video_status_msg.edit_text(text='✔️Загружено!\n🕒Отправляю...')
            try:
                await bot.send_video(user_msg.chat.id, open(video_path, 'rb'), reply_to_message_id=user_msg.message_id)
                fdel(video_path)
            except:
                await video_status_msg.edit_text(text='❌Ошибка отправки файла!'+
                                'Попробуйте еще раз.')
                rlog.exception(f'Failed sending a video to user [blue u]{user_id}')
                return
            c.log(f'Video [blue u]{video_path}[/blue u] was sent!')
            await video_status_msg.delete()
    
    is_working = False


@dp.message_handler(content_types = ['text'])
async def echo_download_msg(msg: types.message):
    if not extractor.has_urls(msg.text):
        await msg.reply("❌В вашем сообщении нету ссылки!")
        return
    status_msg = await msg.reply('Вы добавлены в очередь!')
    await queue.put([msg, status_msg])
    user_id=msg.from_user.id
    c.log(f'User @{msg.from_user.username} ({user_id}) is added to the queue!')
    if not is_working:
        await downloader()




c.rule("[bold green]Starting bot!")
try:
    executor.start_polling(dp)
except:
    c.rule("[bold red]Error, turning bot off...", style='red')