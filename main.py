# region: setup
import asyncio
import codecs
import os
import random
import time

import discord
import pymysql.cursors
from discord.ext import commands
from discord.ext.commands import *
from discord.ext.tasks import *
from discord_slash import *
from dotenv import load_dotenv

import config

intents = discord.Intents.default()
intents.members = True
intents.presences = True

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="&", intents=intents)
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

# region: defs
# cleans users that have 0 points

async def getusertier(user):
  with connection:
    with connection.cursor() as cursor:
      try:
        sql = "SELECT punishTier FROM punish WHERE userId = %s"
        cursor.execute(sql, user.id)
        result = cursor.fetchone()
        result = result['punishTier']
        success = True
      except:
        success = False
  return result
  
async def cleanup():
  with connection:
    with connection.cursor() as cursor:
        sql = "DELETE FROM punish WHERE punishTier = 0 AND punishType is NULL"

        cursor.execute(sql)

    connection.commit()
    print("Completed cleanup")
# remove a point from those with over two weeks of age
@loop(seconds=300)
async def rempoint():
  with connection:
    with connection.cursor() as cursor:
        sql = "UPDATE punish SET punishTier = punishTier - 1 WHERE updateTime < (NOW() - INTERVAL 20160 MINUTE);"

        cursor.execute(sql)

    connection.commit()
  print("Completed auto point removal")
  await cleanup()

async def punish(ctx,offender):

  async def mute(offender, time):
    with connection:
      with connection.cursor() as cursor:
          sql = "UPDATE punish SET punishLength = %s, punishType = 'm' WHERE userId = %s"
          var = (time, offender.id)
          cursor.execute(sql, var)

      connection.commit()
      role = discord.utils.get(ctx.guild.roles, name='Muted')
      await offender.add_roles(role)
      await offender.send("You have been muted for **" + str(time) + " seconds**. Please stay safe! \n- the Warbler team")

  async def warn(offender,final):
    # f = final warning
    if final == True:
      await offender.send("You have been warned! this is your final shot, so please be careful! \n- the Warbler team")
    else:
      await offender.send("You have been warned! you only have one more shot before we start giving real punishments, so please be careful! \n- the Warbler team")
  async def ban(offender, time):
    if time == "forever":
      with connection:
        with connection.cursor() as cursor:
            sql = "UPDATE punish SET punishType = 'p' WHERE userId = %s"
            var = (offender.id)
            cursor.execute(sql, var)

        connection.commit()
        await offender.send("You have been permabanned. we are sorry it had to come to this. \n- the Warbler team")
        await ctx.guild.ban(offender,delete_message_days=1)
    else:
      with connection:
        with connection.cursor() as cursor:
            sql = "UPDATE punish SET punishLength = %s, punishType = 'b' WHERE userId = %s"
            var = (time,offender.id)
            cursor.execute(sql, var)

        connection.commit()
        await offender.send("You have been banned for. **" + str(time) + " seconds**. we are sorry it had to come to this. \n- the Warbler team")
        await ctx.guild.ban(offender,delete_message_days=1)
        
  tier = await getusertier(offender)
  if tier == 1:
  # Warn offender
    await warn(offender,False)
  elif tier == 2:
  # Final warn offender
    await warn(offender,True)
  elif tier == 3:
  # Remove member role from offender (read the rules)
    pass
  elif tier == 4:
  # Mute offender for 5 minutes
    t = 300
    await mute(offender, t)
  elif tier == 5:
  # Mute offender for 10 minutes
    t = 600
    await mute(offender, t)
  elif tier == 6:
  # Mute offender for 30 minutes
    t = 1800
    await mute(offender, t)
  elif tier == 7:
  # Mute offender for 1 hour
    t = 3600
    await mute(offender, t)
  elif tier == 8:
  # Mute offender for 12 hours
    t = 43200
    await mute(offender, t)
  elif tier == 9:
  # mute offender for 24 hours
    t = 86400
    await mute(offender, t)
  elif tier == 10:
  # Ban offender for 3 days
    t = 259200
    await ban(offender,t)
  elif tier == 11:
  # Ban offender for 5 days
    t = 432000
    await ban(offender,t)
  elif tier == 12:
  # Ban offender for 7 days
    t = 604800
    await ban(offender,t)
  elif tier == 13:
  # Ban offender for 14 days
    t = 1210000
    await ban(offender,t)
  elif tier == 14:
  # Ban offender for 30 days
    t = 2592000
    await ban(offender,t)
  elif tier == 15:
  # Permaban
    await ban(offender,"forever")

