from os import getenv
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from BotData import BotData

if __name__ == '__main__':
    load_dotenv()
    bot = BotData(client=commands.Bot(command_prefix='=', intents=Intents.default()),
                  extensions=['muzyka', 'cointoss', 'guessthenumber', 'tictactoe', 'przypomnienia'],
                  _token=getenv('DISCORD_TOKEN'),
                  guild=getenv('DISCORD_GUILD')
                  )
    bot.start()
