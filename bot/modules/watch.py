from telegram.ext import CommandHandler
from telegram import Bot, Update
from bot import DOWNLOAD_DIR, dispatcher, LOGGER
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage
from .mirror import MirrorListener
from bot.helper.mirror_utils.download_utils.youtube_dl_download_helper import YoutubeDLHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
import threading


def _watch(bot: Bot, update, isTar=False, isZip=False):
    mssg = update.message.text
    message_args = mssg.split(' ')
    name_args = mssg.split('|')
    
    try:
        link = message_args[1]
    except IndexError:
        msg = f"/{BotCommands.WatchCommand} [youtube-dl supported link] [quality] |[CustomName] to mirror with youtube-dl.\n\n"
        msg += "<b>Note: Quality and custom name are optional</b>\n\nExample of quality: audio, 144, 240, 360, 480, 720, 1080, 2160."
        msg += "\n\nIf you want to use custom filename, enter it after |"
        msg += f"\n\nExample:\n<code>/{BotCommands.WatchCommand} https://youtu.be/LmBYPXGqtss 720 |Eunha</code>\n\n"
        msg += "This file will be downloaded in 720p quality and it's name will be <b>Eunha</b>"
        sendMessage(msg, bot, update)
        return
    
    try:
      if "|" in mssg:
        mssg = mssg.split("|")
        qual = mssg[0].split(" ")[2]
        if qual == "":
          raise IndexError
      else:
        qual = message_args[2]
      if qual != "audio":
        qual = f'bestvideo[height<={qual}]+bestaudio/best[height<={qual}]'
    except IndexError:
      qual = "bestvideo+bestaudio/best"
    
    try:
      name = name_args[1]
    except IndexError:
      name = ""
    
    pswd = ""
    listener = MirrorListener(bot, update, pswd, isTar, isZip=isZip)
    ydl = YoutubeDLHelper(listener)
    threading.Thread(target=ydl.add_download,args=(link, f'{DOWNLOAD_DIR}{listener.uid}', qual, name)).start()
    sendStatusMessage(update, bot)


def watchTar(update, context):
    _watch(context.bot, update, True)

def watchZip(update, context):
    _watch(context.bot, update, True, True)

def watch(update, context):
    _watch(context.bot, update)


mirror_handler = CommandHandler(BotCommands.WatchCommand, watch,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
tar_mirror_handler = CommandHandler(BotCommands.TarWatchCommand, watchTar,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
zip_mirror_handler = CommandHandler(BotCommands.ZipWatchCommand, watchZip,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)


dispatcher.add_handler(mirror_handler)
dispatcher.add_handler(tar_mirror_handler)
dispatcher.add_handler(zip_mirror_handler)
