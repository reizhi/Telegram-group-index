# -*- coding: utf-8 -*-
import asyncio
from threading import Timer
from pyrogram import Client
from pyrogram.enums import MessageMediaType
from pyrogram.client import Cache
from pyrogram import filters
import uvloop
import pymysql
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

api_id = 114514111
api_hash = "qwe123zxc000000000000"
admin = 233333333333

db_host = "127.0.0.1"
db_user = "root"
db_pwd = "mydbpwd00000"

app = Client("tgindex", api_id=api_id, api_hash=api_hash, max_concurrent_transmissions = 2)
app.message_cache = Cache(1000000)
m_types = [MessageMediaType.PHOTO, MessageMediaType.VIDEO, MessageMediaType.AUDIO, MessageMediaType.DOCUMENT]

database = {-10018000000001:"tgindexdb1", -100180000000002: "tgindexdb2"}

def wdb(dbname, msgid, msg_text):
    conn = pymysql.connect(host = db_host, db_user = "root", password = db_pwd, database = database[dbname])
    cursor = conn.cursor()
    sql = 'INSERT INTO msglist (id, content) VALUES ("%s", "%s")'
    cursor.execute(sql, (msgid, msg_text))
    conn.commit()
    cursor.close()
    conn.close()

def wconf(dbname, conf, value):
    conn = pymysql.connect(host = db_host, db_user = "root", password = db_pwd, database = database[dbname])
    cursor = conn.cursor()
    sql = 'INSERT INTO config (config, value) VALUES (%s, %s)'
    cursor.execute(sql, (conf, value))
    conn.commit()
    cursor.close()
    conn.close()

def rconf(dbname, conf):
    conn = pymysql.connect(host = db_host, db_user = "root", password = db_pwd, database = database[dbname])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM config WHERE config = %s ORDER BY id DESC LIMIT 1", (conf))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    if (len(result) == 0):
        return False
    else:
        return result[0][2]

def sdb(dbname, keyw):
    conn = pymysql.connect(host = db_host, db_user = "root", password = db_pwd, database = database[dbname])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM msglist WHERE content LIKE %s ORDER BY id ASC limit 8", ("%" + str(keyw) + "%",))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

async def updatedb(dbname, msglist):
    for mit in msglist:
        msg = await app.get_messages(chat_id = dbname, message_ids = mit)
        if (msg.media and msg.media in m_types):
            content = ""
            if (msg.caption):
                try:
                    content = msg.caption[:18]
                except:
                    print("切割失败")
                finally:
                    content = msg.caption
            if (msg.media == MessageMediaType.VIDEO and msg.video.file_name):
                content = msg.video.file_name + " " + content
            elif (msg.media == MessageMediaType.AUDIO and msg.audio.file_name):
                content = msg.audio.file_name + " " + content
            elif (msg.media == MessageMediaType.DOCUMENT and msg.document.file_name):
                content = msg.document.file_name + " " + content
            if (content == ""):
                continue
            wdb(dbname, msg.id, content)
            await asyncio.sleep(0.05)

@app.on_message(filters.command("search") & filters.group)
async def search(client, message):
    if (message.chat.id in database):
        keyw = message.text.replace("/search ", "", 1)
        result = sdb(message.chat.id, keyw)
        await message.reply_text("以下为搜索结果：", quote=True)
        for i in result:
            await app.send_message(message.chat.id, str(i[1]), reply_to_message_id = i[0])


@app.on_message(filters.command("initdb") & filters.group)
async def start_cmd(client, message):
    if (message.from_user.id and message.from_user.id == admin and message.chat.id in database):
        await message.reply_text("开始创建索引", quote=True)
        last_msgid = await app.get_chat_history(message.chat.id, limit = 1).__anext__()
        msglist = [i for i in range(1, last_msgid.id)]
        await updatedb(message.chat.id ,msglist)
        await message.reply_text("索引完成", quote=True)
        wconf(message.chat.id, "progress", last_msgid.id)

@app.on_message(filters.command("updatedb") & filters.group)
async def start_cmd(client, message):
    if (message.from_user.id and message.from_user.id == admin and message.chat.id in database):
        await message.reply_text("开始更新索引", quote=True)
        first_msgid = int(rconf(message.chat.id, "progress")) + 1
        last_msgid = await app.get_chat_history(message.chat.id, limit = 1).__anext__()
        msglist = [i for i in range(first_msgid, last_msgid.id)]
        await updatedb(message.chat.id ,msglist)
        await message.reply_text("索引完成", quote=True)
        wconf(message.chat.id, "progress", last_msgid.id)

app.run()