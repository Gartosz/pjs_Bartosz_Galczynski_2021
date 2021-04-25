import os
import traceback
from discord.ext import commands
from dotenv import load_dotenv

extensions = ['muzyka','cointoss','guessthenumber','tictactoe']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot=commands.Bot(command_prefix='=')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} jest aktywny na serwerze:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

if __name__ == '__main__':
    for x in extensions:
        try:
            bot.load_extension(x)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {x}.')
            traceback.print_exc()

bot.run(TOKEN, bot=True, reconnect=True)