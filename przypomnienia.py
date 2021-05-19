import datetime
import sqlite3
import asyncio
from dateutil.parser import parse
from discord.ext import commands
from discord.ext import tasks

connection = sqlite3.connect('dates.db')

cursor = connection.cursor()
cursor2 = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS wydarzenia (id INTEGER PRIMARY KEY AUTOINCREMENT, nazwa TEXT, data DATE, opis TEXT, uid BIGINT)")
cursor2.execute("CREATE TABLE IF NOT EXISTS przypomnienia (id INTEGER, data DATE)")

bot=commands.Bot(command_prefix='=')

_loop=asyncio.get_event_loop()

async def message(ctx, msg):
    await ctx.send(msg)

def reminder_check(ctx, data1, data2):
    if data1 >= data2:
        _loop.create_task(message(ctx, 'Data przypomnienia musi być przed datą wydarzenia!'))
        return True
    elif data1 <= datetime.datetime.now():
        _loop.create_task(message(ctx, 'Data przypomnienia musi być w przyszłości!'))
        return True

    return False

class przypomnienia(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.time_check.start()

    sec = 1

    @tasks.loop(seconds=sec)
    async def time_check(self):
        await self.bot.wait_until_ready()

        if self.sec == 60:
            cursor.execute("SELECT * FROM wydarzenia")
            rows_w = cursor.fetchall()
            cursor2.execute("SELECT * FROM przypomnienia")
            rows_p = cursor2.fetchall()
            if rows_w:
                now = datetime.datetime.now()
                for row_w in rows_w:
                    if now < datetime.datetime.strptime(row_w[2], '%d.%m.%Y %H:%M'):
                        if rows_p:
                            for row_p in rows_p:
                                if row_w[0] == row_p[0] and datetime.datetime.strftime(now, '%d.%m.%Y %H:%M') == row_p[1]:
                                    user = await self.bot.fetch_user(row_w[4])
                                    msg = 'Cześć, przypominam, że ' + row_w[2] + ' odbędzie się Twoje wydarzenie o nazwie ' + row_w[1] + '.'
                                    if row_w[3]:
                                        msg += '\nOpis wydarzenia: ' + row_w[3]
                                    await user.send(msg)
                                    cursor2.execute("DELETE FROM przypomnienia WHERE id=\"" + str(row_w[0]) + "\" AND data=\"" + row_p[1] + "\"")
                                    connection.commit()

                    elif datetime.datetime.strftime(now, '%d.%m.%Y %H:%M') == row_w[2]:
                        user = await self.bot.fetch_user(row_w[4])
                        msg = 'Cześć, przypominam, że właśnie odbywa się Twoje wydarzenie o nazwie ' + row_w[1] + '.'
                        if row_w[3]:
                            msg += '\nOpis wydarzenia: ' + row_w[3]
                        await user.send(msg)
                        cursor2.execute("DELETE FROM przypomnienia WHERE id=\"" + str(row_w[0]) + "\"")
                        cursor.execute("DELETE FROM wydarzenia WHERE id=\"" + str(row_w[0]) + "\"")
                        connection.commit()

                    else:
                        user = await self.bot.fetch_user(row_w[4])
                        msg = 'Cześć, przepraszam, że nie mogłem przypomnieć Ci o Twoim wydarzeniu ' + row_w[1] + ', które odbyło się ' + row_w[2] + ' :('
                        if row_w[3]:
                            msg += '\nOpis wydarzenia: ' + row_w[3]
                        await user.send(msg)
                        cursor2.execute("DELETE FROM przypomnienia WHERE id=\"" + str(row_w[0]) + "\"")
                        cursor.execute("DELETE FROM wydarzenia WHERE id=\"" + str(row_w[0]) + "\"")
                        connection.commit()

        elif datetime.datetime.now().second == 59:
            self.sec = 60
            self.time_check.change_interval(seconds=self.sec)

    @bot.command(name='reminder',aliases=['przypomnienie','notification'])
    async def reminder_command(self, ctx, nazwa, data, godzina, *czasy):
        try:
            data_=parse(data+' '+godzina, dayfirst=True)
        except (ValueError, OverflowError):
            await ctx.send('Podano złą datę.')
            return

        if datetime.datetime.now() >= data_:
            await ctx.send('Data wydarzenia musi być w przyszłości!')
            return

        czasy_=[]
        opis=''
        i=0
        for x in czasy:
            p = ''
            if x[0]=='-':
                if x[-1] != '-':
                    i=1
                    opis += x[1:] + ' '
                else:
                    opis += x[1:-1]
            elif i==1:
                if x[-1]=='-':
                    opis += x[:-1]
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

                if reminder_check(ctx, datetime.datetime.strptime(p, '%d.%m.%Y %H:%M'), data_):
                    return

                if(p!=''):
                    czasy_.append(str(p))

        if len(czasy_) != len(set(czasy_)):
            await ctx.send('Nie możesz wielokrotnie podać takiej samej daty przypomnienia!')
            return

        cursor.execute("INSERT INTO wydarzenia (nazwa,data,opis,uid) VALUES(\"" + nazwa + "\",\"" + data_.strftime('%d.%m.%Y %H:%M') + "\",\"" + opis + "\",\"" + str(ctx.author.id) +"\")")
        for x in czasy_:
            cursor2.execute("INSERT INTO przypomnienia VALUES(\"" + str(cursor.lastrowid) + "\",\"" + x + "\")")
        connection.commit()
        msg = 'Przypomnienie wydarzenia ' + nazwa + ', które odbędzie się ' + data_.strftime('%d.%m.%Y %H:%M') + ' zostanie przypomniane'
        if czasy_:
            msg += ': ' + ', '.join(czasy_) + ' oraz o czasie rozpoczęcia.'
        else:
            msg += ' o czasie rozpoczęcia.'

        if opis:
            msg += '\nOpis: '+opis

        await ctx.send(msg)

    @reminder_command.error
    async def reminder_missing(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Brak wymaganych danych!')

    @bot.command(name='events',aliases=['wydarzenia','wyświetl_wydarzenia','show_events'])
    async def events_command(self, ctx):
        cursor.execute("SELECT * FROM wydarzenia WHERE uid=\"" + str(ctx.author.id) + "\"")
        rows_w = cursor.fetchall()
        cursor2.execute("SELECT * FROM przypomnienia")
        rows_p = cursor2.fetchall()

        user = await self.bot.fetch_user(ctx.author.id)

        if rows_w:
            msg = ''
            for row_w in rows_w:
                msg += 'ID: ' + str(row_w[0]) + ' Wydarzenie ' + row_w[1] + ' odbędzie się ' + row_w[2] + '. Opis: ' + row_w[3] + '.\nPrzypomnienia: '
                for row_p in rows_p:
                    if row_w[0] == row_p[0]:
                        msg += row_p[1] + ' '
                msg += '\n\n'

            await user.send(msg)

        else:
            await user.send('Nie masz ustawionych żadnych wydarzeń!')

    @bot.command(name='delete', aliases=['usuń_wydarzenie', 'delete_event'])
    async def delete_command(self, ctx, *, id_ ):
        cursor.execute("SELECT * FROM wydarzenia WHERE uid=\"" + str(ctx.author.id) + "\"")
        rows_w = cursor.fetchall()

        user = await self.bot.fetch_user(ctx.author.id)

        if rows_w:
            for row_w in rows_w:
                if int(row_w[0]) == int(id_):

                    msg = 'Wydarzenie ' + str(row_w[1]) + ' zostało usunięte.'
                    await user.send(msg)
                    cursor2.execute("DELETE FROM przypomnienia WHERE id=\"" + str(id_) + "\"")
                    cursor.execute("DELETE FROM wydarzenia WHERE id=\"" + str(id_) + "\"")
                    connection.commit()
                    return

            await user.send('Wydarzenie o tym id nie istnieje, bądź nie jest utworzone przez Ciebie')

        else:
            await user.send('Nie masz ustawionych żadnych wydarzeń!')

    @delete_command.error
    async def delete_missing(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Brak wymaganych danych!')

    @bot.command(name='edit', aliases=['edytuj', 'edit_event', 'edytuj_wydarzenie'])
    async def edit_command(self, ctx, id_, *edit):
        cursor.execute("SELECT * FROM wydarzenia WHERE uid=\"" + str(ctx.author.id) + "\"")
        rows_w = cursor.fetchall()

        user = await self.bot.fetch_user(ctx.author.id)

        if len(edit) < 1:
            await ctx.send('Zbyt mało parametrów!')
            return

        if rows_w:
            for row_w in rows_w:
                if int(row_w[0]) == int(id_):
                    i = 0
                    while i < len(edit):
                        if edit[i] == 'nazwa' or edit[i] == 'name':
                            if edit[i+1]:
                                cursor.execute("UPDATE wydarzenia SET nazwa = \"" + str(edit[i+1]) + "\" WHERE id = \"" + str(id_) + "\"")
                                connection.commit()
                                i += 2
                            else:
                                await ctx.send('Brak odpowiedniej ilości parametrów!')
                                return

                        elif edit[i] == 'opis' or edit[i] == 'description':
                            opis = ''
                            if edit[i + 1]:
                                if edit[i + 1][0] == '-':
                                    if edit[i + 1][-1] != '-':
                                        opis += edit[i + 1][1:]
                                        i += 1
                                        while i + 1 < len(edit) and edit[i + 1][-1] != '-':
                                            opis += ' ' + edit[i + 1]
                                            i += 1
                                        if i + 1 < len(edit) and edit[i + 1][-1] == '-':
                                            opis += ' ' +edit[i + 1][:-1]
                                        elif i + 1 < len(edit):
                                            opis += ' ' + edit[i + 1]
                                    else:
                                        opis += edit[i + 1][1:-1]
                                    i += 2
                                else:
                                    await ctx.send('Opis musi być ograniczony znakiem - !')
                                    return

                            cursor.execute("UPDATE wydarzenia SET opis = \"" + opis + "\" WHERE id = \"" + str(id_) + "\"")
                            connection.commit()

                        elif edit[i] == 'data' or edit[i] == 'date':
                            if parse(edit[i + 1] + ' ' + edit[i + 2]) and parse(edit[i + 1] + ' ' + edit[i + 2]) > datetime.datetime.now():
                                i += 3
                                cursor.execute("UPDATE wydarzenia SET data = \"" + parse(edit[i - 2] + ' ' + edit[i - 1]).strftime('%d.%m.%Y %H:%M') + "\" WHERE id = \"" + str(id_) + "\"")
                                connection.commit()
                            else:
                                await ctx.send('Podano nieprawidłową datę!')
                                return

                        elif edit[i] == 'przypomnienie' or edit[i] == 'reminder':
                            cursor2.execute("SELECT * FROM przypomnienia WHERE id = \"" + str(id_) + "\"")
                            rows_p = cursor2.fetchall()
                            rodzaje = ['zmień', 'change', 'usuń', 'remove', 'dodaj', 'add']
                            if i + 1 < len(edit) and edit[i + 1] in rodzaje:
                                typ = str(edit[i + 1])
                                i += 2
                            else:
                                await ctx.send('Brak typu operacji!')
                                return

                            dates = []

                            while i + 1 < len(edit) and parse(edit[i] + ' ' + edit[i + 1]):
                                dates.append(parse(edit[i] + ' ' + edit[i + 1], dayfirst=True))
                                i += 2

                            if not dates:
                                await ctx.send('Brak wymaganych danych!')
                                return

                            i += 1

                            if rodzaje.index(typ) < 2:
                                if not len(dates) % 2:
                                    j = 0
                                    while j < len(dates):
                                        for x in rows_p:
                                            if dates[j].strftime('%d.%m.%Y %H:%M') == x[1]:
                                                if reminder_check(ctx, dates[j + 1], datetime.datetime.strptime(row_w[2],'%d.%m.%Y %H:%M')):
                                                    return

                                                cursor2.execute("UPDATE przypomnienia SET data = \"" + dates[j + 1].strftime('%d.%m.%Y %H:%M') + "\" WHERE id = \"" + str(id_) + "\" AND data = \"" + x[1] + "\"")
                                                connection.commit()

                                                j += 2
                                                break

                                        if not j % 2:
                                            await ctx.send('Taka data nie istnieje!')
                                            return

                                else:
                                    await ctx.send('Zbyt mała ilość dat!')

                            elif rodzaje.index(typ) < 4:
                                for x in dates:
                                    j = 1
                                    for y in rows_p:
                                        if x.strftime('%d.%m.%Y %H:%M') == y[1]:
                                            cursor2.execute("DELETE FROM przypomnienia WHERE id = \"" + str(id_) + "\" AND data = \"" + y[1] + "\"")
                                            connection.commit()
                                            j = 0
                                            break
                                    if j:
                                        await ctx.send('Taka data nie istnieje!')
                                        return

                            else:
                                for x in dates:
                                    if reminder_check(ctx, x, datetime.datetime.strptime(row_w[2],'%d.%m.%Y %H:%M')):
                                        return
                                    cursor2.execute("INSERT INTO przypomnienia VALUES(\"" + str(id_) + "\",\"" + x.strftime('%d.%m.%Y %H:%M') + "\")")
                                    connection.commit()


                        else:
                            await ctx.send(edit[i] + ' nie jest poprawnym atrybutem!')
                            return
                    return

            await user.send('Wydarzenie o tym id nie istnieje, bądź nie jest utworzone przez Ciebie')
        else:
            await user.send('Nie masz ustawionych żadnych wydarzeń!')

    @edit_command.error
    async def delete_missing(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Brak wymaganych danych!')

def setup(bot):
    bot.add_cog(przypomnienia(bot))