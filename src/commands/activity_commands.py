from discord.ext import commands
import discord

class ActivityCommands(commands.Cog):
    def __init__(self, bot, rs_api, activity_suggester, player_data_manager):
        self.bot = bot
        self.rs_api = rs_api
        self.activity_suggester = activity_suggester
        self.player_data_manager = player_data_manager

    @commands.command(name='whatdo')
    async def suggest_activity(self, ctx):
        user_id = str(ctx.author.id)
        player_name = self.player_data_manager.get_player_name(user_id)
        
        if not player_name:
            await ctx.send("Please set your RuneScape name first using !setrsn <name>")
            return

        try:
            player_data = self.rs_api.get_player_stats(player_name)
            
            if 'error' in player_data:
                await ctx.send(f"Could not find player: {player_name}")
                return

            suggestions = await self.activity_suggester.get_suggestions(player_data)
            
            embed = discord.Embed(
                title=f"Suggested activities for {player_name}",
                color=discord.Color.blue()
            )
            
            for i, suggestion in enumerate(suggestions[:5], 1):
                embed.add_field(
                    name=f"Suggestion {i}",
                    value=suggestion,
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
