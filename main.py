# region: setup
import asyncio
import codecs
import csv
import os
import random

import discord
import mysql.connector
from discord.ext import commands
from discord.ext.commands import CheckFailure, has_permissions
from discord_slash import SlashCommand, SlashContext
from dotenv import load_dotenv
import pymysql.cursors

import config

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="&")
slash = SlashCommand(bot, sync_commands=True)

birdfacts = ["Lucy's warbler is the smallest known species of warbler!", "my pfp came from <https://www.drawingtenthousandbirds.com/new-blog-1/2015/4/18/why-a-yellow-warbler>", "There are 119 species of warbler"]

wordblacklist = open("config/blacklist.txt","r")
wordblacklist = wordblacklist.readlines()
wordblacklist = [x.replace('\n', '') for x in wordblacklist]
wordblacklist = [codecs.encode(x, 'rot_13') for x in wordblacklist]
print("Loaded " + str(len(wordblacklist)) + " words from the blacklistlist")

wordgraylist = open("config/graylist.txt","r")
wordgraylist = wordgraylist.readlines()
wordgraylist = [x.replace('\n', '') for x in wordgraylist]
wordgraylist = [codecs.encode(x, 'rot_13') for x in wordgraylist]
print("Loaded " + str(len(wordgraylist)) + " words from the graylist")

bot.remove_command("help")
try:
  connection = pymysql.connect(host='localhost',user='root',password='',database='warbler',cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.InternalError:
  print("Error: You must have a my sql instence running and a database called 'warbler'")
else:
  print("Connected to SQL")


createtable = """
CREATE TABLE IF NOT EXISTS punish (
	userId BIGINT UNSIGNED NOT NULL COMMENT 'The snowflake id of a punished user',
	punishTier TINYINT UNSIGNED NOT NULL COMMENT 'The tier a given user is on (does not necessarily represent if the user is currently serving a punishment, as it may decrease (every two weeks!) before a users punishment is over), serves as a baseline for future punishments)',
	punishTime BIGINT UNSIGNED NULL COMMENT 'The time a user received the punishment they are currently serving, may be empty if user has points but their punishment has ended',
	punishLength INT UNSIGNED NULL COMMENT 'The length of a punishment a user is serving, may be empty if user has points but their punishment has ended',
	punishType TINYTEXT NULL COMMENT 'm, or b = mute or ban so that when it comes time to revoke a punishment the bot knows what to remove, may be empty if user has points but their punishment has ended',

  PRIMARY KEY (userId)
);
"""

with connection:
    with connection.cursor() as cursor:
        cursor.execute(createtable)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

# endregion

print("beginning login")

@bot.event
async def on_ready():
  print(f'> Logged in as: {bot.user}')
  print(bot.user.id)
  print('-----READY----- \n')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The chat! do /help to learn more about my functions"))

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
  # not working yet, will ping all online mods
  if mention in message.content:
    users = []
    role = discord.utils.get(message.guild.roles,name="Helper")
    for member in message.guild.members:
      memberis = member.id
      if role in member.roles: # does member have the specified role?
        if member.status == discord.Status.online:
          users.append(memberis)
    await message.channel.send("⚠️ " + message.author.mention + " Mentioned me!")
    print([f"<@!{i}>" for i in users])
    await message.channel.send([f"<@!{i}>" for i in users])
  await bot.process_commands(message)

@slash.slash(name="checkpoints",guild_ids=config.guild_ids,description="check the points of any user ever!")
async def checkpoints(ctx, user: discord.Member):
  await ctx.channel.send("**Hey! 👋** Give me a sec while I look that up for you!")
  success = False
  async with ctx.channel.typing():
    await asyncio.sleep(1)
  with open('database/punish.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            pass
        else:
            if row[0] == str(user.id):
                success = True
                await ctx.channel.send("**Ok!** we found the user! at time of checking, they have **" + row[1] + "** points")
        line_count = line_count + 1
  if success == True:
    pass
  else:
    await ctx.channel.send("**Awesome**, " + user.mention + " Currently has **no points**. thanks for being a great person!")

@slash.slash(name="help",guild_ids=config.guild_ids,description="you should know this already - but maybe you just want bird facts")
async def help(ctx):
  await ctx.channel.send("**Hey! 👋** \nmy job is mostly to help keep the chat clean, and give our wonderful helpers a hand, but there is some useful stuff you should know!\n**Ping Me** if something needs immediate (like right right right now) attention\n**DM me** to contact the mods if something needs private attention\n\n**Oh!** One last thing. here is a random bird fact!\n> " + random.choice(birdfacts))

@slash.slash(name="point",guild_ids=config.guild_ids, description="Gives users points for being bad children")
@commands.has_role("Helper")
async def point(ctx, amount, user: discord.Member, *, reason):
  author = ctx.author
  success = False
  with open('database/punish.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            pass
        else:
            if row[0] == str(user.id):
                success = True
                mathishard = int(row[1]) + int(amount)
                await ctx.channel.send("We already have the user. they have **" + row[1] + "** points. after this, they will have **" + str(mathishard) + "** points. **are you sure?** (**y** or **n**)")
                break
        line_count = line_count + 1
    if not success:
      await ctx.channel.send("This will give the user **" + str(amount) + "** points. **are you sure?** (**y** or **n**)")
  def check(message):
      return message.author == author and message.content.startswith("y") or message.content.startswith("n")
  try:
    message = await bot.wait_for('message', timeout=60.0, check=check)
    if message.content.startswith("y"):
      await ctx.channel.send("**Got it!** giving " + user.mention + " the treatment they deserve!")
      if success:
        pass
      elif not success:
        query = "INSERT INTO punish ( userId, punishTier ) VALUES ( %s, %s )"
        val = [(int(user.id), int(amount))]
        executemany_query(connection,query,val)
    elif message.content.startswith("n"):
      await ctx.channel.send("**Aborted**")
  except asyncio.TimeoutError:
          return

bot.run(DISCORD_TOKEN)
