import os
import re
import sys
import ffmpeg
import asyncio
import subprocess
from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.bot_utils import USERNAME
from config import AUDIO_CALL, VIDEO_CALL
from plugins.video import ydl, group_call
from helpers.decorators import authorized_users_only, sudo_users_only
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


@Client.on_message(filters.command(["play", f"play@{USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def play(client, m: Message):
    msg = await m.reply_text("🔄 `Se descarcă ...`")
    chat_id = m.chat.id
    media = m.reply_to_message
    if not media and not ' ' in m.text:
        await msg.edit("❗ __Trimite-mi un link de radio live / Link video YouTube / Răspunde la un audio sau la un streaming!__")

    elif ' ' in m.text:
        text = m.text.split(' ', 1)
        query = text[1]
        if not 'http' in query:
            return await msg.edit("❗ __Trimite-mi un link de radio live / Link video YouTube / Răspunde la un audio sau la un streaming!__")
        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, query)
        if match:
            await msg.edit("🔄 `Pornire audio YouTube ...`")
            try:
                meta = ydl.extract_info(query, download=False)
                formats = meta.get('formats', [meta])
                for f in formats:
                    ytstreamlink = f['url']
                link = ytstreamlink
            except Exception as e:
                return await msg.edit(f"❌ **Eroare de descărcare YouTube !** \n\n`{e}`")
                print(e)

        else:
            await msg.edit("🔄 `Pornire Live Audio Stream ...`")
            link = query

        vid_call = VIDEO_CALL.get(chat_id)
        if vid_call:
            await VIDEO_CALL[chat_id].stop()
            VIDEO_CALL.pop(chat_id)
            await sleep(0)

        aud_call = AUDIO_CALL.get(chat_id)
        if aud_call:
            await AUDIO_CALL[chat_id].stop()
            AUDIO_CALL.pop(chat_id)
            await sleep(0)

        try:
            await sleep(0)
            await group_call.join(chat_id)
            await group_call.start_audio(link, repeat=False)
            AUDIO_CALL[chat_id] = group_call
            await msg.delete()
            await m.reply_text(f"▶️ **Start [Audio Streaming]({query}) In {m.chat.title} !**",
               reply_markup=InlineKeyboardMarkup(
               [
                   [
                       InlineKeyboardButton(
                          text="⏸",
                          callback_data="pause_callback",
                       ),
                       InlineKeyboardButton(
                          text="▶️",
                          callback_data="resume_callback",
                       ),
                       InlineKeyboardButton(
                          text="⏹️",
                          callback_data="end_callback",
                       ),
                   ],
               ]),
            )
        except Exception as e:
            await msg.edit(f"❌ **A apărut o eroare !** \n\nEroare: `{e}`")
            return await group_call.stop()

    elif media.audio or media.document:
        await msg.edit("🔄 `Se descarcă ...`")
        audio = await client.download_media(media)

        vid_call = VIDEO_CALL.get(chat_id)
        if vid_call:
            await VIDEO_CALL[chat_id].stop()
            VIDEO_CALL.pop(chat_id)
            await sleep(0)

        aud_call = AUDIO_CALL.get(chat_id)
        if aud_call:
            await AUDIO_CALL[chat_id].stop()
            AUDIO_CALL.pop(chat_id)
            await sleep(0)

        try:
            await sleep(0)
            await group_call.join(chat_id)
            await group_call.start_audio(audio, repeat=False)
            AUDIO_CALL[chat_id] = group_call
            await msg.delete()
            await m.reply_text(f"▶️ **Start [Audio Streaming](https://t.me/pixeldeep) In {m.chat.title} !**",
               reply_markup=InlineKeyboardMarkup(
               [
                   [
                       InlineKeyboardButton(
                          text="⏸",
                          callback_data="pause_callback",
                       ),
                       InlineKeyboardButton(
                          text="▶️",
                          callback_data="resume_callback",
                       ),
                       InlineKeyboardButton(
                          text="⏹️",
                          callback_data="end_callback",
                       ),
                   ],
               ]),
            )
        except Exception as e:
            await msg.edit(f"❌ **A apărut o eroare !** \n\nEroare: `{e}`")
            return await group_call.stop()

    else:
        await msg.edit(
            "Doriți să căutați o melodie YouTube?",
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Da", switch_inline_query_current_chat=""
                    ),
                    InlineKeyboardButton(
                        "Nu ❌", callback_data="close"
                    )
                ]
            ]
        )
    )


@Client.on_message(filters.command(["restart", f"restart@{USERNAME}"]))
@sudo_users_only
async def restart(client, m: Message):
    k = await m.reply_text("🔄 `Restart ...`")
    await sleep(3)
    os.execl(sys.executable, sys.executable, *sys.argv)
    try:
        await k.edit("✅ **Repornit cu succes!")
    except:
        pass
