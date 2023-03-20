import discord
from discord.ext import commands, tasks
import requests
import matplotlib.pyplot as plt
import pandas as pd


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print("we are logged in as  {0.user}".format(bot))


@bot.command("price")
async def price(ctx,keyword):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={keyword}&tsyms=USD'
    response = requests.get(url).json()
    if "Response" in response and response["Response"] == "Error":
        await ctx.channel.send(f"Sorry , {keyword} is not a valid cryptocurrency!")
    if keyword == "shib" or keyword == "SHIB":
        get_price = response
        await ctx.channel.send(f'The price of {keyword.upper()} is ${get_price["USD"]:.8f}')
    else:
        get_price = response["USD".format(".2f")]
        await ctx.channel.send(f'The price of {keyword.upper()} is ${get_price}')


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.lower() == "who is admin?":
        user_id = 556599313409638411
        user = await bot.fetch_user(user_id)
        await message.channel.send(f"{user.mention} is admin!")


@bot.command("graph")
async def graph(ctx, keyword):
    url = f'https://min-api.cryptocompare.com/data/histoday?fsym={keyword}&tsym=USD&limit=30'
    response = requests.get(url).json()
    if "Response" in response and response["Response"] == "Error":
        await ctx.channel.send(f"Sorry, {keyword} is not a valid cryptocurrency!")
    else:
        data = response["Data"]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['time'], unit='s').dt.date
        plt.plot(df['date'], df['close'])
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.title(f"{keyword.upper()} Price over Time")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('graph.png')
        await ctx.channel.send(file=discord.File('graph.png'))
        plt.clf()


def ban_check(ctx, member):
    return ctx.author.top_role > member.top_role


@bot.command("ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):

    if not ban_check(ctx, member):
        await ctx.send("Failed to ban, lacking role hierarchy.")
        return

    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"Banned {member} for reason *{reason}*")


def kick_check(ctx, member):
    return ctx.author.top_role > member.top_role


@bot.command("kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):

    if not kick_check(ctx, member):
        await ctx.send("Failed to kick, lacking role hierarchy.")
        return

    await ctx.guild.kick(member, reason=reason)
    await ctx.send(f"Kicked {member} for reason *{reason}*")

with open("token.txt","r") as f:
    t = f.read()
bot.run(t)