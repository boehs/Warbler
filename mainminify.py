_G='punishTier'
_F='SELECT punishTier FROM punish WHERE userId = %s'
_E='Helper'
_D='help'
_C='Loaded '
_B='rot_13'
_A=True
import asyncio,codecs,os,random,time,discord,pymysql.cursors
from discord.ext import commands
from discord.ext.commands import *
from discord.ext.tasks import *
from discord_slash import *
from dotenv import load_dotenv
import config
intents=discord.Intents.default()
intents.members=_A
intents.presences=_A
load_dotenv()
DISCORD_TOKEN=os.getenv('DISCORD_TOKEN')
bot=commands.Bot(command_prefix='&',intents=intents)
slash=SlashCommand(bot,sync_commands=_A)
birdfacts=["Lucy's warbler is the smallest known species of warbler!",'my pfp came from <https://www.drawingtenthousandbirds.com/new-blog-1/2015/4/18/why-a-yellow-warbler>','There are 119 species of warbler']
wordblacklist=open('config/blacklist.txt','r')
wordblacklist=wordblacklist.readlines()
wordblacklist=[x.replace('\n','')for x in wordblacklist]
wordblacklist=[codecs.encode(x,_B)for x in wordblacklist]
print(_C+str(len(wordblacklist))+' words from the blacklistlist')
wordgraylist=open('config/graylist.txt','r')
wordgraylist=wordgraylist.readlines()
wordgraylist=[x.replace('\n','')for x in wordgraylist]
wordgraylist=[codecs.encode(x,_B)for x in wordgraylist]
print(_C+str(len(wordgraylist))+' words from the graylist')
bot.remove_command(_D)
try:connection=pymysql.connect(host='localhost',user='root',password='',database='warbler',cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.InternalError:print("Error: You must have a my sql instence running and a database called 'warbler'")
else:print('Connected to SQL')
createtable="\nCREATE TABLE IF NOT EXISTS punish (\n\tuserId BIGINT UNSIGNED NOT NULL COMMENT 'The snowflake id of a punished user',\n\tpunishTier TINYINT UNSIGNED NOT NULL COMMENT 'The tier a given user is on (does not necessarily represent if the user is currently serving a punishment, as it may decrease (every two weeks!) before a users punishment is over), serves as a baseline for future punishments)',\n\tpunishTime BIGINT UNSIGNED NULL COMMENT 'The time a user received the punishment they are currently serving, may be empty if user has points but their punishment has ended',\n\tpunishLength INT UNSIGNED NULL COMMENT 'The length of a punishment a user is serving, may be empty if user has points but their punishment has ended',\n\tpunishType TINYTEXT NULL COMMENT 'm, or b = mute or ban so that when it comes time to revoke a punishment the bot knows what to remove, may be empty if user has points but their punishment has ended',\n\n  PRIMARY KEY (userId)\n);\n"
with connection:
	with connection.cursor()as cursor:cursor.execute(createtable)
	connection.commit()
async def cleanup():
	with connection:
		with connection.cursor()as cursor:sql='DELETE FROM punish WHERE punishTier = 0 AND punishType is NULL';cursor.execute(sql)
		connection.commit();print('Completed cleanup')
@loop(seconds=300)
async def rempoint():
	with connection:
		with connection.cursor()as cursor:sql='UPDATE punish SET punishTier = punishTier - 1 WHERE updateTime < (NOW() - INTERVAL 20160 MINUTE);';cursor.execute(sql)
		connection.commit()
	print('Completed auto point removal');await cleanup()
@bot.event
async def on_ready():print(f"> Logged in as: {bot.user}");print(bot.user.id);print('-----READY----- \n');await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name='The chat! do /help to learn more about my functions'))
@bot.event
async def on_message(message):
	if message.author==bot.user:return
	for word in wordblacklist:
		if word in message.content:await message.delete()
	for word in wordgraylist:
		if word in message.content:await message.delete()
	mention=f"<@!{bot.user.id}>"
	if mention in message.content:
		users=[];role=discord.utils.get(message.guild.roles,name=_E)
		for user in message.guild.members:
			if role in user.roles and str(user.status)=='online':
				if user==bot.user:0
				else:users.append(user.id)
		await message.channel.send('⚠️ '+message.author.mention+' Mentioned me! (Pinging all online mods... this should be good 👀) \n'+''.join((f"<@!{user}>, "for user in users)))
	await bot.process_commands(message)
@slash.slash(name='checkpoints',guild_ids=config.guild_ids,description='check the points of any user ever!')
async def checkpoints(ctx,user):
	await ctx.channel.send('**Hey! 👋** Give me a sec while I look that up for you!')
	async with ctx.channel.typing():await asyncio.sleep(1)
	with connection:
		with connection.cursor()as cursor:
			try:sql=_F;cursor.execute(sql,user.id);result=cursor.fetchone();result=result[_G];await ctx.channel.send('**Ok!** we found the user! at time of checking, they have **'+str(result)+'** points')
			except TypeError:await ctx.channel.send('**Awesome**, '+user.mention+' Currently has **no points**. thanks for being a great person!')
@slash.slash(name=_D,guild_ids=config.guild_ids,description='you should know this already - but maybe you just want bird facts')
async def help(ctx):await ctx.channel.send('**Hey! 👋** \nmy job is mostly to help keep the chat clean, and give our wonderful helpers a hand, but there is some useful stuff you should know!\n**Ping Me** if something needs immediate (like right right right now) attention\n**DM me** to contact the mods if something needs private attention\n\n**Oh!** One last thing. here is a random bird fact!\n> '+random.choice(birdfacts))
@slash.slash(name='point',guild_ids=config.guild_ids,description='Gives users points for being bad children')
@commands.has_role(_E)
async def point(ctx,amount,user):
	D='n';C='y';B='** points. **are you sure?** (**y** or **n**)';A=False;author=ctx.author;success=A
	with connection:
		with connection.cursor()as cursor:
			try:sql=_F;cursor.execute(sql,user.id);result=cursor.fetchone();result=result[_G]
			except TypeError:success=A
			else:success=_A;mathishard=int(result)+int(amount);await ctx.channel.send('We already have the user. they have **'+str(result)+'** points. after this, they will have **'+str(mathishard)+B)
	if not success:await ctx.channel.send('This will give the user **'+str(amount)+B)
	def check(message):return message.author==author and message.content.startswith(C)or message.content.startswith(D)
	try:
		message=await bot.wait_for('message',timeout=60.0,check=check)
		if message.content.startswith(C):
			await ctx.channel.send('**Got it!** giving '+user.mention+' the treatment they deserve!')
			if success:
				with connection:
					with connection.cursor()as cursor:sql='UPDATE punish SET punishTier = %s, punishTime = %s WHERE userId = %s';var=int(mathishard),int(time.time()),int(user.id);cursor.execute(sql,var)
					connection.commit()
			elif not success:
				with connection:
					with connection.cursor()as cursor:sql='INSERT INTO punish ( userId, punishTier, punishTime ) VALUES ( %s, %s, %s )';var=int(user.id),int(amount),int(time.time());cursor.execute(sql,var)
					connection.commit()
			await cleanup()
		elif message.content.startswith(D):await ctx.channel.send('**Aborted**')
	except asyncio.TimeoutError:return
rempoint.start()
print('Beginning login')
bot.run(DISCORD_TOKEN)