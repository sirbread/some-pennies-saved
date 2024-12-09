import discord
import asyncio
import random
import json
import math
import os
from discord.ext import commands

client = commands.Bot(command_prefix = ['!'], intents=discord.Intents.all())
client.remove_command('help')

dbdir = "db.json"

def admin(ctx):
    return ctx.author.id in [910711848184193084]

@client.event
async def on_ready():
    print('Bot is online')
    print(f'Running with {round(client.latency * 100)}ms ping.')
    await client.change_presence(activity=discord.Game(name="!help / !create"))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply("You have to wait {:.0f} seconds until you can do that again.".format(error.retry_after))
        #print("timer error thing happned")

@client.command(aliases=["join"])
async def create(ctx):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            await ctx.reply("You're already in the database!")
        else:
            data[str(ctx.author.id)] = {
                "money": 0,
                "bank": 0
            }
            #print("data written now")
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            await ctx.reply("You have been added!")

@client.command(aliases=["balance", "bal"])
async def money(ctx, member : discord.Member=None):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if member:
            if str(member.id) in data:
                embed = discord.Embed(
                    title="Money",
                    color=0xebca3b,
                    description=""
                )
                embed.set_thumbnail(url="https://i.ibb.co/9tFrDyq/ligmas.png")
                embed.add_field(name="**Hand:**", value=f"${data[str(member.id)]['money']}")
                embed.add_field(name="**Bank:**", value=f"${data[str(member.id)]['bank']}")
                await ctx.reply(embed=embed)
            else:
                await ctx.reply("You need to be in the database! (use `!create`)")
        else:
            if str(ctx.author.id) in data:
                embed = discord.Embed(
                    title="Money",
                    color=0xebca3b,
                    description=""
                )
                embed.set_thumbnail(url="https://i.ibb.co/9tFrDyq/ligmas.png")
                embed.add_field(name="**Hand:**", value=f"${data[str(ctx.author.id)]['money']}")
                embed.add_field(name="**Bank:**", value=f"${data[str(ctx.author.id)]['bank']}")
                await ctx.reply(embed=embed)
            else:
                await ctx.reply("The person whose money you're trying to check needs to be in the database! (they need to use `!create`)")

@client.command(aliases=["lb"])
async def leaderboard(ctx):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        allmoney = {}
        for el in data:
            allmoney[el] = (data[el]["money"] + data[el]["bank"])
        allmoney = sorted(allmoney.items(), key=lambda x: x[1], reverse=True)

        if 9 in allmoney:
            for el in range(10):
                person = int(allmoney[el][0])
                globals()['person%s' % el] = client.get_user(person)
        else:
            for el in range(len(allmoney)):
                person = int(allmoney[el][0])
                globals()['person%s' % el] = client.get_user(person)
        embed = discord.Embed(
            title="Leaderboard",
            color=0xebca3b,
            description=""
        )
        embed.set_thumbnail(url="https://i.ibb.co/9tFrDyq/ligmas.png")
        print(len(allmoney))
        if 9 in allmoney:
            for el in range(10):
                embed.add_field(name=el+1, value=f"{(globals()['person%s' % el]).mention} - {allmoney[el][1]}", inline=False)
        else:
            for el in range(len(allmoney)):
                embed.add_field(name=el+1, value=f"{(globals()['person%s' % el]).mention} - {allmoney[el][1]}", inline=False)
        await ctx.reply(embed=embed)

@client.command(aliases=["dep"])
async def deposit(ctx, amount):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            isnumber = 1
            try:
                int(amount)
            except:
                isnumber = 0
            if isnumber == 1:
                amount = int(amount)
                if data[str(ctx.author.id)]["money"] >= amount:
                    data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] - amount
                    data[str(ctx.author.id)]["bank"] = data[str(ctx.author.id)]["bank"] + amount
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                    await ctx.reply(f"${amount} was deposited!")
                else:
                    await ctx.reply("You don't have that much to deposit!")
            else:
                if amount.lower() == "all":
                    await ctx.reply(f"${data[str(ctx.author.id)]['money']} was deposited!")
                    data[str(ctx.author.id)]["bank"] = data[str(ctx.author.id)]["bank"] + data[str(ctx.author.id)]["money"]
                    data[str(ctx.author.id)]["money"] = 0
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                else:
                    await ctx.reply("You can only deposit a number or 'all'!")
        else:
            await ctx.reply("You need to be in the database! (use `!create`)")


