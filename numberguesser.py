import random
import asyncio
from discord.ext import commands


class NumberGuesser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='guess_the_number', aliases=['zgadnij_liczbę', 'zgadywanie'],
                 description='Umożliwia zgadnięcie wylosowanej liczby całkowitej od 0 do 10, bądź z podanego zakresu')
    async def guess(self, ctx, a=0, b=10):

        await ctx.send("Musisz zgadnąć liczbę z zakresu od " + str(a) + " do " + str(b))

        x = random.randint(a, b)
        number = a - 1
        i = 0
        while (number != x):
            if (number > b or number < a) and i != 0 and t:
                await ctx.send("Podałeś liczbę spoza zakresu!")
            elif i != 0 and t:
                await ctx.send("Nie zgadłeś/aś")
            i += 1
            t = 1
            try:
                message = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.send('Niestety, skończył ci się czas :(')
                return
            try:
                number = int(message.content)
            except ValueError:
                await ctx.send("Podałeś zły typ danych")
                i -= 1
                t = 0

        await ctx.send("Zgadłeś/aś liczbę " + str(x) + " po " + str(i) + " próbach.")

    @guess.error
    async def guess_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Podałeś zły typ danych")


def setup(bot):
    bot.add_cog(NumberGuesser(bot))
