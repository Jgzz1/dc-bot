import discord
from discord.ext import commands
import os
import asyncio

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store warnings
warnings = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="over the server"
    ))

# --- MODERATION COMMANDS ---

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member.mention}. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.mention}. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, username):
    banned_users = [entry async for entry in ctx.guild.bans()]
    for entry in banned_users:
        if entry.user.name == username:
            await ctx.guild.unban(entry.user)
            await ctx.send(f"Unbanned {entry.user.mention}")
            return
    await ctx.send(f"User '{username}' not found in ban list.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)
    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"Muted {member.mention}. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"Unmuted {member.mention}")
    else:
        await ctx.send(f"{member.mention} is not muted.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("Please provide a number between 1 and 100.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Deleted {len(deleted) - 1} messages.")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    user_id = str(member.id)
    if user_id not in warnings:
        warnings[user_id] = []
    warnings[user_id].append(reason)
    count = len(warnings[user_id])
    await ctx.send(f"Warned {member.mention} (Warning #{count}). Reason: {reason}")
    try:
        await member.send(f"You have been warned in **{ctx.guild.name}**.\nReason: {reason}\nTotal warnings: {count}")
    except:
        pass

@bot.command()
async def warnings_list(ctx, member: discord.Member):
    user_id = str(member.id)
    if user_id not in warnings or not warnings[user_id]:
        await ctx.send(f"{member.mention} has no warnings.")
        return
    warn_list = "\n".join([f"{i+1}. {w}" for i, w in enumerate(warnings[user_id])])
    await ctx.send(f"Warnings for {member.mention}:\n{warn_list}")

# --- VOICE / AFK COMMANDS ---

@bot.group()
async def afk(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Use `!afk join` or `!afk leave`")

@afk.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel first!")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(f"Joined **{channel.name}** and will stay there.")

@afk.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

# --- UTILITY ---

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency: {latency}ms")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, color=0x7F77DD)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Channels", value=len(guild.channels))
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Owner", value=guild.owner.mention)
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument. Usage: `!{ctx.command.name} <arguments>`")

# Run the bot
bot.run(os.environ.get("MTUwMTA0ODA5NTM4NTk3NzAyMg.GA4L3a.tnZKW7Rcrp7yXQ4mtCbLhIviBJJF82KA7LNwXI"))
