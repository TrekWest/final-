import discord
from discord import ui
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import time
import random
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
GUILD_ID = discord.Object(id=1389514810865225879)
pair = {'(':')', '{':'}', '[':']'}
@bot.event
async def on_ready():
    if not hasattr(bot, "synced"):
        await bot.tree.sync()
        bot.synced = True
        print("Logged in as {}".format(bot.user.name))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    stack = []
    for i in message.content:
        if i in pair.keys():
            stack.append(i)
        elif i in pair.values():
            length = len(stack)
            if length == 0:
                await message.reply("Bryan is a dog")
                return
            elif pair[stack[length-1]] != i:
                await message.reply('Bryan is a dog')
                return
            elif pair[stack[length-1]] == i:
                stack.pop()
     if len(stack) != 0:
        await message.reply('Bryan is a dog')
        return
    await bot.process_commands(message)

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)