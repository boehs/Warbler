# region: setup
# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
# IMPORT THE OS MODULE.
import os
# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.
from discord.ext import commands
# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# CREATES A NEW BOT OBJECT WITH A SPECIFIED PREFIX. IT CAN BE WHATEVER YOU WANT IT TO BE.
bot = commands.Bot(command_prefix="&")

wordblacklist = open("config/blacklist.txt","r")
wordblacklist = wordblacklist.readlines()
wordblacklist = [x.replace('\n', '') for x in wordblacklist]
print(str(wordblacklist))

wordgraylist = open("config/graylist.txt","r")
wordgraylist = wordgraylist.readlines()
wordgraylist = [x.replace('\n', '') for x in wordgraylist]
print(str(wordgraylist))

async def tiers(offender, tier, reason):
  if tier == 1:
  # Warn offender
    return
  elif tier == 2:
  # Final warn offender
    return
  elif tier == 3:
  # Remove member role from offender (read the rules)
    return
  elif tier == 4:
  # Mute offender for 5 minutes
    return
  elif tier == 5:
  # Mute offender for 10 minutes
    return
  elif tier == 6:
  # Mute offender for 30 minutes
    return
  elif tier == 7:
  # Mute offender for 1 hour
    return
  elif tier == 8:
  # Mute offender for 12 hours
    return
  elif tier == 9:
  # mute offender for 24 hours
    return
  elif tier == 10:
  # Ban offender for 3 days
    return
  elif tier == 11:
  # Ban offender for 5 days
    return
  elif tier == 12:
  # Ban offender for 7 days
    return
  elif tier == 13:
  # Ban offender for 14 days
    return
  elif tier == 13:
  # Ban offender for 14 days
    return
  elif tier == 14:
  # Ban offender for 30 days
    return
  elif tier == 15:
  # Permaban
    return

@bot.event
async def on_ready():
  print(f'> Logged in as: {bot.user}')
  print(bot.user.id)
  print('-----READY----- \n')

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  for word in wordblacklist:
    if word in message.content:
      await message.delete()
      # give user a point
  for word in wordgraylist:
    if word in message.content:
      await message.delete()

@bot.command()
async def checkpoints(ctx, user):
	await ctx.channel.send("eventually this will check points")

@bot.command()
@commands.check(ban_members=True)
async def point(ctx, ammount, user, *, reason):
	await ctx.channel.send("eventually this will grant a point")

bot.run(DISCORD_TOKEN)