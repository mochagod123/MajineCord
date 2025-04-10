import aiofiles.os
import discord
from discord.ext import commands, tasks
import os
import re
import pykakasi
import ast
from ult import embed, upload, ytdl_req
import time
import datetime
import aiohttp
from PIL import Image
import json
from discord import Webhook
import random
import asyncio
import base64
import urllib.parse
from bs4 import BeautifulSoup
import sys
import mimetypes
from functools import partial
import requests
import io
import sqlite3
import configparser
import operator
from yt_dlp import YoutubeDL
import aiofiles
import ssl

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ytdl = YoutubeDL(YTDL_OPTIONS)

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

tts = []

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def return_setting(guild: discord.Guild, data: str):
    try:
        config = configparser.ConfigParser()
        config.read('settings/guild_setting.ini', encoding='utf-8')
        return config[str(guild.id)][data]
    except:
        return "False"

def put_value(section, key, value):
    config = configparser.ConfigParser()

    config.read('settings/guild_setting.ini', encoding='utf-8')

    if not config.has_section(section):
        config.add_section(section)

    config.set(section, key, value)

    with open('settings/guild_setting.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def UploadFile(io, filename: str):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://firestorage.jp/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'act': 'flashupjs',
        'type': 'flash10b',
        'photo': '1',
        'talk': '1',
        'json': '1',
        'eid': '',
    }

    uploadfolder = requests.get('https://firestorage.jp/flashup.cgi', params=params, headers=headers)

    uploadid = uploadfolder.json()

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Origin': 'https://firestorage.jp',
        'Referer': 'https://firestorage.jp/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    mime_type, _ = mimetypes.guess_type(filename)

    files = [
            ('folder_id', (None, f'{uploadid["folder_id"]}')),
            ('ppass', (None, '')),
            ('dpass', (None, '')),
            ('thumbnail', (None, 'nomal')),
            ('top', (None, '1')),
            ('jqueryupload', (None, '1')),
            ('max_size', (None, '2147483648')),
            ('max_sized', (None, '2')),
            ('max_size_photo', (None, '15728640')),
            ('max_size_photod', (None, '15')),
            ('max_size_photo', (None, '150')),
            ('max_count', (None, '20')),
            ('max_count_photo', (None, '150')),
            ('jqueryupload', (None, '1')),
            ('eid', (None, '')),
            ('processid', (None, f'{uploadid["folder_id"]}')),
            ('qst', (None, 'n1=Mozilla&n2=Netscape&n3=Win32&n4=Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/131.0.0.0%20Safari/537.36')),
            ('comments', (None, '')),
            ('comment', (None, '')),
            ('arc', (None, '')),
            ('zips', (None, '')),
            ('file_queue', (None, '1')),
            ('pc', (None, '1')),
            ('exp', (None, '7')),
            ('Filename', (f"{filename}", io, mime_type)),
    ]

    response = requests.post('https://server73.firestorage.jp/upload.cgi', headers=headers, files=files)

    decoded_str = urllib.parse.unquote(response.text)

    soup = BeautifulSoup(decoded_str, 'html.parser')

    download_url = soup.find('a', {'id': 'downloadlink'})['href']

    return download_url

whitelist = [1335428061541437531]

cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "CNAME", "TXT", "SOA", "PTR", "SRV"]

cooldown_expand_time = {}
URL_REGEX = re.compile(r"https://discord.com/channels/(\d+)/(\d+)/(\d+)")

cooldown_mention_time = {}

def draw_card():
    return random.choice(cards)

def calculate_score(hand):
    score = sum(hand)
    ace_count = hand.count(11)
    
    while score > 21 and ace_count:
        score -= 10
        ace_count -= 1
    
    return score

