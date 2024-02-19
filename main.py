import discord
import os
from keepalive import keep_alive
from discord.ext import commands
from dotenv import load_dotenv
import pymongo
import random

load_dotenv()
#play  ow) chance to get money (eboy) or get banned (chat ban, low skill level, afk)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='iw ', intents=intents)

conn = os.getenv('CONN')
client = pymongo.MongoClient(conn)
db = client["cherry"]
col = db["users"]
ongoing = []
game = {}


def createembed(name, avatar, type):
    if type == "bj":
        title = "{}'s blackjack game".format(name)
        description = "Type 'h' to hit (take another card) or type 's' to stand"
        color = 0x7851a9
        footer = "nice gambling addiction"

    elif type == "sd":
        title = "{}'s sugar daddy".format(name)
        description = "He has a profile picture of a old white guy"
        color = 0x800000
        footer = "he looks kinda musty"

    elif type == 'pc':
        title = "{}'s wallet".format(name)
        description = "you hear clinking noises as coins knock against your vape"
        color = 0xAA336A
        footer = "maybe its time to stop spending money on skins"

    elif type == 'ml':
        title = "{}'s MLBB game result".format(name)
        description = "welcome to mobile legends!!!"
        color = 0x1929ff
        footer = "five seconds till the enemy reaches the battlefield, smash them!"

    elif type == 'valo':
        title = "{}'s VALORANT game result".format(name)
        description = "match found (dun dun dun dun dun)"
        color = 0x820812
        footer = "*rocket engine noises from the viper's mic*"

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name=name, icon_url=avatar)
    embed.set_footer(text=footer)
    return embed


def calctotal(cards):
    total = 0
    one = 0
    for card in cards:
        if card.isdigit():
            total += int(card)
        elif card != 'A':
            total += 10
        else:
            one += 1

    for i in range(one):
        if (total + 11) <= 21:
            total += 11
        else:
            total += 1

    return total


def checkwin(dcards, pcards):
    dtotal = calctotal(dcards)
    ptotal = calctotal(pcards)

    if dtotal == ptotal:
        return "Draw"
    elif dtotal == 21:
        return "Uncle Wins"
    elif ptotal == 21:
        return "You Win"
    elif dtotal > ptotal and dtotal < 21:
        return "Uncle Wins"
    elif ptotal > dtotal and ptotal < 21:
        return "You Win"
    elif dtotal > 21:
        return "You Win"
    elif ptotal > 21:
        return "Uncle Wins"


def cardstr(cards):
    result = ''
    for card in cards:
        result += card + ' '
    return result


def pickcard(cards=[]):
    card = random.randint(1, 13)
    if card == 1:
        card = 'A'
    elif card == 11:
        card = 'J'
    elif card == 12:
        card = 'Q'
    elif card == 13:
        card = 'K'

    return str(card)


def regis(discid):
    check = col.find_one({'discid': discid})
    if check == None:
        money = 0
        toadd = {'discid': discid, 'money': money}

        col.insert_one(toadd)
        print("{} registered".format(discid))


def earnmoney(money, query, author):
    currentbal = query["money"]
    newbal = currentbal + money
    toadd = {"$set": {"money": newbal}}
    col.update_one({'discid': author}, toadd)

    return newbal


@bot.command(name='bj', help='iw bj <money>')
async def bj(ctx, money):
    author = int(ctx.message.author.id)
    check = col.find_one({'discid': author})
    money = int(money)
    if check != None and money > 0:
        name = ctx.message.author.name
        avatar = ctx.message.author.avatar

        if check["money"] < money:
            await ctx.message.channel.send("{}, you are broke.".format(
                ctx.author.mention))
        else:

            embed = createembed(name, avatar, 'bj')

            dealercards = [pickcard(), pickcard()]
            dtotal = calctotal(dealercards)
            playercards = [pickcard(), pickcard()]
            total = calctotal(playercards)
            end = False

            if dtotal == 21:
                if total != 21:
                    end = True
                    money = -1 * money
                    result = "Uncle Wins"
                else:
                    end = True
                    result = "Draw"
                    money = 0
            if total == 21:
                end = True
                result = "You Win"

            if end:
                dcardstr = cardstr(dealercards)
                embed.add_field(name="Uncle's cards",
                                value=dcardstr,
                                inline=False)
                embed.add_field(name="Total", value=dtotal, inline=False)

                pcardstr = cardstr(playercards)
                embed.add_field(name="{}'s cards".format(name),
                                value=pcardstr,
                                inline=False)
                embed.add_field(name="Total", value=total, inline=False)

                embed.add_field(name=result, value='', inline=False)
                earnmoney(money, check, author)

            else:
                embed.add_field(name="Uncle's cards",
                                value="? ?",
                                inline=False)
                embed.add_field(name="Total", value="?", inline=False)

                pcardstr = cardstr(playercards)
                embed.add_field(name="{}'s cards".format(name),
                                value=pcardstr,
                                inline=False)
                embed.add_field(name="Total", value=total, inline=False)

                game[author] = [avatar, dealercards, playercards, money]
                ongoing.append(author)
            await ctx.message.channel.send(embed=embed)
    elif check == None:
        await ctx.message.channel.send(
            "{}, please register with 'iw register'!".format(
                ctx.author.mention))
    else:
        await ctx.message.channel.send("{} what are you doing".format(
            ctx.author.mention))


