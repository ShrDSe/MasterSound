from discord.ext import commands

class Minor(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def uwu(self, ctx):
        await ctx.send()


async def setup(bot):
    await bot.add_cog(Minor(bot))
