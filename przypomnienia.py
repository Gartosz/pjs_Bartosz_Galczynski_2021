import datetime
import dateparser
import sqlite3
from discord.ext import commands

connection = sqlite3.connect('dates.db')

cursor = connection.cursor()
cursor2=connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS wydarzenia (id INTEGER PRIMARY KEY AUTOINCREMENT,nazwa TEXT, data DATE, opis TEXT, uid BIGINT)")
cursor2.execute("CREATE TABLE IF NOT EXISTS przypomnienia (id INTEGER, data DATE)")

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
        czasy_.append(str(data_))
        opis=''
        i=0
        for x in czasy:
            p = ''
            if x[0]=='-':
                i=1
                opis+=x[1:]+' '
            elif i==1:
                if x[-1]=='-':
                    opis += x[0:-1]
                    i=0
                else:
                    opis += x+' '
            else:
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
        cursor.execute("INSERT INTO wydarzenia (nazwa,data,opis,uid) VALUES(\"" + nazwa + "\",\"" + data_.strftime('%d.%m.%Y %H:%M') + "\",\"" + opis + "\",\"" + str(ctx.author.id) +"\")")
        for x in czasy_:
            cursor2.execute("INSERT INTO przypomnienia VALUES(\"" + str(cursor.lastrowid) + "\",\"" + x + "\")")
        connection.commit()
        await ctx.send('Przypomnienie wydarzenia '+nazwa+', które odbędzie się '+str(data_)+' zostanie przypomniane: '+str(czasy_)+'. Opis: '+opis)

def setup(bot):
    bot.add_cog(przypomnienia(bot))