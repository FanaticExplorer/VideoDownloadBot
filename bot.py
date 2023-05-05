from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.bot.api import TelegramAPIServer
from aiogram.utils import exceptions as tg_errors
import asyncio

from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

import logging
import os
import copy

from urlextract import URLExtract
import tldextract


from time import sleep
from datetime import datetime

import downloader as dl
import config as cg



install()
c = Console(record=True)
rlog = logging.getLogger("rich")
extractor = URLExtract()


FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])

local_server = TelegramAPIServer.from_base('http://161.35.91.121:8081')
bot = Bot(token=cg.token, server=local_server)
dp = Dispatcher(bot)
queue = asyncio.Queue(maxsize=100)
while not queue.empty():
    queue_get = queue.get()
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
            try:
                await video_status_msg.edit_text('👍Начинаю загрузку!')
                video_path = await asyncio.to_thread(dl.download, user_url, f'{user_id}')
                c.log(f'Downloaded from site: {user_url}')
                c.log(f'Requested by user @{user_msg.from_user.username} ({user_id})')
                await video_status_msg.edit_text(text='✔️Загружено!\n🕒Отправляю...')
                await bot.send_video(user_msg.chat.id, open(video_path, 'rb'), reply_to_message_id=user_msg.message_id)
                os.remove(video_path)
                c.log(f'Video [blue u]{video_path}[/blue u] was sent!')
                await video_status_msg.delete()
            except Exception as e:
                str_error=str(e)
                if 'File too large for uploading' in str_error:
                    await video_status_msg.edit_text(text='❌Ошибка, видео слишком большое!')
                    c.log(f'Video [blue u]{video_path}[/blue u] was not sent because of it size')
                elif 'is not a valid URL' in str_error or 'Unsupported URL' in str_error:
                    await video_status_msg.edit_text(text='❌На этом сайте нет видео или сайт не поддерживается!')
                    c.log(f'Site {user_url} was not a video!')
                elif '[instagram:story]' in str_error and 'You need to log in to access this content' in str_error:
                    await video_status_msg.edit_text(text='❌Stories временно недоступны для скачивания')
                    c.log(f'Site {user_url} was a Stories')
                elif 'yt_dlp' in str(type(e)):
                    await video_status_msg.edit_text(text='❌Ошибка скачивания!')
                    c.log(f'[red u b]Failed downloading video from site {user_url} [/red u b]')
                    c.print_exception()
                elif 'aiogram' in str(type(e)):
                    await video_status_msg.edit_text(text='❌Ошибка отправки!')
                    c.log(f'[red u b]Failed sending a video to user [blue u]{user_id} [/blue u] [/red u b]')
                    c.print_exception()
                else:
                    await video_status_msg.edit_text(text='❌Непредвиденная ошибка')
                    c.print_exception()
    
    is_working = False

@dp.message_handler(commands = ['exit'])
async def process_exit_command(msg: types.message):
    if not msg.from_user.id == cg.fe_id:
        await msg.answer("You don't have enough access. Don't even try, it won't work for you.")
        return
    await msg.answer("Goodbye, cruel world!")

    log_name = bot_start.strftime("%Y-%m-%d-%H-%M-%S-log")
    if not os.path.exists(cg.logs_folder):
        os.mkdir(cg.logs_folder)
    
    c.rule("[bold red]Turning bot off...", style='red')
    c.save_html(f"{cg.logs_folder}/{log_name}.html")
    c.log(f'[bold green]The log file has been saved at {log_name}.html')
    try:
        await msg.reply_document(open(f"{cg.logs_folder}/{log_name}.html", 'rb'))
    except Exception as e:
        if 'File too large for uploading' in str(e):
            await msg.reply("Oh nooo... The log file is too large")
    exit(1)

@dp.message_handler(content_types = ['text'])
async def echo_download_msg(msg: types.message):
    msg_datetime = msg.date
    if msg_datetime<bot_start:
        return
    if not extractor.has_urls(msg.text):
        await msg.reply("❌В вашем сообщении нету ссылки!")
        return
    status_msg = await msg.reply('Вы добавлены в очередь!')
    await queue.put([msg, status_msg])
    user_id=msg.from_user.id
    c.log(f'User @{msg.from_user.username} ({user_id}) is added to the queue!')
    if not is_working:
        await downloader()

def launch_bot(l):
    try:
        global bot_start
        bot_start = datetime.now()
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        if l < 3:
            c.print_exception()
            c.rule("[bold red]Error, trying to restart...", style='red')
            sleep(5)
            c.rule("[bold yellow]Restarting...", style='yellow')
            launch_bot(l+1)
        else:
            log_name = bot_start.strftime("%Y-%m-%d-%H-%M-%S-log")
            if not os.path.exists(cg.logs_folder):
                os.mkdir(cg.logs_folder)
            c.save_html(f"{cg.logs_folder}/{log_name}.html")
            c.log(f'[bold green]The log file has been saved at {log_name}.html')
            c.print_exception()
            c.rule("[bold red]Turning off...", style='red')


if __name__ == '__main__':
    c.rule("[bold green]Starting bot!")
    launch_bot(0)