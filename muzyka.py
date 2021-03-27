import discord
import youtube_dl
import urllib.request
import re
from discord.ext import commands

bot=commands.Bot(command_prefix='=')

ytdl_format_options = {
    'format': 'bestaudio/best',
    'ignoreerrors': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'}

class muzyka(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @bot.command(name='play', aliases=['graj'])
    async def play_command(self,ctx,*, music_name):
        author_voice = ctx.author.voice
        bot_voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        for i in range(len(music_name)):
            if music_name[i]==' ':
                x=list(music_name)
                x[i]='+'
                music_name=''.join(x)
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + music_name)
        wyniki = re.findall(r'watch\?v=(\S{11})', html.read().decode())
        music_url=("https://www.youtube.com/watch?v=" + wyniki[0])

        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            info = ydl.extract_info(music_url, download=False)
            URL = info['formats'][0]['url']

        if bot_voice != None:
            bot_voice.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))
        elif author_voice is not None:
            if bot_voice == None:
                await author_voice.channel.connect()
                voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
                voice.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))

            else:
                await ctx.send('Bot już jest połączony z kanałem głosowym!')
        else:
            await ctx.send('Musisz być na kanale głosowym, aby to zrobić!')

    @bot.command(name='quit', aliases=['wyjdź'])
    async def quit_command(self,ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice != None:
            await voice.disconnect()
        else:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')

    @bot.command(name='pause', aliases=['pauza'])
    async def pause_command(self,ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            voice.pause()
        else:
            await ctx.send('Obecnie nic nie jest odtwarzane!')

    @bot.command(name='resume', aliases=['wznów'])
    async def resume_command(self,ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_paused():
            voice.resume()
        else:
            await ctx.send('Aby wznowić musisz najpierw zapauzować!')

    @bot.command(name='stop', aliases=['zatrzymaj'])
    async def stop_command(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            voice.stop()
        else:
            await ctx.send('Aby zatrzymać odtwarzanie, coś musi grać!')

def setup(bot):
    bot.add_cog(muzyka(bot))