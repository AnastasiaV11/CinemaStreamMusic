"""
VideoPlayerBot, Telegram Video Chat Bot
Copyright (c) 2021  Asm Safone <https://github.com/AsmSafone>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import os
import re
import sys
import time
import ffmpeg
import asyncio
import subprocess
from asyncio import sleep
from plugins.nopm import User
from youtube_dl import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import GroupCallFactory
from helpers.bot_utils import USERNAME
from config import AUDIO_CALL, VIDEO_CALL
from youtubesearchpython import VideosSearch
from helpers.decorators import authorized_users_only
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


ydl_opts = {
        "quiet": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
}
ydl = YoutubeDL(ydl_opts)
group_call = GroupCallFactory(User, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM).get_group_call()


@Client.on_callback_query(filters.regex("pause_callback"))
async def pause_callbacc(client, CallbackQuery):
    chat_id = CallbackQuery.message.chat.id
    if chat_id in AUDIO_CALL:
        text = f"⏸ Pauză !"
        await AUDIO_CALL[chat_id].set_audio_pause(True)
    elif chat_id in VIDEO_CALL:
        text = f"⏸ Pauză !"
        await VIDEO_CALL[chat_id].set_video_pause(True)
    else:
        text = f"❌ Nimic nu rulează !"
    await Client.answer_callback_query(
        CallbackQuery.id, text, show_alert=True
    )

@Client.on_callback_query(filters.regex("resume_callback"))
async def resume_callbacc(client, CallbackQuery):
    chat_id = CallbackQuery.message.chat.id
    if chat_id in AUDIO_CALL:
        text = f"▶️ Reluat !"
        await AUDIO_CALL[chat_id].set_audio_pause(False)
    elif chat_id in VIDEO_CALL:
        text = f"▶️ Reluat !"
        await VIDEO_CALL[chat_id].set_video_pause(False)
    else:
        text = f"❌ Nimic nu rulează !"
    await Client.answer_callback_query(
        CallbackQuery.id, text, show_alert=True
    )


@Client.on_callback_query(filters.regex("end_callback"))
async def end_callbacc(client, CallbackQuery):
    chat_id = CallbackQuery.message.chat.id
    if chat_id in AUDIO_CALL:
        text = f"⏹️ Oprit !"
        await AUDIO_CALL[chat_id].stop()
        AUDIO_CALL.pop(chat_id)
    elif chat_id in VIDEO_CALL:
        text = f"⏹️ Oprit !"
        await VIDEO_CALL[chat_id].stop()
        VIDEO_CALL.pop(chat_id)
    else:
        text = f"❌ Nimic nu a pornit !"
    await Client.answer_callback_query(
        CallbackQuery.id, text, show_alert=True
    )
    await Client.send_message(
        chat_id=CallbackQuery.message.chat.id,
        text=f"✅ **Streamingul a fost oprit și a părăsit chatul video !**"
    )
    await CallbackQuery.message.delete()


@Client.on_message(filters.command(["stream", f"stream@{USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def stream(client, m: Message):
    msg = await m.reply_text("🔄 `Prelucrare ...`")
    chat_id = m.chat.id
    media = m.reply_to_message
    if not media and not ' ' in m.text:
        await msg.edit("❗ __Trimite-mi un link de stream live / Link video YouTube /Răspunde la un videoclip pentru a începe redarea în stream video!__")

    elif ' ' in m.text:
        text = m.text.split(' ', 1)
        query = text[1]
        if not 'http' in query:
            return await msg.edit("❗ __Trimite-mi un link de stream live / Link video YouTube /Răspunde la un videoclip pentru a începe redarea în stream video!__")
        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, query)
        if match:
            await msg.edit("🔄 `Starting YouTube Video Stream ...`")
            try:
                meta = ydl.extract_info(query, download=False)
                formats = meta.get('formats', [meta])
                for f in formats:
                    ytstreamlink = f['url']
                link = ytstreamlink
                search = VideosSearch(query, limit=1)
                opp = search.result()["result"]
                oppp = opp[0]
                thumbid = oppp["thumbnails"][0]["url"]
                split = thumbid.split("?")
                thumb = split[0].strip()
            except Exception as e:
                return await msg.edit(f"❌ **Eroare de descărcare YouTuber !** \n\n`{e}`")
                print(e)

        else:
            await msg.edit("🔄 `Start Live Video Stream ...`")
            link = query
            thumb = "https://telegra.ph/file/3e14128ad5c9ec47801bd.jpg"

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
            await group_call.start_video(link, with_audio=True, repeat=False)
            VIDEO_CALL[chat_id] = group_call
            await msg.delete()
            await m.reply_photo(
               photo=thumb, 
               caption=f"▶️ **Start [Video Streaming]({query}) In {m.chat.title} !**",
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

    elif media.video or media.document:
        await msg.edit("🔄 `Downloading ...`")
        if media.video and media.video.thumbs:
            lol = media.video.thumbs[0]
            lel = await client.download_media(lol['file_id'])
            thumb = lel
        else:
            thumb = "https://telegra.ph/file/62e86d8aadde9a8cbf9c2.jpg"

        video = await client.download_media(media)

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
            await group_call.start_video(video, with_audio=True, repeat=False)
            VIDEO_CALL[chat_id] = group_call
            await msg.delete()
            await m.reply_photo(
               photo=thumb,
               caption=f"▶️ **Start [Video Streaming](https://t.me/pixeldeep) In {m.chat.title} !**",
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
            "Doriți să căutați un videoclip YouTube?",
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


@Client.on_message(filters.command(["pause", f"pause@{USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def pause(_, m: Message):
    chat_id = m.chat.id

    if chat_id in AUDIO_CALL:
        await AUDIO_CALL[chat_id].set_audio_pause(True)
        await m.reply_text("⏸ **Streaming audio întrerupt !**")

    elif chat_id in VIDEO_CALL:
        await VIDEO_CALL[chat_id].set_video_pause(True)
        await m.reply_text("⏸ **Streaming video întrerupt !**")

    else:
        await m.reply_text("❌ **Nimic nu rulează !**")


@Client.on_message(filters.command(["resume", f"resume@{USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def resume(_, m: Message):
    chat_id = m.chat.id

    if chat_id in AUDIO_CALL:
        await AUDIO_CALL[chat_id].set_audio_pause(False)
        await m.reply_text("▶️ **Streaming audio reluat !**")

    elif chat_id in VIDEO_CALL:
        await VIDEO_CALL[chat_id].set_video_pause(False)
        await m.reply_text("▶️ **Streaming video reluat !**")

    else:
        await m.reply_text("❌ **Nimic nu rulează !**")


@Client.on_message(filters.command(["endstream", f"endstream@{USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def endstream(client, m: Message):
    msg = await m.reply_text("🔄 `Procesare ...`")
    chat_id = m.chat.id

    if chat_id in AUDIO_CALL:
        await AUDIO_CALL[chat_id].stop()
        AUDIO_CALL.pop(chat_id)
        await msg.edit("⏹️ **S-a oprit difuzarea audio !**")

    elif chat_id in VIDEO_CALL:
        await VIDEO_CALL[chat_id].stop()
        VIDEO_CALL.pop(chat_id)
        await msg.edit("⏹️ **S-a oprit redarea în flux video !**")

    else:
        await msg.edit("🤖 **Vă rugăm să începeți mai întâi un stream !**")


# pytgcalls handlers

@group_call.on_audio_playout_ended
async def audio_ended_handler(_, __):
    await sleep(3)
    await group_call.stop()
    print(f"[INFO] - AUDIO_CALL ENDED !")

@group_call.on_video_playout_ended
async def video_ended_handler(_, __):
    await sleep(0)
    await group_call.stop()
    print(f"[INFO] - VIDEO_CALL ENDED !")
