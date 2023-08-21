import discord
import youtube_dl
import urllib.request
import re
import validators
import asyncio
from discord.ext import commands

bot = commands.Bot(command_prefix='=')

ytdl_format_options = {
    'format': 'bestaudio/best',
    'ignoreerrors': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'}


def get_video_title(url):
    r = urllib.request.urlopen(url).read().decode()
    title = re.search(r'{"title":{"runs":\[{"text":"(.*?)"}]},"view', r).group(1)
    return title


_loop = asyncio.get_event_loop()


class muzyka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    music_queue = []
    volume = 1.0
    current = ''
    number = 0
    stop = 1
    loop = 0

    def yt_play(self, music):
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            info = ydl.extract_info(music, download=False)
            URL = info['formats'][0]['url']
        return URL

    async def playing_now(self, ctx, type, n):
        song_link = discord.Embed(
            title=type,
            description="[" + get_video_title(self.music_queue[n]) + "](" + self.music_queue[n] + ")"
        )
        await ctx.send(embed=song_link)

    def play_next(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if self.loop < 2 and self.stop:
            self.number += 1
        if len(self.music_queue) == self.number and self.loop == 1:
            self.number = 0
        if len(self.music_queue) > self.number and self.stop:
            if self.loop < 2:
                _loop.create_task(self.playing_now(ctx, 'Odtwarzanie', self.number))
            self.current = self.music_queue[self.number]
            voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                       after=lambda a: self.play_next(ctx))
            voice.source = discord.PCMVolumeTransformer(voice.source, volume=self.volume)
        if self.stop == 0:
            self.stop = 1

    @bot.command(name='play', aliases=['graj', 'p'],
                 description='Odtwarza utwór lub dodaje go do kolejki na podstawie wpisanego linku/tytułu lub kontynuuje odtwarzanie z kolejki')
    async def play_command(self, ctx, *, music_name):
        bot_voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        author_voice = ctx.author.voice

        if validators.url(music_name):
            music_url = music_name
        else:
            for i in range(len(music_name)):
                if music_name[i] == ' ':
                    x = list(music_name)
                    x[i] = '+'
                    music_name = ''.join(x)
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + music_name)
            wyniki = re.findall(r'watch\?v=(\S{11})', html.read().decode())
            music_url = ("https://www.youtube.com/watch?v=" + wyniki[0])

        if (bot_voice is None and author_voice is not None) or (bot_voice is not None and not bot_voice.is_playing()):
            _loop.create_task(self.playing_now(ctx, 'Odtwarzanie', len(self.music_queue)))
        elif bot_voice is not None:
            _loop.create_task(self.playing_now(ctx, 'Dodano do kolejki', len(self.music_queue)))

        if bot_voice is not None:
            self.music_queue.append(music_url)
            if not bot_voice.is_playing():
                self.current = music_url
                bot_voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                               after=lambda a: self.play_next(ctx))
                bot_voice.source = discord.PCMVolumeTransformer(bot_voice.source, volume=self.volume)
        elif author_voice is not None:
            self.music_queue.append(music_url)
            if bot_voice == None:
                await author_voice.channel.connect()
                self.current = music_url
                voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
                voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                           after=lambda a: self.play_next(ctx))
                voice.source = discord.PCMVolumeTransformer(voice.source, volume=self.volume)
        else:
            await ctx.send('Musisz być na kanale głosowym, aby to zrobić!')

    @play_command.error
    async def play_queue(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            bot_voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            author_voice = ctx.author.voice
            if self.music_queue[0]:
                self.current = self.music_queue[0]
                self.number = 0
                if bot_voice is not None:
                    if not bot_voice.is_playing():
                        bot_voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                                       after=lambda a: self.play_next(ctx))
                        bot_voice.source = discord.PCMVolumeTransformer(bot_voice.source, volume=self.volume)
                elif author_voice is not None:
                    if bot_voice == None:
                        await author_voice.channel.connect()
                        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
                        voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                                   after=lambda a: self.play_next(ctx))
                        voice.source = discord.PCMVolumeTransformer(voice.source, volume=self.volume)
                else:
                    await ctx.send('Musisz być na kanale głosowym, aby to zrobić!')
            else:
                await ctx.send("Brak muzyki w kolejce!")

    @bot.command(name='quit', aliases=['wyjdź'], description='Odłącza bota od serwera głosowego')
    async def quit_command(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice != None:
            await voice.disconnect()
        else:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')

    @bot.command(name='pause', aliases=['pauza'], description='Pauzuje aktualny utwór')
    async def pause_command(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            voice.pause()
        else:
            await ctx.send('Obecnie nic nie jest odtwarzane!')

    @bot.command(name='resume', aliases=['wznów'], description='Wznawia zpauzowany utwór')
    async def resume_command(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_paused():
            voice.resume()
        else:
            await ctx.send('Aby wznowić musisz najpierw zapauzować!')

    @bot.command(name='stop', aliases=['zatrzymaj'], description='Zatrzymuje odtwarzanie')
    async def stop_command(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            self.stop = 0
            voice.stop()
            if self.loop == 2:
                self.number += 1
        else:
            await ctx.send('Obecnie nic nie jest odtwarzane!')

    @bot.command(name='move', aliases=['przesuń', 'm'], description='Przesuwa do podanego czasu')
    async def move_command(self, ctx, *, time):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        ffmpeg_options_ = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -ss {}'.format(time)}
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            if self.loop != 2:
                self.number -= 1
            self.stop = 0
            voice.stop()
            voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options_),
                       after=lambda a: self.play_next(ctx))
            voice.source = discord.PCMVolumeTransformer(voice.source, volume=self.volume)
        else:
            await ctx.send('Obecnie nic nie jest odtwarzane!')

    @bot.command(name='volume', aliases=['głośność', 'v'], description='Zmienia głośność')
    async def volume_command(self, ctx, *, vol):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            self.volume = int(vol) / 100
            voice.source.volume = self.volume
        else:
            await ctx.send('Obecnie nic nie jest odtwarzane!')

    @bot.command(name='skip', aliases=['pomiń', 's'], description='Pomija aktualny utwór')
    async def skip_command(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send('Bot nie jest połączony z żadnym kanałem głosowym!')
        elif voice.is_playing():
            if self.loop == 2:
                self.number += 1
            voice.stop()
        else:
            await ctx.send('Obecnie nic nie jest odtwarzane!')

    @bot.command(name='queue', aliases=['kolejka', 'q'], description='Wyświetla zawartosć kolejki')
    async def queue_command(self, ctx):
        titles = 'Kolejka:\n'
        for x in range(len(self.music_queue)):
            titles += (str(x + 1) + '. ' + get_video_title(self.music_queue[x]))
            if x == self.number:
                titles += (" <- teraz odtwarzane")
            titles += ('\n')

        if titles == 'Kolejka:\n':
            titles = 'Nic tu nie ma :('

        await ctx.send(titles)

    @bot.command(name='remove', aliases=['usuń', 'r'], description='Usuwa piosenkę od podanym numerze z kolejki')
    async def remove_command(self, ctx, n: int):
        if len(self.music_queue) >= n:
            del self.music_queue[n - 1]
            if self.number >= n - 1:
                self.number -= 1
            await ctx.send('Usunięto pozycję nr ' + str(n) + '.')
        else:
            await ctx.send('Kolejka nie zawiera utworu o takim numerze.')

    @bot.command(name='clear', aliases=['wyczyść', 'c'], description='Czyści kolejkę')
    async def clear_command(self, ctx):
        self.music_queue.clear()
        self.number = -1
        await ctx.send('Wyczyszczono kolejkę odtwarzania.')

    @bot.command(name='goto', aliases=['g', 'zmień'], description='Przechodzi do utworu o podanym numerze')
    async def goto_command(self, ctx, n: int):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        author_voice = ctx.author.voice
        if self.music_queue[n - 1]:
            if voice.is_playing() and voice is not None:
                voice.stop()
            self.number = n - 1
            self.stop = 0
            self.current = self.music_queue[self.number]
            if voice is not None:
                voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                           after=lambda a: self.play_next(ctx))
                voice.source = discord.PCMVolumeTransformer(voice.source, volume=self.volume)
            elif author_voice is not None:
                await author_voice.channel.connect()
                bot_voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
                bot_voice.play(discord.FFmpegPCMAudio(self.yt_play(self.current), **ffmpeg_options),
                               after=lambda a: self.play_next(ctx))
                bot_voice.source = discord.PCMVolumeTransformer(bot_voice.source, volume=self.volume)
            else:
                await ctx.send('Musisz być na kanale głosowym, aby to zrobić!')
        else:
            await ctx.send('Brak utworu o takim numerze!')

    @bot.command(name='loop', aliases=['zapętl', 'l'], description='Zmienia ustawienia zapętlania')
    async def loop_command(self, ctx, *, option):
        if option == 'stop':
            self.loop = 0
            await ctx.send('Zapętlanie wyłączone.')
        elif option == 'one' or option == 'jedną':
            self.loop = 2
            await ctx.send('Zapętlanie obecnego utworu.')
        elif option == 'all' or option == 'wszystkie':
            self.loop = 1
            await ctx.send('Zapętlanie wszystkich utworów w kolejce')

    @loop_command.error
    async def loop_(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            self.loop += 1
            if self.loop == 3:
                self.loop = 0
            communicats = ['Zapętlanie wyłączone.', 'Zapętlanie wszystkich utworów w kolejce',
                           'Zapętlanie obecnego utworu.']
            await ctx.send(communicats[self.loop])


def setup(bot):
    bot.add_cog(muzyka(bot))
