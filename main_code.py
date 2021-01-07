import discord
from discord.ext import commands
import random
import time
import asyncpg
from datetime import datetime,timedelta
import re
import pytz
import ssl
import asyncio
import bs4
import lxml
import requests
import os

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

async def get_pre(bot,message):
	async with bot.pool.acquire() as conn:
		async with conn.transaction():
			prefix = await conn.fetch('SELECT prefix FROM prefix WHERE guild=$1',message.guild.id)
			if not prefix[0]['prefix']:
				return ';'
			return prefix[0]['prefix']

game = discord.Game('with Cute Cats 😸')
bot = commands.Bot(command_prefix=get_pre,help_command = None, intents = intents,activity = game)

TOKEN = 'NzcyNDE0NDg2MTMyMDMxNDg5.X56VDA.F3VBV5qfKohHzL22gOIJeo2CSW0'
UTC = pytz.utc

def is_admin():
    def predicate(ctx):
        return ctx.message.author.guild_permissions.administrator
    return commands.check(predicate)

def subcmdchk(ctx):
	return bool(ctx.invoked_subcommand)

@bot.event
async def on_ready():
	print('ONLINE.')

@bot.event
async def on_member_remove(member:discord.Member):
	if member.bot:
		return
	async with bot.pool.acquire() as conn:
		async with conn.transaction():
			await conn.execute('DELETE FROM userafk WHERE id = $1 AND guild = $2',member.id,member.guild.id)

@bot.event
async def on_guild_join(guild:discord.Guild):
	async with bot.pool.acquire() as conn:
		async with conn.transaction():
			await conn.execute('INSERT INTO prefix(guild) VALUES($1)',guild.id)

@bot.event
async def on_guild_remove(guild:discord.Guild):
	async with bot.pool.acquire() as conn:
		async with conn.transaction():
			await conn.execute('DELETE FROM prefix WHERE guild=$1',guild.id)

