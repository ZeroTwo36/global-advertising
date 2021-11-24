import discord
from discord.ext import commands,tasks
import datetime
from dhooks import Webhook,Embed
import typing
import asyncio
bot = commands.Bot(command_prefix="g!")
import discord
import json
from discord.ext import commands
import os

if os.path.isfile("globalchat.json"):
    with open("globalchat.json",encoding="utf-8") as f:
        chats = json.load(f)

else:
    chats = {'servers': []}
    with open("globalchat.json","w",encoding="utf-8") as f:
        json.dump(chats,f,indent=4)

JOINSTRING = """
Hi! Thanks for adding `Global Advertising` to your server
*Here is a few things about me and a method to setting me up!

_About me_
I am an Advertisement Bot designed for Discord. I work similar to a Global Chat Bot.

_Setup_
To get started, type in `g!link #channel`. Then everyone can post their Ads in there and
They'll reach incredibly much attention!

If you need any support or have any questions, please join our support server: https://discord.gg/6wDNZAq8we
"""

hook = Webhook("https://discord.com/api/webhooks/910213503325978675/tLe887NfyOA7ws09Ci6xkyPNfwTFenw55Q93Xcj-N0j9ehYMHqO4CdaQ3JTM_60Oc2ba")
queue = []

@bot.event
async def on_guild_join(guild):
    embed = Embed(title="Guild Join",description=f'Bot added to {guild.name} ({guild.id})')
    embed.add_field(name="Guild Number",value=len(bot.guilds))
    hook.send(embed=embed)
    for channel in guild.text_channels:
        try:
            await channel.send(JOINSTRING)
            break
        except:
            continue

@bot.command()
async def invite(ctx):
    embed = discord.Embed()
    embed.description = "[`Invite me`](https://discord.com/api/oauth2/authorize?client_id=909513527268618330&permissions=92177&scope=bot)"
    await ctx.send(embed=embed)

@bot.command()
async def ratelimits(ctx):
    await ctx.send("Since <t:1637107200>, the Bot works using a Queue System. This is,\nbecause Advertising Bots like me tend to get ratelimits.\n\nThe Queue has been made to prevent that.\nHow does it work?\n```- You send an Ad\n- It will be cached\n- It will be sent to each Server - but with a 30-second-delay```\nIf you're not happy with that, please Contact `ZeroTwo#9568`")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name="Ads | g!help"))
    print(f"Logged in as {bot.user}")

class Globalchat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, 14400, commands.BucketType.member) # Change accordingly
        

    def guild_exists(self,guildid):
        for server in chats['servers']:
            if(int(server['guildid']) == int(guildid)):
                return True
        
        return False

    def get_globalchat(self,guildid,channelid=None):
        globalChat = None
        for server in chats['servers']:
            if(int(server['guildid']) == int(guildid)):
                if channelid:
                    if int(channelid) == int(server['channelid']):
                        globalChat = server

                else:
                    globalChat = server

        return globalChat

    def get_globalchat_id(self,guildid):
        globalChat = -1
        i = 0
        for server in chats['servers']:
            if(int(server['guildid']) == int(guildid)):
                globalChat = i

            i += 1
        
        return globalChat


    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.command()
    async def config(self,ctx):
        globalchat = self.get_globalchat(ctx.guild.id)
        now = datetime.datetime.utcnow()
        embed = discord.Embed(title=ctx.guild.name,color=discord.Color.dark_green(), timestamp=now)
        embed.add_field(name="Advertising Channel",value=f"`{ctx.guild.get_channel(globalchat['channelid']).name or None}`" )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def link(self,ctx,channel:discord.TextChannel):
            server = {
                'guildid':ctx.guild.id,
                'channelid':channel.id,
                'invite': f'{(await ctx.channel.create_invite()).url}'
            }
            chats['servers'].append(server)
            with open("globalchat.json","w",encoding="utf-8") as f:
                json.dump(chats,f,indent=4)
            await channel.send(f"```Ads will now be posted here!```")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlink(self,ctx): 

        if self.guild_exists(ctx.guild.id):
            globalid = self.get_globalchat_id(ctx.guild.id)
            if globalid != -1:
                chats['servers'][globalid]['channelid'] = 0
                with open("globalchat.json","w",encoding="utf-8") as f:
                    json.dump(chats,f,indent=4)

                await ctx.send("```Your Server has been disconnected```")
                
    async def sendAll(self,message:discord.Message):
        embed2 = discord.Embed()
        embed2.set_author(name=f'Sent by {message.author} in {message.guild.name}',icon_url=message.author.avatar_url)
        msg = await message.channel.send(f"Please wait, your Ad is being posted to {len(self.bot.guilds)} Servers.\nEstimated Time remaining: {30*len(self.bot.guilds)} Seconds.\n\Read `g!ratelimits` to learn more about this change")
        for server in chats['servers']:
            guild:discord.Guild = self.bot.get_guild(int(server['guildid']))
            if guild:
                channel:discord.TextChannel = guild.get_channel(int(server['channelid']))
                if channel:
                    await channel.send(message.content)
                    await channel.send(embed=embed2)
            await asyncio.sleep(30)
        await msg.delete()
        await message.delete()

    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        if message.author.bot:
            return
        for server in chats['servers']:
                if int(message.channel.id) == int(server['channelid']):
                            
                    ratelimit = self.get_ratelimit(message)
                    if ratelimit is None:
                        await self.sendAll(message)

                    else:
                        await message.channel.send("```You are being rate limited!```")
                # The user is ratelimited
        # await self.bot.process_commands(message)
       


bot.add_cog(Globalchat(bot))
bot.run("Le Token")
