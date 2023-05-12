from aiogram import Bot, Dispatcher, types
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import FSInputFile
import asyncio

from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

import logging
import os
import zipfile

from urlextract import URLExtract


from time import sleep
from datetime import datetime

import downloader as dl
import config as cg



install()
c = Console(record=True, log_path=False)
rlog = logging.getLogger("rich")
extractor = URLExtract()


FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, 
                    format=FORMAT, 
                    datefmt="[%X]", 
                    handlers=[RichHandler(
                        rich_tracebacks=True, show_path=False)])
logging.getLogger("aiogram.event").disabled = True

session = AiohttpSession(
    api=TelegramAPIServer.from_base(
        cg.config_o.api_server.get_secret_value()))
bot = Bot(token=cg.config_o.token.get_secret_value(), 
        session=session)
dp = Dispatcher()
queue = asyncio.Queue(maxsize=100)
while not queue.empty():
    queue_get = queue.get()
is_working = False

with open(cg.start_msg_path, encoding='utf8') as f_start:
    start_msg = f_start.read()

with open(cg.help_msg_path, encoding='utf8') as f_help:
    help_msg = f_help.read()

def update_logs(name):
    if not os.path.exists(cg.logs_folder):
        os.mkdir(cg.logs_folder)
    if not os.path.exists(f"{cg.logs_folder}/{name}"):
        os.mkdir(f"{cg.logs_folder}/{name}")
    c.save_html(f"{cg.logs_folder}/{name}/rich-logs.html", clear=False)
    c.save_text(f"{cg.logs_folder}/{name}/rich-logs.log", clear=False)
    c.log(f'[bold green]Logs updated')

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=rel_path)

async def on_startup(dispatcher):
    global bot_start, log_name
    bot_start = datetime.now()
    log_name = bot_start.strftime("%Y-%m-%d-%H-%M-%S-log")

@dp.message(Command('start'))
async def process_start_command(msg: types.message):
    await msg.reply(start_msg)



@dp.message(Command('help'))
async def process_help_command(msg: types.message):
    await msg.reply(help_msg, disable_web_page_preview = True)

@dp.message(Command('logs'))
async def process_logs_command(msg: types.message):
    if not msg.from_user.id == cg.fe_id:
        await msg.answer("You don't have enough access. Don't even try, it won't work for you.")
        return
    log_send_status = await msg.reply("Updating logs...")
    update_logs(log_name)
    await log_send_status.edit_text('Sending logs...')
    zip_folder(f"{cg.logs_folder}/{log_name}", cg.logs_zip)
    c.log('Archive has been created')
    logs_archive = FSInputFile(cg.logs_zip)
    await msg.reply_document(logs_archive)
    await log_send_status.delete()

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
                # video = open(video_path, 'rb')
                video = FSInputFile(video_path)
                await bot.send_video(user_msg.chat.id, video, reply_to_message_id=user_msg.message_id)
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
            finally:
                update_logs(log_name)
    
    is_working = False

@dp.message(F.text)
async def echo_download_msg(msg: types.message):
    if msg.text.startswith('/'):
        await msg.reply("❌Unknown command")
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

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    c.rule("[bold green]Starting bot!")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(1)
    except SystemExit:
        exit(1)