@bot.command(name='register',
             help="Creates a profile for you if you don't already have one")
async def register(ctx):
    discid = int(ctx.author.id)
    regis(discid)
    await ctx.message.channel.send("{} registered!".format(ctx.author.mention))


@bot.command(name='sugardaddy', help="get monies!!!")
async def sugardaddy(ctx):
    author = int(ctx.author.id)
    check = col.find_one({'discid': author})
    if check != None:
        choice = random.randint(1, 10)
        embed = createembed(ctx.author.name, ctx.author.avatar, 'sd')
        if choice >= 1 and choice <= 5:
            newbal = earnmoney(500, check, author)

            embed.add_field(name="Success!",
                            value="you lick his toes and get $500",
                            inline=False)
            embed.add_field(name="Current Balance", value=newbal, inline=False)

        elif choice <= 8:
            currentbal = check["money"]

            embed.add_field(
                name="fail...",
                value="you accidentally mention your da gege and he blocks you",
                inline=False)
            embed.add_field(name="Current Balance",
                            value=currentbal,
                            inline=False)

        elif choice <= 10:
            newbal = earnmoney(1000, check, author)
            embed.add_field(
                name="Success!",
                value=
                "you do his favourite cosplay and he gives you $1000 as a treat",
                inline=False)
            embed.add_field(name="Current Balance", value=newbal, inline=False)

        await ctx.message.channel.send(embed=embed)

    else:
        await ctx.message.channel.send(
            "{}, please register with 'iw register'!".format(
                ctx.author.mention))


@bot.command(name='play', help="iw play <ml/valo>")
async def play(ctx, game):
    author = int(ctx.author.id)
    check = col.find_one({'discid': author})
    george = False
    if game == "ml":
        values = [
            "an yp eboy is impressed by ur angela and sends u $500 to spend on skins",
            "you go 0/20/0 as floryn and get reported for low skill level",
            "you carry as odette and a lancelot main falls in love with u and gives u $1000"
        ]

    elif game == "valo":
        if author == 591859813852643342:
            embed = createembed(ctx.author.name, ctx.author.avatar, game)
            newbal = earnmoney(100 * -1, check, author)

            embed.add_field(name="george",
                            value='george plays shit game',
                            inline=False)
            embed.add_field(name="Current Balance", value=newbal, inline=False)
            george = True
            await ctx.message.channel.send(embed=embed)
        else:
            values = [
                "you pocket sage for a jett n meow for him, earning u $500",
                "u encounter another ecouple n the gf reports u for throwing",
                "the jett aces when u promise him ur snap if he clutches n u get $1000"
            ]

    if check != None:
        if george == False:
            choice = random.randint(1, 10)
            embed = createembed(ctx.author.name, ctx.author.avatar, game)
            if choice >= 1 and choice <= 5:
                newbal = earnmoney(500, check, author)

                embed.add_field(name="Success!", value=values[0], inline=False)
                embed.add_field(name="Current Balance",
                                value=newbal,
                                inline=False)

            elif choice <= 8:
                currentbal = check["money"]

                embed.add_field(name="fail...", value=values[1], inline=False)
                embed.add_field(name="Current Balance",
                                value=currentbal,
                                inline=False)

            elif choice <= 10:
                newbal = earnmoney(1000, check, author)
                embed.add_field(name="Success!", value=values[2], inline=False)
                embed.add_field(name="Current Balance",
                                value=newbal,
                                inline=False)

            await ctx.message.channel.send(embed=embed)

    else:
        await ctx.message.channel.send(
            "{}, please register with 'iw register'!".format(
                ctx.author.mention))


@bot.command(name='invite', help='Sends invite link')
async def invite(ctx):

    await ctx.message.channel.send(
        "https://discord.com/api/oauth2/authorize?client_id=1055044229132455936&permissions=274877974528&scope=bot"
    )


