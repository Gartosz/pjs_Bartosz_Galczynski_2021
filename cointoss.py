import random
from discord.ext import commands



class cointoss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cointoss', aliases=['moneta'], description='Losuje reszkę lub orła')
    async def coin_toss(self, ctx):
        x = ['Wypadła reszka', 'Wypadł orzeł']
        side = random.choice(x)
        await ctx.send(side)


def setup(bot):
    bot.add_cog(cointoss(bot))