async def fetch_ipinfo(ip: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://ip-api.com/json/{ip}?lang=ja') as response:
            jso = json.loads(await response.text())
            if jso["status"] == "success":
                return f"""
> **国**: {jso["country"]}
> **街**: {jso["city"]}
> **タイムゾーン**: {jso["timezone"]}
"""
            else:
                return "Error"

async def fetch_whois(target_domain):
    url = 'https://tech-unlimited.com/proc/whois.php'

    data = {'params': f'target_domain={urllib.parse.quote_plus(target_domain)}'}

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://tech-unlimited.com',
        'priority': 'u=1, i',
        'referer': 'https://tech-unlimited.com/whois.html',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            wh = json.loads(await response.text())
            return io.StringIO(wh["data"])

class SafeCalculator(ast.NodeVisitor):
    def visit_BinOp(self, node):
        # 左右のノードを再帰的に評価
        left = self.visit(node.left)
        right = self.visit(node.right)
        # 演算子を取得して評価
        operator_type = type(node.op)
        if operator_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[operator_type](left, right)
        return "エラー。"

    def visit_Num(self, node):
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit_Expr(node)
        elif isinstance(node, ast.BinOp):
            return self.visit_BinOp(node)
        elif isinstance(node, ast.Constant):  # Python 3.8以降
            return node.value
        elif isinstance(node, ast.Num):  # Python 3.7以前
            return self.visit_Num(node)
        else:
            return "エラー。"

def safe_eval(expr):
    try:
        tree = ast.parse(expr, mode='eval')
        calculator = SafeCalculator()
        return calculator.visit(tree.body)
    except Exception as e:
        return f"Error: {e}"

class Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.cur.execute("""
            CREATE TABLE IF NOT EXISTS score (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER NOT NULL,
                score INTEGER NOT NULL
            )
        """)
        self.bot.cur.execute("""
            CREATE TABLE IF NOT EXISTS dissoku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guildid INTEGER NOT NULL
            )
        """)
        self.bot.cur.execute("""
            CREATE TABLE IF NOT EXISTS dicoall (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guildid INTEGER NOT NULL
            )
        """)
        self.bot.cur.execute("""
            CREATE TABLE IF NOT EXISTS rolepanel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message INTEGER NOT NULL,
                role INTEGER NOT NULL,
                emoji TEXT NOT NULL
            )
        """)
        self.bot.cur.execute("""
            CREATE TABLE IF NOT EXISTS deletelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                messageid INTEGER NOT NULL,
                content TEXT NOT NULL,
                authorid INTEGER NOT NULL,
                author TEXT NOT NULL,
                channelid INTEGER NOT NULL,
                guildid INTEGER NOT NULL
            )
        """)
        self.bot.cur.execute("""
            CREATE TABLE IF NOT EXISTS botperm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER NOT NULL
            )
        """)

    @commands.group()
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def perm(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("""
```
使い方:
*perm add .. 権限者を追加
*perm remove .. 権限者を削除
```
""")
        return
    
    @perm.command(name="add")
    async def perm_add(self, ctx: commands.Context, メンバー: discord.Member):
        if ctx.author.id == 1335428061541437531:
            self.bot.cur.execute("INSERT OR REPLACE INTO botperm (userid) VALUES (?)", (メンバー.id,))
            self.bot.db.commit()
            await ctx.message.add_reaction("✅")

    @perm.command(name="remove")
    async def perm_remove(self, ctx: commands.Context, メンバー: discord.Member):
        if ctx.author.id == 1335428061541437531:
            self.bot.cur.execute("DELETE FROM botperm WHERE userid = ?", (メンバー.id,))
            self.bot.db.commit()
            await ctx.message.add_reaction("✅")

    @commands.command()
    async def reload(self, ctx: commands.Context):
        if ctx.author.id == 1335428061541437531:
            await self.bot.reload_extension(f"cog")
            await self.bot.reload_extension(f"cog2")
            await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def japan(self, ctx: commands.Context, user: discord.User):
        if not ctx.author.id in whitelist:
            await ctx.message.add_reaction("❌")
            return
        if not user.avatar:
            return
        
        io_ = io.BytesIO()
        
        b = await user.avatar.read()

        at = io.BytesIO(b)

        background = Image.open("japan.png")

        overlay = Image.open(at)

        overlay = overlay.resize((130, 110))

        background.paste(overlay, (208, 228))

        background.save(io_, format="png")

        io_.seek(0)

        return await ctx.reply(file=discord.File(io_, "japan.png"))

    async def add_reactions_from_text(self, message, text):
        kakasi = pykakasi.kakasi()
        result = kakasi.convert(text)
        
        error_moji = 0

        def text_to_discord_emoji(text):
            emoji_map = {chr(97 + i): chr(0x1F1E6 + i) for i in range(26)}
            num_emoji_map = {str(i): f"{i}️⃣" for i in range(10)}
            return [emoji_map[char.lower()] if char.isalpha() else num_emoji_map[char] if char.isdigit() else None for char in text if char.isalnum()]
        
        romaji_text = "".join(item["kunrei"] for item in result if "kunrei" in item)
        emojis = text_to_discord_emoji(romaji_text)
        
        for e in emojis:
            if e:
                try:
                    await message.add_reaction(e)
                    await asyncio.sleep(1)
                except Exception as err:
                    error_moji += 1
                    continue
        return error_moji

    @commands.command()
    @commands.cooldown(2, 30, type=commands.BucketType.guild)
    async def emoji_art(self, ctx: commands.Context, message: discord.Message, text: str):
        await self.add_reactions_from_text(message, text)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.cooldown(2, 30, type=commands.BucketType.guild)
    async def textmoji(self, ctx: commands.Context, text: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://emoji-gen.ninja/emoji?align=center&back_color=00000000&color=FF0000FF&font=notosans-mono-bold&locale=ja&public_fg=true&size_fixed=false&stretch=true&text={text}") as resp:
                i = io.BytesIO(await resp.read())
                await ctx.reply(file=discord.File(i, "emoji.png"))

    @commands.command()
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def embed(self, ctx: commands.Context, title: str, desc: str, color: str = "#5440ba", url: str = "https://api.sharkbot.xyz/"):
        embed_ = await embed.Embed(title, desc, color, url).build()

        msg = await ctx.channel.send(embed_)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def get_invite(self, ctx: commands.Context, guild: discord.Guild):
        if not ctx.author.id in whitelist:
            await ctx.message.add_reaction("❌")
            return
        url = await guild.channels[0].create_invite()
        await ctx.reply(f"{url.url}")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def leave_guild(self, ctx: commands.Context, guild: discord.Guild):
        if not ctx.author.id in whitelist:
            await ctx.message.add_reaction("❌")
            return
        await guild.leave()
        await ctx.reply("退出しました。")

    @commands.command()
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def sim(self, ctx: commands.Context, sim_name: str, age: int, gb: int):
        if sim_name == "楽天":
            if age >= 65:
                price_3gb = 880
                price_20gb = 1880
                price_unlimited = 2880
            elif age >= 22:
                price_3gb = 880
                price_20gb = 1880
                price_unlimited = 2880
            elif age >= 12:
                price_3gb = 580
                price_20gb = 1880
                price_unlimited = 2880
            else:
                price_3gb = 980
                price_20gb = 1980
                price_unlimited = 2980

            if gb <= 3:
                price = price_3gb
            elif 3 < gb <= 20:
                price = price_20gb
            else:
                price = price_unlimited

            return await ctx.reply(f"```{gb}GBの値段 (楽天)\n{price}円```")
        else:
            return await ctx.reply("""
```
「楽天」のみ対応しています。
```""")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def upload(self, ctx: commands.Context):
        if not ctx.message.attachments:
            return await ctx.reply("""
```
使い方: *upload
説明: 添付ファイルを添付する必要があります。
```
""")
        ファイル = ctx.message.attachments[0]
        if ファイル.size > 10 * 1024 * 1024:
            return await ctx.reply("容量がでかすぎます！")
        ios = io.BytesIO(await ファイル.read())
        try:
            url = await upload.Upload(ios, ファイル.filename).upload()
            await ctx.reply(url)
        except Exception as e:
            return await ctx.reply(f"{e}")
        
    @commands.command(name="ytdl")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def ytdl_(self, ctx: commands.Context, url: str):
        url_ = await ytdl_req.YTDL(url).build()
        await ctx.reply(content=f"Youtubeダウンロード完了！\n[ダウンロードする]({url_})")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def clear(self, ctx):
        try:
            def check(msg):
                return msg.author.id == 1356943299805446245
            
            deleted = await ctx.channel.purge(limit=80, check=check)
            await ctx.send(f"{len(deleted)}件のメッセージを撤回しました。", delete_after=5)
        except:
            await ctx.send(f"撤回できませんでした。", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def info(self, ctx: commands.Context):
        if ctx.guild.me.guild_permissions.administrator:
            adminfo = "はい"
        else:
            adminfo = "いいえ"
        await ctx.reply(f"""
```
{ctx.guild.name}での情報
この鯖で権限を持っているか: {adminfo}

私の情報
{len(self.bot.guilds)}サーバーに存在中。
{len(self.bot.friends)}人とお友達です。
```
        """)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def server(self, ctx: commands.Context, サーバー: discord.Guild):
        if not サーバー.icon:
            await ctx.reply(f"""
> **ID**: {サーバー.id}
> **名前**: {サーバー.name}
    """)
        else:
            await ctx.reply(f"""
> **ID**: {サーバー.id}
> **名前**: {サーバー.name}
> **アイコン**: [アイコン](<{サーバー.icon.url}>)
    """)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def vote(self, ctx: commands.Context, 質問: str, 回答1: str, 回答2: str):
        payload = {"title": 質問, "description": f"""
🅰️. {回答1}
🅱️. {回答2}
            """, "color": "#5440ba", "url": "https://api.sharkbot.xyz/"}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.sharkbot.xyz/embed/make", json=payload) as resp:
                data = await resp.json()

                embed = data['url']

                msg = await ctx.channel.send(f"[⁠︎]({embed})")
        await msg.add_reaction("🅰️")
        await msg.add_reaction("🅱️")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def iplookup(self, ctx: commands.Context, ip: str):
        await ctx.message.add_reaction("🔄")
        info = await fetch_ipinfo(ip)
        await ctx.reply(info)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def whois(self, ctx: commands.Context, ドメイン: str):
        await ctx.message.add_reaction("🔄")
        info = await fetch_whois(ドメイン)
        await ctx.reply(file=discord.File(info, "whois.txt"))
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def news(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://www3.nhk.or.jp/news/', ssl=ssl_context) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                title = soup.find_all('h1', class_="content--header-title")[0]
                url = title.find_all('a')[0]
                return await ctx.reply(f"https://www3.nhk.or.jp{url["href"]}")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def guilds(self, ctx: commands.Context):
        if not ctx.author.id == 1335428061541437531:
            return
        g = [f"{s.name} - {s.id}" for s in self.bot.guilds]
        await ctx.reply(f"```{"\n".join(g)}```")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def giveaway(self, ctx, duration: int, *, prize: str):
        embed = await embed.Embed("Giveaway!", f"以下の🎉リアクションを押して、\n「{prize}」をゲットしよう！").build()
        giveaway_message = await ctx.channel.send(embed)
        await giveaway_message.add_reaction("🎉")

        await asyncio.sleep(duration)

        giveaway_message = await ctx.channel.fetch_message(giveaway_message.id)
        users = [user async for user in giveaway_message.reactions[0].users() if user != self.bot.user]

        if users:
            winner = random.choice(users)
            await ctx.send(f"🎉 おめでとう！ {winner.mention} が **{prize}** を獲得しました！ 🎉")
        else:
            await ctx.send("😢 参加者がいなかったため、当選者なしです。")

    @commands.group()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def score(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("""
```
使い方:
*score show .. 信頼度スコアの表示
*score set .. 信頼度スコアの設定
```
""")
        return

    @score.command(name="show")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def score_show(self, ctx: commands.Context, member: discord.Member):
        self.bot.cur.execute("SELECT * FROM score where userid = ?;", (member.id,))
        rows = self.bot.cur.fetchone()
        if rows is None:
            return await ctx.reply(f"{member.name}さんの信頼度スコア: 100")
        await ctx.reply(f"{member.name}さんの信頼度スコア: {rows[2]}")

    @score.command(name="set")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def score_set(self, ctx: commands.Context, member: discord.Member, score: int):
        if member.id == 1335428061541437531:
            return
        self.bot.cur.execute("INSERT OR REPLACE INTO score (userid, score) VALUES (?, ?)", (member.id, score))
        self.db.commit()
        await ctx.message.add_reaction("✅")

    @commands.group()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def settings(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("""
```
使い方:
*settings dissoku .. DissokuのUpの通知を設定します。
*settings dicoall .. DicoallのUpの通知を設定します。
*settings rolepanel .. ロールパネルを作成します。
*settings add .. ロールパネルにロールを追加します。
*settings remove .. ロールパネルからロールを削除します。
*settings now .. 現在の設定を取得します。
```
""")
        return

    @settings.command(name="dissoku")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def settings_dissoku(self, ctx: commands.Context, onoff: bool):
        if onoff:
            self.bot.cur.execute("INSERT OR REPLACE INTO dissoku (guildid) VALUES (?)", (ctx.guild.id,))
        else:
            self.bot.cur.execute("DELETE FROM dissoku WHERE guildid = ?", (ctx.guild.id,))
        self.bot.db.commit()
        await ctx.message.add_reaction("✅")

    @settings.command(name="dicoall")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def settings_dicoall(self, ctx: commands.Context, onoff: bool):
        if onoff:
            self.bot.cur.execute("INSERT OR REPLACE INTO dicoall (guildid) VALUES (?)", (ctx.guild.id,))
        else:
            self.bot.cur.execute("DELETE FROM dicoall WHERE guildid = ?", (ctx.guild.id,))
        self.bot.db.commit()
        await ctx.message.add_reaction("✅")

    @settings.command(name="rolepanel")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    @commands.has_permissions(manage_roles=True)
    async def settings_rolepanel(self, ctx: commands.Context, タイトル: str, ロール: discord.Role, 絵文字: str):
        if not ctx.guild.me.guild_permissions.administrator:
            return await ctx.reply("私に管理者権限が必要です。")
        embed = await embed.Embed(タイトル, f"{絵文字}: {ロール.name}").build()
        msg = await ctx.channel.send(embed)
        await msg.add_reaction(絵文字)
        self.bot.cur.execute("INSERT OR REPLACE INTO rolepanel (message, role, emoji) VALUES (?, ?, ?)", (msg.id, ロール.id, 絵文字,))
        self.bot.db.commit()
        await ctx.message.add_reaction("✅")

    @settings.command(name="add")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    @commands.has_permissions(manage_roles=True)
    async def settings_rolepanel_add(self, ctx: commands.Context, メッセージ: discord.Message, ロール: discord.Role, 絵文字: str):
        if not メッセージ.embeds:
            return
        if not ctx.guild.me.guild_permissions.administrator:
            return await ctx.reply("私に管理者権限が必要です。")
        embed = await embed.Embed(メッセージ.embeds[0].title, f"{メッセージ.embeds[0].description}\n{絵文字}: {ロール.name}").build()
        await メッセージ.edit(content=embed)
        await メッセージ.add_reaction(絵文字)
        self.bot.cur.execute("INSERT OR REPLACE INTO rolepanel (message, role, emoji) VALUES (?, ?, ?)", (メッセージ.id, ロール.id, 絵文字,))
        self.bot.db.commit()
        await ctx.message.add_reaction("✅")

    @settings.command(name="remove")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    @commands.has_permissions(manage_roles=True)
    async def settings_rolepanel_remove(self, ctx: commands.Context, メッセージ: discord.Message, ロール: discord.Role, 絵文字: str):
        if not メッセージ.embeds:
            return
        if not ctx.guild.me.guild_permissions.administrator:
            return await ctx.reply("私に管理者権限が必要です。")
        embed = await embed.Embed(メッセージ.embeds[0].title, f"{メッセージ.embeds[0].description}".replace(f"\n{絵文字}: {ロール.name}", "").replace(f"{絵文字}: {ロール.name}\n", "").replace(f"{絵文字}: {ロール.name}", "")).build()
        await メッセージ.edit(content=embed)
        await メッセージ.clear_reaction(絵文字)
        self.bot.cur.execute("DELETE FROM rolepanel WHERE role = ? AND emoji = ?;", (ロール.id,絵文字,))
        self.bot.db.commit()
        await ctx.message.add_reaction("✅")

    @settings.command(name="now")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def settings_now(self, ctx: commands.Context):
        self.bot.cur.execute("SELECT * FROM dissoku where guildid = ?;", (ctx.guild.id,))
        rows = self.bot.cur.fetchone()
        if rows is None:
            dissoku_alert = "無効"
        else:
            dissoku_alert = "有効"
        self.bot.cur.execute("SELECT * FROM dicoall where guildid = ?;", (ctx.guild.id,))
        rows = self.bot.cur.fetchone()
        if rows is None:
            dicoall_alert = "無効"
        else:
            dicoall_alert = "有効"
        await ctx.reply(f"ディス速Up通知: `{dissoku_alert}`\nDicoallのUp通知: `{dicoall_alert}`")

    @settings.command(name="reset")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def settings_reset(self, ctx: commands.Context):
        self.bot.cur.execute("DELETE FROM dissoku where guildid = ?;", (ctx.guild.id,))
        self.bot.cur.execute("DELETE FROM dicoall where guildid = ?;", (ctx.guild.id,))
        self.bot.db.commit()
        await ctx.reply("このサーバーの設定をリセットしました。\nロールパネルなどはリセットされません。")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def blackjack(self, ctx: commands.Context):
        if not ctx.guild.me.guild_permissions.administrator:
            return await ctx.reply("私の権限がありません！\n管理者権限をつけてください！")
        player_hand = [draw_card(), draw_card()]
        dealer_hand = [draw_card(), draw_card()]
        
        message = await ctx.send(f"あなたの手札: {player_hand}, 合計: {calculate_score(player_hand)}\nディーラーの手札: [{dealer_hand[0]}, ?]\n✅: ヒット\n⏹: スタンド")
        await asyncio.sleep(1)
        logmsg = await ctx.send("----------------------------------\nログ")
        
        await message.add_reaction("✅")
        await message.add_reaction("⏹")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "⏹"]
        
        while calculate_score(player_hand) < 21:
            reaction, user = await self.bot.wait_for("reaction_add", check=check)

            await message.remove_reaction(reaction.emoji, user)
            
            if str(reaction.emoji) == "✅":
                player_hand.append(draw_card())
                await message.edit(content=f"あなたの手札: {player_hand}, 合計: {calculate_score(player_hand)}\nディーラーの手札: [{dealer_hand[0]}, ?]\n✅: ヒット\n⏹: スタンド")
            else:
                break
        
        player_score = calculate_score(player_hand)
        if player_score > 21:
            await message.edit("バースト！あなたの負けです。")
            await message.clear_reactions()
            return
        
        await logmsg.edit(logmsg.content + f"\nディーラーの手札: {dealer_hand}, 合計: {calculate_score(dealer_hand)}")
        await asyncio.sleep(2)
        
        while calculate_score(dealer_hand) < 17:
            dealer_hand.append(draw_card())
            await logmsg.edit(logmsg.content + f"\nディーラーの手札: {dealer_hand}, 合計: {calculate_score(dealer_hand)}")
            await asyncio.sleep(2)
        
        dealer_score = calculate_score(dealer_hand)
        
        if dealer_score > 21 or player_score > dealer_score:
            await message.edit("あなたの勝ちです！")
        elif player_score < dealer_score:
            await message.edit("ディーラーの勝ちです。")
        else:
            await message.edit("引き分けです。")
        await message.clear_reactions()

    @commands.group()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def music(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("""
```
使い方:
*music join .. VCに参加します。
*music leave .. VCから退出します。
*music play .. 音楽を再生します。
```
""")
        return

    @music.command(name="join")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def music_join(self, ctx: commands.Context):
        try:
            await ctx.author.voice.channel.connect()
            await ctx.message.add_reaction("✅")
        except:
            return

    @music.command(name="leave")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def music_leave(self, ctx: commands.Context):
        try:
            await ctx.guild.voice_client.disconnect()
            await ctx.message.add_reaction("✅")
        except:
            return

    async def get_music_info(self, url):
        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, partial(ytdl.extract_info, url, download=False, process=False))
            info["url"] = url
            info["time"] = time.time() + 60 * 60 * 24 * 7
            return info
        except:
            return

    @music.command(name="play")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def music_play(self, ctx: commands.Context, url: str):
        try:
            info = await self.get_music_info(url)
            ru = ""
            for f in info['formats']:
                    try:
                        if f["ext"] == "mp4":
                            ru = f["url"]
                            break
                    except:
                        continue
            ctx.guild.voice_client.play(discord.FFmpegOpusAudio(ru, bitrate=64, stderr=sys.stdout))
            await ctx.message.add_reaction("✅")
        except:
            return

    @commands.command(name="ping")
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f"""```
Status:
 - Ping: {round(self.bot.latency * 1000)}ms
```""")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def help(self, ctx: commands.Context):
        await ctx.reply("""
```
User: help, info, settings
File: upload, music, deletelog
Status: ping. info, status
Fun: blackjack, giveaway, ishiba, textmoji
Search: iplookup, sim, news, tweet, t0kenlookup
Tool: score, vote, embed, emoji_art, clear, webhook, webshot

Prefix: '*'
```
""")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def tweet(self, ctx: commands.Context, word: str):
        url = f"https://search.yahoo.co.jp/realtime/api/v1/pagination?p={word}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    
                    if not data.get("timeline", {}).get("entry"):
                        return await ctx.reply("取得に失敗しました。")
                    entries = data["timeline"]["entry"][0]
                    await ctx.reply(f"""
**{entries["name"]}(@{entries["screenName"]})**
{datetime.datetime.fromtimestamp(entries["createdAt"]).strftime("%Y-%m-%d %H:%M:%S")}
{entries["url"]}
""")
            except:
                return

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def deletelog(self, ctx: commands.Context, member: discord.Member = None):
        if member:
            self.bot.cur.execute("SELECT * FROM deletelog where authorid = ? AND channelid = ?;", (member.id, ctx.channel.id))
            logs = self.bot.cur.fetchall()
            io_ = io.StringIO("\n".join([f"{l[2].replace("\n", "\\n")}" for l in logs]))
            await ctx.reply(file=discord.File(io_, "log.txt"), content=f"「{member.name}」の削除・編集ログ\n編集の場合: 編集前の値 -> 編集後の値\n削除の場合: 削除前の値")
        else:
            self.bot.cur.execute("SELECT * FROM deletelog where channelid = ?;", (ctx.channel.id,))
            logs = self.bot.cur.fetchall()
            io_ = io.StringIO("\n".join([f"{l[4]} ({l[3]})/ {l[2].replace("\n", "\\n")}" for l in logs]))
            await ctx.reply(file=discord.File(io_, "log.txt"), content=f"このチャンネルの削除・編集ログ\n編集の場合: 編集前の値 -> 編集後の値\n削除の場合: 削除前の値")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def clearlog(self, ctx: commands.Context):
        if not ctx.author.id == 1335428061541437531:
            return
        self.bot.cur.execute("DELETE FROM deletelog")
        self.bot.db.commit()
        await ctx.reply("削除ログをクリアしました。")

    @commands.Cog.listener("on_message_delete")
    async def on_message_delete_log(self, message: discord.Message):
        if message.author.id == 1356943299805446245:
            return
        if not message.content:
            return
        if message.author.bot:
            return
        try:
            self.bot.cur.execute("INSERT OR REPLACE INTO deletelog (messageid, content, authorid, author, channelid, guildid) VALUES (?, ?, ?, ?, ?, ?)", (message.id, message.content, message.author.id, message.author.name, message.channel.id, message.guild.id,))
            self.bot.db.commit()
        except:
            return
        
    @commands.Cog.listener("on_message_edit")
    async def on_message_edit_log(self, before: discord.Message, after: discord.Message):
        if after.author.id == 1356943299805446245:
            return
        if after.author.bot:
            return
        if not after.content:
            return
        try:
            self.bot.cur.execute("INSERT OR REPLACE INTO deletelog (messageid, content, authorid, author, channelid, guildid) VALUES (?, ?, ?, ?, ?, ?)", (after.id, f"{before.content} -> {after.content}", after.author.id, after.author.name, after.channel.id, after.guild.id,))
            self.bot.db.commit()
        except:
            return

    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove_rolepanel(self, payload: discord.RawReactionActionEvent):
        try:
            msg = payload.message_id
            self.bot.cur.execute("SELECT * FROM rolepanel where message = ? AND emoji = ?;", (msg, str(payload.emoji)))
            rows = self.bot.cur.fetchone()
            if rows is None:
                return
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            role = guild.get_role(rows[2])
            if not role:
                return
            member = guild.get_member(payload.user_id)
            if member:
                await member.remove_roles(role, reason="リアクションによるロール削除")
            else:
                return
        except:
            return

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add_rolepanel(self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:
            return
        if payload.member.id == 1350790737662574674:
            return
        try:
            msg = payload.message_id
            self.bot.cur.execute("SELECT * FROM rolepanel where message = ? AND emoji = ?;", (msg, str(payload.emoji)))
            rows = self.bot.cur.fetchone()
            if rows is None:
                return
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            role = guild.get_role(rows[2])
            if not role:
                return
            member = guild.get_member(payload.user_id)
            if member:
                await member.add_roles(role, reason="リアクションによるロール付与")
            else:
                return
        except:
            return

    @commands.Cog.listener("on_message_edit")
    async def on_message_edit_dissoku(self, before: discord.Message, after: discord.Message):
        if after.author.id == 761562078095867916:
            try:
                if "をアップしたよ!" in after.embeds[0].fields[0].name:
                    self.bot.cur.execute("SELECT * FROM dissoku where guildid = ?;", (after.guild.id,))
                    rows = self.bot.cur.fetchone()
                    if rows is None:
                        return
                    await after.reply("Upを検知しました。\n1時間後に通知します。")
                    await asyncio.sleep(3600)
                    await after.channel.send("ディス速をアップしてね！\n</dissoku up:828002256690610256> でアップ。")
                elif "失敗しました" in after.embeds[0].fields[0].name:
                    self.bot.cur.execute("SELECT * FROM dissoku where guildid = ?;", (after.guild.id,))
                    rows = self.bot.cur.fetchone()
                    if rows is None:
                        return
                    await after.add_reaction("❌")
            except:
                return    

    @commands.Cog.listener("on_message")
    async def on_message_up_dicoall(self, message: discord.Message):
        if message.author.id == 903541413298450462:
            try:
                if "残りました。" in message.content:
                    self.bot.cur.execute("SELECT * FROM dicoall where guildid = ?;", (message.guild.id,))
                    rows = self.bot.cur.fetchone()
                    if rows is None:
                        return
                    await message.add_reaction("❌")
            except:
                return
            try:
                if "サーバーは上部に表示されます。" in message.embeds[0].description:
                    self.bot.cur.execute("SELECT * FROM dicoall where guildid = ?;", (message.guild.id,))
                    rows = self.bot.cur.fetchone()
                    if rows is None:
                        return
                    await message.reply("Upを検知しました。\n一時間後に通知します。")
                    await asyncio.sleep(3600)
                    await message.channel.send("DicoallをUpしてね！\n</up:935190259111706754> でアップ。")
            except:
                return

    @commands.Cog.listener("on_message")
    async def on_message_expand(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.content:
            return
        if type(message.channel) == discord.DMChannel:
            return
        urls = URL_REGEX.findall(message.content)
        if not urls:
            return

        current_time = time.time()
        last_message_time = cooldown_expand_time.get(message.guild.id, 0)
        if current_time - last_message_time < 5:
            return
        cooldown_expand_time[message.guild.id] = current_time

        for guild_id, channel_id, message_id in urls:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue

            channel = guild.get_channel(int(channel_id))
            if not channel or not isinstance(channel, discord.TextChannel):
                continue

            try:
                msg = await channel.fetch_message(int(message_id))
                payload = {"title": f"{msg.author.name}/{msg.guild.name}", "description": f"{msg.content}", "color": "#187007", "url": f"{msg.jump_url}"}

                async with aiohttp.ClientSession() as session:
                    async with session.post("https://api.sharkbot.xyz/embed/make", json=payload) as resp:
                        data = await resp.json()

                embed = data['url']

                msg = await message.channel.send(f"[⁠︎]({embed})")
            except:
                return
            return

    @commands.Cog.listener("on_message")
    async def on_message_mention(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.content.startswith(self.bot.user.mention):
            return
        current_time = time.time()
        last_message_time = cooldown_mention_time.get(message.guild.id, 0)
        if current_time - last_message_time < 5:
            return
        cooldown_mention_time[message.guild.id] = current_time
        print(message.content.split(self.bot.user.mention)[1])
        if message.content.split(self.bot.user.mention)[1].replace(" ", "") == "ピング":
            return await message.reply("ぽんぐ！")
        
    @commands.Cog.listener("on_message")
    async def on_message_cmd(self, message: discord.Message):
        if message.author.bot:
            return
        if message.author.id == 1335428061541437531:
            return await self.bot.process_commands(message)
        self.bot.cur.execute("SELECT * FROM botperm where userid = ?;", (message.author.id,))
        rows = self.bot.cur.fetchone()
        if rows is None:
            return
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, commands.CommandOnCooldown):
            e = 0
            return e
        elif isinstance(err, commands.CommandNotFound):
            e = 0
            return e
        elif isinstance(err, commands.MissingPermissions):
            e = 0
            return e
        else:
            await ctx.message.add_reaction("❌")
            try:
                await self.bot.get_channel(1350794203537473567).send(f"Guild: {ctx.guild.name}/{ctx.guild.id}\nUser: {ctx.author.name}/{ctx.author.id}\n{err}")
            except:
                return

async def setup(bot):
    await bot.add_cog(Cog(bot))