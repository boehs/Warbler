# region: setup
import asyncio
import codecs
import datetime as dt
import os
import random
import time
import re
import discord
from discord import message
import humanize
import pymysql.cursors
from discord.ext import commands
from discord.ext.commands import *
from discord.ext.tasks import *
from discord_slash import *
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
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

workarounds = re.compile('|'.join(map(re.escape, ["\n"," ",".",'"',"'",",","@","*","!","$","?"])))
workarounds = re.compile('[^a-zA-Z]')

bot.remove_command("help")
try:
  connection = pymysql.connect(host='localhost',user='root',password='',database='warbler',cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.InternalError:
  print("Error: You must have a my sql instence running and a database called 'warbler'")
else:
  print("Connected to SQL")


createtable = """
-- warbler.punish definition

CREATE TABLE IF NOT EXISTS `punish` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `userId` bigint(20) unsigned NOT NULL COMMENT 'The snowflake id of a punished user',
  `guildId` bigint(20) unsigned NOT NULL,
  `punishTier` tinyint(2) unsigned NOT NULL COMMENT 'The tier a given user is on (does not necessarily represent if the user is currently serving a punishment, as it may decrease (every two weeks!) before a users punishment is over), serves as a baseline for future punishments)',
  `punishTime` bigint(20) unsigned DEFAULT NULL COMMENT 'The time a user received the punishment they are currently serving, may be empty if user has points but their punishment has ended',
  `punishLength` int(10) unsigned DEFAULT NULL COMMENT 'The length of a punishment a user is serving, may be empty if user has points but their punishment has ended',
  `punishType` tinytext DEFAULT NULL COMMENT 'm, or b = mute or ban so that when it comes time to revoke a punishment the bot knows what to remove, may be empty if user has points but their punishment has ended',
  `updateTime` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
"""

with connection:
    with connection.cursor() as cursor:
        cursor.execute(createtable)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

# endregion

# region: defs
# fetches user tiers
async def getusertier(ctx,user):
  with connection:
    with connection.cursor() as cursor:
      sql = "SELECT punishTier FROM punish WHERE userId = %s AND guildId = %s"
      cursor.execute(sql, (user.id,ctx.guild.id))
      result = cursor.fetchone()
      result = result['punishTier']
  return result
# purges uses with 0 points
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
# take candy from the children
@loop(seconds=60)
async def autoremovepunish(): 
  await bot.wait_until_ready()
  with connection:
    with connection.cursor() as cursor:
      sql = "SELECT userId, guildId, punishType FROM punish WHERE ( punishLength + punishTime ) <= UNIX_TIMESTAMP()"
      cursor.execute(sql)
      users = cursor.fetchall()
      for u in users:
        print(str(u))
        guild = bot.get_guild(u['guildId'])
        user = bot.get_user(u['userId'])
        member = guild.get_member(u['userId'])
        if u['punishType'] == ('b','p'):
            await guild.unban(user)
        elif u['punishType'] == 'm':
          role = discord.utils.get(guild.roles, name='Muted')
          await member.remove_roles(role)
        with connection:
          with connection.cursor() as cursor:
            sql = "UPDATE punish SET punishLength = NULL, punishType = NULL WHERE userId = %s AND guildId = %s"
            cursor.execute(sql, (u['userId'],u['guildId']))
        connection.commit()
        await user.send("cool mate. your punishment is over. welcome back and be good! next time your going to the dungeon :O")
  print("Completed auto punish removal")
          			
# handout punishments like candy
async def punish(ctx,offender,reason):
  if reason == None:
    reason = "None"
  async def mute(offender, time):
    with connection:
      with connection.cursor() as cursor:
          sql = "UPDATE punish SET punishLength = %s, punishType = 'm' WHERE userId = %s AND guildId = %s"
          var = (time, offender.id, ctx.guild.id)
          cursor.execute(sql, var)

      connection.commit()
      role = discord.utils.get(ctx.guild.roles, name='Muted')
      await offender.add_roles(role)
      await offender.send("You have been muted for **" + humanize.naturaldelta(dt.timedelta(seconds=time)) + " **. Please stay safe!\n**Reason**: " + reason + "\n- the Warbler team")

  async def warn(offender,final):
    # f = final warning
    if final == True:
      await offender.send("You have been warned! this is your final shot, so please be careful! \n- the Warbler team")
    else:
      await offender.send("You have been warned! you only have one more shot before we start giving real punishments, so please be careful!\n**Reason**: " + reason + "\n- the Warbler team")
  async def ban(offender, time):
    if time == "forever":
      with connection:
        with connection.cursor() as cursor:
            sql = "UPDATE punish SET punishType = 'p' WHERE userId = %s AND guildId = %s"
            var = (offender.id, ctx.guild.id)
            cursor.execute(sql, var)

        connection.commit()
        await offender.send("You have been permabanned. we are sorry it had to come to this.\n**Reason**: " + reason + "\n- the Warbler team")
        if reason == "None":
          await ctx.guild.ban(offender,delete_message_days=1)
        else:
          await ctx.guild.ban(offender,delete_message_days=1,reason=reason)
    else:
      with connection:
        with connection.cursor() as cursor:
          sql = "UPDATE punish SET punishLength = %s, punishType = 'b' WHERE userId = %s AND guildId = %s"
          var = (time,offender.id,ctx.guild.id)
          cursor.execute(sql, var)

        connection.commit()
        await offender.send("You have been banned for. **" + humanize.naturaldelta(dt.timedelta(seconds=time)) + " **. we are sorry it had to come to this. \n- the Warbler team")
        if reason == "None":
          await ctx.guild.ban(offender,delete_message_days=1)
        else:
          await ctx.guild.ban(offender,delete_message_days=1,reason=reason)
  # [["r"="purge user of all punishments","w"=Warn (0=warning,1=finalwarning),"m"=mute,"b"=ban(0=forever)],[n=punishtime(seconds)]]
  punishtypes = [["r",0],
                  ["w",0],
                  ["w",1],
                  ["k"],
                  ["m",300],
                  ["m",600],
                  ["m",1800],
                  ["m",3600],
                  ["m",43200],
                  ["m",86400],
                  ["b",259200,],
                  ["b",432000],
                  ["b",604800],
                  ["b",1210000],
                  ["b",2592000],
                  ["b",0]]
  n = await getusertier(ctx,offender)
  if punishtypes[n][0] == 'r':
      print("Removing all punishments, " + str(punishtypes[n][1]))
  elif punishtypes[n][0] == 'w':
      if punishtypes[n][1] == 0:
          await warn(offender,False)
      elif punishtypes[n][1] == 1:
          await warn(offender,True)
  elif punishtypes[n][0] == 'k':
      if punishtypes[n][1] == 0:
          print("Kick")
  elif punishtypes[n][0] == 'm':
      if punishtypes[n][1] == 0:
          print("Mute (forever)")
      else:
          await mute(offender, punishtypes[n][1])
  elif punishtypes[n][0] == 'sb':
      print("Soft Ban, " + str(punishtypes[n][1]))
  elif punishtypes[n][0] == 'b':
      if punishtypes[n][1] == 0:
          await ban(offender,punishtypes[n][1])
      else:
          await ban(offender,"forever")
# endregion

# region: events

@bot.event
async def on_ready():
  print(f'> Logged in as: {bot.user}')
  print(bot.user.id)
  print('-----READY----- \n')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The chat! do /help to learn more!"))

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  for word in wordblacklist:
    if word in workarounds.sub("", message.content.lower()):
      await message.delete()
      # give user a point
  for word in wordgraylist: 
    if word in workarounds.sub("", message.content.lower()):
      await message.delete()
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

@bot.event
async def on_message_edit(before,after):
  for word in wordblacklist:
    if word in workarounds.sub("", after.content.lower()):
      await after.delete()
      # give user a point
  for word in wordgraylist:
    if word in workarounds.sub("", after.content.lower()):
      await after.delete()
# endregion

# region: slashes
@slash.slash(name="checkpoints",guild_ids=config.guild_ids,description="check the points of any user ever!")
async def checkpoints(ctx, user: discord.Member):
  with connection:
    with connection.cursor() as cursor:
        try:
          sql = "SELECT punishTier FROM punish WHERE userId = %s AND guildId = %s"
          cursor.execute(sql, (user.id, ctx.guild.id))
          result = cursor.fetchone()

          result = result['punishTier']
          await ctx.send("**Ok!** we found the user! at time of checking, they have **" + str(result) + "** points", hidden=True)
        except TypeError:
          await ctx.send("**Awesome**, " + user.mention + " Currently has **no points**. thanks for being a great person!", hidden=True)
  await ctx.respond(eat=True)

@slash.slash(name="help",guild_ids=config.guild_ids,description="you should know this already - but maybe you just want bird facts")
async def help(ctx):
  await ctx.send("**Hey! 👋** \nmy job is mostly to help keep the chat clean, and give our wonderful helpers a hand, but there is some useful stuff you should know!\n**Ping Me** if something needs immediate (like right right right now) attention\n**DM me** to contact the mods if something needs private attention\n\n**Oh!** One last thing. here is a random bird fact!\n> " + random.choice(birdfacts), hidden=True)
  await ctx.respond(eat=True)

r=0 # fix a bug with discord api
@slash.slash(name="point",
description="Gives users points for being bad children",
guild_ids=config.guild_ids,
options=[
    create_option(
        name="amount",
        description="How many points to grant",
        option_type=4,
        required=True
    ),
    create_option(
        name="user",
        description="Ping the user to punish",
        option_type=6,
        required=True
    ),
    create_option(
        name="reason",
        description="Why is the user being punished?",
        option_type=3,
        required=False
    ),   
])
@commands.has_role("Helper")
async def point(ctx, amount, user: discord.Member, reason = None):
  await ctx.respond()
  global r
  author = ctx.author
  success = False
  with connection:
    with connection.cursor() as cursor:
        try:
            sql = "SELECT punishTier FROM punish WHERE userId = %s AND guildId = %s"
            cursor.execute(sql, (user.id, ctx.guild.id))
            result = cursor.fetchone()
            result = result['punishTier']
        except TypeError:
            success = False
        else:
            success = True
            mathishard = int(result) + int(amount)
            if r == 0:
              await ctx.channel.send("We already have the user. they have **" + str(result) + "** points. after this, they will have **" + str(mathishard) + "** points. **are you sure?** (**y** or **n**)")
              r = r + 1
  if not success:
    await ctx.channel.send("This will give the user **" + str(amount) + "** points. **are you sure?** (**y** or **n**)")
  def check(message):
      return message.author == author and (message.content.startswith("y") or message.content.startswith("n"))
  try:
    message = await bot.wait_for('message', timeout=60.0, check=check)
    if message.content.startswith("y"):
      await ctx.channel.send("**Got it!** giving " + user.mention + " the treatment they deserve!")
      if success:
        with connection:
          with connection.cursor() as cursor:
              sql = "UPDATE punish SET punishTier = %s, punishTime = %s WHERE userId = %s AND guildId = %s"
              var = (int(mathishard), int(time.time()), int(user.id), int(ctx.guild.id))
              cursor.execute(sql, var)

          connection.commit()
      elif not success:
        with connection:
          with connection.cursor() as cursor:
              sql = "INSERT INTO punish ( userId, punishTier, punishTime, guildId ) VALUES ( %s, %s, %s, %s )"
              var = (int(user.id), int(amount), int(time.time()), ctx.guild.id)
              cursor.execute(sql, var)

          connection.commit()
      await punish(ctx,user,reason)
      await cleanup() 
    elif message.content.startswith("n"):
      await ctx.channel.send("**Aborted**")
  except asyncio.TimeoutError:
          return
  r = 0
# endregion
rempoint.start()
autoremovepunish.start()
print("Beginning login")
bot.run(DISCORD_TOKEN)