@client.command(aliases=["with"])
async def withdrawl(ctx, amount):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            isnumber = 1
            try:
                int(amount)
            except:
                isnumber = 0
            if isnumber == 1:
                amount = int(amount)
                if data[str(ctx.author.id)]["bank"] >= amount:
                    data[str(ctx.author.id)]["bank"] = data[str(ctx.author.id)]["bank"] - amount
                    data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + amount
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                    await ctx.reply(f"${amount} was withdrawn")
                else:
                    await ctx.reply("You don't have that much to withdrawl")
            else:
                if amount.lower() == "all":
                    await ctx.reply(f"${data[str(ctx.author.id)]['bank']} was withdrawn")
                    data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + data[str(ctx.author.id)]["bank"]
                    data[str(ctx.author.id)]["bank"] = 0
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
        else:
            await ctx.reply("You need to be in the database! (use `!create`)")

@client.command(aliases=["transfer"])
async def pay(ctx, member: discord.Member = None, amount=None):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if member:
            if amount:
                try:
                    amount = int(amount) 
                except ValueError:
                    await ctx.reply("You can only transfer a number!")
                    return 
                if data[str(ctx.author.id)]["money"] >= amount:
                    data[str(ctx.author.id)]["money"] -= amount
                    data[str(member.id)]["money"] += amount
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                    await ctx.reply(f"Successfully transferred {amount} to {member.mention}!")
                else:
                    await ctx.reply("You can't afford to transfer that, or you need to transfer the money to your hand first!")
            else:
                await ctx.reply("You need to add an amount to transfer!")
        else:
            await ctx.reply("You need to ping a member to transfer money to!")



@client.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            money = random.randint(100, 300)
            data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + money
            await ctx.reply(f"You earned ${money}!")
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        else:
            await ctx.reply("You need to be in the database! (use `!create`)")

@client.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def beg(ctx):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            money = random.randint(-5, 200)
            data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + money
            if money < 0:
                money = (money - money) - money
                await ctx.reply(f"You got robbed of ${money} by a pedestrian!")
            elif money == 0:
                await ctx.reply(f"The pedestrian looked at you, then walked away. What a shame!")
            else:
                await ctx.reply(f"You got paid ${money}!")
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        else:
            await ctx.reply("You need to be in the database! (use `!create`)")

@client.command()
@commands.cooldown(1, 180, commands.BucketType.user)
async def crime(ctx):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            money = random.randint(-200, 500)
            data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + money
            if money < 0:
                money = (money - money) - money
                await ctx.reply(f"You got caught and robbed yourself of ${money}!")
            elif money == 0:
                await ctx.reply(f"You got scared by a noise, then fled!")
            else:
                await ctx.reply(f"You stole ${money}!")
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        else:
            await ctx.reply("You need to be in the database! (use `!create`)")

@client.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def rob(ctx, member : discord.Member=None):
    if member:
        with open(dbdir, "r+") as f:
            data = json.load(f)
            if str(ctx.author.id) in data:
                if str(member.id) in data:
                    gain = random.randint(0, 1)
                    if gain == 0:
                        money = random.randint(-200, 0)
                        data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + money
                        if money == 0:
                            await ctx.reply(f"You got scared by a noise, then fled!")
                        else:
                            money = (money - money) - money
                            await ctx.reply(f"You got caught and lost ${money}!")
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)
                    else:
                        money = random.randint(5, 20)
                        percentage = round((((data[str(member.id)]['money'])/100)*money))
                        data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + percentage
                        data[str(member.id)]["money"] = data[str(member.id)]["money"] - percentage
                        await ctx.reply(f"You robbed {member.mention} of ${percentage}!")
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)
                else:
                    await ctx.reply("The person you're trying to rob needs to be in the database! (they need to use `!create`)")
            else:
                await ctx.reply("You need to be in the database! (use `!create`)")
    else:
        await ctx.reply("You need to ping someone to rob!")

