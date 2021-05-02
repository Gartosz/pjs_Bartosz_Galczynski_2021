import datetime
import dateparser
from discord.ext import commands

bot=commands.Bot(command_prefix='=')

class przypomnienia(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @bot.command(name='reminder',aliases=['przypomnienie','notification'])
    async def reminder_command(self,ctx,nazwa,data,godzina,*czasy):
        data_=''
        try:
            data_ = dateparser.parse(data+' '+godzina)
        except ValueError:
            await ctx.send('Podano złą datę.')
            return
        czasy_=[]

        for x in czasy:
            p = ''
            try:
                p=datetime.datetime.strptime(x,'%H:%M')
                p=data_.strftime('%d.%m.%Y ')+p.strftime('%H:%M')
            except:
                if 'm' in x:
                    p=datetime.datetime.strftime(data_-datetime.timedelta(minutes=int(x.split('m')[0])),'%d.%m.%Y %H:%M')
                elif 'h' in x:
                    p=datetime.datetime.strftime(data_-datetime.timedelta(hours=int(x.split('h')[0])),'%d.%m.%Y %H:%M')
                elif 'd' in x:
                    p=datetime.datetime.strftime(data_-datetime.timedelta(days=int(x.split('d')[0])),'%d.%m.%Y %H:%M')
                elif 'w' in x:
                    p=datetime.datetime.strftime(data_-datetime.timedelta(weeks=int(x.split('w')[0])),'%d.%m.%Y %H:%M')
                else:
                    await ctx.send("Zły format!")
                    return
            if(p!=''):
                czasy_.append(str(p))
        await ctx.send('Przypomnienie wydarzenia '+nazwa+', które odbędzie się '+str(data_)+' zostanie przypomniane: '+str(czasy_))

def setup(bot):
    bot.add_cog(przypomnienia(bot))