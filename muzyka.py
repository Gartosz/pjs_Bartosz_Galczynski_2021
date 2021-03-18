import discord
from discord.ext import commands

bot=commands.Bot(command_prefix='=')

class muzyka(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @bot.command(name='play', aliases=['graj'])
    async def play_command(self,ctx):
        author_voice = ctx.author.voice
        bot_voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if author_voice is not None:
            if bot_voice == None:
                await author_voice.channel.connect()
            else:
                await ctx.send('Bot już jest połączony z kanałem głosowym!')
        else:
            await ctx.send('Musisz być na kanale głosowym, aby to zrobić!')

    @bot.command(name='stop', aliases=['wyjdź'])
    async def stop_command(self,ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice != None:
            await voice.disconnect()
        else:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')

def setup(bot):
    bot.add_cog(muzyka(bot))