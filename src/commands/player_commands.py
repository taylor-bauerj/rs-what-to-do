from discord.ext import commands

class PlayerCommands(commands.Cog):
    def __init__(self, bot, player_data_manager):
        self.bot = bot
        self.player_data_manager = player_data_manager

    @commands.command(name='setrsn')
    async def set_player_name(self, ctx, player_name: str):
        self.player_data_manager.set_player_name(str(ctx.author.id), player_name)
        await ctx.send(f"Your RuneScape name has been set to: {player_name}")
