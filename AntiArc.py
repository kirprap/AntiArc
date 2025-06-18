import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
from dotenv import dotenv_values
config = dotenv_values(".env")
print("Config from .env:", config)


if TOKEN is None:
    print("ERROR: DISCORD_TOKEN not found in environment variables!")
    exit()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_PATTERN = re.compile(r"archit", re.IGNORECASE)
strikes = {}

async def check_and_kick(member: discord.Member, channel: discord.TextChannel = None, *, reason="Matched forbidden name"):
    if TARGET_PATTERN.search(member.name):
        if channel:
            await channel.send("WHO LET ARCHIT JOIN")
        await member.kick(reason=reason)
        print(f"Kicked {member} for name match")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    # Find a text channel the bot can send messages in
    default_channel = None
    for channel in member.guild.text_channels:
        if channel.permissions_for(member.guild.me).send_messages:
            default_channel = channel
            break

    await check_and_kick(member, channel=default_channel, reason="Username contains 'archit'")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if TARGET_PATTERN.search(message.content):
        user_id = str(message.author.id)
        strikes[user_id] = strikes.get(user_id, 0) + 1
        strike_count = strikes[user_id]

        await message.channel.send(f"He who shall not be named (strikes: {strike_count})")

        if strike_count >= 3:
            try:
                await message.author.kick(reason="Reached 3 strikes for using forbidden word 'archit'")
                await message.channel.send(f"{message.author.mention} has been kicked for repeated violations.")
                print(f"Kicked {message.author} after 3 strikes.")
            except Exception as e:
                print(f"Failed to kick {message.author}: {e}")
        return

    await bot.process_commands(message)

@bot.command(name="resetstrikes")
@commands.is_owner()
async def reset_strikes(ctx):
    strikes.clear()
    await ctx.send("All strikes have been reset.")

bot.run(TOKEN)
