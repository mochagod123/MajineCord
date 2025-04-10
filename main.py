import discord
import sqlite3
from discord.ext import commands

class Dainippon(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="*",
            help_command=None,
        )
        self.igaku_user = [1335428061541437531]
        self.db = sqlite3.connect("save.db")
        self.cur = self.db.cursor()
        print("InitDone")

bot = Dainippon()

@bot.event
async def setup_hook():
    await bot.load_extension("cog")
    await bot.load_extension("cog2")

@bot.event
async def on_message(message: discord.Message):
    return

bot.run("T0ken")