@client.command(aliases=["bet"])
@commands.cooldown(1, 30, commands.BucketType.user)
async def roulette(ctx, amount=None, choice=None):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(ctx.author.id) in data:
            if amount:
                try:
                    int(amount)
                except:
                    await ctx.reply("You can only bet a number!")
                amount = int(amount)
                if choice:
                    if data[str(ctx.author.id)]["money"] >= amount:
                        data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] - amount
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)
                        choosenumber = 1
                        try:
                            int(choice)
                        except:
                            choosenumber = 0
                        if choosenumber == 1:
                            if int(choice) < 0 or int(choice) > 36:
                                await ctx.reply("Your bet choice must be between 0-36.")
                            else:
                                number = random.randint(0, 36)
                                if number == 0:
                                    if int(choice) == number:
                                        data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + amount*35
                                        f.seek(0)
                                        f.truncate()
                                        json.dump(data, f, indent=4)
                                        await ctx.reply(f"The ball landed on {number} Green, you won ${amount*35}!")
                                    else:
                                        await ctx.reply(f"The ball landed on {number} Green, you lost!")
                                else:
                                    if number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
                                        color = "Red"
                                    else:
                                        color = "Black"
                                    if int(choice) == number:
                                        data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + amount*35
                                        f.seek(0)
                                        f.truncate()
                                        json.dump(data, f, indent=4)
                                        await ctx.reply(f"The ball landed on {number} {color}, you won ${amount*35}!")
                                    else:
                                        await ctx.reply(f"The ball landed on {number} {color}, you lost!")
                        else:
                            choice = choice.lower()
                            choice = choice.capitalize()
                            if choice in ["Red", "Black", "Odd", "Even"]:
                                number = random.randint(0, 36)
                                if number == 0:
                                    color = "Green"
                                    await ctx.reply(f"The ball landed on {number} {color}, you lost!")
                                else:
                                    if number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
                                        color = "Red"
                                    else:
                                        color = "Black"
                                    if choice in ["Red", "Black"]:
                                        if choice == color:
                                            data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + amount*2
                                            f.seek(0)
                                            f.truncate()
                                            json.dump(data, f, indent=4)
                                            await ctx.reply(f"The ball landed on {number} {color}, you won ${amount*2}!")
                                        else:
                                            await ctx.reply(f"The ball landed on {number} {color}, you lost!")
                                    else:
                                        if (number % 2) == 0:
                                            even = 1
                                        else:
                                            even = 0
                                        if even == 1 and choice == "Even":
                                            data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + amount*2
                                            f.seek(0)
                                            f.truncate()
                                            json.dump(data, f, indent=4)
                                            await ctx.reply(f"The ball landed on {number} {color}, you won ${amount*2}!")
                                        elif even == 0 and choice == "Odd":
                                            data[str(ctx.author.id)]["money"] = data[str(ctx.author.id)]["money"] + amount*2
                                            f.seek(0)
                                            f.truncate()
                                            json.dump(data, f, indent=4)
                                            await ctx.reply(f"The ball landed on {number} {color}, you won ${amount*2}!")
                                        else:
                                            await ctx.reply(f"The ball landed on {number} {color}, you lost!")
                            else:
                                await ctx.reply("Your bet choice must be in (Red/Black OR Odd/Even)!")
                    else:
                        await ctx.reply("You can't afford that bet!")
                else:
                    await ctx.reply("You need to select what to bet on! (Red/Black, Odd/Even, 0-36)")
            else:
                await ctx.reply("You need to select an amount to bet!")
        else:
            await ctx.reply("You need to be in the database! (use `!create`)")