# endregion

# region: events

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
  # not working yet, will ping all online mods
  if bot.user.mentioned_in(message):
    users = []
    role = discord.utils.get(message.guild.roles,name="Helper")
    for user in message.guild.members:
        if role in user.roles and str(user.status) == "online":
          if user == bot.user:
            pass
          else:
            users.append(user.id)
    await message.channel.send("⚠️ " + message.author.mention + " Mentioned me! (Pinging all online mods... this should be good 👀) \n" + "".join(f"<@!{user}>, " for user in users))
  await bot.process_commands(message)

# endregion

# region: slashes
@slash.slash(name="checkpoints",guild_ids=config.guild_ids,description="check the points of any user ever!")
async def checkpoints(ctx, user: discord.Member):
  await ctx.channel.send("**Hey! 👋** Give me a sec while I look that up for you!")
  async with ctx.channel.typing():
    await asyncio.sleep(1)
  with connection:
    with connection.cursor() as cursor:
        try:
          sql = "SELECT punishTier FROM punish WHERE userId = %s"
          cursor.execute(sql, user.id)
          result = cursor.fetchone()

          result = result['punishTier']
          await ctx.channel.send("**Ok!** we found the user! at time of checking, they have **" + str(result) + "** points")
        except TypeError:
          await ctx.channel.send("**Awesome**, " + user.mention + " Currently has **no points**. thanks for being a great person!")

@slash.slash(name="help",guild_ids=config.guild_ids,description="you should know this already - but maybe you just want bird facts")
async def help(ctx):
  await ctx.channel.send("**Hey! 👋** \nmy job is mostly to help keep the chat clean, and give our wonderful helpers a hand, but there is some useful stuff you should know!\n**Ping Me** if something needs immediate (like right right right now) attention\n**DM me** to contact the mods if something needs private attention\n\n**Oh!** One last thing. here is a random bird fact!\n> " + random.choice(birdfacts))

@slash.slash(name="point",guild_ids=config.guild_ids, description="Gives users points for being bad children")
@commands.has_role("Helper")
async def point(ctx, amount, user: discord.Member):
  author = ctx.author
  success = False
  with connection:
    with connection.cursor() as cursor:
        try:
            sql = "SELECT punishTier FROM punish WHERE userId = %s"
            cursor.execute(sql, user.id)
            result = cursor.fetchone()
            result = result['punishTier']
        except TypeError:
            success = False
        else:
            success = True
            mathishard = int(result) + int(amount)
            await ctx.channel.send("We already have the user. they have **" + str(result) + "** points. after this, they will have **" + str(mathishard) + "** points. **are you sure?** (**y** or **n**)")
  if not success:
    await ctx.channel.send("This will give the user **" + str(amount) + "** points. **are you sure?** (**y** or **n**)")

  def check(message):
      return message.author == author and message.content.startswith("y") or message.content.startswith("n")
  try:
    message = await bot.wait_for('message', timeout=60.0, check=check)
    if message.content.startswith("y"):
      await ctx.channel.send("**Got it!** giving " + user.mention + " the treatment they deserve!")
      if success:
        with connection:
          with connection.cursor() as cursor:
              sql = "UPDATE punish SET punishTier = %s, punishTime = %s WHERE userId = %s"
              var = (int(mathishard), int(time.time()), int(user.id))
              cursor.execute(sql, var)

          connection.commit()
      elif not success:
        with connection:
          with connection.cursor() as cursor:
              sql = "INSERT INTO punish ( userId, punishTier, punishTime ) VALUES ( %s, %s, %s )"
              var = (int(user.id), int(amount), int(time.time()))
              cursor.execute(sql, var)

          connection.commit()
      await punish(ctx,user)
      await cleanup()
    elif message.content.startswith("n"):
      await ctx.channel.send("**Aborted**")
  except asyncio.TimeoutError:
          return
# endregion

rempoint.start()
print("Beginning login")
bot.run(DISCORD_TOKEN)