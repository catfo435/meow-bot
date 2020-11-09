import discord
from discord.ext import commands
import random
import time
import asyncio
import bs4
import lxml
import requests

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=';',help_command = None, intents = intents,activity = game)
game = discord.Game('with Cute Cats 😸')


TOKEN = 'NzcyNDE0NDg2MTMyMDMxNDg5.X56VDA.huM6xIgjmiIuPUDd_bMl1XAEqMA'

def is_me():
    def predicate(ctx):
        return ctx.message.author.id == 698200925311074485
    return commands.check(predicate)

def subcmdchk(ctx):
	return bool(ctx.invoked_subcommand)

@bot.event
async def on_ready():
	print('ONLINE.')

@bot.event
async def on_member_join(member:discord.Member):
	channel = bot.get_channel(773083640669274142)
	embed =  discord.Embed(description = f"Dont listen to <@{155149108183695360}>, he's boring.\nDo whatever you want, this is a chill server.\n<@{member.id}>",
							color  = discord.Color.dark_theme())
	await channel.send(embed = embed)

@bot.event
async def on_member_remove(member:discord.Member):
	channel = bot.get_channel(770569301278851076)
	await channel.send(f'{member.name} left! MEOW...')

@bot.event
async def on_command_error(ctx,error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send(f"{ctx.author.mention} Uh.. That command doesn't exist.\nType **;help** for help on Meow Bot's commands.")

@bot.event
async def on_message(message):
	if message.author != bot.user:

		msg = ''
		msg = ''.join(letter for letter in message.content.split())

		if 'rohit' in msg.lower() and not message.author.bot:
			if message.author.id == 698200925311074485:
				await message.channel.send('Hyper..., Please call him SELGK, will you?')
			elif message.author.id == 719906610151030795:
				await message.channel.send("Why my lord, WHY! Why call yourself rohit!!! PLease dont do this. A GREAT EMPEROR as you has to be called... **SELGK!**")
			else:
				responses = ['FOOL!, REFER TO HIM AS **SELGK**, UNDERSTOOD?',
			              	'MORON!, HE IS **SELGK**, HOW DARE YOU ADDRESS HIM WITHOUT HIS TITLE',
			              	'GIVE RESPECT RASCAL, CALL HIM **SELGK**']
				await message.channel.send(f'{message.author.mention} {random.choice(responses)}')

		if '<@!772414486132031489>' in message.content or '<@772414486132031489>' in message.content:
			if 'hello' in message.content.lower() and 'hello' in message.content.lower():
				await message.channel.send(f"Hey there! {message.author.mention}")

			elif 'bye' in message.content.lower():
				await message.channel.send(f"Going?, Ok bye!\n{message.author.mention}")

			elif'<@!772414486132031489>' == message.content or '<@772414486132031489>' == message.content:
				await message.channel.send(f"Meow Bot, at your service.\n{message.author.mention}")

	await bot.process_commands(message)


class Utility(commands.Cog):
	'''THE UTILITY COMMANDS OF THIS BOT'''

	@commands.command()
	async def ping(self,ctx):
		'''Gives the ping of meow bot'''
		await ctx.send(f'Ping is *{bot.latency * 1000 }* ms')


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
						"type 'hint to know how high and low is the number"
					  "\nType 'quit' to quit game")
		num = random.randint(1,10)
		hints = 1

		def response_chk(msg):
				return msg.channel == ctx.channel and msg.author == ctx.author

		attempts = 1		
		while attempts < 3:
			try:
				await ctx.send(f"Guess the number, you have `{3-attempts}` attempts left and `{hints}` hints to use")
				response = await self.bot.wait_for('message',timeout = 10,check = response_chk)
				if response.content.lower() == 'quit':
					await ctx.send(f"Got scared that you'll lose huh?"
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
				elif int(response.content) in range(1,10):
					if int(response.content) == num:
						await ctx.send(f"You win!\n{ctx.author.mention}")
						await ctx.send(f":confetti_ball:")
						return
					elif attempts == 2:
						pass
					else:
						await ctx.send(f"Wrong bro!, Try again!\n{ctx.author.mention}")
			except asyncio.exceptions.TimeoutError:
				await ctx.send(f'{ctx.author.mention} You didnot guess in time.\nBtw, the number was {num}')
				return
			except ValueError:
				await ctx.send(f"Invalid Response {ctx.author.mention}")

			attempts += 1
		await ctx.send(f'{ctx.author.mention} You ran out of attempts.\nThe number was `{num}`')

	@commands.command()
	async def meow(self,ctx):
		'''A random image of a cat'''
		rand = random.randint(1,1500)
		res = requests.get(f"http://random.cat/view/{rand}")
		soup = bs4.BeautifulSoup(res.text,"lxml")

		meow  = discord.Embed(description = "Meowww...",color = discord.Color.teal())
		meow.set_image(url = soup.select('#cat')[0]['src'])
		await ctx.send(embed = meow)

	@commands.command()
	async def simon(self,ctx,*,arg = None):

		if arg == None:
			await ctx.send(f"{ctx.author.mention}, Type a message for simon to say, duh.")
			return
		await ctx.send(f"Simon says {arg}")

	@commands.command()
	async def adminisafool(self,ctx):

		message = "this server's founder is a fool. Imposes thousand rules as if this is a official game server. I think he never heard the words *chill server*"
		await ctx.invoke(self.bot.get_command('simon'),arg = message)


class Election(commands.Cog):
	
	def __init__(self):
		self.link = discord.Embed(title = 'US Election',url ="https://www.theguardian.com/us-news/ng-interactive/2020/nov/05/us-election-2020-live-results-donald-trump-joe-biden-presidential-votes-arizona-nevada-pennsylvania-georgia", 
				            description="Results of US Election 2020",color = 0x008000)
		self.link.set_image(url='https://i.guim.co.uk/img/media/5a04c4d1d6d43bac9a2007f4bd0827e59ae08390/0_0_2000_1200/master/2000.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&enable=upscale&s=60bb2ecf9357d10003bf9ecfed6699b0')	

	@commands.group()
	async def uselection(self,ctx):
		'''The US Election result 2020'''
		if subcmdchk:
			return
		uselec = discord.Embed(description = "Get to know the status of US Presidential Election '20 with the ;uselection p command\n"
							"Get to know the status of US Senate Election '20 with the ;uselection s command\n"
							 "Get to know the status of US Presidential Election '20 with the ;uselection p command\n")
		await ctx.send(embed = uselec)

	@uselection.command()
	async def p(self,ctx):
		'''Get to know the US Presidential Election '20 results'''

		res = requests.get('https://www.theguardian.com/us-news/ng-interactive/2020/nov/05/us-election-2020-live-results-donald-trump-joe-biden-presidential-votes-arizona-nevada-pennsylvania-georgia')
		soup = bs4.BeautifulSoup(res.text,"lxml")
		
		biden = int(soup.find_all('div',{"class":"ge-bar__count ge-bar__count--p color--D"})[0].text)
		trump = int(soup.find_all("div",{"class":"ge-bar__count ge-bar__count--p color--R"})[0].text)

		b_embed = discord.Embed(description="::confetti_ball::Trump has lost the US PRESIDENTIAL Election!!! :confetti_ball:\nAah also Biden won the election",
			                    color = 0x0000ff )
		t_embed = discord.Embed(description="Trump has won the US PRESIDENTIAL Election",color = 0xff0000 )

		b_votes = discord.Embed(description=f"Biden(Democratic Party) has **{biden}** electoral votes",color = 0x0000ff )
		t_votes = discord.Embed(description=f"Trump(Republican Party) has **{trump}** electoral votes ",color = 0xff0000 )

		await ctx.send(embed = b_votes)
		await ctx.send(embed = t_votes)

		if biden >= 270:
			await ctx.send(embed = b_embed)
		elif trump >= 270:
			await ctx.send(embed = t_embed)
		else:
			await ctx.send("**Either Candidate hasn't reached the 270 mark yet**")

		await ctx.send("For more info, refer:")
		await ctx.send(embed = self.link)

	@uselection.command()
	async def s(self,ctx):
		'''Get to know the US Senate Election '20 results'''

		res = requests.get('https://www.theguardian.com/us-news/ng-interactive/2020/nov/05/us-election-2020-live-results-donald-trump-joe-biden-presidential-votes-arizona-nevada-pennsylvania-georgia')
		soup = bs4.BeautifulSoup(res.text,"lxml")
		
		dem = int(soup.find_all('div',{"class":"ge-bar__count ge-bar__count--s color--D"})[0].text)
		rep = int(soup.find_all("div",{"class":"ge-bar__count ge-bar__count--s color--R"})[0].text)

		d_embed = discord.Embed(description="Democratic Party has won the senate",color = 0x0000ff )
		r_embed = discord.Embed(description="Republican Party has won the senate",color = 0xff0000 )

		d_votes = discord.Embed(description=f"Democratic Party has **{dem}** senate seats",color = 0x0000ff )
		r_votes = discord.Embed(description=f"Republican Party has **{rep}** senate seats",color = 0xff0000 )

		await ctx.send(embed = d_votes)
		await ctx.send(embed = r_votes)

		if dem >= 51:
			await ctx.send(embed = d_embed)
		elif rep >= 51:
			await ctx.send(embed = r_embed)
		else:
			await ctx.send("**Either Candidate hasn't reached the 270 mark yet**")

		await ctx.send("For more info, refer:")
		await ctx.send(embed = self.link)

	@uselection.command()
	async def h(self,ctx):
		'''Get to know the US House Election '20 results'''

		res = requests.get('https://www.theguardian.com/us-news/ng-interactive/2020/nov/05/us-election-2020-live-results-donald-trump-joe-biden-presidential-votes-arizona-nevada-pennsylvania-georgia')
		soup = bs4.BeautifulSoup(res.text,"lxml")
		
		dem = int(soup.find_all('div',{"class":"ge-bar__count ge-bar__count--h color--D"})[0].text)
		rep = int(soup.find_all("div",{"class":"ge-bar__count ge-bar__count--h color--R"})[0].text)

		d_embed = discord.Embed(description="Democratic Party has won the house",
			                    color = 0x0000ff )
		r_embed = discord.Embed(description="Republican Party has won the election",color = 0xff0000 )

		d_votes = discord.Embed(description=f"Biden(Democratic Party) has **{dem}** senate seats",color = 0x0000ff )
		r_votes = discord.Embed(description=f"Trump(Republican Party) has **{rep}** senate seats",color = 0xff0000 )

		await ctx.send(embed = d_votes)
		await ctx.send(embed = r_votes)

		if dem >= 218:
			await ctx.send(embed = d_embed)
		elif rep >= 218:
			await ctx.send(embed = r_embed)
		else:
			await ctx.send("**Either Candidate hasn't reached the 218 mark yet**")

		await ctx.send("For more info, refer:")
		await ctx.send(embed = self.link)


class EmbedHelpCommand(commands.HelpCommand):

	COLOUR = discord.Colour.orange()

	def get_ending_note(self):
		return 'Use {0}{1} [command] for more info on a command.'.format(self.clean_prefix, self.invoked_with)

	def get_command_signature(self, command):
		return '{0.qualified_name} {0.signature}'.format(command)

	async def send_bot_help(self, mapping):
		embed = discord.Embed(title='Bot Commands', colour=self.COLOUR)
		description = self.context.bot.description
		if description:
			embed.description = description

		for cog, commands in mapping.items():
			name = 'No Category' if cog is None else cog.qualified_name
			filtered = await self.filter_commands(commands, sort=True)
			if filtered:
				value = '\u2002\n'.join(c.name for c in filtered)
				if cog:
					value = '{0}\n'.format(value)

				embed.add_field(name=name, value=value)

		embed.set_footer(text=self.get_ending_note())
		await self.get_destination().send(embed=embed)

	async def send_command_help(self,command):
		embed = discord.Embed(title=f'{command.qualified_name.capitalize()} Command', colour=self.COLOUR)

		embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

		embed.set_footer(text=self.get_ending_note())
		await self.get_destination().send(embed=embed)

	async def send_cog_help(self, cog):
		embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog), colour=self.COLOUR)
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
bot.add_cog(Election())
bot.add_cog(Help(bot))


@bot.command(hidden = True)
@is_me()
async def stop_r12(ctx):
	await ctx.send('Going offline...')
	await bot.close()

bot.run(TOKEN)