@bot.event
async def on_command_error(ctx,error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send(f"{ctx.author.mention} Uh.. That command doesn't exist.\nType **;help** for help on Meow Bot's commands.")
	if isinstance(error,commands.CommandOnCooldown):
		await ctx.send(f"{ctx.author.mention} wait for {error.retry_after:.2f} seconds")

@bot.event
async def on_message(message):
	global UTC
	if message.author == bot.user:
		return
		
	async with bot.pool.acquire() as conn:
		async with conn.transaction():
				afk = await conn.fetchval('SELECT afk FROM userafk WHERE id = $1 AND guild = $2',message.author.id,message.guild.id)
				afkall = await conn.fetch('SELECT id,reason,time FROM userafk WHERE afk = true AND guild = $1',message.guild.id)

				if not afk:
					pass
				if afk:
					embed = discord.Embed(title = 'AFK Removed', description = f"Welcome back {message.author.mention}!",color = discord.Color.green())
					await message.channel.send(embed = embed)
					await conn.execute('UPDATE userafk SET afk = false,reason = NULL,time = NULL WHERE id = $1 AND guild = $2',message.author.id,message.guild.id)
					return

				for record in afkall:
					user = message.guild.get_member(record['id'])
					if user.mentioned_in(message):

						time = datetime.now(UTC) - record['time']
						days = f'{time.days} days' if time.days != 0 else ''
						time = time.seconds
						time = time % (24 * 3600)
						hours = f'{time // 3600} hours' if time // 3600 != 0 else ''
						time %= 3600
						minutes = f'{time // 60} minutes' if time // 60 != 0 else ''
						time %= 60
						seconds = f'{time} seconds'
						
						embed = discord.Embed(title = 'AFK ping', description = f'*{user.display_name}* is afk for**{days} {hours} {minutes} {seconds}**.\nReason: {record["reason"]}',color = discord.Color.orange())
						await message.channel.send(embed = embed)

	if bot.user.mention in message.content:
		if 'hello' in message.content.lower():
			await message.channel.send(f"Hey there! {message.author.mention}")

		elif 'bye' in message.content.lower():
			await message.channel.send(f"Going?, Ok bye!\n{message.author.mention}")

		elif bot.user.mention == message.content:
			await message.channel.send(f"Meow Bot, at your service.\n{message.author.mention}")

	await bot.process_commands(message)

class Utility(commands.Cog):
	'''THE UTILITY COMMANDS OF THIS BOT'''

	@commands.command()
	async def info(self,ctx):
		'''Get to know about the bot'''
		embed = discord.Embed(title="Meow Bot",color=ctx.me.color)
		embed.set_thumbnail(url=bot.user.avatar_url)
		embed.add_field(name='Joined Discord on',value=ctx.me.created_at.date(),inline=False)
		embed.add_field(name=f'Joined {ctx.guild.name} on',value=ctx.me.joined_at.date(),inline=False)
		await ctx.send(embed=embed)

	@commands.command()
	async def ping(self,ctx):
		'''Gives the ping of meow bot'''
		await ctx.send(f"Cats don't care about pings actually\nFor the dogs, the ping is *{round(bot.latency * 1000)}* ms")

	@commands.command()
	async def afk(self,ctx,*,args = None):
		'''Set your afk'''
		global UTC
		if len(args) > 500:
		        await ctx.send(f"{ctx.author.mention}Exceeded Character Limit!")
		async with bot.pool.acquire() as conn:

			async with conn.transaction():
				accstate = await conn.fetchval('SELECT * FROM userafk WHERE id=$1 AND guild =$2',ctx.author.id,ctx.guild.id)

				if not accstate:
					await conn.execute('INSERT INTO userafk(id,guild,afk) VALUES($1,$2,false)',ctx.author.id,ctx.guild.id)
				else:
					pass

				await conn.execute('UPDATE userafk SET afk = true,reason = $1,time = $2 WHERE id = $3 AND guild = $4',args,datetime.now(UTC),ctx.author.id,ctx.guild.id)
				embed = discord.Embed(title = 'AFK Set', description = f'Your afk has been set: {args}',color = discord.Color.red())
				embed.set_footer(text='To avoid pings,set your status to DND.',icon_url="https://cdn.discordapp.com/embed/avatars/4.png")
				await ctx.send(embed = embed)

	@commands.command()
	async def announce(self,ctx,channel:discord.TextChannel,*,args):
		'''Sends an embed with given text in the given channel'''

		embed = discord.Embed(title='ANNOUNCEMENT',description=args,color=discord.Color.red())
		announcement = await channel.send(embed = embed)
		await ctx.send(f'Announced in {channel.name}\n{announcement.jump_url}')
	
	@commands.command(aliases=['av','pfp'])
	async def avatar(self,ctx,user:discord.Member = None):
		'''Get the pfp of yourself or someone else's'''
								      
		embed = discord.Embed(title=f"{user.name if user else ctx.author.name}'s pfp",color=user.color if user else ctx.author.color)
		embed.set_image(url=user.avatar_url + "&size=1024" if user else ctx.author.avatar_url+ "&size=1024")
		embed.set_footer(text = f"Requested by {ctx.author.name}")
		await ctx.send(embed = embed)
	
	@commands.command()
	async def remind(self,ctx,time,*,args=None):
		'''Use this to remind yourself abt smth
		   The time argument supports all types of time:
		   1.1week 10days
		   2.1w 10d
		   3.1WEEK 10DAYS
		   
		   If the time has more than one keyword like 10min 20sec, then put it in quotes
		   But donot give space between the value and word'''
		async def convert(time):

			if 'month' in time.lower():
				return None

			ref = {'s':'seconds', 'm':'minutes', 'h':'hours', 'd':'days', 'w':'weeks'}
			return int(timedelta(**{
			ref.get(m.group('unit').lower(), 'seconds'): int(m.group('val'))
			for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', time, flags=re.I)
			}).total_seconds())
		
		time_seconds = await convert(time)

		if not time_seconds:
			await ctx.send('Invalid Entry')
			return

		desc = f'to {args} in {time}' if args else f'in {time}'
		embed = discord.Embed(title='Remind',description=f'Ok {ctx.author.mention}, I will remind you {desc}',color = discord.Color.green())
		await ctx.send(embed=embed)
		await asyncio.sleep(time_seconds)
		embed = discord.Embed(title='Reminder!',description=args,color=discord.Color.orange())
		await ctx.send(ctx.author.mention)
		await ctx.send(embed=embed)
	
	@commands.command()
	@is_admin()
	@commands.cooldown(1,86400,commands.BucketType.guild)
	async def setprefix(self,ctx,prefix):
		'''Sets the prefix for the bot(only for current guild)
			Needs Administrator Perms'''
		if len(prefix) > 1:
			await ctx.send('More than one character not allowed')
			return
		
		async with bot.pool.acquire() as conn:
			async with conn.transaction():
				await conn.execute('UPDATE prefix SET prefix=$1 WHERE guild=$2',prefix,ctx.guild.id)
				await ctx.send(f'{ctx.author.mention}, prefix is set to {prefix}')	

class Fun(commands.Cog):
	'''Have fun with these commands'''

	@commands.command()
	async def rolldice(self,ctx):
		'''Rolls a dice of 6'''
		await ctx.send(f"{ctx.author.mention} The dice rolled {random.randint(1,6)}")

	@commands.command()
	async def guessnum(self,ctx):
		'''Guess a number between 1 to 10'''

		await ctx.send(f"{ctx.author.mention}, guess a number between 1 to 10. (You have 10 seconds to answer and `2 attempts` and a `hint`.)"
						"type 'hint to know how high or low is the number"
					  "\nType 'quit' to quit game")
		num = random.randint(1,10)
		hints = 1

		def response_chk(msg):
				return msg.channel == ctx.channel and msg.author == ctx.author

		attempts = 1		
		while attempts < 3:
			try:
				await ctx.send(f"Guess the number, you have `{3-attempts}` attempts left and `{hints}` hints to use")
				response = await bot.wait_for('message',timeout = 10,check = response_chk)

				if response.content.lower() == 'quit':
					await ctx.send(f"Got scared that you'll lose huh?\n"
									f"\nBtw, the number was {num}\n{ctx.author.mention}")
					return

				elif response.content.lower() == 'hint' and hints:
					hints = 0
					attempts -= 1
					if num not in [1,10]:
						choice = random.randint(0,1)
						if choice:
							await ctx.send(f"The number is higher than {random.randint(1,num-1)}")
						else:
							await ctx.send(f"The number is lower than {random.randint(num+1,10)}")
					else:
						if num == 1:
							await ctx.send(f"The number is lower than {random.randint(num+1,10)}")
						else:
							await ctx.send(f"The number is higher than {random.randint(1,num-1)}")

				elif int(response.content) in range(1,11):
					if int(response.content) == num:
						await ctx.send(f"You win!\n{ctx.author.mention}")
						await ctx.send(f":confetti_ball:")
						return
					elif attempts == 2:
						pass
					else:
						await ctx.send(f"Wrong bro!, Try again!\n{ctx.author.mention}")

				else:
					await ctx.send('Response not in range 1 to 10')
					attempts -= 1

			except Exception as err:
				if isinstance(err,ValueError):
					await ctx.send("Invalid Response")
					attempts -= 1
				else:
					await ctx.send("Time's Up!")
					return

			attempts += 1
		await ctx.send(f'{ctx.author.mention} You ran out of attempts.\nThe number was `{num}`')
	

	@commands.command(aliases=['mew','cat'])
	@commands.cooldown(1,5,commands.BucketType.member)
	async def meow(self,ctx):
		'''A random image of a cat'''

		#The Cat API

		res = requests.get('https://api.thecatapi.com/v1/images/search?size=small&mime_types=png,jpg&api_key=63b9a514-aad1-40fd-bb8c-d50b5ed28db3')
		soup = bs4.BeautifulSoup(res.text,"lxml")
		soup = soup.p.text

		imglist = eval(soup)
		imgurl = imglist[0]['url']

		meow  = discord.Embed(description = "Meowww...",color = discord.Color.teal())
		meow.set_image(url = imgurl)
		meow.set_footer(text = "Powered by The Cat API | https://thecatapi.com",icon_url='https://cdn2.thecatapi.com/logos/thecatapi_256xW.png')
		await ctx.send(embed = meow)

	@commands.command(aliases=['doggo','dog'])
	@commands.cooldown(1,5,commands.BucketType.member)
	async def woof(self,ctx):
		'''A random image of a dog'''

		#The Dog API

		res = requests.get('https://api.thedogapi.com/v1/images/search?size=small&mime_types=png,jpg&api_key=f118c7ee-c9fe-4fb6-8836-d2487e3b0f28-d50b5ed28db3')
		soup = bs4.BeautifulSoup(res.text,"lxml")
		soup = soup.p.text

		imglist = eval(soup)
		imgurl = imglist[0]['url']

		woof  = discord.Embed(description = "Woof!",color = discord.Color.gold())
		woof.set_image(url = imgurl)
		woof.set_footer(text = "Powered by The Dog API | https://thedogapi.com",icon_url='https://cdn2.thedogapi.com/logos/wave-square_256.png')
		await ctx.send(embed = woof)

	@commands.command()
	async def simon(self,ctx,*,arg = None):
		'''Simon says what u say'''
		if not arg:
			await ctx.send(f"{ctx.author.mention}, Type a message for simon to say, duh.")
			return
		await ctx.send(f"Simon says {arg}")

class EmbedHelpCommand(commands.HelpCommand):

	COLOUR = discord.Colour.orange()
	emoji_ref = {'Utility':':tools:','Fun':':partying_face:','Help':':speech_balloon:'}
	version = os.getenv('VERSION')

	def get_ending_note(self,mode = 0):
		if not mode:
			return 'Use {0}{1} [command] for more info on a command | Version: {2}'.format(self.clean_prefix, self.invoked_with, self.version)
		else:
			return 'Use {0}{1} [category] for more info on the category | Version: {2}'.format(self.clean_prefix, self.invoked_with, self.version)

	def get_command_signature(self, command):
		return '{0.qualified_name} {0.signature}'.format(command)

	async def send_bot_help(self, mapping):
		embed = discord.Embed(title='Bot Help', colour=self.COLOUR)

		cog_names = []
		
		def cogs():
			for cog in bot.cogs.items():
				yield cog[0] #name of cog

		for cog_name in cogs():
			name = f'{cog_name} {self.emoji_ref[cog_name] or ""}'

			cog_names.append(name)

		value = ''
		for i in range(len(cog_names)):
			if i and i%3==0:
				value += cog_names[i] + '\n'
				continue

			value += cog_names[i] + '\u2002'*6	
		embed.description = value		

		embed.set_footer(text=self.get_ending_note(1))
		await self.get_destination().send(embed=embed)

	async def send_command_help(self,command):
		embed = discord.Embed(title=f'{command.qualified_name.capitalize()} Command', colour=self.COLOUR)

		embed.add_field(name=self.get_command_signature(command), value=command.help or '...', inline=False)
		aliases = ' , '.join(c for c in command.aliases) if command.aliases else 'None'
		embed.add_field(name='Aliases', value=aliases,inline=False)

		embed.set_footer(text=self.get_ending_note())
		await self.get_destination().send(embed=embed)

	async def send_cog_help(self, cog):
		cog_name = f'{cog.qualified_name} {self.emoji_ref[cog.qualified_name] or ""}'
		embed = discord.Embed(title=f'{cog_name} Commands', colour=self.COLOUR)
		if cog.description:
			embed.description = cog.description

		filtered = await self.filter_commands(cog.get_commands(), sort=True)
		for command in filtered:
			embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

		embed.set_footer(text=self.get_ending_note())
		await self.get_destination().send(embed=embed)

	async def send_group_help(self, group):
		embed = discord.Embed(title=group.qualified_name, colour=self.COLOUR)
		if group.help:
			embed.description = group.help

		if isinstance(group, commands.Group):
			filtered = await self.filter_commands(group.commands, sort=True)
			for command in filtered:
				embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

		embed.set_footer(text=self.get_ending_note())
		await self.get_destination().send(embed=embed)

	#This makes it so it uses the function above
	#Less work for us to do since they're both similar.
	#If you want to make regular command help look different then override it

class Help(commands.Cog):
	'''The Help Command'''

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.bot._original_help_command = bot.help_command
		self.bot.help_command = EmbedHelpCommand()
		self.bot.help_command.cog = self


	def cog_unload(self):
		self.bot.help_command = self.bot._original_help_command
		

bot.add_cog(Utility())
bot.add_cog(Fun())
bot.add_cog(Help(bot))

cntxt = ssl.create_default_context(cafile='rds-ca-2019-root.pem')
cntxt.check_hostname = False
cntxt.verify_mode = ssl.CERT_NONE

bot.pool = asyncio.get_event_loop().run_until_complete(asyncpg.create_pool(dsn=os.getenv('DATABASE_URL'),
	min_size = 1,max_size=1,ssl = cntxt))
	
bot.run(TOKEN)
