# region: setup
import discord
import os
from dotenv import load_dotenv
load_dotenv()
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="&")
import random
import asyncio

birdfacts = ["Lucy's warbler is the smallest known species of warbler!", "my pfp came from <https://www.drawingtenthousandbirds.com/new-blog-1/2015/4/18/why-a-yellow-warbler>", "There are 119 species of warbler"]

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

bot.remove_command("help")

@bot.event
async def on_ready():
  print(f'> Logged in as: {bot.user}')
  print(bot.user.id)
  print('-----READY----- \n')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The chat! do &help to learn more about my functions"))

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
  mention = f'<@!{bot.user.id}>'
  if mention in message.content:
    users = []
    role = discord.utils.get(message.guild.roles,name="Helper")
    for member in message.guild.members:
      memberis = member.id
      if role in member.roles: # does member have the specified role?
        print(memberis)
        if member.status == discord.Status.online:
          print(memberis)
          users.append(memberis)
    await message.channel.send("⚠️ " + message.author.mention + " Mentioned me!")
    print([f"<@!{i}>" for i in users])
    await message.channel.send([f"<@!{i}>" for i in users])
  await bot.process_commands(message)

@bot.command()
async def checkpoints(ctx, user):
  async with ctx.typing():
    # do expensive stuff here
    await asyncio.sleep(1)
  await ctx.channel.send("**Hey! 👋** Give me a sec while I look that up for you!")

@bot.command()
async def help(ctx):
  async with ctx.typing():
    # do expensive stuff here
    await asyncio.sleep(1)
  await ctx.channel.send("**Hey! 👋** \nmy job is mostly to help keep the chat clean, and give our wonderful helpers a hand, but there is some useful stuff you should know!\n**Ping Me** if something needs immediate (like right right right now) attention\n**DM me** to contact the mods if something needs private attention\n\n**Oh!** One last thing. here is a random bird fact!\n> " + random.choice(birdfacts))

@bot.command()
@commands.has_role("Helper")
async def point(ctx, ammount, user, *, reason):
	await ctx.channel.send("eventually this will grant a point")

bot.run(DISCORD_TOKEN)