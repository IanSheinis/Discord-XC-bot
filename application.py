import os
import discord
import settings
import datetime
from discord.ext import commands

#setup bot
logger = settings.logging.getLogger("bot")
intents: discord.Intents = discord.Intents.all()
bot: commands.Bot = commands.Bot(command_prefix="!",intents=intents)

def run() -> None:
    
    bot.run(settings.DISCORD_API_SECRET,root_logger=True)
  
##commands
@bot.event
async def on_ready() -> None:
    #Cogs
    
    for cog_file in settings.COGS_DIR.glob("*.py"):
        if cog_file.name!= "__init__.py":
            await bot.load_extension(f"cogs.{cog_file.name[:-3]}")
    logger.info(f"User: {bot.user} (ID: {bot.user.id})")

#Load cogs
@bot.command()
async def load(ctx, cog: str) -> None:
    try:
      await bot.load_extension(f"cogs.{cog.lower()}")
      await ctx.send("Cog loaded")
    except commands.ExtensionAlreadyLoaded:
      await ctx.send("Cog already loaded")
    except commands.ExtensionNotFound:
      await ctx.send("Not a cog")
@load.error
async def loadError(ctx, error) -> None:
    await ctx.send("Put a cog after command")

#Reload cogs
@bot.command()
async def reload(ctx, cog: str) -> None:
    await bot.reload_extension(f"cogs.{cog.lower()}")
    await ctx.send("Cog reloaded")
@reload.error
async def reloadError(ctx, error) -> None:
    await ctx.send("Not a cog")

#Unload cogs
@bot.command()
async def unload(ctx, cog: str) -> None:
  try:
    await bot.unload_extension(f"cogs.{cog.lower()}")
    await ctx.send("Cog unloaded")
  except commands.ExtensionNotLoaded:
    await ctx.send("Not a cog or Already unloaded cog")
@unload.error
async def unloadError(ctx, error) -> None:
    await ctx.send("Put a cog after command")

#Sync
@bot.command()
@commands.is_owner()
async def sync(ctx) -> None:
    if ctx.guild is not None:
        bot.tree.copy_global_to(ctx.guild.id)
        await bot.tree.sync(ctx.guild.id)
        await ctx.send(f'Command tree synced to {ctx.guild}')
    else:
        await bot.tree.sync()
        await ctx.send('Command tree synced globally')
@sync.error
async def sync(ctx, error) -> None:
    if ctx.author.id == settings.SAPO_ID or settings.MONKEY_ID:
        await bot.tree.sync()
        await ctx.send(f'Command tree synced to {ctx.guild}')
    else:
        await ctx.send('Only owners can use this command')

if __name__ == "__main__":
    run()