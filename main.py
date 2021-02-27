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
import csv

birdfacts = ["Lucy's warbler is the smallest known species of warbler!", "my pfp came from <https://www.drawingtenthousandbirds.com/new-blog-1/2015/4/18/why-a-yellow-warbler>", "There are 119 species of warbler"]

wordblacklist = open("config/blacklist.txt","r")
wordblacklist = wordblacklist.readlines()
wordblacklist = [x.replace('\n', '') for x in wordblacklist]
print("Loaded " + str(len(wordblacklist)) + " words from the blacklistlist")

wordgraylist = open("config/graylist.txt","r")
wordgraylist = wordgraylist.readlines()
wordgraylist = [x.replace('\n', '') for x in wordgraylist]
print("Loaded " + str(len(wordgraylist)) + " words from the graylist")

bot.remove_command("help")

print("beginning login")

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

@bot.command()
async def checkpoints(ctx, user: discord.Member):
  await ctx.channel.send("**Hey! 👋** Give me a sec while I look that up for you!")
  success = False
  async with ctx.typing():
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
                await ctx.channel.send("**Ok!** we found the user! at time of checking, they have " + row[1] + " points")
        line_count = line_count + 1
  if success == True:
    pass
  else:
    await ctx.channel.send("Awesome, " + user.mention + " Currently has no points. thanks for being a great person!")

@bot.command()
async def help(ctx):
  async with ctx.typing():
    await asyncio.sleep(1)
  await ctx.channel.send("**Hey! 👋** \nmy job is mostly to help keep the chat clean, and give our wonderful helpers a hand, but there is some useful stuff you should know!\n**Ping Me** if something needs immediate (like right right right now) attention\n**DM me** to contact the mods if something needs private attention\n\n**Oh!** One last thing. here is a random bird fact!\n> " + random.choice(birdfacts))

@bot.command()
@commands.has_role("Helper")
async def point(ctx, ammount, user: discord.Member, *, reason):
  author = ctx.author
  success = False
  async with ctx.typing():
    with open('database/punish.csv') as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_count = 0
      for row in csv_reader:
          if line_count == 0:
              pass
          else:
              if row[0] == str(user.id):
                  success = True
                  mathishard = int(row[1]) + int(ammount)
                  await ctx.channel.send("We already have the user. they have" + row[1] + " points. after this, they will have " + str(mathishard) + " points. are you sure? (y or n)")
                  break
          line_count = line_count + 1
    if not success:
      await ctx.channel.send("This will give the user **" + str(ammount) + "** points. are you sure? (y or n)")
  def check(message):
      return message.author == author and message.content.startswith("y") or message.content.startswith("n")
  try:
    message = await bot.wait_for('message', timeout=60.0, check=check)
    if message.content.startswith("y"):
      await ctx.channel.send("Got it! giving " + user.mention + " the treatment they deserve!")
    elif message.content.startswith("n"):
      await ctx.channel.send("aborted")
  except asyncio.TimeoutError:
          return

bot.run(DISCORD_TOKEN)