@client.command(aliases=["itemshop"])
async def shop(ctx):
    embed = discord.Embed(
        title="Shop",
        color=0xebca3b,
        description=""
    )
    embed.set_thumbnail(url="https://i.ibb.co/9tFrDyq/ligmas.png")
    embed.add_field(name="This feature is being worked on! -sirbread", value="money\ndescription")
    await ctx.reply(embed=embed)

@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        color=0xebca3b,
        description=""
    )
    embed.set_thumbnail(url="https://i.ibb.co/9tFrDyq/ligmas.png")
    embed.add_field(name="Money", value="Check your, or someone else's balance\n`!money {@person (optional)}`\nNo Cooldown")
    embed.add_field(name="Create", value="Get into the database and be able to use the bot\n`!create` `!join`\nNo Cooldown")
    embed.add_field(name="Leaderboard", value="Check the top totals\n`!balance` `!lb`\nNo Cooldown")
    embed.add_field(name="Deposit", value="Put money in bank out of hand\n`!deposit {amount/all}` `!dep {amount/all}`\nNo Cooldown")
    embed.add_field(name="Withdrawl", value="Put money in hand out of bank\n`!withdrawl {amount/all}` `!with {amount/all}`\nNo Cooldown")
    embed.add_field(name="Work", value="Work for money\n`!work`\n1 Minute Cooldown")
    embed.add_field(name="Crime", value="Perform some criminal activities\n`!crime`\n3 Minute Cooldown")
    embed.add_field(name="Beg", value="Beg, on the street\n`!beg`\n2 Minute Cooldown")
    embed.add_field(name="Rob", value="Rob a fellow member\n`!rob {@person}`\n5 Minute Cooldown")
    embed.add_field(name="Roulette", value="Try your chances at some betting on roulette\n`!roulette {bet amount} {bet on (Red/Black, Odd/Even, 0-36)}` `!bet {bet amount} {bet on (Red/Black, Odd/Even, 0-36)}`\n30 Second Cooldown")
    embed.add_field(name="Transfer", value="Send someone cash\n`!transfer {@person} {amount}` `!pay {@person} {amount}`\nNo Cooldown")
    embed.add_field(name="Shop", value="Check the Item Shop\n`!shop` `!itemshop`\nNo Cooldown")
    embed.add_field(name="Help", value="This Command\n`!help`\nNo Cooldown")
    await ctx.reply(embed=embed)

@client.command()
@commands.check(admin)
async def add(ctx, member : discord.Member, amount):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(member.id) in data:
            try:
                int(amount)
            except:
                await ctx.reply("You can only give a numerical amount of money!")
            amount = int(amount)
            data[str(member.id)] = data[str(member.id)] + amount
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        await ctx.reply("The person who you're trying to add money to needs to be in the database! (they need to use `!create`)")

@client.command()
@commands.check(admin)
async def remove(ctx, member : discord.Member, amount):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(member.id) in data:
            try:
                int(amount)
            except:
                await ctx.reply("You can only remove a numerical amount of money!")
            amount = int(amount)
            data[str(member.id)] = data[str(member.id)] - amount
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        await ctx.reply("The person who you're trying to remove money from needs to be in the database! (they need to use `!create`)")

@client.command(aliases=["set"])
@commands.check(admin)
async def agag(ctx, member : discord.Member, amount):
    with open(dbdir, "r+") as f:
        data = json.load(f)
        if str(member.id) in data:
            try:
                int(amount)
            except:
                await ctx.reply("You can only set a numerical amount of money!")
            amount = int(amount)
            data[str(member.id)] = amount
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        await ctx.reply("The person whose money you're trying to set needs to be in the database! (they need to use `!create`)")

client.run("you-extremely-skibidi-rizz-token")