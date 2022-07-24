# (c) Jigarvarma2005

from bot import JVBot
from pyrogram import filters
from pyrogram.types import Message
from bot import AUTHORIZED_CHATS, OWNER_ID
import requests
from bot.helper.status_utils.pyro_status import progress_for_pyrogram
import time
import os
import shlex
import asyncio
import re
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

AUDIO_SUFFIXES = ("MP3", "M4A", "M4B", "FLAC", "WAV", "AIF", "OGG", "AAC", "DTS", "MID", "AMR", "MKA")
VIDEO_SUFFIXES = ("M4V", "MP4", "MOV", "FLV", "WMV", "3GP", "MPG", "WEBM", "MKV", "AVI")

def check_is_streamable(file_path:str) -> bool:
    return file_path.upper().endswith(VIDEO_SUFFIXES)

def check_is_audio(file_path:str) -> bool:
    return file_path.upper().endswith(AUDIO_SUFFIXES)

async def get_video_duration(input_file):
    metadata = extractMetadata(createParser(input_file))
    total_duration = 0
    if metadata.has("duration"):
        total_duration = metadata.get("duration").seconds
    return total_duration

@JVBot.on_message(filters.command("tgupload") & (filters.chat(AUTHORIZED_CHATS) | filters.user(OWNER_ID)))
async def tg_Uploader_Handler(bot: JVBot, message: Message):
    sts_msg = await message.reply_text("Please wait ...")
    try:
        input_str = message.text.split(" ", 1)[1]
    except:
        await message.reply_text("send along with file path")
        await sts_msg.delete()
        return
    if not os.path.exists(input_str):
        await sts_msg.edit(f"{input_str} not found")
        return
    current_time = time.time()
    thumb = str(message.from_usr.id) + ".jpg"
    file_name = os.path.basename(input_str)
    if check_is_streamable(file_name):
        duration = await get_video_duration(input_str)
        await message.reply_video(video=input_str,
                                  thumb=thumb,
                                  duration=duration,
                                  progress=progress_for_pyrogram,
                                  progress_args=("Uploading",
                                                 sts_msg,
                                                 current_time,
                                                 file_name))
    elif check_is_audio(file_name):
        duration = await get_video_duration(input_str)
        await message.reply_audio(audio=input_str,
                                  thumb=thumb,
                                  duration=duration,
                                  progress=progress_for_pyrogram,
                                  progress_args=("Uploading",
                                                 sts_msg,
                                                 current_time,
                                                 file_name))
    else:
        await message.reply_document(document=input_str,
                                  thumb=thumb,
                                  progress=progress_for_pyrogram,
                                  progress_args=("Uploading",
                                                 sts_msg,
                                                 current_time,
                                                 file_name))
    try:
        await sts_msg.delete()
    except:
        pass

@JVBot.on_message(filters.photo & (filters.chat(AUTHORIZED_CHATS) | filters.user(OWNER_ID)))
async def sav_Thumb_Handler(bot: JVBot, message: Message):
    sts_msg = await message.reply_text("Please wait ...")
    filename = await message.download(str(message.from_usr.id) + ".jpg")
    await sts_msg.edit("custom thumbnail saved ....")

@JVBot.on_message(filters.command("getthumb") & (filters.chat(AUTHORIZED_CHATS) | filters.user(OWNER_ID)))
async def tg_Uploader_Handler(bot: JVBot, message: Message):
    if os.path.exists(str(message.from_usr.id) + ".jpg"):
        await message.reply_photo(str(message.from_usr.id) + ".jpg")
    else:
        await message.reply_text("Thumbnail not found, send photo to save thumbnail.")

@JVBot.on_message(filters.command("webupload") & (filters.chat(AUTHORIZED_CHATS) | filters.user(OWNER_ID)))
async def web_Uploader_Handler(bot: JVBot, message: Message):
    error_msg = """send along with type and file path

**Available types:**
`anonfiles`, `transfer`, `filebin`, `anonymousfiles`,`megaupload`, `bayfiles`, `vshare`, `0x0`, `fileio`, `ninja`, `infura`, `bashupload`, `cat`

**Example:**
`/webupload transfer my_video.mp4`
"""
    sts_msg = await message.reply_text("Please wait ...")
    try:
        input_str = message.text.split(" ", 1)[1]
        type_ = input_str.split(" ", 1)[0].lower()
        file_path = input_str.split(" ", 1)[1]
    except:
        await message.reply_text(error_msg)
        await sts_msg.delete()
        return
    if not os.path.exists(file_path):
        await sts_msg.edit(f"{file_path} not found")
        return
    file_name = os.path.basename(file_path)
    hosts = {
        "anonfiles": "curl -F \"file=@{}\" https://anonfiles.com/api/upload",
        "transfer": "curl --upload-file \"{}\" https://transfer.sh/" + file_name,
        "filebin": "curl -X POST --data-binary \"@test.png\" -H \"filename"
                   ": {}\" \"https://filebin.net\"",
        "anonymousfiles": "curl -F file=\"@{}\" https://api.anonymousfiles.io/",
        "megaupload": "curl -F \"file=@{}\" https://megaupload.is/api/upload",
        "bayfiles": "curl -F \"file=@{}\" https://api.bayfiles.com/upload",
        "vshare": "curl -F \"file=@{}\" https://api.vshare.is/upload",
        "0x0": "curl -F \"file=@{}\" https://0x0.st",
        "bashupload": "curl -T \"{}\" https://bashupload.com",
        "fileio": "curl -F \"file =@{}\" https://file.io",
        "ninja": "curl -i -F file=@{} https://tmp.ninja/api.php?d=upload-tool",
        "cat": "curl -F reqtype=fileupload -F \"fileToUpload=@{}\" https://catbox.moe/user/api.php",
        "infura": "curl -X POST -F file=@'{}' \"https://ipfs.infura.io:5001/api/v0/add?pin=true\""
    }
    try:
        cmd = hosts[type_].format(file_path)
    except:
        await sts_msg.edit(error_msg)
        return
    await sts_msg.edit(f"`now uploading {file_name} to {type_} ...`")
    process = await asyncio.create_subprocess_exec(
        *shlex.split(cmd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    response, err = await process.communicate()
    links = '\n'.join(re.findall(r'https?://[^\"\']+', response.decode()))
    if links:
        await sts_msg.edit(f"**Found these links** :\n{links}")
    else:
        await sts_msg.edit('`' + response.decode() + err.decode() + '`')
