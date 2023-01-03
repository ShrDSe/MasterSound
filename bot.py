import config
from discord.ext import commands
from discord import Intents

# ------------------------------------------

CONFIG = config.CONFIG
YDL_CONFIG = config.YDL_CONFIG
FFMPEG_CONFIG = config.FFMPEG_CONFIG

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=CONFIG['prefix'], intents = intents) 

exts = ['cogs.music',]
   
# ------------------------------------------

@bot.event
async def on_ready():
    for ext in exts:
        await bot.load_extension(ext)
    print('Logged in as')
    print(bot.user.name)
    print('Have a nice day! ^w^') 

@bot.command()
async def reload(ctx):
    for ext in exts:
        await bot.unload_extension(ext)
        await bot.load_extension(ext)
    await ctx.send("Reloaded!")

# ------------------------------------------

if __name__ == '__main__':
    bot.run(CONFIG['token'])
    