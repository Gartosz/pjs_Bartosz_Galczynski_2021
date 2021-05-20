import random
import copy
import asyncio
from discord.ext import commands

bot=commands.Bot(command_prefix='=')

class plansza():
    def __init__(self):
        self.moves_count=0
        self.fields = [[' . ' for y in range(3)] for x in range(3)]

    def print(self):
        p = '```'
        i=1
        for x in range(3):
            for y in range(3):
                if self.fields[x][y] == ' . ':
                    if i==1:
                        p +='(' + str(i) + ')'
                    else:
                        p += '(' + str(i) + ')'
                else:
                    p+=''+self.fields[x][y]
                if y!=2:
                    p+=' | '
                i+=1
            if x!=2:
                p+='\n'+8*'- '+'\n'
        p+='\n```'
        return p

    def winner(self):
        if self.moves_count<5:
            return None
        else:
            for x in range(3):
                r = set(self.fields[x])
                if len(r)==1:
                    r_ = r.pop()
                    if r_ != ' . ':
                        return r_

            for x in range(3):
                c = set()
                for y in range(3):
                    c.add(self.fields[y][x])
                if len(c)==1:
                    c_ = c.pop()
                    if c_ != ' . ':
                        return c_

            d = {self.fields[0][0], self.fields[1][1], self.fields[2][2]}
            if len(d) == 1:
                d_ = d.pop()
                if d_ != ' . ':
                    return d_

            d = {self.fields[0][2], self.fields[1][1], self.fields[2][0]}
            if len(d) == 1:
                d_ = d.pop()
                if d_ != ' . ':
                    return d_
            return None

    def is_empty(self,x,y):
        if self.fields[x][y]==' . ':
            return True
        return False

    def move(self,x,y,player):
        if self.is_empty(x,y):
            self.fields[x][y]=player
            self.moves_count+=1

    def available_moves(self):
        moves=[]
        for x in range(3):
            for y in range(3):
                if self.fields[x][y] == ' . ':
                  moves.append([x,y])
        return moves

def bot_1(board,bot):
    moves = board.available_moves()
    n = random.randint(0,len(moves)-1)
    board.move(moves[n][0], moves[n][1], bot)

def bot_2(board, bot):
    moves = board.available_moves()
    for x in moves:
        new = copy.deepcopy(board)
        new.move(x[0], x[1], bot)

        if new.winner() == bot:
            board.move(x[0], x[1], bot)
            return

    n = random.randint(0, len(moves) - 1)
    board.move(moves[n][0], moves[n][1], bot)

def bot_3(board,bot,player):
    moves = board.available_moves()
    for x in moves:
        new = copy.deepcopy(board)
        new.move(x[0], x[1], bot)

        if new.winner() == bot:
            board.move(x[0], x[1], bot)
            return

    for x in moves:
        new = copy.deepcopy(board)
        new.move(x[0], x[1], player)

        if new.winner() == player:
            board.move(x[0], x[1], bot)
            return

    n = random.randint(0,len(moves)-1)
    board.move(moves[n][0], moves[n][1], bot)

class tictactoe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(name='tictactoe',aliases=['kółkokrzyżyk','ttt','kk'], description='Uruchamia grę w kółko i krzyżyk o podanym poziomie trudności 1,2 lub 3')
    async def start(self,ctx,lvl=1):
        if lvl<1 or lvl>3:
            await ctx.send('Nie ma takiego poziomu trudności')
            return
        starts=random.randint(0,1)
        board = plansza()

        if starts:
            player = ' x '
            bot = ' o '
        else:
            player = ' o '
            bot = ' x '

        await ctx.send(board.print())
        for i in range(9):
            if (not i % 2 and starts == 1) or (i % 2 and starts == 0):
                while True:
                    await ctx.send('Podaj numer pola')

                    try:
                        message = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=20.0)
                    except asyncio.TimeoutError:
                        await ctx.send('Niestety, skończył ci się czas :(')
                        return
                    try:
                        pole = int(message.content)
                    except ValueError:
                        await ctx.send("Podałeś zły typ danych")
                        continue

                    pole -= 1
                    x = pole // 3
                    y = pole % 3
                    if board.is_empty(x, y):
                        board.move(x, y, player)
                        break
                    else:
                        await ctx.send("Nie można ruszyć się na to pole!")
            else:
                if lvl == 1:
                    bot_1(board, bot)
                elif lvl == 2:
                    bot_2(board, bot)
                elif lvl == 3:
                    bot_3(board, bot, player)
            await ctx.send(board.print())
            if board.winner() and board.winner()==player:
                await ctx.send('Wygrałeś!')
                break
            elif board.winner():
                await ctx.send('Przegrałeś!')
                break
        if not board.winner():
            await ctx.send('Remis')

    @start.error
    async def start_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Poziom trudności musi być liczbą całkowitą od 1 do 3!")

def setup(bot):
    bot.add_cog(tictactoe(bot))