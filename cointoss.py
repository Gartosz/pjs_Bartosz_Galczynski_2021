import random
from discord.ext import commands

bot=commands.Bot(command_prefix='=')

class cointoss(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @bot.command(name='cointoss', aliases=['moneta'])
    async def coin_toss(self, ctx):
        x = ['Wypadła reszka','Wypadł orzeł']
        side = random.choice(x)
        await ctx.send(side)

def setup(bot):
    bot.add_cog(cointoss(bot))