@bot.command(name='wallet', help='checks how much money you have')
async def wallet(ctx):
    author = int(ctx.author.id)
    check = col.find_one({'discid': author})
    if check != None:
        embed = createembed(ctx.author.name, ctx.author.avatar, 'pc')
        embed.add_field(name="Current Balance",
                        value=check["money"],
                        inline=False)

        await ctx.message.channel.send(embed=embed)
    else:
        await ctx.message.channel.send(
            "{}, please register with 'iw register'!".format(
                ctx.author.mention))


@bot.command(name='donate', help="iw donate <mention user> <amt>")
async def donate(ctx, receiver, money):
    author = int(ctx.author.id)
    check = col.find_one({'discid': author})
    money = int(money)
    if check != None:

        if check["money"] < money:
            await ctx.message.channel.send("{}, you are broke.".format(
                ctx.author.mention))
        else:
            receiverid = int(receiver[2:-1])
            taker = col.find_one({'discid': receiverid})
            if taker == None:
                await ctx.message.channel.send("{} who is {}".format(
                    ctx.author.mention, receiver))
            else:
                earnmoney(money * -1, check, author)
                earnmoney(money, taker, receiverid)
                await ctx.message.channel.send("{} give {} {} alr".format(
                    ctx.author.mention, receiver, money))

    else:
        await ctx.message.channel.send(
            "{}, please register with 'iw register'!".format(
                ctx.author.mention))


@bot.event
async def on_message(message):
    if message.author == client.user:
        return
    if int(message.author.id) in ongoing:
        if message.content == "h":

            set = game[int(message.author.id)]
            name = message.author.name

            embed = createembed(name, set[0], 'bj')
            dealercards = set[1]
            playercards = set[2]
            money = set[3]
            card = pickcard(playercards)
            result = ''

            playercards.append(card)
            total = calctotal(playercards)

            if total >= 21:
                result = checkwin(dealercards, playercards)
                if result == "Uncle Wins":
                    money = money * -1
                elif result == "Draw":
                    money = 0

                dtotal = calctotal(dealercards)
                dcardstr = cardstr(dealercards)
                embed.add_field(name="Uncle's cards",
                                value=dcardstr,
                                inline=False)
                embed.add_field(name="Total", value=dtotal, inline=False)

                check = col.find_one({'discid': int(message.author.id)})
                earnmoney(money, check, int(message.author.id))
                ongoing.remove(int(message.author.id))
                game.pop(int(message.author.id))
            elif len(playercards) == 5:
                result = "You Win"
                dtotal = calctotal(dealercards)
                dcardstr = cardstr(dealercards)
                embed.add_field(name="Uncle's cards",
                                value=dcardstr,
                                inline=False)
                embed.add_field(name="Total", value=dtotal, inline=False)

                check = col.find_one({'discid': int(message.author.id)})
                earnmoney(money, check, int(message.author.id))
                ongoing.remove(int(message.author.id))
                game.pop(int(message.author.id))
            else:
                embed.add_field(name="Uncle's cards",
                                value="? ?",
                                inline=False)
                embed.add_field(name="Total", value="?", inline=False)
                check = col.find_one({'discid': int(message.author.id)})

            pcardstr = cardstr(playercards)
            embed.add_field(name="{}'s cards".format(name),
                            value=pcardstr,
                            inline=False)
            embed.add_field(name="Total", value=total, inline=False)
            embed.add_field(name=result, value='', inline=False)

            await message.channel.send(embed=embed)

        if message.content == "s":

            set = game[int(message.author.id)]
            name = message.author.name
            embed = createembed(name, set[0], 'bj')
            dealercards = set[1]
            playercards = set[2]
            money = set[3]

            dtotal = calctotal(dealercards)

            while dtotal < 18:
                card = pickcard(dealercards)
                dealercards.append(card)
                dtotal = calctotal(dealercards)

            result = checkwin(dealercards, playercards)
            if result == "Uncle Wins":
                money = money * -1
            elif result == "Draw":
                money = 0

            dcardstr = cardstr(dealercards)
            embed.add_field(name="Uncle's cards", value=dcardstr, inline=False)
            embed.add_field(name="Total", value=dtotal, inline=False)

            total = calctotal(playercards)
            pcardstr = cardstr(playercards)
            embed.add_field(name="{}'s cards".format(name),
                            value=pcardstr,
                            inline=False)
            embed.add_field(name="Total", value=total, inline=False)

            embed.add_field(name=result, value='', inline=False)

            check = col.find_one({'discid': int(message.author.id)})
            earnmoney(money, check, int(message.author.id))
            ongoing.remove(int(message.author.id))
            game.pop(int(message.author.id))
            await message.channel.send(embed=embed)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print('We have logged in as {}'.format(bot.user))


keep_alive()
bot.run(os.getenv('TOKEN'))
