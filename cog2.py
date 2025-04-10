import aiofiles.os
import psutil
import discord
import json
import re
from discord.ext import commands, tasks
import base64
import unicodedata
import jaconv
import re
import subprocess
from alphabet2kana import a2k
from pydub import AudioSegment
import os
import io
import aiofiles
from discord import Webhook
import asyncio
from bs4 import BeautifulSoup
from pykakasi import kakasi
import aiohttp

class Cog2(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def file_remove(self, filename: str):
        await aiofiles.os.remove(filename)

    @commands.command(name="ishiba")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def isiba_voice(self, ctx: commands.Context, text: str):
        m = await ctx.reply("""
```
=====================
IShibaVoice v1.1 Free
=====================
生成中。。
```
""")
        await asyncio.sleep(1)

        def remove_diacritics(text):
            normalized_text = unicodedata.normalize('NFD', text)
            result = ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn')
            return result
        
        text_ = a2k(text[:30])
        kakasi_ = kakasi()
        kakasi_.setMode('J', 'H') 

        conv = kakasi_.getConverter()
        text_ = conv.do(text_)

        text_ = remove_diacritics(text_)

        text_ = jaconv.kata2hira(text_)

        await m.edit(content=f"""
```
=====================
IShibaVoice v1.1 Free
=====================
生成中。。
言葉: {text_}
```
""")

        await asyncio.sleep(1)

        aud = []
        for a in text_:
            file_path = f"Ishiba/{a}.mp3"
            if await aiofiles.os.path.isfile(file_path):
                try:
                    aud.append(AudioSegment.from_file(file_path, format="mp3"))
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

        if aud:
            cmb = aud[0] + 10
            for aa in aud[1:]:
                a_ = aa + 10
                cmb = cmb + a_
            cmb.export(f"out/ishiba_{ctx.author.id}.mp3", format="mp3")
            await m.edit(content=f"""
```
=====================
IShibaVoice v1.1 Free
=====================
生成中。。
言葉: {text_}
生成完了！
```
""")
            await m.add_files(discord.File(f"out/ishiba_{ctx.author.id}.mp3"))
            await self.file_remove(f"out/ishiba_{ctx.author.id}.mp3")
        else:
            return await ctx.reply("エラーが発生しました。")

    @commands.group(name="webhook")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def webhook(self, ctx: commands.Context):
        if ctx.invoked_subcommand:
            return
        await ctx.reply("""
```使い方
*webhook send .. WebHookに送信
*webhook delete .. WebHookを権限なしでも削除
*webhook edit .. WebHookを権限なしでも編集
```
""")

        return
    
    @webhook.group(name="send")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def webhook_send(self, ctx: commands.Context, url: str, *, message: str):
        async with aiohttp.ClientSession() as session:
            wh = Webhook.from_url(url, session=session)
            await wh.send(content=message)
            await ctx.message.add_reaction("✅")

    @webhook.group(name="delete")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def webhook_delete(self, ctx: commands.Context, url: str):
        async with aiohttp.ClientSession() as session:
            wh = Webhook.from_url(url, session=session)
            await wh.delete(prefer_auth=False)
            await ctx.message.add_reaction("✅")

    @webhook.group(name="edit")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def webhook_edit(self, ctx: commands.Context, url: str, username: str):
        async with aiohttp.ClientSession() as session:
            wh = Webhook.from_url(url, session=session)
            await wh.edit(prefer_auth=False, name=username)
            await ctx.message.add_reaction("✅")

    def is_valid_url(self, url):
        url_regex = re.compile(
            r'^(https?|ftp)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(url_regex, url) is not None

    @commands.command(name="webshot")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def webshot(self, ctx: commands.Context, url: str):
        if self.is_valid_url(url):
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            body = f"url={url}&waitTime=1&browserWidth=1000&browserHeight=1000"
            async with aiohttp.ClientSession() as session:
                async with session.post("https://securl.nu/jx/get_page_jx.php", headers=headers, data=body) as response:
                    text = await response.text()
                    js = json.loads(text)
                    payload={
                        "color": "#5440ba",
                        "description": f"{url}",
                        "image": f"https://securl.nu{js["img"]}",
                        "redirect_enabled": False,
                        "redirect_url": "",
                        "thumbImage": False,
                        "title": "Webショット",
                        "video": ""
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.post("https://nemtudo.me/api/tools/embeds", json=payload) as resp:
                            data = await resp.json()

                    embed = data['data']['id']

                    embed = f"[⁠︎](https://nemtudo.me/e/{embed})"
                    await ctx.reply(embed)
        else:
            return await ctx.message.add_reaction("❌")

    async def get_system_status(self):
        loop = asyncio.get_running_loop()
        
        cpu_usage = await loop.run_in_executor(None, psutil.cpu_percent, 1)
        memory = await loop.run_in_executor(None, psutil.virtual_memory)
        disk = await loop.run_in_executor(None, psutil.disk_usage, "/")
        
        return cpu_usage, memory, disk

    @commands.command(name="status")
    @commands.cooldown(2, 10, commands.BucketType.guild)
    async def status_bot(self, ctx: commands.Context):
        cpu_usage, memory, disk = await self.get_system_status()
        await ctx.reply(f"```CPU: {cpu_usage}%\nMemory: {memory.percent}% ({memory.used // (1024**2)}MB / {memory.total // (1024**2)}MB)\nDisk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)```")

    @commands.group(name="t0kenlookup")
    @commands.cooldown(2, 10, type=commands.BucketType.guild)
    async def t0kenlookup(self, ctx: commands.Context):
        if ctx.invoked_subcommand:
            return
        await ctx.reply("""
```使い方
*t0kenlookup userid .. ユーザーIDから前半を特定します。
```
""")

        return

    @t0kenlookup.command(name="userid")
    async def t0kenlookup_userid(self, ctx: commands.Context, userid: discord.User):
        await ctx.reply(f"{userid.name}さんのt0kenの前半: {base64.b64encode(str(userid.id).encode()).decode().rstrip("=")}")

    @commands.command(name="nmap")
    @commands.cooldown(2, 10, commands.BucketType.guild)
    async def nmap(self, ctx: commands.Context, ip: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.voids.top/nmap/{ip}") as response:
                js = await response.json()
                ports = js["ports"]
                ps = []
                for port, details in ports.items():
                    port_number = port
                    port_type = details["type"]
                    ps.append(f"{port_number} - {port_type}")
                if ps == []:
                    return await ctx.reply("開いているポートはありません。")
                return await ctx.reply(f"```{"\n".join(ps)}```")
            
async def setup(bot):
    await bot.add_cog(Cog2(bot))